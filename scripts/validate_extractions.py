"""Validate every extracted record against its schema.

- data/extracted/*.json          model records   -> schema.ExtractedModel
- data/extracted/engines/*.json  engine records  -> engine_schema.EngineRecord, plus
  cross-link checks: the filename equals `<engine>-<release_tag>`, the commit is a full SHA,
  every `model_slugs` entry has a model record, every `glossary_slug` has a glossary entry,
  and every `integrations[].engine_slug` has an engine snapshot.

Run locally:
    uv run python scripts/validate_extractions.py

Exits non-zero if any file fails validation. Used by CI to enforce the
"schema strictness" cardinal rule (CLAUDE.md).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pydantic import ValidationError

from llm_tech_matrix.engine_schema import ENGINE_SCHEMA_VERSION, EngineRecord
from llm_tech_matrix.schema import SCHEMA_VERSION, ExtractedModel

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"
ENGINES_DIR = EXTRACTED_DIR / "engines"
GLOSSARY_DIR = REPO_ROOT / "docs" / "glossary"


def _engine_crosslinks(path: Path, record: EngineRecord) -> list[str]:
    errors: list[str] = []
    meta = record.metadata
    expected = f"{meta.engine}-{meta.release_tag}".lower()
    if path.stem != expected:
        errors.append(f"filename slug {path.stem!r} != <engine>-<release_tag> {expected!r}")
    if not re.fullmatch(r"[0-9a-f]{40}", meta.commit_sha):
        errors.append(f"commit_sha {meta.commit_sha!r} is not a full 40-char SHA")
    models = {p.stem for p in EXTRACTED_DIR.glob("*.json")}
    for row in record.model_support:
        errors += [
            f"model_support {row.hf_architecture}: no model record {slug!r}"
            for slug in row.model_slugs
            if slug not in models
        ]
    for row in record.technique_support:
        if not (GLOSSARY_DIR / f"{row.glossary_slug}.md").exists():
            errors.append(f"technique_support: no glossary entry {row.glossary_slug!r}")
    engines = {p.stem for p in ENGINES_DIR.glob("*.json")}
    for row in record.model_support:
        if row.delegated_to == path.stem:
            errors.append(f"model_support {row.hf_architecture}: delegated_to its own snapshot")
        elif row.delegated_to is not None and row.delegated_to not in engines:
            errors.append(
                f"model_support {row.hf_architecture}: no engine snapshot {row.delegated_to!r}"
            )
    for row in record.integrations:
        if row.engine_slug and row.engine_slug not in engines:
            errors.append(f"integrations {row.name}: no engine snapshot {row.engine_slug!r}")
    return errors


def validate_engines() -> tuple[int, list[str]]:
    files = sorted(ENGINES_DIR.glob("*.json"))
    failures: list[str] = []
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as err:
            failures.append(f"{rel}:\n{err}")
            continue
        declared = data.get("engine_schema_version")
        if declared != ENGINE_SCHEMA_VERSION:
            failures.append(
                f"{rel}:\nengine_schema_version is {declared!r}, expected {ENGINE_SCHEMA_VERSION}."
            )
            continue
        try:
            record = EngineRecord.model_validate(data)
        except ValidationError as err:
            failures.append(f"{rel}:\n{err}")
            continue
        errors = _engine_crosslinks(path, record)
        if errors:
            failures.append(f"{rel}:\n" + "\n".join(errors))
        else:
            print(f"  OK  engines/{path.name}")
    return len(files), failures


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

    engine_count, engine_failures = validate_engines()
    failures += engine_failures

    if failures:
        print("\nFailed:\n", file=sys.stderr)
        for msg in failures:
            print(msg, file=sys.stderr)
            print("---", file=sys.stderr)
        return 1

    print(f"\nValidated {len(files)} extraction(s) and {engine_count} engine snapshot(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
