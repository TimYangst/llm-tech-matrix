# Agent Swarm — Parallel-Agent Reinforcement Learning (PARL)

> 中文版：[agent-swarm.zh.md](./agent-swarm.zh.md)

**Slug:** `agent-swarm`
**Category:** alignment / RL
**One-line:** A self-directed parallel agent orchestration framework where one orchestrator model dynamically spawns frozen sub-agents and aggregates their outputs; only the orchestrator receives RL gradients (sub-agent trajectories are excluded from the loss), sidestepping credit-assignment ambiguity and training instability of end-to-end multi-agent RL.
**First introduced in:** [Kimi K2.5: Visual Agentic Intelligence (Moonshot AI, 2026)](https://arxiv.org/abs/2602.02276) §1, §4.4.2.

## Description

Most agentic LLMs execute tool calls sequentially. Even systems capable of hundreds of reasoning steps (e.g. Kimi K2-Thinking with 200–300 sequential calls) suffer linear inference-time scaling — long-horizon tasks like "build a complex project that involves massive-scale research, design, and development" become latency-bound long before they become quality-bound.

K2.5's Agent Swarm restructures this. Rather than one model executing all steps in series, the orchestrator model dynamically decomposes the task into heterogeneous sub-problems and instantiates **domain-specialised sub-agents** that execute concurrently. The training innovation is **PARL (Parallel-Agent Reinforcement Learning)**: in addition to the standard verifiable-reward RL on tool execution, the orchestrator is given interfaces for sub-agent creation and task delegation. During training, sub-agents are **frozen** and their execution trajectories are **excluded from the optimisation objective** — only the orchestrator's policy is updated.

The decoupling matters because end-to-end co-optimisation across orchestrator + sub-agents introduces two failure modes the K2.5 paper calls out: (a) *credit-assignment ambiguity* (which agent's actions caused the reward?) and (b) *training instability* (sub-agents drift mid-training, destabilising the orchestrator's gradient signal). PARL pays for these problems with sub-agent staleness, but the K2.5 paper reports it works well empirically.

Reported deltas on K2.5: BrowseComp 60.6 → 78.4 (single agent → swarm); WideSearch item-F1 72.7 → 79.0 — with up to 4.5× latency reduction over single-agent baselines. Swarm Mode benchmark settings: BrowseComp main agent max 15 steps, sub-agents max 100 steps; WideSearch both at max 100 steps. K2.6 scales this further to **300 sub-agents executing 4,000 coordinated steps** per K2.6 README §1.

## Reference materials

- Kimi K2.5: Visual Agentic Intelligence: <https://arxiv.org/abs/2602.02276>
- Kimi K2.6 README §1 (300 sub-agents / 4000 steps): <https://huggingface.co/moonshotai/Kimi-K2.6>

## Used by

| Model     | Variation / details                                                                                                                                                                                                                                                                                                                                                                                |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K2.5 | First public deployment of PARL. Trained jointly with the rest of K2.5's text-vision RL stack (token-level clip RL with MuonClip optimizer + verifiable + GRM rewards). BrowseComp 60.6 → 74.9 (with simple context management) → 78.4 (Agent Swarm); WideSearch item-F1 72.7 → 79.0; latency up to 4.5× lower than single-agent. Swarm config: main agent max 15 steps; sub-agents max 100 steps. |
| Kimi K2.6 | Same PARL framework, scaled in deployment to **300 sub-agents executing 4,000 coordinated steps** per task (README §1). BrowseComp 83.2 → 86.3 with swarm; described qualitatively for "long-horizon coding, coding-driven design, proactive autonomous execution, and swarm-based task orchestration". K2.6 paper not yet published — only the README narrative is available.                     |

## Related techniques

- [GRPO](./grpo.md) — alternative on-policy RL algorithm; K2.5's underlying RL is a token-level clip variant rather than GRPO, but both target the same family of long-horizon multi-step tool-use problems.
- [On-Policy Distillation](./on-policy-distillation.md) — DeepSeek-V4's analogous "use a frozen model to teach the trainee" pattern, but for output supervision rather than agent-orchestration RL.
