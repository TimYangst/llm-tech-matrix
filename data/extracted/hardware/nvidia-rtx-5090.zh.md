# NVIDIA GeForce RTX 5090

> English: [nvidia-rtx-5090.md](./nvidia-rtx-5090.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | NVIDIA GeForce RTX 5090 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| 厂商 | NVIDIA | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| 加速器类型 | GPU | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| 变体 | Reference desktop RTX 5090 32GB / Founders Edition; excludes RTX 5090 D and partner overclocks | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| 形态 | PCIe graphics card | [source 1](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/) |
| 记录范围 | per_accelerator | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| 器件数 | 1 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |
| 快照日期 | 2026-10-22 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | RTX Blackwell (GB202) | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=46) |
| 制程 | TSMC 4nm 4N NVIDIA custom process | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| 计算单元 | 170 enabled SMs; 21,760 CUDA cores; 680 fifth-generation Tensor Cores; 170 fourth-generation RT Cores | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=46) |
| 缓存 | 96 MB L2 (98,304 KB) | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| 片上存储 | 128 KB configurable L1/shared memory and 256 KB register file per SM | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=10) |
| 执行模型 | Streaming multiprocessors with CUDA, Tensor and RT execution units | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=10) |
| 说明 | The full GB202 design has 192 SMs and 128 MB L2; those full-die figures are not the RTX 5090 product configuration. | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=9) |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | GDDR7 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| 容量（GB） | 32.0 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| 容量（GiB） | [Unknown/Not Disclosed] | — |
| 带宽（TB/s） | 1.792 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| 范围 | per_accelerator | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |
| 说明 | 512-bit memory interface; 28 Gbit/s memory data rate. Peak local memory bandwidth; no read-plus-write aggregation. | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=47) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | — | — |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
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

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCI Express Gen5 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| 机内扩展 | [Unknown/Not Disclosed] | — |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | 575.0 | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| 范围 | per_accelerator | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |
| 说明 | Vendor metric is Total Graphics Power (TGP), stored in the catalog power field; not minimum system PSU power or measured power. | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=48) |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | NVIDIA CUDA | [source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf#page=12) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | [Unknown/Not Disclosed] | — |

## 公开实测

暂无公开实测记录。

## 开放问题

- TF32 and INT8 accumulation formats are not stated in Table 3 and remain unknown.
- FP64 product throughput is not reconstructed from a full-GB202 ratio.
- Partner card power limits, clocks and cooling can differ from this reference product.

## 来源

- [Source 1](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf)
- [Source 2](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/)
