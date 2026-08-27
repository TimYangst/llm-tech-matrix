"""Controlled vocabulary: typed extraction fields -> glossary entries.

Layer 3 reads only `data/extracted/*.json` (see docs/pipeline.md). This module turns
the *typed* fields of those records into technique->model edges.

The distinction that makes the edges trustworthy: a typed slot is an **assertion**
("this model's sparse_attention.kind is dsa"), whereas prose is often a **mention**
("unlike MLA, ...", "the family report documents Muon but 5.2 does not restate it").
Only assertions become edges. Prose stays out — see docs/glossary/registry.json's
`prose_only` block for the glossary entries that are consequently hand-maintained.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "docs" / "glossary" / "registry.json"
EXTRACTED_DIR = REPO_ROOT / "data" / "extracted"


def load_registry(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or REGISTRY_PATH).read_text())


def load_extractions(directory: Path | None = None) -> dict[str, dict]:
    directory = directory or EXTRACTED_DIR
    return {p.stem: json.loads(p.read_text()) for p in sorted(directory.glob("*.json"))}


def dig(obj: Any, path: str) -> list[Any]:
    """Resolve a dotted path, where a `foo[]` segment fans out over a list."""
    current: list[Any] = [obj]
    for key in path.split("."):
        nxt: list[Any] = []
        listy = key.endswith("[]")
        key = key[:-2] if listy else key
        for node in current:
            if not isinstance(node, dict):
                continue
            value = node.get(key)
            if value is None:
                continue
            if listy and isinstance(value, list):
                nxt.extend(value)
            elif not listy:
                nxt.append(value)
        current = nxt
    return current


def _alias_map(registry: dict[str, Any]) -> dict[str, list[str]]:
    """Lowercased field value -> list of glossary slugs it asserts."""
    out: dict[str, list[str]] = {}
    for slug, spec in registry["techniques"].items():
        for alias in spec.get("aliases", []):
            out.setdefault(alias.lower(), []).append(slug)
        for raw, slugs in (spec.get("compound") or {}).items():
            out[raw.lower()] = list(slugs)
    return out


def _taxonomy(registry: dict[str, Any]) -> set[str]:
    vals: set[str] = set()
    for key, values in registry["taxonomy"].items():
        if key == "_doc":
            continue
        vals.update(v.lower() for v in values)
    return vals


def build_edges(
    extractions: dict[str, dict], registry: dict[str, Any]
) -> tuple[dict[str, set[str]], list[tuple[str, str, str]]]:
    """Return (slug -> {model slugs}, unregistered values as (model, slot, value))."""
    aliases = _alias_map(registry)
    taxonomy = _taxonomy(registry)
    fuzzy = set(registry.get("fuzzy_slots", []))
    edges: dict[str, set[str]] = {slug: set() for slug in registry["techniques"]}
    unregistered: list[tuple[str, str, str]] = []

    for model, record in extractions.items():
        for slot in registry["slots"]:
            for value in dig(record, slot):
                if not isinstance(value, str):
                    continue
                key = value.strip().lower()
                if key in taxonomy:
                    continue
                if slot in fuzzy:
                    # free-ish text (e.g. "multi_token_prediction / speculative_decoding",
                    # "capacity_scaling — adds parameters outside the backbone ...");
                    # match on contained aliases rather than the whole string
                    hits = [
                        slug for alias, slugs in aliases.items() for slug in slugs if alias in key
                    ]
                    if not hits:
                        unregistered.append((model, slot, value))
                    for slug in hits:
                        edges.setdefault(slug, set()).add(model)
                    continue
                slugs = aliases.get(key)
                if slugs is None:
                    unregistered.append((model, slot, value))
                    continue
                for slug in slugs:
                    edges.setdefault(slug, set()).add(model)

        # presence rules: a non-null subobject is itself the assertion
        for slug, spec in registry["techniques"].items():
            for path in spec.get("presence", []):
                if any(v is not None for v in dig(record, path)):
                    edges[slug].add(model)

    # `requires` gates (e.g. int4 counts as INT4-QAT only when method == qat)
    for slug, spec in registry["techniques"].items():
        for path, expected in (spec.get("requires") or {}).items():
            edges[slug] = {
                m
                for m in edges[slug]
                if any(
                    isinstance(v, str) and expected.lower() in v.lower()
                    for v in dig(extractions[m], path)
                )
            }

    return edges, unregistered
