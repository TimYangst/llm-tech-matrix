"""One-shot migration: schema v7 → v8.

For each data/extracted/<slug>.json:
- Bump schema_version to 8.
- Populate the three new v8 slots where the facts are ALREADY present in the record's own
  prose (inference_modes triggers, sparse_attention text, auxiliary_modules). This is a
  restatement into structured form, never new research:
    * architecture.attention.cross_layer_sharing[]  (IndexShare, CSA2, causal encoder-decoder)
    * architecture.memory_modules[]                 (n-gram embedding, Engram) — MOVED out of
                                                    architecture.auxiliary_modules
    * training.alignment.reasoning_effort           (structured effort axis)
- Mark the open questions that v8 resolves as "RESOLVED IN v8", keeping their text so the
  history of the gap stays readable (the same convention the v7 migration used).

All new fields are optional with defaults, so a v7 record is valid as v8 with a bare
schema_version bump; the per-slug content below is what makes the v8 records carry real data.
Idempotent: re-running on v8 records is a no-op for already-migrated slots.

Usage:
    uv run python scripts/migrate_v7_to_v8.py
"""

# ruff: noqa: RUF001
# The per-slug content quotes sources verbatim: DeepSeek's full-width-bar token spelling
# (the <|System|> token) and the tech reports' math symbols (multiplication, minus, gamma,
# tau, script-l, union). Replacing them with ASCII look-alikes would corrupt the recorded
# text, so RUF001 is suppressed at file scope, as in src/llm_tech_matrix/extraction/render.py.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"

UNKNOWN = "[Unknown/Not Disclosed]"

# ---------------------------------------------------------------------------
# Reasoning effort
# ---------------------------------------------------------------------------

QWEN38_XHIGH = (
    "'Reasoning effort is set to xhigh. Please think carefully through the task, validate key "
    "assumptions, consider plausible alternatives, and prioritize correctness, consistency, and "
    "clarity in the final answer.' (injected into the system message)"
)
QWEN38_LOW = (
    "'Reasoning effort is set to low. Keep your thinking brief and focused, moving directly to "
    "the conclusion without unnecessary elaboration.' (injected into the system message)"
)


def _qwen38_effort(applies_when: str) -> dict[str, Any]:
    return {
        "api_parameter": "reasoning_effort",
        "delivery": "system_message_instruction",
        "scale": "discrete",
        "range": "",
        "levels": [
            {
                "name": "xhigh",
                "numeric_value": None,
                "rendering": QWEN38_XHIGH,
                "is_default": True,
                "notes": "",
            },
            {
                "name": "medium",
                "numeric_value": None,
                "rendering": "none — the template leaves reasoning_instructions empty for this level",
                "is_default": False,
                "notes": "The middle level is the bare prompt; only xhigh and low add text.",
            },
            {
                "name": "low",
                "numeric_value": None,
                "rendering": QWEN38_LOW,
                "is_default": False,
                "notes": "",
            },
        ],
        "applies_when": applies_when,
        "invalid_value_behavior": "The chat template raises an exception for any value outside {xhigh, medium, low}.",
        "training_method": UNKNOWN,
        "notes": (
            "If no system message exists the template synthesizes one; when tools are declared "
            "the instruction is prepended inside the tools system block. Whether the model was "
            "RL-trained against these strings is undisclosed (see open_questions)."
        ),
    }


