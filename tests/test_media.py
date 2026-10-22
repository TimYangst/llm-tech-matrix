"""Guard media provenance and deterministic output contracts without network access."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from llm_tech_matrix.extraction.render_media import render
from llm_tech_matrix.media_schema import UNKNOWN, MediaRecord
from llm_tech_matrix.synthesis.media import render_index

SOURCE = "https://example.com/vendor/commit/README.md"


def record_data() -> dict:
    metadata = {
        "name": "Example media",
        "family": "example",
        "organization": "Example",
        "release_date": "2026-10",
        "openness": "open_weights",
        "license": "Example License",
        "variant_policy": "Base weights; hosted preprocessing excluded.",
    }
    metadata["evidence"] = {field: [SOURCE] for field in metadata}
    metadata["sources"] = [SOURCE]
    return {
        "media_schema_version": 1,
        "metadata": metadata,
        "generation": {
            "input_modalities": ["text"],
            "output_modalities": ["audio"],
            "evidence": {"input_modalities": [SOURCE], "output_modalities": [SOURCE]},
        },
        "architecture": {},
        "output": {},
        "training": {},
        "precision": {},
        "release": {},
    }


class MediaTests(unittest.TestCase):
    def test_architecture_claim_needs_registered_evidence(self):
        data = record_data()
        data["architecture"] = {"backbone": "Flow transformer"}
        with self.assertRaisesRegex(ValidationError, "architecture.backbone: no evidence"):
            MediaRecord.model_validate(data)
        data["architecture"]["evidence"] = {"backbone": [SOURCE + "#L4"]}
        self.assertEqual(MediaRecord.model_validate(data).architecture.backbone, "Flow transformer")
        data["architecture"]["evidence"]["backbone"] = ["https://other.example/config.json"]
        with self.assertRaisesRegex(ValidationError, "not in metadata.sources"):
            MediaRecord.model_validate(data)

    def test_unknown_is_not_an_evidenced_claim(self):
        data = record_data()
        data["architecture"] = {"backbone": UNKNOWN, "evidence": {"backbone": [SOURCE]}}
        with self.assertRaisesRegex(ValidationError, "field is unknown"):
            MediaRecord.model_validate(data)

    def test_incompatible_schema_and_unsupported_modalities_rejected(self):
        data = record_data()
        data["schema_version"] = 8
        with self.assertRaises(ValidationError):
            MediaRecord.model_validate(data)
        del data["schema_version"]
        data["generation"]["output_modalities"] = ["arbitrary"]
        with self.assertRaises(ValidationError):
            MediaRecord.model_validate(data)

    def test_render_preserves_hosted_scope_unknowns_and_table_safety(self):
        data = record_data()
        data["release"] = {
            "hosted_scope": "Hosted | IR\nservice",
            "evidence": {"hosted_scope": [SOURCE]},
        }
        record = MediaRecord.model_validate(data)
        en = render(record, "en", "example")
        zh = render(record, "zh", "example")
        self.assertIn("Hosted \\| IR service", en)
        self.assertIn(UNKNOWN, en)
        self.assertIn("托管流程范围", zh)
        self.assertIn(SOURCE, zh)

    def test_validator_checks_manifest_and_generated_freshness(self):
        script = Path(__file__).resolve().parents[1] / "scripts/validate_extractions.py"
        spec = importlib.util.spec_from_file_location("validate_extractions", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            media = root / "data/extracted/media"
            media.mkdir(parents=True)
            record_path = media / "example.json"
            record_path.write_text(json.dumps(record_data()))
            source_dir = root / "data/sources/example"
            source_dir.mkdir(parents=True)
            manifest_path = source_dir / "manifest.json"
            manifest = {
                "slug": "example",
                "assets": [
                    {
                        "name": "card",
                        "kind": "model_card",
                        "url": SOURCE,
                        "filename": "README.md",
                        "description": "card",
                        "sha256": "a" * 64,
                        "size_bytes": 10,
                        "fetched_at": "2026-10-22",
                    }
                ],
            }
            manifest_path.write_text(json.dumps(manifest))
            with patch.object(module, "REPO_ROOT", root), patch.object(module, "MEDIA_DIR", media):
                count, failures = module.validate_media()
                self.assertEqual(count, 1)
                self.assertTrue(any("missing or stale" in item for item in failures))
                for path, content in (
                    module.rendered_media_files(media) | module.media_index_files(media)
                ).items():
                    path.write_text(content)
                self.assertEqual(module.validate_media()[1], [])
                manifest["assets"][0]["url"] = "https://example.com/unregistered"
                manifest_path.write_text(json.dumps(manifest))
                self.assertTrue(
                    any("differs from manifest" in item for item in module.validate_media()[1])
                )

    def test_index_reads_media_records_only(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "example.json").write_text(json.dumps(record_data()))
            text = render_index(directory)
            self.assertIn("[Example media](./example.md)", text)
            self.assertIn("text → audio", text)


if __name__ == "__main__":
    unittest.main()
