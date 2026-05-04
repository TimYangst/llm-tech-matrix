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

from llm_tech_matrix.schema import ExtractedModel

EXTRACTED_DIR = Path(__file__).resolve().parent.parent / "data" / "extracted"


def main() -> int:
    files = sorted(EXTRACTED_DIR.glob("*.json"))
    if not files:
        print(f"No JSON files found under {EXTRACTED_DIR} — nothing to validate.")
        return 0

    failures: list[str] = []
    for path in files:
        try:
            ExtractedModel.model_validate(json.loads(path.read_text()))
        except (ValidationError, json.JSONDecodeError) as err:
            failures.append(f"{path.relative_to(EXTRACTED_DIR.parent.parent)}:\n{err}")
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
