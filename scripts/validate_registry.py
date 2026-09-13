#!/usr/bin/env python3
"""CI gate for the technique registry and its generated outputs.

Two checks, both cheap and both about keeping the index trustworthy:

1. **No vocabulary drift.** Every value appearing in a registered typed slot must
   resolve to a glossary entry (an alias) or be declared structural (taxonomy).
   This is what stops `kda` / `kda_linear_attention` style drift from accumulating
   silently across batches.
2. **Generated files are current.** The model index, technique index, coverage report,
   engine support matrix, engine adoption report and the generated "Implemented by
   (engines)" glossary sections are deterministic from the JSON + registry, so a stale copy
   in git means someone edited data without re-running the generator.

Run: `uv run python scripts/validate_registry.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from llm_tech_matrix.synthesis import index as index_mod
from llm_tech_matrix.synthesis.registry import (
    REPO_ROOT,
    build_edges,
    load_extractions,
    load_registry,
)


def main() -> int:
    registry = load_registry()
    extractions = load_extractions()
    edges, unregistered = build_edges(extractions, registry)
    failures: list[str] = []

    if unregistered:
        failures.append(
            f"{len(unregistered)} value(s) in registered slots are not in "
            f"docs/glossary/registry.json:"
        )
        for model, slot, value in unregistered:
            failures.append(f"    {model}: {slot} = {value!r}")
        failures.append(
            "  Fix by adding an alias to the matching technique, adding a new glossary "
            "entry, or declaring the value structural under `taxonomy`."
        )

    expected, _, _ = index_mod.expected_outputs()
    stale = [
        p.relative_to(REPO_ROOT)
        for p, content in expected.items()
        if not p.exists() or p.read_text() != content
    ]
    if stale:
        failures.append("Generated files are stale: " + ", ".join(str(p) for p in stale))
        failures.append("  Run: uv run python -m llm_tech_matrix.synthesis.index")

    if failures:
        print("Registry validation FAILED\n")
        print("\n".join(failures))
        return 1

    total = sum(len(v) for v in edges.values())
    print(
        f"  OK  registry: {len(registry['techniques'])} techniques, "
        f"{len(registry['prose_only']['entries'])} prose-only"
    )
    print(f"  OK  {total} structured edges over {len(extractions)} models, no drift")
    print("  OK  generated index files are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
