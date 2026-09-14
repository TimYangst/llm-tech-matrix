# Megatron-Bridge v0.6.0

> English: [megatron-bridge-v0.6.0.md](./megatron-bridge-v0.6.0.md)

*引擎 schema 版本： 3*

## 概览

| 字段 | 值 |
|---|---|
| 仓库 | https://github.com/NVIDIA-NeMo/Megatron-Bridge |
| 许可证 | Apache-2.0 |
| 发布 tag | `v0.6.0` |
| Commit | `51885cf132b2814188b6855c25a8588254274c2a` |
| 发布日期 | 2026-08-19 |
| 快照日期 | 2026-09-13 |
| 角色 | `training` |
| 硬件平台 | NVIDIA GPU |

## 并行方式

| 维度 | 是否支持 | 实现方式 | 说明 | 证据 |
|---|---|---|---|---|
| 张量并行 | ✓ | tensor_model_parallel_size on the model provider (Megatron Core TP) | DeepSeek-V4 requires TP=1 (MLA tensor parallelism is not supported with its hybrid attention). | [parallelisms.md#L53](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L53), [README.md#L163](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L163) |
| 流水线并行 | ✓ | pipeline_model_parallel_size, optional interleaved schedule (virtual_pipeline_model_parallel_size) | — | [parallelisms.md#L87](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L87), [parallelisms.md#L121](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L121) |
| 数据并行 | ✓ | Megatron Core DDP with the distributed optimizer | — | [parallelisms.md#L9](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L9), [parallelisms.md#L16](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L16) |
| 专家并行 | ✓ | expert_model_parallel_size for MoE models | — | [parallelisms.md#L132](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L132) |
| 上下文并行 | ✓ | context_parallel_size (Megatron Core CP); THD-packed CP for long-context SFT | DeepSeek-V4 sparse layers do not support packed THD sequences at this tag. | [parallelisms.md#L369](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L369), [README.md#L125](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L125) |
| 序列并行 | ✓ | sequence_parallel alongside TP | — | [parallelisms.md#L343](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md#L343) |

## 训练

**混合精度：** Megatron mixed-precision configs over BF16 with optional FP8 recipes and FP4 (default fp4_recipe nvfp4).

_证据：_ [mixed_precision.py#L50](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/training/mixed_precision.py#L50), [mixed_precision.py#L64](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/training/mixed_precision.py#L64)

**Checkpoint：** Megatron checkpoints; PyTorch DCP format is detected on load; HF weights can be saved alongside native checkpoints.

_证据：_ [checkpointing.py#L253](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/training/checkpointing.py#L253), [release notes](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.6.0)

**LoRA：** PEFT LoRA (and DoRA) applied to matched modules, with multi-GPU adapter export.

_证据：_ [lora.py#L50](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/peft/lora.py#L50), [release notes](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.6.0)

**训练类型** (4)： HF <-> Megatron checkpoint conversion and verification, pre-training, SFT, SFT LoRA

_证据：_ [README.md#L73](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md#L73), [auto_bridge.py#L63](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/auto_bridge.py#L63)

**训练后端** (1)： `megatron-core`

_证据：_ [pyproject.toml#L186](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/pyproject.toml#L186)

**优化器** (2)： `distributed fused Adam (cosine annealing)`, `distributed Muon (adam or lion for scalar parameters)`

_证据：_ [optimizer_utils.py#L100](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/recipes/utils/optimizer_utils.py#L100), [optimizer_utils.py#L20](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/recipes/utils/optimizer_utils.py#L20)

_说明：_ Model support is an explicit registry: @MegatronModelBridge.register_bridge(source=<HF architecture>) per bridge; AutoBridge accepts architectures ending in ForCausalLM / ForConditionalGeneration and dispatches to the registered bridge. The README's functional matrix marks RL and RL LoRA as 'N' for Megatron-Bridge (RL is NeMo RL's job), so the rl_post_training role is not claimed.

## 集成

| 名称 | 关系 | 版本约束 | 说明 | 证据 |
|---|---|---|---|---|
| Megatron-LM (Megatron Core) ([`megatron-lm-core_v0.19.0`](./megatron-lm-core_v0.19.0.md)) | `training_backend` | 3rdparty/Megatron-LM git submodule: commit cd4afffa648426a959dc7cb1e24b5ce7d0c3ff54 (Megatron-LM main, 2026-07-25), not the core_v0.19.0 tag<br>pyproject.toml: megatron-core[dev,mlm] installed from path 3rdparty/Megatron-LM<br>examples/models/deepseek_v4/README.md: DeepSeek-V4 pretraining tested with Megatron-LM dev commit 35f36c7c9dba plus PR #4839<br>examples/models/deepseek_v4/README.md: DeepSeek-V4 SFT validated on main2dev Megatron-LM commit ed6b1f65502aec7f2fe27e14a1245c29e435c2a6 | The tracked megatron-lm-core_v0.19.0 snapshot matches none of these: the submodule is a main commit, and DeepSeek-V4 needs dev-branch code absent from both the submodule commit and the release tag. | [.gitmodules#L2](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/.gitmodules#L2), [3rdparty](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/51885cf132b2814188b6855c25a8588254274c2a/3rdparty), [pyproject.toml#L186](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/pyproject.toml#L186), [README.md#L9](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L9), [README.md#L145](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L145) |
| verl ([`verl-v0.9.0`](./verl-v0.9.0.md)) | `used_by` | — | The README states VeRL adopted Megatron-Bridge as its connector to Megatron Core and for LoRA; docs/bridge-rl-integration.md describes the adaptation pattern (mirroring NeMo RL). | [README.md#L289](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md#L289), [bridge-rl-integration.md#L1](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/bridge-rl-integration.md#L1) |
| Hugging Face Transformers | `other` | pyproject.toml: transformers>=5.8,<=5.12.1 | Bridges import HF model classes (or register by architecture string for auto_map models). | [pyproject.toml#L74](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/pyproject.toml#L74) |

## 模型支持

| 架构 | 模型记录 | 支持程度 | 文档列出 | 特性 | 投机解码 | 证据 |
|---|---|---|---|---|---|---|
| `DeepseekV3ForCausalLM` | [`deepseek-v3`](../deepseek-v3.md), [`kimi-k2-thinking`](../kimi-k2-thinking.md) | `registered` | ✓ | — | — | [deepseek_v3_bridge.py#L45](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v3_bridge.py#L45) |
| `DeepseekV32ForCausalLM` | [`deepseek-v3.2-exp`](../deepseek-v3.2-exp.md) | `not_found` | ✗ | — | — | [model_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/model_bridge.py), [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md), [51885cf132b2814188b6855c25a8588254274c2a](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/51885cf132b2814188b6855c25a8588254274c2a) |
| `DeepseekV4ForCausalLM` | [`deepseek-v4-pro`](../deepseek-v4-pro.md), [`deepseek-v4-flash`](../deepseek-v4-flash.md), [`deepseek-v4-flash-0731`](../deepseek-v4-flash-0731.md) | `registered` | ✓ | — | — | [deepseek_v4_bridge.py#L350](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v4_bridge.py#L350), [README.md#L52](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L52), [README.md#L54](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L54), [README.md#L163](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L163), [README.md#L138](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L138), [release notes](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.6.0) |
| `DeepseekV41ForCausalLM` | [`deepseek-v4.1-flash`](../deepseek-v4.1-flash.md) | `not_found` | ✗ | — | — | [model_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/model_bridge.py), [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md), [51885cf132b2814188b6855c25a8588254274c2a](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/51885cf132b2814188b6855c25a8588254274c2a) |
| `Glm4MoeForCausalLM` | [`glm-4.7`](../glm-4.7.md) | `registered` | ✓ | — | — | [glm45_bridge.py#L43](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm/glm45_bridge.py#L43), [glm47.md#L9](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm47.md#L9) |
| `GlmMoeDsaForCausalLM` | [`glm-5`](../glm-5.md), [`glm-5.1`](../glm-5.1.md), [`glm-5.2`](../glm-5.2.md) | `registered` | ✓ | — | — | [glm5_bridge.py#L36](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L36), [glm5.md#L11](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm5.md#L11), [glm5_bridge.py#L92](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L92) |
| `Glm5NextForConditionalGeneration` | [`glm-5.3-flash`](../glm-5.3-flash.md) | `not_found` | ✗ | — | — | [model_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/model_bridge.py), [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md), [51885cf132b2814188b6855c25a8588254274c2a](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/51885cf132b2814188b6855c25a8588254274c2a) |
| `KimiK25ForConditionalGeneration` | [`kimi-k2.5`](../kimi-k2.5.md), [`kimi-k2.6`](../kimi-k2.6.md) | `registered` | ✓ | — | — | [kimi_k25_vl_bridge.py#L47](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/kimi_vl/kimi_k25_vl_bridge.py#L47), [kimi-k25-vl.md#L12](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/kimi/kimi-k25-vl.md#L12) |
| `KimiK3ForConditionalGeneration` | [`kimi-k3`](../kimi-k3.md) | `not_found` | ✗ | — | — | [model_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/model_bridge.py), [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md), [51885cf132b2814188b6855c25a8588254274c2a](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/51885cf132b2814188b6855c25a8588254274c2a) |
| `Qwen3ForCausalLM` | [`qwen3-32b`](../qwen3-32b.md) | `registered` | ✓ | — | — | [qwen3_bridge.py#L28](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen3_bridge.py#L28) |
| `Qwen3MoeForCausalLM` | [`qwen3-235b-a22b`](../qwen3-235b-a22b.md) | `registered` | ✓ | — | — | [qwen3_moe_bridge.py#L28](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen3_moe_bridge.py#L28) |
| `Qwen3_5ForConditionalGeneration` | [`qwen3.5-27b`](../qwen3.5-27b.md), [`qwen3.6-27b`](../qwen3.6-27b.md), [`qwen3.8-27b`](../qwen3.8-27b.md) | `registered` | ✓ | — | — | [qwen35_vl_bridge.py#L60](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen_vl/qwen35_vl_bridge.py#L60), [qwen35_vl_bridge.py#L272](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen_vl/qwen35_vl_bridge.py#L272) |
| `Qwen3_5MoeForConditionalGeneration` | [`qwen3.5-35b-a3b`](../qwen3.5-35b-a3b.md), [`qwen3.6-35b-a3b`](../qwen3.6-35b-a3b.md) | `registered` | ✓ | — | — | [qwen35_vl_bridge.py#L61](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen_vl/qwen35_vl_bridge.py#L61), [qwen35_vl_bridge.py#L139](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen_vl/qwen35_vl_bridge.py#L139), [qwen35-vl.md#L5](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/qwen/qwen35-vl.md#L5) |
| `Qwen3_5MoeForCausalLM` | [`qwen3.8-2.4t-a95b`](../qwen3.8-2.4t-a95b.md) | `registered` | _未知_ | — | — | [qwen35_bridge.py#L137](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen35_bridge.py#L137) |
| `Qwen4ExpForConditionalGeneration` | [`qwen3.8-flash-next`](../qwen3.8-flash-next.md) | `not_found` | ✗ | — | — | [model_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/model_bridge.py), [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/README.md), [51885cf132b2814188b6855c25a8588254274c2a](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/51885cf132b2814188b6855c25a8588254274c2a) |

### 逐模型信息

| 模型记录 | 起始版本 | Reasoning parser | Tool parser | 说明 | 证据 |
|---|---|---|---|---|---|
| [`glm-5.2`](../glm-5.2.md) | v0.6.0 | _未知_ | _未知_ | The v0.6.0 release notes list GLM-5.2 bridge and recipes (GB200/H100, cuDNN DSA path) as new model support. | [release notes](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.6.0) |

### 逐行说明

- **`DeepseekV3ForCausalLM`** — The README lists DeepSeek V3 and Kimi K2 (a separate KimiK2ForCausalLM bridge also exists); Kimi K2 Thinking checkpoints declare DeepseekV3ForCausalLM.
- **`DeepseekV4ForCausalLM`** — Registered in the bridge registry, but the Megatron Core modules it needs are on Megatron-LM dev (see integrations). V4-Flash logits verified against official inference (cosine 0.96-0.99); V4-Pro import/export/inference verified. SFT runs with MTP on or off; TP must be 1; packed THD sequences are unsupported on the sparse layers; MXFP8 and Muon SFT fail upstream. The release notes still say 'verification in progress'.
- **`DeepseekV41ForCausalLM`** — The model (2026-09) postdates this release (2026-08-19).
- **`GlmMoeDsaForCausalLM`** — MTP is disabled by default in the bridge (provider.mtp_num_layers = None) although the HF config has num_nextn_predict_layers=1.
- **`KimiK25ForConditionalGeneration`** — The docs name only Kimi-K2.5-VL; Kimi K2.6 is covered by architecture, not named.
- **`Qwen3_5MoeForConditionalGeneration`** — The docs state Qwen3.6-35B-A3B uses the same bridge.

## 技术实现

| Glossary 条目 | 实现方式 | 参数 | 起始版本 | 证据 |
|---|---|---|---|---|
| [dsa](../../../docs/glossary/dsa.md) | GLM-5 bridge maps the DSA indexer (experimental_attention_variant 'dsa', indexer heads / head dim / top-k from the HF config, indexer loss); GLM-5.2 recipes use the cuDNN fused DSA path. | `experimental_attention_variant=dsa` | _未知_ | [glm5_bridge.py#L131](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L131), [release notes](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.6.0) |
| [indexshare](../../../docs/glossary/indexshare.md) | GLM-5.2 IndexShare-style index reuse: index_topk_freq and index_skip_topk_offset are read from the HF config into the DSA provider. | `dsa_indexer_topk_freq`<br>`dsa_indexer_skip_topk_offset` | _未知_ | [glm5_bridge.py#L136](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L136), [glm5.md#L11](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm5.md#L11) |
| [csa-hca](../../../docs/glossary/csa-hca.md) | DeepSeek-V4 bridge maps hybrid self-attention layers (CompressedSparseAttention with CSAIndexer and Compressor; per-layer compress ratios) to Megatron modules. | — | _未知_ | [deepseek_v4_bridge.py#L59](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v4_bridge.py#L59), [deepseek_v4_bridge.py#L94](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v4_bridge.py#L94) |
| [mhc](../../../docs/glossary/mhc.md) | DeepSeek-V4 mHC (hc_mult = 4) with an optional fused cuTile kernel (use_fused_mhc, Blackwell-only). | `use_fused_mhc` | _未知_ | [deepseek-v4.md#L11](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/deepseek/deepseek-v4.md#L11), [README.md#L104](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L104) |
| [mtp](../../../docs/glossary/mtp.md) | MTP weights mapped end to end (DeepSeek-V4 mtp.N.* with separate e_proj / h_proj); DeepSeek-V4-Flash SFT recipes with MTP on or off; MTP disabled for inference. | `MTP=on\|off (slurm_sft.sh)` | _未知_ | [deepseek_v4_bridge.py#L34](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v4_bridge.py#L34), [README.md#L62](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L62), [README.md#L175](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L175) |
| [mla](../../../docs/glossary/mla.md) | MLAModelProvider builds MLA configs for DeepSeek-V3/V4, GLM-5 and Kimi K2.5 bridges. | — | _未知_ | [mla_provider.py#L28](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/mla_provider.py#L28), [glm5_bridge.py#L36](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L36) |
| [gated-deltanet](../../../docs/glossary/gated-deltanet.md) | Qwen3.5 bridges set experimental_attention_variant 'gated_delta_net' and map GatedDeltaNet weights (column-parallel). | `experimental_attention_variant=gated_delta_net` | _未知_ | [qwen35_bridge.py#L61](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen35_bridge.py#L61), [qwen35-vl.md#L7](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/qwen/qwen35-vl.md#L7) |
| [muon](../../../docs/glossary/muon.md) | Recipe helper distributed_muon_with_cosine_annealing (Megatron Core Muon: spectral scale mode, blockwise TP mode, adam or lion for scalar parameters). | — | _未知_ | [optimizer_utils.py#L20](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/recipes/utils/optimizer_utils.py#L20), [README.md#L138](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md#L138) |

- **dsa** — Kernels live in Megatron Core.
- **csa-hca** — The attention modules come from Megatron-LM dev, not a release; packed THD is unsupported on these layers.
- **mhc** — Use the unfused path on Hopper.
- **mtp** — The GLM-5 bridge disables MTP by default.
- **muon** — DeepSeek-V4 Muon SFT fails upstream and no SFT recipe is shipped.

## 开放问题

- DeepSeek-V4 is registered, but its Megatron Core dependency (CSA/HCA, mHC, hash MoE, MTP+mHC) is on Megatron-LM dev; neither the pinned submodule commit nor core_v0.19.0 contains it. The release notes still say 'verification in progress'.
- The pinned Megatron-LM submodule (cd4afff, main 2026-07-25) differs from the same-day Megatron-LM release core_v0.19.0 (a release-branch tag not on main), so 'Bridge v0.6.0 + Megatron-LM 0.19.0' is not a combination these sources describe.
- Kimi K2.6 and Qwen3.8-27B / Qwen3.8-2.4T-A95B are covered only because they reuse registered architectures; no doc or verification card names them.
- Qwen3_5MoeForCausalLM (text-only, used by Qwen3.8-2.4T-A95B) has a registered bridge, but no model doc among the sources covers the text-only variant.
- DeepSeek-V4 checkpoints ship MXFP4 experts; the bridge dequantizes MXFP4 on import and can export quantized checkpoints, but no MXFP4 quantization-aware training is documented, so fp4-qat is not asserted.
- The README says VeRL adopted Megatron-Bridge, but no verl version is stated; the verl-v0.9.0 link is to the tracked snapshot, not a tested pairing.

## 来源

- <https://api.github.com/repos/NVIDIA-NeMo/Megatron-Bridge/releases/tags/v0.6.0>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/README.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/pyproject.toml>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/.gitmodules>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/auto_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/conversion/model_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/mla_provider.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v3_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/deepseek/deepseek_v4_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm/glm45_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/kimi_vl/kimi_k25_vl_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen3_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen3_moe_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen/qwen35_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/qwen_vl/qwen35_vl_bridge.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/recipes/utils/optimizer_utils.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/training/mixed_precision.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/training/checkpointing.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/peft/lora.py>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/parallelisms.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/bridge-rl-integration.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/models/deepseek/deepseek-v4.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm5.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm47.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/models/kimi/kimi-k25-vl.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/models/qwen/qwen35-vl.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/docs/models/qwen/qwen3-moe.md>
- <https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/51885cf132b2814188b6855c25a8588254274c2a/examples/models/deepseek_v4/README.md>
