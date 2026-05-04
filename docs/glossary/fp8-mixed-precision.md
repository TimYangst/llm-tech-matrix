# FP8 mixed precision (DeepSeek-V3 variant)

**Slug:** `fp8-mixed-precision`
**Category:** quantization
**One-line:** A training-precision recipe that runs compute-density GEMMs in FP8 (E4M3) with fine-grained tile/block scaling, while keeping precision-sensitive ops (embedding, attention, normalization, optimizer state) in BF16/FP32.
**First introduced (in this form):** [DeepSeek-V3 Technical Report (DeepSeek-AI, 2024)](https://arxiv.org/abs/2412.19437) (Section 3.3). Builds on prior FP8 training proposals (e.g. NVIDIA Transformer Engine, Peng et al. 2023b).

## Description

DeepSeek-V3's mixed-precision recipe is the first reported successful application of
FP8 to a frontier-scale (671B-param MoE) pre-training run. Key design choices:

- **All-E4M3** rather than the standard E4M3-forward / E5M2-backward hybrid. The
  fine-grained scaling (below) compensates for E4M3's smaller dynamic range.
- **Fine-grained quantization scaling** — activations scaled per `1×128` tile (per
  token, per 128 channels); weights scaled per `128×128` block. This is what makes
  the all-E4M3 choice viable at scale.
- **Online quantization** — scaling factors recomputed each step rather than tracked
  via historical maxima.
- **CUDA-core promotion for accumulation** — Hopper Tensor Core FP8 GEMM accumulates
  at ~14 bits internally; DeepSeek-V3 promotes partial sums to FP32 registers on
  CUDA cores every Nc=128 elements to recover precision.
- **High precision retained** for: embedding, output head, MoE gating, normalization,
  attention. AdamW first/second moments stored in BF16; master weights and gradient
  accumulators in FP32. Activations cached in FP8 for the backward pass.

The reported relative loss error vs. BF16 is consistently below 0.25%.

## Reference materials

- DeepSeek-V3 paper, Section 3.3: <https://arxiv.org/abs/2412.19437>
- NVIDIA FP8 primer: <https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/index.html>

## Used by

| Model       | Variation / details                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3 | Recipe described above. Validated on V2-Lite and V2-scale baselines for ~1T tokens before full V3 training. |

## Related techniques

- _Block-wise INT8 quantization (LLM.int8, GPTQ)_ — inference-time analogues
