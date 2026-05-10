# Hybrid Thinking（chat-template 驱动的思考模式融合）

> English: [hybrid-thinking.md](./hybrid-thinking.md)

**Slug:** `hybrid-thinking`
**类别：** alignment
**一句话概括：** 一种后训练食谱——把 long-CoT 推理（"thinking"）和直接回复（"non-thinking"）两种行为融合到同一组权重里，推理时用 chat-template 指令切换，而不是部署两个独立模型。
**首次提出：** [Qwen3 Technical Report (Qwen Team, 2025)](https://arxiv.org/abs/2505.09388)

## 概述

前沿模型常把能力拆成两个 checkpoint：推理调优版（long CoT，慢、贵）和指令调优版（短、快、便宜）。Hybrid Thinking 把两者合到同一个 checkpoint：

- **训练**（Qwen3 四阶段后训练的第 3 阶段，称为 *Thinking Mode Fusion*）：在推理 RL 后的 checkpoint 上继续做 SFT，混合大约 50/50 的 thinking 样本（从推理 RL 模型自身做 rejection sampling，以保质量）和 non-thinking 样本（精选的多领域指令数据）。Chat template 引入 `/think` 和 `/no_think` 指令插在 user/system 消息里，并约定 non-thinking 回复使用空的 `<think></think>` 块。

- **推理**：用户在 prompt 中插入 `/think` 或 `/no_think` 切换模式（或在 HuggingFace tokenizer 中设 `enable_thinking=False`）。多轮对话可以交错使用——模型遵从最近一次 flag。

- **Thinking budget** 自然涌现：模型一旦能舒服地处理被截断的 thinking 块的回复，你就可以在中途插入一个固定的 stop-thinking 哨兵 token 来打断思考，模型会基于已有的推理直接给出最终答案。这个能力在 Qwen3 中 *没有* 单独训练——是 Thinking Mode Fusion 的免费副产品。

这个模式与 OpenAI 的 reasoning-effort 旋钮和 Anthropic Claude 的 extended-thinking 旋钮思路相近（但不完全相同）——后者也是在单一模型上暴露一个显式推理预算。

## 参考资料

- 原始论文（Qwen3 §4.3）：<https://arxiv.org/abs/2505.09388>

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3-32B       | `/think`（默认）vs `/no_think` 指令插在 user/system 消息里；`<think>...</think>` 包住推理块。两种模式的默认采样不同（thinking：T=0.6、top-p=0.95、top-k=20；non-thinking：T=0.7、top-p=0.8、top-k=20、presence_penalty=1.5）。Thinking-budget 控制通过插入哨兵 `"Considering the limited time by the user, I have to give the solution based on the thinking directly now. </think>"`。                                                                                    |
| Qwen3-235B-A22B | 与 Qwen3-32B 同食谱（包括 Thinking Mode Fusion 在内的四阶段 pipeline 在两个旗舰间共享）。235B-A22B 同时是 Strong-to-Weak 蒸馏中两个教师之一（另一个是 32B），把 thinking + non-thinking 行为传给较小的 Qwen3 规模。                                                                                                                                                                                                                                                        |
| Qwen3.5-27B     | Chat-template 信封仍是 `<think>...</think>`，但 **`/think` / `/no_think` 软开关被移除**（README："Qwen3.5 does not officially support the soft switch of Qwen3"）。模式切换只剩 API 上的 `chat_template_kwargs={"enable_thinking": False}`（阿里云模型工作室简化为顶层 `enable_thinking` kwarg）。默认 thinking on。两种模式的采样默认值仍然不同（thinking T=1.0 / top-p=0.95；non-thinking T=0.7 / top-p=0.8）。生成融合权重的后训练 pipeline 没有像 Qwen3 那样披露细节。 |
| Qwen3.5-35B-A3B | Chat-template + API 切换与 Qwen3.5-27B 完全相同——只支持 `enable_thinking` API kwarg，不支持 `/think` 软开关。两种模式的采样默认值相同。MoE 骨干不影响运行时模式机制。                                                                                                                                                                                                                                                                                                      |
| Qwen3.6-27B     | 与 Qwen3.5 一致的 `enable_thinking` API 切换；软开关仍被记为 "not officially supported"（template 里仍有 5 处 `/think`——软 token 的行为没明确）。**新增第三个正交 kwarg `preserve_thinking`**（默认 False）：为 True 时模型在历史轮次的 `<think>...</think>` 块上保留并条件化，而不仅是最近一次 user 消息。厂商论点是这能改善多轮 agent 决策一致性、减少重复推导以节省 token、并提升 KV-cache 利用率。能力是"额外训练"而来，但食谱（继续 SFT？RL？数据规模？）没披露。     |
| Qwen3.6-35B-A3B | API kwarg 与 Qwen3.6-27B 相同：`enable_thinking` + `preserve_thinking`（无软开关）。Qwen3.6-35B-A3B chat template 引用 `preserve_thinking` 2 次，仍引用 `/think` 5 次。多轮 `<think>` 保留规则（滑动窗口？全历史？打 tag？）template 和 README 都没说明。                                                                                                                                                                                                                  |

## 相关技术

- [GRPO](./grpo.md) — 在融合之前构建思考能力的 Reasoning RL 阶段
