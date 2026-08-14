# DeepSeek-V3.2-Exp

Slug: `deepseek-v3.2-exp`
Family: `DeepSeek`
Status: `extracted`

## Sources

Authoritative list in `data/sources/deepseek-v3.2-exp/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp/raw/main/config.json`
- [x] `readme` (`model_card`) — `.../README.md`
- [x] `tokenizer_config` (`other`) — `.../tokenizer_config.json` (carries the Jinja chat template → tool-call wire format)
- [x] `generation_config` (`other`) — `.../generation_config.json`
- [x] `paper` (`tech_report`) — `https://raw.githubusercontent.com/deepseek-ai/DeepSeek-V3.2-Exp/main/DeepSeek_V3_2.pdf`
- [x] `v3_paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2412.19437` (cited only for the architecture V3.2-Exp inherits unchanged)
- [x] `release_news` (`blog_html`) — `https://api-docs.deepseek.com/news/news250929` (release date, >50% price cut)

## Open questions

- [ ] **Optimizer unnamed** — the paper gives per-stage LRs but no optimizer. AdamW is likely (V3 lineage; Muon arrives only with V4) but unstated → UNKNOWN.
- [ ] **Param counts not in-source** — 671B/37B carried from the V3 report on the strength of a config diff whose only architectural additions are the three indexer keys, plus the README's `config_671B_v3.2.json`. The indexer's own parameters are unaccounted for in either figure.
- [ ] **Token-count accounting differs** — `data_total_tokens` records the 945.8B *continued-training* budget, not a lifetime total (V3: 14.8T, V4-Flash: 32T, V4-Pro: 33T). Do not compare across records naively.
- [ ] **V3.1 / V3.1-Terminus unextracted** — the immediate baseline for every benchmark row has no record. The V3 → V3.1 → V3.1-Terminus → V3.2-Exp chain is represented by endpoints only.
- [ ] **V3.2 (non-Exp, 2025-12)** is a distinct later model, not covered here.
- [ ] **Indexer-RoPE bug scope** — the 2025-11-17 README update documents a non-interleaved-vs-interleaved RoPE layout bug, scoped to the *demo code*. Whether released weights trained with the correct layout, and whether published benchmarks were affected, is unstated.
- [ ] **Masked-MHA prefill mode** — mentioned in one sentence with no engagement threshold.
- [ ] **FIM** — not restated for the continued-training stages; left null rather than assumed from V3's PSM@0.1.

### Schema gaps surfaced (drivers for v7)

- [ ] **No slot for a sparse-attention modifier.** DSA is not a per-layer variant (all 61 layers are uniform) but a mechanism layered *on top of* MLA. `Attention` has no free-text `notes` and no structured sparse/compressed subobject, so the indexer parameters ride in a `variants[]` entry the schema intends for hybrid stacks. **Fourth** record needing this — V4-Pro, V4-Flash (CSA/HCA), GLM-5/5.1 (DSA), and now the DSA origin itself.
- [ ] **`AlignmentStage.method` has no continued-pre-training vocabulary.** The two DSA training stages are pre-training, not alignment, but `alignment.stages` is the only ordered-pipeline structure in the schema. Recorded as `distillation` / `rl` with inline caveats.

## Resolved

- **Release date** — 2025-09-29 (DeepSeek API news). Also cut API prices >50% and kept V3.1-Terminus callable until 2025-10-15 for comparison.
- **The architectural delta is exactly three config keys.** Full diff vs `deepseek-ai/DeepSeek-V3`: `+index_n_heads=64`, `+index_head_dim=128`, `+index_topk=2048`, `quantization_config.scale_fmt="ue8m0"`, class/model_type rename, dropped `auto_map`, `transformers_version` bump. Everything else byte-identical. This is the cleanest single-variable architecture experiment in the repo.
- **DSA mechanism** — (1) Lightning Indexer: `I_{t,s} = Σ_j w_{t,j}·ReLU(q_{t,j}·k_s)` over 64 heads × 128 dim, ReLU chosen for throughput, implementable in FP8; still O(L²) but cheap. (2) Fine-grained top-k selection: only the top 2048 KV entries feed core attention, dropping it from O(L²) to O(Lk).
- **DSA is instantiated under MLA in MQA mode** — kernel efficiency requires each KV entry to be shared across queries. V3.1-Terminus used MLA's MHA mode for training/prefill and MQA only for decode; DSA forces MQA throughout. A masked-MHA mode simulates DSA for short-sequence prefill.
- **Two-stage bolt-on recipe** — dense warm-up (LR 1e-3, 1000 steps, 2.1B tokens, everything frozen but the indexer) then sparse adaptation (LR 7.3e-6, 15000 steps, 943.7B tokens, all params trainable, k=2048).
- **Indexer trains on attention self-distillation, not text.** Target = the model's own head-summed, L1-normalized attention distribution; loss = KL. The indexer input is **detached** from the graph — indexer optimized only by `L_I`, main model only by the LM loss. That separation is precisely what makes DSA retrofittable onto a dense checkpoint.
- **Post-training held identical to V3.1-Terminus by design** — specialist distillation over 5 domains + writing/QA, then **single mixed RL stage** (GRPO) merging reasoning + agent + human alignment to avoid the catastrophic forgetting of multi-stage RL. This is the exact stage DeepSeek-V4 later replaces with multi-teacher OPD.
- **Quality is flat, not better** — the point was efficiency. Where V3.2-Exp scores lower (GPQA, HLE, HMMT) the paper attributes it to generating *fewer reasoning tokens*, with the gap closing at token-matched intermediate checkpoints.
- **Tool-call wire format** — `<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>{name}<｜tool▁sep｜>{json_args}<｜tool▁call▁end｜>…<｜tool▁calls▁end｜>`, results in `<｜tool▁output▁begin｜>…<｜tool▁output▁end｜>`. Read from the Jinja template; undocumented in README and paper.

## Notes

- **This extraction closes the repo's biggest citation hole.** `docs/glossary/dsa.md` names V3.2-Exp as DSA's "first introduced in" anchor while carrying a note that the model was unextracted; that note is now obsolete and the Used-by table gains the origin row.
- The V3-lineage **tool-call protocol endpoint**: JSON arguments delimited by special tokens, no type discriminator, no nesting — and still a Jinja template. V4 breaks all three (XML-like `｜DSML｜`, `string="true|false"` discriminator, Python `encoding_dsv4` module instead of Jinja).
- Fills the V3 → V4 architecture gap: V4's CSA is literally "DSA + KV compression", so without this record the repo had the endpoint (CSA/HCA) with no origin. `index_n_heads`/`index_head_dim` are unchanged at 64/128 from V3.2-Exp through V4-Flash; only `index_topk` moves (2048 → 1024 Pro / 512 Flash) as compression takes over part of the reduction.
- Also the origin of DeepSeek's **single-mixed-RL-stage** stance, which V3.2-Exp adopts and V4 then abandons for OPD — a clean two-step trajectory for longitudinal synthesis.
