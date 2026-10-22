# Development guide

How to set up your environment, run lint/format/CI locally, and open a
pull request that the project's automation will accept.

For the *content* contract (what gets extracted, how files are named,
schema versioning), see [`conventions.md`](./conventions.md). For the
project's cardinal rules, see [`../CLAUDE.md`](../CLAUDE.md).

## Tooling

| Tool                                                             | Used for                       | Source of truth            |
| ---------------------------------------------------------------- | ------------------------------ | -------------------------- |
| [`uv`](https://docs.astral.sh/uv/)                               | Python and dependency mgmt     | `pyproject.toml`           |
| [`ruff`](https://docs.astral.sh/ruff/)                           | Python lint + format           | `[tool.ruff]` in pyproject |
| [`mdformat`](https://mdformat.readthedocs.io/)                   | Markdown format (GFM, tables)  | `.mdformat.toml`           |
| [`pre-commit`](https://pre-commit.com/)                          | Git hook framework             | `.pre-commit-config.yaml`  |
| GitHub Actions                                                   | Presubmit CI on PR / push main | `.github/workflows/ci.yml` |
| [Gemini Code Assist](https://github.com/apps/gemini-code-assist) | AI code review on PR           | `.gemini/`                 |

Python is pinned to **3.13** by `.python-version` and `requires-python` in
`pyproject.toml`.

## Style guides

We follow Google's style guides as the default rubric, with two pragmatic
adjustments enforced by tooling:

- **Python** — [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
  via `ruff`. Line length **100** (relaxed from pyguide's 80 to read
  comfortably with PEP 604 unions and longer type hints). Docstrings use
  Google convention (`Args:`, `Returns:`, `Raises:`); they are not
  *required* on every symbol yet, but where present they must follow
  Google style. See `[tool.ruff.lint]` in `pyproject.toml` for the exact
  rule selection.
- **Markdown** — [Google Markdown Style Guide](https://google.github.io/styleguide/docguide/style.html)
  via `mdformat` + `mdformat-gfm` + `mdformat-tables` + `mdformat-frontmatter`.
  Source-level formatting (line breaks, table padding, list markers) is
  dictated by the formatter — don't edit them by hand; let the formatter
  rewrite on save.

Pre-commit excludes all Markdown beneath `data/extracted/` and `data/reports/`
from mdformat. These are renderer/generator outputs for all three tracks. Use the
matching generator rather than formatting them directly.

## First-time setup

```bash
# Sync the venv (installs dev deps from [dependency-groups.dev])
uv sync

# Install the git pre-commit hook so every commit is auto-formatted
uv run pre-commit install
```

After this, every `git commit` runs the hooks defined in
`.pre-commit-config.yaml`. If a hook makes changes (e.g. mdformat fixes a
table), the commit is aborted; re-stage the files and commit again.

## Day-to-day commands

```bash
# Run all hooks across the entire repo (same as what CI runs)
uv run pre-commit run --all-files

# Lint + format Python only
uv run ruff check --fix .
uv run ruff format .

# Format maintained Markdown, honoring generated-output exclusions
uv run pre-commit run mdformat --all-files

# Validate LLM/VL, engine and media records, plus generated registry/report outputs
uv run python scripts/validate_extractions.py
uv run python scripts/validate_registry.py
uv run python -m unittest discover -s tests -v
```

Adding a new dependency:

```bash
uv add <pkg>             # runtime dependency
uv add --dev <pkg>       # dev-only dependency
```

After changing dev tooling versions, bump the corresponding `rev:` in
`.pre-commit-config.yaml` (or run `uv run pre-commit autoupdate`).

## What CI runs on every pull request

`.github/workflows/ci.yml` runs a single `quality` job on Ubuntu:

1. `uv sync --frozen` — installs from `uv.lock`.

2. `uv run pre-commit run --all-files --show-diff-on-failure` — same
   hooks you run locally.

3. `uv run python -m unittest discover -s tests -v` — media evidence and generated-view regression checks.

4. `uv run python scripts/validate_extractions.py` — re-validates every
   `data/extracted/*.json` against `src/llm_tech_matrix/schema.py`, and every
   `data/extracted/engines/*.json` against `src/llm_tech_matrix/engine_schema.py` plus
   its cross-links. Media records in `data/extracted/media/` validate against
   `media_schema.py`, including evidence/source manifests and generated bilingual
   views/index freshness. This is the gate for the **schema strictness** cardinal rule.

5. `uv run python scripts/validate_registry.py` — controlled vocabulary and generated report freshness.

## AI code review (Gemini Code Assist)

[Gemini Code Assist for GitHub](https://github.com/apps/gemini-code-assist)
can provide advisory PR reviews when installed for the repository. To enable it:

1. Visit https://github.com/apps/gemini-code-assist.
2. Click **Install** and select the target repository.
3. Open or push to a PR and inspect the actual review activity.

The bot reviews against `.gemini/styleguide.md`, which encodes the
project's cardinal rules and layer boundaries so its feedback stays
project-specific instead of generic. `.gemini/config.yaml` controls
severity thresholds and ignore patterns.

The review is advisory — it does not block merge. Treat its suggestions
like any other reviewer's: accept good ones, ignore noisy ones.

## GitHub identity

Commit identity (`git config user.email`), SSH authentication and GitHub CLI/API
login are separate settings. Verify the CLI login used for PR operations with
`gh api user --jq .login`. This checkout has a local `git gh` alias that uses a
repository-scoped CLI configuration; use `git gh api user --jq .login` and
`git gh pr ...` here. Other clones need their own login/alias setup; Git config
and authentication files are not committed.

## Pull request conventions

### Drafting

The `draft-pr` skill (`.claude/skills/draft-pr/`) produces a title +
description from the branch's commits and diff and saves it to
`.claude/drafts/pr/<YYYY-MM-DD>-...md`. Drafts are gitignored.

### Title

- Under **70 characters**.
- Describe the *theme* across all commits in the branch, not the latest
  commit alone.
- Use the same `<type>` prefix as commit messages where it fits
  (`chore`, `ci`, `docs`, `extract`, `schema`, `report`).

### Body structure

```markdown
## Summary

<2–5 bullets on what changes and *why*. The diff shows what; the
summary explains why.>

## Notes for review

<Optional. Large mechanical diffs to skim past, surprising choices,
deliberately deferred follow-ups.>

## Test plan

- [ ] <Concrete commands or steps a reviewer can run.>
```

### Commit messages

Project history uses `Ting: <type> - <imperative description>`, e.g.:

- `Ting: chore - add ruff/mdformat/pre-commit infrastructure`
- `Ting: extract Qwen3-235B-A22B (Qwen flagship MoE)`
- `Ting: schema v3 - context_extension + multi-stage alignment + inference_modes`
- `Ting: ci - add GitHub Actions presubmit workflow`

`<type>` mirrors the PR title prefix. For data-only changes (a new
extraction), the `<type>` may be `extract` and the description is the
model identifier.

Don't squash extraction commits with code or schema commits — review of
JSON is faster when the diff is just JSON. See
[`conventions.md`](./conventions.md#commit-conventions).

## What lives where

```
.pre-commit-config.yaml      hook definitions
.mdformat.toml               markdown formatter config
.gemini/config.yaml          Gemini Code Assist behavior
.gemini/styleguide.md        review rubric (cardinal rules + style)
.github/workflows/ci.yml     presubmit CI
scripts/validate_extractions.py   all record contracts and media views (CI)
scripts/validate_registry.py      vocabulary and generated synthesis checks (CI)
tests/test_media.py              media evidence/rendering regressions (CI)
pyproject.toml               [tool.ruff.*] lint + format config
.claude/skills/draft-pr/     skill for PR drafting
docs/conventions.md          data-side conventions (naming, schema log)
docs/development.md          this file
CLAUDE.md                    cardinal rules + project orientation
```

## When something feels off

- A hook keeps changing the same file every commit → check
  `.mdformat.toml` and `.pre-commit-config.yaml`; the most common cause
  is a CRLF/LF mismatch or a plugin defaulting to a stricter mode.
- CI fails but formatting hooks pass → run both validators and the media regression tests above; these are separate CI steps.
- Gemini bot doesn't show up on a PR → confirm the app is installed and
  scoped to this repo; inspect its current service/account limits.
- `validate_extractions.py` rejects a JSON you just wrote → don't loosen
  the schema. Either fix the JSON or, if the schema genuinely needs a
  new field, follow the schema-versioning steps in
  [`conventions.md`](./conventions.md#schema-changelog).
