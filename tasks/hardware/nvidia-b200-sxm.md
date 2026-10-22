# NVIDIA B200 SXM (HGX B200 variant): public-source snapshot

- Snapshot: 2026-10-22; schema: hardware v1; scope: one Blackwell SXM module.
- Extraction complete; independent review tracked in the project coordination state.
- Public vendor pages/PDFs only. No internal measurements were consulted or published.

## Evidence and caveats

Blackwell datasheet, PDF page 8: use Individual Blackwell GPU Specifications → HGX B200 column. Values are 180 GB, 7.7 TB/s, up to 1000 W. Page 9 supplies the two-die architecture. Do not substitute GB200 or the eight-GPU HGX aggregates.

## Registered sources

- [datasheet](https://dam-cdn.nvd.orangelogic.com/AssetLink/y441155802qub41q118b2852i557jem5.pdf): fetched 2026-10-22; SHA-256 `ad8ed65e64974278670d8e6904c0e3020391027925e339bf28e75fdfe2d307d7`.
- [product](https://www.nvidia.com/en-us/data-center/hgx/): fetched 2026-10-22; SHA-256 `ae2c8dd2eebcbba9b1b5e2e4bd186ff15e8d547314b3f63695910e1412a4d261`.

## Open questions

- Operation-specific FP64 vector and FP64 Tensor Core values cannot be separated from the combined vendor row.
- SM counts and cache capacities for this exact shipped B200 variant are not established by the registered datasheet.
- Dense matrix peaks are omitted rather than deriving half of sparse specifications.

## 中文记录

仅采集厂商公开网页和 PDF，记录范围为单个 Blackwell SXM module。理论峰值按精度、向量/矩阵操作、稠密/稀疏及累加格式分别保存；不包含内部实测。数值来源、抓取日期和 SHA-256 见上述 manifest 对应条目。
