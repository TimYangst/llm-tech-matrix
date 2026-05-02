# &lt;Model Name&gt;

Slug: `<model-slug>`
Family: `<family-slug>`
Status: `backlog` | `sourcing` | `extracting` | `extracted` | `reviewed` | `blocked`

## Sources

Primary (must-have):

- [ ] HuggingFace `config.json` — URL: `https://huggingface.co/<org>/<model>/raw/main/config.json`
- [ ] Tech report / paper — URL:
- [ ] Official release blog — URL:

Supporting (optional):

- [ ] Vendor model card
- [ ] Independent analysis posts (cite carefully — these are secondary)

## Open questions

Things flagged during extraction that need resolution. Move to "Resolved" when answered, with the source.

- [ ] (example) Is the FFN `intermediate_size` per-expert or total? Paper Section 3.2 ambiguous.

## Resolved

- (none yet)

## Inferred fields (closed models only)

If applicable, list values that are public-but-not-officially-confirmed. Mirror these into the `inferred_fields` array of the extracted JSON.

| Field | Inferred value | Basis | Confidence |
|---|---|---|---|
| | | | |

## Notes

Free-form scratch space — context, surprises, decisions. Not consumed by tooling.
