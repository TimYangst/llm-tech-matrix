"""Render an extracted model JSON to a human-readable Markdown summary.

The .md is a deterministic view of the JSON — no narrative is added that isn't already
in the data. This keeps the two from drifting; if you want to change the summary,
change the JSON (or the renderer).

Two language variants are produced from the same JSON:

- ``<slug>.md``     — English (section headers, table labels, and chrome in English).
- ``<slug>.zh.md``  — Chinese chrome (headers + labels translated). Field *values*
  stay in source-language English to keep the .md a faithful view of the JSON; the
  glossary is the place to look up term definitions in Chinese.

CLI:
    uv run python -m llm_tech_matrix.extraction.render <slug>
    uv run python -m llm_tech_matrix.extraction.render --all
"""

# ruff: noqa: RUF001
# This file is intentionally bilingual. Full-width punctuation in the Chinese
# rendering path is a deliberate typography choice, not an ambiguous-unicode bug,
# so RUF001/RUF003 are suppressed at file scope.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from llm_tech_matrix.schema import ExtractedModel

EXTRACTED_DIR = Path("data/extracted")

LANGS: tuple[str, ...] = ("en", "zh")

# All translatable strings used by the renderer.
# Add a key here, then reference it via labels["key"] in render(). Keep the English
# values aligned with the original hand-written rendering.
LABELS: dict[str, dict[str, str]] = {
    "en": {
        # Sections
        "schema_version": "Schema version",
        "overview": "Overview",
        "sources": "Sources",
        "architecture": "Architecture",
        "backbone": "Backbone",
        "attention": "Attention",
        "ffn": "FFN",
        "components": "Components",
        "residual_connections": "Residual connections",
        "parallelism": "Parallelism / infra",
        "training": "Training",
        "training_objectives": "Training objectives (beyond next-token prediction)",
        "alignment": "Alignment",
        "advanced": "Advanced",
        "multimodal": "Multimodal",
        "vision_encoder": "Vision encoder",
        "vision_token_anchors": "Vision token anchors (LM vocab IDs)",
        "inferred_fields": "Inferred fields",
        "open_questions": "Open questions",
        # Overview rows
        "family": "Family",
        "released": "Released",
        "openness": "Openness",
        "params_total": "Total parameters",
        "params_active": "Active parameters",
        # Backbone rows
        "layers": "Layers",
        "hidden_dim": "Hidden dim",
        "context_window": "Context window",
        "context_notes": "Context notes",
        "context_extension": "Context extension",
        "method": "Method",
        "trained_max": "Trained max",
        "extended_max": "Extended max",
        "factor": "Factor",
        "original_max_rope": "Original max (RoPE)",
        "notes": "Notes",
        # Attention rows
        "variant": "Variant",
        "heads": "Heads",
        "kv_heads": "KV heads",
        "head_dim": "Head dim",
        "rope_label": "RoPE",
        "rope_scaling": "RoPE scaling",
        "mla_specific": "MLA-specific",
        "hybrid_attention_variants": "Hybrid attention variants",
        "layer_pattern": "Layer pattern",
        "var_table_header": "| Name | Family | Q heads | KV heads | Head dim | RoPE | Notes |",
        # FFN rows
        "dense_intermediate_size": "Dense intermediate size",
        "moe": "MoE",
        "routed_experts": "Routed experts",
        "active_experts_per_token": "Active experts per token",
        "shared_experts": "Shared experts",
        "per_expert_intermediate_size": "Per-expert intermediate size",
        "routing": "Routing",
        "layer_partition": "Layer partition",
        # Components rows
        "activation": "Activation",
        "normalization": "Normalization",
        "embedding_notes": "Embedding notes",
        # Training rows
        "optimizer": "Optimizer",
        "total_training_tokens": "Total training tokens",
        "lr_schedule": "LR schedule",
        "data_mix": "Data mix",
        "data_mix_notes": "Data mix notes",
        # Objectives
        "mtp_label": "Multi-Token Prediction (MTP)",
        "depth_d": "Depth (D)",
        "loss_weight_schedule": "Loss weight schedule",
        "shared_modules": "Shared modules",
        "fim_label": "Fill-in-Middle (FIM)",
        "format": "Format",
        "rate": "Rate",
        "other_objectives": "Other objectives",
        # Alignment
        "sft": "SFT",
        "rl_method": "RL method",
        "rlaif": "RLAIF",
        "post_training_stages": "Post-training stages",
        "stages_table_header": "| # | Name | Method | Description |",
        "inference_modes": "Inference modes (runtime-switchable)",
        "modes_table_header": "| Name | Trigger | Description |",
        # Advanced
        "self_distillation": "Self-distillation",
        "mixed_precision": "Mixed precision",
        "stability_notes": "Stability tricks",
        # Residual connections
        "rc_kind": "Kind",
        "rc_expansion_factor": "Expansion factor (n_hc)",
        "rc_constraint": "Constraint",
        "rc_iterations": "Solver iterations",
        "rc_dynamic_parameterization": "Dynamic parameterization",
        # Multimodal
        "modalities": "Modalities",
        "fusion": "Fusion",
        "fusion_notes": "Fusion notes",
        # Vision encoder
        "ve_architecture": "Architecture",
        "ve_depth_layers": "Depth (layers)",
        "ve_hidden_size": "Hidden size",
        "ve_intermediate_size": "Intermediate size",
        "ve_num_heads": "Num heads",
        "ve_patch_size": "Patch size",
        "ve_in_channels": "Input channels",
        "ve_output_dim_lm": "Output dim → LM",
        "ve_spatial_merge_size": "Spatial merge size",
        "ve_temporal_patch_size": "Temporal patch size",
        # Audio
        "audio_encoder": "Audio encoder",
        "audio_notes": "Audio notes",
        # Inferred
        "inferred_table_header": "| Field | Basis | Confidence |",
        # Misc
        "none_marker": "_(none)_",
        "openness_open_source": "Open source",
        "openness_open_weights": "Open weights",
        "openness_closed": "Closed",
        "footer_template": (
            "_Generated from `data/extracted/{slug}.json` by "
            "`python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._"
        ),
        "cross_link_template": "> 中文版：[{slug}.zh.md](./{slug}.zh.md)",
        "convention_note": "",  # English version: no convention note
    },
    "zh": {
        # Sections
        "schema_version": "Schema 版本",
        "overview": "概览",
        "sources": "数据源",
        "architecture": "架构",
        "backbone": "骨干网络",
        "attention": "注意力",
        "ffn": "FFN",
        "components": "组件",
        "residual_connections": "残差连接",
        "parallelism": "并行 / 基础设施",
        "training": "训练",
        "training_objectives": "训练目标（next-token prediction 之外）",
        "alignment": "对齐",
        "advanced": "进阶",
        "multimodal": "多模态",
        "vision_encoder": "视觉编码器",
        "vision_token_anchors": "Vision token anchor（LM vocab ID）",
        "inferred_fields": "推断字段（inferred_fields）",
        "open_questions": "待解问题（open_questions）",
        # Overview rows
        "family": "模型家族",
        "released": "发布时间",
        "openness": "开放程度",
        "params_total": "总参数量",
        "params_active": "激活参数量",
        # Backbone rows
        "layers": "层数",
        "hidden_dim": "隐藏维度",
        "context_window": "上下文窗口",
        "context_notes": "上下文说明",
        "context_extension": "上下文扩展",
        "method": "方法",
        "trained_max": "训练最大长度",
        "extended_max": "扩展最大长度",
        "factor": "倍率",
        "original_max_rope": "RoPE 原始最大长度",
        "notes": "说明",
        # Attention rows
        "variant": "变体",
        "heads": "头数",
        "kv_heads": "KV 头数",
        "head_dim": "头维度",
        "rope_label": "RoPE",
        "rope_scaling": "RoPE scaling",
        "mla_specific": "MLA 特有字段",
        "hybrid_attention_variants": "混合注意力变体",
        "layer_pattern": "层模式",
        "var_table_header": "| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |",
        # FFN rows
        "dense_intermediate_size": "Dense 中间维度",
        "moe": "MoE",
        "routed_experts": "可路由专家数",
        "active_experts_per_token": "每 token 激活专家数",
        "shared_experts": "共享专家数",
        "per_expert_intermediate_size": "单专家中间维度",
        "routing": "路由",
        "layer_partition": "层划分",
        # Components rows
        "activation": "激活函数",
        "normalization": "归一化",
        "embedding_notes": "Embedding 说明",
        # Training rows
        "optimizer": "优化器",
        "total_training_tokens": "训练总 token 数",
        "lr_schedule": "学习率调度",
        "data_mix": "数据配比",
        "data_mix_notes": "数据配比说明",
        # Objectives
        "mtp_label": "Multi-Token Prediction (MTP)",
        "depth_d": "深度（D）",
        "loss_weight_schedule": "损失权重调度",
        "shared_modules": "共享模块",
        "fim_label": "Fill-in-Middle (FIM)",
        "format": "格式",
        "rate": "比例",
        "other_objectives": "其他训练目标",
        # Alignment
        "sft": "SFT",
        "rl_method": "RL 方法",
        "rlaif": "RLAIF",
        "post_training_stages": "后训练阶段",
        "stages_table_header": "| # | 名称 | 方法 | 描述 |",
        "inference_modes": "推理模式（runtime 可切换）",
        "modes_table_header": "| 名称 | 触发方式 | 描述 |",
        # Advanced
        "self_distillation": "自蒸馏",
        "mixed_precision": "混合精度",
        "stability_notes": "稳定性 trick",
        # Residual connections
        "rc_kind": "类型",
        "rc_expansion_factor": "扩展因子（n_hc）",
        "rc_constraint": "约束",
        "rc_iterations": "求解迭代数",
        "rc_dynamic_parameterization": "动态参数化",
        # Multimodal
        "modalities": "模态",
        "fusion": "融合方式",
        "fusion_notes": "融合方式说明",
        # Vision encoder
        "ve_architecture": "架构",
        "ve_depth_layers": "层数",
        "ve_hidden_size": "隐藏维度",
        "ve_intermediate_size": "中间维度",
        "ve_num_heads": "头数",
        "ve_patch_size": "patch 大小",
        "ve_in_channels": "输入通道数",
        "ve_output_dim_lm": "输出维度 → LM",
        "ve_spatial_merge_size": "空间合并大小",
        "ve_temporal_patch_size": "时序 patch 大小",
        # Audio
        "audio_encoder": "音频编码器",
        "audio_notes": "音频说明",
        # Inferred
        "inferred_table_header": "| 字段 | 依据 | 置信度 |",
        # Misc
        "none_marker": "_（无）_",
        "openness_open_source": "开源",
        "openness_open_weights": "开放权重",
        "openness_closed": "闭源",
        "footer_template": (
            "_由 `data/extracted/{slug}.json` 通过 "
            "`python -m llm_tech_matrix.extraction.render` 自动生成。"
            "请勿直接编辑此文件——修改 JSON 或渲染器。_"
        ),
        "cross_link_template": "> English: [{slug}.md](./{slug}.md)",
        "convention_note": (
            "_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），"
            "以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_"
        ),
    },
}


