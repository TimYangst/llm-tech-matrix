# Fill-in-Middle (FIM)

> 中文版：[fim.zh.md](./fim.zh.md)

**Slug:** `fim`
**Category:** training-objective
**One-line:** A pre-training data augmentation that randomly rewrites documents into "given prefix and suffix, predict the middle" form, giving autoregressive LMs a fill-in-the-blank capability without architectural changes.
**First introduced in:** [Efficient Training of Language Models to Fill in the Middle (Bavarian et al., OpenAI, 2022)](https://arxiv.org/abs/2207.14255)

## Description

A fraction of training documents are rewritten so that the autoregressive objective
predicts a middle span given a wrapped prefix and suffix. Two formats are standard:

- **PSM (Prefix-Suffix-Middle):** `<fim_begin> prefix <fim_hole> suffix <fim_end> middle <eos>`
- **SPM (Suffix-Prefix-Middle):** swapped ordering, sometimes preferred for tooling.

The original paper showed that with rates around 50% on code data, FIM can be added
during pre-training without measurable harm to next-token-prediction quality. Newer
work (e.g. DeepSeekCoder-V2, DeepSeek-V3) applies FIM at lower rates (~10%) at the
document level during data packing.

The capability matters for code editors, where "complete this region" is a more common
operation than "continue from the cursor."

## Reference materials

- Original paper: <https://arxiv.org/abs/2207.14255>
- DeepSeek-V3 application: <https://arxiv.org/abs/2412.19437> (Section 4.1)

## Used by

| Model             | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3       | PSM format, rate 0.1, applied at document level during pre-packing (no cross-sample attention masking).                                                                                                                                                                                                                                                                                                                                                                                             |
| DeepSeek-V4-Pro   | Inherits PSM format from DeepSeek-V3 (paper Section 4.1: 'we also inherit the token-splitting and Fill-in-Middle (FIM) strategies from DeepSeek-V3'). Rate not restated — assume V3's 0.1 unless V4 ablations land later.                                                                                                                                                                                                                                                                           |
| DeepSeek-V4-Flash | Same PSM inheritance as V4-Pro. Rate not restated.                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| GLM-4.7           | "the Fill-In-the-Middle training objective is applied to all source code data" (GLM-4.5 ARC paper §2.2). FIM is applied across the entire code corpus rather than at a fractional rate — distinct from DSV3's 10% PSM rate. Specific token format (PSM vs SPM) and special tokens not disclosed. GLM-5 inherits the same code pre-training pipeline ("Building upon the GLM-4.5 data pipeline" — GLM-5 paper §2.2) so FIM presumably carries over, but the GLM-5 paper does not separately confirm. |

## Related techniques

- _(none yet in this repo)_
