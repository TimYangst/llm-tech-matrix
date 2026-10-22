# AMD Instinct MI300X: public-source snapshot

- Snapshot: 2026-10-22; schema: hardware v1; scope: one OAM module.
- Extraction complete; independent review tracked in the project coordination state.
- Public vendor pages/PDFs only. No internal measurements were consulted or published.

## Evidence and caveats

Datasheet PDF page 1 separates peak theoretical AI dense/with-sparsity columns and HPC vector/matrix rows. Page 2 and the architecture whitepaper supply chiplet/cache/software details. CDNA3 whitepaper describes two-of-four sparsity.

## Registered sources

- [datasheet](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf): fetched 2026-10-22; SHA-256 `60d78bc2849cd7c3a34aa17fdbcd263c44c0447d597895ab41d2832ab740c7ab`.
- [whitepaper](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf): fetched 2026-10-22; SHA-256 `a0811d04f101f9127bd183d6e228f462b6fd988b0e0e6d263a25e4bed712f593`.

Sparse-row source audit: compute-row evidence includes the architecture source establishing structured sparsity; product tables alone establish only the published sparse rate. MI300X TF32 remains `sparse_unspecified` because the cited structure description names other formats.

## Open questions

- Exact matrix accumulation modes are not stated in the product specification table.
- No public benchmark selected; application performance depends on software and workload.

## 中文记录

仅采集厂商公开网页和 PDF，记录范围为单个 OAM module。理论峰值按精度、向量/矩阵操作、稠密/稀疏及累加格式分别保存；不包含内部实测。数值来源、抓取日期和 SHA-256 见上述 manifest 对应条目。
