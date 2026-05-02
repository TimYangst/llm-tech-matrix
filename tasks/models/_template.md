# &lt;Model Name&gt;

Slug: `<model-slug>`
Family: `<family-slug>`
Status: `backlog` | `sourcing` | `extracting` | `extracted` | `reviewed` | `blocked`

## Sources

The authoritative source list is `data/sources/<slug>/manifest.json` (committed). This
section is for human notes — links you intend to register, candidates you considered,
and rationale.

Register each source via:

```bash
uv run python -m llm_tech_matrix.sourcing add <slug> \
  --name <logical-name> --kind <hf_config|arxiv_pdf|tech_report|blog_html|model_card|other> \
  --url <public-url> [--filename <local>] [--description "..."]
```

Planned sources:

- [ ] `config` (`hf_config`) — `https://huggingface.co/<org>/<model>/raw/main/config.json`
- [ ] `paper` (`arxiv_pdf` or `tech_report`) — `<url>`
- [ ] `release_blog` (`blog_html`) — `<url>`

Considered but excluded:

- (none)

## Open questions

Things flagged during extraction that need resolution. Move to "Resolved" when answered, with the source.

- [ ] (example) Is the FFN `intermediate_size` per-expert or total? Paper Section 3.2 ambiguous.

## Resolved

- (none yet)

## Inferred fields (closed models only)

If applicable, list values that are public-but-not-officially-confirmed. Mirror these
into the `inferred_fields` array of the extracted JSON.

| Field | Inferred value | Basis | Confidence |
|---|---|---|---|
| | | | |

## Notes

Free-form scratch space — context, surprises, decisions. Not consumed by tooling.
