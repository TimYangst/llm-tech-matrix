# verl v0.9.0

> 中文版：[verl-v0.9.0.zh.md](./verl-v0.9.0.zh.md)

*Engine schema version: 2*

## Overview

| Field | Value |
|---|---|
| Repository | https://github.com/verl-project/verl |
| License | Apache-2.0 |
| Release tag | `v0.9.0` |
| Commit | `483b8a009ba3a97563edee3a19887e4862b8094a` |
| Release date | 2026-08-14 |
| Snapshot date | 2026-09-13 |
| Roles | `training`, `rl_post_training` |
| Hardware | NVIDIA GPU (cuda), Ascend NPU (npu), AMD (naive weight sync) |

## Parallelism

| Dimension | Supported | Implementation | Notes | Evidence |
|---|---|---|---|---|
| Tensor | ✓ | megatron: tensor_model_parallel_size; torchtitan: tensor_parallel_size; automodel: tp_size | Training-side parallelism depends on the selected engine; FSDP/FSDP2 has no TP. | [megatron.yaml#L14](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml#L14) |
| Pipeline | ✓ | megatron: pipeline_model_parallel_size | The TorchTitan engine documents that pipeline parallelism is not yet supported. | [megatron.yaml#L23](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml#L23), [torchtitan_workers.rst#L12](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/torchtitan_workers.rst#L12) |
| Data | ✓ | fsdp: fsdp_size (FSDP/FSDP2 sharding); rollout data_parallel_size | — | [fsdp.yaml#L26](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/fsdp.yaml#L26) |
| Expert | ✓ | megatron: expert_model_parallel_size; veomni: expert_parallel_size | — | [megatron.yaml#L17](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml#L17), [veomni.yaml#L15](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/veomni.yaml#L15) |
| Context | ✓ | megatron: context_parallel_size | — | [megatron.yaml#L29](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml#L29) |
| Sequence | ✓ | fsdp: ulysses_sequence_parallel_size; veomni: ulysses_parallel_size; megatron: sequence_parallel | — | [fsdp.yaml#L45](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/fsdp.yaml#L45), [megatron.yaml#L32](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml#L32) |

## Training

**Mixed precision:** FP8 end-to-end is documented with FP8 training in Megatron (via Transformer Engine) and FP8 rollout in vLLM.

_Evidence:_ [fp8.md#L10](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/low_precision/fp8.md#L10)

**Quantization-aware training:** NVFP4 QAT: fake quantization during BF16 training (FSDP or Megatron), weights packed to NVFP4 W4A16 for vLLM rollout.

_Evidence:_ [nvfp4_qat.md#L5](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/low_precision/nvfp4_qat.md#L5)

**Checkpointing:** Checkpoint save/load contents are configurable (checkpoint.save_contents / load_contents).

_Evidence:_ [checkpoint.rst#L15](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/checkpoint.rst#L15)

**LoRA:** LoRA for RL algorithms such as PPO and GRPO.

_Evidence:_ [ppo_lora.rst#L6](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/ppo_lora.rst#L6)

**Workloads** (3): RL post-training, SFT, DPO

_Evidence:_ [README.md#L24](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/README.md#L24), [sft_trainer.py#L50](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/sft_trainer.py#L50), [engine_workers.rst#L138](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/engine_workers.rst#L138)

**Training backends** (7): `fsdp`, `fsdp2`, `megatron`, `automodel`, `veomni`, `torchtitan`, `mindspeed_megatron`

_Evidence:_ [engine_workers.rst#L195](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/engine_workers.rst#L195), [engine_workers.rst#L145](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/engine_workers.rst#L145), [base.py#L337](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/engine/base.py#L337)

**Optimizers** (2): `AdamW (fsdp / veomni optim defaults)`, `adam / sgd / muon (megatron)`

_Evidence:_ [fsdp.yaml#L5](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/fsdp.yaml#L5), [veomni.yaml#L4](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/veomni.yaml#L4), [megatron.yaml#L25](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/megatron.yaml#L25)

_Notes:_ Training engines are resolved at runtime from actor/critic `strategy` through EngineRegistry, keyed by (model_type, backend, device). The VeOmni engine imports the external `veomni` package. Megatron defaults to Megatron-Bridge (`use_mbridge: True`). Megatron Lite's glue lives outside the repository.

## RL post-training

**Weight sync:** Colocated actor/rollout reshards through the 3D-HybridEngine (`hybrid_engine: true`). Weight transfer is pluggable via `rollout.checkpoint_engine.backend` (default naive, for colocated on-policy training; the others target disaggregated off-policy setups). delta_sharded is the only delta backend.

_Evidence:_ [README.md#L42](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/README.md#L42), [ppo_trainer.yaml#L56](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/ppo_trainer.yaml#L56), [rollout.yaml#L278](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/rollout/rollout.yaml#L278), [delta_weight_sync.md#L26](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/delta_weight_sync.md#L26)

**Routing replay:** MoE router replay modes disabled / R2 / R3: R2 records routes during actor log-prob computation; R3 records routes in the rollout backend and replays them in training. Rollout routing replay requires vLLM >= 0.22.0.

_Evidence:_ [actor.py#L57](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/config/actor.py#L57), [deepseek_v4_integration.rst#L69](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/deepseek_v4_integration.rst#L69), [vllm_async_server.py#L400](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/vllm_rollout/vllm_async_server.py#L400)

**Reward:** Function-based (verifiable) and model-based rewards; reward managers selected by name (default naive); reward models may be discriminative or generative. Reward Loop is the default reward computation implementation.

_Evidence:_ [reward.yaml#L26](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/reward/reward.yaml#L26), [reward.yaml#L19](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/reward/reward.yaml#L19), [reward_loop.rst#L13](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/reward_loop.rst#L13)

**Distillation:** On-policy distillation (OPD) via the `distillation` config (disabled by default; loss_mode k3 default), with forward-KL top-k and KL-family loss modes.

_Evidence:_ [distillation.yaml#L24](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/distillation/distillation.yaml#L24), [opd.md#L1](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/algo/opd.md#L1)

**Algorithms** (14): `gae`, `grpo`, `reinforce_plus_plus`, `reinforce_plus_plus_baseline`, `remax`, `rloo`, `opo`, `grpo_passk`, `gpg`, `rloo_vectorized`, `grpo_vectorized`, `optimal_token_baseline`, `tir_optimal_token_baseline`, `gdpo`

_Evidence:_ [core_algos.py#L88](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/ppo/core_algos.py#L88), [ppo_trainer.yaml#L74](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/ppo_trainer.yaml#L74)

**Policy losses** (12): `vanilla`, `dppo_tv`, `dppo_kl`, `gspo`, `sapo`, `gpg`, `clip_cov`, `kl_cov`, `geo_mean`, `dro`, `cispo`, `bypass_mode`

_Evidence:_ [core_algos.py#L1285](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/ppo/core_algos.py#L1285), [core_algos.py#L2412](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/ppo/core_algos.py#L2412)

**Rollout backends** (3): `vllm`, `sglang`, `trtllm`

_Evidence:_ [replica.py#L378](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/replica.py#L378), [rollout.yaml#L4](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/rollout/rollout.yaml#L4)

**Trainer modes** (3): `sync`, `colocate_async`, `separate_async`

_Evidence:_ [ppo_trainer.yaml#L227](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/ppo_trainer.yaml#L227), [ppo_trainer.yaml#L222](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/ppo_trainer.yaml#L222)

**Weight-sync backends** (7): `naive`, `nccl`, `hccl`, `nixl`, `kimi_ckpt_engine`, `mooncake`, `delta_sharded`

_Evidence:_ [README.md#L17](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/checkpoint_engine/README.md#L17), [README.md#L22](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/checkpoint_engine/README.md#L22), [delta_weight_sync.md#L26](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/delta_weight_sync.md#L26)

_Notes:_ Algorithms are the AdvantageEstimator enum values; DAPO is composed from a `dapo` reward manager plus group filtering and clip settings rather than an estimator. Policy losses are the @register_policy_loss names. HF rollout exists (HFRollout) but is not in the rollout replica registry. Trainer modes are the v1 trainer (`trainer.use_v1: true`); one-step-off and fully-async trainers are experimental.

## Integrations

| Name | Relation | Version constraints | Notes | Evidence |
|---|---|---|---|---|
| vLLM ([`vllm-v0.29.0`](./vllm-v0.29.0.md)) | `rollout_backend` | setup.py extra: vllm>=0.18.0<br>docs/start/install.rst: vllm 0.18.0 and later versions are supported<br>docker/Dockerfile.stable.vllm: VLLM_VERSION=0.24.0<br>vllm_async_server.py: rollout routing replay requires vLLM >= 0.22.0 | The tracked snapshot vllm-v0.29.0 satisfies the >=0.18.0 floor but is newer than the Docker-tested 0.24.0. | [setup.py#L55](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/setup.py#L55), [install.rst#L25](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/start/install.rst#L25), [Dockerfile.stable.vllm#L13](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docker/Dockerfile.stable.vllm#L13), [vllm_async_server.py#L398](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/vllm_rollout/vllm_async_server.py#L398) |
| SGLang ([`sglang-v0.5.19`](./sglang-v0.5.19.md)) | `rollout_backend` | setup.py extra: sglang[srt,openai]==0.5.8<br>docker/Dockerfile.stable.sglang: lmsysorg/sglang:v0.5.12<br>docs/workers/sglang_worker.rst: 'Currently 0.4.8' (stale)<br>async_sglang_server.py: weights CPU backup path needs sglang >= 0.5.6 | Sources disagree (0.5.8 pin, 0.5.12 Docker base, 0.4.8 in docs); none matches the tracked snapshot sglang-v0.5.19. | [setup.py#L59](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/setup.py#L59), [Dockerfile.stable.sglang#L4](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docker/Dockerfile.stable.sglang#L4), [sglang_worker.rst#L27](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/sglang_worker.rst#L27), [async_sglang_server.py#L390](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/sglang_rollout/async_sglang_server.py#L390) |
| TensorRT-LLM | `rollout_backend` | setup.py extra: tensorrt-llm>=1.2.0rc6 | — | [setup.py#L56](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/setup.py#L56) |
| VeOmni ([`veomni-v0.1.12`](./veomni-v0.1.12.md)) | `training_backend` | — | The `veomni` engine imports the external veomni package (registered for language_model and value_model on cuda and npu). No version pin was found in setup.py. | [transformer_impl.py#L25](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/engine/veomni/transformer_impl.py#L25), [transformer_impl.py#L865](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/engine/veomni/transformer_impl.py#L865) |
| Megatron-Bridge / Megatron | `training_backend` | — | The megatron engine uses Megatron-Bridge by default; MTP training is only supported on the Megatron-Bridge + Megatron combination. | [megatron.yaml#L98](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml#L98), [mtp.md#L11](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/mtp.md#L11) |

## Model support

| Architecture | Model records | Support | Documented | Features | Spec. decoding | Evidence |
|---|---|---|---|---|---|---|
| `DeepseekV3ForCausalLM` | [`deepseek-v3`](../deepseek-v3.md), [`kimi-k2-thinking`](../kimi-k2-thinking.md) | `model_specific` | _unknown_ | — | — | [registry.py#L123](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L123), [registry.py#L87](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L87), [patch.py#L23](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/utils/vllm/patch.py#L23) |
| `DeepseekV32ForCausalLM` | [`deepseek-v3.2-exp`](../deepseek-v3.2-exp.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |
| `DeepseekV4ForCausalLM` | [`deepseek-v4-pro`](../deepseek-v4-pro.md), [`deepseek-v4-flash`](../deepseek-v4-flash.md), [`deepseek-v4-flash-0731`](../deepseek-v4-flash-0731.md) | `model_specific` | ✓ | — | — | [deepseek_v4_integration.rst#L6](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/deepseek_v4_integration.rst#L6), [vllm_fp4_utils.py#L51](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/utils/vllm/vllm_fp4_utils.py#L51) |
| `DeepseekV41ForCausalLM` | [`deepseek-v4.1-flash`](../deepseek-v4.1-flash.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |
| `Glm4MoeForCausalLM` | [`glm-4.7`](../glm-4.7.md) | `model_specific` | _unknown_ | — | — | [registry.py#L130](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L130), [registry.py#L87](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L87) |
| `GlmMoeDsaForCausalLM` | [`glm-5`](../glm-5.md), [`glm-5.1`](../glm-5.1.md), [`glm-5.2`](../glm-5.2.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |
| `Glm5NextForConditionalGeneration` | [`glm-5.3-flash`](../glm-5.3-flash.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |
| `KimiK25ForConditionalGeneration` | [`kimi-k2.5`](../kimi-k2.5.md), [`kimi-k2.6`](../kimi-k2.6.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |
| `KimiK3ForConditionalGeneration` | [`kimi-k3`](../kimi-k3.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |
| `Qwen3ForCausalLM` | [`qwen3-32b`](../qwen3-32b.md) | `model_specific` | _unknown_ | — | — | [registry.py#L127](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L127), [registry.py#L87](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L87) |
| `Qwen3MoeForCausalLM` | [`qwen3-235b-a22b`](../qwen3-235b-a22b.md) | `model_specific` | _unknown_ | — | — | [patch.py#L44](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/utils/vllm/patch.py#L44), [registry.py#L128](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L128) |
| `Qwen3_5ForConditionalGeneration` | [`qwen3.5-27b`](../qwen3.5-27b.md), [`qwen3.6-27b`](../qwen3.6-27b.md), [`qwen3.8-27b`](../qwen3.8-27b.md) | `model_specific` | _unknown_ | — | — | [monkey_patch.py#L497](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/transformers/monkey_patch.py#L497) |
| `Qwen3_5MoeForConditionalGeneration` | [`qwen3.5-35b-a3b`](../qwen3.5-35b-a3b.md), [`qwen3.6-35b-a3b`](../qwen3.6-35b-a3b.md) | `model_specific` | _unknown_ | — | — | [monkey_patch.py#L497](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/transformers/monkey_patch.py#L497) |
| `Qwen3_5MoeForCausalLM` | [`qwen3.8-2.4t-a95b`](../qwen3.8-2.4t-a95b.md) | `model_specific` | _unknown_ | — | — | [patch.py#L72](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/utils/vllm/patch.py#L72), [registry.py#L129](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py#L129) |
| `Qwen4ExpForConditionalGeneration` | [`qwen3.8-flash-next`](../qwen3.8-flash-next.md) | `not_found` | ✗ | — | — | [README.md](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md), [483b8a009ba3a97563edee3a19887e4862b8094a](https://github.com/verl-project/verl/tree/483b8a009ba3a97563edee3a19887e4862b8094a) |

### Row notes

- **`DeepseekV3ForCausalLM`** — No FSDP-specific patch; FSDP/FSDP2 load HF implementations directly.
- **`DeepseekV32ForCausalLM`** — The architecture string appears nowhere in the repository at this commit (checked across the full tree).
- **`DeepseekV4ForCausalLM`** — The integration guide covers DeepSeek-V4-Flash with a Megatron actor and vLLM rollout: dense FP8 (E4M3 + UE8M0) and packed FP4 expert weight sync, R2/R3 routing replay, hash-router layers. The architecture string itself appears nowhere; support is keyed on model_type.
- **`DeepseekV41ForCausalLM`** — Not present at this commit; verl v0.9.0 predates the model (2026-08-14 vs 2026-09-10).
- **`Glm4MoeForCausalLM`** — Only the legacy Megatron registry names it.
- **`GlmMoeDsaForCausalLM`** — The architecture string appears nowhere in the repository at this commit.

## Technique support

| Glossary entry | Implementation | Flags | Since | Evidence |
|---|---|---|---|---|
| [grpo](../../../docs/glossary/grpo.md) | AdvantageEstimator 'grpo' (plus grpo_passk and grpo_vectorized); selected with algorithm.adv_estimator. | `algorithm.adv_estimator=grpo` | _unknown_ | [core_algos.py#L98](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/ppo/core_algos.py#L98), [ppo_trainer.yaml#L74](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/ppo_trainer.yaml#L74) |
| [on-policy-distillation](../../../docs/glossary/on-policy-distillation.md) | `distillation` config with teacher-based KL losses (k3 default; forward_kl_topk and KL-family modes), usable with async generation. | `distillation.enabled=true` | _unknown_ | [distillation.yaml#L14](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/distillation/distillation.yaml#L14), [opd.md#L1](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/algo/opd.md#L1) |
| [mtp](../../../docs/glossary/mtp.md) | MtpConfig (enable / enable_train / enable_rollout): MTP training on Megatron-Bridge + Megatron, MTP speculative rollout in vLLM (method=mtp) or SGLang (EAGLE). | `actor_rollout_ref.model.mtp.enable=true` | _unknown_ | [model.py#L30](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/config/model.py#L30), [mtp.md#L11](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/mtp.md#L11) |
| [muon](../../../docs/glossary/muon.md) | Megatron engine optimizer 'muon' through Megatron-Core's emerging_optimizers path (tensor-parallel-aware Muon). | `optim: muon (megatron)` | _unknown_ | [megatron.yaml#L25](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/megatron.yaml#L25) |
| [fp8-mixed-precision](../../../docs/glossary/fp8-mixed-precision.md) | FP8 end-to-end: FP8 training in Megatron via Transformer Engine plus FP8 rollout in vLLM. | — | _unknown_ | [fp8.md#L10](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/low_precision/fp8.md#L10), [fp8.md#L163](https://github.com/verl-project/verl/blob/483b8a009ba3a97563edee3a19887e4862b8094a/docs/low_precision/fp8.md#L163) |

- **mtp** — The guide names mimo-7B-RL, Qwen-next and DeepSeek-series models, and advises against enabling MTP acceleration during inference for now.
- **muon** — Megatron engine only; the FSDP and VeOmni optim defaults are AdamW.

## Open questions

- SGLang version is contradictory across sources: setup.py pins sglang[srt,openai]==0.5.8, the stable Docker image is lmsysorg/sglang:v0.5.12, and docs/workers/sglang_worker.rst still says 'Currently 0.4.8'. None matches the tracked sglang-v0.5.19 snapshot, so verl v0.9.0 + SGLang v0.5.19 is an untested pairing as far as these sources go.
- vLLM compatibility is a floor (>=0.18.0) plus a Docker-tested 0.24.0; the tracked vllm-v0.29.0 satisfies the floor but is five minor versions past the tested build.
- Release notes vs code on PD rollout: the notes advertise `rollout.name=vllm_pd`, but PD is selected with rollout.disaggregation.enabled and a test asserts 'vllm_pd' is not in the rollout replica registry ('sglang_pd/vllm_pd were dropped').
- Megatron model coverage: the in-repo mcore SupportedModel enum sits under a 'deprecated code' banner and the default path is Megatron-Bridge AutoBridge, so which architectures the Megatron engine actually supports is decided upstream in Megatron-Bridge, outside these sources. The mcore entries recorded as model_specific are therefore legacy signals.
- DeepSeek-V4 support is keyed on model_type 'deepseek_v4' rather than the architecture string; the row is joined through the architecture only because every DeepSeek-V4 record's config uses that model_type.
- FSDP/FSDP2 load any HF implementation the installed transformers (pinned >=5.5.3,!=5.6.0,<5.11) can load, so `not_found` rows (GLM-5.x, Kimi K2.5/K3, Qwen3.8-Flash-Next, DeepSeek-V3.2/V4.1) may still run on the generic path; whether that transformers range includes those architectures is not assessed here.
- NVFP4 QAT is documented, but the fp4-qat glossary entry describes the MXFP4 recipe used by DeepSeek-V4/Kimi, so it is not asserted as a technique edge. DSpark does not appear anywhere at this commit.
- Megatron Lite (mlite) is documented but its glue lives outside the repository and it is not in EngineRegistry, so it is not listed as a backend.

## Sources

- <https://api.github.com/repos/verl-project/verl/releases/tags/v0.9.0>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/README.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/index.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/setup.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docker/Dockerfile.stable.vllm>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docker/Dockerfile.stable.sglang>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docker/Dockerfile.stable.trtllm>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/start/install.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/sglang_worker.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/trtllm_worker.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/engine_workers.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/workers/torchtitan_workers.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/ppo/core_algos.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/ppo_trainer.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/rollout/rollout.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/replica.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/base.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/config/rollout.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/vllm_rollout/vllm_async_server.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/rollout/sglang_rollout/async_sglang_server.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/engine/base.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/megatron.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/fsdp.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/veomni.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/torchtitan.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/engine/automodel.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/fsdp.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/megatron.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/optim/veomni.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/ppo/v1/trainer_base.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/checkpoint_engine/README.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/delta_weight_sync.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/config/actor.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/reward/reward.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/reward_loop.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/config/distillation/distillation.yaml>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/algo/opd.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/algo/dapo.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/reward_manager/dapo.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/README.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/fsdp_extension.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/mcore/registry.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/models/transformers/monkey_patch.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/utils/vllm/patch.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/utils/vllm/vllm_fp4_utils.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/config/model.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/deepseek_v4_integration.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/mtp.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/megatron_lite_backend.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/low_precision/fp8.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/low_precision/nvfp4_qat.md>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/workers/engine/veomni/transformer_impl.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/tests/workers/rollout/test_pd_disaggregation.py>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/checkpoint.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/docs/advance/ppo_lora.rst>
- <https://raw.githubusercontent.com/verl-project/verl/483b8a009ba3a97563edee3a19887e4862b8094a/verl/trainer/sft_trainer.py>
