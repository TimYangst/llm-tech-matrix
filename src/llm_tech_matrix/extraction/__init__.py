"""Layer 2: schema-strict information extraction.

Reads data/sources/<model-slug>/, runs LLM-driven extraction with the no-hallucination
rule (see docs/schema.md), writes one validated JSON to data/extracted/<model-slug>.json.

Prompt templates and the merging step that reconciles fields across multiple sources
live here. Implementation pending — see .claude/skills/extract-model for the
human-in-the-loop version.
"""
