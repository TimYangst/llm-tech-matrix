# GLM-5.1

Slug: `glm-5.1`
Family: `glm-5`
Status: `extracted`

## Sources

Authoritative list in `data/sources/glm-5.1/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/zai-org/GLM-5.1/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/zai-org/GLM-5.1/raw/main/tokenizer_config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/zai-org/GLM-5.1/raw/main/chat_template.jinja`
- [x] `readme` (`model_card`) — `https://huggingface.co/zai-org/GLM-5.1/raw/main/README.md`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2602.15763` (shared GLM-5 paper)
- [x] `blog` (`blog_html`) — `https://z.ai/blog/glm-5.1` (JS-rendered SPA — minimal content captured)

## Open questions

- [ ] **No dedicated GLM-5.1 tech report.** README cites the GLM-5 paper (arxiv:2602.15763) as the canonical reference. Specifics of the post-training refresh (RL token budget, environment counts, rollout-length distribution, hyperparameter changes vs GLM-5) are not numerically disclosed.
- [ ] Whether GLM-5.1 saw any additional pre-training tokens vs GLM-5 (continued pre-training, additional mid-training stages) is not stated. README phrasing supports post-training-only.
- [ ] Chat-template additions (`defer_loading` / `strict` key filtering, OpenAI-format unwrapping, `tool_reference` content type) suggest GLM-5.1 was trained with a deferred / lazy tool-loading workflow — likely related to MCP servers exposing many tools where only a subset is materialized per turn. The training data recipe for this scenario is not documented.
- [ ] Sampling presets per inference mode are not separately disclosed for GLM-5.1 — README §Benchmark uses the GLM-5 evaluation settings (temperature/top_p inherited per task).

## Resolved

- **GLM-5 → GLM-5.1 is post-training-only refresh** — config.json byte-identical except `transformers_version` (5.0.2.dev0 → 5.4.0); tokenizer_config.json identical. Same 744B / 40B active. Architecture / MoE topology / DSA indexer / RoPE all unchanged.
- **Chat-template diff** vs GLM-5 (4 meaningful additions): (1) `tool_to_json` macro filtering `defer_loading` and `strict` keys; (2) OpenAI-format `{function: {...}}` envelope unwrapping; (3) `thinking_indices` namespace tracking historical thinking presence per user turn; (4) `tool_reference` content-type support inlining the matching tool definition into the `<tool_response>` envelope.
- **Long-horizon agentic delta is the GLM-5.1 headline** — README intro: "sustains optimization over hundreds of rounds and thousands of tool calls". Empirical: SWE-Bench Pro 55.1 → 58.4 (state-of-the-art), NL2Repo 35.9 → 42.7, Terminal-Bench 2.0 (Terminus-2) 56.2 → 63.5, BrowseComp 62.0 → 68.0, CyberGym 48.3 → 68.7, Vending-Bench 2 $4,432 → $5,634.
- **Tool-call parsers reused from GLM-5** — `glm47` (tool-call) and `glm45` (reasoning) parser names inherited; Z.AI did not bump labels for the 5.1 refresh.

## Notes

- This is the second clean within-generation post-training-only refresh in the repo (after Qwen3.5 → Qwen3.6 and Kimi K2.5 → K2.6). Same pattern: byte-identical (or near-identical) config, post-training engineering moves the needle on coding/agentic benchmarks, chat-template adds new mode kwargs.
- The `tool_reference` content type addition is the most concrete chat-template-level signal that GLM-5.1 was trained on lazy-loaded MCP-style tool catalogs — a workflow where tool definitions are surfaced to the model only when relevant cross-turn, rather than dumping the entire catalog into the system prompt.
- Z.AI explicitly cites Claude Opus 4.6 / Gemini 3.1 Pro / GPT-5.4 as comparison frontier models in the GLM-5.1 README (vs GLM-5's GPT-5.2 / Claude Opus 4.5 / Gemini 3 Pro), suggesting GLM-5.1 was released ~2 months after GLM-5.
