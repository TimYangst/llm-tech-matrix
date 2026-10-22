# MiniMax-H3

Slug: `minimax-h3` · Family: MiniMax · Status: `extracted` (media schema v1).

Canonical technical record: [JSON](../../data/extracted/media/minimax-h3.json),
[English](../../data/extracted/media/minimax-h3.md),
[中文](../../data/extracted/media/minimax-h3.zh.md).
Source list: [manifest](../../data/sources/minimax-h3/manifest.json).

## Source scope

Pinned official HF revision `42ed227ee7df40d41602854ae760620d6eb651fe`.
Registered card, license, both task-family transformer configs, visual/audio VAE,
text encoder, video/audio schedulers and pipeline index. No weights downloaded.
The license explicitly dates public release August 2, 2026; the repository's
July creation is not used as the release date.

## Resolved

- H3 is a joint audio/video generative system, not the next MiniMax language-model
  generation. Its released base belongs in the media track.
- Both FL2VA and Ref2VA base weights are released. Their transformer configs are
  byte-identical at this revision; conditioning differs by task family.
- 33B counts the Omni-Transformer including approximately 13B AdaLN branches,
  excluding the separate Qwen3-VL-32B encoder and VAEs.
- Open base generates 768p. Context-IR and Regenerate-2K are hosted components,
  excluded from the release; the complete product is classified `mixed`.
- Native sparse-attention training does not mean the initial public inference
  release contains sparse kernels: the card explicitly says full attention only.

## Open questions

- Exact pretraining objective, solver, optimizer, data mix and compute are not
  disclosed by the registered sources.
- No complete encoder + transformer + VAE parameter accounting is published.
- No inference validation was run; serving and output claims are source-derived.

Tracking: [refresh state](../deepseek-minimax-refresh.md), T05.
