项目文档：大模型技术演进与架构解析矩阵 (LLM Tech Evolution Matrix)
一、 项目愿景 (Project Vision)
建立一个结构化、可更新的知识库，系统性地追踪和拆解主流 AI 模型（Text, Multimodal, Diffusion）的核心技术栈。通过标准化数据收集，最终实现技术的横向对比（各家方案差异）与纵向分析（单一技术的生命周期与趋势，如优化器演进、注意力机制变迁）。

二、 阶段规划 (Milestones)
Milestone 1 (M1): 主流文本与多模态大模型 (Focus)

目标模型库: Qwen 系列, Llama 系列, DeepSeek 系列, GLM, GPT-4 系列, Kimi, MiniMax 等。

重点: 开源模型深度解析（基于 HuggingFace Config & 技术报告），闭源模型关键技术推演。

Milestone 2 (M2): 扩散模型与图像/视频生成 (Future)

目标模型库: Stable Diffusion 系列, Midjourney (推测), Flux, Sora (推测), Veo 等。

三、 核心数据模型定义 (Core Data Schema)
这是指导 AI 从海量 Paper 和 Config 中提取信息的标准 JSON/结构化模板。

1. 模型元数据 (Model Metadata)

发布时间与家族: (如: 2024-12, DeepSeek-V3)

开源状态: (Open Weights, Open Source, Closed)

参数量级: (Total Params, Active Params 激活参数)

2. 核心架构设计 (Architecture & Components)

骨干网络 (Backbone): 层数 (Layers), 隐藏层维度 (Hidden Dim), 序列长度 (Context Window).

注意力机制 (Attention): 具体的 Attention 变体 (如 MHA, GQA, MLA), 旋转位置编码 (RoPE) 细节.

前馈网络 (FFN) / 专家系统 (MoE):

如果是 MoE: 专家总数, 激活专家数, 路由算法 (Routing Algorithm, 如 DeepSeek 的无辅助损失负载均衡), 共享专家设计.

底层组件: 激活函数 (如 SwiGLU, GeLU), 归一化策略 (如 RMSNorm), 特殊的 Embedding 技术.

分布式/并行友好度 (Infra Considerations): 架构上是否有针对序列并行 (SP)、专家并行 (EP) 等特殊设计的解耦或优化 (如 DeepLink)。

3. 训练与优化策略 (Training & Optimization)

优化器 (Optimizer): 算法选择 (AdamW, Muon 等), 学习率调度策略 (LR Schedule).

训练数据 (Data): Token 总量级 (如 15T tokens), 数据配比 (Code/Math/Text 比例，如果公开).

对齐与强化学习 (Alignment & Post-training): SFT 策略, 强化学习算法 (RLHF, PPO, DPO, GRPO), 是否使用了 RLAIF.

特殊技术 (Advanced Tech): 自蒸馏 (Self-Distillation), 混合精度训练策略 (FP8/BF16 混合).

4. 多模态扩展 (Multimodal Specifics - 仅限多模态模型)

视觉/音频编码器 (Encoders): 选用的 Vision Transformer 或 Audio 架构.

模态融合机制 (Fusion): 投影层设计 (MLP, Cross-Attention), 原生多模态 vs 拼接多模态.

四、 AI 执行流 (Agentic Workflow)
为了让 AI 自动化执行，项目将分为以下几个 Pipeline：

数据获取层 (Data Sourcing):

调用脚本拉取 HuggingFace 上的 config.json。

提供目标模型的 ArXiv 论文或官方 Tech Blog URL 给 AI。

信息抽取层 (Information Extraction):

AI 任务: 严格按照上述【核心数据 Schema】从长文本中提取结构化字段。

Prompt 策略: 设定 AI 为 "Senior AI Researcher"，要求对于找不到的信息标注为 [Unknown/Not Disclosed]，切忌幻觉。

汇总与对比层 (Synthesis & Analytics):

AI 任务: 将提取的所有 JSON 数据合并入图表或数据库。根据需求生成《XX技术演进趋势报告》（例如：分析从 Adam 到 Muon 的底层逻辑转变）。