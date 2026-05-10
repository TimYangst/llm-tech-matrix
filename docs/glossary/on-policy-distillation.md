# On-Policy Distillation (OPD)

> 中文版：[on-policy-distillation.zh.md](./on-policy-distillation.zh.md)

**Slug:** `on-policy-distillation`
**Category:** alignment
**One-line:** Trains a single unified student model to minimize the reverse KL between its own next-token distribution and an ensemble of expert teacher models, evaluated on trajectories the student samples itself ("on-policy"); used to consolidate per-domain specialists into one model after specialist training.
**First introduced in:** [Gu et al., 2024 — On-Policy Distillation of Language Models](https://arxiv.org/abs/2306.13649); refined / scaled in [Lu and Lab, 2025](https://arxiv.org/abs/2502.04428) and DeepSeek-V4 paper Section 5.1.2.

## Description

Standard knowledge distillation (Hinton et al., 2015) has the student match teacher logits on a fixed dataset. **On-policy distillation** instead samples the training trajectories from the *student* itself and then asks the student to match the teachers on those trajectories. This keeps the distillation signal aligned with what the student actually generates at inference time, avoiding the off-policy drift that hurts vanilla distillation when the student's distribution diverges from the data distribution.

The objective for `N` expert teachers `{π_E_1, ..., π_E_N}`:

`L_OPD(θ) = Σ_i w_i · D_KL( π_θ ∥ π_E_i )`

where `π_θ` is the student, `w_i` is the per-teacher weight, and the reverse-KL is computed on student-sampled trajectories. Reverse KL (vs forward KL) penalizes the student putting mass where teachers have low probability — encouraging the student to focus on regions teachers actually agree with.

DeepSeek-V4 uses OPD as the **final post-training step** to consolidate `>10` per-domain specialists (math, code, agent, instruction-following, ...) into one unified model — replacing the mixed-RL stage that V3.2 used at this point in the pipeline. The student samples trajectories; for each trajectory, the relevant domain teachers' reverse-KL loss is computed and aggregated. Knowledge from physically distinct expert weights is consolidated into a single parameter space via logits-level alignment, sidestepping the performance degradation of weight-merging or mixed-RL strategies.

V4 prefers **full-vocabulary logit distillation** over the variance-prone token-level KL estimate common in earlier work — it's more expensive but yields more stable gradients. To make it feasible at scale: (1) teacher weights live in centralized distributed storage with on-demand ZeRO-like sharding; (2) only last-layer hidden states are cached during the teacher forward, with logits reconstructed on the fly through the prediction head; (3) training samples are dispatched in teacher-index order so at most one teacher head sits in device memory per mini-batch; (4) the KL kernel is a custom TileLang implementation.

## Reference materials

- Gu et al., 2024 (origin): <https://arxiv.org/abs/2306.13649>
- Lu and Lab, 2025 (scaling refinements): <https://arxiv.org/abs/2502.04428>
- DeepSeek-V4 Technical Report Section 5.1.2 + 5.2.2 (Efficient Teacher Scheduling).

## Used by

| Model             | Variation / details                                                                                                                                                                                                                                                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro   | Multi-teacher OPD with >10 domain specialists (math, code, agent, instruction-following, ...). Full-vocabulary logit distillation (not token-level). Centralized ZeRO-sharded teacher storage; last-layer-hidden-state caching with on-the-fly logit reconstruction; teacher-index-ordered sample dispatch. Replaces the mixed-RL stage used in DeepSeek-V3.2. |
| DeepSeek-V4-Flash | Identical OPD recipe to V4-Pro (same family pipeline). Smaller per-teacher and student parameter budgets but the same engineering — student is V4-Flash; teachers are >10 V4-Flash specialists.                                                                                                                                                                |

## Related techniques

- [GRPO](./grpo.md) — used in the per-domain specialist training stage immediately before OPD; OPD then collapses the specialists into one model.