DEEPSEEK_V4_PREVIEW_EFFORT: dict[str, Any] = {
    "api_parameter": UNKNOWN,
    "delivery": "prompt_prefix",
    "scale": "discrete",
    "range": "",
    "levels": [
        {
            "name": "non-think",
            "numeric_value": None,
            "rendering": "none — output begins directly with '</think> summary'",
            "is_default": True,
            "notes": "Recorded as the default response mode; trained as a separate specialist mode under a shorter context window and tighter length penalty.",
        },
        {
            "name": "think-high",
            "numeric_value": None,
            "rendering": "none — '<think> thinking tokens </think> summary' output framing, no effort prefix",
            "is_default": False,
            "notes": "",
        },
        {
            "name": "think-max",
            "numeric_value": None,
            "rendering": "'Reasoning Effort: Absolute maximum with no shortcuts permitted...' prepended to the system prompt (paper Table 3), plus <think> framing",
            "is_default": False,
            "notes": "",
        },
    ],
    "applies_when": "Three modes described in the technical report; the preview release documents no named request parameter.",
    "invalid_value_behavior": UNKNOWN,
    "training_method": (
        "Separate specialist modes trained with per-mode RL context windows (8K / 128K / 384K at "
        "evaluation) and length-penalty schedules — the tighter the penalty, the lower the effort."
    ),
    "notes": "Non-think doubles as the thinking-off switch: the preview's effort axis and thinking toggle are one axis.",
}

