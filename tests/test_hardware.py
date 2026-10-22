"""Regressions for public provenance, compute semantics and generated freshness."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from llm_tech_matrix.extraction.render_hardware import render, rendered_files
from llm_tech_matrix.hardware_schema import UNKNOWN, HardwareRecord
from llm_tech_matrix.sourcing.fetch import TRACK_ROOTS
from llm_tech_matrix.sourcing.fetch import main as sourcing_main
from llm_tech_matrix.synthesis.hardware import generated_files, render_index

SOURCE = "https://www.nvidia.com/en-us/data-center/"


def fixture() -> dict:
    """Synthetic claims exercise contracts, not a real device's specifications."""
    metadata = {
        "name": "Fixture Accelerator",
        "vendor": "Fixture Vendor",
        "accelerator_type": "GPU",
        "variant": "test",
        "form_factor": "module",
        "record_scope": "per_accelerator",
        "device_count": 1,
        "snapshot_date": "2026-10-22",
    }
    return {
        "hardware_schema_version": 1,
        "metadata": metadata | {"sources": [SOURCE], "evidence": {k: [SOURCE] for k in metadata}},
        "architecture": {},
        "memory": {
            "capacity_gb": 80,
            "scope": "per_accelerator",
            "evidence": {"capacity_gb": [SOURCE], "scope": [SOURCE]},
        },
        "compute": {
            "peaks": [
                {
                    "precision": "BF16",
                    "operation": "matrix",
                    "throughput": rate,
                    "unit": "TFLOP/s",
                    "sparsity": sparse,
                    "scope": "per_accelerator",
                    "evidence": [SOURCE],
                }
                for rate, sparse in ((100, "dense"), (200, "structured_sparse"))
            ]
        },
        "interconnect": {},
        "power": {"scope": "per_accelerator", "evidence": {"scope": [SOURCE]}},
        "software": {},
    }


