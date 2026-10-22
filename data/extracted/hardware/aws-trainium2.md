# AWS Trainium2

> 中文版：[aws-trainium2.zh.md](./aws-trainium2.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | AWS Trainium2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Vendor | AWS | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Accelerator type | ASIC | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Variant | trainium2 chip | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Form factor | [Unknown/Not Disclosed] | — |
| Record scope | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Device count | 1 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Snapshot date | 2026-10-22 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | AWS Trainium2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Process | [Unknown/Not Disclosed] | — |
| Compute units | 8 NeuronCore-v3; 16 collective-communication cores. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Cache | [Unknown/Not Disclosed] | — |
| On-chip memory | 224 MiB SBUF per chip, as published in the chip memory table. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#memory) |
| Execution model | Heterogeneous Tensor, Vector, Scalar and GPSIMD engines; software-managed SRAM. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v3.html#neuroncore-v3-architecture) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Capacity (GB) | [Unknown/Not Disclosed] | — |
| Capacity (GiB) | 96.0 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Bandwidth (TB/s) | 2.9 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Scope | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Notes | Published HBM capacity: 96 GiB per chip; retained in source units, not relabeled GB. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Published aggregate chip rates: FP8 1299; BF16/FP16/TF32 667; FP32 181 TFLOP/s; sparse FP8/FP16/BF16/TF32 2563 TFLOP/s. Engine decomposition is unspecified.; NeuronCore-v3 TensorEngine rates are per core and differ from chip aggregate divided by eight; no chip matrix peak is inferred. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute), [source 2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v3.html#tensor-engine) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| FP8 | undisclosed | 1299.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| BF16 | undisclosed | 667.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| FP16 | undisclosed | 667.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| TF32 | undisclosed | 667.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| FP32 | undisclosed | 181.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| FP8 | undisclosed | 2563.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Chip aggregate sparse rate; source table does not identify the exact sparsity pattern or engine breakdown. | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| FP16 | undisclosed | 2563.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Chip aggregate sparse rate; source table does not identify the exact sparsity pattern or engine breakdown. | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| BF16 | undisclosed | 2563.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Chip aggregate sparse rate; source table does not identify the exact sparsity pattern or engine breakdown. | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |
| TF32 | undisclosed | 2563.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Chip aggregate sparse rate; source table does not identify the exact sparsity pattern or engine breakdown. | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | [Unknown/Not Disclosed] | — |
| Scale up | NeuronLink-v3: 1.28 TB/s per chip; directionality unspecified in this source. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-chip-components) |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | [Unknown/Not Disclosed] | — |
| Scope | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Notes | — | — |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | AWS Neuron | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| ISA | NeuronCore-v3 ISA extensions support dynamic shapes and control flow. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| Programming model | Custom operators through embedded GPSIMD engines. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |

## Published measurements

No published measurements recorded.

## Open questions

- Per-chip TDP, manufacturing process and exact matrix/vector chip throughput require additional public evidence.

## Sources

- [Source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html)
- [Source 2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v3.html)
