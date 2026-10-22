"""Render media records deterministically in English and Chinese.

Usage: uv run python -m llm_tech_matrix.extraction.render_media --all [--check]
"""

# ruff: noqa: RUF001

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from llm_tech_matrix.media_schema import MediaRecord

MEDIA_DIR = Path("data/extracted/media")
LANGS = ("en", "zh")
LABELS = {
    "en": {
        "metadata": "Release identity and scope",
        "generation": "Generation",
        "architecture": "Architecture",
        "output": "Output",
        "training": "Training",
        "precision": "Precision",
        "release": "Release artifacts and limitations",
        "open_questions": "Open questions",
        "sources": "Sources",
        "field": "Field",
        "value": "Value",
        "evidence": "Evidence",
        "schema": "Media schema version",
        "name": "Name",
        "family": "Family",
        "organization": "Organization",
        "release_date": "Release date",
        "openness": "Openness",
        "license": "License",
        "variant_policy": "Variant policy",
        "input_modalities": "Input modalities",
        "output_modalities": "Output modalities",
        "tasks": "Tasks",
        "objective": "Objective",
        "scheduler": "Scheduler",
        "sampling": "Sampling",
        "backbone": "Backbone",
        "parameters": "Parameters",
        "attention": "Attention",
        "conditioning": "Conditioning",
        "vae": "VAE",
        "audio_codec": "Audio codec",
        "multimodal_coupling": "Multimodal coupling",
        "implementation": "Implementation",
        "resolution": "Resolution",
        "frame_rate": "Frame rate",
        "duration": "Duration",
        "sample_rate": "Audio sample rate",
        "channels": "Audio channels",
        "formats": "Formats",
        "data": "Training data",
        "pretraining": "Pretraining",
        "post_training": "Post-training",
        "weights": "Weight precision",
        "compute": "Compute precision",
        "quantization": "Quantization",
        "artifacts": "Released artifacts",
        "hosted_scope": "Hosted pipeline scope",
        "limitations": "Limitations",
        "none": "None recorded.",
    },
    "zh": {
        "metadata": "发布信息与范围",
        "generation": "生成机制",
        "architecture": "架构",
        "output": "输出",
        "training": "训练",
        "precision": "精度",
        "release": "发布产物与限制",
        "open_questions": "开放问题",
        "sources": "来源",
        "field": "字段",
        "value": "值",
        "evidence": "证据",
        "schema": "媒体 schema 版本",
        "name": "名称",
        "family": "系列",
        "organization": "组织",
        "release_date": "发布日期",
        "openness": "开放程度",
        "license": "许可证",
        "variant_policy": "变体范围",
        "input_modalities": "输入模态",
        "output_modalities": "输出模态",
        "tasks": "任务",
        "objective": "生成目标",
        "scheduler": "调度器",
        "sampling": "采样",
        "backbone": "主干网络",
        "parameters": "参数量",
        "attention": "注意力",
        "conditioning": "条件输入",
        "vae": "VAE",
        "audio_codec": "音频编解码器",
        "multimodal_coupling": "多模态耦合",
        "implementation": "实现",
        "resolution": "分辨率",
        "frame_rate": "帧率",
        "duration": "时长",
        "sample_rate": "音频采样率",
        "channels": "音频声道",
        "formats": "格式",
        "data": "训练数据",
        "pretraining": "预训练",
        "post_training": "后训练",
        "weights": "权重精度",
        "compute": "计算精度",
        "quantization": "量化",
        "artifacts": "已发布产物",
        "hosted_scope": "托管流程范围",
        "limitations": "限制",
        "none": "暂无记录。",
    },
}


def _cell(value: object) -> str:
    if value == []:
        return "—"
    if isinstance(value, list):
        value = "; ".join(value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def _links(urls: list[str]) -> str:
    return ", ".join(f"[source {i}]({url})" for i, url in enumerate(urls, 1)) or "—"


def render(record: MediaRecord, lang: str, slug: str) -> str:
    labels = LABELS[lang]
    other = (
        f"> 中文版：[{slug}.zh.md](./{slug}.zh.md)"
        if lang == "en"
        else f"> English: [{slug}.md](./{slug}.md)"
    )
    parts = [
        f"# {record.metadata.name}",
        "",
        other,
        "",
        f"*{labels['schema']}: {record.media_schema_version}*",
        "",
    ]
    for name in (
        "metadata",
        "generation",
        "architecture",
        "output",
        "training",
        "precision",
        "release",
    ):
        section = getattr(record, name)
        parts += [
            f"## {labels[name]}",
            "",
            f"| {labels['field']} | {labels['value']} | {labels['evidence']} |",
            "|---|---|---|",
        ]
        for field in type(section).model_fields:
            if field in {"evidence", "sources"}:
                continue
            parts.append(
                f"| {labels[field]} | {_cell(getattr(section, field))} | {_links(section.evidence.get(field, []))} |"
            )
        parts.append("")
    parts += [f"## {labels['open_questions']}", ""]
    parts += [f"- {question}" for question in record.open_questions] or [labels["none"]]
    parts += ["", f"## {labels['sources']}", ""]
    parts += [f"- [Source {i}]({url})" for i, url in enumerate(record.metadata.sources, 1)]
    return "\n".join(parts) + "\n"


def rendered_files(directory: Path = MEDIA_DIR) -> dict[Path, str]:
    outputs = {}
    for path in sorted(directory.glob("*.json")):
        record = MediaRecord.model_validate_json(path.read_text(encoding="utf-8"))
        for lang in LANGS:
            suffix = ".md" if lang == "en" else ".zh.md"
            outputs[path.with_suffix(suffix)] = render(record, lang, path.stem)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check", action="store_true", help="Fail on missing or stale views")
    args = parser.parse_args(argv)
    if not args.all and not args.slug:
        parser.error("slug is required (or pass --all)")
    if args.slug and not (MEDIA_DIR / f"{args.slug}.json").is_file():
        parser.error(f"no media record for {args.slug!r}")
    stale = []
    for path, content in rendered_files().items():
        if args.slug and path.name not in {f"{args.slug}.md", f"{args.slug}.zh.md"}:
            continue
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Rendered {path}")
    if stale:
        print("Missing or stale media views: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
