# Google TPU7x (Ironwood)

> 中文版：[google-tpu7x-ironwood.zh.md](./google-tpu7x-ironwood.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | Google TPU7x (Ironwood) | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Vendor | Google | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Accelerator type | TPU | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Variant | TPU7x whole chip; two chiplets | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#dual-chiplet_architecture) |
| Form factor | [Unknown/Not Disclosed] | — |
| Record scope | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Device count | 1 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Snapshot date | 2026-10-22 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | Ironwood, seventh-generation TPU | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x) |
| Process | [Unknown/Not Disclosed] | — |
| Compute units | 2 TensorCores and 4 SparseCores per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Cache | [Unknown/Not Disclosed] | — |
| On-chip memory | VMEM is on-chip SRAM; size is not given. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#memory_hierarchy) |
| Execution model | Two chiplets with separate memory spaces; frameworks expose two devices per physical chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#dual-chiplet_architecture) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Capacity (GB) | [Unknown/Not Disclosed] | — |
| Capacity (GiB) | 192.0 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Bandwidth (TB/s) | 7.38 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Scope | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Notes | Published capacity: 192 GiB per physical chip, 96 GiB per chiplet; not relabeled GB.; Specification table gives 7380 GB/s per chip; decimal conversion to TB/s. Memory-hierarchy prose rounds this to approximately 7.37 TB/s. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Published whole-chip peaks: BF16 2307 TFLOP/s and FP8 4614 TFLOP/s; engine breakdown, sparsity, accumulation, and FMA counting are unspecified. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| BF16 | undisclosed | 2307.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| FP8 | undisclosed | 4614.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCIe connects each four-chip group to its CPU host; generation and link width unspecified. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#memory_hierarchy) |
| Scale up | ICI: six links at 200 GB/s bidirectional each, totaling 1200 GB/s bidirectional per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#configurations) |
| Scale out | DCN: 100 Gbit/s per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Topology | 3D mesh below 64 chips; 4x4x4 cubes and larger slices use 3D torus. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#configurations) |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | [Unknown/Not Disclosed] | — |
| Scope | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| Notes | — | — |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | JAX and PyTorch; TensorFlow unsupported. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | Two framework-visible devices per chip, each with its own memory space. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#programming_model_and_framework_exposure) |

## Published measurements

No published measurements recorded.

## Open questions

- Process technology, per-chip power, and exact matrix/vector decomposition remain undisclosed in this snapshot.

## Sources

- [Source 1](https://docs.cloud.google.com/tpu/docs/tpu7x)
