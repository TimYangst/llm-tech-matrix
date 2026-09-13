# verl v0.9.0

Slug: `verl-v0.9.0`
Engine: `verl` (upstream `verl-project/verl`; the local `../verl` is a fork and was not used)
Tag: `v0.9.0` → commit `483b8a009ba3a97563edee3a19887e4862b8094a` (lightweight tag, published 2026-08-14)
Snapshot: 2026-09-13 (2026-Q3, phase E3)
Roles: `training`, `rl_post_training`
Status: `extracted`

## Sources

Authoritative list: `data/sources/engines/verl-v0.9.0/manifest.json` (56 assets). The asset groups:

- Algorithm registries (`core_algos.py`) and the trainer, rollout, engine, optimizer, reward and
  distillation config YAMLs.
- The rollout replica registry, and rollout servers with runtime version gates.
- Version pins: `setup.py` and the stable Dockerfiles.
- Model-specific code: the FSDP monkey patch, the vLLM MoE patch, the legacy Megatron registry
  and the DeepSeek-V4 FP4 utilities.
- Design docs: DeepSeek-V4 integration, MTP, delta weight sync, FP8, NVFP4 QAT, engine workers.

**How absence was verified:** the local clone is a fork without this commit, so a codeload tarball of the
commit was unpacked in the session scratchpad and grepped across the full tree. The committed
evidence for `not_found` rows is `verl/models/README.md` (the generic-FSDP statement) plus the
repository tree at the commit.

## What E3 needed from the schema (engine schema v2)

- **`training` and `rl` subobjects.** verl documents both an RL loop and SFT / DPO training on
  the same engines, so it claims both roles.
- **`support` instead of `in_native_registry`.** verl has no model registry. FSDP/FSDP2 load any
  HF implementation. What it does have is code keyed on `model_type`: `deepseek_v4` FP4/FP8 weight
  sync, and Qwen3.5 FSDP patches. A boolean would have shown "supports nothing".
- **`integrations[].version_constraints`.** verl's rollout-engine requirements come from several
  sources that disagree with one another.

## Findings

- **Rollout pins vs our inference snapshots.**
  - vLLM: `setup.py` floor `>=0.18.0` and a Docker-tested 0.24.0. A runtime gate needs ≥0.22.0 for
    rollout routing replay. `vllm-v0.29.0` meets the floor but is untested.
  - SGLang: three sources, three versions — `setup.py` 0.5.8, the Docker base v0.5.12, and the
    docs "Currently 0.4.8". None is `sglang-v0.5.19`.
- **Model coverage is backend-shaped.**
  - DeepSeek-V4 support means DeepSeek-V4-Flash with a **Megatron** actor and a **vLLM** rollout:
    FP8 dense and FP4 expert weight sync, plus R2/R3 routing replay. It is keyed on model_type;
    the architecture string never appears.
  - Qwen3.5 dense and MoE have FSDP patches.
  - DeepSeek-V3, GLM-4.7, Qwen3 and Qwen3-MoE appear only in the deprecated Megatron `mcore` enum
    or the vLLM MoE weight-loading patch.
  - GLM-5.x, Kimi K2.5/K3, DeepSeek-V3.2/V4.1, GLM-5.3-Flash and Qwen3.8-Flash-Next are
    `not_found`. They may still run through generic FSDP if the pinned transformers supports
    them.
- **RL surface.**
  - 14 advantage estimators and 12 policy losses.
  - Rollout backends: vLLM, SGLang and TensorRT-LLM.
  - Three v1 trainer modes: sync, colocate_async and separate_async.
  - Seven weight-sync backends. `delta_sharded` is the only delta backend, and it is scoped to
    disaggregated setups with SGLang BF16.
  - OPD is supported, and so are generative reward models.
- **Techniques asserted:**
  - `grpo`
  - `on-policy-distillation`
  - `mtp` (Megatron-Bridge + Megatron only)
  - `muon` (Megatron only)
  - `fp8-mixed-precision` (FP8 end-to-end with Megatron + vLLM)
- **Not asserted:**
  - NVFP4 QAT: `fp4-qat` describes the MXFP4 recipe.
  - DSA: kernel handling lives in Megatron.
  - DSpark: absent from the whole tree.

## Open questions

See the record's `open_questions`. Worth tracking:

- **Release notes vs code.** The release notes advertise `rollout.name=vllm_pd`, but the code
  selects PD with `rollout.disaggregation.enabled`, and a test asserts `vllm_pd` was dropped.
- **Megatron coverage is decided upstream in Megatron-Bridge.** The in-repo `mcore` enum is
  deprecated.
- **Megatron Lite's glue lives outside the repository**, so it is not a listed backend.