class HardwareTests(unittest.TestCase):
    def test_evidence_is_required_and_registered(self):
        data = fixture()
        data["memory"]["evidence"].pop("capacity_gb")
        with self.assertRaisesRegex(ValidationError, "memory.capacity_gb: no evidence"):
            HardwareRecord.model_validate(data)
        data = fixture()
        data["compute"]["peaks"][0]["evidence"] = ["https://example.org/unregistered"]
        with self.assertRaisesRegex(ValidationError, "not in metadata.sources"):
            HardwareRecord.model_validate(data)

    def test_unknown_numeric_strictness(self):
        for invalid in ("80GB", "unknown", -1, 0, float("inf"), True):
            data = fixture()
            data["memory"]["capacity_gb"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                HardwareRecord.model_validate(data)
        data = fixture()
        data["memory"]["capacity_gb"] = UNKNOWN
        data["memory"]["evidence"].pop("capacity_gb")
        self.assertEqual(HardwareRecord.model_validate(data).memory.capacity_gb, UNKNOWN)

    def test_private_sources_and_internal_receipts_are_rejected(self):
        for url in (
            "file:///tmp/internal.json",
            "http://localhost/a",
            "http://127.0.0.1/a",
            "http://10.0.0.1/a",
            "http://169.254.169.254/a",
            "https://host.internal/a",
            "https://host.example.ts.net/a",
            "https://user:pass@example.com/a",
            "https://example.com/a?token=secret",
        ):
            data = fixture()
            data["metadata"]["sources"] = [url]
            with self.subTest(url=url), self.assertRaises(ValidationError):
                HardwareRecord.model_validate(data)
        data = fixture()
        data["internal_measurements"] = [{"receipt": "/private/result.json"}]
        with self.assertRaises(ValidationError):
            HardwareRecord.model_validate(data)

    def test_scope_and_integer_unit_are_checked(self):
        data = fixture()
        data["compute"]["peaks"][0]["scope"] = "system"
        with self.assertRaisesRegex(ValidationError, "scopes must match"):
            HardwareRecord.model_validate(data)
        data = fixture()
        data["compute"]["peaks"][0]["precision"] = "INT8"
        with self.assertRaisesRegex(ValidationError, "Integer peaks use TOPS"):
            HardwareRecord.model_validate(data)

    def test_sparse_dense_and_gib_survive_bilingual_outputs(self):
        data = fixture()
        data["memory"].pop("capacity_gb")
        data["memory"]["evidence"].pop("capacity_gb")
        data["memory"]["capacity_gib"] = 96
        data["memory"]["evidence"]["capacity_gib"] = [SOURCE]
        record = HardwareRecord.model_validate(data)
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "fixture.json").write_text(json.dumps(data))
            for lang in ("en", "zh"):
                index = render_index(directory, lang)
                view = render(record, lang, "fixture")
                for text in (index, view):
                    self.assertIn("dense", text)
                    self.assertIn("structured_sparse", text)
                    self.assertIn("100.0", text)
                    self.assertIn("200.0", text)
                    self.assertIn("per_accelerator", text)
                    self.assertIn("TFLOP/s", text)
                self.assertIn("96.0 GiB", index)
                self.assertNotIn("96.0 GB", index)

    def test_validator_checks_manifest_and_generated_freshness_without_cache(self):
        spec = importlib.util.spec_from_file_location(
            "validate_hardware_test", "scripts/validate_extractions.py"
        )
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "data/extracted/hardware"
            directory.mkdir(parents=True)
            (directory / "fixture.json").write_text(json.dumps(fixture()))
            source_dir = root / "data/sources/hardware/fixture"
            source_dir.mkdir(parents=True)
            manifest = {
                "slug": "fixture",
                "assets": [
                    {
                        "name": "public",
                        "kind": "blog_html",
                        "url": SOURCE,
                        "filename": "public.html",
                        "description": "Test public page",
                        "sha256": "a" * 64,
                        "size_bytes": 1,
                        "fetched_at": "2026-10-22",
                    }
                ],
            }
            manifest_path = source_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            outputs = rendered_files(directory) | generated_files(directory)
            for path, content in outputs.items():
                path.write_text(content)
            with (
                patch.object(validator, "REPO_ROOT", root),
                patch.object(validator, "HARDWARE_DIR", directory),
            ):
                self.assertEqual(validator.validate_hardware(), (1, []))
                next(iter(outputs)).write_text("stale")
                self.assertTrue(
                    any("stale generated hardware" in s for s in validator.validate_hardware()[1])
                )
                broken = copy.deepcopy(manifest)
                broken["assets"][0]["sha256"] = None
                manifest_path.write_text(json.dumps(broken))
                self.assertTrue(
                    any("invalid sha256" in s for s in validator.validate_hardware()[1])
                )
                broken = copy.deepcopy(manifest)
                broken["assets"][0]["url"] = "https://example.org/another"
                manifest_path.write_text(json.dumps(broken))
                self.assertTrue(
                    any("differs from manifest" in s for s in validator.validate_hardware()[1])
                )

    def test_hardware_fetch_rejects_private_url_before_network(self):
        with patch("llm_tech_matrix.sourcing.fetch.fetch_asset") as fetch:
            result = sourcing_main(
                [
                    "--track",
                    "hardware",
                    "add",
                    "fixture",
                    "--name",
                    "private",
                    "--kind",
                    "other",
                    "--url",
                    "http://10.0.0.1/private",
                    "--filename",
                    "private.html",
                ]
            )
        self.assertEqual(result, 1)
        fetch.assert_not_called()

    def test_dual_capacity_units_are_not_silently_collapsed(self):
        data = fixture()
        data["memory"]["capacity_gib"] = 80
        data["memory"]["evidence"]["capacity_gib"] = [SOURCE]
        with self.assertRaisesRegex(ValidationError, "one original capacity unit"):
            HardwareRecord.model_validate(data)

    def test_hardware_track_does_not_reuse_model_source_root(self):
        self.assertEqual(TRACK_ROOTS["hardware"], Path("data/sources/hardware"))
        self.assertNotEqual(TRACK_ROOTS["hardware"], TRACK_ROOTS["models"])


if __name__ == "__main__":
    unittest.main()
