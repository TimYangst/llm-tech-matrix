"""Render public hardware snapshots as deterministic bilingual Markdown.

Usage: uv run python -m llm_tech_matrix.extraction.render_hardware --all [--check]
"""

# ruff: noqa: RUF001
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from llm_tech_matrix.hardware_schema import HardwareRecord

HARDWARE_DIR = Path("data/extracted/hardware")
FIELDS = {
    "metadata": ("Identity and scope", "身份与范围"),
    "architecture": ("Architecture", "架构"),
    "memory": ("Memory", "内存"),
    "compute": ("Theoretical compute peaks", "理论计算峰值"),
    "interconnect": ("Interconnect", "互连"),
    "power": ("Power", "功耗"),
    "software": ("Software", "软件"),
    "public_measurements": ("Published measurements", "公开实测"),
    "open_questions": ("Open questions", "开放问题"),
    "name": ("Name", "名称"),
    "vendor": ("Vendor", "厂商"),
    "accelerator_type": ("Accelerator type", "加速器类型"),
    "variant": ("Variant", "变体"),
    "form_factor": ("Form factor", "形态"),
    "record_scope": ("Record scope", "记录范围"),
    "device_count": ("Device count", "器件数"),
    "snapshot_date": ("Snapshot date", "快照日期"),
    "family": ("Family", "系列"),
    "process": ("Process", "制程"),
    "compute_units": ("Compute units", "计算单元"),
    "cache": ("Cache", "缓存"),
    "on_chip_memory": ("On-chip memory", "片上存储"),
    "execution_model": ("Execution model", "执行模型"),
    "notes": ("Notes", "说明"),
    "technology": ("Technology", "存储技术"),
    "capacity_gb": ("Capacity (GB)", "容量（GB）"),
    "capacity_gib": ("Capacity (GiB)", "容量（GiB）"),
    "bandwidth_tb_s": ("Bandwidth (TB/s)", "带宽（TB/s）"),
    "scope": ("Scope", "范围"),
    "host": ("Host", "主机接口"),
    "scale_up": ("Scale up", "机内扩展"),
    "scale_out": ("Scale out", "跨机扩展"),
    "topology": ("Topology", "拓扑"),
    "tdp_w": ("TDP (W)", "TDP（W）"),
    "ecosystem": ("Ecosystem", "生态"),
    "isa": ("ISA", "指令集"),
    "programming_model": ("Programming model", "编程模型"),
    "precision": ("Precision", "精度"),
    "operation": ("Operation", "运算类型"),
    "throughput": ("Rate", "速率"),
    "unit": ("Unit", "单位"),
    "sparsity": ("Sparsity", "稀疏条件"),
    "accumulation": ("Accumulation", "累加精度"),
    "conditions": ("Conditions", "条件"),
    "fma_counting": ("FMA counting", "FMA 计数"),
    "evidence": ("Evidence", "证据"),
    "benchmark": ("Benchmark", "基准"),
    "metric": ("Metric", "指标"),
    "value": ("Value", "值"),
    "configuration": ("Configuration", "配置"),
}


def label(field: str, lang: str) -> str:
    return FIELDS[field][lang == "zh"]


def cell(value: object) -> str:
    if value == []:
        return "—"
    if isinstance(value, list):
        value = "; ".join(str(v) for v in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def links(urls: list[str]) -> str:
    return ", ".join(f"[source {i}]({url})" for i, url in enumerate(urls, 1)) or "—"


def _row_table(rows: list, fields: tuple[str, ...], lang: str) -> list[str]:
    parts = ["| " + " | ".join(label(f, lang) for f in fields) + " |", "|" + "---|" * len(fields)]
    for row in rows:
        parts.append(
            "| "
            + " | ".join(
                links(row.evidence) if f == "evidence" else cell(getattr(row, f)) for f in fields
            )
            + " |"
        )
    return parts


def render(record: HardwareRecord, lang: str, slug: str) -> str:
    zh = lang == "zh"
    other = (
        f"> English: [{slug}.md](./{slug}.md)"
        if zh
        else f"> 中文版：[{slug}.zh.md](./{slug}.zh.md)"
    )
    note = (
        "仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。"
        if zh
        else "Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred."
    )
    parts = [
        f"# {record.metadata.name}",
        "",
        other,
        "",
        note,
        "",
        f"*Hardware schema: {record.hardware_schema_version}*",
        "",
    ]
    for name in (
        "metadata",
        "architecture",
        "memory",
        "compute",
        "interconnect",
        "power",
        "software",
    ):
        section = getattr(record, name)
        parts += [
            f"## {label(name, lang)}",
            "",
            "| 字段 | 值 | 证据 |" if zh else "| Field | Value | Evidence |",
            "|---|---|---|",
        ]
        for field in type(section).model_fields:
            if field in {"evidence", "sources", "peaks"}:
                continue
            parts.append(
                f"| {label(field, lang)} | {cell(getattr(section, field))} | {links(section.evidence.get(field, []))} |"
            )
        parts.append("")
        if name == "compute" and record.compute.peaks:
            parts += _row_table(
                record.compute.peaks,
                (
                    "precision",
                    "operation",
                    "throughput",
                    "unit",
                    "sparsity",
                    "scope",
                    "accumulation",
                    "conditions",
                    "fma_counting",
                    "evidence",
                ),
                lang,
            )
            parts.append("")
    parts += [f"## {label('public_measurements', lang)}", ""]
    if record.public_measurements:
        parts += _row_table(
            record.public_measurements,
            (
                "benchmark",
                "metric",
                "value",
                "unit",
                "scope",
                "configuration",
                "conditions",
                "evidence",
            ),
            lang,
        )
    else:
        parts += ["暂无公开实测记录。" if zh else "No published measurements recorded."]
    parts += ["", f"## {label('open_questions', lang)}", ""]
    parts += [f"- {q}" for q in record.open_questions] or ["暂无记录。" if zh else "None recorded."]
    parts += ["", "## 来源" if zh else "## Sources", ""]
    parts += [f"- [Source {i}]({url})" for i, url in enumerate(record.metadata.sources, 1)]
    return "\n".join(parts) + "\n"


def rendered_files(directory: Path = HARDWARE_DIR) -> dict[Path, str]:
    outputs = {}
    for path in sorted(directory.glob("*.json")):
        record = HardwareRecord.model_validate_json(path.read_text(encoding="utf-8"))
        for lang in ("en", "zh"):
            outputs[path.with_suffix(".md" if lang == "en" else ".zh.md")] = render(
                record, lang, path.stem
            )
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.all and not args.slug:
        parser.error("slug is required (or pass --all)")
    if args.slug and not (HARDWARE_DIR / f"{args.slug}.json").is_file():
        parser.error(f"No hardware record for {args.slug!r}")
    stale = []
    for path, content in rendered_files().items():
        if args.slug and path.name not in {f"{args.slug}.md", f"{args.slug}.zh.md"}:
            continue
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Rendered {path}")
    if stale:
        print("Missing or stale hardware views: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
