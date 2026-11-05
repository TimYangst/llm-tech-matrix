# Public AI accelerator catalog

This track records publicly documented GPU, TPU and other AI accelerators. It is
independent of model, media and engine records. Start from the generated
[English index](../../data/extracted/hardware/README.md) or
[中文索引](../../data/extracted/hardware/README.zh.md), then open the exact device variant.

The first collection covers representative data-center devices plus a consumer GPU
reference. It is a snapshot of verified public specifications, not an exhaustive
product list or a performance ranking. The [schema](schema.md) defines the fields and
comparability rules; the [project state](../../tasks/projects/public-hardware-catalog.md)
tracks coverage, review and follow-up work.

## Publication boundary

Every known factual field must cite a registered public web page or PDF. Prefer vendor
product pages, architecture whitepapers, official documentation and papers authored by
the hardware provider. Record the exact variant and the date when the public sources
were checked. Keep the source URL and page/table context in the record, so another
reader can verify the fact.

**Do not use internal measurements, local benchmark receipts, private machine inventories,
privileged dashboards, unpublished configurations, internal notes or nonpublic files.**
An internally known value remains `"[Unknown/Not Disclosed]"` here unless a public source
independently states it. Do not register an internal URL, sanitized internal screenshot
or local file as evidence. This phase contains no internal measurements. The optional
`public_measurements` collection is only for already published benchmarks with their
configuration, metric, scope, conditions and public source.

URL validation rejects obvious private/local hosts, local file paths and
credential-bearing links. It cannot prove that arbitrary HTTP content is public or
supports a claim. Source collection and independent review must check accessibility,
content and provenance. A hash records fetched bytes; it does not establish that a
claim is true. A fresh CI checkout validates registered hashes without requiring the
ignored source cache; a local cache, when present, must match its manifest.

## Workflow

1. Select one exact product variant and scope. Separate PCIe/SXM/OAM variants and
   multi-device systems when their specifications differ.

2. Register and fetch openly accessible source pages/PDFs:

   ```bash
   uv run python -m llm_tech_matrix.sourcing --track hardware add <slug> --name datasheet --kind tech_report --url <public-pdf-url> --filename datasheet.pdf --description "Vendor datasheet, exact variant"
   uv run python -m llm_tech_matrix.sourcing.pdf_to_text --track hardware <slug>
   uv run python -m llm_tech_matrix.sourcing --track hardware verify <slug>
   ```

   Use `blog_html` or `other` for HTML pages and describe what they contain. Committed
   manifests live in `data/sources/hardware/<slug>/manifest.json`; raw cache bytes are
   ignored. Do not manually invent hashes or change a recorded hash to hide a mismatch.

3. Read the public source content and write
   `data/extracted/hardware/<slug>.json` against `hardware_schema.py`. Leave undisclosed
   fields unknown; record ambiguity in `open_questions`.

4. Generate bilingual views and the comparison index, then validate:

   ```bash
   uv run python -m llm_tech_matrix.extraction.render_hardware <slug>
   uv run python -m llm_tech_matrix.synthesis.hardware
   uv run python scripts/validate_extractions.py
   uv run python -m unittest discover -s tests -v
   ```

5. Independently review the exact change against the source set. Verify variants,
   decimal/binary units, per-device/system scopes and precision/sparsity conditions.

Use `render_hardware --all --check` and `synthesis.hardware --check` to check generated
freshness without changing files. Generated Markdown must be changed via its JSON or
renderer, not by hand.

## Reading comparisons

The index keeps separate compute rows for each precision, operation, sparsity and
scope. Dense BF16, sparse FP8, vector FP32 and a system aggregate cannot be treated as
one comparable performance number. `undisclosed` means the source does not establish
the operation or sparsity assumption; `sparse_unspecified` means sparse throughput is
explicitly published but its pattern is not established. Quoted vendor peaks are
not measured model throughput or latency.

GB and TB are decimal. A source that states GiB uses `capacity_gib`; no silent conversion
to GB is made. Wafer-scale on-chip SRAM belongs in `architecture.on_chip_memory`; do
not present it as interchangeable with discrete HBM without an explicit source.
Interconnect prose distinguishes host, scale-up and scale-out links and preserves
aggregate/directional qualifiers. TDP is a rated envelope for the cited variant,
not measured energy per inference.
