---
name: extract-engine
description: Record one engine release snapshot (vLLM, SGLang, verl, VeOmni, Megatron-LM, Megatron-Bridge) as data/extracted/engines/<engine>-<tag>.json, validated against src/llm_tech_matrix/engine_schema.py and rendered to .md / .zh.md. Use when the user asks to "snapshot vLLM", "do the sglang-v0.5.19 snapshot", "refresh the engine records", or similar engines-track work.
---

# extract-engine

You are recording what an **engine** implements at one pinned release, so that synthesis
can join it with the model records. Read [`docs/engines/overview.md`](../../../docs/engines/overview.md)
(design) and [`docs/engines/schema.md`](../../../docs/engines/schema.md) (fields) before starting.

## Cardinal rules

1. **No hallucination.** Unsourced values are `"[Unknown/Not Disclosed]"`. A parser named
   `deepseek_v4` is not evidence that DeepSeek-V4 uses it; a backend named `*_DSV4` is not
   evidence that CSA is implemented. Only what code or docs at the pinned commit state.
2. **Evidence on every claim.** Use GitHub `blob/<sha>/<path>#L<n>` URLs (or the release page
   for release-note claims). The schema rejects populated serving fields, parallelism
   entries, model rows or technique rows without evidence.
3. **Pinned upstream only.** Resolve the tag to a SHA with the GitHub API and cite
   `vllm-project/vllm`, `sgl-project/sglang`, `verl-project/verl`, `ByteDance-Seed/VeOmni`,
   `NVIDIA/Megatron-LM` (tags `core_vX.Y.Z`, on release branches) or `NVIDIA-NeMo/Megatron-Bridge`.
   Never a fork, never a local path, never `main`. Sibling checkouts (`../vllm`) are reading
   aids only, and may be forks at an arbitrary commit — `docs/design/hisparse.md` is on
   vLLM `main` but not in `v0.29.0`.
4. **Code outranks docs.** Registries (model, parser, quantization, attention backend,
   speculative methods) are exhaustive and reproducible; docs lag. When they disagree, record
   both and add an open question.

## Procedure

1. **Pick the snapshot** from [`tasks/ENGINES.md`](../../../tasks/ENGINES.md): the latest
   non-prerelease tag at snapshot time (quarterly), or the tag an on-demand refresh needs.
   Slug: `<engine>-<tag>` lowercase.

   ```bash
   gh api repos/<org>/<repo>/git/ref/tags/<tag> -q '.object.type + " " + .object.sha'
   # type "tag" = annotated tag (SGLang): dereference it, the object sha is NOT the commit
   gh api repos/<org>/<repo>/git/tags/<tag-object-sha> -q .object.sha
   gh api repos/<org>/<repo>/releases/tags/<tag> -q .published_at   # release date
   gh api "repos/<org>/<repo>/git/trees/<commit-sha>?recursive=1"    # find registries & docs
   ```

2. **Register sources** under the engines track, pinned to the SHA:

   ```bash
   uv run python -m llm_tech_matrix.sourcing --track engines add <slug> \
     --kind repo_file --name model_registry \
     --url https://raw.githubusercontent.com/<org>/<repo>/<sha>/<path> --filename <path> \
     --description "..."
   uv run python -m llm_tech_matrix.sourcing --track engines add <slug> \
     --kind release_notes --name release_notes \
     --url https://api.github.com/repos/<org>/<repo>/releases/tags/<tag> --filename release_notes.md
   ```

   Register specific files, not the repository: model registry, supported-models docs, the
   speculative / quantization / attention / cache / parallel configs, parser registries, and
   the design docs you will cite. For `release_notes`, the fetcher stores and hashes only the
   release `body`, because the API JSON carries mutable counters.

   If `fetch` or `add` reports failures, work from its `FETCH REPORT` block: each failed asset
   lists the expected and fetched sha256, keeps the new bytes as `<filename>.fetched` next to
   the untouched cached copy, and says what to check next. Never edit a recorded sha256 just to
   make it pass.

3. **Join against the model records.** For every `data/extracted/*.json`, take the HF
   `architectures[0]` from its cached or manifest `config.json`, and check it against the
   engine's native registry *and* its docs. Record one `model_support` row per architecture,
   including architectures that are **absent** (`support: not_found`, whole-file evidence).
   Absence is a snapshot fact, not a claim the model cannot run. Use `registered` for registry
   entries, `delegated` when the engine's sources hand HF model mapping to another tracked engine,
   and `model_specific` when there is no registry entry (or no registry, like verl) but
   code keyed on the architecture or its model_type exists.

   Registries differ: vLLM has a static table (`registry.py`); SGLang collects `EntryClass`
   from every module under `srt/models/`, so register the modules that declare your
   architectures and prove absence with `git grep <arch> <commit-sha> -- <models dir> docs`
   against a local upstream clone (reading the commit object, not the checkout). Megatron-LM has
   no HF-architecture registry at all: rows with an in-repo docs signal are `model_specific`,
   and the rest are `delegated` with `delegated_to: megatron-bridge-<tag>` (evidence: the docs
   sending HF conversion to Megatron-Bridge, after a whole-tree absence check). Record
   per-model facts — doc-stated parsers, `since_version` from release notes — in
   `model_details[]`, never on the architecture row.

4. **Fill the record.** Each claimed role needs its subobject (`serving` / `training` / `rl`).
   Record version requirements on the counterpart engine in `integrations[].version_constraints`,
   one entry per source, even when they disagree. Submodule pins count as a source: Megatron-Bridge
   pins Megatron-LM by commit, not by release tag.

   **Details.** Keep list fields as literal registry contents; keep prose fields to
   what design docs state. Fill `model_details[]` (`reasoning_parser` / `tool_call_parser` /
   `since_version`) only when docs or release notes state them for that specific model. Add `technique_support` only for glossary slugs the
   sources assert; name-based guesses go to `open_questions` instead.

   Compute `#L` anchors from the cached files rather than typing them — a small script that
   looks each quoted needle up and fails when it is missing keeps anchors honest.

5. **Validate and render.**

   ```bash
   uv run python scripts/validate_extractions.py          # schema + cross-links (model slugs, glossary slugs, filename, SHA)
   uv run python -m llm_tech_matrix.extraction.render_engine <slug>
   uv run python -m llm_tech_matrix.synthesis.index      # support matrix, adoption report, glossary "Implemented by" sections
   uv run python scripts/validate_registry.py             # CI fails if the generated files are stale
   uv run pre-commit run --all-files
   ```

   Never hand-edit the "Implemented by (engines)" glossary sections or the `engine-*.md`
   reports; change the record and regenerate.

6. **Update tasks.** Status in `tasks/ENGINES.md`; notes, resolved seed questions and open
   questions in `tasks/engines/<slug>.md`. If a model record carries an open question the
   snapshot answers, say so in the engine note — do not edit the model record from the
   engine side (layer boundary).

## When to push back

- Asked to mark a model "supported" because a README news item mentions it: record the news
  item, but code decides `support`.
- Asked to snapshot `main` or a local checkout: refuse; pick a tag.
- Asked to claim a role the snapshot's own sources do not document (e.g. `rl_post_training`
  for VeOmni, whose RL algorithms live in verl): refuse; record the relationship under
  `integrations[]` instead.
