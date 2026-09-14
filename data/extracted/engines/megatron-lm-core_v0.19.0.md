# Megatron-LM core_v0.19.0

> 中文版：[megatron-lm-core_v0.19.0.zh.md](./megatron-lm-core_v0.19.0.zh.md)

*Engine schema version: 3*

## Overview

| Field | Value |
|---|---|
| Repository | https://github.com/NVIDIA/Megatron-LM |
| License | BSD-3-Clause (LICENSE file; bundled third-party code under Apache-2.0 and others) |
| Release tag | `core_v0.19.0` |
| Commit | `5be9626709af2722333bf54797c954c09edeada3` |
| Release date | 2026-08-19 |
| Snapshot date | 2026-09-13 |
| Roles | `training`, `rl_post_training`, `inference` |
| Hardware | NVIDIA GPU |

## Parallelism

| Dimension | Supported | Implementation | Notes | Evidence |
|---|---|---|---|---|
| Tensor | ✓ | tensor_model_parallel_size | — | [parallelism-guide.md#L74](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L74), [model_parallel_config.py#L55](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/model_parallel_config.py#L55) |
| Pipeline | ✓ | pipeline_model_parallel_size, with configurable pipeline layouts | — | [parallelism-guide.md#L89](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L89), [arguments.py#L2950](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2950) |
| Data | ✓ | DDP, distributed optimizer (optimizer state sharded across DP ranks), Megatron-FSDP, torch FSDP2 | Megatron-FSDP sharding strategies: no_shard, optim (ZeRO-1), optim_grads (ZeRO-2), optim_grads_params (ZeRO-3). | [parallelism-guide.md#L29](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L29), [parallelism-guide.md#L40](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L40), [parallelism-guide.md#L57](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L57), [dist_optimizer.md#L12](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/dist_optimizer.md#L12), [arguments.py#L2997](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2997) |
| Expert | ✓ | expert_model_parallel_size; token dispatchers include DeepEP, HybridEP and (new in 0.19.0) NCCL EP | — | [parallelism-guide.md#L121](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L121), [model_parallel_config.py#L127](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/model_parallel_config.py#L127), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |
| Context | ✓ | context_parallel_size (cp_comm_type, default p2p) | — | [parallelism-guide.md#L104](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L104), [arguments.py#L3054](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L3054) |
| Sequence | ✓ | sequence_parallel (activation partitioning alongside TP) | — | [parallelism-guide.md#L217](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L217), [model_parallel_config.py#L94](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/model_parallel_config.py#L94) |

## Serving

**Scheduler:** DynamicInferenceEngine with dynamic batching; coordinator mode routes requests across data-parallel replicas and is required for HTTP serving.

_Evidence:_ [arguments.py#L1995](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L1995), [README.md#L3](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/README.md#L3)

**KV cache management:** Block-based KV cache (KVBlockAllocator manages a pool of block IDs; block size set by --inference-dynamic-batching-block-size).

_Evidence:_ [kv_block_allocator.py#L14](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/contexts/kv_block_allocator.py#L14), [arguments.py#L2020](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2020)

**Prefix caching:** Optional (--inference-dynamic-batching-prefix-caching) with eviction and coordinator routing policies; 0.19.0 adds load-aware prefix-cache routing across workers.

_Evidence:_ [arguments.py#L2078](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2078), [arguments.py#L2085](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2085), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0)

**Disaggregation:** Foundations only in 0.19.0 (release notes): heterogeneous inference-shard specifications, multi-destination refit, KV/Mamba-state resharding and a NIXL copy backend.

_Evidence:_ [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0)

**API surfaces** (2): MegatronLLM.generate (sync, offline), MegatronAsyncLLM.serve: OpenAI-compatible HTTP (/v1/completions, /v1/chat/completions)

_Evidence:_ [README.md#L3](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/README.md#L3), [README.md#L28](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/README.md#L28)

**Speculative decoding methods** (1): `mtp`

_Evidence:_ [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0)

_Notes:_ Megatron-RL uses this engine for rollouts, with refit copying weights from the training model (see rl.weight_sync); the README lists refit-oriented weight-update APIs as future work. The HTTP frontend is fixed to global rank 0, returns model 'EMPTY' and has no /v1/models endpoint; streaming and a `megatron serve` CLI are listed as future work. Response parsers are configurable (ServeConfig.parsers, --rl-inference-parsers) but no parser registry is among the sources, so none are listed.

## Training

**Mixed precision:** FP16, BF16, FP8 and FP4. FP8 recipes run through Transformer Engine: delayed, tensorwise, blockwise, mxfp8 and custom; 0.19.0 adds MXFP8 training paths.

_Evidence:_ [README.md#L20](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/README.md#L20), [fp8_utils.py#L743](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/fp8_utils.py#L743), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0)

**Quantization-aware training:** NVFP4 quantization-aware training through NVIDIA ModelOpt (examples/post_training/modelopt).

_Evidence:_ [README.md#L57](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L57)

**Checkpointing:** Megatron checkpoints or distributed checkpoints (--use-dist-ckpt, --dist-ckpt-format), with optional fully parallel save.

_Evidence:_ [arguments.py#L2886](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2886), [arguments.py#L2896](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2896)

**Kernels:** Transformer Engine for FP8/FP4 recipes and fused layers; DSA indexer and sparse-attention kernels in cuDNN and TileLang.

_Evidence:_ [fp8_utils.py#L744](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/fp8_utils.py#L744), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0)

**Workloads** (3): pre-training (GPT, Mamba, hybrid, VLM), RL post-training (Megatron-RL), ModelOpt post-training (quantization, QAT, EAGLE3, pruning, distillation)

_Evidence:_ [README.md#L6](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/README.md#L6), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3), [megatron_rl.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/megatron_rl.md#L16), [README.md#L29](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L29)

**Training backends** (3): `ddp`, `megatron-fsdp`, `torch-fsdp2`

_Evidence:_ [parallelism-guide.md#L29](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md#L29), [megatron_fsdp.md#L14](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/megatron_fsdp.md#L14), [arguments.py#L3051](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L3051)

**Optimizers** (7): `adam`, `sgd`, `muon`, `dist_muon`, `lion`, `soap`, `adaptive_muon`

_Evidence:_ [arguments.py#L2777](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2777)

_Notes:_ Megatron Core is the library (building blocks, parallelism, precision); Megatron-LM is the reference training scripts around it. Model architectures are generic composable specs (GPTModel, the new HybridModel, Mamba, T5, BERT, MIMO); converting HF checkpoints is delegated to Megatron-Bridge. GPTModel is being deprecated in favour of HybridModel. `dist_muon` is deprecated in favour of `muon` with the distributed optimizer.

## RL post-training

**Weight sync:** Refit copies weights from the training model to the colocated inference model between rollout steps (--refit-method; default gloo over CPU). KV cache during training can persist, be offloaded or be recomputed (--rl-kv-cache-management-mode).

_Evidence:_ [arguments.py#L2698](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2698), [arguments.py#L2622](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2622)

**Reward:** Agents / environments receive an inference handle and return rollouts with rewards; examples include countdown, GSM8K, MATH and DAPO environments.

_Evidence:_ [megatron_rl.md#L33](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/megatron_rl.md#L33)

**Algorithms** (1): `grpo`

_Evidence:_ [rl_utils.py#L831](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/rl/rl_utils.py#L831), [arguments.py#L2576](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2576)

**Rollout backends** (3): `megatron`, `openai`, `huggingface`

_Evidence:_ [megatron_rl.md#L23](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/megatron_rl.md#L23)

**Weight-sync backends** (3): `nccl`, `gloo`, `nvshmem`

_Evidence:_ [arguments.py#L2699](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2699)

_Notes:_ GRPO is the only advantage estimator (group size, prompts per step, clamp eps, KL beta, entropy weight, same-reward group filtering). The docs call Megatron-RL under active development and aimed at research teams, pointing production users to NeMo RL; megatron/rl/README.md (dated 08/27/2025) still says it is not yet usable by external users.

## Integrations

| Name | Relation | Version constraints | Notes | Evidence |
|---|---|---|---|---|
| Megatron-Bridge ([`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md)) | `used_by` | — | HF checkpoint conversion is delegated to Megatron-Bridge, which builds on Megatron Core. Megatron-Bridge v0.6.0 pins its own Megatron-LM submodule commit rather than this tag (see that record). | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16) |
| Transformer Engine | `kernel_library` | — | Provides the FP8 recipes (DelayedScaling, Float8CurrentScaling, Float8BlockScaling, MXFP8BlockScaling); some recipes require minimum TE versions (e.g. blockwise needs TE >= 2.3.0.dev0). | [fp8_utils.py#L743](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/fp8_utils.py#L743) |
| NVIDIA ModelOpt | `other` | pyproject.toml: nvidia-modelopt[torch]>=0.44 | Quantization, QAT, EAGLE3 draft training, pruning and distillation examples. | [pyproject.toml#L93](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/pyproject.toml#L93), [README.md#L29](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L29) |

## Model support

| Architecture | Model records | Support | Documented | Features | Spec. decoding | Evidence |
|---|---|---|---|---|---|---|
| `DeepseekV3ForCausalLM` | [`deepseek-v3`](../deepseek-v3.md), [`kimi-k2-thinking`](../kimi-k2-thinking.md) | `model_specific` | ✓ | — | — | [README.md#L68](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/megatron_fsdp/README.md#L68), [README.md#L31](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L31), [README.md#L34](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L34) |
| `DeepseekV32ForCausalLM` | [`deepseek-v3.2-exp`](../deepseek-v3.2-exp.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `DeepseekV4ForCausalLM` | [`deepseek-v4-pro`](../deepseek-v4-pro.md), [`deepseek-v4-flash`](../deepseek-v4-flash.md), [`deepseek-v4-flash-0731`](../deepseek-v4-flash-0731.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |
| `DeepseekV41ForCausalLM` | [`deepseek-v4.1-flash`](../deepseek-v4.1-flash.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `Glm4MoeForCausalLM` | [`glm-4.7`](../glm-4.7.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `GlmMoeDsaForCausalLM` | [`glm-5`](../glm-5.md), [`glm-5.1`](../glm-5.1.md), [`glm-5.2`](../glm-5.2.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `Glm5NextForConditionalGeneration` | [`glm-5.3-flash`](../glm-5.3-flash.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `KimiK25ForConditionalGeneration` | [`kimi-k2.5`](../kimi-k2.5.md), [`kimi-k2.6`](../kimi-k2.6.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `KimiK3ForConditionalGeneration` | [`kimi-k3`](../kimi-k3.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `Qwen3ForCausalLM` | [`qwen3-32b`](../qwen3-32b.md) | `model_specific` | ✓ | — | — | [README.md#L40](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L40) |
| `Qwen3MoeForCausalLM` | [`qwen3-235b-a22b`](../qwen3-235b-a22b.md) | `model_specific` | ✓ | — | — | [README.md#L41](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L41) |
| `Qwen3_5ForConditionalGeneration` | [`qwen3.5-27b`](../qwen3.5-27b.md), [`qwen3.6-27b`](../qwen3.6-27b.md), [`qwen3.8-27b`](../qwen3.8-27b.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `Qwen3_5MoeForConditionalGeneration` | [`qwen3.5-35b-a3b`](../qwen3.5-35b-a3b.md), [`qwen3.6-35b-a3b`](../qwen3.6-35b-a3b.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `Qwen3_5MoeForCausalLM` | [`qwen3.8-2.4t-a95b`](../qwen3.8-2.4t-a95b.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |
| `Qwen4ExpForConditionalGeneration` | [`qwen3.8-flash-next`](../qwen3.8-flash-next.md) | `delegated` → [`megatron-bridge-v0.6.0`](./megatron-bridge-v0.6.0.md) | ✗ | — | — | [llms.md#L16](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md#L16), [5be9626709af2722333bf54797c954c09edeada3](https://github.com/NVIDIA/Megatron-LM/tree/5be9626709af2722333bf54797c954c09edeada3) |

### Row notes

- **`DeepseekV3ForCausalLM`** — No architecture registry exists in Megatron-LM; the string DeepseekV3ForCausalLM appears nowhere at the commit. ModelOpt converts the HF checkpoint on the fly; Kimi K2 Thinking itself is not named.
- **`DeepseekV32ForCausalLM`** — The DSA attention variant cites DeepSeek-V3.2-Exp as its reference, but no model definition, config or example targets the model.
- **`DeepseekV4ForCausalLM`** — Delegated to Megatron-Bridge, which registers DeepSeek-V4, but the Megatron Core code that bridge needs is not in this release: the 0.19.0 notes place DeepSeek-V4 (migrated to HybridModel) on the `dev` branch only, and neither the architecture string nor model_type deepseek_v4 appears in megatron/ at the tag.
- **`DeepseekV41ForCausalLM`** — The model (2026-09) postdates this release (2026-08-19).
- **`GlmMoeDsaForCausalLM`** — No model definition, but the DSA implementation carries GLM-5 variants (indexer ReLU disabled for GLM5) and IndexShare, which GLM-5.2 introduced; the GLM-5 model is assembled in Megatron-Bridge.
- **`Qwen3ForCausalLM`** — Docs-only signal; Qwen3-32B itself is not named.
- **`Qwen3MoeForCausalLM`** — Quantization is marked 'WAR' (workaround) for the MoE variants.
- **`Qwen3_5ForConditionalGeneration`** — Megatron Core has a GatedDeltaNet layer, but Qwen3.5 is only wired up in Megatron-Bridge.

## Technique support

| Glossary entry | Implementation | Flags | Since | Evidence |
|---|---|---|---|---|
| [dsa](../../../docs/glossary/dsa.md) | experimental_attention_variant 'dsa': lightning indexer + sparse MLA attention with an indexer KL loss; 0.19.0 adds backend-neutral CP and THD, pipeline-aware indexer-loss scaling and fused cuDNN / TileLang kernels. | `experimental_attention_variant=dsa` | _unknown_ | [dsa.py#L407](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/experimental_attention_variant/dsa.py#L407), [experimental_attention_variant_module_specs.py#L143](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/models/gpt/experimental_attention_variant_module_specs.py#L143), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |
| [indexshare](../../../docs/glossary/indexshare.md) | DSA index sharing: with index_topk_freq > 1, layers without their own top-k reuse a previous indexer layer's selection; pipeline splits are validated so shared indices stay on one stage. | `dsa_indexer_topk_freq > 1` | _unknown_ | [dsa.py#L1564](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/experimental_attention_variant/dsa.py#L1564), [experimental_attention_variant_module_specs.py#L339](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/models/gpt/experimental_attention_variant_module_specs.py#L339), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |
| [mla](../../../docs/glossary/mla.md) | Multi-Latent Attention (q/kv LoRA ranks, decoupled RoPE head dim, optional latent caching), now also in HybridModel. | `--multi-latent-attention`<br>`--q-lora-rank`<br>`--kv-lora-rank` | _unknown_ | [multi_latent_attention.md#L14](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/multi_latent_attention.md#L14), [arguments.py#L3383](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L3383), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |
| [mtp](../../../docs/glossary/mtp.md) | DeepSeek-V3-style sequential MTP modules for GPTModel-style models (mtp_num_layers, mtp_loss_scaling_factor default 0.1); full-model CUDA graphs for MTP inference in 0.19.0. | `mtp_num_layers` | _unknown_ | [multi_token_prediction.md#L22](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/multi_token_prediction.md#L22), [transformer_config.py#L68](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/transformer_config.py#L68) |
| [muon](../../../docs/glossary/muon.md) | Muon family through the Emerging-Optimizers library (muon, adaptive_muon; lion or adam for scalar parameters), tensor-parallel aware (muon_tp_mode blockwise) and routed through the distributed optimizer. | `--optimizer muon`<br>`--muon-tp-mode` | _unknown_ | [arguments.py#L2777](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2777), [emerging_optimizers.py#L29](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/optimizer/emerging_optimizers.py#L29), [arguments.py#L2540](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2540) |
| [gated-deltanet](../../../docs/glossary/gated-deltanet.md) | GatedDeltaNet layer selectable as the experimental attention variant 'gated_delta_net' in hybrid layer patterns. | `experimental_attention_variant=gated_delta_net`<br>`--linear-attention-freq` | _unknown_ | [gdn.py#L30](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/ssm/gated_delta_net/gdn.py#L30), [experimental_attention_variant_module_specs.py#L141](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/models/gpt/experimental_attention_variant_module_specs.py#L141) |
| [aux-loss-free-routing](../../../docs/glossary/aux-loss-free-routing.md) | Quantile Balancing router (moe_router_load_balancing_type 'quantile_balancing'): a per-expert routing bias from quantile estimates replaces the auxiliary loss. | `moe_router_load_balancing_type=quantile_balancing` | _unknown_ | [router.py#L220](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/moe/router.py#L220), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |
| [grpo](../../../docs/glossary/grpo.md) | Megatron-RL GRPO: group-relative advantages over grpo_group_size samples per prompt, clipped ratio (grpo_clamp_eps_lower/upper), KL beta and entropy weight. | `--perform-rl-step`<br>`--grpo-group-size` | _unknown_ | [rl_utils.py#L831](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/rl/rl_utils.py#L831), [arguments.py#L2606](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py#L2606) |
| [fp8-mixed-precision](../../../docs/glossary/fp8-mixed-precision.md) | FP8 training through Transformer Engine recipes, including block-wise scaling (Float8BlockScaling) alongside delayed, tensorwise and MXFP8. | `fp8_recipe=blockwise` | _unknown_ | [fp8_utils.py#L743](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/fp8_utils.py#L743), [fp8_utils.py#L744](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/fp8_utils.py#L744) |
| [speculative-decoding](../../../docs/glossary/speculative-decoding.md) | EAGLE3 draft-module training and export through ModelOpt examples; MTP speculative inference in the Megatron inference engine. | `eagle3.sh (ModelOpt example)` | _unknown_ | [README.md#L29](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md#L29), [release notes](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.19.0) |

- **dsa** — Cites DeepSeek-V3.2-Exp; also carries GLM-5 indexer variants.
- **aux-loss-free-routing** — A different bias estimator (dual coordinate-descent quantiles, optional EMA) from DeepSeek-V3's sign-step bias update.
- **fp8-mixed-precision** — Block-wise scaling is the fine-grained variant the glossary entry describes; the other recipes are per-tensor or microscaling.

## Open questions

- DeepSeek-V4 support exists only on the `dev` branch (release notes: 'Deepseek v4 migrated to HybridModel on the `dev` branch'); nothing DeepSeek-V4-specific is in core_v0.19.0. verl's DeepSeek-V4 path (Megatron-Bridge + Megatron) and Megatron-Bridge's own DeepSeek-V4 recipes therefore depend on unreleased Megatron-LM code.
- License: the LICENSE file is BSD-3-Clause for NVIDIA code (with Apache-2.0 and other licenses for bundled third-party files), while the README badge says Apache and GitHub's license detection reports NOASSERTION.
- megatron/rl/README.md (status dated 08/27/2025) says Megatron-RL is not yet usable by external users, while docs/user-guide/features/megatron_rl.md presents it as usable for research with NeMo RL recommended for production. The rl_post_training role is recorded from the code at this tag (GRPO, refit backends), not from a production-readiness claim.
- Megatron-LM maps no HF architectures (generic specs; docs/models/llms.md sends HF conversion to Megatron-Bridge), so rows without an in-repo signal are `delegated` to megatron-bridge-v0.6.0. Delegation records responsibility, not compatibility: Bridge v0.6.0 pins a Megatron-LM main commit, not this tag. The model_specific rows are documentation signals (Megatron-FSDP DeepSeek-V3 example, ModelOpt support matrix), not registry entries.
- Megatron-Bridge v0.6.0 pins Megatron-LM as a submodule at a main-branch commit (cd4afff, 2026-07-25) instead of this release tag, and this tag is not an ancestor of main; which Megatron-LM version a Bridge user actually runs depends on the container.
- CSA/HCA and mHC (DeepSeek-V4) do not appear in megatron/ at this tag; Megatron-Bridge's DeepSeek-V4 README credits them to Megatron-LM PRs available on dev.

## Sources

- <https://api.github.com/repos/NVIDIA/Megatron-LM/releases/tags/core_v0.19.0>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/README.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/pyproject.toml>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/requirements.txt>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/models/llms.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/get-started/overview.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/parallelism-guide.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/megatron_fsdp.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/megatron_rl.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/multi_token_prediction.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/multi_latent_attention.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/moe.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/context_parallel.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/user-guide/features/dist_optimizer.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/docs/api-guide/router_replay.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/training/arguments.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/model_parallel_config.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/fp8_utils.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/optimizer/emerging_optimizers.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/optimizer/muon.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/experimental_attention_variant/dsa.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/models/gpt/experimental_attention_variant_module_specs.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/ssm/gated_delta_net/gdn.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/moe/router.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/transformer_config.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/multi_latent_attention.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/rl/README.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/rl/rl_utils.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/README.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/apis/serve_config.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/megatron/core/inference/contexts/kv_block_allocator.py>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/examples/megatron_fsdp/README.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/examples/post_training/modelopt/README.md>
- <https://raw.githubusercontent.com/NVIDIA/Megatron-LM/5be9626709af2722333bf54797c954c09edeada3/LICENSE>
