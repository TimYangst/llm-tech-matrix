"""One-shot migration: engine schema v1 → v2.

v2 moves `reasoning_parser`, `tool_call_parser` and `since_version` from the architecture-level
`model_support[]` row into per-model `model_support[].model_details[]`, because those facts
vary between models that share an architecture (surfaced by the sglang-v0.5.19 snapshot).

For each data/extracted/engines/<slug>.json:
- Bump engine_schema_version to 2.
- For every row whose v1 row-level values are populated, emit one `model_details` entry per
  model slug the value was stated for, carrying the evidence URLs that back that value
  (matched by the doc / release page they point at). Rows with several model slugs and a
  populated value need an explicit slug decision, so the script refuses to guess.
- Drop the three row-level fields.

Idempotent: v2 records pass through unchanged.

Usage:
    uv run python scripts/migrate_engine_v1_to_v2.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINES_DIR = Path(__file__).resolve().parent.parent / "data" / "extracted" / "engines"
UNKNOWN = "[Unknown/Not Disclosed]"
MOVED = ("since_version", "reasoning_parser", "tool_call_parser")
# Evidence that backs each moved field, by URL substring.
EVIDENCE_HINTS = {
    "since_version": ("/releases/tag/",),
    "reasoning_parser": ("reasoning",),
    "tool_call_parser": ("tool_calling", "tool_parser"),
}


def migrate_row(row: dict) -> dict:
    values = {k: row.pop(k, UNKNOWN) for k in MOVED}
    row.setdefault("model_details", [])
    populated = {k: v for k, v in values.items() if v != UNKNOWN}
    if not populated:
        return row
    if len(row["model_slugs"]) != 1:
        raise SystemExit(
            f"{row['hf_architecture']}: v1 row-level {sorted(populated)} with "
            f"{len(row['model_slugs'])} model slugs; decide which models the value applies to"
        )
    evidence = [
        url
        for url in row["evidence"]
        if any(hint in url for k in populated for hint in EVIDENCE_HINTS[k])
    ]
    if not evidence:
        raise SystemExit(f"{row['hf_architecture']}: no evidence matches {sorted(populated)}")
    row["model_details"].append(
        {
            "model_slug": row["model_slugs"][0],
            **{k: values[k] for k in MOVED},
            "notes": "",
            "evidence": evidence,
        }
    )
    return row


def main() -> int:
    for path in sorted(ENGINES_DIR.glob("*.json")):
        record = json.loads(path.read_text())
        if record.get("engine_schema_version") == 2:
            print(f"{path.stem:20} already v2")
            continue
        record["engine_schema_version"] = 2
        record["model_support"] = [migrate_row(row) for row in record["model_support"]]
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        moved = sum(len(r["model_details"]) for r in record["model_support"])
        print(f"{path.stem:20} -> v2 ({moved} model_details)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
