"""Generate hardware configuration and compute tables without cross-precision rankings.

Usage: uv run python -m llm_tech_matrix.synthesis.hardware [--check]
"""

# ruff: noqa: RUF001
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from llm_tech_matrix.extraction.render_hardware import HARDWARE_DIR, cell, links
from llm_tech_matrix.hardware_schema import UNKNOWN, HardwareRecord


def render_index(directory: Path = HARDWARE_DIR, lang: str = "en") -> str:
    zh = lang == "zh"
    parts = [
        "# 公开 AI 加速器索引" if zh else "# Public AI accelerator index",
        "",
        (
            "由公开硬件 JSON 生成，按文件名排序。GB/TB 为十进制；GiB 保留厂商原始单位。理论峰值不是应用实测或可直接比较的排名。每个峰值保留精度、运算类型、稀疏条件和范围；完整条件、累加精度、FMA 口径与证据见详情。"
            if zh
            else "Generated from public hardware JSON, sorted by filename. GB/TB are decimal; published GiB values retain their unit. Theoretical peaks are not application measurements or a ranking. Each peak retains precision, operation, sparsity and scope; see each record for full conditions, accumulation precision, FMA counting and evidence."
        ),
        "",
        "## 配置" if zh else "## Configuration",
        "",
        "| 器件 | 厂商 | 类型 | 变体/范围 | 架构 | 内存容量 | 带宽（TB/s） | TDP（W） |"
        if zh
        else "| Device | Vendor | Type | Variant / scope | Architecture | Memory capacity | Bandwidth (TB/s) | TDP (W) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    records = []
    suffix = ".zh.md" if zh else ".md"
    for path in sorted(directory.glob("*.json")):
        record = HardwareRecord.model_validate_json(path.read_text(encoding="utf-8"))
        records.append((path, record))
        meta = record.metadata
        capacity = (
            f"{record.memory.capacity_gb} GB"
            if record.memory.capacity_gb != UNKNOWN
            else (
                f"{record.memory.capacity_gib} GiB"
                if record.memory.capacity_gib != UNKNOWN
                else UNKNOWN
            )
        )
        parts.append(
            f"| [{cell(meta.name)}](./{path.stem}{suffix}) | {cell(meta.vendor)} | {meta.accelerator_type} | {cell(meta.variant)} / {meta.record_scope} | {cell(record.architecture.family)} | {capacity} | {record.memory.bandwidth_tb_s} | {record.power.tdp_w} |"
        )
    parts += [
        "",
        "## 理论峰值（完整条件见详情）"
        if zh
        else "## Theoretical peaks (full conditions in each record)",
        "",
        "| 器件 | 精度 | 运算 | 速率 | 单位 | 稀疏条件 | 范围 | 条件 | 证据 |"
        if zh
        else "| Device | Precision | Operation | Rate | Unit | Sparsity | Scope | Conditions | Evidence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for path, record in records:
        for peak in record.compute.peaks:
            parts.append(
                f"| [{cell(record.metadata.name)}](./{path.stem}{suffix}) | {cell(peak.precision)} | {peak.operation} | {peak.throughput} | {peak.unit} | {peak.sparsity} | {peak.scope} | {cell(peak.conditions)} | {links(peak.evidence)} |"
            )
    return "\n".join(parts) + "\n"


def generated_files(directory: Path = HARDWARE_DIR) -> dict[Path, str]:
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
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Generated {path}")
    if stale:
        print("Missing or stale hardware index: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
