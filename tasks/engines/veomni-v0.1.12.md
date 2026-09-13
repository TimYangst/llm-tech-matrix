# VeOmni v0.1.12

Slug: `veomni-v0.1.12`
Engine: `veomni` (upstream `ByteDance-Seed/VeOmni`)
Tag: `v0.1.12` → commit `fd99abfda9ef4d9d485f0dae14841de88d30963d` (lightweight tag, published 2026-09-09)
Snapshot: 2026-09-13 (2026-Q3, phase E3)
Roles: `training`
Status: `extracted`

## Sources

Authoritative list: `data/sources/engines/veomni-v0.1.12/manifest.json` (45 assets):

- README, `pyproject.toml` and `_version.py`.
- The typed config surface (`arguments_types.py`).
- The model loader registries and the per-model `__init__.py` registrations for every
  registered architecture.
- Patchgen configs for DeepSeek-V4, GLM-5 and Qwen3.5.
- The DeepSeek-V4 checkpoint converter and parallel plan.
- The kernel registry and MoE kernels.
- The verl-facing kernels and hooks.
- Design docs: kernel selection, context parallelism, indexer loss, verl distillation contract,
  patchgen.
- Hardware and LoRA docs, and sample configs.

**How absence was verified:** `git grep` against the commit object in the local upstream clone (read-only).
Seven architectures appear nowhere in the tree, and no file mentions "Kimi".

## Findings

- **Model support is registry-based.** A HF `model_type` resolves through `MODELING_REGISTRY` to
  patchgen-generated modeling code; there are no runtime monkey patches.
  - **Registered:** DeepSeek-V3, DeepSeek-V4, GLM-5.x (`glm_moe_dsa`), Qwen3, Qwen3-MoE, Qwen3.5
    dense and MoE, and Qwen3.5-MoE text-only (`qwen3_5_moe_text`, the Qwen3.8-2.4T model_type).
  - **Not found:** DeepSeek-V3.2 / V4.1, GLM-4.7, GLM-5.3-Flash, Kimi K2.5 / K3 and Qwen3.8-Flash-Next.
- **DeepSeek-V4 is the flagship integration:**
  - TileLang DSA indexer and sparse attention, and tile-kernels mHC;
  - context parallelism (allow-listed to `deepseek_v4`, GPU-only);
  - an indexer KL loss following DeepSeek-V3.2 eq. (4);
  - an FP8-blockwise QAT recipe with FP4 expert groups;
  - Muon.
  - **MTP is dropped at checkpoint load** ("MTP not supported for now, ignore it").
- **GLM-5.x is registered but thinner.** It has cuDNN / FlashMLA-cuDNN DSA kernels, but no
  `parallel_plan.py` (so no EP shard plan) and no sample config.
- **Parallelism:**
  - Supported: FSDP2 or DDP, Ulysses SP (including async), EP, and CP for DeepSeek-V4 only.
  - Refused: `tp_size` and `pp_size` must be 1 ("not supported yet").
- **Training stack:**
  - Optimizers: AdamW, anyprecision AdamW, and Muon (DistributedMuon, with head-grouped "Muon
    Split").
  - A PEFT-free LoRA with MoE-LoRA and EP-LoRA.
  - Torch DCP checkpointing, async save included.
  - Config-driven kernel registry: Liger defaults, and fused MoE for Triton, Quack, NPU and MLU.
- **Pins:** transformers==5.9.0 (the later 5.16.1 upgrade came after this tag), torch 2.11.0+cu130
  for GPU, and torch-npu 2.10.0 for NPU.
- **Relationship to verl** (`used_by`):
  - VeOmni does not import verl.
  - It exports contracts verl's VeOmni engine consumes: top-k forward-KL distillation without
    materializing student logits, chunked fused log-probs mirroring verl's
    `FusedLinearForPPOFunction`, and R2/R3 MoE router replay hooks.
  - Hence the `rl_post_training` role is **not** claimed; the RL algorithms live in verl.
- **Techniques asserted:** `muon`, `dsa`, `mhc`, `gated-deltanet`, `fp4-qat` (the DeepSeek-V4 QAT
  recipe) and `on-policy-distillation` (the verl distillation kernel).
- **MLA not asserted:** the sparse-MLA TileLang modules are not among the sources.

## Cross-engine notes (E3)

- **A DeepSeek-V4 RL run with MTP has one documented path:** verl + Megatron-Bridge / Megatron +
  vLLM. VeOmni cannot train MTP at this version.
- **transformers is compatible on paper.** VeOmni pins 5.9.0, inside verl's
  `>=5.5.3,!=5.6.0,<5.11`.
- **Hardware claims are softer than the README suggests:**
  - ROCm has no VeOmni-specific code and runs through PyTorch's HIP backend.
  - The optimized DSA, mHC and QAT paths need NVIDIA SM90+.
  - Cambricon MLU has kernels in-tree but is not named in the README's hardware line.
