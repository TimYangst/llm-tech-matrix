# Native INT4 Quantization-Aware Training

> 中文版：[int4-qat.zh.md](./int4-qat.zh.md)

**Slug:** `int4-qat`
**Category:** quantization
**One-line:** Post-training Quantization-Aware Training that targets only routed-MoE-expert weights at INT4 (group-wise, group_size=32, symmetric), leaving attention, shared experts, dense FFNs, lm_head, and the vision tower at high precision — yields ~2× generation speedup at ostensibly lossless quality on long-decoding "thinking" workloads.
**First introduced in:** Adopted as a deployment recipe in [Kimi K2-Thinking (Moonshot AI, 2025)](https://moonshotai.github.io/Kimi-K2/thinking.html); ported unchanged into [Kimi K2.5](https://arxiv.org/abs/2602.02276) and Kimi K2.6.

## Description

Naive post-hoc INT4 weight quantization at trillion-parameter scale tends to hurt quality, and the hit is amplified for "thinking" models that decode tens of thousands of tokens per query (errors accumulate down the chain of thought). Kimi's recipe sidesteps this in two ways:

1. **QAT during the post-training stage**, not pre-training: the model trains aware of the eventual INT4 representation so the optimiser absorbs the quantization error into the weights rather than letting it surface at inference. K2-Thinking README §4: "We adopt Quantization-Aware Training (QAT) during the post-training phase, applying INT4 weight-only quantization to the MoE components."
2. **Routed-MoE-expert weights only**. The HF `config.quantization_config.ignore` patterns explicitly exclude `re:.*self_attn.*`, `re:.*shared_experts.*`, `re:.*mlp\\.(gate|up|gate_up|down)_proj.*`, `lm_head`, and (on K2.5/K2.6) `re:vision_tower.*` and `re:mm_projector.*`. So attention paths, shared experts, dense-FFN gate/up/down projections, the LM head, and the entire vision pipeline run at high precision (BF16); only the routed-expert linear layers — by far the dominant parameter count in a 1T MoE with 384 experts — are INT4.

The compressed format is `compressed-tensors` `pack-quantized` with `group_size=32`, `num_bits=4`, `type=int`, `symmetric=true`, `strategy=group`, `observer=minmax`. INT4 weights can be unpacked to FP8/BF16 via the official `compressed-tensors` repo if higher-precision deployment is required. K2-Thinking's README claims all reported benchmark scores are produced under INT4 precision.

This contrasts with DeepSeek-V4's [FP4 QAT (MXFP4)](./fp4-qat.md): same idea (post-training QAT, MoE expert weights only) but FP4 with E2M1 + per-32-element micro-block scaling rather than INT4 with per-32-element symmetric integer scaling.

## Reference materials

- Kimi K2-Thinking blog (canonical recipe description): <https://moonshotai.github.io/Kimi-K2/thinking.html>
- Kimi K2-Thinking README §4 "Native INT4 Quantization": <https://huggingface.co/moonshotai/Kimi-K2-Thinking>
- compressed-tensors repository: <https://github.com/vllm-project/compressed-tensors>

## Used by

| Model            | Variation / details                                                                                                                                                                                                                                                                                                                                                           |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K2-Thinking | The original recipe. `config.quantization_config`: `format='pack-quantized'`, `group_size=32`, `num_bits=4`, `type=int`, `symmetric=true`, `strategy=group`, `observer='minmax'`. Ignore: `lm_head`, `re:.*self_attn.*`, `re:.*shared_experts.*`, `re:.*mlp\\.(gate\|up\|gate_up\|down)_proj.*`. Roughly 2× generation-speed improvement; all reported benchmarks under INT4. |
| Kimi K2.5        | Inherits the K2-Thinking recipe verbatim (README §4: "Kimi-K2.5 adopts the same native int4 quantization method as Kimi-K2-Thinking"). Adds two additional `ignore` patterns to spare the vision pipeline: `re:vision_tower.*` and `re:mm_projector.*`.                                                                                                                       |
| Kimi K2.6        | Identical to K2.5 (README §4: "Kimi-K2.6 adopts the same native int4 quantization method as Kimi-K2-Thinking"). config.quantization_config matches K2.5 byte-for-byte except for the unrelated eos_token_id field.                                                                                                                                                            |

## Related techniques

- [FP4 QAT (MXFP4)](./fp4-qat.md) — DeepSeek-V4's analogous post-training-stage MoE-expert-weight QAT, but at FP4 with micro-block scaling rather than INT4 with group-wise symmetric integer scaling.
- [DeepSeekMoE](./deepseekmoe.md) — the MoE topology onto which INT4 QAT applies (only routed-expert linears are quantised; shared-expert is excluded).
