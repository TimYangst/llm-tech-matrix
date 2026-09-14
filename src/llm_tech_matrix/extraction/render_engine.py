"""Render an engine snapshot JSON to Markdown (English and Chinese chrome).

Engine counterpart of `render.py`: a deterministic view of
`data/extracted/engines/<slug>.json`, written to `<slug>.md` and `<slug>.zh.md` next to it.
Values stay in source-language English; only headers and labels are translated. Evidence
URLs render as short `file#Lnn` links so every claim stays one click from its source.

CLI:
    uv run python -m llm_tech_matrix.extraction.render_engine <slug>
    uv run python -m llm_tech_matrix.extraction.render_engine --all
"""

# ruff: noqa: RUF001
# Bilingual renderer: full-width punctuation in the Chinese labels is deliberate.

from __future__ import annotations

import argparse
import json
import sys
from functools import partial
from pathlib import Path

from llm_tech_matrix.engine_schema import UNKNOWN, EngineRecord

ENGINES_DIR = Path("data/extracted/engines")
PLAIN_LISTS = frozenset({"api_surfaces", "workloads"})
LANGS: tuple[str, ...] = ("en", "zh")

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "lang_link": "> 中文版：[{slug}.zh.md](./{slug}.zh.md)",
        "schema_version": "Engine schema version",
        "overview": "Overview",
        "field": "Field",
        "value": "Value",
        "repository": "Repository",
        "license": "License",
        "release_tag": "Release tag",
        "commit": "Commit",
        "release_date": "Release date",
        "snapshot_date": "Snapshot date",
        "roles": "Roles",
        "hardware": "Hardware",
        "parallelism": "Parallelism",
        "par_header": "| Dimension | Supported | Implementation | Notes | Evidence |",
        "serving": "Serving",
        "api_surfaces": "API surfaces",
        "scheduler": "Scheduler",
        "kv_cache_management": "KV cache management",
        "prefix_caching": "Prefix caching",
        "disaggregation": "Disaggregation",
        "speculative_decoding_methods": "Speculative decoding methods",
        "quantization_methods": "Quantization methods",
        "kv_cache_dtypes": "KV cache dtypes",
        "attention_backends": "Attention backends",
        "reasoning_parsers": "Reasoning parsers",
        "tool_call_parsers": "Tool-call parsers",
        "training": "Training",
        "workloads": "Workloads",
        "backends": "Training backends",
        "optimizers": "Optimizers",
        "mixed_precision": "Mixed precision",
        "quantization_aware_training": "Quantization-aware training",
        "checkpointing": "Checkpointing",
        "lora": "LoRA",
        "kernels": "Kernels",
        "rl": "RL post-training",
        "algorithms": "Algorithms",
        "policy_losses": "Policy losses",
        "rollout_backends": "Rollout backends",
        "trainer_modes": "Trainer modes",
        "weight_sync": "Weight sync",
        "weight_sync_backends": "Weight-sync backends",
        "routing_replay": "Routing replay",
        "reward": "Reward",
        "distillation": "Distillation",
        "notes": "Notes",
        "evidence": "Evidence",
        "integrations": "Integrations",
        "int_header": "| Name | Relation | Version constraints | Notes | Evidence |",
        "model_support": "Model support",
        "ms_header": "| Architecture | Model records | Support | Documented | Features | Spec. decoding | Evidence |",
        "ms_notes": "Row notes",
        "md_title": "Per-model details",
        "md_header": "| Model record | Since | Reasoning parser | Tool parser | Notes | Evidence |",
        "technique_support": "Technique support",
        "ts_header": "| Glossary entry | Implementation | Flags | Since | Evidence |",
        "open_questions": "Open questions",
        "sources": "Sources",
        "none": "_None._",
        "unknown": "_unknown_",
        "dims": "tensor=Tensor|pipeline=Pipeline|data=Data|expert=Expert|context=Context|sequence=Sequence",
    },
    "zh": {
        "lang_link": "> English: [{slug}.md](./{slug}.md)",
        "schema_version": "引擎 schema 版本",
        "overview": "概览",
        "field": "字段",
        "value": "值",
        "repository": "仓库",
        "license": "许可证",
        "release_tag": "发布 tag",
        "commit": "Commit",
        "release_date": "发布日期",
        "snapshot_date": "快照日期",
        "roles": "角色",
        "hardware": "硬件平台",
        "parallelism": "并行方式",
        "par_header": "| 维度 | 是否支持 | 实现方式 | 说明 | 证据 |",
        "serving": "推理服务",
        "api_surfaces": "API 接口",
        "scheduler": "调度",
        "kv_cache_management": "KV cache 管理",
        "prefix_caching": "前缀缓存",
        "disaggregation": "分离式部署",
        "speculative_decoding_methods": "投机解码方法",
        "quantization_methods": "量化方法",
        "kv_cache_dtypes": "KV cache 数据类型",
        "attention_backends": "Attention 后端",
        "reasoning_parsers": "Reasoning parser",
        "tool_call_parsers": "Tool-call parser",
        "training": "训练",
        "workloads": "训练类型",
        "backends": "训练后端",
        "optimizers": "优化器",
        "mixed_precision": "混合精度",
        "quantization_aware_training": "量化感知训练",
        "checkpointing": "Checkpoint",
        "lora": "LoRA",
        "kernels": "算子",
        "rl": "RL 后训练",
        "algorithms": "算法",
        "policy_losses": "Policy loss",
        "rollout_backends": "Rollout 后端",
        "trainer_modes": "Trainer 模式",
        "weight_sync": "权重同步",
        "weight_sync_backends": "权重同步后端",
        "routing_replay": "路由回放",
        "reward": "奖励",
        "distillation": "蒸馏",
        "notes": "说明",
        "evidence": "证据",
        "integrations": "集成",
        "int_header": "| 名称 | 关系 | 版本约束 | 说明 | 证据 |",
        "model_support": "模型支持",
        "ms_header": "| 架构 | 模型记录 | 支持程度 | 文档列出 | 特性 | 投机解码 | 证据 |",
        "ms_notes": "逐行说明",
        "md_title": "逐模型信息",
        "md_header": "| 模型记录 | 起始版本 | Reasoning parser | Tool parser | 说明 | 证据 |",
        "technique_support": "技术实现",
        "ts_header": "| Glossary 条目 | 实现方式 | 参数 | 起始版本 | 证据 |",
        "open_questions": "开放问题",
        "sources": "来源",
        "none": "_无。_",
        "unknown": "_未知_",
        "dims": "tensor=张量并行|pipeline=流水线并行|data=数据并行|expert=专家并行|context=上下文并行|sequence=序列并行",
    },
}


