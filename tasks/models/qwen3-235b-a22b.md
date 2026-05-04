# Qwen3-235B-A22B

Slug: `qwen3-235b-a22b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3-235b-a22b/manifest.json` (committed).
This section is for human notes — links registered, candidates considered, and rationale.

Registered sources (see manifest for sha256s):

- [x] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3-235B-A22B/raw/main/config.json`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2505.09388` (Qwen3 Technical Report; same paper covers all Qwen3 sizes including this MoE flagship)

Considered but excluded:

- A separate "Qwen3-MoE" paper or blog: doesn't exist. The Qwen3 Technical Report
  documents both dense and MoE flagships in one paper.
- Qwen3-30B-A3B (the smaller MoE): produced via Strong-to-Weak Distillation from
  235B-A22B, not via the four-stage flagship pipeline. Different training story; would
  be its own slug if/when we extract it.

## Open questions

Things flagged during extraction that need resolution.

- [ ] HF config sets `intermediate_size=12288` AND `moe_intermediate_size=1536`. With
  `mlp_only_layers=[]` and `decoder_sparse_step=1`, every layer is MoE so the dense
  `intermediate_size` field has no inference-time consumer. Likely a vestige (1536 ×
  8 active = 12288 = effective per-token compute width); confirm via a Qwen3-MoE
  reference implementation that the field is unused.
- [ ] `router_aux_loss_coef=0.001` in HF config corresponds to the global-batch load
  balancing loss (Qiu et al., 2025 — paper §2). Confirm whether this is the only
  balancing signal or whether a sequence-level loss is also stacked.
- [ ] Same `max_position_embeddings=40960` mystery as Qwen3-32B (neither 32K trained
  max nor 131K productized max).
- [ ] Pre-training data total tokens for the MoE flagship — is it the same 36T as the
  dense models, or a different mix? Paper §3 implies all Qwen3 models share the same
  pre-train pipeline but doesn't explicitly say MoE matches dense token-for-token.
- [ ] All other Qwen3-32B open questions (optimizer, parallelism, mixed precision)
  apply equally here.

## Resolved

- **Q: Does the MoE flagship share the dense Qwen3 pre-training recipe?** ✅ Per
  paper §3, the same three-stage pre-training (S1 30T@4K, S2 5T@4K, S3 long-context
  @32K) and the same 36T total tokens / 119 languages / Qwen2.5-VL-OCR-augmented
  corpus appear to apply across both dense and MoE flagships. (Caveat retained as an
  open question: the paper does not explicitly assert token-for-token equality.)
- **Q: Does the MoE flagship share the dense post-training recipe?** ✅ Yes — paper
  §4 describes the four-stage Long-CoT Cold Start → Reasoning RL → Thinking Mode
  Fusion → General RL pipeline as applied to *flagships* (32B and 235B-A22B). Smaller
  Qwen3 sizes are produced via Strong-to-Weak Distillation from these two teachers.
- **Q: Routing balance approach?** ✅ **Global-batch load balancing loss** (Qiu et
  al., 2025), with `router_aux_loss_coef=0.001` in HF config. This is structurally
  different from DeepSeek-V3's auxiliary-loss-free per-expert bias updates. Captured
  in `architecture.ffn.moe.routing` and a new glossary entry
  [`global-batch-load-balancing`](../../docs/glossary/global-batch-load-balancing.md).
- **Q: Shared experts?** ✅ **None.** Paper §2 explicitly says "Unlike Qwen2.5-MoE,
  the Qwen3-MoE design excludes shared experts." All 94 layers are MoE
  (`mlp_only_layers=[]`, `decoder_sparse_step=1`).

## Inferred fields (closed models only)

N/A — Qwen3-235B-A22B is open-weight under Apache 2.0.

## Notes

- This is a **flagship** model: it goes through the full four-stage post-training
  pipeline (Long-CoT Cold Start → Reasoning RL → Thinking Mode Fusion → General RL),
  and serves alongside Qwen3-32B as a teacher in the Strong-to-Weak Distillation
  pipeline that produces smaller Qwen3 sizes.
- Quick-look from HF config: 94 layers, hidden=4096, GQA(64Q/4KV), head_dim=128,
  128 experts × 1536 each, 8 active per token, `model_type=qwen3_moe`. The "A22B"
  in the slug = 22B activated parameters per token.
- Cross-vendor MoE comparison: Qwen3 explicitly excludes shared experts (paper §2)
  whereas DeepSeek-V3 has 1 shared expert + 256 routed; Qwen3 uses global-batch
  load balancing loss (Qiu et al., 2025) whereas DeepSeek-V3 uses auxiliary-loss-free
  routing with per-expert bias updates.
