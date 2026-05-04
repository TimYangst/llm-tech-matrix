# Qwen3-32B

Slug: `qwen3-32b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3-32b/manifest.json` (committed). This
section is for human notes — links registered, candidates considered, and rationale.

Registered sources (see manifest for sha256s):

- [x] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3-32B/raw/main/config.json`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2505.09388` (Qwen3 Technical Report, 2025-05-15)

Considered but excluded:

- Per-size sibling configs (Qwen3-0.6B/1.7B/4B/8B/14B). Qwen3 dense siblings share
  architecture and training recipe modulo width/depth — capturing the 32B flagship is
  representative for cross-vendor comparison. If size-scaling analysis becomes a need,
  add `metadata.size_variants` to the schema and re-source.
- Qwen3-Coder / Qwen3-VL / Qwen3-Omni — separate training branches; would be their own
  slugs, not source documents for `qwen3-32b`.
- Release blog (qwenlm.github.io). The arXiv tech report supersedes it for primary
  technical content; revisit if specific operational details (e.g. license, deployment
  recommendations) are missing from the paper.

## Open questions

Things flagged during extraction that need resolution. (See also the `open_questions`
array in `data/extracted/qwen3-32b.json` — that list is the authoritative one for
synthesis tooling; this section is for human-readable context.)

- [ ] HF `config.json` reports `max_position_embeddings=40960` (neither the 32,768
  trained max nor the 131,072 productized max). The paper does not address this
  specific value. May be a deployment-margin convention; worth confirming with a Qwen
  maintainer or by checking the deployment configs published alongside the model.
- [ ] Pre-training optimizer (AdamW vs other), peak/min LR, batch-size schedule, weight
  decay, gradient clipping. Paper says scaling-law-predicted values are used per-model
  but no concrete numbers are given.
- [ ] Mixed-precision recipe during training (BF16-only vs FP8 GEMM with BF16 master
  weights, etc.). Released checkpoint dtype is BF16 but training-time precision is
  not disclosed.
- [ ] Parallelism strategy and infrastructure (TP/PP/EP/DP shapes, GPU type and count,
  framework). Not disclosed in the paper.
- [ ] Long-CoT Cold Start dataset size and step count; Stage-3 Thinking Mode Fusion
  SFT volume. Both discussed qualitatively only.
- [ ] Per-stage data mix percentages for S1/S2/S3 pre-training. Only qualitative
  descriptions are given.

## Resolved

- **Q: Is 128K achieved via YaRN, DCA, or both?** ✅ Both. ABF (RoPE base 10K → 1M)
  is applied during the Long Context Stage of pre-training at sequence length 32,768;
  YaRN + DCA together provide a 4× extension at deployment to lift the served context
  to 128K. The static HF `config.json` keeps `rope_scaling=null` because the extension
  is opt-in per deployment (vLLM/SGLang config). Captured in
  `architecture.backbone.context_extension` (schema v3). [Paper §3.2]
- **Q: Is hybrid thinking architectural or post-training?** ✅ Post-training only.
  Stage 3 of Qwen3's four-stage pipeline ("Thinking Mode Fusion") is continual SFT
  on the Reasoning-RL checkpoint with mixed thinking + non-thinking data; runtime
  switching uses the chat-template directives `/think` (default) and `/no_think`,
  with `<think>...</think>` delimiting the reasoning block. No graph changes. Captured
  in `training.alignment.stages` and `training.alignment.inference_modes` (schema v3).
  [Paper §4]
- **Q: Pre-train data total tokens?** ✅ **36T** (Qwen3 paper §3.1). About 2× Qwen2.5,
  with 3× more languages (29 → 119).
- **Q: Is thinking-budget trained or inference-only?** ✅ Inference-only; capability
  emerges naturally from Thinking Mode Fusion. Implementation: insert the fixed
  sentinel `"Considering the limited time by the user, I have to give the solution based on the thinking directly now. </think>"` at a user-defined token threshold.
  [Paper §4.3]

## Inferred fields (closed models only)

N/A — Qwen3 is open-weight under Apache 2.0.

## Notes

- Naming: `qwen3-32b` (no dot, lowercase) aligns with HF official `Qwen/Qwen3-32B` and
  with kebab-case slug convention. The older roadmap used `qwen-3-235b`; updated to
  `qwen3-235b-a22b` (active-params suffix mirrors DeepSeek's MoE naming convention).
- Quick-look from HF config: 64 layers, hidden=5120, GQA(64Q/8KV), head_dim=128,
  intermediate=25600, vocab=151936, rope_theta=1e6, no rope_scaling, tie=false,
  bf16 native. `model_type=qwen3` (new; Qwen2.5 was `qwen2`).
