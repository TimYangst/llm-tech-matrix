# Extraction Schema

This schema is the **contract** between the extraction layer and the synthesis layer. Every extracted model must conform — downstream comparison and trend analysis assume identical field structure across models.

The executable version lives in `src/llm_oss_summary/schema.py` (Pydantic). This document is the human-readable spec; if the two diverge, **the Pydantic version wins** and this doc must be updated.

## Cardinal rule: no hallucination

When information is not present in the source material, the field value is the literal string `"[Unknown/Not Disclosed]"`. **Do not guess, do not infer "reasonable defaults", do not fill from training-data prior knowledge.** Inferred-but-public values (e.g. closed-model architecture from leaks) go in a `notes` field with a citation, never in the primary field.

This rule is load-bearing. Half the project's value is being able to trust the data.

## Field groups

### 1. Model metadata

| Field | Type | Notes |
|---|---|---|
| `name` | string | Canonical name, e.g. `"DeepSeek-V3"`, `"Llama-3.1-70B"` |
| `family` | string | Family name, e.g. `"DeepSeek"`, `"Llama"` |
| `release_date` | string (`YYYY-MM`) | Public release/announcement date |
| `openness` | enum | `"open_source"` / `"open_weights"` / `"closed"` |
| `params_total` | string | e.g. `"671B"`, `"70B"` — keep human-readable units |
| `params_active` | string | For MoE; equals total for dense models |
| `sources` | list of URLs | Where this extraction was sourced from (paper, HF, blog) |

### 2. Architecture

**Backbone**

- `layers` — int
- `hidden_dim` — int
- `context_window` — int (max sequence length supported)

**Attention**

- `variant` — enum: `"MHA"` / `"GQA"` / `"MLA"` / `"sliding_window"` / other
- `num_heads` — int
- `num_kv_heads` — int (= num_heads for MHA, < for GQA)
- `head_dim` — int
- `rope` — object: `{ "type": "standard" | "yarn" | "ntk" | "none", "base": int, "scaling": object | null }`

**FFN / MoE**

- `ffn_type` — enum: `"dense"` / `"moe"`
- `intermediate_size` — int (dense FFN width, or per-expert width for MoE)
- If MoE:
  - `num_experts` — int
  - `num_active_experts` — int (top-k)
  - `routing` — string describing the routing algorithm (e.g. `"auxiliary-loss-free load balancing (DeepSeek-V3)"`)
  - `shared_experts` — int (count of always-on experts)

**Base components**

- `activation` — e.g. `"SwiGLU"`, `"GeLU"`
- `normalization` — e.g. `"RMSNorm"`, `"LayerNorm"`
- `embedding_notes` — string (tied embeddings? special tokenizer? etc.)

**Infra hooks**

- `parallelism_notes` — string describing any architectural hooks for sequence parallelism, expert parallelism, pipeline parallelism (e.g. DeepSeek-V3's DualPipe, MLA's KV compression for SP)

### 3. Training & optimization

- `optimizer` — e.g. `"AdamW"`, `"Muon"`
- `lr_schedule` — e.g. `"cosine with 2000 warmup steps, peak 3e-4"`
- `data_total_tokens` — string, e.g. `"15T"`, `"14.8T"`
- `data_mix` — object, e.g. `{ "code": "17%", "math": "10%", "text": "73%" }` — only fill what's disclosed
- `alignment` — object:
  - `sft` — string description
  - `rl_method` — enum or string: `"PPO"` / `"DPO"` / `"GRPO"` / `"RLHF"` / etc.
  - `rlaif` — bool
- `advanced` — object:
  - `self_distillation` — bool + notes
  - `mixed_precision` — e.g. `"FP8 + BF16"`, `"BF16"`

### 4. Multimodal specifics (multimodal models only)

- `vision_encoder` — e.g. `"ViT-L/14 (CLIP-init)"`, or `"[Unknown/Not Disclosed]"`
- `audio_encoder` — same shape
- `fusion` — enum: `"native"` (single transformer over interleaved tokens) / `"projected"` (encoder → MLP → LLM) / `"cross_attention"` / other
- `fusion_notes` — string with details

### 5. Notes (optional but encouraged)

- `inferred_fields` — list of `{field: "...", basis: "...", confidence: "low" | "medium" | "high"}` for closed-model inferences
- `open_questions` — list of strings — things the extractor flagged as unclear or contested

## Versioning

This schema will evolve. When breaking changes happen:

1. Bump `schema_version` (top-level field, integer) in `src/llm_oss_summary/schema.py`.
2. Document the change in `docs/conventions.md` under "Schema changelog".
3. Old extractions are not auto-migrated; they remain valid against their declared `schema_version`.
