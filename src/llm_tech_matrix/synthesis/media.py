"""Generate a separate media release index from validated extraction JSON only.

Usage: uv run python -m llm_tech_matrix.synthesis.media [--check]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from llm_tech_matrix.media_schema import MediaRecord

MEDIA_DIR = Path("data/extracted/media")


def _cell(value: object) -> str:
    if value == []:
        return "—"
    if isinstance(value, list):
        value = "; ".join(value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_index(directory: Path = MEDIA_DIR, lang: str = "en") -> str:
    zh = lang == "zh"
    title = "媒体生成模型索引" if zh else "Media generation model index"
    note = (
        "由媒体提取 JSON 自动生成。开放范围、输出限制和托管组件的区别见各模型记录。"
        if zh
        else "Generated from media extraction JSON. Each record distinguishes released weights, output limits and hosted pipeline components."
    )
    header = (
        "| 模型 | 系列 | 日期 | 开放程度 | 输入 → 输出 | 已发布产物 |"
        if zh
        else "| Model | Family | Date | Openness | Input → output | Released artifacts |"
    )
    suffix = ".zh.md" if zh else ".md"
    parts = [f"# {title}", "", note, "", header, "|---|---|---|---|---|---|"]
    for path in sorted(directory.glob("*.json")):
        record = MediaRecord.model_validate_json(path.read_text(encoding="utf-8"))
        meta = record.metadata
        modalities = f"{', '.join(record.generation.input_modalities)} → {', '.join(record.generation.output_modalities)}"
        parts.append(
            f"| [{_cell(meta.name)}](./{path.stem}{suffix}) | {_cell(meta.family)} | {_cell(meta.release_date)} | {_cell(meta.openness)} | {_cell(modalities)} | {_cell(record.release.artifacts)} |"
        )
    return "\n".join(parts) + "\n"


def generated_files(directory: Path = MEDIA_DIR) -> dict[Path, str]:
    return {
        directory / "README.md": render_index(directory, "en"),
        directory / "README.zh.md": render_index(directory, "zh"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    stale = []
    for path, content in generated_files().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Generated {path}")
    if stale:
        print("Missing or stale media index: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
