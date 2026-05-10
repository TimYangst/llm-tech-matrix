"""Validate every data/extracted/*.json against the project schema.

Run locally:
    uv run python scripts/validate_extractions.py

Exits non-zero if any file fails validation. Used by CI to enforce the
"schema strictness" cardinal rule (CLAUDE.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from llm_tech_matrix.schema import SCHEMA_VERSION, ExtractedModel

EXTRACTED_DIR = Path(__file__).resolve().parent.parent / "data" / "extracted"


def main() -> int:
    files = sorted(EXTRACTED_DIR.glob("*.json"))
    if not files:
        print(f"No JSON files found under {EXTRACTED_DIR} — nothing to validate.")
        return 0

    failures: list[str] = []
    for path in files:
        rel = path.relative_to(EXTRACTED_DIR.parent.parent)
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as err:
            failures.append(f"{rel}:\n{err}")
            continue

        # The Pydantic model defaults `schema_version` to the current SCHEMA_VERSION,
        # so a file missing the field, or with a stale value, would otherwise pass
        # `model_validate` silently. Enforce equality here so CI catches missed
        # migrations after a schema bump.
        declared = data.get("schema_version")
        if declared != SCHEMA_VERSION:
            failures.append(
                f"{rel}:\nschema_version is {declared!r}, expected {SCHEMA_VERSION}. "
                f"Either migrate the file or pin the schema version explicitly."
            )
            continue

        try:
            ExtractedModel.model_validate(data)
        except ValidationError as err:
            failures.append(f"{rel}:\n{err}")
        else:
            print(f"  OK  {path.name}")

    if failures:
        print("\nFailed:\n", file=sys.stderr)
        for msg in failures:
            print(msg, file=sys.stderr)
            print("---", file=sys.stderr)
        return 1

    print(f"\nValidated {len(files)} extraction(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
