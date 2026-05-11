# Agent Swarm — 并行智能体强化学习（PARL）

> English: [agent-swarm.md](./agent-swarm.md)

**Slug:** `agent-swarm`
**类别：** alignment / RL
**一句话概括：** 一个自指挥的并行智能体编排框架——一个 orchestrator 模型动态生成"冻结的"子智能体并聚合它们的输出；只有 orchestrator 接受 RL 梯度（子智能体轨迹被排除在损失之外），从而绕开端到端多智能体 RL 的归因模糊和训练不稳定问题。
**首次提出：** [Kimi K2.5: Visual Agentic Intelligence (Moonshot AI, 2026)](https://arxiv.org/abs/2602.02276) §1、§4.4.2。

## 概述

大多数智能体型 LLM 是串行执行工具调用的。即便是能跑数百步推理的系统（如 Kimi K2-Thinking 的 200–300 步连续工具调用），推理时间也随步数线性增长——"做一个涉及大规模研究、设计、开发的复杂项目"这种长时序任务，往往在质量瓶颈出现之前就先撞上延迟瓶颈。

K2.5 的 Agent Swarm 重组了这一执行模式：不再让一个模型串行跑所有步骤，orchestrator 模型动态地把任务分解成异构子问题，并实例化一组**领域专长的子智能体**并行执行。训练上的创新是 **PARL（Parallel-Agent Reinforcement Learning）**：在标准的"工具执行可验证奖励"RL 之上，给 orchestrator 提供"创建子智能体 + 委派任务"的接口。训练时子智能体被**冻结**，它们的执行轨迹**不进入优化目标**——只有 orchestrator 的策略被更新。

这种解耦很重要，因为 orchestrator + 子智能体的端到端协同优化会引入 K2.5 论文点名的两个失败模式：（a）*归因模糊*——奖励是哪个 agent 的行为带来的？（b）*训练不稳定*——子智能体在训练中漂移会拖垮 orchestrator 的梯度信号。PARL 用"子智能体陈旧化"换掉了这两个问题，K2.5 论文报告其经验上工作良好。

K2.5 上的报告增量：BrowseComp 60.6 → 78.4（单 agent → swarm）；WideSearch item-F1 72.7 → 79.0——延迟相比单 agent 基线最高降低 4.5×。Swarm Mode benchmark 配置：BrowseComp 主 agent 最多 15 步，子 agent 最多 100 步；WideSearch 都是最多 100 步。K2.6 在部署时进一步把规模扩到 **300 个子智能体协同执行 4,000 步**（K2.6 README §1）。

## 参考资料

- Kimi K2.5: Visual Agentic Intelligence：<https://arxiv.org/abs/2602.02276>
- Kimi K2.6 README §1（300 子智能体 / 4000 步）：<https://huggingface.co/moonshotai/Kimi-K2.6>

## 使用此技术的模型

| 模型      | 变体 / 细节                                                                                                                                                                                                                                                                                                    |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K2.5 | PARL 的首次公开部署。与 K2.5 文本-视觉联合 RL（MuonClip 优化器 + 可验证奖励 + GRM 奖励的 token-level clip RL）一起训练。BrowseComp 60.6 → 74.9（简单上下文管理）→ 78.4（Agent Swarm）；WideSearch item-F1 72.7 → 79.0；延迟相比单 agent 最高降低 4.5×。Swarm 配置：主 agent 最多 15 步，子 agent 最多 100 步。 |
| Kimi K2.6 | 沿用同一 PARL 框架，部署规模扩到**300 个子智能体协同执行 4,000 步**（README §1）。BrowseComp 83.2 → 86.3（with swarm）。"长时序编码、编码驱动设计、主动式自主执行、基于群体的任务编排"——只有 README 叙述，K2.6 论文尚未发表。                                                                                  |

## 相关技术

- [GRPO](./grpo.zh.md) — 另一种 on-policy RL 算法；K2.5 底层 RL 是一种 token-level clip 变体而非 GRPO，但都瞄准同一类长时序多步工具使用问题。
- [On-Policy Distillation](./on-policy-distillation.zh.md) — DeepSeek-V4 的类比"用冻结模型教学员"模式，但作用对象是输出监督，而不是智能体编排 RL。
