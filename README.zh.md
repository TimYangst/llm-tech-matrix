# 大模型技术演进与架构解析矩阵

> English version: [README.md](./README.md)

一个结构化、可持续更新的知识库，系统性追踪和拆解主流 AI 模型的技术栈——既支持**横向对比**（各家方案差异），也支持**纵向分析**（单一技术的生命周期与演进趋势）。

## 当前状态

**M1 进行中，媒体生成分支已启动。** 已有 **35 个 LLM/VL 记录，覆盖 5 家厂商**（DeepSeek、Qwen、Kimi、智谱、MiniMax），使用 LLM schema v8；另有 **3 个媒体生成记录**（H3、Music3、Speech 2.8），使用独立 media schema v1。6 个引擎快照保持独立。技术索引、覆盖报告和引擎支持矩阵已生成；解释性的趋势报告仍待完成。

最新补录 DeepSeek-V4.1-Flash-1017、V4-Pro-0813、Flash-Vision-Exp，以及 MiniMax 从 Text-01/VL-01、M1 到 M3 的主线。音视频记录明确区分开放权重和托管服务；M3.1 Flash 尚未发布权重，不计入已抽取记录。

浏览 [LLM 模型索引](data/extracted/README.md)、[媒体生成索引](data/extracted/media/README.zh.md)与[媒体 schema](docs/media/schema.md)。本轮任务、review 和交接见[协调状态](tasks/deepseek-minimax-refresh.md)；完整排期见 [tasks/ROADMAP.md](tasks/ROADMAP.md)。

## 文档导航

| 你想了解                                   | 请看                                                                   |
| ------------------------------------------ | ---------------------------------------------------------------------- |
| 项目为什么存在                             | [`docs/vision.md`](./docs/vision.md)                                   |
| LLM/VL 抽取的字段是什么                    | [`docs/schema.md`](./docs/schema.md)                                   |
| 数据获取 → 信息抽取 → 综合分析的流程       | [`docs/pipeline.md`](./docs/pipeline.md)                               |
| 命名、文件布局、Schema 版本管理规则        | [`docs/conventions.md`](./docs/conventions.md)                         |
| 战略路线图（里程碑、范围）                 | [`docs/roadmap.md`](./docs/roadmap.md)                                 |
| 每个模型的进度（待抽取 / 已抽取 / 已审阅） | [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)                               |
| 浏览 LLM/VL 记录                           | [`data/extracted/README.md`](./data/extracted/README.md)               |
| 查看哪些模型用了哪项技术                   | [`data/reports/technique-index.md`](./data/reports/technique-index.md) |

媒体生成字段和流程见 [media schema](docs/media/schema.md) 与[媒体索引](data/extracted/media/README.zh.md)；引擎字段和快照见[引擎 schema](docs/engines/schema.md)、[排期](tasks/ENGINES.md)及[支持矩阵](data/reports/engine-support-matrix.md)。

## 目录结构

```
docs/                  权威参考文档（愿景、Schema、流水线、约定、路线图）
  glossary/            分技术的中英双语小词条，每条带"使用此技术的模型"表
src/llm_tech_matrix/   Python 包
  engine_schema.py     引擎快照（schema v3）
  media_schema.py      媒体生成（schema v1）
  schema.py            Pydantic 模型 —— docs/schema.md 的可执行版本
  sourcing/            第一层 —— 拉取 HF config、论文、博客；manifest + sha256
  extraction/          第二层 —— Agent 按各类合同抽取；render*.py 生成双语视图。
  synthesis/           第三层 —— registry.py + index.py，生成各类浏览入口
scripts/               validate_extractions.py + validate_registry.py（CI 闸门）+ 迁移脚本
data/
  sources/<model>/     manifest.json（提交进 git）+ 缓存的原始文件（gitignore）
  extracted/<model>.json  通过 Schema 校验的抽取产物（提交进 git）
  extracted/<model>.md    渲染出的英文摘要（提交进 git，由 .json 生成）
  extracted/<model>.zh.md 渲染出的中文摘要（提交进 git，由 .json 生成）
  extracted/engines/     引擎 JSON + 双语摘要（schema v3）
  extracted/media/       媒体 JSON + 双语摘要/索引（schema v1）
  extracted/README.md     生成的模型索引（勿手改）
  reports/             生成物：technique-index.md（技术↔模型矩阵）、coverage.md
tasks/
  ENGINES.md           引擎快照状态和排期
  ROADMAP.md           各模型状态总表 + Current focus
  models/<model>.md    每个模型的笔记、数据源、未决问题
.claude/skills/        抽取 LLM/引擎与 PR 草稿的工作流说明
```

媒体回归检查：`uv run python -m unittest discover -s tests -v`。CI 同时通过 `scripts/validate_extractions.py` 检查 schema、媒体来源证据和生成视图。

## 快速开始

本项目使用 [`uv`](https://docs.astral.sh/uv/) + Python 3.13。

```bash
# 安装锁定的依赖
uv sync --locked

# 校验仓库已有的三类记录和生成索引
uv run python scripts/validate_extractions.py
uv run python scripts/validate_registry.py
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

验证已提交记录不需要 HF_TOKEN。抓取来源前可参考 `.env.example`；模型权重下载和推理不属于此流程。

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

7. 更新受控词汇后，运行 `uv run python -m llm_tech_matrix.synthesis.index`，再运行上面的两个校验命令，避免模型索引或技术矩阵过期。

以上步骤适用于 LLM/VL。音视频生成按[媒体流程](docs/media/overview.md)生成 `data/extracted/media/` 记录；引擎快照按[引擎流程](docs/engines/overview.md)执行。

完整 LLM/VL 流程见 [`.claude/skills/extract-model/SKILL.md`](./.claude/skills/extract-model/SKILL.md)。

## 铁律

当源材料中没有某个字段的信息时，该字段的值必须是字符串 `"[Unknown/Not Disclosed]"`。**严禁幻觉。** 项目一半的价值在于数据可信。完整规则及闭源模型推断字段（`inferred_fields`）机制见 [`docs/schema.md`](./docs/schema.md#cardinal-rule-no-hallucination)。
