# NVIDIA B200 SXM (HGX B200 variant)

> English: [nvidia-b200-sxm.md](./nvidia-b200-sxm.md)

仅收录公开来源。理论峰值与公开实测分开；比较时须同时保留精度、运算类型、稀疏条件、器件/系统范围与厂商条件。未披露的参数不作推算。

*Hardware schema: 1*

## 身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | NVIDIA B200 SXM (HGX B200 variant) | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| 厂商 | NVIDIA | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| 加速器类型 | GPU | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| 变体 | Individual B200 GPU in HGX B200; 180 GB HBM3E; excludes GB200 NVL4/NVL72 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| 形态 | Blackwell SXM module | [source 1](https://www.nvidia.com/en-us/data-center/hgx/) |
| 记录范围 | per_accelerator | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| 器件数 | 1 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |
| 快照日期 | 2026-10-22 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 系列 | Blackwell | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |
| 制程 | TSMC 4NP | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |
| 计算单元 | [Unknown/Not Disclosed] | — |
| 缓存 | [Unknown/Not Disclosed] | — |
| 片上存储 | [Unknown/Not Disclosed] | — |
| 执行模型 | Blackwell Tensor Cores; second-generation Transformer Engine | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |
| 说明 | One logical Blackwell GPU combines two reticle-limited dies using a 10 TB/s chip-to-chip link. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=9) |

## 内存

| 字段 | 值 | 证据 |
|---|---|---|
| 存储技术 | HBM3E | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 容量（GB） | 180.0 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 容量（GiB） | [Unknown/Not Disclosed] | — |
| 带宽（TB/s） | 7.7 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 范围 | per_accelerator | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 说明 | Directly transcribed individual HGX B200 GPU column. The GB200 columns list a different 186 GB / 8 TB/s configuration.; Bandwidth is peak local device memory bandwidth; no division of aggregate HGX totals. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

## 理论计算峰值

| 字段 | 值 | 证据 |
|---|---|---|
| 说明 | PFLOP/s-to-TFLOP/s conversion is a decimal unit conversion only; no system-to-device or sparse-to-dense derivation. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

| 精度 | 运算类型 | 速率 | 单位 | 稀疏条件 | 范围 | 累加精度 | 条件 | FMA 计数 | 证据 |
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

## 互连

| 字段 | 值 | 证据 |
|---|---|---|
| 主机接口 | PCIe Gen5; 128 GB/s published aggregate bandwidth, direction not specified in this table | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 机内扩展 | Fifth-generation NVLink; 1.8 TB/s per GPU, direction not specified in this table | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 跨机扩展 | [Unknown/Not Disclosed] | — |
| 拓扑 | [Unknown/Not Disclosed] | — |

## 功耗

| 字段 | 值 | 证据 |
|---|---|---|
| TDP（W） | 1000.0 | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 范围 | per_accelerator | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |
| 说明 | Maximum configurable individual HGX B200 GPU TDP; GB200 columns have a different up-to-1200 W limit. | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=8) |

## 软件

| 字段 | 值 | 证据 |
|---|---|---|
| 生态 | NVIDIA TensorRT-LLM; NeMo Framework | [source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf#page=6) |
| 指令集 | [Unknown/Not Disclosed] | — |
| 编程模型 | [Unknown/Not Disclosed] | — |

## 公开实测

暂无公开实测记录。

## 开放问题

- Operation-specific FP64 vector and FP64 Tensor Core values cannot be separated from the combined vendor row.
- SM counts and cache capacities for this exact shipped B200 variant are not established by the registered datasheet.
- Dense matrix peaks are omitted rather than deriving half of sparse specifications.

## 来源

- [Source 1](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf)
- [Source 2](https://www.nvidia.com/en-us/data-center/hgx/)
