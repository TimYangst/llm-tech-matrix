"""One-shot migration: engine schema v1 → v2.

v2 adds the `training` and `rl` role subobjects and `integrations[].version_constraints`
(optional, backwards-compatible), and replaces `model_support[].in_native_registry: bool` with
`model_support[].support` ∈ {registered, model_specific, not_found}. verl has no model registry
but does carry model-specific code, which a boolean could not express.

For each data/extracted/engines/<slug>.json:
- Bump engine_schema_version to 2.
- `in_native_registry: true` → `support: "registered"`; `false` → `support: "not_found"`
  (both v1 records came from engines with a registry, so no row needs `model_specific`).

Idempotent: v2 records pass through unchanged.

Usage:
    uv run python scripts/migrate_engine_v1_to_v2.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINES_DIR = Path(__file__).resolve().parent.parent / "data" / "extracted" / "engines"


def main() -> int:
    for path in sorted(ENGINES_DIR.glob("*.json")):
        record = json.loads(path.read_text())
        if record.get("engine_schema_version") == 2:
            print(f"{path.stem:20} already v2")
            continue
        for row in record["model_support"]:
            registered = row.pop("in_native_registry")
            row["support"] = "registered" if registered else "not_found"
        # keep key order readable: support right after model_slugs
        record["model_support"] = [
            {
                **{k: row[k] for k in ("hf_architecture", "model_slugs", "support")},
                **{
                    k: v
                    for k, v in row.items()
                    if k not in ("hf_architecture", "model_slugs", "support")
                },
            }
            for row in record["model_support"]
        ]
        record["engine_schema_version"] = 2
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        print(f"{path.stem:20} -> v2 ({len(record['model_support'])} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
