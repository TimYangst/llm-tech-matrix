# Per-Model Roadmap

Tactical, model-by-model status. For strategic milestones (M1/M2 scope, sequencing), see [`../docs/roadmap.md`](../docs/roadmap.md). For how to pick up the project from a fresh session, see [`../docs/session-start.md`](../docs/session-start.md).

## Current focus

**Phase:** M1 — **Qwen3.8 batch: the open-weight Qwen line rejoins the front, and a
Max-class model opens for the first time.** Two slugs added (`qwen3.8-27b`,
`qwen3.8-2.4t-a95b`), taking the repo to **20 extractions across 4 vendors**, all on
schema v7 with **no schema bump required** — the v6/v7 fields absorbed both records
cleanly, including a brand-new runtime-control axis.

**Qwen3.8-27B** (2026-08-05, Apache-2.0) is the cleanest frozen-architecture record in
the repo. Its `config.json` is **byte-identical to Qwen3.6-27B except
`transformers_version`** — and Qwen3.6-27B was already architecturally identical to
Qwen3.5-27B, so this is **one frozen backbone across three consecutive generations**
(64L, hidden 5120, 16×(3×GDN + 1×Gated Attn), dense FFN 17408, MTP-1, 262K native).
Every artifact-level delta lives in the chat template: (1) **`reasoning_effort`** —
`xhigh` (default) / `medium` / `low`, injected as *system-message instruction text*, with
`medium` injecting nothing at all; (2) **`preserve_thinking` default flips OFF → ON**, so
callers must now opt *out* of carrying full reasoning history; (3) the 3.6 fallback that
split `<think>` out of historical content is gone. Reported gains are large for a frozen
architecture — QwenSWEBench 49.3 → 79.0, DeepSWE 1.1 13.3 → 42.2, Terminal Bench 2.1
63.4 → 73.0 — and whether that came from new pre-training or post-training alone is the
extraction's headline open question.

**Qwen3.8-2.4T-A95B** (2026-08-08, custom `qwen3.8-max` licence) is the first
**Qwen-Max-class model ever released with open weights** and the repo's largest record
(2.4T total / 95B active, 92L, hidden 8192, 512 experts top-10 + 1 shared). It is a pure
widen-and-deepen scale-up of the unchanged Qwen3.5 recipe: same `Qwen3_5MoeForCausalLM`
class, same 3:1 Gated DeltaNet : Gated Attention cadence, same classic aux-loss routing
(`router_aux_loss_coef=0.001` — Qwen still has not adopted aux-loss-free bias routing at
any scale). Two structural firsts for this repo: it is the **first Qwen 3.x open
checkpoint that is not native-VL** (text-only; vision exists only in the hosted
Qwen3.8-Max), and the **first model anywhere in the repo to remove non-thinking as an
option** (`enable_thinking=false` raises in the chat template). Its Gated DeltaNet
scaling law is worth recording: V heads scale with width (48 → 128) while QK heads stay
pinned at 16 at every size, and the KV width (4×256=1024) is *identical* to the 27B
despite 1.6× the hidden size.

**The cross-vendor signal in this batch is `reasoning_effort`.** Three vendors now ship
the same API surface with three different mechanisms — DeepSeek-V4 prepends a prompt
prefix, Kimi K3 renders a typed `thinking-effort` option message, Qwen3.8 injects a
system-message instruction — and none of them is a control token or separate weights.
A new bilingual glossary entry (`reasoning-effort`) collects the comparison. Meanwhile
the *non-thinking* mode is disappearing as effort levels arrive, in both Qwen and
DeepSeek.

**Two vendor-lineage facts established while sourcing this batch:** Qwen3.6 never shipped
sizes beyond the April 27B + 35B-A3B pair (verified against the HF org listing), so
nothing was missing there; and **Qwen3.7 has no open weights at all** — it shipped as
hosted API models only (Qwen3.7-Max 2026-05, Qwen3.7-Plus 2026-06), so the open-weight
lineage runs 3.6 → 3.8 with one unobservable generation in between. `qwen3.7-max` is now
a tracked backlog entry in the closed-models table.

**No schema change.** `reasoning_effort` fits v6's `inference_modes[].kwargs` following
the DeepSeek-V4 / Kimi K3 precedent (one mode entry per effort level). One schema *gap*
was surfaced and deliberately left open: the repo cannot express that an **open
checkpoint is a strict subset of the vendor's hosted product** (Qwen3.8-Max adds vision,
non-thinking, 1M default context and built-in tools on top of the same weights;
Qwen3.8-27B gets a hosted variant with 1M context and built-in tools). It is recorded in
`variant_policy` prose and in `open_questions` for now — one occurrence is not yet a
schema trigger.

