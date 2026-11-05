# NVIDIA B200 SXM (HGX B200 variant)

> 中文版：[nvidia-b200-sxm.zh.md](./nvidia-b200-sxm.zh.md)

Public sources only. Theoretical peaks and published measurements are separate. Comparisons must retain precision, operation, sparsity, device/system scope and vendor conditions. Undisclosed specifications are not inferred.

*Hardware schema: 1*

## Identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | NVIDIA B200 SXM (HGX B200 variant) | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| Vendor | NVIDIA | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| Accelerator type | GPU | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| Variant | Individual B200 GPU in HGX B200; 180 GB HBM3E; excludes GB200 NVL4/NVL72 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| Form factor | Blackwell SXM module | [source 1](https://www.nvidia.com/en-us/data-center/hgx/) |
| Record scope | per_accelerator | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| Device count | 1 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| Snapshot date | 2026-10-22 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Family | Blackwell | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |
| Process | TSMC 4NP | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |
| Compute units | [Unknown/Not Disclosed] | — |
| Cache | [Unknown/Not Disclosed] | — |
| On-chip memory | [Unknown/Not Disclosed] | — |
| Execution model | Blackwell Tensor Cores; second-generation Transformer Engine | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |
| Notes | One logical Blackwell GPU combines two reticle-limited dies using a 10 TB/s chip-to-chip link. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |

## Memory

| Field | Value | Evidence |
|---|---|---|
| Technology | HBM3E | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Capacity (GB) | 180.0 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Capacity (GiB) | [Unknown/Not Disclosed] | — |
| Bandwidth (TB/s) | 7.7 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Scope | per_accelerator | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Notes | Directly transcribed individual HGX B200 GPU column. The GB200 columns list a different 186 GB / 8 TB/s configuration.; Bandwidth is peak local device memory bandwidth; no division of aggregate HGX totals. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

## Theoretical compute peaks

| Field | Value | Evidence |
|---|---|---|
| Notes | PFLOP/s-to-TFLOP/s conversion is a decimal unit conversion only; no system-to-device or sparse-to-dense derivation. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

| Precision | Operation | Rate | Unit | Sparsity | Scope | Accumulation | Conditions | FMA counting | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| FP32 | vector | 75.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Vendor-published theoretical peak; not a measured workload result. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| FP64 / FP64 Tensor Core | undisclosed | 37.0 | TFLOP/s | dense | per_accelerator | [Unknown/Not Disclosed] | Datasheet combines FP64 / FP64 Tensor Core in one row; operation-specific vector and matrix peaks are not independently established. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| FP4 | matrix | 18000.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| FP8 | matrix | 9000.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| FP6 | matrix | 9000.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| INT8 | matrix | 9000.0 | TOPS | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| FP16 | matrix | 4500.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| BF16 | matrix | 4500.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| TF32 | matrix | 2200.0 | TFLOP/s | sparse_unspecified | per_accelerator | [Unknown/Not Disclosed] | Individual HGX B200 GPU column; footnote 2 marks sparse rates. Dense values are not derived by division. | [Unknown/Not Disclosed] | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

## Interconnect

| Field | Value | Evidence |
|---|---|---|
| Host | PCIe Gen5; 128 GB/s published aggregate bandwidth, direction not specified in this table | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Scale up | Fifth-generation NVLink; 1.8 TB/s per GPU, direction not specified in this table | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Scale out | [Unknown/Not Disclosed] | — |
| Topology | [Unknown/Not Disclosed] | — |

## Power

| Field | Value | Evidence |
|---|---|---|
| TDP (W) | 1000.0 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Scope | per_accelerator | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| Notes | Maximum configurable individual HGX B200 GPU TDP; GB200 columns have a different up-to-1200 W limit. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

## Software

| Field | Value | Evidence |
|---|---|---|
| Ecosystem | NVIDIA TensorRT-LLM; NeMo Framework | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=6) |
| ISA | [Unknown/Not Disclosed] | — |
| Programming model | [Unknown/Not Disclosed] | — |

## Published measurements

No published measurements recorded.

## Open questions

- Operation-specific FP64 vector and FP64 Tensor Core values cannot be separated from the combined vendor row.
- SM counts and cache capacities for this exact shipped B200 variant are not established by the registered datasheet.
- Dense matrix peaks are omitted rather than deriving half of sparse specifications.

## Sources

- [Source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf)
- [Source 2](https://www.nvidia.com/en-us/data-center/hgx/)
