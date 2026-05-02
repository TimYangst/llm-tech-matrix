# 大模型技术演进与架构解析矩阵

> English version: [README.md](./README.md)

一个结构化、可持续更新的知识库，系统性追踪和拆解主流 AI 模型的技术栈——既支持**横向对比**（各家方案差异），也支持**纵向分析**（单一技术的生命周期与演进趋势）。

## 当前状态

**项目初始化阶段。** 基础脚手架和设计文档已就位，首次抽取尚未开始。

当前重点：**M1——文本与多模态大模型。** 战略路线图见 [`docs/roadmap.md`](./docs/roadmap.md)，每个模型的具体状态见 [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)。

## 文档导航

| 你想了解 | 请看 |
|---|---|
| 项目为什么存在 | [`docs/vision.md`](./docs/vision.md) |
| 抽取的字段到底是什么 | [`docs/schema.md`](./docs/schema.md) |
| 数据获取 → 信息抽取 → 综合分析的流程 | [`docs/pipeline.md`](./docs/pipeline.md) |
| 命名、文件布局、Schema 版本管理规则 | [`docs/conventions.md`](./docs/conventions.md) |
| 战略路线图（里程碑、范围） | [`docs/roadmap.md`](./docs/roadmap.md) |
| 每个模型的进度（待抽取 / 已抽取 / 已审阅） | [`tasks/ROADMAP.md`](./tasks/ROADMAP.md) |

## 目录结构

```
docs/                  权威参考文档（愿景、Schema、流水线、约定、路线图）
src/llm_tech_matrix/   Python 包
  schema.py            Pydantic 模型 —— docs/schema.md 的可执行版本
  sourcing/            第一层 —— 拉取 HF config、论文、博客
  extraction/          第二层 —— Schema 严格的 LLM 抽取
  synthesis/           第三层 —— 跨模型对比与趋势报告
data/
  sources/<model>/     原始抓取文件（config.json、paper.pdf、manifest.json）
  extracted/<model>.json  通过 Schema 校验的抽取产物（提交进 git）
  reports/             生成的综合分析报告
tasks/
  ROADMAP.md           各模型状态总表
  models/<model>.md    每个模型的笔记、数据源、未决问题
.claude/skills/        Claude Code skills（extract-model 等）
tests/                 Schema 校验和流水线测试
```

## 快速开始

本项目使用 [`uv`](https://docs.astral.sh/uv/) + Python 3.13。

```bash
# 安装 / 同步虚拟环境
uv sync

# 配置环境变量
cp .env.example .env
# 填入 HF_TOKEN

# 运行入口
uv run python -m llm_tech_matrix
```

添加依赖：

```bash
uv add <package>
```

## 添加一个新模型抽取

1. 在 [`tasks/ROADMAP.md`](./tasks/ROADMAP.md) 中添加条目，状态为 `backlog`。
2. 创建 `tasks/models/<model-slug>.md`，列出数据源 URL。
3. 运行 `extract-model` skill（或参照 [`docs/schema.md`](./docs/schema.md) 手动抽取）。
4. 用 `src/llm_tech_matrix/schema.py` 校验输出文件 `data/extracted/<model-slug>.json`。
5. 把路线图中的状态更新为 `extracted`。

## 铁律

当源材料中没有某个字段的信息时，该字段的值必须是字符串 `"[Unknown/Not Disclosed]"`。**严禁幻觉。** 项目一半的价值在于数据可信。完整规则及闭源模型推断字段（`inferred_fields`）机制见 [`docs/schema.md`](./docs/schema.md#cardinal-rule-no-hallucination)。
