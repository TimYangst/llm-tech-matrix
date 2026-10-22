# MiniMax Sparse Attention (MSA)

> 中文版：[msa.zh.md](./msa.zh.md)

**Slug:** `msa`

MSA adds a lightweight index branch to grouped-query attention. The indexer ranks KV blocks for each group using max-pooled scores; the main branch performs softmax attention over selected blocks plus mandatory local context. The research report evaluates a 109B MoE, while the released M3 has a different parameter scale: report training budgets and speedups must keep their experimental scope. M3 replaces the earlier MiniMax Lightning hybrid with this sparse GQA path.

## Used by

| Model      | Variation / details                                                                         |
| ---------- | ------------------------------------------------------------------------------------------- |
| MiniMax-M3 | Sparse GQA; deployed configuration and research-model measurements are recorded separately. |

## Reference materials

- [MiniMax Sparse Attention](https://arxiv.org/abs/2606.13392)
