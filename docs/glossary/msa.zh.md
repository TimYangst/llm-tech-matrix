# MiniMax Sparse Attention (MSA)

> English: [msa.md](./msa.md)

**Slug:** `msa`

MSA 在 GQA 上增加轻量索引分支，按组用最大池化分数选择 KV 块；主分支对选中块和必须保留的局部上下文做 softmax 注意力。论文实验使用 109B MoE，而发布的 M3 参数规模不同，不能把论文训练预算或加速结果直接当作 M3 实测。M3 从此前的 Lightning 混合路线转向稀疏 GQA。

## 使用模型

| 模型       | 变体 / 说明                                      |
| ---------- | ------------------------------------------------ |
| MiniMax-M3 | 稀疏 GQA；部署配置与论文实验模型的测量分开记录。 |

## 参考资料

- [MiniMax Sparse Attention](https://arxiv.org/abs/2606.13392)
