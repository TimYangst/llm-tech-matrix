# 推理强度控制（Reasoning-effort control）

> English: [reasoning-effort.md](./reasoning-effort.md)

**Slug:** `reasoning-effort`
**类别：** alignment
**一句话概括：** 一个 per-request 的旋钮，在同一个会思考的 checkpoint 上用推理深度换延迟和 token 成本，既不切换权重、也不彻底关掉思考。

**首次提出：** 没有正式论文。API 层的这个名字来自 OpenAI o 系列的 `reasoning_effort` 请求参数；开源厂商各自独立收敛到了同一套接口，但底下的实现互不相同。

## 概述

[混合思考](./hybrid-thinking.zh.md) 给模型的是一个二元轴——思考或不思考。推理强度控制在其之上再加一个「准连续」轴：既然要思考，那该思考多深？动机是经济性。在 agent 循环里，长思维链主导了成本和延迟，而长程任务的大多数步骤并不需要模型最深的推理。

这件事值得跨厂商追踪的原因是：**API 接口收敛了，机制却没有**。本仓库里的每个实现暴露的都是几乎相同的三到四档枚举，但底下：

- **DeepSeek-V4** 前置一段 *prompt 前缀*——一块放在 system message 之前的指令文本（"Reasoning Effort: Absolute maximum with no shortcuts permitted…"）。
- **Kimi K3** 把档位渲染成 XTML chat template 里的*带类型的 option message*（`thinking-effort`），插在工具声明之后、对话之前。
- **Qwen3.8** 把一段*自然语言指令注入 system message*——而且值得注意的是，它的中间档 `medium` 什么都不注入，就是裸 prompt。

三者都不是控制 token、不是路由决策、也不是另一套权重。所有情况下档位都只是模型读到的文本，这就给三家提出了同一个开放问题：策略到底有没有针对这些字符串做过 RL 训练，还是说这个枚举只是厂商钦定措辞的 prompt engineering？没有任何一家给出答案。

第二个跨厂商观察：随着强度档位的到来，*non-thinking* 模式反而在消失。Qwen3.8-2.4T-A95B 的开源权重直接拒绝 `enable_thinking=false`，而 DeepSeek-V4 的 non-think 模式是靠*没有*强度前缀来选中的，并不是一个平级模式。强度档位看起来是思考开关的后继接口，而不是它的搭档。

## 参考资料

- 原始论文：—（没有正式发表）
- 参考实现：各模型仓库的 chat template——Qwen3.8 / Kimi K3 看 `tokenizer_config.json`；DeepSeek-V4-Flash-0731 看 `encoding/README.md`。
- 相关博客 / 文章：—

## 使用此技术的模型

| 模型 | 变体 / 细节 |
| ---- | ----------- |
| DeepSeek-V4-Pro | 三档：`non-think` / `think-high` / `think-max`。`think-max` 通过在 system prompt 前置一段特殊指令实现（"Reasoning Effort: Absolute maximum with no shortcuts permitted…"）；`non-think` 则是靠*没有*这个前缀来选中，所以强度前缀是唯一载体。 |
| DeepSeek-V4-Flash | 与 V4-Pro 相同的三档结构、相同的 prompt 前缀机制。 |
| DeepSeek-V4-Flash-0731 | 正式版**重命名了档位**：预览版的最高档 "Think Max" 前缀现在叫 `high`，而 `max` 是新增的、更强的一档。`encoding/README.md` 把每一档的前缀原文都钉死了——本仓库里文档最精确的实现。 |
| Kimi K3 | 顶层 `reasoning_effort` 请求字段（默认 `max` / `high` / `low`）。chat template 把它渲染为类型为 `thinking-effort` 的全局 option message，放在工具声明之后、对话之前——是*带类型的槽位*而非自由散文。K3 根本没有思考开关，强度是唯一的深度控制。 |
| Qwen3.8-27B | `reasoning_effort` chat-template kwarg，档位 `xhigh`（默认）/ `medium` / `low`；非法值直接抛异常。实现方式是把指令注入 system message（没有 system 就合成一个，有工具就前置到 tools system 块里）。**`medium` 不注入任何文本**，所以「中间档」其实是无指令的基线，只有两个极端被引导。`enable_thinking=false` 时整段逻辑被跳过。 |
| Qwen3.8-2.4T-A95B | 与 27B 相同的三档和相同的注入机制，但档位解析是*无条件*的——因为模板拒绝 `enable_thinking=false`，没有 non-thinking 分支可跳过。 |

## 相关技术

- [混合思考](./hybrid-thinking.zh.md) —— 本技术所依附的「思考 / 不思考」二元轴，也是相关的 `preserve_thinking` / 交错思考行为的所在条目。
