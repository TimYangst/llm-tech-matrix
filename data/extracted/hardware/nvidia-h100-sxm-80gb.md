# NVIDIA H100 SXM 80GB

> 中文版：[nvidia-h100-sxm-80gb.zh.md](./nvidia-h100-sxm-80gb.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | NVIDIA H100 SXM 80GB | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Vendor | NVIDIA | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Accelerator type | GPU | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Variant | H100 SXM 80GB; excludes H100 NVL and PCIe variants | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Form factor | SXM5 module | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Record scope | per_accelerator | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Device count | 1 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Snapshot date | 2026-10-22 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | Hopper (GH100) | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Process | TSMC 4N | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Compute units | 132 SMs; 16,896 FP32 CUDA cores; 528 fourth-generation Tensor Cores | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Cache | 50 MB L2; product configuration, not the 60 MB full GH100 die | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| On-chip memory | Up to 228 KB shared memory per SM | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Execution model | CUDA threads, thread blocks and thread block clusters; asynchronous tensor memory transfers | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Notes | Architecture counts use the H100 SXM5 product configuration; launch-era compute rates are not used. | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM3 | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Capacity (GB) | 80.0 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Capacity (GiB) | [Unknown/Not Disclosed] | — |
| Bandwidth (TB/s) | 3.35 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Scope | per_accelerator | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Notes | Peak local GPU-memory bandwidth; not NVLink bandwidth or read-plus-write aggregate. | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Current product page publishes sparse Tensor Core rates; unlisted dense Tensor rates and FP4 rates remain unrecorded. | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| FP64 | vector | 34.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| FP64 | matrix | 67.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| FP32 | vector | 67.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| TF32 | matrix | 989.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. Hopper architecture article identifies Tensor Core sparsity as fine-grained structured sparsity. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/), [source 2](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| BF16 | matrix | 1979.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. Hopper architecture article identifies Tensor Core sparsity as fine-grained structured sparsity. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/), [source 2](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| FP16 | matrix | 1979.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. Hopper architecture article identifies Tensor Core sparsity as fine-grained structured sparsity. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/), [source 2](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| FP8 | matrix | 3958.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. Hopper architecture article identifies Tensor Core sparsity as fine-grained structured sparsity. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/), [source 2](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| INT8 | matrix | 3958.0 | TOPS | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. Hopper architecture article identifies Tensor Core sparsity as fine-grained structured sparsity. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/), [source 2](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCIe Gen5; 128 GB/s total bidirectional (64 GB/s each direction) | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Scale up | Fourth-generation NVLink; 900 GB/s total bidirectional per GPU | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | 700.0 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Scope | per_accelerator | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| Notes | Maximum configurable GPU TDP; up to 700 W, not observed power or full-server power. | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | NVIDIA CUDA; Transformer Engine | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | CUDA threads, thread blocks, thread block clusters and cooperative groups | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |

## Published measurements

No published measurements recorded.

## Open questions

- Dense Tensor Core rates at the same final-product configuration and accumulation formats are not separately listed on the current product page.
- No public workload measurements selected in this snapshot; theoretical peaks cannot establish application throughput.

## Sources

- [Source 1](https://www.nvidia.com/en-us/data-center/h100/)
- [Source 2](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/)
- [Source 3](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
