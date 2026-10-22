# Lightning Attention

> English: [lightning-attention.md](./lightning-attention.md)

**Slug:** `lightning-attention`

Lightning Attention 是 MiniMax-01 与 M1 使用的线性注意力路径。MiniMax-01 每七层 Lightning 后接一层 softmax/GQA，将递推的线性状态计算与周期性的全注意力结合。M1 沿用混合骨干，长推理后训练属于另一项变化。它与 DeepSeek 用来选择稀疏 softmax 项的 lightning indexer 不是同一机制。

## 使用模型

| 模型            | 变体 / 说明                                   |
| --------------- | --------------------------------------------- |
| MiniMax-Text-01 | 7:1 Lightning/GQA 混合；长上下文外推。        |
| MiniMax-VL-01   | 同系列语言骨干，增加视觉编码器与投影。        |
| MiniMax-M1-80k  | 采用 Lightning/softmax 混合架构的推理检查点。 |

## 参考资料

- [MiniMax-01 report](https://arxiv.org/abs/2501.08313)
- [MiniMax-M1 report](https://arxiv.org/abs/2506.13585)
