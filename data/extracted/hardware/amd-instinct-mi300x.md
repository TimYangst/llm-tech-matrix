# AMD Instinct MI300X

> 中文版：[amd-instinct-mi300x.zh.md](./amd-instinct-mi300x.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | AMD Instinct MI300X | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Vendor | AMD | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Accelerator type | GPU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Variant | AMD Instinct MI300X 192GB OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Form factor | OAM module | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Record scope | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Device count | 1 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |
| Snapshot date | 2026-10-22 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | CDNA 3 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| Process | TSMC 5nm XCDs; 6nm I/O dies | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=5), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Compute units | 304 CUs; 1216 Matrix Cores; 19,456 stream processors; eight XCDs | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| Cache | 32 KB L1 per CU; 4 MB L2 per XCD; 256 MB shared Infinity Cache | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| On-chip memory | 64 KB LDS per CU | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=9) |
| Execution model | GPU compute units with scalar, vector and matrix instruction execution | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=6) |
| Notes | — | — |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM3 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Capacity (GB) | 192.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Capacity (GiB) | [Unknown/Not Disclosed] | — |
| Bandwidth (TB/s) | 5.3 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Scope | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Notes | Peak local on-package GPU memory bandwidth; capacity and rate are for one OAM module. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | Theoretical peaks preserve source rounding. Accumulation formats are not supplied by the product table. No performance measurements are included. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
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

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCIe Gen5 x16; 128 GB/s published total bandwidth | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Scale up | Seven Infinity Fabric links; 128 GB/s bidirectional per link | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1), [source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=2) |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | 750.0 | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Scope | per_accelerator | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |
| Notes | Vendor metric is maximum total board power (TBP), 750 W per OAM module; stored in catalog power field, not measured power. | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf#page=1) |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | AMD ROCm | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=20) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | HIP runtime, API and C++-like language | [source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf#page=20) |

## Published measurements

No published measurements recorded.

## Open questions

- Exact matrix accumulation modes are not stated in the product specification table.
- No public benchmark selected; application performance depends on software and workload.

## Sources

- [Source 1](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf)
- [Source 2](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf)
