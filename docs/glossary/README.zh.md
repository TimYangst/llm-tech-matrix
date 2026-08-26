# 术语表（Glossary）

> English: [README.md](./README.md)

跨多个 extracted 模型出现的技术的简短参考条目。每个条目说明这项技术是什么、源自何处、本仓库中哪些模型用到它。

目标 **不是** 替代原论文——每条 1-2 段为限。目标是让 `data/extracted/<slug>.md`（及其中文版 `<slug>.zh.md`）在不熟悉每个缩写的前提下也读得懂，同时把跨模型的采用情况集中起来，支持后续综合分析（例如"哪些模型采用 auxiliary-loss-free routing？"）。

## 添加新条目

1. 复制 [`_template.md`](./_template.md)（英文）或 [`_template.zh.md`](./_template.zh.md)（中文）为 `<slug>.md` / `<slug>.zh.md`（kebab-case）。每个新条目都应该同时有英文版和中文版。
2. 填写内容。保持简短——能链到原论文就别复述论文。
3. 在下方相关分类的索引里加一行。
4. 抽取一个新模型且它使用了这项技术时，给该条目的 "Used by" / "使用此技术的模型" 表格加一行。

"Used by" 表目前手工维护。未来一个综合分析工具可以扫 `data/extracted/*.json` 中提到的技术，自动建议补充。

## 索引

### 注意力（Attention）

- [Multi-head Latent Attention (MLA)](./mla.zh.md)
- [Grouped Query Attention (GQA)](./gqa.zh.md)
- [QK-Norm](./qk-norm.zh.md)
- [Gated DeltaNet](./gated-deltanet.zh.md)
- [DeepSeek Sparse Attention (DSA)](./dsa.zh.md)
- [Compressed Sparse Attention + Heavily Compressed Attention (CSA + HCA)](./csa-hca.zh.md)
- [Kimi Delta Attention (KDA)](./kda.zh.md)
- [Qwen 稀疏注意力（QSA）](./qsa.zh.md)

### FFN / MoE

- [DeepSeekMoE（细粒度 + 共享专家）](./deepseekmoe.zh.md)
- [Auxiliary-loss-free routing](./aux-loss-free-routing.zh.md)
- [Global-batch load balancing](./global-batch-load-balancing.zh.md)
- [Stable LatentMoE（LatentMoE + SiTU-GLU + Quantile Balancing）](./latentmoe.zh.md)
- [N-gram 嵌入（卸载到主机内存的容量扩展）](./ngram-embedding.zh.md)

### 训练目标（Training objectives）

- [Multi-Token Prediction (MTP)](./mtp.zh.md)
- [Fill-in-Middle (FIM)](./fim.zh.md)

### 对齐 / RL

- [Group Relative Policy Optimization (GRPO)](./grpo.zh.md)
- [Hybrid Thinking（chat-template 思考模式融合）](./hybrid-thinking.zh.md)
- [On-Policy Distillation（多教师 OPD）](./on-policy-distillation.zh.md)
- [Agent Swarm — 并行智能体 RL（PARL）](./agent-swarm.zh.md)
- [推理强度控制（Reasoning-effort control）](./reasoning-effort.zh.md)

### 位置编码 / 长上下文

- [YaRN RoPE scaling](./yarn-rope.zh.md)
- [Dual Chunk Attention (DCA)](./dual-chunk-attention.zh.md)
- [Multimodal RoPE (mRoPE)](./mrope.zh.md)

### 量化 / 混合精度

- [FP8 mixed precision（DeepSeek-V3 变体）](./fp8-mixed-precision.zh.md)
- [FP4 量化感知训练 (MXFP4)](./fp4-qat.zh.md)
- [Native INT4 量化感知训练（QAT）](./int4-qat.zh.md)

### 视觉编码器（Vision encoders）

- [MoonViT — 原生分辨率 + 3D 时序视觉编码器](./moonvit.zh.md)

### 分布式训练

- [DualPipe pipeline scheduling](./dualpipe.zh.md)
- [投机解码模块（MTP-1 → EAGLE-3 / DSpark）](./speculative-decoding.zh.md)

### 优化器

- [Muon（按矩阵 Newton-Schulz 正交化）](./muon.zh.md)

### 残差连接

- [Manifold-Constrained Hyper-Connections (mHC)](./mhc.zh.md)
- [Attention Residuals (AttnRes)](./attnres.zh.md)
- [门控残差（Gated Residual, GR）](./gated-residual.zh.md)
