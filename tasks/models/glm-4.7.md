# GLM-4.7

Slug: `glm-4.7`
Family: `glm-4.5`
Status: `extracted`

## Sources

Authoritative list in `data/sources/glm-4.7/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/zai-org/GLM-4.7/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/zai-org/GLM-4.7/raw/main/tokenizer_config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/zai-org/GLM-4.7/raw/main/chat_template.jinja`
- [x] `readme` (`model_card`) — `https://huggingface.co/zai-org/GLM-4.7/raw/main/README.md`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2508.06471` (GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models, Aug 2025)
- [x] `blog` (`blog_html`) — `https://z.ai/blog/glm-4.7` (JS-rendered SPA — minimal content captured)

## Open questions

- [ ] **Total parameter count** — GLM-4.5 ARC paper Table 1 reports 355B "including MTP layers but not word embeddings and the output layer"; GLM-4.7 HF README + org-listing report 358B. The 3B difference matches expected embedding+output-head parameters (vocab 151552 × hidden 5120 × 2 ≈ 3.1B). Recorded 358B (model-card-authoritative).
- [ ] **Activated parameters for GLM-4.7 specifically** not separately stated; paper Table 1 lists GLM-4.5 at 32B activated. Recorded as UNKNOWN per strict-extraction rule.
- [ ] **Context window discrepancy** — GLM-4.5 ARC paper §2.4 / Figure 3 trains to a maximum of 131072 (128K). Config has max_position_embeddings=202752 (~200K). Possible follow-up mid-training stage between GLM-4.5 and GLM-4.7 not documented in the paper, or buffer reservation. Recorded as 131072 (paper-authoritative).
- [ ] **GLM-4.6 → GLM-4.7 RL details not disclosed** — README characterizes the delta qualitatively (multilingual coding RL, terminal-task RL, tool-using RL) but provides no algorithm names, environment counts, reward-system specifics, or token budgets.
- [ ] **Post-training RL algorithm specifics not in available paper excerpt** — paper §3 SFT data preparation is detailed (Cold Start, Overall SFT, Rejection Sampling, Function Call Templates, Prompt Selection, Automatic Agentic SFT Data Construction) but RL algorithm choices / reward-model architecture / hyperparameters are not.
- [ ] Pre-training data mix percentages not disclosed.
- [ ] Pre-training tensor/pipeline parallelism layout, mixed-precision recipe, and training infrastructure details not in available paper excerpt.

## Resolved

- **Architecture inherits GLM-4.5 ARC paper Table 1** — 92 layers (3 dense + 89 MoE) + 1 MTP, hidden 5120, 96 attention heads × 8 KV heads (GQA 12:1), `head_dim=128`, `partial_rotary_factor=0.5`, `use_qk_norm=true`, 160 routed × 1 shared experts × top-8.
- **Three thinking modes** — README explicitly names Interleaved Thinking (since GLM-4.5), Preserved Thinking (introduced in GLM-4.7), Turn-level Thinking (introduced in GLM-4.7). Same `enable_thinking` / `clear_thinking` kwargs that GLM-5 inherits.
- **XML-like tool-call wire format** — established in GLM-4.5 ARC paper §3.1 ("Reducing Character Escaping in Function Call Templates"), parser names `glm47` (tool-call) and `glm45` (reasoning) reflect the GLM-4.7 + GLM-4.5 origins. Same wire format inherited unchanged into GLM-5/5.1.
- **Wider-and-thinner head-count design choice** — paper §2.1: 96 attention heads at hidden 5120 = 2.5x more heads-per-hidden vs DSV3. Counterintuitively no training-loss gain but consistent MMLU/BBH improvements.
- **FIM applied to all source code** — paper §2.2 (vs DSV3's 10% rate).
- **Two-stage post-training** — Stage 1 Expert Training (Reasoning, Agent, General Chat experts via Cold-start CoT SFT + RL); Stage 2 Unified Training (self-distillation of experts → unified hybrid-reasoning model via Overall SFT + RL). GLM-4.6 / GLM-4.7 are post-training-only refreshes on the GLM-4.5 architecture.

## Notes

- GLM-4.7 is the **predecessor anchor for the GLM-5 batch** — gives a cross-generation reference for the GQA→MLA + QK-Norm→Muon-Split + GQA-partial-RoPE→full-RoPE transition that GLM-5 makes. The GLM-4.5 ARC paper is the canonical tech report for the entire 4.5/4.6/4.7 generation; the README only documents GLM-4.6 → GLM-4.7 deltas qualitatively.
- **Wider-and-thinner-vs-deeper-and-narrower flip across GLM-4.5 → GLM-5.** GLM-4.5 ARC paper §2.1 explicitly motivates "deeper, narrower" vs DSV3 / Kimi K2 ("we found that deeper models exhibited better reasoning capacity" — 92 layers at hidden 5120 vs DSV3's 61 × 7168). GLM-5 paper §2.1 reverses this: "scales to 256 experts and reduces its layer count to 80 to minimize expert parallelism communication overhead." Z.AI's stated philosophy moved when MLA + DSA gave them headroom to widen rather than deepen.
- **Smaller GLM-4.7-Flash sibling deferred** — GLM-4.7 ships with a Flash variant (~31B active, GLM-4.7-Flash) following the V4 Pro+Flash sibling pattern. Not extracted in this batch; would parallel the V4-Pro / V4-Flash within-generation comparison if added later.
