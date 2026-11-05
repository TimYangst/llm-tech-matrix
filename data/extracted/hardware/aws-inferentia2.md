# AWS Inferentia2

> 中文版：[aws-inferentia2.zh.md](./aws-inferentia2.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | AWS Inferentia2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Vendor | AWS | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Accelerator type | ASIC | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Variant | inferentia2 chip | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Form factor | [Unknown/Not Disclosed] | — |
| Record scope | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Device count | 1 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Snapshot date | 2026-10-22 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | AWS Inferentia2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Process | [Unknown/Not Disclosed] | — |
| Compute units | 2 NeuronCore-v2. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Cache | [Unknown/Not Disclosed] | — |
| On-chip memory | [Unknown/Not Disclosed] | — |
| Execution model | Heterogeneous Tensor, Vector, Scalar and GPSIMD engines; software-managed SRAM. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v2.html#neuroncore-v2-architecture) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Capacity (GB) | [Unknown/Not Disclosed] | — |
| Capacity (GiB) | 32.0 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Bandwidth (TB/s) | [Unknown/Not Disclosed] | — |
| Scope | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Notes | Published HBM capacity: 32 GiB per chip; retained in source units, not relabeled GB.; Published bandwidth: 820 GiB/s; not relabeled decimal GB/s or TB/s. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Published aggregate chip rates: INT8 380 TOPS; FP16/BF16/cFP8/TF32 190 TFLOP/s; FP32 47.5 TFLOP/s. Engine decomposition, sparsity, accumulation and FMA counting are unspecified. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| INT8 | undisclosed | 380.0 | TOPS | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| FP16 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| BF16 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| cFP8 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| TF32 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| FP32 | undisclosed | 47.5 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | [Unknown/Not Disclosed] | — |
| Scale up | NeuronLink-v2; bandwidth and directionality are unspecified in this source. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | [Unknown/Not Disclosed] | — |
| Scope | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Notes | — | — |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | AWS Neuron | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| ISA | NeuronCore-v2 ISA extensions support dynamic shapes and control flow. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| Programming model | Custom operators through embedded GPSIMD engines. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## Published measurements

No published measurements recorded.

## Open questions

- Per-chip TDP, manufacturing process and exact matrix/vector chip throughput require additional public evidence.

## Sources

- [Source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html)
- [Source 2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v2.html)
