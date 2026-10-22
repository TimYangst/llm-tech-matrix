# AWS Inferentia2

> English: [aws-inferentia2.md](./aws-inferentia2.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | AWS Inferentia2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 厂商 | AWS | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 加速器类型 | ASIC | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 变体 | inferentia2 chip | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 形态 | [Unknown/Not Disclosed] | — |
| 记录范围 | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 器件数 | 1 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 快照日期 | 2026-10-22 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | AWS Inferentia2 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 制程 | [Unknown/Not Disclosed] | — |
| 计算单元 | 2 NeuronCore-v2. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 缓存 | [Unknown/Not Disclosed] | — |
| 片上存储 | [Unknown/Not Disclosed] | — |
| 执行模型 | Heterogeneous Tensor, Vector, Scalar and GPSIMD engines; software-managed SRAM. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v2.html#neuroncore-v2-architecture) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 容量（GB） | [Unknown/Not Disclosed] | — |
| 容量（GiB） | 32.0 | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 带宽（TB/s） | [Unknown/Not Disclosed] | — |
| 范围 | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 说明 | Published HBM capacity: 32 GiB per chip; retained in source units, not relabeled GB.; Published bandwidth: 820 GiB/s; not relabeled decimal GB/s or TB/s. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Published aggregate chip rates: INT8 380 TOPS; FP16/BF16/cFP8/TF32 190 TFLOP/s; FP32 47.5 TFLOP/s. Engine decomposition, sparsity, accumulation and FMA counting are unspecified. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| INT8 | undisclosed | 380.0 | TOPS | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| FP16 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| BF16 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| cFP8 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| TF32 | undisclosed | 190.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| FP32 | undisclosed | 47.5 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | [Unknown/Not Disclosed] | — |
| 机内扩展 | NeuronLink-v2; bandwidth and directionality are unspecified in this source. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | [Unknown/Not Disclosed] | — |
| 范围 | per_accelerator | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 说明 | — | — |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | AWS Neuron | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 指令集 | NeuronCore-v2 ISA extensions support dynamic shapes and control flow. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |
| 编程模型 | Custom operators through embedded GPSIMD engines. | [source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html#inferentia2-architecture) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Per-chip TDP, manufacturing process and exact matrix/vector chip throughput require additional public evidence.

## 来源

- [Source 1](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html)
- [Source 2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/neuron-core-v2.html)
