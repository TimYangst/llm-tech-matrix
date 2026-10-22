# NVIDIA H100 SXM 80GB

> English: [nvidia-h100-sxm-80gb.md](./nvidia-h100-sxm-80gb.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | NVIDIA H100 SXM 80GB | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 厂商 | NVIDIA | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 加速器类型 | GPU | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 变体 | H100 SXM 80GB; excludes H100 NVL and PCIe variants | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 形态 | SXM5 module | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 记录范围 | per_accelerator | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 器件数 | 1 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 快照日期 | 2026-10-22 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | Hopper (GH100) | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 制程 | TSMC 4N | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 计算单元 | 132 SMs; 16,896 FP32 CUDA cores; 528 fourth-generation Tensor Cores | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 缓存 | 50 MB L2; product configuration, not the 60 MB full GH100 die | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 片上存储 | Up to 228 KB shared memory per SM | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 执行模型 | CUDA threads, thread blocks and thread block clusters; asynchronous tensor memory transfers | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 说明 | Architecture counts use the H100 SXM5 product configuration; launch-era compute rates are not used. | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM3 | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 容量（GB） | 80.0 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 容量（GiB） | [Unknown/Not Disclosed] | — |
| 带宽（TB/s） | 3.35 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 范围 | per_accelerator | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 说明 | Peak local GPU-memory bandwidth; not NVLink bandwidth or read-plus-write aggregate. | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Current product page publishes sparse Tensor Core rates; unlisted dense Tensor rates and FP4 rates remain unrecorded. | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| FP64 | vector | 34.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| FP64 | matrix | 67.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| FP32 | vector | 67.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| TF32 | matrix | 989.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| BF16 | matrix | 1979.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| FP16 | matrix | 1979.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| FP8 | matrix | 3958.0 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| INT8 | matrix | 3958.0 | TOPS | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Product specification marked with the with-sparsity footnote; dense throughput is not inferred. | [Unknown/Not Disclosed] | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCIe Gen5; 128 GB/s total bidirectional (64 GB/s each direction) | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 机内扩展 | Fourth-generation NVLink; 900 GB/s total bidirectional per GPU | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | 700.0 | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 范围 | per_accelerator | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |
| 说明 | Maximum configurable GPU TDP; up to 700 W, not observed power or full-server power. | [source 1](https://www.nvidia.com/en-us/data-center/h100/) |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | NVIDIA CUDA; Transformer Engine | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | CUDA threads, thread blocks, thread block clusters and cooperative groups | [source 1](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Dense Tensor Core rates at the same final-product configuration and accumulation formats are not separately listed on the current product page.
- No public workload measurements selected in this snapshot; theoretical peaks cannot establish application throughput.

## 来源

- [Source 1](https://www.nvidia.com/en-us/data-center/h100/)
- [Source 2](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/)
- [Source 3](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