EFFORT: dict[str, dict[str, Any]] = {
    "deepseek-v4-pro": DEEPSEEK_V4_PREVIEW_EFFORT,
    "deepseek-v4-flash": DEEPSEEK_V4_PREVIEW_EFFORT,
    "deepseek-v4-flash-0731": {
        "api_parameter": "reasoning_effort",
        "delivery": "prompt_prefix",
        "scale": "discrete",
        "range": "",
        "levels": [
            {
                "name": "low",
                "numeric_value": None,
                "rendering": "none — the bare thinking-mode prompt",
                "is_default": True,
                "notes": "The preview's unprefixed 'Think High' mode, renamed.",
            },
            {
                "name": "high",
                "numeric_value": None,
                "rendering": "'Reasoning Effort: Absolute maximum with no shortcuts permitted. …' at the very start of the prompt, before the system message",
                "is_default": False,
                "notes": "Exactly the preview's 'Think Max' prefix, demoted.",
            },
            {
                "name": "max",
                "numeric_value": None,
                "rendering": "'Reasoning Effort: Beyond maximum — exhaustive, relentless, and uncompromising. …' at the very start of the prompt",
                "is_default": False,
                "notes": "New top level in this release.",
            },
        ],
        "applies_when": "thinking_mode='thinking' only; reasoning_effort has no effect with thinking_mode='chat'.",
        "invalid_value_behavior": UNKNOWN,
        "training_method": UNKNOWN,
        "notes": "Level names shifted against the preview, so cross-version 'max' comparisons are not the same prompt condition.",
    },
    "deepseek-v4.1-flash": {
        "api_parameter": "reasoning_effort",
        "delivery": "prompt_prefix",
        "scale": "continuous",
        "range": "1-100",
        "levels": [
            {
                "name": "low",
                "numeric_value": 50,
                "rendering": "'<｜System｜>Reasoning Effort: 50 (range 1-100, the higher the value, the more thorough the reasoning)'",
                "is_default": False,
                "notes": "",
            },
            {
                "name": "high",
                "numeric_value": 75,
                "rendering": "'<｜System｜>Reasoning Effort: 75 (range 1-100, the higher the value, the more thorough the reasoning)'",
                "is_default": True,
                "notes": "Default moved from V4-Flash-0731's unprefixed `low` to `high`=75.",
            },
            {
                "name": "max",
                "numeric_value": 100,
                "rendering": "'<｜System｜>Reasoning Effort: 100 (range 1-100, the higher the value, the more thorough the reasoning)'",
                "is_default": False,
                "notes": "All instruct benchmarks are reported at 100.",
            },
        ],
        "applies_when": "thinking_mode='thinking' only; rendered once, as a <｜System｜> block before the system prompt, at conversation index 0. Any integer 1–100 is accepted; the names are aliases.",
        "invalid_value_behavior": UNKNOWN,
        "training_method": (
            "RL conditioned on a scalar effort b prepended to the system prompt: M_b responses "
            "sampled per training effort level, advantages mean-centered within each "
            "(prompt, b) subgroup, and a length penalty r_len = −min(C_max, k(b)·ℓ/L_norm) with "
            "k(b) = k0·exp(−(b − b_min)/τ), τ = λΔb. Trained on a finite, undisclosed set of levels; "
            "intermediate values interpolate (tech report §5.1.4, Appendix C)."
        ),
        "notes": (
            "Effort 25 → 100 lifts the 8-benchmark reasoning average 67.1% → 76.3%, DeepSWE v1.1 "
            "66.0% → 74.2% and Terminal-Bench 2.1 82.4% → 90.6% at ≈2.5× output tokens (Figure 9). "
            "The report's quoted training string differs slightly from the encoder's rendering."
        ),
    },
    "glm-5.2": {
        "api_parameter": "reasoning_effort",
        "delivery": "prompt_prefix",
        "scale": "discrete",
        "range": "",
        "levels": [
            {
                "name": "max",
                "numeric_value": None,
                "rendering": "'<|system|>Reasoning Effort: Max' as the very first thing in the prompt",
                "is_default": True,
                "notes": "",
            },
            {
                "name": "high",
                "numeric_value": None,
                "rendering": "'<|system|>Reasoning Effort: High'",
                "is_default": False,
                "notes": "",
            },
        ],
        "applies_when": "Only when thinking is enabled — the effort line is guarded by enable_thinking.",
        "invalid_value_behavior": "Strict two-way branch: anything other than exactly 'high' silently falls back to 'max' (no error).",
        "training_method": UNKNOWN,
        "notes": "First GLM with an effort axis; GLM-5 / GLM-5.1 had none.",
    },
    "glm-5.3-flash": {
        "api_parameter": "reasoning_effort",
        "delivery": "prompt_prefix",
        "scale": "discrete",
        "range": "",
        "levels": [
            {
                "name": "max",
                "numeric_value": None,
                "rendering": "'<|system|>Reasoning Effort: Max' as the prompt prefix",
                "is_default": True,
                "notes": "",
            },
            {
                "name": "high",
                "numeric_value": None,
                "rendering": UNKNOWN,
                "is_default": False,
                "notes": "",
            },
            {
                "name": "low",
                "numeric_value": None,
                "rendering": UNKNOWN,
                "is_default": False,
                "notes": "New in 5.3-Flash; GLM-5.2 accepted only {high, max}.",
            },
        ],
        "applies_when": "Unconditional — resolved before any thinking check; there is no enable_thinking in this template.",
        "invalid_value_behavior": "Accepts 'low' and 'high'; anything else silently falls back to 'max'.",
        "training_method": UNKNOWN,
        "notes": "",
    },
    "kimi-k3": {
        "api_parameter": "reasoning_effort",
        "delivery": "typed_option_message",
        "scale": "discrete",
        "range": "",
        "levels": [
            {
                "name": "max",
                "numeric_value": None,
                "rendering": "global option message of type 'thinking-effort', inserted after the tool declaration and before the input messages, stating the level in natural language",
                "is_default": True,
                "notes": "All README §3 benchmark numbers are at max.",
            },
            {
                "name": "high",
                "numeric_value": None,
                "rendering": "same 'thinking-effort' option message with level high",
                "is_default": False,
                "notes": "",
            },
            {
                "name": "low",
                "numeric_value": None,
                "rendering": "same 'thinking-effort' option message with level low",
                "is_default": False,
                "notes": "",
            },
        ],
        "applies_when": "Always — K3 has no non-thinking mode on the API surface.",
        "invalid_value_behavior": UNKNOWN,
        "training_method": (
            "Nine RL experts = 3 domains × 3 effort levels, with per-problem token-budget rewards "
            "annealed stage-wise (budget multiplier tau annealed down from the max-budget variant) "
            "to carve out the levels; consolidated into one checkpoint by Multi-Teacher On-Policy "
            "Distillation, with the teacher chosen by domain and sampled effort."
        ),
        "notes": "The XTML schema reserves four levels (low, medium, high, max); K3 documents only three.",
    },
    "qwen3.8-27b": _qwen38_effort(
        "Thinking mode only — with enable_thinking=false the template skips effort resolution entirely."
    ),
    "qwen3.8-2.4t-a95b": _qwen38_effort(
        "Unconditional — the open checkpoint is thinking-only (the template raises on enable_thinking=false)."
    ),
    "qwen3.8-flash-next": _qwen38_effort(
        "Thinking mode only; chat_template.jinja is byte-identical to Qwen3.8-27B's (bar a trailing newline)."
    ),
}

