# Kimi K2.5

> English: [kimi-k2.5.md](./kimi-k2.5.md)

*Schema 版本: 6*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Kimi K2 |
| 发布时间 | 2026-01 |
| 开放程度 | 开放权重 |
| 总参数量 | 1.04T |
| 激活参数量 | 32B |

**变体策略（variant policy）：** Within the K2 generation Moonshot ships sibling-per-mode text-only checkpoints (K2-Base, K2-Instruct, K2-Instruct-0905, K2-Thinking). The K2.5 generation collapses that sibling layout into a single unified-weights multimodal checkpoint with two runtime modes (Instant vs Thinking) selected via the chat-template `thinking` kwarg, plus a third K2.6-only `preserve_thinking` kwarg. K2.5 is built by continual pretraining on top of K2-Base; no separate Math / Coder / VL checkpoints exist for the K2.5/K2.6 generations.

## 数据源

- <https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/config.json>
- <https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/tokenizer_config.json>
- <https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/preprocessor_config.json>
- <https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/chat_template.jinja>
- <https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/README.md>
- <https://arxiv.org/pdf/2602.02276>
- <https://www.kimi.com/blog/kimi-k2-5.html>
- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/docs/tool_call_guidance.md>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 61 |
| 隐藏维度 | 7168 |
| 上下文窗口 | 262144 |

**上下文说明：** README reports 256K. config.json max_position_embeddings=262144 (= 64 x YaRN original_max 4096). Long-context curriculum: 32K then 256K via YaRN during the mid-training stage (500B tokens at 32K then 200B tokens at 256K, per paper Table 3).

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 262144 |
| 倍率 | 64.0 |
| RoPE 原始最大长度 | 4096 |

_说明：_ Joint pre-training runs at 4K sequence length over ~15T mixed vision-text tokens; mid-training is the third K2.5 pre-training stage (paper §4.3) and sequentially extends sequence length 32768 → 262144 via YaRN interpolation (500B tokens at 32K then 200B tokens at 256K, paper Table 3). The model has therefore seen sequences up to 262144 during pre-training (`trained_max=262144`); YaRN is baked into config.json (`original_max_position_embeddings=4096`, `factor=64`) so the same RoPE anchoring is reused at deployment without further extension. This is the V4-style 'trained out to the productized length' pattern, not V3's 'short pre-train + deployment-time stretch'.

### 注意力（MLA）

| | |
|---|---|
| 变体 | MLA |
| 头数 | 64 |
| KV 头数 | [Unknown/Not Disclosed] |
| 头维度 | [Unknown/Not Disclosed] |

**RoPE：** type=`yarn`, base=`50000`

RoPE scaling：

