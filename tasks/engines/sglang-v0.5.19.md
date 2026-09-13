# SGLang v0.5.19

Slug: `sglang-v0.5.19`
Engine: `sglang` (upstream `sgl-project/sglang`)
Tag: `v0.5.19` is an **annotated** tag: tag object `59f20bf` dereferences to commit
`0bcd822377da7b5718e674eaf9c870d349424dd1` (published 2026-09-05).
Snapshot: 2026-09-12 (2026-Q3, phase E2)
Status: `extracted`

## Sources

Authoritative list: `data/sources/engines/sglang-v0.5.19/manifest.json` (38 assets, repo files
pinned to the commit).

SGLang has **no static model table**. `srt/models/registry.py` imports every module under
`srt/models/` and collects each module's `EntryClass`. So the sources include the 10 model
files that declare our architectures, the 5 NextN / MTP / EAGLE3 draft files, and
`configs/model_config.py`, which remaps targets to draft architectures.

Absence claims (DeepSeek-V4.1-Flash, GLM-5.3-Flash, Qwen3.8-Flash-Next) were verified with
`git grep` against the commit object in the local upstream clone, across `srt/models/` and
`docs/`. The clone's checkout was not changed. The committed evidence is the registry file plus
the models tree at the commit.

**Reproducibility caveat:** `release_notes.json` is GitHub API output with mutable counters, so
its sha256 will drift.

## What E2 was for: stress-testing engine schema v1

The first cross-engine record broke one v1 assumption, now fixed in **engine schema v2**:

- **Parsers and `since_version` are per model, not per architecture.** SGLang's docs map Kimi
  K2 Thinking to the `kimi_k2` reasoning and tool parsers, while DeepSeek-V3 (same
  `DeepseekV3ForCausalLM`) gets none. The release notes list Qwen3.8-27B as new in v0.5.19,
  although `Qwen3_5ForConditionalGeneration` was already supported for Qwen3.5-27B and 3.6-27B.
  v2 moves those three fields into `model_support[].model_details[]`
  (`scripts/migrate_engine_v1_to_v2.py` migrated `vllm-v0.29.0`).

Held without change:

- **"Native registry"** generalized from vLLM's static table to SGLang's `EntryClass`
  declarations; only the docstring changed.
- **`documented`** still fits, but SGLang's docs are family-level and tell users to search the
  code, so it is a weak signal here. This is recorded per row and in `open_questions`.
- **Role subobject, parallelism dimensions, integrations, technique rows:** no vLLM-shaped
  fields surfaced.

## Cross-engine comparison with `vllm-v0.29.0` (same quarter)

| Architecture                             | vLLM v0.29.0     | SGLang v0.5.19        |
| ---------------------------------------- | ---------------- | --------------------- |
| `DeepseekV41ForCausalLM` (V4.1-Flash)    | absent           | absent                |
| `Glm5NextForConditionalGeneration`       | absent           | absent                |
| `Qwen4ExpForConditionalGeneration`       | **native (new)** | **absent**            |
| `KimiK25ForConditionalGeneration` drafts | none recorded    | EAGLE3 / EAGLE3.1 MLA |
| `DeepseekV4ForCausalLM` drafts           | MTP, DSpark      | MTP (NextN), DSpark   |
| every other extracted architecture       | native           | native                |

- **Qwen3.8-Flash-Next is the first adoption split.** vLLM added it in v0.29.0 (2026-09-09).
  SGLang v0.5.19 (2026-09-05) has no implementation, and whether SGLang has one at all needs a
  later snapshot.
- **Both engines reuse DeepSeek code for GLM-5, but in different places.** vLLM implements
  `GlmMoeDsaForCausalLM` inside its `deepseek_v32` module; SGLang subclasses
  `DeepseekV2ForCausalLM` in `glm4_moe.py`.
- **IndexShare / IndexCache reaches the model differently.** vLLM documents it behind
  `--hf-overrides '{"use_index_cache": true, ...}'` for DeepSeek-V3.2. SGLang reads
  `index_topk_freq` / `index_topk_pattern` from the config and calls it native in GLM-5.2.
- **DeepSeek-V4 DSpark behaves the same in both.** Draft weights come from the target
  checkpoint. SGLang additionally documents in code that a DSpark-bundled checkpoint "may also
  carry MTP layers" and picks DSpark or NextN by the selected algorithm. This is engine-side
  evidence for the `deepseek-v4-flash-0731` MTP-vs-DSpark open question; the model record is not
  edited from here.
- **Docs lag code in both, differently.** vLLM has registered-but-undocumented architectures.
  SGLang's family table omits DeepSeek V3.2/V4, GLM-4.7/5.x and Kimi K2.5/K3 entirely, and its
  speculative-decoding guide never mentions DSpark.
- **CSA/HCA is still unasserted in both.** SGLang's hint is stronger (a `dsv4` backend whose
  deprecated alias is `compressed`, and HiSparse describing "C4 KV" / "c4_indexer" / "C128 KV"),
  but no source names the technique.
- **SGLang exposes more parallelism knobs:** DP attention, `attn_cp_size`, `moe_dp_size`, and
  Megatron-style LayerNorm sequence parallelism for Qwen3 dense. It also documents RL-facing
  features (sleep/wake, weight refit) that no v2 field holds yet.

## Open questions

See `data/extracted/engines/sglang-v0.5.19.json` `open_questions`. Worth tracking:

- **GLM-5.3 cookbook vs code.** The release notes advertise a GLM-5.3 deployment guide, yet no
  code at the tag mentions `Glm5NextForConditionalGeneration`.
- **`NEXTN` is advertised as a builtin speculative algorithm but is not in the enum.**
- **The Kimi K3 DSpark draft source** is unknown in both engines.
