# AMD Instinct MI300X

> English: [amd-instinct-mi300x.md](./amd-instinct-mi300x.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | AMD Instinct MI300X | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 厂商 | AMD | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 加速器类型 | GPU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 变体 | AMD Instinct MI300X 192GB OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 形态 | OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 记录范围 | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 器件数 | 1 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| 快照日期 | 2026-10-22 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | CDNA 3 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| 制程 | TSMC 5nm XCDs; 6nm I/O dies | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=5), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 计算单元 | 304 CUs; 1216 Matrix Cores; 19,456 stream processors; eight XCDs | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| 缓存 | 32 KB L1 per CU; 4 MB L2 per XCD; 256 MB shared Infinity Cache | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| 片上存储 | 64 KB LDS per CU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=9) |
| 执行模型 | GPU compute units with scalar, vector and matrix instruction execution | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=6) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM3 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 容量（GB） | 192.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 容量（GiB） | [Unknown/Not Disclosed] | — |
| 带宽（TB/s） | 5.3 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 范围 | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 说明 | Peak local on-package GPU memory bandwidth; capacity and rate are for one OAM module. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Theoretical peaks preserve source rounding. Accumulation formats are not supplied by the product table. No performance measurements are included. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| FP64 | vector | 81.7 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| FP32 | vector | 163.4 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| FP64 | matrix | 163.4 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| FP32 | matrix | 163.4 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| TF32 | matrix | 653.7 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| TF32 | matrix | 1307.4 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. Registered structure description lists INT8/FP8/FP16/BF16; TF32 pattern is not established. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| FP16 | matrix | 1307.4 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| FP16 | matrix | 2614.9 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. CDNA 3 whitepaper page 8 specifies at least two zero inputs per group of four for INT8/FP8/FP16/BF16. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=8) |
| BF16 | matrix | 1307.4 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| BF16 | matrix | 2614.9 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. CDNA 3 whitepaper page 8 specifies at least two zero inputs per group of four for INT8/FP8/FP16/BF16. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=8) |
| FP8 | matrix | 2614.9 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| FP8 | matrix | 5229.8 | TFLOP/s | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. CDNA 3 whitepaper page 8 specifies at least two zero inputs per group of four for INT8/FP8/FP16/BF16. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=8) |
| INT8 | matrix | 2614.9 | TOPS | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| INT8 | matrix | 5229.8 | TOPS | structured_sparse | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. CDNA 3 whitepaper page 8 specifies at least two zero inputs per group of four for INT8/FP8/FP16/BF16. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=8) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCIe Gen5 x16; 128 GB/s published total bandwidth | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 机内扩展 | Seven Infinity Fabric links; 128 GB/s bidirectional per link | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | 750.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 范围 | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| 说明 | Vendor metric is maximum total board power (TBP), 750 W per OAM module; stored in catalog power field, not measured power. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | AMD ROCm | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=20) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | HIP runtime, API and C++-like language | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=20) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Exact matrix accumulation modes are not stated in the product specification table.
- No public benchmark selected; application performance depends on software and workload.

## 来源

- [Source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf)
- [Source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf)
