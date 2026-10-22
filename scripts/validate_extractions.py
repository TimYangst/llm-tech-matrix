"""Validate every extracted record against its schema.

- data/extracted/*.json          model records   -> schema.ExtractedModel
- data/extracted/engines/*.json  engine records  -> engine_schema.EngineRecord, plus
  cross-link checks: the filename equals `<engine>-<release_tag>`, the commit is a full SHA,
  every `model_slugs` entry has a model record, every `glossary_slug` has a glossary entry,
  and every `integrations[].engine_slug` has an engine snapshot.
- data/extracted/media/*.json    media records   -> media_schema.MediaRecord, with
  source-manifest consistency and deterministic bilingual views/index freshness.
- data/extracted/hardware/*.json hardware snapshots -> hardware_schema.HardwareRecord,
  with public URL/evidence, fetched-manifest/hash and generated-view freshness checks.

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
from urllib.parse import urldefrag

from pydantic import ValidationError

from llm_tech_matrix.engine_schema import ENGINE_SCHEMA_VERSION, EngineRecord
from llm_tech_matrix.extraction.render_hardware import rendered_files as rendered_hardware_files
from llm_tech_matrix.extraction.render_media import rendered_files as rendered_media_files
from llm_tech_matrix.hardware_schema import (
    HARDWARE_SCHEMA_VERSION,
    HardwareRecord,
    validate_public_url,
)
from llm_tech_matrix.media_schema import MEDIA_SCHEMA_VERSION, MediaRecord
from llm_tech_matrix.schema import SCHEMA_VERSION, ExtractedModel
from llm_tech_matrix.sourcing.fetch import sha256_of
from llm_tech_matrix.sourcing.manifest import SourceManifest
from llm_tech_matrix.synthesis.hardware import generated_files as hardware_index_files
from llm_tech_matrix.synthesis.media import generated_files as media_index_files

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"
ENGINES_DIR = EXTRACTED_DIR / "engines"
MEDIA_DIR = EXTRACTED_DIR / "media"
HARDWARE_DIR = EXTRACTED_DIR / "hardware"
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


def _media_sources(path: Path, record: MediaRecord) -> list[str]:
    manifest_path = REPO_ROOT / "data" / "sources" / path.stem / "manifest.json"
    if not manifest_path.is_file():
        return [f"no source manifest at {manifest_path.relative_to(REPO_ROOT)}"]
    try:
        manifest = SourceManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    except ValidationError as err:
        return [f"invalid source manifest: {err}"]
    errors = []
    if manifest.slug != path.stem:
        errors.append(f"manifest slug {manifest.slug!r} differs from record {path.stem!r}")
    source_urls = {urldefrag(url)[0] for url in record.metadata.sources}
    manifest_urls = {urldefrag(asset.url)[0] for asset in manifest.assets}
    if source_urls != manifest_urls:
        errors.append(
            f"metadata.sources differs from manifest: missing={sorted(manifest_urls - source_urls)}, unregistered={sorted(source_urls - manifest_urls)}"
        )
    for asset in manifest.assets:
        if not asset.sha256 or not re.fullmatch(r"[0-9a-f]{64}", asset.sha256):
            errors.append(f"source {asset.name!r}: missing or invalid sha256")
        if asset.size_bytes is None or asset.fetched_at is None:
            errors.append(f"source {asset.name!r}: asset has not been fetched")
    return errors


def validate_media() -> tuple[int, list[str]]:
    files = sorted(MEDIA_DIR.glob("*.json"))
    failures: list[str] = []
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("media_schema_version") != MEDIA_SCHEMA_VERSION:
                raise ValueError(f"media_schema_version must equal {MEDIA_SCHEMA_VERSION}")
            record = MediaRecord.model_validate(data)
        except (ValueError, ValidationError) as err:
            failures.append(f"{rel}:\n{err}")
            continue
        errors = _media_sources(path, record)
        if errors:
            failures.append(f"{rel}:\n" + "\n".join(errors))
        else:
            print(f"  OK  media/{path.name}")
    if files and not failures:
        generated = rendered_media_files(MEDIA_DIR) | media_index_files(MEDIA_DIR)
        for path, expected in generated.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: missing or stale generated media output; run render_media --all and synthesis.media"
                )
    return len(files), failures


def _hardware_sources(path: Path, record: HardwareRecord) -> list[str]:
    source_dir = REPO_ROOT / "data" / "sources" / "hardware" / path.stem
    manifest_path = source_dir / "manifest.json"
    if not manifest_path.is_file():
        return [f"no source manifest at {manifest_path.relative_to(REPO_ROOT)}"]
    try:
        manifest = SourceManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    except ValidationError as err:
        return [f"invalid source manifest: {err}"]
    errors = []
    if manifest.slug != path.stem:
        errors.append(f"manifest slug {manifest.slug!r} differs from record {path.stem!r}")
    urls = {urldefrag(url)[0] for url in record.metadata.sources}
    manifest_urls = {urldefrag(asset.url)[0] for asset in manifest.assets}
    if urls != manifest_urls:
        errors.append(
            f"metadata.sources differs from manifest: missing={sorted(manifest_urls - urls)}, unregistered={sorted(urls - manifest_urls)}"
        )
    for asset in manifest.assets:
        try:
            validate_public_url(asset.url)
            if asset.archive_url:
                validate_public_url(asset.archive_url)
        except ValueError as err:
            errors.append(f"source {asset.name!r}: {err}")
        if not asset.sha256 or not re.fullmatch(r"[0-9a-f]{64}", asset.sha256):
            errors.append(f"source {asset.name!r}: missing or invalid sha256")
        if asset.size_bytes is None or asset.size_bytes <= 0 or asset.fetched_at is None:
            errors.append(f"source {asset.name!r}: asset has not been fetched")
        filename = Path(asset.filename)
        if filename.is_absolute() or ".." in filename.parts:
            errors.append(f"source {asset.name!r}: unsafe cache filename")
            continue
        cached = source_dir / filename
        # A fresh CI clone has no cache. If present, ensure it is the registered public asset.
        if cached.is_file() and (
            sha256_of(cached) != asset.sha256 or cached.stat().st_size != asset.size_bytes
        ):
            errors.append(f"source {asset.name!r}: cached bytes differ from manifest")
    return errors


def validate_hardware() -> tuple[int, list[str]]:
    files = sorted(HARDWARE_DIR.glob("*.json"))
    failures = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("hardware_schema_version") != HARDWARE_SCHEMA_VERSION:
                raise ValueError(f"hardware_schema_version must equal {HARDWARE_SCHEMA_VERSION}")
            record = HardwareRecord.model_validate(data)
        except (ValueError, ValidationError) as err:
            failures.append(f"{path.relative_to(REPO_ROOT)}:\n{err}")
            continue
        errors = _hardware_sources(path, record)
        if errors:
            failures.append(f"{path.relative_to(REPO_ROOT)}:\n" + "\n".join(errors))
        else:
            print(f"  OK  hardware/{path.name}")
    if files and not failures:
        for path, expected in (
            rendered_hardware_files(HARDWARE_DIR) | hardware_index_files(HARDWARE_DIR)
        ).items():
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: missing or stale generated hardware output; run render_hardware --all and synthesis.hardware"
                )
    return len(files), failures


def main() -> int:
    files = sorted(EXTRACTED_DIR.glob("*.json"))
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
    media_count, media_failures = validate_media()
    failures += media_failures

    hardware_count, hardware_failures = validate_hardware()
    failures += hardware_failures

    if failures:
        print("\nFailed:\n", file=sys.stderr)
        for msg in failures:
            print(msg, file=sys.stderr)
            print("---", file=sys.stderr)
        return 1

    print(
        f"\nValidated {len(files)} extraction(s), {engine_count} engine snapshot(s), {media_count} media record(s), and {hardware_count} hardware snapshot(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
