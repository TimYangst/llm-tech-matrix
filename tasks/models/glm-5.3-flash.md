# GLM-5.3-Flash

Slug: `glm-5.3-flash`
Family: `glm`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/glm-5.3-flash/manifest.json` (committed).

- [x] `config` (`hf_config`) — `https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json`
- [x] `chat_template`, `tokenizer_config`, `processor_config` (`other`), `readme` (`model_card`)
- [x] `paper` (`arxiv_pdf`) — GLM-5 family report `https://arxiv.org/pdf/2602.15763`
  (predates this architecture and cannot cover it — registered because the card cites it)
- [x] `blog` (`blog_html`) — `https://z.ai/blog/glm-5.3-flash` (SPA shell, 0 chars)

Considered but excluded:

- `GLM-5.3-Flash-BF16` — the unquantized sibling. **Note the inversion**: the primary repo
  ships FP8; BF16 is the sibling. Every prior GLM record had bf16 primary, FP8 sibling.

## Open questions

See the extracted JSON. Two that matter most:

1. **No numeric benchmark table** — results ship only as `bench_53.png`. No GLM-5.2 deltas
   are recorded. Re-extract if Z.AI publishes a text table (it did for 5.2).
2. **The chat template handles audio but nothing else does** — `emit_audio()` renders
   `<|begin_of_audio|><|end_of_audio|>`, but there is no audio encoder, no audio token id,
   and no audio claim in the README.

## Resolved

- ✅ **Is this a 5.2 refresh?** No. `Glm5NextForConditionalGeneration` / `glm5_next` vs
  `GlmMoeDsaForCausalLM`. README: "starts from a newly trained base model, with its
  architecture and training recipe redesigned".
- ✅ **First natively multimodal GLM-5-series model** — stated in the README and confirmed
  by `vision_config` + processor config.

## Inferred fields (closed models only)

N/A — open-weight under MIT.

## Notes

**Architecture snapshot**

- 320B total / **18B active**, 45 layers, hidden 4096, 1M native context
- `(KDA, KDA, KDA, DSA-MLA) × 11 + KDA` — 34 linear-attention + 11 sparse-attention layers
- KDA: 64 heads, head_dim 128, short conv 4, `gate_lower_bound=-5.0`
- MLA: **NoPE** (`mla_use_nope=true`, `qk_rope_head_dim=0`), kv_lora 512, q_lora 1536
- DSA indexer: 32 heads × 128, top-k 2048, **`index_kpool=4` + `index_kpool_compress`**
- mHC: `hc_mult=4`, `hc_sinkhorn_iters=20`
- MoE: 288 experts (up from 256), top-8 + 1 shared, width 2048, aux-loss-free
- SwiGLU clamp `swiglu_limit=10.0`; `moe_router_dtype=float32`
- Vision: 24-layer ViT, hidden 1024, fixed 448px, patch 14, MLP projector (10240)

**This model is a synthesis of four other vendors' ideas.** That is the story worth
recording:

| Component               | Origin in this repo     | GLM's version                                |
| ----------------------- | ----------------------- | -------------------------------------------- |
| KDA linear attention    | Kimi (Kimi Linear → K3) | **First non-Moonshot KDA deployment**        |
| NoPE attention          | Kimi K3                 | Same choice; Qwen tested and *rejected* NoPE |
| mHC widened residual    | DeepSeek-V4             | **Second vendor to ship mHC**, Sinkhorn kept |
| SwiGLU clamping         | DeepSeek-V4             | Adopted (`swiglu_limit=10.0`)                |
| Key-pooled DSA indexer  | Qwen (QSA, Aug 2026)    | Convergent — `index_kpool=4`                 |
| 3:1 linear:full cadence | Qwen 3.x, Kimi K3       | Third independent convergence                |

**GLM switched sides on the indexer question in two months.** GLM-5.2 answered DSA's
residual O(L²) indexer cost with *cross-layer* index sharing (IndexShare). GLM-5.3-Flash
answers it with *within-layer* key pooling and drops the Full/Shared partition entirely —
exactly the trade Qwen's report argued for on the grounds that cross-layer similarity is
weak in hybrid stacks. GLM-5.3-Flash is a hybrid stack. `index_share_for_mtp_iteration`
survives (reuse into MTP steps), but per-layer sharing does not.

**The FP8 exclusion list is an architecture x-ray.** `modules_to_not_convert` holds out the
entire mHC apparatus (`hyper_connection`, per-layer `hc_attn_base/fn/scale`,
`hc_ffn_base/fn/scale`) and every KDA state-path tensor (`A_log`, `dt_bias`, conv1d kernels,
the a/b/f/g low-rank projections, `o_norm`) — i.e. a precise inventory of what Z.AI
considers numerically fragile, which is exactly the two newest parts of the architecture.

**Runtime modes**: `reasoning_effort` gains a **`low`** level (5.2 had only {high, max}),
**`enable_thinking` is gone** — the template always opens `<think>`, so there is no
non-thinking mode — and `clear_thinking` now defaults to false, i.e. **full reasoning
history preserved by default**. Both of the latter two mirror moves Qwen made in the same
month (Qwen3.8-2.4T-A95B removing non-thinking; Qwen3.8 flipping `preserve_thinking` to
default-ON), arrived at independently through an inverse-polarity kwarg.

**No full-size GLM-5.3 exists** — only Flash. Whether `glm5_next` will carry a flagship, and
whether this release functions as a public architecture preview the way Qwen3.8-Flash-Next
does for Qwen4, is not stated.
