# MiniMax-Music3

Slug: `minimax-music3` · Family: MiniMax · Status: `extracted` (media schema v1).

Canonical technical record: [JSON](../../data/extracted/media/minimax-music3.json),
[English](../../data/extracted/media/minimax-music3.md),
[中文](../../data/extracted/media/minimax-music3.zh.md).
Source list: [manifest](../../data/sources/minimax-music3/manifest.json).

## Source scope

Pinned official HF revision `fbdf52fbaaca799592917417eb05f1899f1255ec`.
Registered card, license, global/local language-model, condition encoder,
flow-matching transformer, vocoder, scheduler, root config and inference example.
No weights downloaded. The registered official launch article dates release
August 13, 2026; earlier HF repository creation is not used as the release date.

## Resolved

- Model is text-to-music, combining hierarchical autoregressive RVQ prediction
  with continuous hidden-state-conditioned Flow Matching and Flow-VAE synthesis.
- Card's component counts are 8B Global LLM, 0.6B Local LLM, 2.4B Flow Matching
  and 123M decoder. Do not mistake HF's partial tensor count for a pipeline total.
- The `/v1/audio/speech` serving route alone does not make Music3 a TTS model.

## Open questions

- Card/API output says 32 kHz; diffusers vocoder and condition-encoder configs say
  44.1 kHz output. Both facts are preserved pending path-specific verification.
- Card advertises five-minute songs but separately caps generation at 9000
  acoustic frames at 25 frames/s. Do not assert six-minute support from arithmetic.
- Official launch article says Qwen3.5-8B initialization; checkpoint card says
  Qwen3-8B and config names Qwen3ForCausalLM. Preserve that provenance conflict.
- Training data totals, optimizer and compute are not disclosed.
- No runtime/quality or GPU-memory claims were independently tested.

Tracking: [refresh state](../deepseek-minimax-refresh.md), T05.
