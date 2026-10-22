# NVIDIA H100 SXM 80GB: public-source snapshot

- Snapshot: 2026-10-22; schema: hardware v1; scope: one SXM5 module.
- Extraction complete; independent review tracked in the project coordination state.
- Public vendor pages/PDFs only. No internal measurements were consulted or published.

## Evidence and caveats

Product Specifications: H100 SXM column, with-sparsity footnote. The technical blog provides the SXM5 configuration and the per-direction PCIe/NVLink interpretation; its preliminary launch throughput numbers are not used.

## Registered sources

- [product](https://www.nvidia.com/en-us/data-center/h100/): fetched 2026-10-22; SHA-256 `fa8a2aba20f56ff23127078447419a5ae94643c54aba181dc2a7f8b6c08db5fb`.
- [architecture](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/): fetched 2026-10-22; SHA-256 `0ad9c690d09fb434705011e593994b4948294f182a7e954c900cf1061e5c522d`.
- [technical-blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/): fetched 2026-10-22; SHA-256 `29de170a1079fe9747535a752eb45ce27a6376a3f452f118ed7b515f1414f95b`.

## Open questions

- Dense Tensor Core rates at the same final-product configuration and accumulation formats are not separately listed on the current product page.
- No public workload measurements selected in this snapshot; theoretical peaks cannot establish application throughput.

## 中文记录

仅采集厂商公开网页和 PDF，记录范围为单个 SXM5 module。理论峰值按精度、向量/矩阵操作、稠密/稀疏及累加格式分别保存；不包含内部实测。数值来源、抓取日期和 SHA-256 见上述 manifest 对应条目。
