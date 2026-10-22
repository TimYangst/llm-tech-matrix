# DeepSeek-V4-Flash-Vision-Exp

Status: extracted (schema v8). Collected 2026-10-22; pending independent review.

## Identity and evidence

[Official checkpoint](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-Vision-Exp),
revision `6821d6ad3681a4b137b066b76094fa82ebd0a380`.
[API changelog](https://api-docs.deepseek.com/updates/) dates the API introduction
to 2026-08-21; official HF metadata dates repository creation to 2026-08-31.
`release_date=2026-08` is consistent with both; they denote different events.

Manifest pins current model config/card, tokenizer, encoder documentation/code,
inference config/code and ViT/aligner code. The release HTML and HF metadata are
collection snapshots; revision-scoped HF metadata still contains mutable counters.
Only small sources were fetched, no checkpoint weights.

## Difference from text Flash and later V4.1

The model card says visual modules were added to the Flash architecture and
continued training enabled vision. This differs from the later V4.1 family's
multimodal-from-start training claim. The extraction uses `fusion=projection_mlp`:
32-layer ViT, width 1024, 16 heads, patch 14, 2D RoPE, RGB input;
3×3 spatial merge and two-layer GELU aligner project into width 4096. Image-token
budget is 384, min pixels 147456 and max aspect ratio 8 in current config.

The 43-layer text stack retains CSA/HCA, 256 routed experts, top-6 + 1 shared,
mHC and three-block DSpark. Normalization epsilon is 1e-20. Current Gate code
shows that image tokens use modality-specific score routing even in the first
three text-hash-routing layers. Image positions are constructed by the reference
preprocessor; no image vocabulary ID is asserted from sibling configs.

Current card reports text-agent DeepSWE 54.4 → 59.3 relative to Flash-0731 and
multimodal Chartography 64.3 / ZeroBench Pass@5 35.0. The comparison's text-only
Flash baseline ignores multimodal inputs on the dagger-marked evaluations;
these are vendor-reported benchmark results, not independent reproductions.

Current encoder confirms low/high/max effort with low default, exact prompt
prefixes, validation and V4 DSML tool syntax. The vLLM tool parser is explicitly
`deepseek_v4`. No training method for effort control is published.

## Unknowns and checks

Full vision/draft-inclusive parameters and activated counts remain UNKNOWN;
284B/13B text-Flash numbers are not substituted for this modified checkpoint.
Continued-training objective, budget, dataset, optimizer, freezing schedule and
alignment algorithm are undisclosed. Training precision is not inferred from
FP4+FP8 deployment formats.

Schema validation, bilingual deterministic rendering and source SHA verification
passed. Exact UNKNOWN leaf count: 20; no `inferred_fields` entries.

## Integration handoff

Proposed ROADMAP row: `DeepSeek-V4-Flash-Vision-Exp | extracted | 2026-08 |`
with notes: added ViT+MLP and continued training, retained Flash text backbone,
full parameter accounting undisclosed.

Glossary edges: CSA/HCA, DeepSeekMoE, auxiliary-loss-free routing, mHC,
reasoning effort, hybrid thinking, YaRN and speculative decoding. No generic
new ViT glossary page is needed for this one checkpoint. Do not add inherited
text-Flash GRPO, Muon, token-budget or quantization-training assertions.
