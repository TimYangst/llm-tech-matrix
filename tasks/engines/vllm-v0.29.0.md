# vLLM v0.29.0

Slug: `vllm-v0.29.0`
Engine: `vllm` (upstream `vllm-project/vllm`)
Tag: `v0.29.0` → commit `98dff2a81d747d1dba01a47f939f48c3526d4206` (published 2026-09-09)
Snapshot: 2026-09-12 (2026-Q3, pilot E1)
Status: `extracted`

## Sources

Authoritative list: `data/sources/engines/vllm-v0.29.0/manifest.json` (24 assets). Every repo
file is a raw URL pinned to the tag commit; release notes come from the GitHub releases API.

Selected for the three track questions:

- **Support matrix:**
  - `vllm/model_executor/models/registry.py` (the native registry, exhaustive)
  - `docs/models/supported_models.md` (docs with LoRA / PP columns)
  - the release notes
- **Technique support:**
  - `vllm/config/speculative.py`, the speculative decoding README and `mtp.md`
  - `docs/features/index_cache.md`
  - the attention backend registry, the quantization registry, `vllm/config/cache.py`
- **Serving surface:**
  - the architecture overview, prefix caching and hybrid KV cache manager design docs
  - the disaggregated prefill and encoder guides
  - the reasoning and tool-call parser registries and guides
  - `vllm/config/parallel.py`

Considered but excluded:

- `docs/design/hisparse.md` was named as a candidate in the E0 docs, but it is **not in
  `v0.29.0`**: it landed on `main` on 2026-09-12 (commit `e19a3e1`). The local `../vllm`
  checkout is newer than the tag, which is exactly why local clones are not evidence.
- Model implementation files (`deepseek_v4.py` etc.) are too large for the value they add
  here. The registry and the speculative config already carry the join facts.

**Reproducibility caveat:** `release_notes.json` includes mutable fields (asset download
counts, `updated_at`), so its sha256 will drift. The release-notes body is what is cited.

## Seed questions from `tasks/ENGINES.md`

- **DSpark (answered in part).** `dspark` is a SpeculativeMethod in v0.29.0.
  - For DeepSeek-V4 the draft weights load from the target checkpoint (`DSparkDraftModel`),
    and DSpark forces parallel drafting.
  - Adaptive verification is documented as DSpark-only.
  - The `num_speculative_tokens: 7` vs trained γ=5 question from `deepseek-v4-flash-0731` is
    **not settled**. A strict `num_speculative_tokens == block_size` check exists only in the
    Qwen3-Omni DSpark validator. For DeepSeek-V4, `num_speculative_tokens` defaults to the draft
    config's `n_predict` when unset, and no V4-specific validation was found in
    `speculative.py`.
- **DeepSeek-V4.1-Flash (answered).** `DeepseekV41ForCausalLM` is **not** in the v0.29.0 native
  registry or docs. The tag predates the model by one day (vLLM 2026-09-09, V4.1 2026-09-10).
  Other loading paths were not assessed.
- **Sparse attention (answered in part).**
  - DSA is implemented: `DeepseekV32ForCausalLM` and `GlmMoeDsaForCausalLM` share the
    `deepseek_v32` module, and there are several sparse-MLA backends.
  - IndexShare/IndexCache is implemented as `--hf-overrides use_index_cache`.
  - CSA/HCA is **not asserted**: the DSV4-named backends and ROCm "C4" kernels are name-level
    hints only.
- **Parsers (answered: the gap is the engine's too).** `deepseek_v4` / `kimi_k3` parsers exist
  in both registries, but no v0.29.0 doc maps them to a model. The only doc-stated mappings
  for our models are:
  - Qwen3 series → `qwen3` reasoning parser
  - GLM-4.7 → `glm47` tool parser

## Findings worth carrying

- **Docs lag code:**
  - `Qwen3_5MoeForCausalLM` (Qwen3.8-2.4T-A95B) and `Qwen4ExpForConditionalGeneration`
    (Qwen3.8-Flash-Next) are registered but not in `supported_models.md`.
  - DeepSeek-V4's LoRA column is empty although the release adds DeepSeek V4 LoRA (#53361).
- **Absent at this snapshot:** DeepSeek-V4.1-Flash and GLM-5.3-Flash
  (`Glm5NextForConditionalGeneration`).
- **Adoption timestamp:** Qwen3.8-Flash-Next arrived in v0.29.0 (#53896, published
  2026-09-09). The model record dates it `2026-08`, and its HF repo was created on 2026-08-24.
  This is the first `since_version` data point for the adoption-lag question.
- **Vendor-reuse echo on the engine side:** GLM-5's `GlmMoeDsaForCausalLM` is implemented inside
  vLLM's DeepSeek-V3.2 module and shares its MTP path (`DeepseekV32MTPModel`).
- **Kimi K3:** vLLM recognizes a `K3DSparkModel` draft and runs K3 DCP with DSpark, while the
  Kimi K3 model record says its trained EAGLE-3 draft was withheld. Where a K3 DSpark draft
  comes from is open.

## Schema notes from the pilot (feed into v1 → v2)

- **Absence rows were needed.** v1 records `in_native_registry: false` with whole-file evidence.
  Without them the support matrix couldn't distinguish "not supported yet" from "not checked".
- **Glossary gap for serving formats.** MXFP4 / NVFP4 serving support has no glossary entry
  (`fp4-qat` is a training recipe), so it can't become a typed edge yet.
- **Non-native loading paths** (Transformers backend, plugins) are out of v1. Revisit if absent
  architectures turn out to run anyway.
- **`speculative_decoding_methods` collapses the MTP model-type sub-literal to `mtp`.** The
  per-family MTP types are captured in `technique_support` and `model_support` instead.
