"""One-shot migration: engine schema v2 → v3.

v3 adds `model_support[].support: "delegated"` with `model_support[].delegated_to` (the engine
snapshot that maps the architecture). The addition is backwards-compatible: no v2 row changes
meaning, so existing records only get the version bump. Rows move to `delegated` when a
snapshot is (re)built from its sources, never by this script.

Idempotent: v3 records pass through unchanged.

Usage:
    uv run python scripts/migrate_engine_v2_to_v3.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINES_DIR = Path(__file__).resolve().parent.parent / "data" / "extracted" / "engines"


def main() -> int:
    for path in sorted(ENGINES_DIR.glob("*.json")):
        record = json.loads(path.read_text())
        if record.get("engine_schema_version") == 3:
            print(f"{path.stem:26} already v3")
            continue
        record["engine_schema_version"] = 3
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        print(f"{path.stem:26} -> v3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