```json
{
  "factor": 64.0,
  "beta_fast": 32.0,
  "beta_slow": 1.0,
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
| 可路由专家数 | 384 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free routing (config.topk_method='noaux_tc') with sigmoid affinity scoring (scoring_func='sigmoid') and routed_scaling_factor=2.827. norm_topk_prob=true. n_group=1 (no node-limited / grouped routing — distinct from DeepSeek-V3's 8-group + node-limited variant). seq_aux=true with aux_loss_alpha=0.001 retained as a complementary signal. Sparsity 48 (384 routed / 8 active per token).

**层划分：** First 1 of 61 layers is dense (intermediate_size=18432); remaining 60 layers are MoE (per-expert intermediate_size=2048). config.first_k_dense_replace=1, moe_layer_freq=1.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config.hidden_act='silu' — gated SiLU is the SwiGLU form used in the FFN). |
| 归一化 | RMSNorm (rms_norm_eps=1e-5). |

**Embedding 说明：** tie_word_embeddings=false (separate output head). Vocabulary 163840 (README: '160K'); TikTokenTokenizer (auto_map: tokenization_kimi.TikTokenTokenizer). Reserved special tokens include [BOS]=163584, [EOS]=163585, <|im_user|>/<|im_assistant|>/<|im_system|>/<|im_middle|>/<|im_end|> for chat roles, <|tool_calls_section_begin|>...<|tool_call_argument_begin|>...<|tool_call_end|>/<|tool_calls_section_end|> for tool calls, <|media_begin|>/<|media_content|>/<|media_pad|>/<|media_end|> for vision tokens, <think>/</think> (163606/163607) for thinking blocks.

### 并行 / 基础设施

K2.5 inherits the K2 training infrastructure with one multimodal addition: Decoupled Encoder Process (DEP) — the vision encoder is replicated on all GPUs (since it is small), all visual data in the global batch is forward-passed there (load-balanced by patch counts) and only the final activations are gathered back to PP Stage-0; backward recomputes the vision forward pass to produce gradients. This decouples the vision-encoder pipeline from the main backbone pipeline, lets text-only parallel strategies be reused unchanged, and yields ~90% multimodal-vs-text-only training efficiency. K2 backbone parallel strategy details (PP/EP/TP layout, scheduler, framework) are not restated in the K2.5 report and the underlying K2 tech report has not been published.

## 训练

| | |
|---|---|
| 优化器 | MuonClip — Muon optimizer with QK-Clip for stability (per paper §4.1: 'Kimi K2 employs the token-efficient MuonClip optimizer with QK-Clip for training stability'). The same MuonClip optimizer is used during the joint pre-training and the RL post-training stage (paper §4.4.2: 'We employ the MuonClip optimizer to minimize this objective'). |
| 训练总 token 数 | ~30T cumulative (15T K2-base text-only + 15T K2.5 joint mixed vision-text) + ~700B mid-training (500B at 32K then 200B at 256K) |

**学习率调度：** [Unknown/Not Disclosed] — the K2.5 report defers the K2-base lr schedule to the unpublished K2 tech report and does not restate it. Joint pre-training and mid-training schedules are not disclosed numerically.

**数据配比说明：** K2 base was trained on '15 trillion high-quality text tokens' (paper §4.1, exact distribution not disclosed in the K2.5 report). K2.5 joint pre-training adds ~15T mixed vision+text tokens at a constant text:vision ratio across the entire run (paper §2.1 finds early fusion with low vision ratio outperforms late high-ratio fusion). Joint data extends K2's distribution by introducing unique tokens, increasing weight on coding-related content, and capping max-epochs per source. Mid-training data includes long text, long video, reasoning data, and Long-CoT (paper Table 3). ViT-stage data: alt text, synthetic captions for images and videos, grounding bboxes, OCR.

### 对齐

**SFT：** Zero-vision SFT (paper §1, §2.2): text-only SFT alone is sufficient to activate visual reasoning and tool use, because the joint pre-training already establishes strong vision-text alignment. Adding human-designed visual SFT trajectories was found to hurt generalization. SFT data is synthesized by running K2, K2-Thinking, and an internal suite of proprietary expert models, with domain-specialized pipelines combining human annotation, prompt engineering, and multi-stage verification (paper §4.4.1). Output emphasizes interactive reasoning and precise tool calling.

**RL 方法：** Token-level clip RL with MuonClip optimizer (paper §4.4.2 eq. 1). Departs from K1.5 by introducing a token-level log-ratio gradient-mask: tokens whose log-ratio policy/old falls outside [α, β] have their gradients zeroed, regardless of advantage sign — a stricter off-policy bound than PPO clipping. KL-style regulariser τ on log-ratio retained. Joint text+vision RL is run on the same backbone, plus Parallel-Agent RL (PARL) for Agent Swarm: orchestrator updated, sub-agents frozen, sub-agent trajectories excluded from the loss to avoid credit-assignment ambiguity.

**RLAIF：** `[Unknown/Not Disclosed]`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | ViT Training | `continual_pretraining` | MoonViT-3D continually pre-trained from SigLIP-SO-400M on image-text and video-text pairs with cross-entropy caption loss only (no contrastive loss, unlike Kimi-VL). Two-stage alignment: stage-1 updates MoonViT-3D against Moonlight-16B-A3B via caption loss (~1T tokens, very low FLOPs); short stage-2 updates only the MLP projector to bridge to the 1T LLM. Sequence length 4096. |
| 2 | Joint Pre-training | `continual_pretraining` | Joint multimodal continual pre-training from a near-end Kimi K2 checkpoint over ~15T vision+text tokens at 4K sequence length. Updates both ViT and LLM. Constant low-ratio text:vision mix across the whole run (early fusion finding from paper §2.1). |
| 3 | Joint Long-context Mid-training | `continual_pretraining` | High-quality text + multimodal data, long text, long video, reasoning, Long-CoT. Sequentially extends sequence length 32768 → 262144 via YaRN interpolation. ~500B tokens at 32K then ~200B tokens at 256K (paper Table 3). |
| 4 | Zero-vision SFT | `sft` | Text-only SFT — activates visual reasoning + tool use without paired visual SFT examples (paper §1). |
| 5 | Joint Text+Vision RL | `rl` | Token-level clip RL on text and vision tasks jointly. Rewards: rule-based outcome reward + budget-control (token-efficiency) reward. Generative Reward Models (GRMs) for general / open-ended tasks aligned to Kimi's value criteria (helpfulness, response readiness, contextual relevance, level of detail, aesthetic quality, instruction following); multiple alternative GRM rubrics rotated per task to mitigate reward hacking. Vision-task-specific rewards: F1 with soft IoU matching (grounding), Gaussian-weighted distance F1 (point localization), rasterized-mask IoU (segmentation), normalized edit distance (OCR), absolute-difference (counting). LLM verifier (Kimi K2 itself) for synthetic visual puzzles. 'Toggle' training heuristic alternates between budget-limited and standard-scaling phases every m iterations to prevent length-overfitting while still trimming output length 25–30% with negligible quality impact. |
| 6 | Parallel-Agent RL (PARL) for Agent Swarm | `rl` | Adds sub-agent creation + task-delegation interfaces to the orchestrator; trains only the orchestrator with the same token-level clip RL. Sub-agents frozen; their trajectories excluded from the loss to avoid credit-assignment ambiguity and training instability. Yields BrowseComp 60.6 → 78.4 and WideSearch item-F1 72.7 → 79.0 with up to 4.5× latency reduction vs single-agent. |
| 7 | Native INT4 Quantization-Aware Training | `qat` | Same QAT recipe as Kimi K2-Thinking applied during post-training. INT4 weight-only quantization on MoE expert weights (group_size=32, num_bits=4, type=int, format=pack-quantized). config.quantization_config.ignore excludes self_attn, shared_experts, mlp gate/up/down projections, lm_head, and the vision tower / mm_projector — only routed-expert weights are INT4. Yields roughly 2× generation speedup at lossless quality. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking` | Default mode; chat-template kwarg `thinking=true` (or omitted). Official API: `extra_body={'thinking': {'type': 'enabled'}}`. The chat template emits an open `<think>` tag before the assistant turn so the model produces a reasoning block before its final answer. | Reasoning mode — the model produces a `<think>`...`</think>` block whose content is exposed as `reasoning_content` on the OpenAI-compatible API. README §6 sets recommended sampling at temperature 1.0, top_p 0.95. |
| `instant` | Chat-template kwarg `thinking=false`. vLLM/SGLang: `extra_body={'chat_template_kwargs': {'thinking': false}}`. Official API: `extra_body={'thinking': {'type': 'disabled'}}`. The chat template emits an empty `<think></think>` pair so the model skips the reasoning block. | Non-reasoning mode — answers directly without an interleaved chain-of-thought. README §6 sets recommended sampling at temperature 0.6, top_p 0.95. |

