# GLM-5

Slug: `glm-5`
Family: `glm-5`
Status: `extracted`

## Sources

Authoritative list in `data/sources/glm-5/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/zai-org/GLM-5/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/zai-org/GLM-5/raw/main/tokenizer_config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/zai-org/GLM-5/raw/main/chat_template.jinja`
- [x] `readme` (`model_card`) — `https://huggingface.co/zai-org/GLM-5/raw/main/README.md`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2602.15763` (GLM-5: from Vibe Coding to Agentic Engineering, Feb 17 2026)
- [x] `blog` (`blog_html`) — `https://z.ai/blog/glm-5` (JS-rendered SPA — minimal content captured)

## Open questions

- [ ] Layer count discrepancy — paper §2.1 says "reduces its layer count to 80"; config has `num_hidden_layers=78` (+ `num_nextn_predict_layers=1` MTP). Recorded as 78 (config-authoritative). Possible explanations: paper counts MTP differently, pipeline-stage-level counting, or a late-stage architectural change not reflected in the released config.
- [ ] Total parameters discrepancy — paper / README intro report 744B. The HF org-listing tile shows GLM-5 as 754B. Paper-authoritative used.
- [ ] Pre-training data mix percentages not disclosed (qualitative descriptions only — Web/Code/Math&Science).
- [ ] Pre-training and mid-training lr schedules not disclosed numerically (only the DSA continued-pretraining warmup max-lr 5e-3 is stated).
- [ ] MTP loss weight schedule for GLM-5 not stated (GLM-4.5 ARC paper has 0.3 → 0.1 at 15T tokens, but GLM-5 paper does not restate).
- [ ] Whether IcePop's β=2 / ε_low=0.2 / ε_high=0.28 hyperparameters apply only to Reasoning RL or also carry over to Agentic RL is not explicit (paper §3.2 specifies them for Reasoning RL; §3.3 / §4.1.2 describes the asynchronous Agentic RL variant without restating numbers).

## Resolved

- **Architecture is MLA + DSA + 256-expert MoE** (config + paper §2.1 + §2.1.1).
- **DSA = DeepSeek Sparse Attention from V3.2-Exp** (paper §2.1 explicitly cites). First non-DeepSeek vendor to ship DSA. New glossary entry `docs/glossary/dsa.md` created for this batch.
- **MLA tuning vs DSV3** — paper §2.1 motivates 64 heads × 256 head_dim (vs DSV3's 128 × 192) as roofline-aware adjustment for non-H800 hardware. Closes the MLA-vs-GQA-8 gap via Muon Split optimizer adaptation, which also obviates QK-Clip (`use_qk_norm` is not present in GLM-5 config; paper Table 1 doesn't list QK-Norm for GLM-5).
- **MTP parameter sharing across 3 layers** — paper §2.1; config exposes 1 module, recipe shares parameters across 3 sequential predictions. Accept length 2.76 vs DSV3.2's 2.55 at 4 speculative steps (paper Table 2).
- **Three thinking modes via chat-template kwargs** — `enable_thinking` and `clear_thinking` give Interleaved (default) / Turn-level (per-turn `enable_thinking=false`) / Preserved (`clear_thinking=false`) modes. Paper §3.1 + chat_template.jinja confirm.
- **slime asynchronous RL infrastructure** — paper §3.6, §4.1, README intro. Not a new glossary entry yet (need a 2nd vendor's async-RL infra to justify).
- **Tool-call wire format = XML-like inherited from GLM-4.5/4.7** — `<tool_call>{name}<arg_key>K</arg_key><arg_value>V</arg_value>...</tool_call>`. vLLM `--tool-call-parser glm47 --reasoning-parser glm45`. Inherited unchanged into GLM-5.1.

## Notes

- **Cross-vendor DSA adoption is the headline finding for this batch.** GLM-5's `GlmMoeDsaForCausalLM` model class makes Z.AI the first non-DeepSeek vendor to ship DSA in production weights. Compared to the DSV4 family (which extends DSA into the more aggressive [CSA + HCA hybrid](../../docs/glossary/csa-hca.md) with additional KV compression), GLM-5 stays close to the V3.2-Exp recipe — same Lightning Indexer mechanism, same MLA underneath.
- **Architecture rewrite vs GLM-4.7.** GLM-4.7 → GLM-5 is essentially a *full architecture replacement* (GQA + QK-Norm + partial RoPE → MLA + DSA + Muon Split), not an incremental refresh. The naming continuity hides this — the GLM-4.5 ARC paper (which GLM-4.7 inherits) and the GLM-5 paper are essentially separate model families that share a vendor and post-training philosophy.
- **GLM-5.1 is byte-identical config except `transformers_version`** — the cleanest possible "post-training-only refresh" signal in the repo (Kimi K2.5 → K2.6 had `eos_token_id` change too).
- **slime async RL infrastructure** is referenced both in GLM-5 paper as "initialized in GLM-4.5" and in GLM-5 README intro. The full asynchronous decoupled framework with TITO gateway / Direct Double-sided Importance Sampling / Multi-Task Rollout Orchestrator was new in GLM-5.
