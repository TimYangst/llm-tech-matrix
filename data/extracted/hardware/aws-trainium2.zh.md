# AWS Trainium2

> English: [aws-trainium2.md](./aws-trainium2.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | AWS Trainium2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 厂商 | AWS | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 加速器类型 | ASIC | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 变体 | trainium2 chip | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 形态 | [Unknown/Not Disclosed] | — |
| 记录范围 | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 器件数 | 1 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 快照日期 | 2026-10-22 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | AWS Trainium2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 制程 | [Unknown/Not Disclosed] | — |
| 计算单元 | 8 NeuronCore-v3; 16 collective-communication cores. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 缓存 | [Unknown/Not Disclosed] | — |
| 片上存储 | 224 MiB SBUF per chip, as published in the chip memory table. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#memory) |
| 执行模型 | Heterogeneous Tensor, Vector, Scalar and GPSIMD engines; software-managed SRAM. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v3.html#neuroncore-v3-architecture) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 容量（GB） | [Unknown/Not Disclosed] | — |
| 容量（GiB） | 96.0 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 带宽（TB/s） | 2.9 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 范围 | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 说明 | Published HBM capacity: 96 GiB per chip; retained in source units, not relabeled GB. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Published aggregate chip rates: FP8 1299; BF16/FP16/TF32 667; FP32 181 TFLOP/s; sparse FP8/FP16/BF16/TF32 2563 TFLOP/s. Engine decomposition is unspecified.; NeuronCore-v3 TensorEngine rates are per core and differ from chip aggregate divided by eight; no chip matrix peak is inferred. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#compute), [source 2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v3.html#tensor-engine) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
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

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | [Unknown/Not Disclosed] | — |
| 机内扩展 | NeuronLink-v3: 1.28 TB/s per chip; directionality unspecified in this source. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-chip-components) |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | [Unknown/Not Disclosed] | — |
| 范围 | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 说明 | — | — |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | AWS Neuron | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 指令集 | NeuronCore-v3 ISA extensions support dynamic shapes and control flow. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |
| 编程模型 | Custom operators through embedded GPSIMD engines. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html#trainium2-architecture) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Per-chip TDP, manufacturing process and exact matrix/vector chip throughput require additional public evidence.

## 来源

- [Source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html)
- [Source 2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v3.html)
