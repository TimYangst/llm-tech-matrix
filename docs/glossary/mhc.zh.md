# Manifold-Constrained Hyper-Connections (mHC，流形约束超连接)

> English: [mhc.md](./mhc.md)

**Slug:** `mhc`
**类别：** other（残差流拓扑）
**一句话概括：** 把标准残差连接替换为宽度 `n_hc` 的超连接残差流，并通过 Sinkhorn-Knopp 把层间混合矩阵 `B` 约束在双随机矩阵流形上，从而保证 `∥B∥₂ ≤ 1`、深层堆叠时信号传播非膨胀且数值稳定。
**首次提出：** 超连接（Hyper-Connections）由 Zhu et al., 2025 提出；流形约束 + Sinkhorn 投影由专门的 mHC 论文（Xie et al., 2026）引入，DeepSeek-V4 第 2.2 节直接引用。

## 概述

标准 Transformer 的残差流是 `R^d` 维。**Hyper-Connections (HC)** 把它扩展到 `R^(n_hc × d)`，并在每层引入三个小线性映射：
`X_{l+1} = B_l · X_l + C_l · F_l(A_l · X_l)`
其中 `A_l ∈ R^(1×n_hc)` 把残差投影成层输入，`F_l` 是该层算子（注意力或 MoE），`C_l ∈ R^(n_hc×1)` 把输出写回，`B_l ∈ R^(n_hc×n_hc)` 在 `n_hc` 个槽位之间混合残差流自身。它把残差宽度与隐藏维度解耦，几乎无额外算力开销，但堆叠多层 HC 时数值稳定性较差。

**mHC 的贡献**是把 `B_l` 约束到双随机矩阵流形（Birkhoff 多面体）上：先产生未约束的 `B̃_l`，取 `M^(0) = exp(B̃_l)`，再做 `t_max ≈ 20` 次 Sinkhorn-Knopp 行列归一化迭代，收敛到行和、列和都为 1 的 `B_l`。这保证了 `∥B_l∥₂ ≤ 1`（前向、反向均非膨胀），且该流形对乘法封闭，深层堆叠依旧稳定。`A_l`、`C_l` 额外用 Sigmoid 约束为非负且有界（`A = σ(Ã)`，`C = 2·σ(C̃)`）。

映射采用动态参数化：原始 `Ã, B̃, C̃` 由静态可学偏置加上输入相关项 `α·RMSNorm(vec(X_l))·W` 组成，使残差混合可以随 token 自适应。DeepSeek-V4 在 1F1B 重叠流水线上 mHC 的实际墙钟开销被压在 ~6.7%，得益于融合 kernel 与"大量重算 + 极少存储"的检查点策略。

## 参考资料

- mHC 论文 (Xie et al., 2026) — DeepSeek-V4 第 2.2 节引用为标准参考。
- Hyper-Connections (Zhu et al., 2025) — 底层 HC 残差扩展思想。
- DeepSeek-V4 技术报告第 2.2 节 + 3.4.2 节（实现细节）。

## 使用此技术的模型

| 模型                          | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro               | n_hc=4（config.hc_mult），Sinkhorn t_max=20（config.hc_sinkhorn_iters），收敛容差 hc_eps=1e-6。静态 + 动态参数化。mHC 的静态偏置与 gating 因子用 AdamW 优化（其余主体用 Muon）。                                                                                                                                                                                            |
| DeepSeek-V4-Flash             | mHC 配置与 V4-Pro 完全相同：n_hc=4，t_max=20，hc_eps=1e-6，启用动态参数化。是 V4 系列里唯一在 Flash 与 Pro 之间没有规模差异的组件。                                                                                                                                                                                                                                         |
| DeepSeek-V4-Flash-0731        | backbone 的 mHC 配置与预览版相同（`hc_mult=4`、`hc_sinkhorn_iters=20`、`hc_eps=1e-6`）。新增的关联点：附带的 **DSpark 草稿 backbone 同样使用 mHC**（DSpark 论文 §5.1 —— 「三层 MoE，带 mHC 与窗口 128 的滑窗注意力」），因此目标模型与草稿共享残差拓扑。见[投机解码](./speculative-decoding.zh.md)。                                                                        |
| Qwen3.8-Flash-Next（经由 GR） | 同一家族、不同的容量分配——见 [门控残差](./gated-residual.zh.md)。Qwen 保留 4 分支加宽残差流，但把*读*做成逐元素、数据相关的，同时**整个删掉 `H_res`**，依据是消融发现：一旦读和写足够有表达力，混合算子「不带来显著改进」。这也顺带去掉了 mHC 的双随机约束机制。25B-A3B 规模下两者 loss/benchmark 相当（mHC 动态 1.594 / 54.47 vs GR 1.590 / 54.66），GR 赢在效率与稳定性。 |

## 相关技术

- [DualPipe](./dualpipe.zh.md) — V4 的 mHC 实现调整了 DualPipe 1F1B 重叠以吸收额外的流水线通讯量。
