# Extraction Schema (v4)

This schema is the **contract** between the extraction layer and the synthesis layer.
Every extracted model must conform — downstream comparison and trend analysis assume
identical field structure across models.

The executable version lives in `src/llm_tech_matrix/schema.py` (Pydantic). This
document is the human-readable spec; if the two diverge, **the Pydantic version wins**
and this doc must be updated.

For the schema changelog (what changed across versions), see
[`conventions.md`](./conventions.md#schema-changelog).

## Cardinal rule: no hallucination

When information is not present in the source material, the field value is the literal
string `"[Unknown/Not Disclosed]"`. **Do not guess, do not infer "reasonable defaults",
do not fill from training-data prior knowledge.** Inferred-but-public values (e.g.
closed-model architecture from leaks) go in the top-level `inferred_fields` array
with a citation, never in the primary field.

This rule is load-bearing. Half the project's value is being able to trust the data.

## Field groups

### 1. Model metadata

| Field           | Type               | Notes                                                    |
| --------------- | ------------------ | -------------------------------------------------------- |
| `name`          | string             | Canonical name, e.g. `"DeepSeek-V3"`, `"Llama-3.1-70B"`  |
| `family`        | string             | Family name, e.g. `"DeepSeek"`, `"Llama"`                |
| `release_date`  | string (`YYYY-MM`) | Public release/announcement date                         |
| `openness`      | enum               | `"open_source"` / `"open_weights"` / `"closed"`          |
| `params_total`  | string             | e.g. `"671B"`, `"70B"` — keep human-readable units       |
| `params_active` | string             | For MoE; equals total for dense models                   |
| `sources`       | list of URLs       | Where this extraction was sourced from (paper, HF, blog) |

### 2. Architecture

#### Backbone

- `layers` — int
- `hidden_dim` — int
- `context_window` — int (canonical user-facing max, e.g. 131072 for "128K")
- `context_window_notes` — string (free-text for paper-vs-config discrepancies, extension
  method, or caveats; empty `""` if none)
- `context_extension` — object **(null when the model uses its trained length without
  scaling tricks)**:
  - `method` — string, e.g. `"yarn"`, `"yarn+dca"`, `"longrope"`, `"abf+yarn"`,
    `"sliding+global"`
  - `trained_max` — int (max sequence length seen during pre-training)
  - `extended_max` — int (productized max — equals `context_window`)
  - `factor` — float (scaling ratio)
  - `original_max` — int (YaRN-style `original_max_position_embeddings`)
  - `notes` — string (e.g. "applied at deployment via vLLM YaRN config; not in static
    config.json")

#### Attention

- `variant` — string: `"MHA"` / `"GQA"` / `"MLA"` / `"sliding_window"` / `"hybrid"` / other
- `num_heads` — int (or UNKNOWN for MLA)
- `num_kv_heads` — int (meaningful for MHA/GQA; UNKNOWN for MLA — use the `mla` subobject)
- `head_dim` — int (meaningful for MHA/GQA; for MLA the per-head dim is split across
  `mla.qk_nope_head_dim` + `mla.qk_rope_head_dim`)
- `rope` — object: `{ "type": "standard"|"yarn"|"ntk"|"mrope"|"none", "base": int, "scaling": object|null }`
- `mla` — object **(required when variant == "MLA", else null)**:
  - `kv_lora_rank` — int (KV compression dim)
  - `q_lora_rank` — int (query compression dim)
  - `qk_nope_head_dim` — int (NoPE part of QK head)
  - `qk_rope_head_dim` — int (RoPE part of QK head)
  - `v_head_dim` — int
- `variants` — list of `{name, family, num_query_heads, num_kv_heads, head_dim, rope, notes}`
  **for hybrid stacks** (Qwen3.5/3.6 interleave Gated DeltaNet + Gated Attention 3:1).
  Empty list `[]` for single-variant stacks. When non-empty, the top-level
  `num_heads`/`num_kv_heads`/`head_dim` should describe the dominant or full-attention
  variant for back-compat readers.
  - `name` — logical name, e.g. `"gated_attention"`, `"gated_deltanet"`
  - `family` — `"mha"` / `"gqa"` / `"mqa"` / `"mla"` / `"linear_attention"` / `"sliding_window"` / `"other"`
  - `num_query_heads`, `num_kv_heads`, `head_dim` — per-variant (variants of the same
    model can disagree on these)
  - `rope` — string description if RoPE handling differs per variant
  - `notes` — string for variant-specific knobs (e.g. `"v_heads=32, conv_kernel_dim=4"`)
- `layer_pattern` — string for hybrid stacks describing layer ordering, e.g.
  `"(L,L,L,F)×10 with L=gated_deltanet, F=gated_attention"`. Empty `""` for
  single-variant stacks.

The MLA field names mirror HuggingFace `config.json` keys so extractors can copy them
directly.

#### FFN

- `ffn_type` — enum: `"dense"` / `"moe"` / `"hybrid"` (hybrid = some layers dense, others MoE)
- `dense_intermediate_size` — int (required if `ffn_type` in `{"dense", "hybrid"}`, else null)
- `moe` — object **(required if `ffn_type` in `{"moe", "hybrid"}`, else null)**:
  - `num_experts` — int
  - `num_active_experts` — int (top-k)
  - `shared_experts` — int (count of always-on experts)
  - `expert_intermediate_size` — int (per-expert FFN intermediate width)
  - `routing` — string describing the routing algorithm (free text)
- `layer_partition` — string (free-text for hybrids, e.g. `"first 3 dense, remaining 58 MoE"`)

#### Base components

- `activation` — e.g. `"SwiGLU"`, `"GeLU"`
- `normalization` — e.g. `"RMSNorm"`, `"LayerNorm"`
- `embedding_notes` — string (tied embeddings? special tokenizer? etc.)

#### Parallelism / infra

- `parallelism_notes` — string describing any architectural hooks for sequence parallelism,
  expert parallelism, pipeline parallelism (e.g. DeepSeek-V3's DualPipe, MLA's KV
  compression for SP)

### 3. Training & optimization

- `optimizer` — e.g. `"AdamW"`, `"Muon"`
- `lr_schedule` — free-text e.g. `"cosine with 2000 warmup steps, peak 3e-4"`
- `data_total_tokens` — string, e.g. `"15T"`, `"14.8T"`
- `data_mix` — object, e.g. `{ "code": "17%", "math": "10%", "text": "73%" }` — only fill
  what's disclosed numerically
- `data_mix_notes` — string for qualitative descriptions (e.g. "math/code ratio enhanced
  vs. predecessor; multilingual coverage expanded; no percentages disclosed")
- `objectives` — object describing pre-training objectives **beyond** next-token prediction
  (which is implicit):
  - `multi_token_prediction` — object or null:
    - `depth` — int (D, number of additional tokens predicted)
    - `loss_weight_schedule` — string (free-text describing weight schedule)
    - `shared_modules` — string (which modules are shared with the main model)
  - `fill_in_middle` — object or null:
    - `format` — string (e.g. `"PSM (Prefix-Suffix-Middle)"`)
    - `rate` — string (e.g. `"0.1"`)
  - `other` — list of strings (free-form, for novel objectives without a slot yet)
- `alignment` — object:
  - `sft` — string description (flat summary; can stay UNKNOWN if a `stages` list is
    used instead)
  - `rl_method` — enum or string: `"PPO"` / `"DPO"` / `"GRPO"` / `"RLHF"` / etc. (flat
    summary; can stay UNKNOWN if a `stages` list is used instead)
  - `rlaif` — bool. **True only if AI generates the preference labels themselves**
    (e.g. Constitutional AI). A model-based reward model trained on human preferences
    is **RLHF, not RLAIF**.
  - `stages` — list of `{name, method, description}` for multi-stage post-training
    pipelines (e.g. Qwen3's four-stage Long-CoT Cold Start → Reasoning RL → Thinking
    Mode Fusion → General RL). Empty list `[]` for simple SFT+RL pipelines.
    - `name` — e.g. `"Long-CoT Cold Start"`, `"Reasoning RL"`
    - `method` — e.g. `"sft"`, `"rl"`, `"distillation"`, `"rejection_sampling+sft"`
    - `description` — string (data, signals, key recipe details)
  - `inference_modes` — list of `{name, trigger, description}` for runtime-switchable
    behaviors produced by post-training (e.g. Qwen3's `/think` vs `/no_think`,
    thinking-budget). Empty list `[]` for single-mode models.
    - `name` — e.g. `"thinking"`, `"non-thinking"`, `"thinking-budget"`
    - `trigger` — string describing how a user activates the mode (chat-template flag,
      system prompt, special token, etc.)
    - `description` — string
- `advanced` — object:
  - `self_distillation` — string description (or `"No"`)
  - `mixed_precision` — e.g. `"FP8 + BF16"`, `"BF16"`

### 4. Multimodal specifics (multimodal models only)

The top-level `multimodal` field is null for text-only LMs. When a model handles non-text
modalities, populate this section.

- `modalities` — list of strings, e.g. `["text", "image", "video"]`
- `fusion` — enum:
  - `"native_early"` — text and vision share the same backbone+vocab from pre-training
    (Qwen3.5/3.6); image patches map to reserved vocab IDs and flow through the LM stack.
  - `"projection_mlp"` — vision encoder + MLP projector mapping into the LM hidden_size
    (Qwen2-VL, LLaVA-style).
  - `"cross_attention"` — vision tokens attended-to via dedicated cross-attn layers
    (Flamingo).
  - `"resampler"` — Q-Former / Perceiver Resampler downsampling to a fixed query count
    (BLIP-2, MiniCPM-V).
  - `"other"` / `"[Unknown/Not Disclosed]"`
- `fusion_notes` — string with specifics (early vs late, projector shape, training-stage
  timing, etc.)
- `vision_encoder` — object or null:
  - `architecture` — e.g. `"ViT"`, `"ViT with window attention"`, `"EVA-CLIP"`
  - `depth` — int (layers in the vision encoder)
  - `hidden_size` — int (encoder hidden dim)
  - `intermediate_size` — int (encoder FFN intermediate)
  - `num_heads` — int (encoder attention heads)
  - `patch_size` — int (spatial patch size in pixels)
  - `in_channels` — int (typically 3 for RGB)
  - `output_dim` — int (projected dim feeding into the LM hidden stream; for native VL
    typically equals LM hidden_size after spatial_merge)
  - `spatial_merge_size` — int
  - `temporal_patch_size` — int (for video frames)
  - `notes` — string (window-attention layout, special block indexes, training data, etc.)
- `vision_token_anchors` — object or null: token IDs in the LM vocab where vision data
  attaches (relevant for native-VL models; can stay null for projection-fusion models)
  - `image_token_id` — int
  - `video_token_id` — int
  - `vision_start_token_id` — int
  - `vision_end_token_id` — int
- `audio_encoder` — string (free-form for now; lift to a structured AudioEncoder when
  we extract a serious audio model)
- `audio_notes` — string

### 5. Top-level: inferred fields and open questions

- `inferred_fields` — list of `{field: "...", basis: "...", confidence: "low"|"medium"|"high"}`
  for closed-model inferences (see [conventions](./conventions.md#inferred-values-closed-models))
- `open_questions` — list of strings — things the extractor flagged as unclear, contested,
  or hitting a current schema gap

## Versioning

Schema versions are integers tracked in the top-level `schema_version` field. Breaking
changes bump the version and are documented in [conventions changelog](./conventions.md#schema-changelog).
Old extractions remain valid against their declared `schema_version` and are migrated
file-by-file when convenient.
