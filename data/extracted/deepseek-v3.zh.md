# DeepSeek-V3

> English: [deepseek-v3.md](./deepseek-v3.md)

*Schema 版本: 5*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | DeepSeek |
| 发布时间 | 2024-12 |
| 开放程度 | 开放权重 |
| 总参数量 | 671B |
| 激活参数量 | 37B |

## 数据源

- <https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/config.json>
- <https://arxiv.org/pdf/2412.19437>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 61 |
| 隐藏维度 | 7168 |
| 上下文窗口 | 131072 |

**上下文说明：** Paper validates 128K via the Needle-In-A-Haystack test. config.json sets max_position_embeddings=163840 (= YaRN scaling factor 40 x original 4096). 131072 is recorded as the canonical user-facing 128K spec.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | [Unknown/Not Disclosed] |
| 扩展最大长度 | 131072 |
| 倍率 | 40.0 |
| RoPE 原始最大长度 | 4096 |

_说明：_ Pre-train sequence length is 4K per paper; long-context extension uses YaRN. config.json reports max_position_embeddings=163840 (= 4096 x 40); 131072 is the canonical productized 128K spec.

### 注意力（MLA）

| | |
|---|---|
| 变体 | MLA |
| 头数 | 128 |
| KV 头数 | [Unknown/Not Disclosed] |
| 头维度 | [Unknown/Not Disclosed] |

**RoPE：** type=`yarn`, base=`10000`

RoPE scaling：

```json
{
  "factor": 40,
  "beta_fast": 32,
  "beta_slow": 1,
  "mscale": 1.0,
  "mscale_all_dim": 1.0,
  "original_max_position_embeddings": 4096
}
```

**MLA 特有字段：**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 1536 |
| qk_nope_head_dim | 128 |
| qk_rope_head_dim | 64 |
| v_head_dim | 128 |

### FFN（hybrid）

**Dense 中间维度：** `18432`

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free (DeepSeek-V3 / noaux_tc): sigmoid affinity scores per expert, plus a learnable per-expert bias that is dynamically adjusted based on per-step expert load (bias update speed gamma=0.001 for first 14.3T tokens, 0.0 for last 500B). Top-K selection uses (affinity + bias); gating value uses raw affinity. 8 expert groups; each token routed to top-4 groups, then to at most M=4 nodes (node-limited routing). Complementary sequence-wise balance loss with alpha=0.0001. No token dropping in train or inference.

**层划分：** First 3 of 61 layers are dense (intermediate_size=18432); remaining 58 layers are MoE (per-expert intermediate_size=2048).

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in the FFN) |
| 归一化 | RMSNorm (rms_norm_eps=1e-6); additional RMSNorm after MLA compressed latent vectors |

**Embedding 说明：** tie_word_embeddings=false (separate output head). Byte-level BPE tokenizer with 128K vocabulary (vocab_size=129280); pretokenizer optimized for multilingual compression and includes combined punctuation+linebreak tokens with random splitting during training to mitigate boundary bias.

### 并行 / 基础设施

16-way Pipeline Parallelism with custom DualPipe scheduling (bidirectional micro-batches, fewer bubbles than 1F1B/ZB1P, full overlap of all-to-all and PP communication). 64-way Expert Parallelism across 8 nodes. ZeRO-1 Data Parallelism. NO Tensor Parallelism. Trained on 2048 H800 GPUs via custom HAI-LLM framework. Cross-node all-to-all uses 20 SMs partitioned into 10 channels with warp-specialized PTX kernels; IB+NVLink fully overlapped. Recompute RMSNorm + MLA up-projections on backward; EMA params kept in CPU.

## 训练

| | |
|---|---|
| 优化器 | AdamW (beta1=0.9, beta2=0.95, weight_decay=0.1); gradient clipping norm 1.0 |
| 训练总 token 数 | 14.8T |

**学习率调度：** Linear warmup 0 -> 2.2e-4 over first 2K steps. Constant 2.2e-4 until 10T tokens consumed. Cosine decay 2.2e-4 -> 2.2e-5 over the next 4.3T tokens. For the final 500B tokens: constant 2.2e-5 for 333B tokens, then constant 7.3e-6 for the remaining 167B tokens. Pre-train sequence length 4K. Batch size schedule: linearly grown from 3072 to 15360 over first 469B tokens, then constant 15360.

**数据配比说明：** Math/code ratio enhanced relative to DeepSeek-V2; multilingual coverage expanded beyond English and Chinese; data processing pipeline refined to minimize redundancy while maintaining diversity; document packing without cross-sample attention masking. No concrete percentage breakdown disclosed.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | 1 |
| 损失权重调度 | lambda=0.3 for first 10T tokens, 0.1 for remaining 4.8T tokens |

_共享模块：_ Embedding layer and output head are shared with the main model. Under DualPipe scheduling, the shallowest layers (with embedding) and deepest layers (with output head) are co-located on the same PP rank to enable physical parameter and gradient sharing between MTP modules and the main model. MTP modules can be discarded for standard inference, or repurposed for speculative decoding.

**Fill-in-Middle (FIM)：**

| | |
|---|---|
| 格式 | PSM (Prefix-Suffix-Middle): <|fim_begin|>f_pre<|fim_hole|>f_suf<|fim_end|>f_middle<|eos_token|>, applied at document level during pre-packing |
| 比例 | 0.1 |

### 对齐

**SFT：** 1.5M instances across multiple domains. Reasoning data (math, code competition, logic puzzles) is generated by an internal DeepSeek-R1 model; for each problem two SFT samples are produced - <problem, original_response> and <system_prompt, problem, R1_response> - then per-domain expert models trained via SFT+RL serve as data generators with rejection sampling. Non-reasoning data (creative writing, role-play, simple QA) is generated by DeepSeek-V2.5 and verified by human annotators. SFT trains for 2 epochs with cosine LR decay 5e-6 -> 1e-6, sequences packed from multiple samples with sample masking to keep them mutually invisible.

**RL 方法：** GRPO (Group Relative Policy Optimization) - foregoes a separate critic model and estimates the baseline from group-sampled outputs. Reward signal combines a rule-based RM (deterministic checks for math final answers, compiler tests for code/LeetCode) and a model-based RM (trained from DeepSeek-V3 SFT checkpoints on human preference data, predicts a chain-of-thought leading to the final reward to mitigate reward hacking).

**RLAIF：** `False`

### 进阶

**自蒸馏：** Yes - reasoning capability is distilled from the DeepSeek-R1 series (long-CoT model) into DeepSeek-V3 via the SFT data-generation pipeline described above; verification and reflection patterns from R1 are incorporated while output style and length are kept under control.

**混合精度：** FP8 (E4M3 format on all tensors - both Fprop and Dgrad/Wgrad - departing from prior E4M3+E5M2 hybrids) for compute-density GEMMs. Fine-grained quantization: 1x128 tile-wise scaling for activations, 128x128 block-wise scaling for weights. Increased accumulation precision via promotion to CUDA cores (FP32 register accumulation every Nc=128 elements). Online quantization (no delayed/historical max). High precision (BF16/FP32) retained for: embedding, output head, MoE gating, normalization, attention. AdamW first/second moments stored in BF16; master weights and gradients in FP32. Activations cached in FP8 for backward.

---

_由 `data/extracted/deepseek-v3.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