def _row(label: str, value: Any) -> str:
    if value is None or value == "":
        value = "—"
    return f"| {label} | {value} |"


def _table(rows: list[tuple[str, Any]]) -> str:
    body = "\n".join(_row(k, v) for k, v in rows)
    return f"| | |\n|---|---|\n{body}"


def _bullets(items: list[str], none_marker: str) -> str:
    if not items:
        return none_marker
    return "\n".join(f"- {item}" for item in items)


def _openness_label(o: str, labels: dict[str, str]) -> str:
    return {
        "open_source": labels["openness_open_source"],
        "open_weights": labels["openness_open_weights"],
        "closed": labels["openness_closed"],
    }.get(o, o)


def _slug_from_name(name: str) -> str:
    return name.lower().replace(" ", "-")


def render(model: ExtractedModel, lang: str = "en", slug: str | None = None) -> str:
    if lang not in LABELS:
        raise ValueError(f"Unsupported lang {lang!r}; expected one of {tuple(LABELS)}")
    labels = LABELS[lang]

    md = model.metadata
    arch = model.architecture
    train = model.training
    # Prefer the caller-supplied slug — render_slug() knows the authoritative
    # filename. Falling back to a slug derived from the display name only
    # round-trips for names without punctuation/spaces.
    if slug is None:
        slug = _slug_from_name(md.name)

    parts: list[str] = []

    # ---- Header ----
    parts.append(f"# {md.name}")
    parts.append("")
    parts.append(labels["cross_link_template"].format(slug=slug))
    parts.append("")
    parts.append(f"*{labels['schema_version']}: {model.schema_version}*")
    parts.append("")
    if labels["convention_note"]:
        parts.append(labels["convention_note"])
        parts.append("")

    # ---- Overview ----
    parts.append(f"## {labels['overview']}")
    parts.append("")
    parts.append(
        _table(
            [
                (labels["family"], md.family),
                (labels["released"], md.release_date),
                (labels["openness"], _openness_label(md.openness, labels)),
                (labels["params_total"], md.params_total),
                (labels["params_active"], md.params_active),
            ]
        )
    )
    parts.append("")

    # ---- Sources ----
    parts.append(f"## {labels['sources']}")
    parts.append("")
    parts.append(_bullets([f"<{u}>" for u in md.sources], labels["none_marker"]))
    parts.append("")

    # ---- Architecture ----
    parts.append(f"## {labels['architecture']}")
    parts.append("")

    parts.append(f"### {labels['backbone']}")
    parts.append("")
    bb = arch.backbone
    parts.append(
        _table(
            [
                (labels["layers"], bb.layers),
                (labels["hidden_dim"], bb.hidden_dim),
                (labels["context_window"], bb.context_window),
            ]
        )
    )
    if bb.context_window_notes:
        parts.append("")
        parts.append(
            f"**{labels['context_notes']}：** {bb.context_window_notes}"
            if lang == "zh"
            else f"**{labels['context_notes']}:** {bb.context_window_notes}"
        )
    if bb.context_extension is not None:
        ce = bb.context_extension
        parts.append("")
        parts.append(
            f"**{labels['context_extension']}：**"
            if lang == "zh"
            else f"**{labels['context_extension']}:**"
        )
        parts.append("")
        parts.append(
            _table(
                [
                    (labels["method"], ce.method),
                    (labels["trained_max"], ce.trained_max),
                    (labels["extended_max"], ce.extended_max),
                    (labels["factor"], ce.factor),
                    (labels["original_max_rope"], ce.original_max),
                ]
            )
        )
        if ce.notes:
            parts.append("")
            parts.append(
                f"_{labels['notes']}：_ {ce.notes}"
                if lang == "zh"
                else f"_{labels['notes']}:_ {ce.notes}"
            )
    parts.append("")

    parts.append(
        f"### {labels['attention']}（{arch.attention.variant}）"
        if lang == "zh"
        else f"### {labels['attention']} ({arch.attention.variant})"
    )
    parts.append("")
    att = arch.attention
    rows: list[tuple[str, Any]] = [
        (labels["variant"], att.variant),
        (labels["heads"], att.num_heads),
        (labels["kv_heads"], att.num_kv_heads),
        (labels["head_dim"], att.head_dim),
    ]
    parts.append(_table(rows))
    parts.append("")

    rope = att.rope
    parts.append(
        f"**{labels['rope_label']}：** type=`{rope.type}`, base=`{rope.base}`"
        if lang == "zh"
        else f"**{labels['rope_label']}:** type=`{rope.type}`, base=`{rope.base}`"
    )
    if rope.scaling:
        parts.append("")
        parts.append(
            f"{labels['rope_scaling']}：" if lang == "zh" else f"{labels['rope_scaling']}:"
        )
        parts.append("")
        parts.append("```json")
        parts.append(json.dumps(rope.scaling, indent=2))
        parts.append("```")
    parts.append("")

    if att.mla is not None:
        parts.append(
            f"**{labels['mla_specific']}：**" if lang == "zh" else f"**{labels['mla_specific']}:**"
        )
        parts.append("")
        parts.append(
            _table(
                [
                    ("kv_lora_rank", att.mla.kv_lora_rank),
                    ("q_lora_rank", att.mla.q_lora_rank),
                    ("qk_nope_head_dim", att.mla.qk_nope_head_dim),
                    ("qk_rope_head_dim", att.mla.qk_rope_head_dim),
                    ("v_head_dim", att.mla.v_head_dim),
                ]
            )
        )
        parts.append("")

    if att.variants:
        parts.append(
            f"**{labels['hybrid_attention_variants']}：**"
            if lang == "zh"
            else f"**{labels['hybrid_attention_variants']}:**"
        )
        parts.append("")
        parts.append(labels["var_table_header"])
        parts.append("|---|---|---|---|---|---|---|")
        for v in att.variants:
            rope_cell = v.rope or "—"
            notes_cell = v.notes or "—"
            parts.append(
                f"| `{v.name}` | `{v.family}` | {v.num_query_heads} | "
                f"{v.num_kv_heads} | {v.head_dim} | {rope_cell} | {notes_cell} |"
            )
        parts.append("")
    if att.layer_pattern:
        parts.append(
            f"**{labels['layer_pattern']}：** {att.layer_pattern}"
            if lang == "zh"
            else f"**{labels['layer_pattern']}:** {att.layer_pattern}"
        )
        parts.append("")

    parts.append(
        f"### {labels['ffn']}（{arch.ffn.ffn_type}）"
        if lang == "zh"
        else f"### {labels['ffn']} ({arch.ffn.ffn_type})"
    )
    parts.append("")
    ffn = arch.ffn
    if ffn.dense_intermediate_size is not None:
        parts.append(
            f"**{labels['dense_intermediate_size']}：** `{ffn.dense_intermediate_size}`"
            if lang == "zh"
            else f"**{labels['dense_intermediate_size']}:** `{ffn.dense_intermediate_size}`"
        )
        parts.append("")
    if ffn.moe is not None:
        parts.append(f"**{labels['moe']}：**" if lang == "zh" else f"**{labels['moe']}:**")
        parts.append("")
        parts.append(
            _table(
                [
                    (labels["routed_experts"], ffn.moe.num_experts),
                    (labels["active_experts_per_token"], ffn.moe.num_active_experts),
                    (labels["shared_experts"], ffn.moe.shared_experts),
                    (labels["per_expert_intermediate_size"], ffn.moe.expert_intermediate_size),
                ]
            )
        )
        parts.append("")
        parts.append(
            f"**{labels['routing']}：** {ffn.moe.routing}"
            if lang == "zh"
            else f"**{labels['routing']}:** {ffn.moe.routing}"
        )
        parts.append("")
    if ffn.layer_partition:
        parts.append(
            f"**{labels['layer_partition']}：** {ffn.layer_partition}"
            if lang == "zh"
            else f"**{labels['layer_partition']}:** {ffn.layer_partition}"
        )
        parts.append("")

    parts.append(f"### {labels['components']}")
    parts.append("")
    parts.append(
        _table(
            [
                (labels["activation"], arch.components.activation),
                (labels["normalization"], arch.components.normalization),
            ]
        )
    )
    parts.append("")
    parts.append(
        f"**{labels['embedding_notes']}：** {arch.components.embedding_notes}"
        if lang == "zh"
        else f"**{labels['embedding_notes']}:** {arch.components.embedding_notes}"
    )
    parts.append("")

    if arch.residual_connections is not None:
        rc = arch.residual_connections
        parts.append(f"### {labels['residual_connections']}")
        parts.append("")
        parts.append(
            _table(
                [
                    (labels["rc_kind"], f"`{rc.kind}`"),
                    (labels["rc_expansion_factor"], rc.expansion_factor),
                    (labels["rc_iterations"], rc.iterations),
                    (labels["rc_dynamic_parameterization"], f"`{rc.dynamic_parameterization}`"),
                ]
            )
        )
        if rc.constraint:
            parts.append("")
            parts.append(
                f"**{labels['rc_constraint']}：** {rc.constraint}"
                if lang == "zh"
                else f"**{labels['rc_constraint']}:** {rc.constraint}"
            )
        if rc.notes:
            parts.append("")
            parts.append(
                f"_{labels['notes']}：_ {rc.notes}"
                if lang == "zh"
                else f"_{labels['notes']}:_ {rc.notes}"
            )
        parts.append("")

    parts.append(f"### {labels['parallelism']}")
    parts.append("")
    parts.append(arch.parallelism_notes)
    parts.append("")

    # ---- Training ----
    parts.append(f"## {labels['training']}")
    parts.append("")
    parts.append(
        _table(
            [
                (labels["optimizer"], train.optimizer),
                (labels["total_training_tokens"], train.data_total_tokens),
            ]
        )
    )
    parts.append("")

    parts.append(
        f"**{labels['lr_schedule']}：** {train.lr_schedule}"
        if lang == "zh"
        else f"**{labels['lr_schedule']}:** {train.lr_schedule}"
    )
    parts.append("")

    if train.data_mix:
        parts.append(
            f"**{labels['data_mix']}：**" if lang == "zh" else f"**{labels['data_mix']}:**"
        )
        parts.append("")
        parts.append(_table(list(train.data_mix.items())))
        parts.append("")
    if train.data_mix_notes:
        parts.append(
            f"**{labels['data_mix_notes']}：** {train.data_mix_notes}"
            if lang == "zh"
            else f"**{labels['data_mix_notes']}:** {train.data_mix_notes}"
        )
        parts.append("")

    # Objectives
    obj = train.objectives
    has_obj = obj.multi_token_prediction is not None or obj.fill_in_middle is not None or obj.other
    if has_obj:
        parts.append(f"### {labels['training_objectives']}")
        parts.append("")
        if obj.multi_token_prediction is not None:
            mtp = obj.multi_token_prediction
            parts.append(
                f"**{labels['mtp_label']}：**" if lang == "zh" else f"**{labels['mtp_label']}:**"
            )
            parts.append("")
            parts.append(
                _table(
                    [
                        (labels["depth_d"], mtp.depth),
                        (labels["loss_weight_schedule"], mtp.loss_weight_schedule),
                    ]
                )
            )
            if mtp.shared_modules:
                parts.append("")
                parts.append(
                    f"_{labels['shared_modules']}：_ {mtp.shared_modules}"
                    if lang == "zh"
                    else f"_{labels['shared_modules']}:_ {mtp.shared_modules}"
                )
            parts.append("")
        if obj.fill_in_middle is not None:
            fim = obj.fill_in_middle
            parts.append(
                f"**{labels['fim_label']}：**" if lang == "zh" else f"**{labels['fim_label']}:**"
            )
            parts.append("")
            parts.append(
                _table(
                    [
                        (labels["format"], fim.format),
                        (labels["rate"], fim.rate),
                    ]
                )
            )
            parts.append("")
        if obj.other:
            parts.append(
                f"**{labels['other_objectives']}：**"
                if lang == "zh"
                else f"**{labels['other_objectives']}:**"
            )
            parts.append("")
            parts.append(_bullets(obj.other, labels["none_marker"]))
            parts.append("")

    parts.append(f"### {labels['alignment']}")
    parts.append("")
    al = train.alignment
    parts.append(
        f"**{labels['sft']}：** {al.sft}" if lang == "zh" else f"**{labels['sft']}:** {al.sft}"
    )
    parts.append("")
    parts.append(
        f"**{labels['rl_method']}：** {al.rl_method}"
        if lang == "zh"
        else f"**{labels['rl_method']}:** {al.rl_method}"
    )
    parts.append("")
    parts.append(
        f"**{labels['rlaif']}：** `{al.rlaif}`"
        if lang == "zh"
        else f"**{labels['rlaif']}:** `{al.rlaif}`"
    )
    parts.append("")

    if al.stages:
        parts.append(
            f"**{labels['post_training_stages']}：**"
            if lang == "zh"
            else f"**{labels['post_training_stages']}:**"
        )
        parts.append("")
        parts.append(labels["stages_table_header"])
        parts.append("|---|---|---|---|")
        for i, s in enumerate(al.stages, start=1):
            parts.append(f"| {i} | {s.name} | `{s.method}` | {s.description} |")
        parts.append("")

    if al.inference_modes:
        parts.append(
            f"**{labels['inference_modes']}：**"
            if lang == "zh"
            else f"**{labels['inference_modes']}:**"
        )
        parts.append("")
        parts.append(labels["modes_table_header"])
        parts.append("|---|---|---|")
        for m in al.inference_modes:
            parts.append(f"| `{m.name}` | {m.trigger} | {m.description} |")
        parts.append("")

    parts.append(f"### {labels['advanced']}")
    parts.append("")
    parts.append(
        f"**{labels['self_distillation']}：** {train.advanced.self_distillation}"
        if lang == "zh"
        else f"**{labels['self_distillation']}:** {train.advanced.self_distillation}"
    )
    parts.append("")
    parts.append(
        f"**{labels['mixed_precision']}：** {train.advanced.mixed_precision}"
        if lang == "zh"
        else f"**{labels['mixed_precision']}:** {train.advanced.mixed_precision}"
    )
    parts.append("")

    if train.stability_notes:
        parts.append(
            f"**{labels['stability_notes']}：** {train.stability_notes}"
            if lang == "zh"
            else f"**{labels['stability_notes']}:** {train.stability_notes}"
        )
        parts.append("")

    # ---- Multimodal ----
    if model.multimodal is not None:
        mm = model.multimodal
        parts.append(f"## {labels['multimodal']}")
        parts.append("")
        modalities_str = ", ".join(mm.modalities) if mm.modalities else "—"
        parts.append(
            _table(
                [
                    (labels["modalities"], modalities_str),
                    (labels["fusion"], f"`{mm.fusion}`"),
                ]
            )
        )
        if mm.fusion_notes:
            parts.append("")
            parts.append(
                f"**{labels['fusion_notes']}：** {mm.fusion_notes}"
                if lang == "zh"
                else f"**{labels['fusion_notes']}:** {mm.fusion_notes}"
            )
        parts.append("")

        if mm.vision_encoder is not None:
            ve = mm.vision_encoder
            parts.append(f"### {labels['vision_encoder']}")
            parts.append("")
            parts.append(
                _table(
                    [
                        (labels["ve_architecture"], ve.architecture),
                        (labels["ve_depth_layers"], ve.depth),
                        (labels["ve_hidden_size"], ve.hidden_size),
                        (labels["ve_intermediate_size"], ve.intermediate_size),
                        (labels["ve_num_heads"], ve.num_heads),
                        (labels["ve_patch_size"], ve.patch_size),
                        (labels["ve_in_channels"], ve.in_channels),
                        (labels["ve_output_dim_lm"], ve.output_dim),
                        (labels["ve_spatial_merge_size"], ve.spatial_merge_size),
                        (labels["ve_temporal_patch_size"], ve.temporal_patch_size),
                    ]
                )
            )
            if ve.notes:
                parts.append("")
                parts.append(
                    f"_{labels['notes']}：_ {ve.notes}"
                    if lang == "zh"
                    else f"_{labels['notes']}:_ {ve.notes}"
                )
            parts.append("")

        if mm.vision_token_anchors is not None:
            va = mm.vision_token_anchors
            parts.append(f"### {labels['vision_token_anchors']}")
            parts.append("")
            parts.append(
                _table(
                    [
                        ("image_token_id", va.image_token_id),
                        ("video_token_id", va.video_token_id),
                        ("vision_start_token_id", va.vision_start_token_id),
                        ("vision_end_token_id", va.vision_end_token_id),
                    ]
                )
            )
            parts.append("")

        if mm.audio_encoder and mm.audio_encoder != "[Unknown/Not Disclosed]":
            parts.append(
                f"**{labels['audio_encoder']}：** {mm.audio_encoder}"
                if lang == "zh"
                else f"**{labels['audio_encoder']}:** {mm.audio_encoder}"
            )
            if mm.audio_notes:
                parts.append("")
                parts.append(
                    f"_{labels['audio_notes']}：_ {mm.audio_notes}"
                    if lang == "zh"
                    else f"_{labels['audio_notes']}:_ {mm.audio_notes}"
                )
            parts.append("")

    # ---- Inferred fields & open questions ----
    if model.inferred_fields:
        parts.append(f"## {labels['inferred_fields']}")
        parts.append("")
        parts.append(labels["inferred_table_header"])
        parts.append("|---|---|---|")
        for inf in model.inferred_fields:
            parts.append(f"| `{inf.field}` | {inf.basis} | {inf.confidence} |")
        parts.append("")

    if model.open_questions:
        parts.append(f"## {labels['open_questions']}")
        parts.append("")
        parts.append(_bullets(model.open_questions, labels["none_marker"]))
        parts.append("")

    # ---- Footer ----
    parts.append("---")
    parts.append("")
    parts.append(labels["footer_template"].format(slug=slug))
    parts.append("")

    return "\n".join(parts)


def render_slug(slug: str) -> list[Path]:
    """Render <slug>.md AND <slug>.zh.md from data/extracted/<slug>.json. Returns both paths."""
    json_path = EXTRACTED_DIR / f"{slug}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No extracted JSON at {json_path}")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    model = ExtractedModel.model_validate(data)

    written: list[Path] = []
    for lang in LANGS:
        suffix = ".md" if lang == "en" else ".zh.md"
        out = EXTRACTED_DIR / f"{slug}{suffix}"
        out.write_text(render(model, lang=lang, slug=slug), encoding="utf-8")
        written.append(out)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m llm_tech_matrix.extraction.render",
        description=(
            "Render extracted model JSON(s) to Markdown summaries. "
            "Each slug produces both <slug>.md (English) and <slug>.zh.md (Chinese chrome)."
        ),
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
            for path in render_slug(slug):
                print(f"  rendered  {path}")
        return 0

    if not args.slug:
        parser.error("slug is required (or pass --all)")
    for path in render_slug(args.slug):
        print(f"Rendered {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
