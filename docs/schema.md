# Extraction Schema (v7)

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

| Field            | Type               | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`           | string             | Canonical name, e.g. `"DeepSeek-V3"`, `"Llama-3.1-70B"`                                                                                                                                                                                                                                                                                                                                                                                      |
| `family`         | string             | Family name, e.g. `"DeepSeek"`, `"Llama"`                                                                                                                                                                                                                                                                                                                                                                                                    |
| `release_date`   | string (`YYYY-MM`) | Public release/announcement date                                                                                                                                                                                                                                                                                                                                                                                                             |
| `openness`       | enum               | `"open_source"` / `"open_weights"` / `"closed"`                                                                                                                                                                                                                                                                                                                                                                                              |
| `params_total`   | string             | e.g. `"671B"`, `"70B"` — keep human-readable units                                                                                                                                                                                                                                                                                                                                                                                           |
| `params_active`  | string             | For MoE; equals total for dense models                                                                                                                                                                                                                                                                                                                                                                                                       |
| `sources`        | list of URLs       | Where this extraction was sourced from (paper, HF, blog)                                                                                                                                                                                                                                                                                                                                                                                     |
| `variant_policy` | string             | Free-text — how the vendor partitions capabilities across weight checkpoints vs. runtime modes (v6+). E.g. Qwen3.5/3.6: "unified weights per (size, dense/MoE); thinking / non-thinking / preserve_thinking via chat-template kwargs; coding via post-training plus serving-time tool-call parser; no Math/Coder/VL siblings." Qwen2.5: "separate Instruct/Math/Coder/VL/Audio/Omni checkpoints per capability." UNKNOWN when not disclosed. |

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
- `sparse_attention` — object **(v7+; null for dense attention — the common case)**.
  A content-dependent sparsification / KV-compression *modifier* layered on top of the
  variant above. Distinct from `variants` / `layer_pattern`, which model a hybrid *stack*
  of different attention types: DeepSeek-V3.2-Exp applies DSA uniformly across all 61 MLA
  layers, so it is a modifier, not a variant. When only some layers carry the modifier
  (DeepSeek-V4's CSA layers), fill this with the modifier's parameters and describe the
  split in `layer_pattern`. **Sliding-window attention is not sparse attention in this
  sense** — it is content-blind and belongs in `variants`.
  - `kind` — `"dsa"` / `"csa"` / `"hca"` / `"csa+hca"` / `"nsa"` / `"other"`
  - `selection` — string, how retained entries are chosen (e.g. `"top-k by lightning-indexer score ReLU(q_I · k_I)"`); UNKNOWN when undisclosed
  - `top_k` — int, entries retained per query (HF key `index_topk`)
  - `indexer_heads` — int (HF key `index_n_heads`)
  - `indexer_head_dim` — int (HF key `index_head_dim`)
  - `kv_compression_ratio` — string, so per-variant values fit (e.g. `"4 (CSA) / 128 (HCA)"`);
    UNKNOWN when selection runs over uncompressed KV entries (plain DSA)
  - `training_recipe` — string, how the mechanism was trained in if retrofitted onto a dense
    checkpoint (warm-up steps/tokens, adaptation budget, freezing scheme); empty when trained
    from scratch or undisclosed
  - `notes` — string (free-text)
- `notes` — string **(v7+)**, free text for attention-level details with no dedicated field:
  output gates, NoPE decisions, per-head QK normalization, attention sinks, training-precision
  choices. Empty `""` when the structured fields say everything.

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
  - `latent_dim` — int **(v7+)**, width of the latent space the *routed* experts operate in
    when it is narrower than the model hidden dim. LatentMoE-style designs down-project into
    the routed branch and up-project back to model width, so dispatch traffic and expert
    weights scale with this instead of `hidden_dim`. Kimi K3: `3584` = 0.5 × hidden 7168
    (HF key `routed_expert_hidden_size`). UNKNOWN for conventional MoE, where routed experts
    read and write full model width.
  - `routing` — string describing the routing algorithm (free text)
- `layer_partition` — string (free-text for hybrids, e.g. `"first 3 dense, remaining 58 MoE"`)

#### Base components

- `activation` — e.g. `"SwiGLU"`, `"GeLU"`
- `normalization` — e.g. `"RMSNorm"`, `"LayerNorm"`
- `embedding_notes` — string (tied embeddings? special tokenizer? etc.)

#### Residual connections (optional, v5+)

- `residual_connections` — object **(null when the model uses standard residual
  connections — the common case before DeepSeek-V4)**:
  - `kind` — string, e.g. `"standard"`, `"hyper-connections"`, `"mhc"`
    (manifold-constrained hyper-connections), `"other"`
  - `expansion_factor` — int (n_hc — width expansion of the residual stream;
    1 for standard residual)
  - `constraint` — string (e.g. `"doubly stochastic via Sinkhorn-Knopp"`,
    `"non-expansive Sigmoid"`); empty for standard residual
  - `iterations` — int (solver iterations, e.g. Sinkhorn-Knopp t_max)
  - `dynamic_parameterization` — bool (true when the residual mappings are
    input-dependent; false for static learnable weights only)
  - `notes` — string (free-text)

#### Auxiliary modules (optional, v7+)

- `auxiliary_modules` — list of trained, weight-bearing modules **outside the main backbone
  stack**: speculative-decoding drafts (DeepSeek's DSpark, EAGLE-3 heads), MTP heads regarded
  as shipped weights. Empty `[]` for models that ship only the backbone. These have no home in
  `backbone` (not layers of the main stack) or in `training.objectives` (modules, not
  objectives), and before v7 they smeared across `parallelism_notes` / `layer_partition` /
  `MTPConfig.shared_modules`.
  - `name` — e.g. `"DSpark draft model"`, `"EAGLE-3 draft head"`
  - `purpose` — `"speculative_decoding"` / `"multi_token_prediction"` / `"reward_model"` / `"other"`
  - `architecture` — string, the module's shape; UNKNOWN when undisclosed
  - `shipped_in_checkpoint` — bool; `false` when the module was trained but withheld from the
    open weights (Kimi K3's draft layer: `num_nextn_predict_layers=0`); UNKNOWN when unstated
  - `activation` — string, how a deployment turns it on (serving flags); empty when N/A
  - `notes` — string (free-text)

Note the deliberate overlap with `training.objectives.multi_token_prediction`: MTP is an
objective *and* (sometimes) shipped weights. Record the objective there and the module here
when both apply.

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
  - `inference_modes` — list of `{name, trigger, description, kwargs, sampling_recommended}`
    for runtime-switchable behaviors produced by post-training (e.g. Qwen3's `/think` vs
    `/no_think`, Qwen3.6's `preserve_thinking`, DeepSeek-V4's reasoning-effort triplet).
    Empty list `[]` for single-mode models.
    - `name` — e.g. `"thinking"`, `"non-thinking"`, `"thinking-budget"`, `"preserve-thinking"`
    - `trigger` — string describing how a user activates the mode (chat-template flag,
      system prompt, special token, etc.)
    - `description` — string
    - `kwargs` — `dict[str, str]` (v6+) — machine-readable chat-template kwargs / API
      parameters that activate this mode. Values stringified for portability across JSON
      booleans / Python booleans (e.g. `{"enable_thinking": "false"}`,
      `{"preserve_thinking": "true"}`). Empty when the mode is the default, is triggered
      by prompt content (e.g. soft-switch tokens in user message), or has no toggle.
    - `sampling_recommended` — `dict[str, str]` (v6+) — vendor-recommended sampling
      parameters when this mode is active (`temperature`, `top_p`, `top_k`, `min_p`,
      `presence_penalty`, `repetition_penalty`, etc.). Values stringified. Empty when
      vendor does not disclose per-mode recommendations.
  - `tool_call_protocol` — object or null (v6+) — wire format the model emits for tool
    calls, plus serving-stack parsers that decode it. None when the model has no
    documented tool-calling protocol or it is undisclosed.
    - `format` — string family of the wire format. Suggested values: `"xml-like"`
      (Qwen3-Coder: `<tool_call><function=NAME><parameter=ARG>VALUE</parameter></function></tool_call>`);
      `"json-only"` (a single JSON object inside a special-token pair);
      `"json-in-text"` (JSON inline in normal text, no special tokens);
      `"function-call-token"` (single special token followed by JSON args); `"other"`.
    - `start_token` — string (e.g. `"<tool_call>"`); empty if no delimiters
    - `end_token` — string (e.g. `"</tool_call>"`); empty if N/A
    - `arguments_schema` — string describing how arguments are encoded inside one call
      (e.g. `"per-arg <parameter=name>VALUE</parameter> blocks"`, `"JSON object"`)
    - `parser_flags` — `dict[str, str]` keyed by serving stack, e.g.
      `{"vllm": "--tool-call-parser qwen3_coder", "sglang": "--tool-call-parser qwen3_coder"}`
    - `notes` — string — multi-tool-per-turn handling, version differences, known issues
- `advanced` — object:
  - `self_distillation` — string description (or `"No"`)
  - `mixed_precision` — e.g. `"FP8 + BF16"`, `"BF16"` — what **training** ran in
- `quantization` — object **(v7+; null when the model ships in its training precision)**.
  The low-precision recipe of the **shipped weights**, a design axis distinct from
  `advanced.mixed_precision`: DeepSeek-V4's MXFP4 expert weights, the Kimi K2 family's native
  INT4, Kimi K3's MXFP4 weights + MXFP8 activations, GLM-5's INT4 QAT during SFT.
  - `weight_format` — `"mxfp4"` / `"int4"` / `"fp8-e4m3"` / `"nvfp4"` / …
  - `activation_format` — `"mxfp8"` / `"bf16"` / `"fp8-e4m3 dynamic"` / …
  - `method` — `"qat"` / `"ptq"` / `"other"`
  - `scope` — string, which parameters are quantized (e.g. "routed MoE expert weights only;
    attention projections, shared experts, routers, lm_head and vision tower excluded")
  - `granularity` — string, block/group structure (e.g. `"group_size=32, symmetric"`)
  - `stage` — string, when in the pipeline it is applied (e.g. "QAT from SFT onward through
    all of RL; rollout and training share the scheme, so no train–inference mismatch")
  - `notes` — string (free-text)
- `stability_notes` — string (v5+) — training-stability tricks distinct from
  optimizer / lr_schedule / mixed_precision. E.g. DeepSeek-V4's Anticipatory Routing
  (decoupled routing-net synchronization) and SwiGLU Clamping. Empty `""` when none
  reported.

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
**On any schema bump, every `data/extracted/*.json` must migrate in the same commit** —
`scripts/validate_extractions.py` (the CI gate) requires the declared `schema_version`
to equal the current `SCHEMA_VERSION` constant. For backwards-compatible additions
(new optional fields with defaults) the migration is a one-line `schema_version` bump.
For breaking changes, file shapes must be updated too.
