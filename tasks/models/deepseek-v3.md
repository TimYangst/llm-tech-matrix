# DeepSeek-V3

Slug: `deepseek-v3`
Family: `deepseek`
Status: `backlog`

This is the **M1 pilot extraction**. Goals: validate the schema covers what we need,
surface gaps in extraction prompts, exercise MoE + MLA + FP8 fields. Expect schema
iteration during this run.

## Sources

The authoritative list is `data/sources/deepseek-v3/manifest.json`. Run the fetcher
to populate the cache:

```bash
uv run python -m llm_oss_summary.sourcing fetch deepseek-v3
```

Planned sources:

- [ ] `config` (`hf_config`) — `https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/config.json`
- [ ] `paper` (`arxiv_pdf`) — DeepSeek-V3 Technical Report (arXiv: 2412.19437) — `https://arxiv.org/pdf/2412.19437`
- [ ] `release_blog` (`blog_html`) — official release post on api-docs.deepseek.com

Background reading (not registered as sources, just human reference):

- DeepSeek-V2 paper — for MLA design lineage.
- DeepSeekMoE paper — for routing algorithm context.

## Open questions

- [ ] (placeholder — fill during extraction)

## Resolved

- (none yet)

## Notes

This is the pilot — when something is awkward to extract, that's signal for schema
improvement, not a reason to skip the field. Capture awkwardness in `open_questions`
and we'll iterate.
