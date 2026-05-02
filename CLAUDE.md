# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository is at **inception**. Only `uv init` scaffolding (`main.py`, `pyproject.toml`, `.python-version`) and `README.md` exist — no implementation yet. The README is a design document, not a description of existing code. When building features, treat README as spec and verify it still reflects current intent before relying on it.

## Project intent (from README.md)

Build a structured, updatable knowledge base that tracks and decomposes the technical stacks of mainstream AI models (text, multimodal, diffusion) for both **horizontal comparison** (cross-vendor differences) and **vertical analysis** (lifecycle of a single technique, e.g. optimizer evolution Adam → Muon).

Milestones:
- **M1 (current focus)**: text + multimodal LLMs — Qwen, Llama, DeepSeek, GLM, GPT-4, Kimi, MiniMax. Open-weight models analyzed deeply via HuggingFace `config.json` + tech reports; closed models inferred from public signals.
- **M2 (future)**: diffusion / image / video — Stable Diffusion, Flux, Sora, Veo, etc.

## Core data schema (the contract for extraction)

All extraction output must conform to this schema. When adding extraction logic or prompts, keep these field groups intact — downstream synthesis depends on uniform structure across models:

1. **Model metadata** — release date + family, open-source status (Open Weights / Open Source / Closed), total params + active params.
2. **Architecture** — backbone (layers, hidden dim, context window); attention variant (MHA/GQA/MLA, RoPE details); FFN/MoE (expert count, active experts, routing algo, shared experts); base components (activation, normalization, embedding); infra hooks (SP/EP-friendly design).
3. **Training & optimization** — optimizer + LR schedule; data (total tokens, code/math/text mix); alignment (SFT, RLHF/PPO/DPO/GRPO, RLAIF); advanced (self-distillation, FP8/BF16 mixed precision).
4. **Multimodal specifics** (multimodal models only) — vision/audio encoder; fusion mechanism (MLP projection, cross-attention; native vs concatenated).

When information is missing, mark `[Unknown/Not Disclosed]` — **never hallucinate**. The extraction prompt frames the AI as a "Senior AI Researcher" and this no-hallucination rule is load-bearing for the project's value.

## Intended pipeline architecture

Three layers — keep them decoupled when implementing:

1. **Data sourcing** — pull HuggingFace `config.json`; ingest ArXiv papers / official tech blog URLs.
2. **Information extraction** — LLM-driven, schema-strict extraction from long-form text into structured JSON.
3. **Synthesis & analytics** — merge JSON into a database/charts; generate trend reports (e.g. "Adam → Muon evolution").

## Tooling

- **Package manager**: `uv` (project was created with `uv init`; `.venv/` is committed-adjacent and `pyproject.toml` is the source of truth).
- **Python**: 3.13 (pinned via `.python-version` and `requires-python` in `pyproject.toml`).
- **Common commands**:
  - `uv run main.py` — run entry point
  - `uv add <pkg>` — add a dependency (edits `pyproject.toml` + lockfile)
  - `uv sync` — install/refresh the venv from lockfile

There are no tests, lint config, or build pipeline yet — add them as the project grows rather than assuming they exist.
