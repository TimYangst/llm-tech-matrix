# NVIDIA GeForce RTX 5090: public-source snapshot

- Snapshot: 2026-10-22; schema: hardware v1; scope: one PCIe graphics card.
- Extraction complete; independent review tracked in the project coordination state.
- Public vendor pages/PDFs only. No internal measurements were consulted or published.

## Evidence and caveats

RTX Blackwell whitepaper v1.1, PDF pages 46–48 (Appendix A, Table 3) provides product counts, explicit dense/sparse pairs and accumulation formats. These are reference-product theoretical specifications, not local benchmark results.

## Registered sources

- [whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf): fetched 2026-10-22; SHA-256 `906ff2a409d7a7e4cbc56f5d3a179d574120d19aaba99520670e1a0c064595fa`.
- [product](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/): fetched 2026-10-22; SHA-256 `7861ae59ae7cae13fbf31fd42f2f1c85e68c14380e2329d4d3b4de71588910bd`.

## Open questions

- TF32 and INT8 accumulation formats are not stated in Table 3 and remain unknown.
- FP64 product throughput is not reconstructed from a full-GB202 ratio.
- Partner card power limits, clocks and cooling can differ from this reference product.

## 中文记录

仅采集厂商公开网页和 PDF，记录范围为单个 PCIe graphics card。理论峰值按精度、向量/矩阵操作、稠密/稀疏及累加格式分别保存；不包含内部实测。数值来源、抓取日期和 SHA-256 见上述 manifest 对应条目。
