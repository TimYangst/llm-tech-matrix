# Google TPU v5p

> English: [google-tpu-v5p.md](./google-tpu-v5p.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | Google TPU v5p | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 厂商 | Google | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 加速器类型 | TPU | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 变体 | v5p chip | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 形态 | [Unknown/Not Disclosed] | — |
| 记录范围 | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 器件数 | 1 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 快照日期 | 2026-10-22 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | TPU v5p | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 制程 | [Unknown/Not Disclosed] | — |
| 计算单元 | 2 TensorCores and 4 SparseCores per chip; each TensorCore has 4 MXUs, a vector unit, and a scalar unit. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 缓存 | [Unknown/Not Disclosed] | — |
| 片上存储 | [Unknown/Not Disclosed] | — |
| 执行模型 | Matrix Multiply Units (MXUs), vector and scalar execution. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 容量（GB） | [Unknown/Not Disclosed] | — |
| 容量（GiB） | 95.0 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 带宽（TB/s） | 2.765 | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 范围 | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 说明 | Published HBM capacity is 95 GiB per chip; retained in the source unit, not relabeled GB.; Bandwidth is published as 2765 GB/s; decimal conversion to TB/s. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Published chip peaks: BF16 459 TFLOP/s and FP8 459 TFLOP/s. The table does not state engine breakdown, sparsity, accumulation, or FMA counting. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| BF16 | undisclosed | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| FP8 | undisclosed | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | [Unknown/Not Disclosed] | — |
| 机内扩展 | ICI: 1200 GB/s total bidirectional bandwidth per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 跨机扩展 | DCN: 50 Gbit/s per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 拓扑 | 3D torus for slices of 4x4x4 chips and larger; smaller slices lack wrap-around links. | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | [Unknown/Not Disclosed] | — |
| 范围 | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/v5p#system-architecture) |
| 说明 | — | — |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | [Unknown/Not Disclosed] | — |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | [Unknown/Not Disclosed] | — |

## 公开实测

暂无公开实测记录。

## 开放问题

- Per-chip power, process technology, and exact matrix/vector decomposition are not disclosed in this source snapshot.

## 来源

- [Source 1](https://docs.cloud.google.com/tpu/docs/v5p)
