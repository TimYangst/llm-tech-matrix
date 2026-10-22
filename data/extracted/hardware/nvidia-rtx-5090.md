# NVIDIA GeForce RTX 5090

> 中文版：[nvidia-rtx-5090.zh.md](./nvidia-rtx-5090.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | NVIDIA GeForce RTX 5090 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| Vendor | NVIDIA | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| Accelerator type | GPU | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| Variant | Reference desktop RTX 5090 32GB / Founders Edition; excludes RTX 5090 D and partner overclocks | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| Form factor | PCIe graphics card | [source 1](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/) |
| Record scope | per_accelerator | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| Device count | 1 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| Snapshot date | 2026-10-22 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | RTX Blackwell (GB202) | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=46) |
| Process | TSMC 4nm 4N NVIDIA custom process | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| Compute units | 170 enabled SMs; 21,760 CUDA cores; 680 fifth-generation Tensor Cores; 170 fourth-generation RT Cores | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=46) |
| Cache | 96 MB L2 (98,304 KB) | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| On-chip memory | 128 KB configurable L1/shared memory and 256 KB register file per SM | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=10) |
| Execution model | Streaming multiprocessors with CUDA, Tensor and RT execution units | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=10) |
| Notes | The full GB202 design has 192 SMs and 128 MB L2; those full-die figures are not the RTX 5090 product configuration. | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=9) |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | GDDR7 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| Capacity (GB) | 32.0 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| Capacity (GiB) | [Unknown/Not Disclosed] | — |
| Bandwidth (TB/s) | 1.792 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| Scope | per_accelerator | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| Notes | 512-bit memory interface; 28 Gbit/s memory data rate. Peak local memory bandwidth; no read-plus-write aggregation. | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | — | — |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| FP32 | vector | 104.8 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Peak rate based on GPU Boost Clock (2407 MHz in Table 3). | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=46) |
| FP16 | vector | 104.8 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Peak rate based on GPU Boost Clock (2407 MHz in Table 3). | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| BF16 | vector | 104.8 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Peak rate based on GPU Boost Clock (2407 MHz in Table 3). | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP4 | matrix | 1676.0 | TFLOP/s | dense | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP4 | matrix | 3352.0 | TFLOP/s | sparse_unspecified | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP8 | matrix | 838.0 | TFLOP/s | dense | per_accelerator | FP16 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP8 | matrix | 1676.0 | TFLOP/s | sparse_unspecified | per_accelerator | FP16 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP8 | matrix | 419.0 | TFLOP/s | dense | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP8 | matrix | 838.0 | TFLOP/s | sparse_unspecified | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP16 | matrix | 419.0 | TFLOP/s | dense | per_accelerator | FP16 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP16 | matrix | 838.0 | TFLOP/s | sparse_unspecified | per_accelerator | FP16 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP16 | matrix | 209.5 | TFLOP/s | dense | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| FP16 | matrix | 419.0 | TFLOP/s | sparse_unspecified | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| BF16 | matrix | 209.5 | TFLOP/s | dense | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| BF16 | matrix | 419.0 | TFLOP/s | sparse_unspecified | per_accelerator | FP32 | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| TF32 | matrix | 104.8 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| TF32 | matrix | 209.5 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| INT8 | matrix | 838.0 | TOPS | dense | per_accelerator | [Unknown/Not Disclosed] | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| INT8 | matrix | 1676.0 | TOPS | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Table 3 publishes the pair explicitly; second value uses Sparsity Feature (footnote 2); peak rates based on GPU Boost Clock. | [Unknown/Not Disclosed] | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCI Express Gen5 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| Scale up | [Unknown/Not Disclosed] | — |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | 575.0 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| Scope | per_accelerator | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| Notes | Vendor metric is Total Graphics Power (TGP), stored in the catalog power field; not minimum system PSU power or measured power. | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | NVIDIA CUDA | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=12) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | [Unknown/Not Disclosed] | — |

## Published measurements

No published measurements recorded.

## Open questions

- TF32 and INT8 accumulation formats are not stated in Table 3 and remain unknown.
- FP64 product throughput is not reconstructed from a full-GB202 ratio.
- Partner card power limits, clocks and cooling can differ from this reference product.

## Sources

- [Source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf)
- [Source 2](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/)
