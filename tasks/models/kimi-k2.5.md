# Kimi K2.5

Slug: `kimi-k2.5`
Family: `kimi-k2`
Status: `extracted`

## Sources

Authoritative list in `data/sources/kimi-k2.5/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/tokenizer_config.json`
- [x] `preprocessor_config` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/preprocessor_config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/chat_template.jinja`
- [x] `readme` (`model_card`) — `https://huggingface.co/moonshotai/Kimi-K2.5/raw/main/README.md`
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2602.02276` (Kimi K2.5: Visual Agentic Intelligence, Feb 2 2026)
- [x] `blog` (`blog_html`) — `https://www.kimi.com/blog/kimi-k2-5.html`

## Open questions

- [ ] **K2 base tech report not yet published** — K2.5 paper §4.1 says "For detailed descriptions of MuonClip, architecture design, and training infrastructure, we refer to the Kimi K2 technical report [53]" but that report is "coming soon" on the K2-Base HF page. Several K2.5 fields stay at UNKNOWN until that report ships: lr schedule (K2 base), data mix percentages, training-infrastructure parallelism strategy, mixed-precision recipe specifics during pre-training.
- [ ] **Joint pretraining cumulative tokens** — paper §2 and §4.3/Table 3 both quote "approximately 15 trillion mixed visual and text tokens" for the K2.5 joint stage. Whether this is in addition to K2-base's 15T text-only (cumulative ~30T) or replaces a portion of the K2-base run is implied but not explicitly stated. Recorded as "~30T cumulative" in `data_total_tokens` with the breakdown spelled out.
- [ ] **video_token_id** — the chat template handles video via the string token `<|kimi_k25_video_placeholder|>` (not a single tokenizer-vocab integer like `<|media_pad|>=163605`). Recorded as UNKNOWN in `vision_token_anchors.video_token_id`.
- [ ] **Sparsity 48** — K2.5 paper §4.1 quotes "sparsity of 48"; conventional reading is total/active = 384/8 = 48. Recorded under that interpretation; flagged here in case "sparsity" means something different in the (yet unpublished) K2 paper.

## Resolved

- **Variant policy** — confirmed via paper §1: K2.5 is "a unified architecture for general-purpose agentic intelligence, integrating vision and language, thinking and instant modes, chats and agents". K2 generation was sibling-per-mode (Base / Instruct / Instruct-0905 / Thinking); K2.5 collapses to unified-with-modes via chat-template `thinking` kwarg. K2.6 adds `preserve_thinking` as a third kwarg-only mode.
- **Tool-call wire format** — `<|tool_call_begin|>{tool_call_id}<|tool_call_argument_begin|>{json_arguments}<|tool_call_end|>` wrapped by `<|tool_calls_section_begin|>` ... `<|tool_calls_section_end|>`; tool_call_id format `functions.{name}:{idx}`; arguments JSON-encoded. Source: chat_template.jinja + Kimi-K2-Thinking/docs/tool_call_guidance.md (canonical for the K2 family — K2.5 README §6 explicitly says "K2.5 shares the same design as K2 Thinking").
- **MTP** — K2 family does NOT use MTP (config.num_nextn_predict_layers=0). Distinguishes the K2 family from DeepSeek-V3/V4 which both ship MTP heads.
- **MLA dimensions** — kv_lora_rank=512, q_lora_rank=1536, qk_nope=128, qk_rope=64, v=128, num_heads=64. Same as DeepSeek-V3 modulo head count (V3 uses 128 heads; K2 family uses 64). HF config explicitly reuses the `DeepseekV3ForCausalLM` class as the K2 backbone.
- **Long-context curriculum** — K2.5 paper Table 3: 4K joint pre-training, then mid-training 32K (500B tokens) → 256K (200B tokens) via YaRN. config.rope_scaling.factor=64, original_max=4096.

## Notes

- The `KimiK25ForConditionalGeneration` HF model class wraps three components per paper §4.2: MoonViT-3D vision encoder, MLP projector, Kimi K2 MoE LLM. The text backbone reuses the DeepseekV3 model class via `auto_map`.
- Joint pretraining philosophy — early fusion at low constant vision ratio outperforms late fusion at high ratio (paper Table 1, §2.1). This reverses Qwen3.5/3.6's late-VL-in-pretraining choice.
- Zero-vision SFT is the surprising K2.5 finding — text-only SFT alone activates visual reasoning + tool use; adding human-designed visual SFT trajectories was shown to hurt generalization (paper §1, §2.2).
- Native INT4 QAT — K2.5 reuses K2-Thinking's recipe verbatim (README §4). Targets only routed-MoE-expert weights; vision pipeline + attention + shared expert + lm_head + dense FFN gates kept high-precision.
- Recommended sampling per README §6 and benchmark footnote: thinking mode T=1.0 / top_p=0.95 / context=256K; instant mode T=0.6 / top_p=0.95.
