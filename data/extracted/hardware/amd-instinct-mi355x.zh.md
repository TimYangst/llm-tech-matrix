# AMD Instinct MI355X

> English: [amd-instinct-mi355x.md](./amd-instinct-mi355x.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | AMD Instinct MI355X | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 厂商 | AMD | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 加速器类型 | GPU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 变体 | AMD Instinct MI355X 288GB OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 形态 | OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 记录范围 | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 器件数 | 1 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| 快照日期 | 2026-10-22 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | CDNA 4 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=2) |
| 制程 | TSMC 3nm XCDs; 6nm I/O dies | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=4) |
| 计算单元 | 256 CUs; 1024 Matrix Cores; 16,384 stream processors; eight XCDs | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=2) |
| 缓存 | 32 KB L1 per CU; 4 MB L2 per XCD; 256 MB shared Infinity Cache | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=2) |
| 片上存储 | 160 KB LDS per CU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=9) |
| 执行模型 | GPU compute units with scalar, vector and matrix instruction execution | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=6) |
| 说明 | — | — |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM3E | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 容量（GB） | 288.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 容量（GiB） | [Unknown/Not Disclosed] | — |
| 带宽（TB/s） | 8.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 范围 | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 说明 | Peak local on-package GPU memory bandwidth; capacity and rate are for one OAM module. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | Theoretical peaks preserve source rounding. Accumulation formats are not supplied by the product table. No performance measurements are included.; MXFP8/MXFP6/MXFP4 sparsity columns are N/A; no sparse rate is fabricated. PFLOP/s and POPS converted to tera units by decimal unit scaling only. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| FP64 | vector | 78.6 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| FP32 | vector | 157.3 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| FP16 | vector | 157.3 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| FP64 | matrix | 78.6 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| FP32 | matrix | 157.3 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| FP16 | matrix | 2516.6 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| FP16 | matrix | 5033.2 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| BF16 | matrix | 2516.6 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| BF16 | matrix | 5033.2 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| OCP-FP8 | matrix | 5033.2 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| OCP-FP8 | matrix | 10066.4 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| INT8 | matrix | 5033.2 | TOPS | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| INT8 | matrix | 10066.4 | TOPS | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Vendor with-sparsity column; explicitly published rate, not calculated from the dense value. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| MXFP8 | matrix | 5033.2 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| MXFP6 | matrix | 10066.3 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| MXFP4 | matrix | 10066.3 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCIe Gen5 x16; 128 GB/s published total bandwidth | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 机内扩展 | Seven Infinity Fabric links; 153.6 GB/s peak total aggregate transport data bandwidth per link | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=21) |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | 1400.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 范围 | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| 说明 | Vendor metric is maximum total board power (TBP), 1400 W per OAM module; stored in catalog power field, not measured power. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | AMD ROCm | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=17) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | Triton kernel language; vLLM and SGLang serving frameworks | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=17) |

## 公开实测

暂无公开实测记录。

## 开放问题

- Exact matrix accumulation modes are not stated in the product specification table.
- No public benchmark selected; application performance depends on software and workload.
- Datasheet page 1 lists 7 × 153.6 GB/s links, while page 2 says 160 GB/s bidirectional between GPUs; retain the table value and do not silently reconcile payload vs link rate.
- The datasheet labels sparse peaks without specifying the sparsity structure; the catalog preserves sparse rather than assuming a structure.

## 来源

- [Source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf)
- [Source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf)
