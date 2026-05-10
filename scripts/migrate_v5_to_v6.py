"""One-shot migration: schema v5 → v6.

For each data/extracted/<slug>.json:
- Bump schema_version to 6.
- Add metadata.variant_policy (per-model free text).
- For each alignment.inference_modes entry, add `kwargs` and `sampling_recommended` dicts
  (per-mode, populated from source material; empty when source is silent).
- Optionally add alignment.tool_call_protocol when the wire format is documented in sources.

The new fields are all backwards-compatible (optional with defaults). A v5 record without
any of the new content is still valid as v6 — but this migration populates the content
that *is* documented, so the v6 records carry real data.

Usage:
    uv run python scripts/migrate_v5_to_v6.py
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"

# ---------------------------------------------------------------------------
# Per-model content. Slug -> dict of edits to apply on top of the v5 record.
#
# Schema:
#   variant_policy: str
#   modes: dict[mode_name -> dict with optional "kwargs", "sampling_recommended"]
#   tool_call_protocol: dict | None  (full ToolCallProtocol body)
#
# Notes inline cite where each value comes from to keep the no-hallucination rule.
# ---------------------------------------------------------------------------

QWEN35_VARIANT_POLICY = (
    "Unified weights per (size, dense/MoE) — Qwen3.5 ships ~7 open-weight sizes (per the "
    "Qwen3.6-27B README comparison table the 3.5 family includes 27B dense and 397B-A17B "
    "MoE among others). Each checkpoint handles thinking, non-thinking, vision and tool "
    "use through chat-template kwargs (`enable_thinking`) and serving-time parsers; there "
    "are NO separate Math / Coder / VL / Thinking siblings (a deliberate departure from "
    "Qwen2.5's Math/Coder/VL split). 'Coder' capability is exposed via the "
    "`--tool-call-parser qwen3_coder` serving flag (vLLM / SGLang) and post-training "
    "emphasis, not a separate weight checkpoint. Native VL is unified into the base "
    "weights via the `qwen3_5` ViT shared with the LM vocabulary (image / video / "
    "vision_start / vision_end token IDs). README pipeline_tag is `image-text-to-text` "
    "for both 27B and 35B-A3B."
)

QWEN36_VARIANT_POLICY = (
    "Same unified-weights philosophy as Qwen3.5: one checkpoint per (size, dense/MoE), "
    "modes via chat-template kwargs. Qwen3.6 adds a third runtime mode `preserve_thinking` "
    "(multi-turn reasoning carryover) via a chat-template kwarg — composable with "
    "`enable_thinking`. As of release the open-weight surface is narrower than 3.5 — only "
    "27B dense + 35B-A3B MoE shipped open-weight (README: 'first open-weight variant of "
    "Qwen3.6'). Same NO-separate-Math/Coder/VL-siblings policy; Coder capability is "
    "post-training emphasis ('Agentic Coding' highlight) plus the `qwen3_coder` serving "
    "parser, not a sibling checkpoint."
)

QWEN3_VARIANT_POLICY = (
    "Per-size open-weight checkpoints — 6 dense sizes (0.6B-32B) + 2 MoE flagships "
    "(30B-A3B, 235B-A22B). All siblings share the unified four-stage post-training "
    "pipeline (Long-CoT Cold Start → Reasoning RL → Thinking Mode Fusion → General RL); "
    "Stage 3 deliberately FUSES thinking and non-thinking into one model rather than "
    "shipping separate Thinking/Instruct checkpoints. No Math/Coder/VL siblings in the "
    "Qwen3 generation — coder/VL/omni capabilities live in Qwen2.5 and Qwen3.5+ "
    "respectively. Modes are toggled via `/think` and `/no_think` soft-switch tokens "
    "in the user/system message (also exposed as `enable_thinking` chat-template kwarg)."
)

DEEPSEEK_V3_VARIANT_POLICY = (
    "Single base + Chat checkpoint per release; no Math / Coder / VL siblings. Reasoning "
    "capability lives in a separate sibling model (DeepSeek-R1) rather than as a runtime "
    "mode — V3 is a non-thinking instruction-following model end-to-end. The V3 → V4 "
    "generation collapses this V3+R1 split into a 3-mode runtime axis on one model."
)

DEEPSEEK_V4_VARIANT_POLICY = (
    "Two open-weight sizes (V4-Pro 1.6T/49B and V4-Flash 284B/13B) with the same V4 "
    "architecture family modulo size-specific differences (Flash uses pure SWA in layers "
    "0-1 instead of pure HCA). Reasoning effort is a runtime axis with three modes "
    "(Non-think / Think High / Think Max) selected via system prompt — collapses what "
    "in the V3 generation was a separate Reasoner sibling (DeepSeek-R1) into modes on a "
    "single checkpoint. A fourth runtime behavior (interleaved-thinking) auto-engages "
    "in tool-calling contexts. No separate Math / Coder / VL siblings."
)

# Qwen3.5/3.6 use the same XML-like Qwen3-Coder protocol (verified by reading
# tokenizer_config.json chat_template — the IF YOU CHOOSE TO CALL A FUNCTION block).
# 3.6 fixes a tool-arg JSON-encoding bug that 3.5 had.
QWEN35_TOOL_CALL_PROTOCOL = {
    "format": "xml-like",
    "start_token": "<tool_call>",
    "end_token": "</tool_call>",
    "arguments_schema": (
        "Per-arg <parameter=name>VALUE</parameter> blocks nested inside a "
        "<function=NAME></function> wrapper. Values are stringified — in Qwen3.5 the "
        "chat template applies `tojson` only to mappings/sequences and falls back to "
        "Python `str()` for scalars (so booleans render as 'True'/'False' rather than "
        "'true'/'false' — fixed in Qwen3.6 to apply `tojson` to anything that is not "
        "already a string)."
    ),
    "parser_flags": {
        "vllm": "--tool-call-parser qwen3_coder",
        "sglang": "--tool-call-parser qwen3_coder",
    },
    "notes": (
        "Verbatim from the chat template (tokenizer_config.json): '<tool_call>\\n"
        "<function=example_function_name>\\n<parameter=example_parameter_1>\\nvalue_1\\n"
        "</parameter>\\n<parameter=example_parameter_2>\\n...\\n</parameter>\\n</function>\\n"
        "</tool_call>'. README serving snippets pair `--tool-call-parser qwen3_coder` with "
        "`--reasoning-parser qwen3` for combined reasoning + tool-use deployments. The "
        "natural-language reasoning may appear BEFORE but NOT after the tool call (template "
        "comment). Tool-call output is wrapped via `<tool_response>...</tool_response>` "
        "blocks emitted as a `tool` role message."
    ),
}

QWEN36_TOOL_CALL_PROTOCOL = {
    "format": "xml-like",
    "start_token": "<tool_call>",
    "end_token": "</tool_call>",
    "arguments_schema": (
        "Per-arg <parameter=name>VALUE</parameter> blocks nested inside a "
        "<function=NAME></function> wrapper. Qwen3.6 fixes a Qwen3.5 JSON-encoding bug — "
        "the chat template now applies `tojson` to anything that is not already a string "
        "(non-string scalars like booleans and numbers serialize as JSON 'true'/'false'/'5' "
        "rather than Python 'True'/'False'/'5'). Strings pass through unchanged."
    ),
    "parser_flags": {
        "vllm": "--tool-call-parser qwen3_coder",
        "sglang": "--tool-call-parser qwen3_coder",
    },
    "notes": (
        "Same Qwen3-Coder XML-like wire format as Qwen3.5; only difference is the tool-arg "
        "scalar encoding fix above. README serving snippets pair `--tool-call-parser "
        "qwen3_coder` with `--reasoning-parser qwen3`. Compatible with `preserve_thinking` "
        "kwarg — README highlights agent scenarios as the primary motivation for the new "
        "preserve_thinking mode (full reasoning context across multi-turn tool-calling "
        "improves decision consistency and KV-cache utilization)."
    ),
}

# ---------------------------------------------------------------------------
# Per-mode kwargs and sampling, sourced from each model's README/paper.
# Outer key is the slug; inner key is the mode `name` exactly as it appears in the
# existing inference_modes list.
# ---------------------------------------------------------------------------

# Qwen3.5 README "Best Practices" — 4 sampling presets.
# Thinking general-task numbers as the default; non-thinking general-task numbers
# as the default. Thinking-coding and non-thinking-reasoning variants noted in the
# trigger/description text already.
QWEN35_MODES = {
    "thinking": {
        "kwargs": {"enable_thinking": "true"},
        "sampling_recommended": {
            "temperature": "1.0",
            "top_p": "0.95",
            "top_k": "20",
            "min_p": "0.0",
            "presence_penalty": "1.5",
            "repetition_penalty": "1.0",
        },
    },
    "non-thinking": {
        "kwargs": {"enable_thinking": "false"},
        "sampling_recommended": {
            "temperature": "0.7",
            "top_p": "0.8",
            "top_k": "20",
            "min_p": "0.0",
            "presence_penalty": "1.5",
            "repetition_penalty": "1.0",
        },
    },
}

# Qwen3.6 README "Best Practices" — 3 sampling presets (one fewer than 3.5).
# Notable diff vs 3.5: thinking-general drops presence_penalty 1.5 → 0.0.
QWEN36_MODES = {
    "thinking": {
        "kwargs": {"enable_thinking": "true"},
        "sampling_recommended": {
            "temperature": "1.0",
            "top_p": "0.95",
            "top_k": "20",
            "min_p": "0.0",
            "presence_penalty": "0.0",
            "repetition_penalty": "1.0",
        },
    },
    "non-thinking": {
        "kwargs": {"enable_thinking": "false"},
        "sampling_recommended": {
            "temperature": "0.7",
            "top_p": "0.80",
            "top_k": "20",
            "min_p": "0.0",
            "presence_penalty": "1.5",
            "repetition_penalty": "1.0",
        },
    },
    "preserve-thinking": {
        "kwargs": {"preserve_thinking": "true"},
        "sampling_recommended": {},  # composable with thinking/non-thinking; no separate preset
    },
}

# Qwen3 README/paper sampling recommendations — restated as machine-readable fields
# from the values already present in the existing inference_modes[].description prose
# (which currently reads "Recommended sampling: temperature=0.6, top-p=0.95, top-k=20"
# for thinking and "temperature=0.7, top-p=0.8, top-k=20, presence_penalty=1.5" for
# non-thinking). Thinking-budget has no separately recommended sampling — the budget
# itself is the knob, not sampling — so it stays empty.
QWEN3_MODES = {
    "thinking": {
        "kwargs": {"enable_thinking": "true"},
        "sampling_recommended": {
            "temperature": "0.6",
            "top_p": "0.95",
            "top_k": "20",
        },
    },
    "non-thinking": {
        "kwargs": {"enable_thinking": "false"},
        "sampling_recommended": {
            "temperature": "0.7",
            "top_p": "0.8",
            "top_k": "20",
            "presence_penalty": "1.5",
        },
    },
    "thinking-budget": {
        "kwargs": {},  # not a chat-template kwarg — manual injection of fixed instruction
        "sampling_recommended": {},
    },
}

# DeepSeek-V4 modes are selected by system-prompt content, not chat-template kwargs;
# the V4 paper does not publish per-mode sampling presets. Both stay empty.
DEEPSEEK_V4_MODES = {
    "non-think": {"kwargs": {}, "sampling_recommended": {}},
    "think-high": {"kwargs": {}, "sampling_recommended": {}},
    "think-max": {"kwargs": {}, "sampling_recommended": {}},
    "interleaved-thinking (cross-turn reasoning preservation)": {
        "kwargs": {},
        "sampling_recommended": {},
    },
}

# DeepSeek-V4 documents an XML-format tool-call protocol that uses the |DSML|
# special-token namespace, citing paper Table 4 (per the existing embedding_notes in
# the v5 extraction — quote: "Tool-call schema special token '|DSML|' wrapping
# XML-format tool invocations <|DSML|tool_calls>...<|DSML|invoke name=...>...
# </|DSML|invoke>... (paper Table 4) - replaces JSON to mitigate string-escape
# failures"). The format deliberately replaces JSON to avoid escape bugs.
DEEPSEEK_V4_TOOL_CALL_PROTOCOL = {
    "format": "xml-like",
    "start_token": "<|DSML|tool_calls>",
    "end_token": "[Unknown/Not Disclosed]",
    "arguments_schema": (
        "Per-call <|DSML|invoke name=NAME>...</|DSML|invoke> blocks nested inside the "
        "tool_calls wrapper. XML format — paper Table 4 explicitly states it replaces "
        "JSON to mitigate string-escape failures (a known weakness of JSON-only tool "
        "protocols). Argument-encoding details inside an invoke block are not restated "
        "in the README; refer to paper Table 4 for full grammar."
    ),
    "parser_flags": {},  # No vLLM/SGLang public parser flag is documented in the README.
    "notes": (
        "Distinguishes V4 from V3 (no documented tool-call protocol in V3). The HF "
        "release ships no Jinja chat template — encoding is done via a Python module "
        "(encoding_dsv4) co-located with the model, so serving stacks need either that "
        "encoder module or a custom integration. Same |DSML| namespace also hosts the "
        "V4 'Quick Instruction' tokens (<|action|>, <|title|>, <|query|>, <|authority|>, "
        "<|domain|>, <|extracted_url|>, <|read_url|>) that enable parallel auxiliary "
        "tasks reusing the existing KV cache (paper Table 5). Auto-engages "
        "interleaved-thinking mode (one of the four runtime inference_modes)."
    ),
}


PER_SLUG: dict[str, dict] = {
    "qwen3.5-27b": {
        "variant_policy": QWEN35_VARIANT_POLICY,
        "modes": QWEN35_MODES,
        "tool_call_protocol": QWEN35_TOOL_CALL_PROTOCOL,
    },
    "qwen3.5-35b-a3b": {
        "variant_policy": QWEN35_VARIANT_POLICY,
        "modes": QWEN35_MODES,
        "tool_call_protocol": QWEN35_TOOL_CALL_PROTOCOL,
    },
    "qwen3.6-27b": {
        "variant_policy": QWEN36_VARIANT_POLICY,
        "modes": QWEN36_MODES,
        "tool_call_protocol": QWEN36_TOOL_CALL_PROTOCOL,
    },
    "qwen3.6-35b-a3b": {
        "variant_policy": QWEN36_VARIANT_POLICY,
        "modes": QWEN36_MODES,
        "tool_call_protocol": QWEN36_TOOL_CALL_PROTOCOL,
    },
    "qwen3-32b": {
        "variant_policy": QWEN3_VARIANT_POLICY,
        "modes": QWEN3_MODES,
        "tool_call_protocol": None,
    },
    "qwen3-235b-a22b": {
        "variant_policy": QWEN3_VARIANT_POLICY,
        "modes": QWEN3_MODES,
        "tool_call_protocol": None,
    },
    "deepseek-v3": {
        "variant_policy": DEEPSEEK_V3_VARIANT_POLICY,
        "modes": {},
        "tool_call_protocol": None,
    },
    "deepseek-v4-pro": {
        "variant_policy": DEEPSEEK_V4_VARIANT_POLICY,
        "modes": DEEPSEEK_V4_MODES,
        "tool_call_protocol": DEEPSEEK_V4_TOOL_CALL_PROTOCOL,
    },
    "deepseek-v4-flash": {
        "variant_policy": DEEPSEEK_V4_VARIANT_POLICY,
        "modes": DEEPSEEK_V4_MODES,
        "tool_call_protocol": DEEPSEEK_V4_TOOL_CALL_PROTOCOL,
    },
}


def migrate_one(path: Path) -> tuple[bool, str]:
    """Apply v5→v6 migration to one record. Returns (changed, summary)."""
    slug = path.stem
    overrides = PER_SLUG.get(slug)
    if overrides is None:
        return False, f"  SKIP {slug}: no per-slug overrides defined"

    data = json.loads(path.read_text(encoding="utf-8"))
    before = copy.deepcopy(data)

    # 1. Bump schema_version
    data["schema_version"] = 6

    # 2. metadata.variant_policy
    data["metadata"]["variant_policy"] = overrides["variant_policy"]

    # 3. inference_modes[].kwargs and .sampling_recommended
    modes = data["training"]["alignment"].get("inference_modes", [])
    mode_overrides = overrides["modes"]
    unmatched = []
    for m in modes:
        name = m["name"]
        if name in mode_overrides:
            mo = mode_overrides[name]
            m["kwargs"] = mo.get("kwargs", {})
            m["sampling_recommended"] = mo.get("sampling_recommended", {})
        else:
            # Default empty dicts so the field is present with the v6 shape.
            m["kwargs"] = {}
            m["sampling_recommended"] = {}
            unmatched.append(name)

    # 4. alignment.tool_call_protocol (only set when not None — None is the default)
    tcp = overrides["tool_call_protocol"]
    if tcp is not None:
        data["training"]["alignment"]["tool_call_protocol"] = tcp

    if data == before:
        return False, f"  unchanged {slug}"

    # Pretty-print preserving indent=2 (matches existing files).
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = f"  migrated {slug}"
    if unmatched:
        summary += f"  (modes without overrides: {unmatched})"
    return True, summary


def main() -> int:
    files = sorted(EXTRACTED_DIR.glob("*.json"))
    if not files:
        print(f"No JSON files in {EXTRACTED_DIR}", file=sys.stderr)
        return 1

    changed = 0
    for path in files:
        ok, msg = migrate_one(path)
        print(msg)
        if ok:
            changed += 1
    print(f"\nMigrated {changed} of {len(files)} record(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
