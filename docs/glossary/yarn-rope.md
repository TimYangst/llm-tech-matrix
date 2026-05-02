# YaRN RoPE scaling

**Slug:** `yarn-rope`
**Category:** position-embedding
**One-line:** A RoPE position-encoding extension method that interpolates frequencies non-uniformly across head dimensions, enabling much longer context windows than the model was originally trained on with minimal fine-tuning.
**First introduced in:** [YaRN: Efficient Context Window Extension of Large Language Models (Peng et al., 2023)](https://arxiv.org/abs/2309.00071)

## Description

Standard RoPE encodes absolute position via per-dimension rotation frequencies. Naïve
context extension (linearly interpolating frequencies, "PI") works but degrades quality;
"NTK-aware" interpolation does better but still hits limits. YaRN observes that
different RoPE dimensions encode position at different scales, and applies different
interpolation strategies per dimension band:

- **High frequency** dimensions: extrapolate (do nothing) — they already average out.
- **Low frequency** dimensions: interpolate (PI-like) — they need to fit.
- **Middle frequencies**: a smooth ramp between the two regimes.

YaRN also rescales attention temperature (`mscale`) to compensate for the larger
effective sequence length. The extension typically requires only a short fine-tune
(thousands of steps) to recover quality.

## Reference materials

- Original paper: <https://arxiv.org/abs/2309.00071>

## Used by

| Model | Variation / details |
|---|---|
| DeepSeek-V3 | Applied **only** to the decoupled RoPE key in MLA (`k_t^R`). Two-phase extension: 4K→32K→128K, 1000 steps each. Config: `factor=40` (40 × 4096 original = 163840 max), `beta_fast=32`, `beta_slow=1`, `mscale=1.0`. |

## Related techniques

- [MLA](./mla.md) — DeepSeek-V3's MLA carries RoPE only on a small decoupled key vector, so YaRN is applied surgically rather than across all KV