**Previous phase (Kimi + DeepSeek catch-up):** landed against new schema v7.
Three slugs added (`kimi-k3`, `deepseek-v4-flash-0731`, `deepseek-v3.2-exp`), taking the
repo to **18 extractions across 4 vendors**. This batch closed a 3-month freshness gap
(the repo's newest record had been April 2026) *and* the repo's biggest citation hole.

**Kimi K3** (2026-07, 2.8T / 104B active, 93L, 1M ctx, native vision) is a **full
architecture rewrite** of the K2 line, not a refresh — every load-bearing component
changed: MLA → hybrid **KDA + Gated MLA** at 3:1, SwiGLU → **SiTU-GLU**, DeepSeekMoE →
**Stable LatentMoE** (896 routed / 16 active in a 3584-wide latent space, Quantile
Balancing), standard residual → **AttnRes** (attention over depth), Muon → **Per-Head
Muon**, INT4 → **MXFP4/MXFP8 QAT**, SigLIP-init → **from-scratch MoonViT-V2**, and
RoPE/YaRN → **NoPE**. Only hidden dim 7168, vocab 160K and the single dense layer survive.
It is the repo's first `rope.type = "none"` record, first linear attention in a flagship
MoE, and first latent-space routed experts. Reported ≈2.5× scaling-efficiency gain over K2.

**DeepSeek-V4-Flash-0731** (2026-07-31) is the official graduation of the April preview:
architecturally frozen (config diff = four `dspark_*` keys + two `compress_ratios` entries)
but re-post-trained, with agentic jumps that are hard to overstate — DeepSWE 7.3 → 54.4,
Cybergym 38.7 → 76.7, Terminal Bench 2.1 61.8 → 82.7 — now beating V4-Pro (Preview) at
13B vs 49B activated. It also ships **DSpark**, a semi-autoregressive speculative-decoding
module *inside the checkpoint*. Cross-vendor note worth tracking: within weeks of each
other, DeepSeek replaced MTP-1 with DSpark and Kimi fine-tuned its MTP layer into an
EAGLE-3 draft — two vendors converging on "MTP head → dedicated draft module".

**DeepSeek-V3.2-Exp** (2025-09) closes the repo's biggest citation hole: `docs/glossary/dsa.md`
named it as DSA's origin while carrying a note that it was unextracted. It is also the
cleanest single-variable architecture experiment in the repo — the full config diff vs
DeepSeek-V3 is **three indexer keys** — and it supplies the V3 → V4 missing link, since
V4's CSA is literally "DSA + KV compression".

**Schema v7** landed with this batch (five additions, all backwards-compatible; migration in
`scripts/migrate_v6_to_v7.py`): `attention.sparse_attention` + `attention.notes`,
`architecture.auxiliary_modules[]`, `ffn.moe.latent_dim`, and `training.quantization`. Two of
these were explicitly deferred in the v5 changelog pending a second occurrence — both
triggers fired in this batch. All 18 records migrated and re-rendered; the new slots are
back-populated for the 6 sparse-attention models and the 7 quantized ones.

**Four new glossary entries:** KDA, AttnRes, Stable LatentMoE, speculative-decoding modules.

**Previous phase (GLM):** GLM family batch landed against schema v6 (no schema bump
required — v6 fields held cleanly across a fourth vendor). Three GLM slugs added
(GLM-4.7, GLM-5, GLM-5.1), all spanning the GLM-4.5 → GLM-5 cross-generation
architecture rewrite. **The GLM batch is the first non-DeepSeek vendor to ship
DeepSeek Sparse Attention (DSA)** — confirmed cross-vendor adoption of a
DeepSeek-V3.2 architectural innovation. GLM-5 / GLM-5.1 (`GlmMoeDsaForCausalLM`
class) combines MLA + DSA + 256-expert MoE + parameter-shared 3-step MTP, all
trained under Muon (with Z.AI's "Muon Split" per-head adaptation that closes the
MLA-vs-GQA-8 quality gap and obviates QK-Clip). GLM-4.7 (`Glm4MoeForCausalLM`,
inherited from the GLM-4.5 ARC paper) is the cross-generation reference: GQA
12:1 + QK-Norm + partial RoPE 0.5 + 160-expert MoE — a *full architecture
rewrite* across the 4.7→5 boundary, not an incremental refresh. GLM-5 / GLM-5.1
config.json is byte-identical except `transformers_version`, the cleanest
post-training-only refresh signal in the repo.

**Previous phase (Kimi K2):** Kimi K2 family batch landed against schema v6
(no schema bump required — v6 fields hold cleanly across a third vendor). Three
K2 slugs added (K2.5, K2.6, K2-Thinking), all 1T total / 32B active / 61L / MLA /
384 routed × 1 shared experts top-8, all reusing `DeepseekV3ForCausalLM` as the
text backbone. The Kimi extraction was the first non-Qwen / non-DeepSeek vendor
and the cleanest cross-vendor stress test for v6 — its `variant_policy` is *both*
sibling-per-mode (within K2: Base / Instruct / Instruct-0905 / Thinking) *and*
unified-weights-with-modes (within K2.5/K2.6: thinking / instant /
preserve-thinking via chat-template kwargs). Three new glossary entries landed
alongside the extractions: MoonViT, Native INT4 QAT, Agent Swarm / PARL.

**Previous phase (v6):** schema v6 landed (cross-vendor *release-strategy* and
*runtime-mode* comparison). Driven by a Qwen3.5/3.6 sub-model exploration that
surfaced three gaps the v5 schema couldn't express cleanly: (1) the *variant
policy* is invisible — Qwen 3.5/3.6's move away from Qwen2.5's separate
Math/Coder/VL/Thinking siblings toward unified weights with chat-template kwargs
had no field to record it; (2) `inference_modes[].trigger` is free text — the
actual chat-template kwargs (`enable_thinking`, `preserve_thinking`) and per-mode
sampling presets were buried in prose; (3) tool-call wire formats vary
meaningfully (Qwen3-Coder XML-like with `qwen3_coder` parser; DeepSeek-V4
`|DSML|` namespaced XML) and were unstructured. v6 adds `metadata.variant_policy`,
dual `inference_modes[].kwargs` + `sampling_recommended` companions, and
`alignment.tool_call_protocol` — all backwards-compatible. All 9 prior v5 records
migrated.

**Previous phase (v5):** DeepSeek-V4 batch landed. Both V4-Pro (1.6T total / 49B
active) and V4-Flash (284B / 13B) are extracted against schema v5 (which added
`architecture.residual_connections` for mHC / Hyper-Connections, and
`training.stability_notes` for Anticipatory Routing / SwiGLU Clamping). V4 is the
first repo entry to use the **Muon optimizer**, **mHC residual connections**, the
**hybrid CSA + HCA attention** with KV compression, **FP4 QAT (MXFP4)** for MoE
expert weights + indexer QK path, **multi-teacher On-Policy Distillation**, and a
3-mode reasoning effort axis (Non-think / Think High / Think Max). Schema v5 was
backwards-compatible — all 7 prior v4 records migrated cleanly with a one-line
`schema_version` bump.

**In progress (sourcing → extracting):**

- ✅ `qwen3.8-27b` — Qwen3.8 dense (Aug 2026, 27B, native VL) — **extracted** (config byte-identical to Qwen3.6-27B except `transformers_version` — a frozen backbone across 3.5 → 3.6 → 3.8; adds `reasoning_effort` xhigh/medium/low as system-message injection; `preserve_thinking` default flips OFF → ON)
- ✅ `qwen3.8-2.4t-a95b` — Qwen3.8 Max-class MoE (Aug 2026, 2.4T / 95B active) — **extracted** (first open-weight Qwen-Max; largest record in the repo; text-only unlike every prior Qwen 3.x open checkpoint; first model in the repo with no non-thinking mode; 512 experts top-10 + 1 shared under classic aux-loss; custom `qwen3.8-max` licence)
- ✅ `kimi-k3` — Kimi K3 (Jul 2026, 2.8T / 104B active, native multimodal, 1M ctx) — **extracted** (full architecture rewrite: KDA + Gated MLA 3:1 with NoPE; Block AttnRes at 12-layer blocks; Stable LatentMoE 896/16 in a 3584-wide latent space with SiTU-GLU + Quantile Balancing; Per-Head Muon; MXFP4 weights + MXFP8 activations QAT from SFT through RL; MoonViT-V2 trained from scratch; nine domain×effort RL experts consolidated by MOPD; XTML chat template; schema-v7 driver)
- ✅ `deepseek-v4-flash-0731` — DeepSeek-V4-Flash official (Jul 2026) — **extracted** (architecturally frozen vs the April preview; re-post-trained with large agentic gains; ships the DSpark semi-autoregressive speculative-decoding module in-checkpoint; `encoding/README.md` pins the full `｜DSML｜` wire format; reasoning-effort levels shifted — the preview's top prefix is now `high`)
- ✅ `deepseek-v3.2-exp` — DeepSeek-V3.2-Exp (Sep 2025, 671B / 37B) — **extracted** (the DSA origin the glossary had been citing without a record; config diff vs V3 is exactly three indexer keys; two-stage bolt-on recipe with the indexer trained by KL against the model's own attention distribution and detached from the graph; single mixed RL stage)
- ✅ `glm-5` — GLM-5 (Feb 2026, 744B / 40B active MoE, MLA + DSA) — **extracted** (first non-DeepSeek vendor to ship DSA; `GlmMoeDsaForCausalLM`; Muon Split adaptation that closes MLA-vs-GQA-8 quality gap and obviates QK-Clip; 28.5T pre-train + staged mid-training to 200K; slime async RL; GRPO+IcePop without KL; deterministic torch.topk in DSA Indexer for RL stability; FP8 rollouts; INT4 QAT during SFT)
- ✅ `glm-5.1` — GLM-5.1 (Apr 2026, post-training-only refresh of GLM-5) — **extracted** (config byte-identical except `transformers_version`; long-horizon agentic optimization "hundreds of rounds, thousands of tool calls"; SWE-Bench Pro 55.1 → 58.4; chat-template adds `defer_loading` filter + OpenAI-format unwrap + `tool_reference` content type for MCP-style lazy tool loading)
- ✅ `glm-4.7` — GLM-4.7 (Jan 2026, 358B MoE, predecessor anchor) — **extracted** (post-training-only refresh of GLM-4.6 on the GLM-4.5 ARC architecture; GQA 12:1 + QK-Norm + partial RoPE 0.5; 160-expert MoE; Muon optimizer; FIM-on-all-source-code; introduces Preserved Thinking + Turn-level Thinking inference modes; XML-like tool-call wire format that GLM-5 inherits unchanged)
- ✅ `kimi-k2-thinking` — Kimi K2-Thinking (text-only, 1T / 32B) — **extracted** (canonical K2-family text-only sibling, native INT4 QAT recipe origin, 200–300 sequential tool calls, Heavy Mode 8-rollout aggregation; `beta_fast=1.0` YaRN delta vs K2.5/K2.6)
- ✅ `kimi-k2.5` — Kimi K2.5 (Jan 2026, native multimodal) — **extracted** (joint text+vision continual-pretrained on K2-base; MoonViT-3D + MLP projector; Agent Swarm / PARL; zero-vision SFT; Toggle token-efficient RL; INT4 QAT inherited from K2-Thinking)
- ✅ `kimi-k2.6` — Kimi K2.6 (post-training-only refresh of K2.5) — **extracted** (same architecture; adds `preserve_thinking` 3rd kwarg-only mode; Agent Swarm scaled to 300 sub-agents × 4000 steps; long-horizon coding focus — clean parallel to Qwen3.5→3.6 post-training-delta pattern)
- ✅ `deepseek-v4-pro` — DeepSeek-V4 Pro (Apr 2026) — **extracted** (first MLA-replacement architecture: hybrid CSA + HCA with KV compression; mHC residuals; Muon optimizer; FP4 QAT; multi-teacher OPD; 3-mode reasoning; schema v5 driven by this extraction)
- ✅ `deepseek-v4-flash` — DeepSeek-V4 Flash (Apr 2026) — **extracted** (smaller V4 sibling, second-pass schema v5 validation; layers 0-1 use pure SWA instead of pure HCA, otherwise architectural shape identical)
- ✅ `qwen3.5-27b` — Qwen3.5 dense (Feb 2026) — **extracted** (first hybrid-backbone validation; schema v4 holds)
- ✅ `qwen3.5-35b-a3b` — Qwen3.5 MoE smaller (Feb 2026) — **extracted** (hybrid attention + MoE-FFN combo; shared-expert reintroduction; reverts to classic aux-loss)
- ✅ `qwen3.6-27b` — Qwen3.6 dense (Apr 2026) — **extracted** (post-training-only refresh of 3.5-27B; adds `preserve_thinking` 3rd inference mode + agentic-coding focus)
- ✅ `qwen3.6-35b-a3b` — Qwen3.6 MoE smaller (Apr 2026) — **extracted** (post-training-only refresh of 3.5-35B-A3B; same `preserve_thinking` + agentic-coding deltas as 3.6-27B)

**Schema gaps — resolved by v6 (2026-05):**

- ✅ Vendor variant policy — `metadata.variant_policy` (free-text). Captures Qwen3.5/3.6's "unified weights, modes via kwargs" stance vs Qwen2.5's "separate Math/Coder/VL siblings" vs DeepSeek's "Reasoner sibling → 3 reasoning-effort modes on one model" trajectory.
- ✅ Per-mode kwargs and sampling — `inference_modes[].kwargs: dict[str, str]` + `sampling_recommended: dict[str, str]`. Qwen3.5/3.6 README "Best Practices" sampling presets are now machine-readable; the `enable_thinking` / `preserve_thinking` toggles are no longer buried in prose.
- ✅ Tool-call wire format — `alignment.tool_call_protocol` (None when undisclosed). Qwen3-Coder XML-like protocol (`<tool_call><function=...><parameter=...></parameter></function></tool_call>` with `--tool-call-parser qwen3_coder`) and DeepSeek-V4's `|DSML|`-namespaced XML format are both now structured. Earlier deferred from v5 changelog ("structured tool-call protocol slot") — V4 + Qwen3.5/3.6 give us 3 protocol records to validate against.

**Schema gaps — resolved by v4 (2026-05):**

- ✅ Hybrid attention layout — `Attention.variants[]` + `layer_pattern` (see [conventions changelog v4](../docs/conventions.md#schema-changelog)).
- ✅ Native-VL encoder details — structured `Multimodal.vision_encoder` (HF `vision_config` keys) + `vision_token_anchors`.
- ✅ mRoPE — `RoPEType` includes `"mrope"`; `mrope_section` / `partial_rotary_factor` go in `rope.scaling` dict.
- ✅ Chat-template `enable_thinking` / `preserve_thinking` — initial v3 home was `alignment.inference_modes[].trigger` (free-form). v6 adds the structured `kwargs` companion.
- ✅ Multi-step MTP — `MTPConfig.depth` (semantic match: "D additional tokens"); `mtp_num_hidden_layers` (head depth) goes in `shared_modules`.

**Vendor-fact corrections (against initial roadmap notes):**

- Qwen3.5 also drops the `/think` soft switch — both 3.5 and 3.6 use `enable_thinking` chat-template kwarg.
- Qwen3.5 already has MTP (README: "MTP: trained with multi-steps"; config: `mtp_num_hidden_layers=1`). The 3.6 delta is `preserve_thinking` (multi-turn reasoning carryover), not MTP.

**Recommended next (after this batch):** 20 extractions, 4 vendors, schema v7 holding.
Highest-value next work, in order:

1. **Close the DeepSeek lineage.** `deepseek-v3.1` / `v3.1-terminus` is now the most
   conspicuous hole — it is the dense checkpoint DSA was retrofitted onto, so every
   V3.2-Exp benchmark row currently compares against a model with no record. Then
   `deepseek-v3.2` (the non-Exp 2025-12 release) and `deepseek-r1`.
2. **A closed model — and `qwen3.7-max` is now the cheapest way in.** `inferred_fields`
   is *still* empty across all 20 open-weight extractions, so the mechanism the schema was
   designed around has never been exercised. Qwen3.7-Max / 3.7-Plus (API-only, 2026-05/06)
   is the strongest candidate: it fills the one unobservable generation in an otherwise
   fully-extracted Qwen lineage, and same-family architectural priors make the inferences
   both cheap to justify and easy to bound. `gpt-4o` / `claude-sonnet-4` remain the
   cross-vendor alternatives.
3. **A reference dense GQA model** (`llama-3.1-70b` / `mistral-large-2`) — the first
   non-MoE extraction since Qwen3-32B / Qwen3.5-27B.
4. **Kimi Linear (`kimi-linear-48b-a3b`)** — newly load-bearing, since it is the KDA origin
   that Kimi K3 builds on. Previously deferred as an off-backbone sibling; K3 changes that
   calculus, and it would give the KDA glossary entry its "first introduced in" record the
   same way `deepseek-v3.2-exp` just did for DSA.
5. **GLM-V / GLM-OCR** to add Z.AI's multimodal axis, or `kimi-k1.5` / the original
   `kimi-k2` for the Kimi family root.

Deferred schema-iteration candidates that survive v7: a structured RewardModel slot
(Generative Reward Models now recur in DeepSeek-V4 OPD, DeepSeek-V3.2-Exp rubric-GRM,
DeepSeek-V3, Kimi K2.5 and Kimi K3's Agentic GRM — five occurrences, probably enough),
and a `training.pretraining_stages` list if pre-training pipelines keep getting more
elaborate (V3.2-Exp's two DSA stages currently sit in `alignment.stages`).
MTP-shaped objectives remain confirmed *not* universal — the K2 family has
`num_nextn_predict_layers=0`, while K3 reintroduces one MTP layer and then converts it
into a speculative-decoding draft.

Two candidates added by the Qwen3.8 batch, both deliberately **not** acted on yet:

- **Open-checkpoint vs hosted-product capability split.** Qwen3.8-Max adds vision,
  non-thinking, 1M default context and built-in tools on top of the *same* open weights;
  a hosted Qwen3.8-27B likewise adds 1M context and built-in tools. The schema can only
  describe the artifact, so this currently lives in `variant_policy` prose and
  `open_questions`. One vendor, one occurrence — wait for a second before adding a field.
- **Structured reasoning-effort slot.** Three vendors, three mechanisms (DeepSeek-V4
  prompt prefix, Kimi K3 typed option message, Qwen3.8 system-message injection), all
  currently flattened into one `inference_modes[]` entry per level with the mechanism
  described in `trigger` free text. That works, and the new `docs/glossary/reasoning-effort.md`
  entry carries the cross-vendor comparison — but a fourth occurrence would justify
  promoting `mechanism` and `levels` to structured fields.

> Note on the Qwen3 family: it ships as 6 dense sizes (0.6B–32B) + 2 MoE flagships
> (30B-A3B, 235B-A22B). We extracted two slugs only — the 32B dense and 235B-A22B MoE
> flagships — since dense siblings share architecture and training recipe modulo
> width/depth. If a per-size scaling analysis becomes useful later, schema can grow a
> `metadata.size_variants` field then.

> Note on Qwen3.5 / 3.6 / 3.7 / 3.8: Qwen3.5 ships ~7 open-weight sizes (0.8B–397B).
> Qwen3.6 opened exactly two — 27B dense + 35B-A3B MoE, both April 2026 — and nothing
> since (verified against the HF `Qwen` org listing). **Qwen3.7 opened nothing at all**;
> it exists only as hosted API models (Qwen3.7-Max 2026-05, Qwen3.7-Plus 2026-06), so the
> open-weight lineage runs 3.6 → 3.8 and 3.7 is tracked in the closed-models table.
> Qwen3.8 opened two: 27B dense (Apache-2.0, native VL) and 2.4T-A95B (custom
> `qwen3.8-max` licence, text-only). We extract six Qwen 3.x slugs total: dense 27B +
> smaller MoE 35B-A3B from 3.5 and 3.6, then 27B + the 2.4T Max-class model from 3.8.
> Same-size cross-version compare (27B at 3.5 / 3.6 / 3.8) is the cleanest signal for the
> per-generation delta, and it is what established that the backbone has been frozen for
> three generations.

> Note on the Kimi family: Moonshot ships sibling-per-mode text-only K2 checkpoints
> (Base / Instruct / Instruct-0905 / Thinking) but only K2-Thinking is extracted —
> Base/Instruct/Instruct-0905 share the same base weights, and only K2-Thinking ships the
> post-training innovations (interleaved thinking + tool use, native INT4 QAT) worth
> comparing across vendors. K2.5/K2.6 are the multimodal generation built on K2-Base via
> continual pre-training; both are extracted because the K2.5→K2.6 delta is a clean
> post-training-only refresh. **K3 is a different family, not a K2 refresh** — it shares no
> load-bearing component with K2 beyond hidden dim, vocab size and the single dense layer,
> and ships as one unified checkpoint with no Base release and no thinking toggle (effort is
> a `reasoning_effort` request field). Smaller siblings (Kimi-VL-A3B, Moonlight-16B-A3B) stay
> deferred, but **Kimi-Linear-48B-A3B has been promoted to a recommended next**: it is the
> KDA origin K3 builds on, so it now anchors a glossary entry the way DeepSeek-V3.2-Exp
> anchors DSA.

**Recently completed (2026-08-20):**

- Qwen3.8 batch: 2 slugs (`qwen3.8-27b`, `qwen3.8-2.4t-a95b`), repo now at 20 extractions.
  **Qwen3.8-27B** — config byte-identical to Qwen3.6-27B bar `transformers_version`, making
  the Qwen 3.x backbone frozen across three generations; the release delta is entirely in
  the chat template (`reasoning_effort` xhigh/medium/low via system-message injection with
  `medium` injecting nothing; `preserve_thinking` default flipped OFF → ON; historical
  `<think>` splitting fallback removed; empty tool-arg guard).
  **Qwen3.8-2.4T-A95B** — first open-weight Qwen-Max-class model and the repo's largest
  record; 92L / hidden 8192 / 512 experts top-10 + 1 shared / classic aux-loss; text-only
  and thinking-only, both of which are properties of the *open release* rather than the
  model (the hosted Qwen3.8-Max adds vision and non-thinking on the same weights).
- **No schema bump** — v7 absorbed both records. `reasoning_effort` fits
  `inference_modes[].kwargs`.
- 1 new bilingual glossary entry: **reasoning-effort** (three vendors, three mechanisms:
  DeepSeek-V4 prompt prefix, Kimi K3 typed option message, Qwen3.8 system-message
  injection). "Used by" rows added across Gated DeltaNet, GQA, mRoPE, MTP, YaRN and
  Hybrid Thinking.
- Vendor-lineage verification: Qwen3.6 has no post-April sizes; Qwen3.7 has no open
  weights at all. `qwen3.7-max` added to the closed-models backlog.
- Data correction: `qwen3.6-27b.json`'s `ffn.layer_partition` cited `mlp_only_layers=[]`,
  a key that Qwen3.5's config carries but Qwen3.6's config drops. Corrected and re-rendered.

**Recently completed (2026-08-14):**

- Kimi + DeepSeek catch-up batch: 3 slugs, closing a 3-month freshness gap.
  **Kimi K3** (2026-07) — full architecture rewrite of the K2 line: hybrid KDA (69 layers)
  - Gated MLA (24 layers) at 3:1 with an extra global layer at the end; Block AttnRes at
    12-layer blocks; Stable LatentMoE (896 routed / 16 active in a 3584-wide latent space,
    RMSNorm before up-projection, SiTU-GLU with β₁=4 / β₂=25, Quantile Balancing);
    Per-Head Muon; cosine decay chosen over WSD after per-schedule scaling-law searches;
    MXFP4 weights + MXFP8 activations with QAT from SFT through all of RL; MoonViT-V2
    trained from scratch under next-token prediction; NoPE with a four-stage 8K → 64K →
    256K → 1M curriculum; nine domain × effort RL experts consolidated by MOPD; XTML
    chat template with think/response/tools channels and dynamically loaded tools.
    **DeepSeek-V4-Flash-0731** (2026-07-31) — official V4-Flash, architecturally frozen,
    re-post-trained, shipping DSpark in-checkpoint; `encoding/README.md` finally pins the
    `｜DSML｜` wire format that the preview extraction had to leave partly UNKNOWN, and
    reveals that the reasoning-effort levels shifted (the preview's top "Think Max" prefix
    is now `high`; `max` is a new, stronger prefix).
    **DeepSeek-V3.2-Exp** (2025-09) — the DSA origin; indexer trained by KL against the
    model's own attention distribution with its input detached from the graph, which is
    what makes DSA retrofittable; single mixed RL stage (later replaced by OPD in V4).
- **Schema v7** — five backwards-compatible additions driven by this batch:
  `attention.sparse_attention` (SparseAttentionConfig — the slot deferred in v5, now with
  6 records), `attention.notes`, `architecture.auxiliary_modules[]` (DSpark + K3's
  EAGLE-3 draft — two independent occurrences in weeks), `ffn.moe.latent_dim` (LatentMoE),
  and `training.quantization` (QuantizationConfig — 7 records, and K3 is the second
  MXFP4 model that the v5 changelog set as the trigger). Plus `continued_pretraining` and
  `quantization_aware_training` as documented `AlignmentStage.method` vocabulary. All 18
  records migrated via `scripts/migrate_v6_to_v7.py` and re-rendered; renderer extended
  with Sparse attention / Auxiliary modules / Quantization sections in both languages.
- 4 new glossary entries (bilingual): KDA, AttnRes, Stable LatentMoE, speculative-decoding
  modules. "Used by" rows added across DSA (incl. the origin row, and its stale
  "not yet extracted" note removed), CSA+HCA, FP4 QAT, INT4 QAT, MLA, MTP, Muon,
  DeepSeekMoE, aux-loss-free routing, On-Policy Distillation, MoonViT, GRPO, mHC,
  Gated DeltaNet, YaRN.
- **Source drift found:** the tech-report URL in the `deepseek-v4-pro` and
  `deepseek-v4-flash` manifests (`huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf`)
  now 404s. The same report is on arXiv as **2606.19348**. Both preview manifests need
  repointing — not done in this batch to keep each extraction's manifest edits its own.

**Recently completed (2026-05-10 late evening):**

- GLM family batch landed: 3 slugs against schema v6 with no schema bump
  required. GLM-4.7 (358B MoE, predecessor anchor on the GLM-4.5 ARC
  architecture — GQA + QK-Norm + partial RoPE + 160-expert MoE + Muon),
  GLM-5 (744B / 40B active, *full architecture rewrite* with MLA + DSA +
  256-expert MoE, Muon Split adaptation closes MLA/GQA-8 gap and obviates
  QK-Clip, slime async RL with GRPO+IcePop, parameter-shared 3-step MTP),
  GLM-5.1 (post-training-only refresh, config byte-identical except
  `transformers_version`, long-horizon agentic delta SWE-Bench Pro 55.1
  → 58.4, chat-template adds `defer_loading` filter + `tool_reference`
  content type for MCP-style lazy tool loading). **First non-DeepSeek
  vendor to ship DSA** — confirmed cross-vendor adoption of a DeepSeek-V3.2
  architectural innovation. New glossary entry: DSA (DeepSeek Sparse
  Attention) covering the V3.2-Exp Lightning Indexer mechanism. GLM-family
  rows added to MLA, DeepSeekMoE, aux-loss-free-routing, MTP, Muon, GRPO,
  Hybrid Thinking, GQA, QK-Norm, FIM "Used by" tables. **Schema v6 held
  cleanly across a fourth vendor** — no schema iteration triggered.

**Recently completed (2026-05-10 evening):**

- Kimi K2 family batch landed: 3 slugs against schema v6 with no schema bump
  required. Kimi K2-Thinking (text-only sibling, native INT4 QAT recipe origin,
  Heavy Mode 8-rollout aggregation), Kimi K2.5 (joint text+vision continual
  pre-train on K2-base, MoonViT-3D vision encoder, Agent Swarm via PARL,
  zero-vision SFT, Toggle token-efficient RL), Kimi K2.6 (post-training-only
  refresh of K2.5, adds `preserve_thinking` 3rd kwarg-only mode, scales Agent
  Swarm to 300 sub-agents × 4000 steps). All three reuse `DeepseekV3ForCausalLM`
  as the text backbone (identical MLA config, modulo head count: 64 K2 vs
  128 V3). 3 new glossary entries: MoonViT, Native INT4 QAT, Agent Swarm /
  PARL. K2-family rows added to MLA, aux-loss-free-routing, Muon, YaRN,
  DeepSeekMoE "Used by" tables. **Schema v6 held cleanly across a third
  vendor** — no schema iteration triggered.

**Recently completed (2026-05-10):**

- Schema v6 — Qwen3.5/3.6-sub-model-exploration-driven, **backwards-compatible**. Three additions: (a) `metadata.variant_policy` — free-text describing how the vendor partitions capabilities across weight checkpoints vs. runtime modes (Qwen3.5/3.6: unified weights with chat-template kwargs; Qwen2.5: separate Math/Coder/VL/Audio/Omni siblings; DeepSeek-V4: 3 reasoning-effort modes via system prompt collapsing what was V3+R1 split). (b) `training.alignment.inference_modes[].kwargs: dict[str, str]` + `sampling_recommended: dict[str, str]` — make chat-template kwargs and per-mode sampling presets machine-queryable instead of buried in trigger/description prose. (c) `training.alignment.tool_call_protocol` — optional `ToolCallProtocol` subobject `{format, start_token, end_token, arguments_schema, parser_flags, notes}` capturing the wire format (Qwen3-Coder XML-like with `qwen3_coder` parser; DeepSeek-V4 `|DSML|`-namespaced XML). All 9 prior v5 records migrated; the 4 Qwen3.5/3.6 records and the 2 DeepSeek-V4 records carry full content, the 2 Qwen3 records and DeepSeek-V3 carry only `variant_policy` (no documented tool-call wire format in their sources). Renderer extended with a `Variant policy` row, per-mode kwargs/sampling sub-bullets, and a `Tool-call protocol` section. Migration script left in `scripts/migrate_v5_to_v6.py` for posterity.
- Sub-model exploration of Qwen3.5/3.6 confirmed (with sources) the absence of separate Thinking/Math/VL/Coder weight checkpoints in this generation. Chat-template byte-diff between 3.5 and 3.6: only 2 lines change — (1) `preserve_thinking` kwarg (controls whether historical `<think>` blocks render in past assistant turns), (2) tool-call argument JSON-encoding fix (`tojson` now applied to non-string scalars, fixing 'True'/'False' → 'true'/'false'). 27B and 35B-A3B within the same generation have byte-identical templates.
- Schema v5 — DeepSeek-V4-driven, **backwards-compatible**: `architecture.residual_connections` adds optional `ResidualConfig` subobject `{kind, expansion_factor, constraint, iterations, dynamic_parameterization, notes}` for inter-layer residual-stream topology beyond standard residual (mHC / Hyper-Connections); `training.stability_notes` adds an optional free-text field for training-stability tricks distinct from optimizer / lr_schedule / mixed_precision (Anticipatory Routing, SwiGLU Clamping). All 7 prior v4 records migrated cleanly with a one-line `schema_version` bump. Renderer extended to surface the two new sections; mdformat row-wrap quirk in conventions.md changelog (unescaped `|` inside `Foo | None` syntax) discovered and worked around.
- DeepSeek-V4-Pro extraction (1.6T total / 49B active / 33T pre-train tokens; 61 layers; hybrid CSA+HCA attention with shared-KV MQA, Lightning Indexer top-1024, query latent d_c=1536, output groups g=16; mHC `n_hc=4` Sinkhorn `t_max=20`; Muon optimizer with hybrid Newton-Schulz; SqrtSoftplus aux-loss-free routing on 384 routed × 1 shared experts top-6, no node-limited routing; Hash routing for first 3 MoE layers; FP4 QAT MXFP4 on MoE expert weights + indexer QK path; multi-teacher On-Policy Distillation replacing V3.2's mixed-RL stage; 3 reasoning modes Non-think / Think High / Think Max; 1M context curriculum-trained). First repo extraction with mHC, Muon, CSA/HCA, FP4 QAT, OPD.
- DeepSeek-V4-Flash extraction (284B / 13B / 32T; smaller V4 sibling; layers 0-1 use pure SWA instead of pure HCA, otherwise architectural family-shared; 256 routed × 1 shared experts; CSA top-512; query latent d_c=1024; output groups g=8; routed_scaling 1.5 vs Pro's 2.5). Second-pass schema v5 validation — all new slots populated cleanly without revision.
- 5 new glossary entries: mHC, Muon, FP4 QAT (MXFP4), On-Policy Distillation, CSA + HCA. Existing entries updated with V4 "Used by" rows: aux-loss-free-routing, deepseekmoe, mtp, fim, yarn-rope, grpo, dualpipe, fp8-mixed-precision.

**Recently completed (2026-05-09):**

- Schema v4 — Qwen3.5/3.6-driven: `Attention.variants[]` + `layer_pattern` for hybrid stacks; structured `Multimodal` (vision_encoder, vision_token_anchors); `RoPEType` adds `"mrope"`. All three v3 extractions (DeepSeek-V3, Qwen3-32B, Qwen3-235B-A22B) re-validated as v4 (multimodal: null → no migration needed).
- Sourced 4 Qwen3.5/3.6 slugs (config + HF README + blog).
- Qwen3.5-27B extraction (Qwen3.5 dense; hybrid 16×(3 GatedDeltaNet + 1 GatedAttention) backbone, partial RoPE 0.25, mRoPE, native VL with shared 248320 vocab; opt-in YaRN 262K→1010K; first stress-test of v4 hybrid-attention shape — schema held without modification).
- Qwen3.5-35B-A3B extraction (Qwen3.5 MoE; same hybrid backbone at 40 layers / hidden 2048, 256 routed × 512 width with 1 shared expert at 512 width, classic aux-loss `router_aux_loss_coef=0.001` reverting from Qwen3's global-batch LB and DeepSeek-V3's aux-loss-free; first hybrid-attention + MoE-FFN combo — schema held).
- Qwen3.6-27B extraction (post-training-only refresh of Qwen3.5-27B; same architecture, MTP, vision encoder, YaRN; deltas: a third runtime mode `preserve_thinking` for multi-turn reasoning carry-over, plus agentic-coding-focused post-training).
- Qwen3.6-35B-A3B extraction (post-training-only refresh of Qwen3.5-35B-A3B; HF model class is still `Qwen3_5MoeForConditionalGeneration`; same MoE topology + same classic aux-loss; same `preserve_thinking` + agentic-coding deltas as 3.6-27B).
- 2 new glossary entries: Gated DeltaNet, mRoPE; "Used by" rows added across GQA, MTP, YaRN, Hybrid Thinking, DeepSeekMoE for the full Qwen3.5/3.6 family.

**Phase complete:** all 4 native-VL Qwen3.5/3.6 slugs extracted (7 extractions total in repo). Schema v4 held throughout — designed up front, no in-flight changes needed. The 3.6 → 3.5 deltas turned out to be post-training-only (same backbone weights presumed; only HF class names differ at the metadata-level).

**Recommended next:** Cross-family dense baseline to break the Qwen monoculture in extracted set. Per the M1 backlog: `llama-3.1-70b` (reference dense GQA + RoPE), `mistral-large-2` (European reference), or `glm-4` (Chinese-language design choices). Then a closed model (`gpt-4o` or `claude-sonnet-4`) to exercise `inferred_fields`.

**Recently completed (2026-05-03):**

- Schema v3 (`backbone.context_extension`, `alignment.stages`, `alignment.inference_modes`); DeepSeek-V3 migrated
- Qwen3-32B extraction (Qwen flagship dense, GQA + QK-Norm + ABF/YaRN+DCA + four-stage post-training)
- Qwen3-235B-A22B extraction (Qwen flagship MoE — 128 experts/8 active, no shared experts, global-batch load balancing; same four-stage pipeline as 32B)
- 5 new glossary entries: GQA, QK-Norm, Hybrid Thinking, Dual Chunk Attention, Global-batch load balancing; YaRN, GRPO, DeepSeekMoE, and Aux-loss-free entries updated with Qwen3 cross-references

**Recently completed (2026-05-02):**

- Schema v2 + DeepSeek-V3 migration + glossary scaffold (9 seed entries) + Markdown renderer
- DeepSeek-V3 M1 pilot extraction (originally v1; the 7 schema gaps it surfaced drove v2)
- Source manifest + fetcher + pdf_to_text infrastructure
- Project scaffolding (docs/, src/, tasks/, .claude/skills/)

## Status enum

| Status       | Meaning                                                           |
| ------------ | ----------------------------------------------------------------- |
| `backlog`    | Identified as a target, no work started                           |
| `sourcing`   | Fetching `config.json`, papers, blogs into `data/sources/<slug>/` |
| `extracting` | Sources collected, extraction in progress                         |
| `extracted`  | `data/extracted/<slug>.json` written and schema-validates         |
| `reviewed`   | Human-reviewed, open questions resolved or accepted               |
| `blocked`    | Waiting on external info (e.g. paper not yet released)            |

## M1 — Open-weight text models

| Slug                     | Family   | Status      | Notes file                                                               | Sources priority                                                                                                                                                                                                                     |
| ------------------------ | -------- | ----------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `deepseek-v3`            | DeepSeek | `extracted` | [`models/deepseek-v3.md`](./models/deepseek-v3.md)                       | **M1 pilot** — extensive paper, exercises MLA + MoE + FP8. Surfaced 7 schema gaps.                                                                                                                                                   |
| `deepseek-v4-pro`        | DeepSeek | `extracted` | [`models/deepseek-v4-pro.md`](./models/deepseek-v4-pro.md)               | **Schema-v5 driver.** Hybrid CSA+HCA, mHC residuals, Muon, FP4 QAT, multi-teacher OPD, 1M ctx. 1.6T / 49B active.                                                                                                                    |
| `deepseek-v4-flash`      | DeepSeek | `extracted` | [`models/deepseek-v4-flash.md`](./models/deepseek-v4-flash.md)           | Schema-v5 second-pass validation. Same V4 architecture family at 284B / 13B; layers 0-1 use SWA instead of HCA.                                                                                                                      |
| `deepseek-v3.2-exp`      | DeepSeek | `extracted` | [`models/deepseek-v3.2-exp.md`](./models/deepseek-v3.2-exp.md)           | **DSA origin.** 671B/37B; config diff vs V3 is exactly 3 indexer keys. Two-stage bolt-on recipe; single mixed RL stage.                                                                                                              |
| `deepseek-v4-flash-0731` | DeepSeek | `extracted` | [`models/deepseek-v4-flash-0731.md`](./models/deepseek-v4-flash-0731.md) | Official V4-Flash. Architecturally frozen vs preview; ships the DSpark speculative-decoding module in-checkpoint.                                                                                                                    |
| `deepseek-r1`            | DeepSeek | `backlog`   | —                                                                        | RL-focused, exercises `alignment.rl_method`                                                                                                                                                                                          |
| `deepseek-v3.1`          | DeepSeek | `backlog`   | —                                                                        | The V3 → V3.2-Exp missing link (V3.1 / V3.1-Terminus is the dense checkpoint DSA was retrofitted onto)                                                                                                                               |
| `llama-3.1-70b`          | Llama    | `backlog`   | —                                                                        | Reference dense model with GQA                                                                                                                                                                                                       |
| `llama-3.1-405b`         | Llama    | `backlog`   | —                                                                        | Largest open dense model                                                                                                                                                                                                             |
| `qwen-2.5-72b`           | Qwen     | `backlog`   | —                                                                        | Strong tech report                                                                                                                                                                                                                   |
| `qwen3-32b`              | Qwen     | `extracted` | [`models/qwen3-32b.md`](./models/qwen3-32b.md)                           | Dense flagship — GQA, hybrid thinking                                                                                                                                                                                                |
| `qwen3-235b-a22b`        | Qwen     | `extracted` | [`models/qwen3-235b-a22b.md`](./models/qwen3-235b-a22b.md)               | MoE flagship — compare routing with DeepSeek-V3                                                                                                                                                                                      |
| `glm-4.7`                | GLM      | `extracted` | [`models/glm-4.7.md`](./models/glm-4.7.md)                               | GLM-4.5 ARC architecture (358B MoE, GQA + QK-Norm + partial RoPE + 160-expert MoE) — predecessor anchor for GLM-5                                                                                                                    |
| `glm-5`                  | GLM      | `extracted` | [`models/glm-5.md`](./models/glm-5.md)                                   | First non-DeepSeek vendor to ship DSA. 744B / 40B active. MLA + DSA + 256-expert MoE + Muon Split. Schema-v6 4th vendor.                                                                                                             |
| `glm-5.1`                | GLM      | `extracted` | [`models/glm-5.1.md`](./models/glm-5.1.md)                               | Post-training-only refresh of GLM-5 (config byte-identical except `transformers_version`); long-horizon agentic delta.                                                                                                               |
| `kimi-k2-thinking`       | Kimi     | `extracted` | [`models/kimi-k2-thinking.md`](./models/kimi-k2-thinking.md)             | K2 text-only Thinking sibling — native INT4 QAT origin, 200–300 sequential tool calls, Heavy Mode aggregation                                                                                                                        |
| `qwen3.8-2.4t-a95b`      | Qwen     | `extracted` | [`models/qwen3.8-2.4t-a95b.md`](./models/qwen3.8-2.4t-a95b.md)           | **First open-weight Qwen-Max-class model** and the repo's largest record. 2.4T / 95B active, 92L, 512 experts top-10 + 1 shared, classic aux-loss. Text-only and thinking-only — both properties of the open release, not the model. |
| `minimax-text-01`        | MiniMax  | `backlog`   | —                                                                        | Linear attention variant                                                                                                                                                                                                             |
| `mistral-large-2`        | Mistral  | `backlog`   | —                                                                        | European reference point                                                                                                                                                                                                             |

## M1 — Multimodal extension

Qwen3.5/3.6 are *natively* multimodal (LM + vision encoder ship together), unlike the
older projection-fusion multimodal models below them. They sit in this table because
their primary characterization includes vision, not because they're a "VL extension"
of a text-only LM.

| Slug              | Family  | Status      | Notes file                                                 | Source priority                                                                                                                                                                                         |
| ----------------- | ------- | ----------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `qwen3.5-35b-a3b` | Qwen    | `extracted` | [`models/qwen3.5-35b-a3b.md`](./models/qwen3.5-35b-a3b.md) | Qwen3.5 MoE — hybrid (10×(3 DeltaNet + 1 GatedAttn)) + 256-expert MoE (top-8 + 1 shared, w 512); native VL                                                                                              |
| `qwen3.5-27b`     | Qwen    | `extracted` | [`models/qwen3.5-27b.md`](./models/qwen3.5-27b.md)         | Qwen3.5 dense — hybrid backbone (16×(3 DeltaNet + 1 GatedAttn)), FFN dense 17408, native VL                                                                                                             |
| `qwen3.6-35b-a3b` | Qwen    | `extracted` | [`models/qwen3.6-35b-a3b.md`](./models/qwen3.6-35b-a3b.md) | Qwen3.6 MoE — architecturally identical to Qwen3.5-35B-A3B (same `Qwen3_5MoeForConditionalGeneration` HF class); deltas: `preserve_thinking` 3rd mode + agentic-coding focus                            |
| `qwen3.6-27b`     | Qwen    | `extracted` | [`models/qwen3.6-27b.md`](./models/qwen3.6-27b.md)         | Qwen3.6 dense — architecturally identical to Qwen3.5-27B; deltas: `preserve_thinking` 3rd inference mode + agentic-coding post-training focus                                                           |
| `kimi-k2.5`       | Kimi    | `extracted` | [`models/kimi-k2.5.md`](./models/kimi-k2.5.md)             | Kimi K2.5 — native multimodal continual-pretrain on K2-base; MoonViT-3D + MLP projector; Agent Swarm via PARL; zero-vision SFT; INT4 QAT inherited from K2-Thinking                                     |
| `kimi-k3`         | Kimi    | `extracted` | [`models/kimi-k3.md`](./models/kimi-k3.md)                 | Kimi K3 — 2.8T/104B, KDA + Gated MLA 3:1, AttnRes, Stable LatentMoE 896/16, SiTU-GLU, NoPE, MXFP4/MXFP8 QAT, MoonViT-V2 from scratch. Full rewrite of the K2 architecture; schema-v7 driver             |
| `kimi-k2.6`       | Kimi    | `extracted` | [`models/kimi-k2.6.md`](./models/kimi-k2.6.md)             | Kimi K2.6 — post-training-only refresh of K2.5; adds `preserve_thinking` 3rd kwarg-only mode; Agent Swarm scaled to 300 sub-agents × 4000 steps; long-horizon coding focus                              |
| `qwen3.8-27b`     | Qwen    | `extracted` | [`models/qwen3.8-27b.md`](./models/qwen3.8-27b.md)         | Qwen3.8 dense — `config.json` byte-identical to Qwen3.6-27B except `transformers_version`; frozen backbone across 3.5 → 3.6 → 3.8. Deltas: `reasoning_effort` 3 levels, `preserve_thinking` default ON. |
| `qwen-2.5-vl-72b` | Qwen    | `backlog`   | —                                                          | Vision encoder + projection fusion                                                                                                                                                                      |
| `minicpm-v-2.6`   | MiniCPM | `backlog`   | —                                                          | Compact multimodal                                                                                                                                                                                      |
| `glm-4v`          | GLM     | `backlog`   | —                                                          | Native vs projected fusion comparison                                                                                                                                                                   |

## M1 — Closed models (inference)

| Slug              | Family    | Status    | Notes file | Inference confidence                                                                                                                                                                             |
| ----------------- | --------- | --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `gpt-4o`          | OpenAI    | `backlog` | —          | Architecture from leaks/papers, training mostly unknown                                                                                                                                          |
| `claude-sonnet-4` | Anthropic | `backlog` | —          | Mostly closed; high `[Unknown]` rate expected                                                                                                                                                    |
| `gemini-2.0-pro`  | Google    | `backlog` | —          | Some details public via Google papers                                                                                                                                                            |
| `qwen3.7-max`     | Qwen      | `backlog` | —          | **Highest-value closed candidate.** Fills the one unobservable generation in the Qwen lineage (API-only, 2026-05); same-family priors make `inferred_fields` cheap to justify and easy to bound. |

## M2 — Diffusion (deferred)

Not started. Add entries when M1 exit criteria are met (see [`../docs/roadmap.md`](../docs/roadmap.md)).

## How to update this file

When you start work on a model:

1. Move the row's status from `backlog` → `sourcing` (or further along).
2. If it doesn't have a notes file yet, create `models/<slug>.md` from the template (`models/_template.md`) and link it.
3. On completion, update to `extracted` and commit `data/extracted/<slug>.json`.