# ---------------------------------------------------------------------------
# Cross-layer sharing
# ---------------------------------------------------------------------------

SHARING: dict[str, list[dict[str, Any]]] = {
    "glm-5.2": [
        {
            "kind": "indexshare",
            "shared_state": ["topk_indices"],
            "source_layers": (
                "21 Full layers (config.indexer_types='full'): layers 0-2, then every fourth layer "
                "from layer 3 (index_topk_freq=4, index_skip_topk_offset=3)"
            ),
            "consumer_layers": "57 Shared layers (config.indexer_types='shared'), each reusing the nearest preceding Full layer's top-k indices",
            "effect": (
                "2.9× fewer per-token FLOPs at 1M context (model card). Paper: 75% of indexer "
                "computation removed with negligible quality loss on a 30B DSA model (1.82× "
                "prefill / 1.48× decode), ~1.2× end-to-end on production-scale GLM-5 at 50% removal."
            ),
            "training_recipe": (
                "Training-aware route of IndexShare/IndexCache (arXiv 2603.12201): a multi-layer "
                "distillation loss trains each retained indexer against the averaged attention "
                "distributions of all the layers it serves. Inferred from the fixed period-4 "
                "pattern; Z.AI does not state which variant shipped."
            ),
            "notes": "Only indexer selections are shared — main KV stays per-layer. index_share_for_mtp_iteration=true extends the reuse into MTP speculative-decoding iterations.",
        }
    ],
    "deepseek-v4.1-flash": [
        {
            "kind": "ced",
            "shared_state": ["kv_from_encoder_output"],
            "source_layers": "hidden state of the final encoder layer (H_{L/2} in the report; zero-indexed layer 19)",
            "consumer_layers": "decoder layers 20-39 — global KV entries C_l and compression weights Z_l are projected from H_{L/2} with layer-dependent weights; under CSA2 only the decoder Full-Mode layer 20 materializes its own",
            "effect": "Prefill stops at the encoder: 8B active parameters per prompt token vs 16B per generated token; prefill complexity O(NL) → ≈ O(NL/2).",
            "training_recipe": "Trained from scratch in the architecture. Decoder SWA Bounded Replay (only the last n_win=128 prompt tokens replayed through the decoder for SWA KV) is simulated during post-training for train-aware adaptation.",
            "notes": "Global attention only. Sliding-window KV remains layer-local in every layer — CED deliberately does not share it.",
        },
        {
            "kind": "csa2",
            "shared_state": ["kv", "indexer_keys"],
            "source_layers": [2, 8, 14, 20],
            "consumer_layers": "every other CSA2 layer: Reindex layers 24, 28, 32, 36 and all 30 Reuse layers, each reading the most recent Full-Mode layer's main KV and indexer K",
            "effect": "Global KV cache 890 bytes/token with FP4 main KV, ~1/4 of DeepSeek-V4-Flash.",
            "training_recipe": "From scratch at 64K with no dense warm-up; cross-stage sharing trained with shadow indexers, pipeline payload extensions and micro-batch shared-state management.",
            "notes": "config.kv_source_layer_ids. Full-Mode layers compute their own main KV and project indexer K from it.",
        },
        {
            "kind": "csa2",
            "shared_state": ["topk_indices"],
            "source_layers": [2, 8, 14, 20, 24, 28, 32, 36],
            "consumer_layers": "the 30 Reuse-Mode layers, each reusing the latest top-k computed against the main KV it reads",
            "effect": "Reuse layers compute no indexer Q and no scores; each runs in 15 kernels (prefill) / 11 (decode).",
            "training_recipe": "",
            "notes": (
                "config.index_source_layer_ids = Full ∪ Reindex. Decoupled from KV sharing: Reindex "
                "layers share KV but select afresh. In the decoder, the Hierarchical Sparse Indexer "
                "additionally restricts Reindex layers to layer 20's candidate pool (2,048 blocks × 8 "
                "positions) — a restriction of the search domain, recorded in sparse_attention.selection."
            ),
        },
    ],
}

