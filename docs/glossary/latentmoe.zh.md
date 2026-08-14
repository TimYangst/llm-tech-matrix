# Stable LatentMoE（LatentMoE + SiTU-GLU + Quantile Balancing）

> English: [latentmoe.md](./latentmoe.md)

**Slug:** `latentmoe`
**类别：** ffn / moe
**一句话概括：** 让**路由专家**在比模型隐藏维更窄的潜空间里运算，使专家数量与路由多重度可以扩大而 dispatch 通信量不随之增长 —— 外加让它在极端稀疏度下仍可训练的三个稳定器（上投影前的 RMSNorm、SiTU-GLU、Quantile Balancing）。
**首次提出：** LatentMoE（Gao et al., 2026），见 [Kimi K3 技术报告 §2.3](https://arxiv.org/abs/2607.24653) 参考文献 [32]；"Stable" 变体在该报告中提出并扩展到 896 个专家。

## 概述

在常规 MoE 中，每个被选中的专家都要接收完整的 `d` 维 token 表示，于是通信量与专家权重访存随路由多重度 `k` 增长，
这就限制了专家池和激活数各自能推到多大。LatentMoE 通过把**模型宽度**与**路由专家宽度**解耦来打破这一耦合：
共享专家保留全宽通路承担通用变换，而路由专家在宽度为 `ℓ` 的紧凑潜空间中运算。

```
u = Σ_{i ∈ Top-k(x)} p_i · E_routed_i(W_down · x)        # 路由分支，宽度 ℓ
y = Σ_j E_shared_j(x) + W_up · RMSNorm(u)                # 共享分支保持宽度 d
```

Kimi K3 取 `ℓ = 3584 = 0.5 × d`，做到 **896 个路由专家、每 token 激活 16 个**，稀疏度 56 ——
专家池约为 Kimi K2 的 2.3 倍、激活数为 2 倍，且单专家 FFN 宽度同时增大（2048 → 3072）。

如此稀疏度会放大两种失效模式，"Stable" 正是对应的三项修补：

1. **上投影前加 RMSNorm**（Normalized LatentMoE，`latent_moe_use_norm=true`）。
   聚合后的路由表示 `u` 的尺度会随命中哪些专家及其路由权重而波动；在 `W_up` 之前归一化，
   可让路由分支在与全宽共享分支合流前对这种尺度波动脱敏。除稳定性外，它还稳定地改善了验证 loss 与下游指标。
2. **SiTU-GLU**（Sigmoid Tanh Unit GLU）取代 SwiGLU。路由通路把 `W_down`、门控多分支专家 FFN 与 `W_up`
   串成近四次连续矩阵乘；这种病态结构在 2.8T 规模下会让内部激活爆炸，而 SwiGLU 的两个乘性因子都无界。
   SiTU-GLU 对 Swish 门的线性因子**以及**上分支各自施加平滑截断 `softcap(x, β) = β·tanh(x/β)`：
   `SiTU-GLU(x) = [β₁·tanh(W_g x / β₁) ⊙ σ(W_g x)] ⊙ [β₂·tanh(W_u x / β₂)]`。
   K3 取 β₁ = 4（门）、β₂ = 25（上分支），输出上界为 β₁β₂ = 100。原点附近它贴合 SwiGLU；
   幅值大时则饱和，而不是在低精度下发散。
3. **Quantile Balancing（QB）**，替换 aux-loss-free 路由中的定步长 bias 更新。基础方案见
   [auxiliary-loss-free routing](./aux-loss-free-routing.zh.md)。原始更新 `b ← b + γ·sign(mean_load − load)`
   要在"适应太慢"与"负载振荡"之间权衡，而在每层约 10³ 个专家的规模下两端都不好用。
   QB 改为直接从**与目标负载 `q = mk/n` 匹配的 router 分数分位数**推出每个专家的 bias：
   路由改用带 bias 分数上的 Top-(k+1)，第 (k+1) 项顺带给出每个 token 的门限 `α_i`，
   新 bias 即 `−quantile_{1−k/n}(s_{:,j} − α)` 再做均值中心化。由于该分位数跨越一个数百万 margin、
   分散在各 rank 上的全局 batch，实际用逐专家**直方图**估计，只需一次对 bin 计数的 all-reduce ——
   计数可加，因此估计在 bin 宽度内等价于全 batch 精确值，每个专家仅需几百个 bin。
   bias 只调节 dispatch（不进入混合权重 `p_i,j`，故不影响 router 梯度），下一步才生效，推理时冻结。

## 参考资料

- Kimi K3 技术报告 §2.3（Stable LatentMoE、SiTU-GLU §2.3.2、Quantile Balancing §2.3.3，附录 B–D）：<https://arxiv.org/abs/2607.24653>
- 基础 MoE 组织形式：[DeepSeekMoE](./deepseekmoe.zh.md) —— 共享 + 细粒度路由专家
- 基础均衡方案：[auxiliary-loss-free routing](./aux-loss-free-routing.zh.md)

## 使用此技术的模型

| 模型    | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K3 | 896 个路由专家、激活 16 个（稀疏度 56），每层固定 2 个全宽共享专家。路由潜空间宽度 3584（`config.routed_expert_hidden_size`，= 0.5 × 隐藏维 7168）；单专家 FFN 宽度 3072（`moe_intermediate_size`）。Sigmoid router、`topk_method='noaux_tc'`、`moe_renormalize=true`、`routed_scaling_factor=1.0`，无分组 / node-limited 路由。三个稳定器全部启用：`latent_moe_use_norm=true`、`hidden_act='situ'` 且 β₁=4 / β₂=25（`activation_situ_beta` / `activation_situ_linear_beta`）、以及 QB 做均衡。只有路由专家被 MXFP4 量化 —— 潜空间投影、共享专家与 router 都保持较高精度。 |

## 相关技术

- [DeepSeekMoE（细粒度 + 共享专家）](./deepseekmoe.zh.md) —— LatentMoE 所基于的共享/路由组织形式，差别在于路由专家不再读写全模型宽度。
- [Auxiliary-loss-free routing](./aux-loss-free-routing.zh.md) —— QB 只替换其 bias 更新规则，而非整个方案。
- [FP4 QAT (MXFP4)](./fp4-qat.zh.md) —— 窄潜空间与 4-bit 专家权重是对同一项成本（专家显存与 dispatch 通信）的互补攻击。
- [Attention Residuals (AttnRes)](./attnres.zh.md) 与 [KDA](./kda.zh.md) —— 同一"三轴扩展"论证中的深度轴与序列轴。
