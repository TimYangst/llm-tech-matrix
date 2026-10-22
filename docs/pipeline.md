# Pipeline Architecture

Three layers communicate through cached source bytes and schema-validated JSON.
Sourcing retrieves evidence; extraction interprets one release; synthesis reads
structured records to build comparisons. Each record belongs to one track.

## Record contracts

| Track                          | Source manifests                            | Canonical JSON                       | Contract                                               | Readable output            |
| ------------------------------ | ------------------------------------------- | ------------------------------------ | ------------------------------------------------------ | -------------------------- |
| LLM / multimodal understanding | `data/sources/<slug>/manifest.json`         | `data/extracted/<slug>.json`         | [LLM schema](schema.md), `schema.py`                   | `extraction.render`        |
| Engines                        | `data/sources/engines/<slug>/manifest.json` | `data/extracted/engines/<slug>.json` | [engine schema](engines/schema.md), `engine_schema.py` | `extraction.render_engine` |
| Media generation               | `data/sources/<slug>/manifest.json`         | `data/extracted/media/<slug>.json`   | [media schema](media/schema.md), `media_schema.py`     | `extraction.render_media`  |

Versions are independent. Root model globs are non-recursive; engine and media
records do not enter the LLM renderer or technique registry. Media records use the
source CLI's default source root; `--track engines` selects the engine subtree.

## Layer 1: Data sourcing

Input is a release identifier and public source URLs. The sourcing CLI writes
cached files plus a committed manifest containing URLs, SHA256, byte sizes, fetch
dates, source kinds and optional archive URLs. Cached files are gitignored.

- `add` registers and fetches an asset, then records its hash.
- `fetch` downloads missing assets, verifies known hashes and reports individual
  failures. A mismatch does not replace previously accepted bytes.
- `verify` checks cached bytes without downloading.
- `list` enumerates manifests for the selected source track.
- `sourcing.pdf_to_text` derives text from cached PDFs for extraction.

Sources follow the existing public-source eligibility convention: ordinary HF
account/token access is permitted, while payment or privileged/nonpublic access
is not. A token does not authorize private sources. Pin model-hub/repository
files and versioned papers; distinguish mutable announcement snapshots. See [source conventions](conventions.md#source-assets-committed-vs-cached).
Sourcing records bytes and provenance, without interpreting technical claims.

## Layer 2: Information extraction

An agent reads the source manifest and cached assets and writes one release's
JSON using the matching contract. There is no automated prompt-template runner
or multi-source reconcile service. Procedures live in
[extract-model](../.claude/skills/extract-model/SKILL.md),
[extract-engine](../.claude/skills/extract-engine/SKILL.md) and the
[media guide](media/overview.md).

Missing descriptive values remain `[Unknown/Not Disclosed]`; preserve each
schema's optional null/default structures. Version-specific facts, predecessor
training claims, shipped components and hosted product capabilities need explicit
scope. Source disagreements remain open questions. Media and engine claims carry
field/row evidence; model records retain source URLs and attribution in their
structured fields and notes.

Renderers deterministically produce English and Chinese summaries. Labels are
translated; extracted technical values stay in their source language. Change JSON
or the renderer, then regenerate; do not hand-edit generated Markdown.

`scripts/validate_extractions.py` validates all three record types and engine
cross-links. For media it also verifies manifest/evidence consistency and
view/index freshness from committed files; cached downloads are not required in
CI. `sourcing verify` separately checks actual cached bytes. Formatting hooks do
not replace schema validation.

## Layer 3: Synthesis and browse surfaces

Synthesis reads canonical JSON without fetching sources or rerunning extraction.
Implemented generators are:

- `synthesis.index`: model index, technique matrix, coverage report, engine support
  matrix/adoption report, and generated bilingual glossary engine sections.
- `synthesis.media`: independent bilingual media index.

The model technique registry matches **typed assertions**. A prose mention such
as “unlike MLA” does not assert adoption. Techniques recorded only in free text
(optimizer, RL method, routing) keep hand-maintained glossary adoption rows;
`data/reports/coverage.md` exposes missing or unexplained mappings.

Engine snapshots name glossary slugs directly. Their support matrix joins only
explicit recorded model mappings, distinguishes unassessed from not-found, and
preserves delegation and snapshot-version scope. Media is outside those joins.
Current indexes and reports do not read `inferred_fields`; an analysis that uses
inferences would need an explicit policy.

Interpretive trend narratives and scientific charts remain future work. Existing
reports provide structured browse/adoption evidence, not runtime benchmarks.

## Regeneration and checks

After LLM/engine or glossary changes, run `synthesis.index`. After media changes,
run its renderer and `synthesis.media`. The
[session guide](session-start.md#common-workflows) lists commands per track.

Run both `scripts/validate_extractions.py` and `scripts/validate_registry.py`;
the latter checks controlled vocabulary and generated report freshness.
[Development checks](development.md#what-ci-runs-on-every-pull-request) also cover
formatting and media regression tests. Each track can iterate independently when
its records and generated outputs satisfy these contracts.
