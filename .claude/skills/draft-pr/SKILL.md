---
name: draft-pr
description: Draft the title and description for a pull request from the current branch's commits and diff, and save it to .claude/drafts/pr/ as a dated Markdown file. Use when the user asks to "draft a PR", "write the PR description", "open a PR", "prepare a PR for this branch", or similar. Optionally calls `gh pr create` with the draft as the body. Do NOT use for force-pushing, amending merged PRs, or editing PRs that already have substantive review activity.
---

# draft-pr

You are drafting a high-signal pull request for the user. The user wants:

1. A short, accurate **title** (under 70 characters).
2. A **description** that summarizes the *theme* across all commits in
   the branch — not just the most recent commit — plus a checklist of how
   the user can verify the change.
3. The draft saved to a file under `.claude/drafts/pr/` (gitignored, per
   the project's `.gitignore`) so the user has a durable artifact.

The skill is invoked any time the user says things like "draft a PR",
"write the PR description", "open a PR for this branch", or "prepare a PR".

## Output location and naming

Drafts go to `.claude/drafts/pr/`. Filename format:

- **No PR exists yet for the branch**: `<YYYY-MM-DD>-<branch-slug>.md`,
  where `<branch-slug>` is the current branch with `/` and other unsafe
  characters replaced by `-` (e.g. `tingyang/proj/lint-formatter` →
  `tingyang-proj-lint-formatter`).
- **PR already exists** (detected via `gh pr view --json number,state -q .number`):
  `<YYYY-MM-DD>-pr<N>.md`. If the PR has already been merged or closed,
  do NOT overwrite an existing file — bail out and tell the user.

Use today's date in the user's local timezone (already exposed in your
context as `currentDate`). If for any reason it's not available, run
`date +%Y-%m-%d`.

## Procedure

1. **Gather context** in parallel:

   - `git rev-parse --abbrev-ref HEAD` — current branch name.
   - `git log --oneline origin/main..HEAD` (or whatever base branch is
     configured — fall back to `main` if `origin/main` is missing).
   - `git diff --stat origin/main...HEAD` — overall scope.
   - `git diff origin/main...HEAD` — the actual changes (read selectively
     if the diff is large).
   - `gh pr view --json number,state,title,body 2>/dev/null` — does a PR
     already exist?
   - `git log -n 5 --pretty=format:"%s"` on `main` — match repo commit
     style.

2. **Draft the title.**

   - Under 70 characters. Use the imperative or descriptive form — match
     what `git log` on `main` shows (e.g. `Ting: chore - ...`,
     `extract: deepseek-v3`).
   - Title reflects the *theme* across the branch's commits, not the most
     recent one. If the branch has 5 commits adding lint + format + CI,
     the title is "set up lint/format/CI", not "add Gemini config".
   - Avoid trailing punctuation; avoid emoji unless the user asks.

3. **Draft the description.** Follow this structure:

   ```markdown
   ## Summary

   <2–5 bullets describing what the PR does and *why*. Mention each
   substantive change. If the branch makes multiple distinct changes,
   group them logically. Link to the relevant files where useful.>

   ## Notes for review

   <Optional. Anything reviewers should know that isn't obvious from the
   diff: behavior changes, follow-ups deliberately deferred, surprising
   choices and their reasoning, large mechanical diffs to skim past.>

   ## Test plan

   - [ ] <How to verify each change. Concrete commands or steps the
         reviewer can run.>
   ```

   Keep it crisp. The summary explains *why*; the diff shows *what*. If
   the branch contains a large mechanical diff (e.g. a unified format
   pass), call it out under "Notes for review" so reviewers don't waste
   attention on whitespace.

4. **Honor project conventions.**

   - This repo's commit messages typically start with `Ting: <type> - ...`
     (`chore`, `ci`, `docs`, `extract`, `schema`, `report`). Match the
     style for the title.
   - Don't invent a "Closes #N" / "Fixes #N" link unless the user
     explicitly mentions an issue.

5. **Write the draft file.** Create `.claude/drafts/pr/` if missing. Write
   the file as:

   ```markdown
   # <Title>

   <Body>
   ```

   First-line H1 must equal the title verbatim — this lets `gh pr create`
   readers / future tools parse the file unambiguously.

6. **Show the user the draft.** Print:

   - The full path of the draft file.
   - The title.
   - The body (verbatim).

7. **Offer the next step.** Ask the user one of:

   - "Open the PR now? I'll run `gh pr create --title '...' --body-file <path>` and rename the draft to include the PR number."
   - Or, if they want to edit first: tell them to edit the file and
     re-invoke the skill — the skill will re-read the file's H1 as the
     title and the rest as the body.

   Do NOT call `gh pr create` without explicit confirmation, even if the
   user originally said "open a PR" — they may want to read the draft
   first.

8. **After `gh pr create` succeeds** (only if the user confirms):

   - Capture the PR number from the `gh` output.
   - Rename the draft file to `<YYYY-MM-DD>-pr<N>.md`.
   - Print the PR URL to the user.

## Hard constraints

- **Never push or force-push** — the user controls when to push. They've
  usually already pushed by the time they invoke this skill.
- **Never amend merged commits.**
- **Never invent issue numbers, "Co-Authored-By" lines for people who
  didn't co-author, or fake test results in the test plan.**
- **Don't fabricate a roadmap impact** — if you don't know whether the
  change unblocks something, don't claim it does.
- **Drafts are local artifacts.** Don't commit them — the `.gitignore`
  excludes `.claude/drafts/`.

## When to refuse / push back

- If the branch has zero commits ahead of base: tell the user, don't
  draft.
- If the branch has uncommitted changes: warn the user and ask whether
  to include them (they might need a commit first).
- If a PR already exists and was merged: refuse to overwrite the draft
  file; suggest a follow-up PR instead.
