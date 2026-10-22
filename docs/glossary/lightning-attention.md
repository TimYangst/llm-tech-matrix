# Lightning Attention

> 中文版：[lightning-attention.zh.md](./lightning-attention.zh.md)

**Slug:** `lightning-attention`

Lightning Attention is the linear-attention path in MiniMax-01 and M1. MiniMax-01 interleaves seven Lightning blocks with one softmax/GQA block, combining recurrent linear-state computation with periodic exact attention. M1 retains the hybrid backbone; its extended reasoning post-training is a separate change. This is distinct from DeepSeek’s “lightning indexer”, which selects sparse softmax-attention entries.

## Used by

| Model           | Variation / details                                                |
| --------------- | ------------------------------------------------------------------ |
| MiniMax-Text-01 | 7:1 Lightning/GQA hybrid; long-context extrapolation.              |
| MiniMax-VL-01   | Same language-backbone family with vision encoder/projector.       |
| MiniMax-M1-80k  | Reasoning checkpoint on the hybrid Lightning/softmax architecture. |

## Reference materials

- [MiniMax-01 report](https://arxiv.org/abs/2501.08313)
- [MiniMax-M1 report](https://arxiv.org/abs/2506.13585)
