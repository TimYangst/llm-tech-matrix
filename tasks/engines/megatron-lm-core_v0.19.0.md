# Megatron-LM core_v0.19.0

Slug: `megatron-lm-core_v0.19.0`
Engine: `megatron-lm` (upstream `NVIDIA/Megatron-LM`: Megatron Core library plus the Megatron-LM reference scripts)
Tag: `core_v0.19.0` → commit `5be9626709af2722333bf54797c954c09edeada3` (lightweight tag on a release branch, not an ancestor of `main`; published 2026-08-19)
Snapshot: 2026-09-13 (2026-Q3, phase E5)
Roles: `training`, `rl_post_training`, `inference` (primary role first)
Status: `extracted`

## Sources

Authoritative list: `data/sources/engines/megatron-lm-core_v0.19.0/manifest.json` (34 assets):

- README, LICENSE, `pyproject.toml`, the release notes.
- `megatron/training/arguments.py` (the CLI surface: parallelism, precision, optimizers, RL,
  inference), `model_parallel_config.py`, `transformer_config.py`, `fp8_utils.py`.
- Technique code: the DSA attention variant and its module specs, GatedDeltaNet, the MoE router,
  MLA, the Emerging-Optimizers bridge and Muon.
- Megatron-RL (`megatron/rl/README.md`, `rl_utils.py`) and the Megatron Core inference README,
  `ServeConfig` and KV block allocator.
- User-guide pages: parallelism, Megatron-FSDP, Megatron-RL, MTP, MLA, MoE, context parallel,
  distributed optimizer; the model list (`docs/models/llms.md`) and router replay design doc.
- Examples: Megatron-FSDP (DeepSeek-V3) and ModelOpt (support matrix).

The local `../Megatron-LM` clone tracks upstream `NVIDIA/Megatron-LM`, so absence was verified
with `git grep` against the tag commit object across the whole tree.

## Findings

- **No model registry.** Megatron Core models are generic, composable specs (GPTModel, the new
  HybridModel, Mamba, T5, BERT, MIMO); converting HF checkpoints is delegated to Megatron-Bridge.
  None of our 15 HF architecture strings appears anywhere at the tag. The only model-level
  signals are documentation, recorded as `model_specific`:
  - DeepSeek-V3 (and Kimi K2 Thinking by architecture): a Megatron-FSDP 671B example and the
    ModelOpt DeepSeek-R1 / Kimi-K2-Instruct configs.
  - Qwen3 and Qwen3-MoE: ModelOpt support-matrix rows.
  - Everything else is `delegated` to `megatron-bridge-v0.6.0` (engine schema v3, added for this
    snapshot): the docs send HF conversion to Megatron-Bridge, and a whole-tree `git grep`
    confirms no in-repo mapping. Synthesis shows Bridge's support through the delegation and
    never counts these rows as missing.
- **DeepSeek-V4 is dev-branch only.** The 0.19.0 notes say DeepSeek-V4 "migrated to HybridModel
  on the `dev` branch"; `deepseek_v4`, CSA/HCA and mHC do not appear in `megatron/` at the tag.
- **Techniques that are in the release:** DSA (cuDNN and TileLang fused kernels, CP/THD,
  indexer loss), IndexShare (`index_topk_freq > 1`), MLA (now in HybridModel), MTP, Muon (via
  Emerging-Optimizers, TP-aware), GatedDeltaNet, a Quantile Balancing router (aux-loss-free
  routing with a different bias estimator from DeepSeek-V3's), GRPO, TE block-wise FP8, and
  EAGLE3 training through ModelOpt.
- **Three roles, uneven maturity.**
  - Training is the core: DDP, distributed optimizer, Megatron-FSDP (ZeRO-1/2/3 strategies),
    FSDP2; TP / PP / EP (DeepEP, HybridEP, new NCCL EP) / CP / SP; FP16 / BF16 / FP8 / FP4.
  - Megatron-RL has GRPO only, with refit backends nccl / gloo / nvshmem. The docs aim it at
    research teams and point production users to NeMo RL.
  - The inference engine has an OpenAI-compatible HTTP server, dynamic batching, block KV cache,
    prefix caching and MTP; disaggregation is "foundations" only.
- **License mismatch.** LICENSE is BSD-3-Clause for NVIDIA code; the README badge says Apache.

## Cross-engine notes (E5)

- verl's Megatron engine and Megatron-Bridge's DeepSeek-V4 recipes both depend on Megatron Core
  code that no Megatron-LM release contains yet.
- Megatron-Bridge v0.6.0 (released the same day) pins Megatron-LM as a submodule at a `main`
  commit (`cd4afff`, 2026-07-25), not this tag. See
  [`megatron-bridge-v0.6.0.md`](./megatron-bridge-v0.6.0.md).
- IndexShare now has three engine implementations of the GLM-5.2 idea: vLLM (`--hf-overrides`),
  SGLang (from config), and Megatron Core (training side, surfaced by Megatron-Bridge).

## Open questions

See the record's `open_questions`. Worth tracking:

- **Delegation is responsibility, not compatibility.** Bridge v0.6.0 pins a Megatron-LM `main`
  commit, and its DeepSeek-V4 path needs `dev`; a `delegated` row pointing at a registered
  Bridge row does not mean this release can train the model.
- **Next snapshot:** check whether DeepSeek-V4 (HybridModel) reaches a `core_v0.20.x` release.
