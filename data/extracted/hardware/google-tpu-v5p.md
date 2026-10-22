# Google TPU v5p

> 中文版：[google-tpu-v5p.zh.md](./google-tpu-v5p.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | Google TPU v5p | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Vendor | Google | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Accelerator type | TPU | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Variant | v5p chip | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Form factor | [Unknown/Not Disclosed] | — |
| Record scope | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Device count | 1 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Snapshot date | 2026-10-22 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | TPU v5p | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Process | [Unknown/Not Disclosed] | — |
| Compute units | 2 TensorCores and 4 SparseCores per chip; each TensorCore has 4 MXUs, a vector unit, and a scalar unit. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Cache | [Unknown/Not Disclosed] | — |
| On-chip memory | [Unknown/Not Disclosed] | — |
| Execution model | Matrix Multiply Units (MXUs), vector and scalar execution. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Capacity (GB) | [Unknown/Not Disclosed] | — |
| Capacity (GiB) | 95.0 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Bandwidth (TB/s) | 2.765 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Scope | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Notes | Published HBM capacity is 95 GiB per chip; retained in the source unit, not relabeled GB.; Bandwidth is published as 2765 GB/s; decimal conversion to TB/s. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Published chip peaks: BF16 459 TFLOP/s and FP8 459 TFLOP/s. The table does not state engine breakdown, sparsity, accumulation, or FMA counting. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| BF16 | undisclosed | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| FP8 | undisclosed | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | [Unknown/Not Disclosed] | — |
| Scale up | ICI: 1200 GB/s total bidirectional bandwidth per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Scale out | DCN: 50 Gbit/s per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Topology | 3D torus for slices of 4x4x4 chips and larger; smaller slices lack wrap-around links. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | [Unknown/Not Disclosed] | — |
| Scope | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| Notes | — | — |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | [Unknown/Not Disclosed] | — |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | [Unknown/Not Disclosed] | — |

## Published measurements

No published measurements recorded.

## Open questions

- Per-chip power, process technology, and exact matrix/vector decomposition are not disclosed in this source snapshot.

## Sources

- [Source 1](https://docs.cloud.google.com/tpu/docs/v5p)
