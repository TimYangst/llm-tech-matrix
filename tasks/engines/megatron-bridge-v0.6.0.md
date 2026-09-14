# Megatron-Bridge v0.6.0

Slug: `megatron-bridge-v0.6.0`
Engine: `megatron-bridge` (upstream `NVIDIA-NeMo/Megatron-Bridge`)
Tag: `v0.6.0` → commit `51885cf132b2814188b6855c25a8588254274c2a` (lightweight tag, published 2026-08-19; NeMo Framework 26.08)
Snapshot: 2026-09-13 (2026-Q3, phase E5)
Roles: `training`
Status: `extracted`

## Sources

Authoritative list: `data/sources/engines/megatron-bridge-v0.6.0/manifest.json` (29 assets):

- README (supported models, functional matrix), `pyproject.toml`, `.gitmodules`, release notes.
- The registry: `conversion/model_bridge.py` (`register_bridge`) and `conversion/auto_bridge.py`.
- The bridges for our architectures: DeepSeek-V3 / V4, GLM-4.5 (GLM-4.7), GLM-5 (`glm_moe_dsa`),
  Kimi K2.5-VL, Qwen3, Qwen3-MoE, Qwen3.5 (text) and Qwen3.5-VL; the MLA provider.
- Training: optimizer recipe helpers, mixed precision, checkpointing, LoRA.
- Docs: parallelisms, RL-framework integration, model pages (DeepSeek-V4, GLM-5, GLM-4.7,
  Kimi K2.5-VL, Qwen3.5-VL, Qwen3-MoE) and the DeepSeek-V4 example README.

No local clone existed. A depth-1 clone of the tag was made in the session scratchpad (HEAD
verified against the tag SHA) and grepped across the full tree to verify absence.

## Findings

- **A real model registry.** Each bridge registers `@MegatronModelBridge.register_bridge(source=<HF architecture>)`. Ten of our 15 architectures are `registered`; not found: DeepSeek-V3.2,
  DeepSeek-V4.1, GLM-5.3-Flash, Kimi K3, Qwen3.8-Flash-Next.
- **GLM-5.2 is new in v0.6.0** (release notes): bridge and GB200/H100 recipes on the cuDNN DSA
  path, with IndexShare settings (`index_topk_freq`, `index_skip_topk_offset`) read from the HF
  config. The only `since_version` this snapshot records.
- **DeepSeek-V4 is registered but not releasable end to end.**
  - The bridge maps CSA/HCA hybrid attention, hash-routed MoE, mHC and MTP, and imports FP8 /
    FP8+MXFP4 checkpoints. V4-Flash logits verified (cosine 0.96-0.99); V4-Pro import / export /
    inference verified. SFT runs with MTP on or off.
  - Limits: TP must be 1; packed THD is unsupported on the sparse layers; MXFP8 and Muon SFT fail
    upstream; release notes still say "verification in progress".
  - The Megatron Core side is on Megatron-LM **dev** (tested dev commit `35f36c7c9dba` + PR #4839;
    SFT on main2dev `ed6b1f6`). The pinned submodule and `core_v0.19.0` both lack it.
- **Submodule pin, not a release pin.** `3rdparty/Megatron-LM` is at `cd4afff` (Megatron-LM
  `main`, 2026-07-25). The same-day Megatron-LM release `core_v0.19.0` sits on a release branch,
  so "Bridge 0.6.0 + Megatron-LM 0.19.0" is not a combination these sources describe.
- **Training only.** The README's functional matrix marks RL and RL LoRA as `N` (RL is NeMo
  RL's job), so `rl_post_training` is not claimed. `used_by` verl: the README says VeRL adopted
  Megatron-Bridge as its connector to Megatron Core and for LoRA.
- **Techniques asserted:** `dsa`, `indexshare`, `csa-hca`, `mhc`, `mtp`, `mla`,
  `gated-deltanet`, `muon`. Not asserted: `fp4-qat` (MXFP4 is dequantized on import, no QAT).

## Cross-engine notes (E5)

- **DeepSeek-V4 training engines now disagree on MTP.** Megatron-Bridge trains V4-Flash with MTP
  on (dev-branch Megatron Core); VeOmni drops MTP weights; verl documents MTP only on
  Megatron-Bridge + Megatron. The one MTP-capable V4 path therefore rests on unreleased Megatron
  Core code.
- **GLM-5.x:** Megatron-Bridge is the first training-side engine with a GLM-5.2-specific entry
  (verl has none; VeOmni registers `glm_moe_dsa` without a parallel plan).
- **Kimi K2.5:** first training-side snapshot to register `KimiK25ForConditionalGeneration`
  (VeOmni and verl: not found).
- verl's `Megatron-Bridge / Megatron` integration now links to this snapshot (no version is
  stated on the verl side).

## Open questions

See the record's `open_questions`. Worth tracking at the next snapshot: whether a Megatron-LM
release carries DeepSeek-V4, and whether Megatron-Bridge pins that release instead of a `main`
commit.