# ---------------------------------------------------------------------------
# Memory modules (moved out of auxiliary_modules)
# ---------------------------------------------------------------------------

MEMORY: dict[str, dict[str, Any]] = {
    "qwen3.8-flash-next": {
        "aux_name": "N-gram embedding layer",
        "module": {
            "name": "N-gram embedding layer",
            "kind": "ngram_embedding",
            "params": "51B (reported separately from the 125B backbone total)",
            "layers": [2],
            "addressing": "Short n-grams ending at each token (ngram_size=3, i.e. bigrams/trigrams), heads_per_ngram=8",
            "table_config": "20,000,000-entry table, embed dim 2560, depthwise conv of kernel 4, split into 128 parts",
            "storage": "Held off-accelerator in host memory and asynchronously prefetched; layer 2 chosen so the prefetch overlaps layer 1's computation",
            "optimizer": "Adam with weight decay disabled for the table; its key/value projections are on Muon",
            "notes": (
                "Placement ablation (report Tab. 7, fixed parameter budget): no depth regime dominates, "
                "layers 1-2 are strongest, splitting the budget across layers gives no consistent "
                "benefit. Vocabulary scaling 20V → 200V (Tab. 9, V=250K): loss decreases monotonically "
                "while downstream accuracy saturates or fluctuates; Chinese benchmarks (C-Eval, CMMLU) "
                "are the exception. Traded against MoE experts at fixed total params (Tab. 8): loss "
                "optimum at 10× (25% of params) but no clear downstream gain — 'N-gram embeddings and "
                "MoE experts play distinct roles in scaling capacity'. Token normalization, non-uniform "
                "allocation across orders and frequency-based slot partitioning gave no consistent gain."
            ),
        },
    },
    "deepseek-v4.1-flash": {
        "aux_name": "Engram conditional memory",
        "module": {
            "name": "Engram conditional memory",
            "kind": "engram",
            "params": "196B, split evenly across two modules (reported separately from the 552B backbone)",
            "layers": [1, 14],
            "addressing": (
                "Multi-head hashing of token n-grams, orders {2, 3, 4} (engram_max_ngram_size=4), 8 hash "
                "heads per order (engram_n_heads=8), over a compressed tokenizer vocabulary of 99,092 ids "
                "(engram_compressed_vocab_size); context-aware gating and multi-branch integration as in "
                "the original Engram design (arXiv:2601.07372)"
            ),
            "table_config": (
                "Each head indexes a ≈16M-entry table (engram_vocab_size=16,000,000) sized to a distinct "
                "prime; 256 dims per head (engram_head_dim=256) = 2,048 per order; "
                "engram_num_embeddings = [384,006,168, 384,016,682] per module. The original design's "
                "short causal convolution is removed."
            ),
            "storage": (
                "Tables and key/value projections in FP8. Training: row-partitioned across engram-parallel "
                "process groups with sharded optimizer states and whole-batch prefetch. Inference: "
                "prefetched from host memory via background RDMA, the first module's prefetch overlapping "
                "the first Transformer block; tables sharded. RL rollouts: tables kept resident in GPU memory."
            ),
            "optimizer": (
                "Sinkhorn-balanced momentum update (K=11 alternating row/column normalizations, τ=1e-3, "
                "γ=0.18, momentum 0.95, no weight decay) instead of Adam, to avoid Adam optimizer-state "
                "memory; Engram learning rate scaled 5×. Engram projection layers are on Muon."
            ),
            "notes": (
                "Placed at layers 1 and 14 to balance memory usage across training pipeline stages. "
                "Arithmetic check (not a vendor statement): 384.0M entries × 256 dims ≈ 98.3B per module, "
                "≈ 196.6B for two, consistent with the reported 196B."
            ),
        },
    },
}