- **`thinking`**
    - Kwargs：`thinking=true`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`
- **`instant`**
    - Kwargs：`thinking=false`
    - 推荐采样参数：`temperature=0.6`, `top_p=0.95`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `function-call-token` |
| 起始 token | `<|tool_call_begin|>` |
| 结束 token | `<|tool_call_end|>` |
| 参数编码方式 | Each call is `<|tool_call_begin|>{tool_call_id}<|tool_call_argument_begin|>{json_arguments}<|tool_call_end|>` where `tool_call_id` has the form `functions.{name}:{idx}` (idx is a global per-conversation counter starting at 0) and `{json_arguments}` is the JSON-encoded arguments object (compact separators ',' and ':' when produced via `tojson`). Multiple tool calls in one turn are wrapped together by `<|tool_calls_section_begin|>` ... `<|tool_calls_section_end|>`. Tool results are returned in subsequent `tool` messages prefixed by `## Return of {tool_call_id}` (see chat_template.jinja). |

_说明：_ K2.5 inherits its tool-call wire format from Kimi K2 (README §6: 'Interleaved Thinking and Multi-Step Tool Call — K2.5 shares the same design as K2 Thinking'). Wire format documented in Kimi-K2-Thinking/docs/tool_call_guidance.md, which is canonical for the family. No published vLLM/SGLang/KTransformers `--tool-call-parser` flag — K2 family relies on the inference engine's built-in support for K2's tool-parsing logic (vLLM/SGLang need recent versions for correct tool-call ID handling per the official FAQ).

### 进阶

