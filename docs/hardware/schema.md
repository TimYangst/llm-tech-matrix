# Hardware schema v1

Executable contract: [`hardware_schema.py`](../../src/llm_tech_matrix/hardware_schema.py).
Canonical records: `data/extracted/hardware/<slug>.json`. Source manifests:
`data/sources/hardware/<slug>/manifest.json`. `hardware_schema_version` is exactly `1`;
this track does not change the LLM, engine or media schema version.

## Required groups

| Group                 | Contents                                                                                                                                     |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `metadata`            | `name`, `vendor`, `accelerator_type`, exact `variant`, `form_factor`, `record_scope`, `device_count`, `snapshot_date`, `sources`, `evidence` |
| `architecture`        | `family`, `process`, `compute_units`, `cache`, `on_chip_memory`, `execution_model`, `notes`, `evidence`                                      |
| `memory`              | `technology`, `capacity_gb`, `capacity_gib`, `bandwidth_tb_s`, `scope`, `notes`, `evidence`                                                  |
| `compute`             | `peaks`, `notes`, `evidence`                                                                                                                 |
| `interconnect`        | `host`, `scale_up`, `scale_out`, `topology`, `evidence`                                                                                      |
| `power`               | `tdp_w`, `scope`, `notes`, `evidence`                                                                                                        |
| `software`            | `ecosystem`, `isa`, `programming_model`, `evidence`                                                                                          |
| `public_measurements` | Optional list of already publicly published benchmarks; defaults to empty                                                                    |
| `open_questions`      | Unresolved disclosure or interpretation questions; defaults to empty                                                                         |

`accelerator_type` is `GPU`, `TPU`, `ASIC` or `WSE`. `record_scope` is
`per_accelerator` or `system`. A per-accelerator record has `device_count: 1`;
`system` uses its documented positive count or the unknown sentinel. Memory, power and
all compute peak scopes must match the record scope. Use a separate record to describe
a system aggregate. `snapshot_date` is an ISO `YYYY-MM-DD` date when public information
was checked, not an implied product release date.

The exact unknown sentinel is `"[Unknown/Not Disclosed]"`. Prose scalars default to it.
Capacity, bandwidth and TDP accept only positive finite JSON numbers or that sentinel;
strings such as `"80GB"`, `"unknown"` and `"N/A"` fail. Counts require positive integers
or the sentinel. Lists default to empty. Blank strings and extra fields fail validation.
An unknown field has no evidence entry.

`capacity_gb` uses decimal GB; `capacity_gib` uses binary GiB. Only one numeric capacity field may be populated. Fill the unit actually
published by the source and retain ambiguity in notes. Do not silently relabel GiB as
GB. `bandwidth_tb_s` uses decimal TB/s and must not conflate memory bandwidth with
interconnect bandwidth. Architecture and interconnect fields remain prose so that
vendor-specific topology, directional and aggregate qualifiers are preserved.

## Field evidence

Every populated scalar and nonempty list in the seven required groups needs an
`evidence` entry keyed by its exact field name. Exceptions are `metadata.sources`,
which registers the source set, and `compute.peaks`, whose rows carry their own evidence.
For example:

```json
{
  "technology": "HBM3",
  "capacity_gb": 80,
  "scope": "per_accelerator",
  "evidence": {
    "technology": ["https://vendor.example.com/product/datasheet.pdf#page=2"],
    "capacity_gb": ["https://vendor.example.com/product/datasheet.pdf#page=2"],
    "scope": ["https://vendor.example.com/product/datasheet.pdf#page=2"]
  }
}
```

The URLs above illustrate syntax only, not a hardware source. Each evidence URL must
match a registered `metadata.sources` URL after removing its fragment. Use fragments
and explanatory conditions to preserve PDF page/table context. The registered source
set must match the source manifest. Each manifest asset needs its fetched SHA-256,
positive byte count and fetched date. Validation checks cached bytes if they exist;
CI does not download sources. Evidence syntax alone does not prove a claim: see the
[publication boundary](overview.md#publication-boundary).

## Theoretical compute peaks

Each `compute.peaks` row has:

| Field          | Contract                                                                                              |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| `precision`    | Published operand precision; preserve format/variant qualifiers                                       |
| `operation`    | `matrix`, `vector` or `undisclosed`                                                                   |
| `throughput`   | Positive finite number                                                                                |
| `unit`         | `TFLOP/s` or `TOPS`; explicit INT/UINT rates require TOPS and FP/BF/TF rates require TFLOP/s          |
| `sparsity`     | `dense`, `structured_sparse`, `sparse_unspecified` or `undisclosed`                                   |
| `scope`        | `per_accelerator` or `system`, matching the record                                                    |
| `accumulation` | Public accumulation precision or unknown                                                              |
| `conditions`   | Exact public variant, clocks, boost/thermal assumptions, sparse conditions and qualifiers, or unknown |
| `fma_counting` | Public multiply-add operation-count convention or unknown                                             |
| `evidence`     | Nonempty list of registered public URLs supporting the entire row                                     |

Do not infer dense throughput by halving a sparse marketing number. Do not label
vendor sparse throughput `structured_sparse` unless the public source establishes
the pattern. Do not infer the operation type from the product category. Keep
`undisclosed` if the published total does not establish matrix/vector composition.
Separate distinct formats, sparsity modes and variants into separate rows. Neither
renderer nor index chooses a single best peak or sorts devices by peak throughput.

## Published measurements

An optional `public_measurements` row requires `benchmark`, `metric`, positive numeric
`value`, `unit`, `scope`, `configuration`, `conditions` and nonempty `evidence`. Preserve
software version, workload, batch/sequence settings and device/system configuration
in its prose context. Evidence must point to an already published web page or PDF.
No local files, private URLs, internal receipts or unpublished results belong here.
This initial collection leaves the list empty; theoretical specification peaks live
in `compute.peaks` instead.

## Generated output and checks

`extraction.render_hardware` generates English and Chinese field labels, evidence
links and independent peak/measurement sections. `synthesis.hardware` generates
bilingual configuration and peak tables. Values retain source wording; labels do not
promise a translation of quoted technical prose.

`scripts/validate_extractions.py` enforces the version, strict schema, evidence
registration, manifest source set, fetched hash metadata, optional local-cache
integrity and bilingual summary/index freshness. Regression tests cover missing and
unregistered evidence, numeric unknowns, private sources, units/scopes, original GiB
units, dense/sparse preservation and cache-free freshness checking.
