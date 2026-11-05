# Intel Gaudi 3 OAM

> English: [intel-gaudi3-oam.md](./intel-gaudi3-oam.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | Intel Gaudi 3 OAM | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 厂商 | Intel | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 加速器类型 | ASIC | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 变体 | HL-325L OAM | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 形态 | OCP OAM 2.0 mezzanine module | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 记录范围 | per_accelerator | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 器件数 | 1 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 快照日期 | 2026-10-22 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | Gaudi 3 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| 制程 | TSMC 5 nm | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=2) |
| 计算单元 | 2 compute dies; 8 MMEs and 64 TPCs in total. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| 缓存 | 96 MB SRAM configurable as unified L3 or four 24 MB L2 slices. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| 片上存储 | 96 MB SRAM | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| 执行模型 | MMEs for matrix operations; programmable TPCs use VLIW SIMD. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | 8 HBM2e devices | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| 容量（GB） | 128.0 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| 容量（GiB） | [Unknown/Not Disclosed] | — |
| 带宽（TB/s） | 3.7 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| 范围 | per_accelerator | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=16) |
| 说明 | — | — |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Exact rates follow Table 5; the introduction separately rounds BF16/FP8 capability to 1.8 PFLOP/s. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=2), [source 2](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| FP8 | matrix | 1678.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| BF16 | matrix | 1678.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP16 (signed) | matrix | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| TF32 | matrix | 459.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP32 | matrix | 229.0 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP8 | vector | 57.3 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| BF16 | vector | 28.7 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP16 | vector | 28.7 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |
| FP32 | vector | 14.3 | TFLOP/s | undisclosed | per_accelerator | [Unknown/Not Disclosed] | Table 5 peak rate; clock and sparsity conditions not specified. | [Unknown/Not Disclosed] | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=11) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCIe Gen5 x16, 128 GB/s bidirectional total (64 GB/s per direction). | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3) |
| 机内扩展 | 24x200 Gbit/s Ethernet RDMA ports; total networking 1200 GB/s bidirectional. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=3), [source 2](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=18) |
| 跨机扩展 | Three 200 Gbit/s ports per OAM routed for scale-out in the HLB-325 baseboard. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 拓扑 | HLB-325 baseboard: eight OAMs all-to-all using 21 ports per module, with three remaining ports for scale-out. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | 900.0 | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 范围 | per_accelerator | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |
| 说明 | HL-325L OAM supports up to 900 W Total Device Power with passive or liquid cooling. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=4) |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | Intel Gaudi software suite with PyTorch integration. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=19) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | Graph compiler, kernel fusion, kernel libraries and programmable TPC kernels. | [source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf#page=19) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Table 5 does not specify sparse/dense conditions, accumulation precision, clock or FMA counting.

## 来源

- [Source 1](https://cdrdv2-public.intel.com/817486/gaudi-3-ai-accelerator-white-paper.pdf)