# ---------------------------------------------------------------------------
# Open questions resolved by v8 (substring match → prefix)
# ---------------------------------------------------------------------------

RESOLVED: dict[str, list[tuple[str, str]]] = {
    "qwen3.8-flash-next": [
        (
            "How the n-gram embedding fits the schema is unresolved.",
            "RESOLVED IN v8 — moved to `architecture.memory_modules[]`, added after Engram "
            "(deepseek-v4.1-flash) became the second occurrence. Original question: ",
        ),
    ],
    "deepseek-v4.1-flash": [
        (
            "SCHEMA GAP — no home for Causal Encoder-Decoder",
            "RESOLVED IN v8 — `architecture.attention.cross_layer_sharing[]` now carries CED and "
            "both CSA2 sharing relations. Original gap: ",
        ),
        (
            "SCHEMA GAP — second occurrence of in-forward-pass embedding memory.",
            "RESOLVED IN v8 — Engram moved to `architecture.memory_modules[]`, with its own "
            "`params`. Original gap: ",
        ),
        (
            "STRUCTURED REASONING-EFFORT — fourth mechanism.",
            "RESOLVED IN v8 — `training.alignment.reasoning_effort` records delivery, "
            "continuous 1-100 scale and the 50/75/100 aliases. Original gap: ",
        ),
    ],
}


def migrate(slug: str, record: dict[str, Any]) -> list[str]:
    changes: list[str] = []
    if record.get("schema_version") != 8:
        record["schema_version"] = 8
        changes.append("schema_version → 8")

    arch = record["architecture"]
    att = arch["attention"]
    if slug in SHARING and not att.get("cross_layer_sharing"):
        att["cross_layer_sharing"] = SHARING[slug]
        changes.append(f"cross_layer_sharing ({len(SHARING[slug])})")

    if slug in MEMORY and not arch.get("memory_modules"):
        spec = MEMORY[slug]
        before = len(arch.get("auxiliary_modules", []))
        arch["auxiliary_modules"] = [
            m for m in arch.get("auxiliary_modules", []) if m["name"] != spec["aux_name"]
        ]
        if len(arch["auxiliary_modules"]) != before - 1:
            raise SystemExit(f"{slug}: expected to move auxiliary module {spec['aux_name']!r}")
        arch["memory_modules"] = [spec["module"]]
        changes.append("memory_modules (moved from auxiliary_modules)")

    al = record["training"]["alignment"]
    if slug in EFFORT and al.get("reasoning_effort") is None:
        al["reasoning_effort"] = EFFORT[slug]
        changes.append("reasoning_effort")

    for needle, prefix in RESOLVED.get(slug, []):
        qs = record["open_questions"]
        hits = [i for i, q in enumerate(qs) if needle in q and not q.startswith("RESOLVED IN v8")]
        for i in hits:
            qs[i] = prefix + qs[i]
            changes.append("open_question resolved")
    return changes


def main() -> int:
    missing = (set(EFFORT) | set(SHARING) | set(MEMORY)) - {
        p.stem for p in EXTRACTED_DIR.glob("*.json")
    }
    if missing:
        print(f"unknown slugs: {sorted(missing)}", file=sys.stderr)
        return 1
    for path in sorted(EXTRACTED_DIR.glob("*.json")):
        record = json.loads(path.read_text())
        changes = migrate(path.stem, record)
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        print(f"{path.stem:26} {', '.join(changes) or 'no change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
