# Qwen3.8-Flash-Next

Slug: `qwen3.8-flash-next`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3.8-flash-next/manifest.json` (committed).

Registered sources:

- [x] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/chat_template.jinja`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/tokenizer_config.json`
- [x] `preprocessor_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/preprocessor_config.json`
- [x] `readme` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/README.md`
- [x] **`tech_report` (`tech_report`)** — `https://raw.githubusercontent.com/QwenLM/Qwen3.8-Flash-Next/main/tech_report.pdf`
- [x] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.8-flash-next`

**This is the first Qwen 3.x extraction backed by a real technical report.** Every prior
Qwen record (3.5, 3.6, 3.8) carried "no technical report exists" as an open question and
had UNKNOWN across the entire optimizer / stability / scaling-law surface. This one has
20 pages of architecture ablations, optimizer detail and stress-test methodology.

Considered but excluded:

- **ModelScope mirror** (`modelscope.cn/models/Qwen/Qwen3.8-Flash-Next`) — same artifacts
  as the HF repo. Registering both would double the sha256 surface for no extra
  information. HF is treated as canonical, consistent with every other record here.
- `video_preprocessor_config.json` — video preprocessing params; not load-bearing for the
  schema's `multimodal.vision_encoder` fields.
- `Qwen/Qwen3.8-Flash-Next-FP8` — not present at extraction time.

## Open questions

See `data/extracted/qwen3.8-flash-next.json` `open_questions`. The three that matter:

1. **The name lies about the architecture.** HF class is `Qwen4ExpForConditionalGeneration`,
   model_type `qwen4_exp`, and the README says outright it is "the architecture that will
   underpin Qwen4". It is filed under the 3.8 name for source fidelity but is not a sibling
   of Qwen3.8-27B / 2.4T-A95B. `metadata.family` cannot express "named 3.8, architecturally 4".
2. **Post-training is still dark.** The report is explicitly an architecture-and-optimization
   report; §4 evaluates the *base* model. Post-trained numbers appear on the model card with
   no method attached.
3. **Schema fit for the n-gram embedding.** Recorded under `architecture.auxiliary_modules`
   because it is a separately-parameterized, off-accelerator, deterministically-addressed
   table — but it sits inside the forward pass at layer 2, so it is not "auxiliary" in the
   DSpark / draft-head sense the v7 field was designed for. A second vendor shipping
   embedding-table capacity scaling should trigger a dedicated slot.

## Resolved

- ✅ **Is this a Qwen3.8 refresh?** No. Config declares a different model class from every
  other Qwen 3.x record. Four load-bearing components are new: QSA, Gated Residual, n-gram
  embedding, and the Muon/AdamW split recipe.
- ✅ **Does Qwen ship DSA-lineage sparse attention?** Yes — QSA, making Qwen the third
  vendor in the repo after DeepSeek (V3.2-Exp origin, V4) and Z.AI (GLM-5).
- ✅ **Does Qwen use Muon?** Yes, first Qwen record to do so — joining DeepSeek-V4, Kimi K3
  and the GLM-5 line.
- ✅ **NoPE question, settled by the vendor.** Report §2.1.1: RoPE and NoPE are
  indistinguishable during pre-training, but NoPE shows "a substantially higher rate of
  endless generation after post-training". Qwen keeps RoPE — a direct counterpoint to
  Kimi K3, which went NoPE.

## Inferred fields (closed models only)

N/A — open-weight, under a custom `qwen-community-1.0` licence (the third distinct licence
inside the Qwen3.8 name: 27B is Apache-2.0, 2.4T-A95B is `qwen3.8-max`).

## Notes

**Architecture snapshot**

- 125B total / **6B activated**, plus **51B n-gram embedding** (host memory) + **4B MTP**
- 48 layers, hidden 2560, `12 × (3 × (Gated DeltaNet → MoE) → 1 × (QSA → MoE))`
- GDN: 48 V heads / 16 QK heads, head_dim 128, **sigmoid** output gate (was swish)
- QSA: 24Q / **2KV** (12:1), head_dim 256, rotary dim 64; indexer MQA 4Q + 1 shared K,
  head_dim 128, budget 2048 tokens = 512 micro-blocks at r=4
- MoE: 512 experts, 10 routed + 1 shared, expert width 640, classic aux-loss 0.001
- Gated Residual: 4 branches, bottleneck rank 320, no `H_res`
- Context 262,144 native (CPT ran at 256K) → 1,000,000 via YaRN factor 4.0

**The four design moves, and what each is for**

| Component | Bottleneck it attacks | Headline number |
| --- | --- | --- |
| GDN hybrid 3:1 | Quadratic mixing + linear KV growth | Beats full-attn on 8/9, SWA-hybrid on 7/9 |
| QSA | DSA's own `O(n²)` indexer cost | `O(n²/r)`; 7.6× prefill / 4.9× decode at 1M |
| Gated Residual | Pre-norm signal attenuation; stability | +3.56 avg pts over pre-norm; no loss spikes |
| N-gram embedding | Capacity per FLOP; accelerator memory | 51B params off-accelerator, ~0 per-token FLOPs |

**Loss ≠ benchmarks — the report's recurring theme.** Three documented disagreements:
n-gram vocabulary scaling lowers loss monotonically while downstream saturates;
static→dynamic GR operators are worth only 0.002 loss but 1.98 accuracy points; and NoPE
is indistinguishable in pre-training but degrades generation after post-training. The
report's stated bottleneck for future work is evaluation throughput — "a cheaper mid-scale
probe that reliably predicts post-training ordering".

**Efficiency claim.** Base model beats Qwen3.8-27B-Base on all 14 benchmarks and the ~3×
larger Qwen3.7-Plus-Base (397B-A17B) on 8 of 14, at ~1/3 the activated params, ~1/3 the
tokens, ~1/9 the training FLOPs.

**Post-trained vs Qwen3.8-27B** (model card): DeepSWE 1.1 42.2 → 58.7, JobBench 33.4 →
55.7, SWE-bench Multilingual 73.8 → 81.0, Toolathlon Verified 67.1 → 73.5, CoWorkBench
70.7 → 73.9, HLE 30.8 → 35.9, GPQA Diamond 89.2 → 91.7.

**Cross-vendor notes worth tracking**

- Qwen is now the **third vendor** shipping DSA-lineage sparse attention, and the first to
  attack the indexer's own asymptotic cost rather than just the core attention's.
- It reuses **GLM-5's** trick of sharing top-k indices across speculative-decoding steps.
- **Everyone is on Muon now** — DeepSeek-V4, Kimi K3, GLM-5, and now Qwen.
- Qwen reports training with **no qk-clip (Kimi) and no SwiGLU-clip (DeepSeek-V4)**,
  attributing the margin to Gated Residual — i.e. a structural fix replacing two vendors'
  explicit clipping crutches.
- **RoPE vs NoPE now has a documented split**: Kimi K3 went NoPE; Qwen tested it and
  rejected it on post-training generation behavior.
