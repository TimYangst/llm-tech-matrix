"""Render an extracted model JSON to a human-readable Markdown summary.

The .md is a deterministic view of the JSON — no narrative is added that isn't already
in the data. This keeps the two from drifting; if you want to change the summary,
change the JSON (or the renderer).

CLI:
    uv run python -m llm_tech_matrix.extraction.render <slug>
    uv run python -m llm_tech_matrix.extraction.render --all
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from llm_tech_matrix.schema import ExtractedModel

EXTRACTED_DIR = Path("data/extracted")


def _row(label: str, value: Any) -> str:
    if value is None or value == "":
        value = "—"
    return f"| {label} | {value} |"


def _table(rows: list[tuple[str, Any]]) -> str:
    body = "\n".join(_row(k, v) for k, v in rows)
    return f"| | |\n|---|---|\n{body}"


def _bullets(items: list[str]) -> str:
    if not items:
        return "_(none)_"
    return "\n".join(f"- {item}" for item in items)


def _openness_label(o: str) -> str:
    return {"open_source": "Open source", "open_weights": "Open weights", "closed": "Closed"}.get(o, o)


def render(model: ExtractedModel) -> str:
    md = model.metadata
    arch = model.architecture
    train = model.training

    parts: list[str] = []

    # ---- Header ----
    parts.append(f"# {md.name}")
    parts.append("")
    parts.append(f"*Schema version: {model.schema_version}*")
    parts.append("")

    # ---- Overview ----
    parts.append("## Overview")
    parts.append("")
    parts.append(_table([
        ("Family", md.family),
        ("Released", md.release_date),
        ("Openness", _openness_label(md.openness)),
        ("Total parameters", md.params_total),
        ("Active parameters", md.params_active),
    ]))
    parts.append("")

    # ---- Sources ----
    parts.append("## Sources")
    parts.append("")
    parts.append(_bullets([f"<{u}>" for u in md.sources]))
    parts.append("")

    # ---- Architecture ----
    parts.append("## Architecture")
    parts.append("")

    parts.append("### Backbone")
    parts.append("")
    bb = arch.backbone
    parts.append(_table([
        ("Layers", bb.layers),
        ("Hidden dim", bb.hidden_dim),
        ("Context window", bb.context_window),
    ]))
    if bb.context_window_notes:
        parts.append("")
        parts.append(f"**Context notes:** {bb.context_window_notes}")
    parts.append("")

    parts.append(f"### Attention ({arch.attention.variant})")
    parts.append("")
    att = arch.attention
    rows: list[tuple[str, Any]] = [
        ("Variant", att.variant),
        ("Heads", att.num_heads),
        ("KV heads", att.num_kv_heads),
        ("Head dim", att.head_dim),
    ]
    parts.append(_table(rows))
    parts.append("")

    rope = att.rope
    parts.append(f"**RoPE:** type=`{rope.type}`, base=`{rope.base}`")
    if rope.scaling:
        parts.append("")
        parts.append("RoPE scaling:")
        parts.append("")
        parts.append("```json")
        parts.append(json.dumps(rope.scaling, indent=2))
        parts.append("```")
    parts.append("")

    if att.mla is not None:
        parts.append("**MLA-specific:**")
        parts.append("")
        parts.append(_table([
            ("kv_lora_rank", att.mla.kv_lora_rank),
            ("q_lora_rank", att.mla.q_lora_rank),
            ("qk_nope_head_dim", att.mla.qk_nope_head_dim),
            ("qk_rope_head_dim", att.mla.qk_rope_head_dim),
            ("v_head_dim", att.mla.v_head_dim),
        ]))
        parts.append("")

    parts.append(f"### FFN ({arch.ffn.ffn_type})")
    parts.append("")
    ffn = arch.ffn
    if ffn.dense_intermediate_size is not None:
        parts.append(f"**Dense intermediate size:** `{ffn.dense_intermediate_size}`")
        parts.append("")
    if ffn.moe is not None:
        parts.append("**MoE:**")
        parts.append("")
        parts.append(_table([
            ("Routed experts", ffn.moe.num_experts),
            ("Active experts per token", ffn.moe.num_active_experts),
            ("Shared experts", ffn.moe.shared_experts),
            ("Per-expert intermediate size", ffn.moe.expert_intermediate_size),
        ]))
        parts.append("")
        parts.append(f"**Routing:** {ffn.moe.routing}")
        parts.append("")
    if ffn.layer_partition:
        parts.append(f"**Layer partition:** {ffn.layer_partition}")
        parts.append("")

    parts.append("### Components")
    parts.append("")
    parts.append(_table([
        ("Activation", arch.components.activation),
        ("Normalization", arch.components.normalization),
    ]))
    parts.append("")
    parts.append(f"**Embedding notes:** {arch.components.embedding_notes}")
    parts.append("")

    parts.append("### Parallelism / infra")
    parts.append("")
    parts.append(arch.parallelism_notes)
    parts.append("")

    # ---- Training ----
    parts.append("## Training")
    parts.append("")
    parts.append(_table([
        ("Optimizer", train.optimizer),
        ("Total training tokens", train.data_total_tokens),
    ]))
    parts.append("")

    parts.append(f"**LR schedule:** {train.lr_schedule}")
    parts.append("")

    if train.data_mix:
        parts.append("**Data mix:**")
        parts.append("")
        parts.append(_table(list(train.data_mix.items())))
        parts.append("")
    if train.data_mix_notes:
        parts.append(f"**Data mix notes:** {train.data_mix_notes}")
        parts.append("")

    # Objectives
    obj = train.objectives
    has_obj = (obj.multi_token_prediction is not None
               or obj.fill_in_middle is not None
               or obj.other)
    if has_obj:
        parts.append("### Training objectives (beyond next-token prediction)")
        parts.append("")
        if obj.multi_token_prediction is not None:
            mtp = obj.multi_token_prediction
            parts.append("**Multi-Token Prediction (MTP):**")
            parts.append("")
            parts.append(_table([
                ("Depth (D)", mtp.depth),
                ("Loss weight schedule", mtp.loss_weight_schedule),
            ]))
            if mtp.shared_modules:
                parts.append("")
                parts.append(f"_Shared modules:_ {mtp.shared_modules}")
            parts.append("")
        if obj.fill_in_middle is not None:
            fim = obj.fill_in_middle
            parts.append("**Fill-in-Middle (FIM):**")
            parts.append("")
            parts.append(_table([
                ("Format", fim.format),
                ("Rate", fim.rate),
            ]))
            parts.append("")
        if obj.other:
            parts.append("**Other objectives:**")
            parts.append("")
            parts.append(_bullets(obj.other))
            parts.append("")

    parts.append("### Alignment")
    parts.append("")
    al = train.alignment
    parts.append(f"**SFT:** {al.sft}")
    parts.append("")
    parts.append(f"**RL method:** {al.rl_method}")
    parts.append("")
    parts.append(f"**RLAIF:** `{al.rlaif}`")
    parts.append("")

    parts.append("### Advanced")
    parts.append("")
    parts.append(f"**Self-distillation:** {train.advanced.self_distillation}")
    parts.append("")
    parts.append(f"**Mixed precision:** {train.advanced.mixed_precision}")
    parts.append("")

    # ---- Multimodal ----
    if model.multimodal is not None:
        mm = model.multimodal
        parts.append("## Multimodal")
        parts.append("")
        parts.append(_table([
            ("Vision encoder", mm.vision_encoder),
            ("Audio encoder", mm.audio_encoder),
            ("Fusion", mm.fusion),
        ]))
        if mm.fusion_notes:
            parts.append("")
            parts.append(f"**Fusion notes:** {mm.fusion_notes}")
        parts.append("")

    # ---- Inferred fields & open questions ----
    if model.inferred_fields:
        parts.append("## Inferred fields")
        parts.append("")
        parts.append("| Field | Basis | Confidence |")
        parts.append("|---|---|---|")
        for inf in model.inferred_fields:
            parts.append(f"| `{inf.field}` | {inf.basis} | {inf.confidence} |")
        parts.append("")

    if model.open_questions:
        parts.append("## Open questions")
        parts.append("")
        parts.append(_bullets(model.open_questions))
        parts.append("")

    # ---- Footer ----
    parts.append("---")
    parts.append("")
    parts.append(f"_Generated from `data/extracted/{md.name.lower().replace(' ', '-')}.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._")
    parts.append("")

    return "\n".join(parts)


def render_slug(slug: str) -> Path:
    json_path = EXTRACTED_DIR / f"{slug}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No extracted JSON at {json_path}")
    data = json.loads(json_path.read_text())
    model = ExtractedModel.model_validate(data)
    md_path = EXTRACTED_DIR / f"{slug}.md"
    md_path.write_text(render(model))
    return md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m llm_tech_matrix.extraction.render",
        description="Render extracted model JSON(s) to Markdown summaries.",
    )
    parser.add_argument("slug", nargs="?", help="Model slug. Required unless --all.")
    parser.add_argument("--all", action="store_true", help="Render every JSON in data/extracted/")
    args = parser.parse_args(argv)

    if args.all:
        slugs = sorted(p.stem for p in EXTRACTED_DIR.glob("*.json"))
        if not slugs:
            print("No extracted JSON files found.")
            return 0
        for slug in slugs:
            path = render_slug(slug)
            print(f"  rendered  {path}")
        return 0

    if not args.slug:
        parser.error("slug is required (or pass --all)")
    path = render_slug(args.slug)
    print(f"Rendered {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
