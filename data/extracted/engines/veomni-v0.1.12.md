# VeOmni v0.1.12

> 中文版：[veomni-v0.1.12.zh.md](./veomni-v0.1.12.zh.md)

*Engine schema version: 2*

## Overview

| Field | Value |
|---|---|
| Repository | https://github.com/ByteDance-Seed/VeOmni |
| License | Apache-2.0 |
| Release tag | `v0.1.12` |
| Commit | `fd99abfda9ef4d9d485f0dae14841de88d30963d` |
| Release date | 2026-09-09 |
| Snapshot date | 2026-09-13 |
| Roles | `training` |
| Hardware | NVIDIA GPU, AMD ROCm (through PyTorch's HIP backend), Ascend NPU, Cambricon MLU |

## Parallelism

| Dimension | Supported | Implementation | Notes | Evidence |
|---|---|---|---|---|
| Tensor | ✗ | tp_size (field exists) | Configuration asserts tp_size == 1: 'Tensor parallel size not supported yet.' | [arguments_types.py#L889](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L889) |
| Pipeline | ✗ | pp_size (field exists) | Configuration asserts pp_size == 1: 'Pipeline parallel size not supported yet.' | [arguments_types.py#L890](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L890) |
| Data | ✓ | fsdp_config.fsdp_mode: ddp \| fsdp2 (FSDP1 removed) | — | [arguments_types.py#L444](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L444) |
| Expert | ✓ | ep_size, with per-model parallel_plan.py shard plans; EP + FSDP2 | — | [arguments_types.py#L561](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L561), [ep_fsdp2.md#L5](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/key_features/ep_fsdp2.md#L5) |
| Context | ✓ | cp_size (all-gathered KV, query-axis sharding) | DeepSeek-V4 only (CONTEXT_PARALLEL_MODEL_TYPES allow-list) and GPU-only in this release. | [arguments_types.py#L593](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L593), [auto.py#L50](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/auto.py#L50), [auto.py#L95](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/auto.py#L95) |
| Sequence | ✓ | ulysses_size (DeepSpeed-Ulysses), optional Async Ulysses | — | [arguments_types.py#L585](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L585), [ulysses.md#L311](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/key_features/ulysses.md#L311) |

## Training

**Mixed precision:** FSDP2 MixedPrecisionConfig: param_dtype bfloat16 and reduce_dtype float32 by default.

_Evidence:_ [arguments_types.py#L413](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L413)

**Quantization-aware training:** qat_implementation none | fp8_blockwise: a DeepSeek-V4 quantization-aware training recipe (block-wise FP8 fake quantization; routed experts use FP4 groups when the checkpoint's expert dtype is FP4).

_Evidence:_ [arguments_types.py#L1224](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L1224), [arguments.md#L196](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/arguments.md#L196)

**Checkpointing:** Torch Distributed Checkpoint (dcp.save / dcp.async_save / dcp.load).

_Evidence:_ [dcp_checkpointer.py#L781](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/checkpoint/dcp_checkpointer.py#L781)

**LoRA:** VeOmni's own PEFT-free LoRA stack (veomni.lora) with MoE-LoRA and EP-LoRA, FSDP2-native.

_Evidence:_ [lora.md#L8](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/key_features/lora.md#L8)

**Kernels:** Kernel selection is config-driven (OpsImplementationConfig) through a kernel registry: Liger-Kernel defaults for cross-entropy / RMSNorm / SwiGLU / RoPE on GPU; fused MoE (Triton group-GEMM, Quack, NPU, MLU); DSA indexer and attention kernels (cuDNN / FlashMLA-cuDNN for GLM-DSA, TileLang for DeepSeek-V4); tile-kernels mHC.

_Evidence:_ [kernel_selection.md#L21](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L21), [kernel_selection.md#L18](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L18), [kernel_registry.py#L180](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/ops/kernel_registry.py#L180), [kernel_selection.md#L166](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L166)

**Workloads** (4): pre-training, post-training, DPO, RL trainer backend

_Evidence:_ [README.md#L20](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/README.md#L20), [train_text_dpo.py#L2](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/tasks/train_text_dpo.py#L2), [base_rl_trainer.py#L16](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/trainer/base_rl_trainer.py#L16)

**Training backends** (2): `fsdp2`, `ddp`

_Evidence:_ [arguments_types.py#L444](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L444), [README.md#L41](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/README.md#L41)

**Optimizers** (3): `adamw`, `anyprecision_adamw`, `muon`

_Evidence:_ [arguments_types.py#L73](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L73)

_Notes:_ Models become supported through registries keyed by HF model_type (MODELING_REGISTRY etc.) plus patchgen-generated modeling files instead of runtime monkey patches. The RL trainer is a backend for RL frameworks; the RL algorithms themselves live in verl.

## Integrations

| Name | Relation | Version constraints | Notes | Evidence |
|---|---|---|---|---|
| verl ([`verl-v0.9.0`](./verl-v0.9.0.md)) | `used_by` | — | VeOmni exposes contracts that verl's VeOmni engine consumes: top-k forward-KL distillation without materializing student logits, chunked fused log-probs mirroring verl's FusedLinearForPPOFunction, and R2/R3 MoE router replay hooks. VeOmni does not import verl. | [verl_topk_distill_integration.md#L54](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/verl_topk_distill_integration.md#L54), [chunk_logprobs.py#L25](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/ops/kernels/cross_entropy/chunk_logprobs.py#L25), [moe_router_replay.py#L21](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/utils/moe_router_replay.py#L21) |
| Hugging Face Transformers | `other` | pyproject.toml default group: transformers==5.9.0 | Modeling code is generated from transformers' modeling files (patchgen), so the transformers version is load-bearing. | [pyproject.toml#L169](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/pyproject.toml#L169), [patchgen.md#L3](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/patchgen.md#L3) |
| Liger-Kernel | `kernel_library` | — | Default GPU implementation for cross-entropy, RMSNorm, SwiGLU and RoPE. | [pyproject.toml#L71](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/pyproject.toml#L71), [kernel_selection.md#L21](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L21) |
| tile-kernels | `kernel_library` | pyproject.toml gpu extra: tile-kernels==1.0.0 | Provides the DeepSeek-V4 mHC implementation. | [pyproject.toml#L81](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/pyproject.toml#L81), [kernel_selection.md#L166](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L166) |

## Model support

| Architecture | Model records | Support | Documented | Features | Spec. decoding | Evidence |
|---|---|---|---|---|---|---|
| `DeepseekV3ForCausalLM` | [`deepseek-v3`](../deepseek-v3.md), [`kimi-k2-thinking`](../kimi-k2-thinking.md) | `registered` | _unknown_ | — | — | [__init__.py#L18](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v3/__init__.py#L18) |
| `DeepseekV32ForCausalLM` | [`deepseek-v3.2-exp`](../deepseek-v3.2-exp.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |
| `DeepseekV4ForCausalLM` | [`deepseek-v4-pro`](../deepseek-v4-pro.md), [`deepseek-v4-flash`](../deepseek-v4-flash.md), [`deepseek-v4-flash-0731`](../deepseek-v4-flash-0731.md) | `registered` | ✓ | — | — | [__init__.py#L28](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v4/__init__.py#L28), [checkpoint_tensor_converter.py#L426](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v4/checkpoint_tensor_converter.py#L426), [deepseek_v4.yaml#L1](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/configs/text/deepseek_v4.yaml#L1) |
| `DeepseekV41ForCausalLM` | [`deepseek-v4.1-flash`](../deepseek-v4.1-flash.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |
| `Glm4MoeForCausalLM` | [`glm-4.7`](../glm-4.7.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |
| `GlmMoeDsaForCausalLM` | [`glm-5`](../glm-5.md), [`glm-5.1`](../glm-5.1.md), [`glm-5.2`](../glm-5.2.md) | `registered` | _unknown_ | — | — | [__init__.py#L5](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/glm_moe_dsa/__init__.py#L5), [glm_moe_dsa_gpu_patch_gen_config.py#L14](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/glm_moe_dsa/glm_moe_dsa_gpu_patch_gen_config.py#L14) |
| `Glm5NextForConditionalGeneration` | [`glm-5.3-flash`](../glm-5.3-flash.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |
| `KimiK25ForConditionalGeneration` | [`kimi-k2.5`](../kimi-k2.5.md), [`kimi-k2.6`](../kimi-k2.6.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |
| `KimiK3ForConditionalGeneration` | [`kimi-k3`](../kimi-k3.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |
| `Qwen3ForCausalLM` | [`qwen3-32b`](../qwen3-32b.md) | `registered` | _unknown_ | — | — | [__init__.py#L18](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3/__init__.py#L18) |
| `Qwen3MoeForCausalLM` | [`qwen3-235b-a22b`](../qwen3-235b-a22b.md) | `registered` | _unknown_ | — | — | [__init__.py#L37](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_moe/__init__.py#L37), [qwen3_moe_muon.yaml](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/configs/text/qwen3_moe_muon.yaml) |
| `Qwen3_5ForConditionalGeneration` | [`qwen3.5-27b`](../qwen3.5-27b.md), [`qwen3.6-27b`](../qwen3.6-27b.md), [`qwen3.8-27b`](../qwen3.8-27b.md) | `registered` | _unknown_ | — | — | [__init__.py#L24](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5/__init__.py#L24), [qwen3_5_gpu_patch_gen_config.py#L21](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5/qwen3_5_gpu_patch_gen_config.py#L21) |
| `Qwen3_5MoeForConditionalGeneration` | [`qwen3.5-35b-a3b`](../qwen3.5-35b-a3b.md), [`qwen3.6-35b-a3b`](../qwen3.6-35b-a3b.md) | `registered` | _unknown_ | — | — | [__init__.py#L46](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5_moe/__init__.py#L46) |
| `Qwen3_5MoeForCausalLM` | [`qwen3.8-2.4t-a95b`](../qwen3.8-2.4t-a95b.md) | `registered` | _unknown_ | — | — | [__init__.py#L74](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5_moe/__init__.py#L74) |
| `Qwen4ExpForConditionalGeneration` | [`qwen3.8-flash-next`](../qwen3.8-flash-next.md) | `not_found` | ✗ | — | — | [loader.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py), [__init__.py](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py) |

### Row notes

- **`DeepseekV32ForCausalLM`** — The architecture string appears nowhere at the commit (DeepSeek-V3.2 is only cited as the source of the indexer-loss equation).
- **`DeepseekV4ForCausalLM`** — The most extensive support in the tree: TileLang DSA indexer/attention, tile-kernels mHC, context parallelism (DeepSeek-V4 only), an indexer KL loss, FP8/FP4 QAT and a sample DeepSeek-V4-Flash-Base SFT config. MTP is explicitly not supported: the checkpoint converter drops MTP weights ('MTP not supported for now, ignore it').
- **`GlmMoeDsaForCausalLM`** — Patchgen description 'GLM-5 with GPU replacements' (cuDNN DSA indexer, FlashMLA-cuDNN attention). Unlike the DeepSeek and Qwen MoE packages, glm_moe_dsa ships no parallel_plan.py, so no expert-parallel shard plan at this commit.
- **`KimiK25ForConditionalGeneration`** — No Kimi model appears anywhere at the commit.
- **`Qwen3MoeForCausalLM`** — A Muon config exists for Qwen3-MoE (configs/text/qwen3_moe_muon.yaml).
- **`Qwen3_5MoeForCausalLM`** — Registered for the text-only qwen3_5_moe_text model_type, which the Qwen3.8-2.4T-A95B config declares.

## Technique support

| Glossary entry | Implementation | Flags | Since | Evidence |
|---|---|---|---|---|
| [muon](../../../docs/glossary/muon.md) | DistributedMuon (DTensor-aware, FSDP2 and MoE expert stacks) as a Muon + AdamW multi-optimizer; optional head-grouped orthogonalization ('Muon Split', GLM-5's variant). | `optimizer type: muon`<br>`muon_head_group_size` | _unknown_ | [arguments_types.py#L73](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L73), [muon.py#L15](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/optim/muon.py#L15), [basic_modules.md#L427](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/basic_modules.md#L427) |
| [dsa](../../../docs/glossary/dsa.md) | DSA indexer and sparse-attention kernels (cuDNN / FlashMLA-cuDNN for GLM-DSA, TileLang for DeepSeek-V4) plus a DeepSeek-V4 indexer KL loss following DeepSeek-V3.2 eq. (4). | `dsa_indexer_implementation`<br>`dsa_attention_implementation` | _unknown_ | [kernel_selection.md#L18](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L18), [deepseek_v4_indexer_loss.md#L9](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/deepseek_v4_indexer_loss.md#L9) |
| [mhc](../../../docs/glossary/mhc.md) | DeepSeek-V4 manifold-constrained Hyper-Connections via mhc_implementation eager \| tilelang (tile-kernels). | `mhc_implementation=tilelang` | _unknown_ | [arguments.md#L195](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/arguments.md#L195), [kernel_selection.md#L166](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md#L166) |
| [gated-deltanet](../../../docs/glossary/gated-deltanet.md) | Qwen3.5 GatedDeltaNet with varlen flash-linear-attention forward and Ulysses sequence parallelism. | — | _unknown_ | [qwen3_5_gpu_patch_gen_config.py#L21](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5/qwen3_5_gpu_patch_gen_config.py#L21) |
| [fp4-qat](../../../docs/glossary/fp4-qat.md) | DeepSeek-V4 QAT recipe (qat_implementation=fp8_blockwise): block-wise FP8 fake quantization, with routed experts in FP4 groups when the checkpoint's expert dtype is FP4. | `qat_implementation=fp8_blockwise` | _unknown_ | [arguments.md#L196](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/arguments.md#L196), [arguments_types.py#L1224](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py#L1224) |
| [on-policy-distillation](../../../docs/glossary/on-policy-distillation.md) | Chunked top-k forward-KL distillation loss for verl's distillation path, computed without materializing the [T, V] student logits. | — | _unknown_ | [verl_topk_distill_integration.md#L4](https://github.com/ByteDance-Seed/VeOmni/blob/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/verl_topk_distill_integration.md#L4) |

- **dsa** — The indexer loss requires TileLang indexer and attention with ulysses_size == 1 and cp_size == 1.
- **fp4-qat** — Training-time fake quantization for the DeepSeek-V4 FP4 expert format, requiring SM90+ CUDA GPUs.
- **on-policy-distillation** — Engine-side kernel support consumed by verl's VeOmni engine; the distillation loop itself lives in verl.

## Open questions

- VeOmni v0.1.12 pins transformers==5.9.0, while verl v0.9.0 requires transformers>=5.5.3,!=5.6.0,<5.11 — compatible on paper. The upstream main branch later moved to transformers 5.16.1 (after this tag).
- MTP is explicitly unsupported (DeepSeek-V4 checkpoint conversion drops MTP weights), while verl documents MTP training only on Megatron. A DeepSeek-V4 RL run with MTP therefore cannot use the VeOmni engine at these versions.
- GLM-5.x (GlmMoeDsaForCausalLM) is registered but has no expert-parallel shard plan and no example config in configs/, unlike the DeepSeek-V4 and Qwen MoE packages; whether EP works for it is not stated.
- The README claims AMD ROCm and Ascend NPU support; the ROCm doc says VeOmni contains no ROCm-specific code and runs through PyTorch's HIP backend, and several optimized kernels (DSA, mHC, QAT) require NVIDIA SM90+.
- VeOmni's own RL trainer is described as a trainer backend for RL frameworks; no RL algorithm implementation (PPO/GRPO loops) exists in VeOmni, so the rl_post_training role is not claimed. RL post-training with VeRL for omni models is listed as upcoming.
- MLA: DeepSeek-V4 sparse-MLA TileLang kernel modules exist in the tree but are not among this snapshot's sources, so mla is not asserted as a technique edge.

## Sources

- <https://api.github.com/repos/ByteDance-Seed/VeOmni/releases/tags/v0.1.12>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/README.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/pyproject.toml>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/_version.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/arguments/arguments_types.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/loader.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/auto.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v3/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v4/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v4/deepseek_v4_gpu_patch_gen_config.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v4/checkpoint_tensor_converter.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/deepseek_v4/parallel_plan.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/glm_moe_dsa/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/glm_moe_dsa/glm_moe_dsa_gpu_patch_gen_config.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_moe/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5/qwen3_5_gpu_patch_gen_config.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/models/transformers/qwen3_5_moe/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/patchgen.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/support_new_models/guide_and_checklist.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/kernel_selection.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/deepseek_v4_context_parallel.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/deepseek_v4_indexer_loss.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/verl_topk_distill_integration.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/design/fused_moe_kernels.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/ops/kernel_registry.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/ops/kernels/moe/__init__.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/ops/kernels/cross_entropy/chunk_logprobs.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/utils/moe_router_replay.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/trainer/base_rl_trainer.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/checkpoint/dcp_checkpointer.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/veomni/optim/muon.py>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/key_features/lora.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/key_features/ulysses.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/key_features/ep_fsdp2.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/hardware_support/get_started_npu.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/hardware_support/rocm/README.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/hardware_support/mlu/README.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/arguments.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/docs/usage/basic_modules.md>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/configs/text/deepseek_v4.yaml>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/configs/text/qwen3_moe_muon.yaml>
- <https://raw.githubusercontent.com/ByteDance-Seed/VeOmni/fd99abfda9ef4d9d485f0dae14841de88d30963d/tasks/train_text_dpo.py>
