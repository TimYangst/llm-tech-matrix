# 大模型技术演进与架构解析矩阵

> English version: [README.md](./README.md)

一个结构化、可持续更新的知识库，系统性追踪和拆解主流 AI 模型的技术栈——既支持**横向对比**（各家方案差异），也支持**纵向分析**（单一技术的生命周期与演进趋势）。

## 当前状态

**M1 进行中。** 已抽取 21 个模型，覆盖 4 家厂商（DeepSeek、Qwen、Kimi、智谱），全部通过 schema v7 校验。最新记录：Qwen3.8-Flash-Next（Qwen4 架构预览，也是本仓库第一个有技术报告支撑的 Qwen 记录）、Qwen3.8-2.4T-A95B（首个开放权重的 Qwen-Max 级模型）、Qwen3.8-27B。综合分析层尚未开始 —— 要等 M1 的抽取门槛达成后再动工。

当前重点：**M1——文本与多模态大模型。** 战略路线图见 [`docs/roadmap.md`](./docs/roadmap.md)，每个模型的具体状态见 [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)。

## 文档导航

| 你想了解                                   | 请看                                           |
| ------------------------------------------ | ---------------------------------------------- |
| 项目为什么存在                             | [`docs/vision.md`](./docs/vision.md)           |
| 抽取的字段到底是什么                       | [`docs/schema.md`](./docs/schema.md)           |
| 数据获取 → 信息抽取 → 综合分析的流程       | [`docs/pipeline.md`](./docs/pipeline.md)       |
| 命名、文件布局、Schema 版本管理规则        | [`docs/conventions.md`](./docs/conventions.md) |
| 战略路线图（里程碑、范围）                 | [`docs/roadmap.md`](./docs/roadmap.md)         |
| 每个模型的进度（待抽取 / 已抽取 / 已审阅） | [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)       |

## 目录结构

```
docs/                  权威参考文档（愿景、Schema、流水线、约定、路线图）
  glossary/            分技术的中英双语小词条，每条带"使用此技术的模型"表
src/llm_tech_matrix/   Python 包
  schema.py            Pydantic 模型 —— docs/schema.md 的可执行版本
  sourcing/            第一层 —— 拉取 HF config、论文、博客；manifest + sha256
  extraction/          第二层 —— render.py（JSON → 双语 Markdown）。抽取本身由
                       .claude/skills/extract-model skill 驱动，不是代码逻辑。
  synthesis/           第三层 —— 空包，尚未开始（见 docs/roadmap.md）
scripts/               validate_extractions.py（CI 的 schema 闸门）+ schema 迁移脚本
data/
  sources/<model>/     manifest.json（提交进 git）+ 缓存的原始文件（gitignore）
  extracted/<model>.json  通过 Schema 校验的抽取产物（提交进 git）
  extracted/<model>.md    渲染出的英文摘要（提交进 git，由 .json 生成）
  extracted/<model>.zh.md 渲染出的中文摘要（提交进 git，由 .json 生成）
  reports/             生成的综合分析报告 —— 尚未创建
tasks/
  ROADMAP.md           各模型状态总表 + Current focus
  models/<model>.md    每个模型的笔记、数据源、未决问题
.claude/skills/        Claude Code skills（extract-model、draft-pr）
```

目前还没有测试套件 —— CI 跑的 schema 闸门是 `scripts/validate_extractions.py`。

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

## 开发环境

clone 后一次性执行：

```bash
uv sync                       # 安装依赖（runtime + dev）
uv run pre-commit install     # 激活 git hook
```

完整开发指南（代码风格、lint/format 命令、CI、AI 代码评审、PR 规范）见
[`docs/development.md`](./docs/development.md)。

## 添加一个新模型抽取

1. 在 [`tasks/ROADMAP.md`](./tasks/ROADMAP.md) 中添加条目，状态为 `backlog`，并创建
   `tasks/models/<model-slug>.md` 列出候选数据源 URL。
2. 注册数据源 —— 这一步会下载文件、记录 sha256 并写入 manifest：
   `uv run python -m llm_tech_matrix.sourcing add <slug> --name config --kind hf_config --url ... --filename config.json`
   （若有 PDF 资产，再跑 `python -m llm_tech_matrix.sourcing.pdf_to_text <slug>`）。
3. 运行 `extract-model` skill（或参照 [`docs/schema.md`](./docs/schema.md) 手动抽取），
   产出 `data/extracted/<model-slug>.json`。
4. 用 `src/llm_tech_matrix/schema.py` 校验 —— 这也是 CI 强制执行的闸门。
5. 渲染需要提交的双语摘要：`uv run python -m llm_tech_matrix.extraction.render <slug>`。
   **不要手改**生成的 `.md` / `.zh.md`，要改就改 JSON 或改渲染器。
6. 给相关的 [`docs/glossary/`](./docs/glossary/) 词条补"使用此技术的模型"行（`.md` 和
   `.zh.md` 都要改），并把路线图状态更新为 `extracted`。

完整流程见 [`.claude/skills/extract-model/SKILL.md`](./.claude/skills/extract-model/SKILL.md)。

## 铁律

当源材料中没有某个字段的信息时，该字段的值必须是字符串 `"[Unknown/Not Disclosed]"`。**严禁幻觉。** 项目一半的价值在于数据可信。完整规则及闭源模型推断字段（`inferred_fields`）机制见 [`docs/schema.md`](./docs/schema.md#cardinal-rule-no-hallucination)。
