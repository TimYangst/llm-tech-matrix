# AMD Instinct MI355X

> 中文版：[amd-instinct-mi355x.zh.md](./amd-instinct-mi355x.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | AMD Instinct MI355X | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Vendor | AMD | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Accelerator type | GPU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Variant | AMD Instinct MI355X 288GB OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Form factor | OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Record scope | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Device count | 1 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |
| Snapshot date | 2026-10-22 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | CDNA 4 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=2) |
| Process | TSMC 3nm XCDs; 6nm I/O dies | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=4) |
| Compute units | 256 CUs; 1024 Matrix Cores; 16,384 stream processors; eight XCDs | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=2) |
| Cache | 32 KB L1 per CU; 4 MB L2 per XCD; 256 MB shared Infinity Cache | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=2) |
| On-chip memory | 160 KB LDS per CU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=9) |
| Execution model | GPU compute units with scalar, vector and matrix instruction execution | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=6) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM3E | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Capacity (GB) | 288.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Capacity (GiB) | [Unknown/Not Disclosed] | — |
| Bandwidth (TB/s) | 8.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Scope | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Notes | Peak local on-package GPU memory bandwidth; capacity and rate are for one OAM module. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Theoretical peaks preserve source rounding. Accumulation formats are not supplied by the product table. No performance measurements are included.; MXFP8/MXFP6/MXFP4 sparsity columns are N/A; no sparse rate is fabricated. PFLOP/s and POPS converted to tera units by decimal unit scaling only. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
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

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCIe Gen5 x16; 128 GB/s published total bandwidth | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Scale up | Seven Infinity Fabric links; 153.6 GB/s peak total aggregate transport data bandwidth per link | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=21) |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | 1400.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Scope | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |
| Notes | Vendor metric is maximum total board power (TBP), 1400 W per OAM module; stored in catalog power field, not measured power. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf#page=1) |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | AMD ROCm | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=17) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | Triton kernel language; vLLM and SGLang serving frameworks | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf#page=17) |

## Published measurements

No published measurements recorded.

## Open questions

- Exact matrix accumulation modes are not stated in the product specification table.
- No public benchmark selected; application performance depends on software and workload.
- Datasheet page 1 lists 7 × 153.6 GB/s links, while page 2 says 160 GB/s bidirectional between GPUs; retain the table value and do not silently reconcile payload vs link rate.
- The datasheet labels sparse peaks without specifying the sparsity structure; the catalog preserves sparse rather than assuming a structure.

## Sources

- [Source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf)
- [Source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf)
