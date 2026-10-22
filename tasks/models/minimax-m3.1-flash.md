# MiniMax M3.1 Flash

Slug: `minimax-m3.1-flash`
Family: `minimax-m3`
Status: `sourced; extraction blocked by schema`
Snapshot: `2026-10-22`

## Sources

Authoritative fetched bytes and SHA256 are registered in `data/sources/minimax-m3.1-flash/manifest.json`.

- [Official launch announcement, October 19, 2026](https://www.minimax.io/blog/minimax-m31f).

## Findings

The dated vendor announcement says M3.1 Flash is available through the API, M Plan and MiniMax Code; model weights will be released later. It is therefore **closed/API-only at this evidence snapshot**, not an open-weight successor. The vendor reports more aggressive sparsity, faster inference and stronger agent/coding/computer-use/cybersecurity capabilities. None of these claims discloses a parameter count, FFN architecture, optimizer or training-token budget. Do not inherit M3 dimensions or MSA settings.

## Extraction blocker

Schema v8 requires `architecture.ffn.ffn_type` to be `dense`, `moe` or `hybrid` and cannot encode `[Unknown/Not Disclosed]` for that enum. The announcement does not disclose this architecture. An honest canonical record needs a separate schema decision allowing unknown FFN type, or future primary architectural evidence. No fabricated extraction is added.

## Follow-up

- [ ] Check for an actual official weights release and pin a checkpoint only after it exists.
- [ ] Resolve unknown architecture representation before attempting a closed canonical extraction.
- [ ] Keep preview/API aliases and eventual open checkpoint identities separate until official evidence identifies their relation.
