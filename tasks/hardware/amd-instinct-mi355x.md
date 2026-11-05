# AMD Instinct MI355X: public-source snapshot

- Snapshot: 2026-10-22; schema: hardware v1; scope: one OAM module.
- Extraction complete; independent review tracked in the project coordination state.
- Public vendor pages/PDFs only. No internal measurements were consulted or published.

## Evidence and caveats

Datasheet PDF page 1 separates peak theoretical AI dense/with-sparsity columns and HPC vector/matrix rows. Page 2 and the architecture whitepaper supply chiplet/cache/software details. CDNA4 whitepaper page 9 documents 160 KB LDS; page 21 gives the 153.6 GB/s per-link transport-data qualification.

## Registered sources

- [datasheet](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/product-briefs/amd-instinct-mi355x-gpu-brochure.pdf): fetched 2026-10-22; SHA-256 `e1a411c53e034f3ea528a75383774a175f52ccd1a58f630d7717d1dca6a2f7c2`.
- [whitepaper](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-4-architecture-whitepaper.pdf): fetched 2026-10-22; SHA-256 `7ebf89edb9b82198b9edea7bb37eb7fe7c998842257eb21ef7a459a87774a4b2`.

## Open questions

- Exact matrix accumulation modes are not stated in the product specification table.
- No public benchmark selected; application performance depends on software and workload.
- Datasheet page 1 lists 7 × 153.6 GB/s links, while page 2 says 160 GB/s bidirectional between GPUs; retain the table value and do not silently reconcile payload vs link rate.
- The datasheet labels sparse peaks without specifying the sparsity structure; the catalog preserves sparse rather than assuming a structure.

## 中文记录

仅采集厂商公开网页和 PDF，记录范围为单个 OAM module。理论峰值按精度、向量/矩阵操作、稠密/稀疏及累加格式分别保存；不包含内部实测。数值来源、抓取日期和 SHA-256 见上述 manifest 对应条目。