**自蒸馏：** Yes — K2.5's SFT data is synthesized by K2 + K2-Thinking + a suite of in-house expert models (paper §4.4.1). The Toggle algorithm in §4.4.2 is also evaluated using K2-Thinking as the trained model.

**混合精度：** BF16 master parameters (config.dtype='bfloat16'); MoE expert weights deployed at INT4 via Quantization-Aware Training (compressed-tensors format, group_size=32, num_bits=4, type=int, symmetric, group strategy, observer=minmax) — applied to routed-expert linears only. self_attn, shared_experts, mlp gate/up/down projections, lm_head, vision_tower, and mm_projector remain at high precision (excluded via config.quantization_config.ignore patterns). The K2-base pre-training mixed precision is not restated in the K2.5 report and the K2 tech report has not been published.

**稳定性 trick：** QK-Clip — applied throughout MuonClip pre-training and post-training, prevents the attention-logit explosion historically observed with Muon on large transformers. Token-level log-ratio gradient masking (paper §4.4.2 eq. 1) is described explicitly as a stability mechanism for long-horizon multi-step tool-use RL: tokens whose policy-vs-old log-ratio falls outside [α, β] have their gradients zeroed, bounding off-policy drift regardless of advantage sign.

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `projection_mlp` |

**融合方式说明：** Architecturally projection-MLP (vision encoder → MLP projector with patchmerger → LM hidden stream) but trained jointly with text from the K2 base checkpoint (~15T mixed vision-text tokens at constant low vision ratio). Vision content is wrapped in `<|media_begin|>` ... `<|media_pad|>` ... `<|media_end|>` tokens in the chat template; the `<|media_pad|>` placeholder is replaced by the projected vision-encoder activations at inference. Video uses a separate `<|kimi_k25_video_placeholder|>` token. Paper §2.1: 'early vision fusion with lower ratios tends to yield better results given the fixed total vision-text tokens'.

### 视觉编码器

| | |
|---|---|
| 架构 | MoonViT-3D — native-resolution ViT initialised from SigLIP-SO-400M (~400M params per README) with NaViT patch-packing for variable-resolution training, extended to 3D by treating up to 4 consecutive video frames as a spatiotemporal volume packed into a single 1D sequence (shared weights for image and video; lightweight temporal pooling at the projector gives 4× temporal compression). |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 14 |
| 输入通道数 | [Unknown/Not Disclosed] |
| 输出维度 → LM | 7168 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 4 |

_说明：_ config.vision_config: mm_projector_type='patchmerger', merge_kernel_size=[2,2], merge_type='sd2_tpool', text_hidden_size=7168 (LM hidden), pos_emb_type='divided_fixed', init_pos_emb_height=64, init_pos_emb_width=64, init_pos_emb_time=4, video_attn_type='spatial_temporal'. Preprocessor (MoonViTMediaProcessorConfig): patch_size=14, image_mean/std=[0.5,0.5,0.5], merge_kernel_size=2, temporal_merge_kernel_size=4, sample_fps=2.0, in_patch_limit=16384, in_patch_limit_each_frame=4096, patch_limit_on_one_side=512, timestamp_mode='hh:mm:ss.fff'. config flag use_unified_vision_chunk=true.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 163605 |
| video_token_id | [Unknown/Not Disclosed] |
| vision_start_token_id | 163602 |
| vision_end_token_id | 163604 |

## 待解问题（open_questions）

- K2 base tech report is not yet published ('paper coming soon' on the K2-Base HF page) — K2.5 paper §4.1 references it for K2-base optimizer, lr schedule, MuonClip / QK-Clip details, training-infrastructure parallelism strategy, mixed-precision recipe, and pre-training data mix. Several training fields stay at UNKNOWN until that report ships.
- Sparsity 48 quoted in paper §4.1 (384 experts, 8 activated) — the convention is total/active = 384/8 = 48, consistent with the recorded fields; flagged in case the paper means something else by 'sparsity'.
- Joint pre-training cumulative token budget: K2.5 paper §2 says '~15 trillion mixed visual and text tokens'; paper §4.3 / Table 3 also lists 15T for the joint stage. Whether this is in addition to K2-base's 15T (cumulative ~30T text+mixed) or replaces a portion of it is implied but not stated explicitly.
- video_token_id — the chat template uses string substitution `<|kimi_k25_video_placeholder|>` rather than a single reserved tokenizer-vocab ID; tokenizer_config.json does not list a video token in added_tokens_decoder. Recorded as UNKNOWN.

---

_由 `data/extracted/kimi-k2.5.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
