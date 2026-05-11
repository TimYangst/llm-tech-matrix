# Kimi K2.6

Slug: `kimi-k2.6`
Family: `kimi-k2`
Status: `extracted`

## Sources

Authoritative list in `data/sources/kimi-k2.6/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/tokenizer_config.json`
- [x] `preprocessor_config` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/preprocessor_config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/chat_template.jinja`
- [x] `readme` (`model_card`) — `https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/README.md`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2602.02276` (shared with K2.5; K2.6 cites the same arXiv ID, no separate paper)
- [x] `blog` (`blog_html`) — `https://www.kimi.com/blog/kimi-k2-6.html`

## Open questions

- [ ] **Release date** — README has no explicit release date. Comparison table cites Claude Opus 4.6 and GPT-5.4 as baselines, suggesting early-to-mid 2026, but YYYY-MM is not disclosed. Recorded as UNKNOWN.
- [ ] **K2.6 post-training delta** — README §1 describes the delta qualitatively (long-horizon coding, coding-driven design, 300-sub-agent / 4000-step swarm, 24/7 background agents) but no separate K2.6 paper has been published; arXiv:2602.02276 covers K2.5 only.
- [ ] **`preserve_thinking` training vs decoding-only** — Whether `preserve_thinking` is a pure inference-time chat-template change or also requires K2.6-specific RL alignment is not stated explicitly. The Terminal-Bench-2.0 footnote ("preserve thinking mode") hints at the latter.

## Resolved

- **Architecture identical to K2.5** — README §5 explicitly: "Kimi-K2.6 has the same architecture as Kimi-K2.5, and the deployment method can be directly reused." config.json byte-diff K2.5 vs K2.6 = 1 line (eos_token_id: 163585 → 163586). preprocessor_config.json byte-identical. tokenizer_config.json byte-identical.
- **chat_template.jinja delta vs K2.5** — adds `preserve_thinking` kwarg (default false). When true, the template skips the "find last non-tool-call assistant" loop so all messages render with their `<think>` blocks visible (instead of only the suffix-after-last-non-tool-call). Also accepts `reasoning` field name in addition to `reasoning_content`. Both consistent with the Qwen3.5→3.6 `preserve_thinking` story.
- **Tool-call wire format** — same as K2.5 / K2-Thinking. README §6: "K2.6 shares the same design of Interleaved Thinking and Multi-Step Tool Call as K2 Thinking."
- **Native INT4 QAT** — same recipe as K2.5 / K2-Thinking. README §4: "Kimi-K2.6 adopts the same native int4 quantization method as Kimi-K2-Thinking."
- **Variant policy** — same as K2.5 (unified-weights checkpoint with chat-template-kwarg modes); K2.6 just adds `preserve_thinking` as a third mode-kwarg.
- **EOS token shift** — eos_token_id moved from 163585 (`[EOS]`) to 163586 (`<|im_end|>`). The chat-template-driven generation now stops on the chat-role end token rather than the bare `[EOS]`. Likely a side-effect of preserve_thinking + long multi-turn conversation handling, but not explained in the README.

## Notes

- K2.6 is a clean Qwen3.5→3.6-style "post-training-only refresh" parallel — same architecture, additional chat-template kwarg, post-training emphasis on agent / coding tasks. Same architecture means the cross-version delta is interpretable as a **pure post-training delta** for synthesis purposes.
- Recommended sampling per README §6: thinking mode T=1.0 / top_p=0.95; instant mode T=0.6 / top_p=0.95. Footnote 1 says benchmark experiments use T=1.0 and **top_p=1.0** (vs README's 0.95 recommendation) at context length 262144 — slightly different from the README's recommended sampling.
- Agent Swarm scaled from K2.5's "main agent max 15 / sub-agents max 100" to K2.6's "300 sub-agents executing 4,000 coordinated steps".
