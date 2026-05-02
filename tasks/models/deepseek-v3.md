# DeepSeek-V3

Slug: `deepseek-v3`
Family: `deepseek`
Status: `backlog`

This is the **M1 pilot extraction**. Goals: validate the schema covers what we need, surface gaps in extraction prompts, exercise MoE + MLA + FP8 fields. Expect schema iteration during this run.

## Sources

Primary (must-have):

- [ ] HuggingFace `config.json` — `https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/config.json`
- [ ] DeepSeek-V3 Technical Report (arXiv: 2412.19437)
- [ ] Official release blog post on api-docs.deepseek.com

Supporting:

- [ ] DeepSeek-V2 paper (for MLA design lineage)
- [ ] DeepSeekMoE paper (for routing algorithm context)

## Open questions

- [ ] (placeholder — fill during extraction)

## Resolved

- (none yet)

## Notes

This is the pilot — when something is awkward to extract, that's signal for schema improvement, not a reason to skip the field. Capture awkwardness in `open_questions` and we'll iterate.
