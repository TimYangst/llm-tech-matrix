# Google TPU7x (Ironwood)

> English: [google-tpu7x-ironwood.md](./google-tpu7x-ironwood.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | Google TPU7x (Ironwood) | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 厂商 | Google | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 加速器类型 | TPU | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 变体 | TPU7x whole chip; two chiplets | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#dual-chiplet_architecture) |
| 形态 | [Unknown/Not Disclosed] | — |
| 记录范围 | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 器件数 | 1 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 快照日期 | 2026-10-22 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | Ironwood, seventh-generation TPU | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x) |
| 制程 | [Unknown/Not Disclosed] | — |
| 计算单元 | 2 TensorCores and 4 SparseCores per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 缓存 | [Unknown/Not Disclosed] | — |
| 片上存储 | VMEM is on-chip SRAM; size is not given. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#memory_hierarchy) |
| 执行模型 | Two chiplets with separate memory spaces; frameworks expose two devices per physical chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#dual-chiplet_architecture) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 容量（GB） | [Unknown/Not Disclosed] | — |
| 容量（GiB） | 192.0 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 带宽（TB/s） | 7.38 | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 范围 | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 说明 | Published capacity: 192 GiB per physical chip, 96 GiB per chiplet; not relabeled GB.; Specification table gives 7380 GB/s per chip; decimal conversion to TB/s. Memory-hierarchy prose rounds this to approximately 7.37 TB/s. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Published whole-chip peaks: BF16 2307 TFLOP/s and FP8 4614 TFLOP/s; engine breakdown, sparsity, accumulation, and FMA counting are unspecified. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| BF16 | undisclosed | 2307.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| FP8 | undisclosed | 4614.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCIe connects each four-chip group to its CPU host; generation and link width unspecified. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#memory_hierarchy) |
| 机内扩展 | ICI: six links at 200 GB/s bidirectional each, totaling 1200 GB/s bidirectional per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#configurations) |
| 跨机扩展 | DCN: 100 Gbit/s per chip. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 拓扑 | 3D mesh below 64 chips; 4x4x4 cubes and larger slices use 3D torus. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#configurations) |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | [Unknown/Not Disclosed] | — |
| 范围 | per_accelerator | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#system-architecture) |
| 说明 | — | — |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | JAX and PyTorch; TensorFlow unsupported. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | Two framework-visible devices per chip, each with its own memory space. | [source 1](https://docs.cloud.google.com/tpu/docs/tpu7x#programming_model_and_framework_exposure) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Process technology, per-chip power, and exact matrix/vector decomposition remain undisclosed in this snapshot.

## 来源

- [Source 1](https://docs.cloud.google.com/tpu/docs/tpu7x)
