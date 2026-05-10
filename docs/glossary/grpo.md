# Group Relative Policy Optimization (GRPO)

> 中文版：[grpo.zh.md](./grpo.zh.md)

**Slug:** `grpo`
**Category:** alignment
**One-line:** A PPO-family RL algorithm that drops the separate value/critic network and estimates the advantage baseline by sampling a group of completions per prompt and using their group-relative reward as the baseline.
**First introduced in:** [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (Shao et al., DeepSeek-AI, 2024)](https://arxiv.org/abs/2402.03300)

## Description

Standard PPO trains a critic network that's roughly the same size as the policy, and
that critic supplies a per-token value estimate from which advantages are computed.
For very large policy models, the critic doubles serving cost during RL. GRPO removes
the critic.

For each prompt, GRPO samples `G` completions from the old policy, scores them with
the reward model, and uses the group's mean reward as a baseline. The advantage for
completion `i` is `(reward_i − group_mean) / group_std` (normalized within the group).
The PPO clipped surrogate objective is then optimized as usual, with an additional KL
penalty against a reference model.

The intuition: since you sample multiple completions per prompt anyway, group-relative
reward gives you a low-variance baseline for free, and the critic was redundant.

## Reference materials

- Original paper (DeepSeekMath): <https://arxiv.org/abs/2402.03300>
- DeepSeek-V3 application: <https://arxiv.org/abs/2412.19437> (Section 5.2.2)
- DeepSeek-R1 application: <https://arxiv.org/abs/2501.12948>

## Used by

| Model           | Variation / details                                                                                                                                                                                                                                                                                                                                                              |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3     | Reward signal mixes a rule-based RM (math final-answer checks, compiler tests on code) and a model-based RM trained from V3 SFT checkpoints with chain-of-thought rewards to mitigate reward hacking.                                                                                                                                                                            |
| Qwen3-32B       | Used in the **Reasoning RL** stage on 3,995 filtered query-verifier pairs (unused-in-cold-start, learnable, challenging, sub-domain-diverse). Large batch + many rollouts + off-policy training; entropy steered to grow steadily for exploration/exploitation balance. Reported example: 235B-A22B AIME'24 70.1 → 85.1 in 170 steps with no manual hyperparameter intervention. |
| Qwen3-235B-A22B | Same Reasoning RL recipe as Qwen3-32B (the four-stage pipeline is shared across both flagships). The reported AIME'24 jump 70.1 → 85.1 over 170 RL steps is on this model.                                                                                                                                                                                                       |

## Related techniques

- _PPO, DPO_ — related-but-distinct alignment-stage algorithms (placeholders for future entries)