def _cell(value: object, unknown: str = "_unknown_") -> str:
    """Table-safe cell: empty becomes an em dash, UNKNOWN a label, pipes and newlines escaped."""
    if value is None or value == "" or value == [] or value == {}:
        return "—"
    if isinstance(value, bool):
        return "✓" if value else "✗"
    if isinstance(value, list):
        value = ", ".join(f"`{v}`" for v in value)
    elif isinstance(value, dict):
        value = ", ".join(f"{k}: {v}" for k, v in value.items())
    text = str(value)
    if text == UNKNOWN:
        return unknown
    return text.replace("|", "\\|").replace("\n", " ")


def _links(urls: list[str]) -> str:
    """Short link labels: `registry.py#L93` for blob URLs, `release notes` for release pages."""
    out = [
        f"[{'release notes' if '/releases/tag/' in url else url.rsplit('/', 1)[-1]}]({url})"
        for url in urls
    ]
    return ", ".join(out) if out else "—"


def render(record: EngineRecord, lang: str, slug: str) -> str:
    labels = LABELS[lang]
    cell = partial(_cell, unknown=labels["unknown"])
    meta = record.metadata
    colon = "：" if lang == "zh" else ":"
    parts: list[str] = [
        f"# {meta.name} {meta.release_tag}",
        "",
        labels["lang_link"].format(slug=slug),
        "",
    ]
    parts += [f"*{labels['schema_version']}{colon} {record.engine_schema_version}*", ""]

    parts += [
        f"## {labels['overview']}",
        "",
        f"| {labels['field']} | {labels['value']} |",
        "|---|---|",
    ]
    rows = [
        ("repository", meta.repository),
        ("license", meta.license),
        ("release_tag", f"`{meta.release_tag}`"),
        ("commit", f"`{meta.commit_sha}`"),
        ("release_date", meta.release_date),
        ("snapshot_date", meta.snapshot_date),
        ("roles", meta.roles),
        ("hardware", ", ".join(meta.hardware)),
    ]
    parts += [f"| {labels[k]} | {cell(v)} |" for k, v in rows]
    parts.append("")

    dims = dict(pair.split("=") for pair in labels["dims"].split("|"))
    parts += [f"## {labels['parallelism']}", "", labels["par_header"], "|---|---|---|---|---|"]
    for name in type(record.parallelism).model_fields:
        entry = getattr(record.parallelism, name)
        parts.append(
            f"| {dims[name]} | {cell(entry.supported)} | {cell(entry.implementation)} | "
            f"{cell(entry.notes)} | {_links(entry.evidence)} |"
        )
    parts.append("")

    for attr in ("serving", "training", "rl"):
        section = getattr(record, attr)
        if section is None:
            continue
        parts += [f"## {labels[attr]}", ""]
        prose = [
            n for n, f in type(section).model_fields.items() if f.annotation is str and n != "notes"
        ]
        lists = [n for n, f in type(section).model_fields.items() if f.annotation == list[str]]
        for name in prose + lists:
            value = getattr(section, name)
            if not value or value == UNKNOWN:
                continue
            if isinstance(value, list):
                shown = (
                    ", ".join(value) if name in PLAIN_LISTS else ", ".join(f"`{v}`" for v in value)
                )
                parts += [f"**{labels[name]}** ({len(value)}){colon} {shown}", ""]
            else:
                parts += [f"**{labels[name]}{colon}** {value}", ""]
            parts += [f"_{labels['evidence']}{colon}_ {_links(section.evidence.get(name, []))}", ""]
        if section.notes:
            parts += [f"_{labels['notes']}{colon}_ {section.notes}", ""]

    parts += [f"## {labels['integrations']}", ""]
    if record.integrations:
        parts += [labels["int_header"], "|---|---|---|---|---|"]
        parts += [
            f"| {i.name}{f' ([`{i.engine_slug}`](./{i.engine_slug}.md))' if i.engine_slug else ''} "
            f"| `{i.relation}` | {cell('<br>'.join(i.version_constraints))} | {cell(i.notes)} | "
            f"{_links(i.evidence)} |"
            for i in record.integrations
        ]
    else:
        parts.append(labels["none"])
    parts.append("")

    parts += [f"## {labels['model_support']}", ""]
    if record.model_support:
        parts += [labels["ms_header"], "|---|---|---|---|---|---|---|"]
        for m in record.model_support:
            slugs = ", ".join(f"[`{x}`](../{x}.md)" for x in m.model_slugs) or "—"
            support = f"`{m.support}`"
            if m.delegated_to:
                support += f" → [`{m.delegated_to}`](./{m.delegated_to}.md)"
            parts.append(
                f"| `{m.hf_architecture}` | {slugs} | {support} | "
                f"{cell(m.documented)} | {cell(m.features)} | {cell(m.speculative_decoding)} | "
                f"{_links(m.evidence)} |"
            )
        parts.append("")
        details = [d for m in record.model_support for d in m.model_details]
        if details:
            parts += [
                f"### {labels['md_title']}",
                "",
                labels["md_header"],
                "|---|---|---|---|---|---|",
            ]
            parts += [
                f"| [`{d.model_slug}`](../{d.model_slug}.md) | {cell(d.since_version)} | "
                f"{cell(d.reasoning_parser)} | {cell(d.tool_call_parser)} | {cell(d.notes)} | "
                f"{_links(d.evidence)} |"
                for d in details
            ]
            parts.append("")
        parts += [f"### {labels['ms_notes']}", ""]
        parts += [
            f"- **`{m.hf_architecture}`** — {m.notes}" for m in record.model_support if m.notes
        ]
    else:
        parts.append(labels["none"])
    parts.append("")

    parts += [f"## {labels['technique_support']}", ""]
    if record.technique_support:
        parts += [labels["ts_header"], "|---|---|---|---|---|"]
        for t in record.technique_support:
            flags = "<br>".join(f"`{f}`" for f in t.flags).replace("|", "\\|") or "—"
            parts.append(
                f"| [{t.glossary_slug}](../../../docs/glossary/{t.glossary_slug}.md) | "
                f"{cell(t.implementation)} | {flags} | {cell(t.since_version)} | {_links(t.evidence)} |"
            )
        parts.append("")
        parts += [
            f"- **{t.glossary_slug}** — {t.notes}" for t in record.technique_support if t.notes
        ]
    else:
        parts.append(labels["none"])
    parts.append("")

    parts += [f"## {labels['open_questions']}", ""]
    parts += [f"- {q}" for q in record.open_questions] or [labels["none"]]
    parts.append("")

    parts += [f"## {labels['sources']}", ""]
    parts += [f"- <{u}>" for u in meta.sources]
    parts.append("")
    return "\n".join(parts)


def render_slug(slug: str) -> list[Path]:
    json_path = ENGINES_DIR / f"{slug}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No engine snapshot JSON at {json_path}")
    record = EngineRecord.model_validate(json.loads(json_path.read_text(encoding="utf-8")))
    written = []
    for lang in LANGS:
        out = ENGINES_DIR / (f"{slug}.md" if lang == "en" else f"{slug}.zh.md")
        out.write_text(render(record, lang, slug), encoding="utf-8")
        written.append(out)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m llm_tech_matrix.extraction.render_engine",
        description="Render engine snapshot JSON(s) to <slug>.md and <slug>.zh.md.",
    )
    parser.add_argument("slug", nargs="?", help="Engine snapshot slug. Required unless --all.")
    parser.add_argument("--all", action="store_true", help="Render every engine snapshot")
    args = parser.parse_args(argv)
    if args.all:
        for slug in sorted(p.stem for p in ENGINES_DIR.glob("*.json")):
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
