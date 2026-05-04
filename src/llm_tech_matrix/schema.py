"""Pydantic models for the extraction schema (v3).

This is the executable version of docs/schema.md. If the two diverge, this file wins
and docs/schema.md must be updated.

Cardinal rule: when source material does not disclose a value, the field MUST hold the
literal string UNKNOWN below. Do not use None, empty string, or invented values.

Schema changelog: see docs/conventions.md.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 3
UNKNOWN = "[Unknown/Not Disclosed]"

Openness = Literal["open_source", "open_weights", "closed"]
RoPEType = Literal["standard", "yarn", "ntk", "none", "[Unknown/Not Disclosed]"]
FFNType = Literal["dense", "moe", "hybrid"]
FusionType = Literal["native", "projected", "cross_attention", "other", "[Unknown/Not Disclosed]"]
Confidence = Literal["low", "medium", "high"]


class _Strict(BaseModel):
    """Forbid extra fields — extraction must match the schema exactly."""

    model_config = ConfigDict(extra="forbid")


# ---------- 1. Metadata ----------


class ModelMetadata(_Strict):
    name: str
    family: str
    release_date: str = Field(description="YYYY-MM, or UNKNOWN")
    openness: Openness
    params_total: str
    params_active: str
    sources: list[str] = Field(description="URLs the extraction was sourced from")


# ---------- 2. Architecture ----------


class RoPEConfig(_Strict):
    type: RoPEType
    base: int | str = UNKNOWN
    scaling: dict | None = None


class MLAConfig(_Strict):
    """Multi-head Latent Attention specifics.

    Field names mirror HuggingFace config keys so extractors can read them off
    config.json directly.
    """

    kv_lora_rank: int | str = UNKNOWN
    q_lora_rank: int | str = UNKNOWN
    qk_nope_head_dim: int | str = UNKNOWN
    qk_rope_head_dim: int | str = UNKNOWN
    v_head_dim: int | str = UNKNOWN


class Attention(_Strict):
    variant: str = Field(description='e.g. "MHA", "GQA", "MLA", "sliding_window"')
    num_heads: int | str = UNKNOWN
    num_kv_heads: int | str = Field(
        default=UNKNOWN,
        description="Meaningful for MHA/GQA. For MLA, set to UNKNOWN (use the mla subobject instead).",
    )
    head_dim: int | str = Field(
        default=UNKNOWN,
        description="Meaningful for MHA/GQA. For MLA, the per-head dim is split across mla.qk_nope_head_dim + mla.qk_rope_head_dim.",
    )
    rope: RoPEConfig
    mla: MLAConfig | None = Field(
        default=None, description="Required when variant == 'MLA', otherwise None"
    )


class ContextExtension(_Strict):
    """Structured record of how a model's productized context was reached.

    For models trained at length T and deployed at length T' > T via a scaling method
    (YaRN, DCA, LongRoPE, ABF, sliding+global, etc.). For models that ship at exactly
    their trained length and apply no extension, leave Backbone.context_extension as None.
    """

    method: str = Field(
        description='e.g. "yarn", "yarn+dca", "longrope", "abf+yarn", "sliding+global"'
    )
    trained_max: int | str = Field(
        default=UNKNOWN, description="Maximum sequence length seen during pre-training"
    )
    extended_max: int | str = Field(
        description="Productized max context length (= Backbone.context_window)"
    )
    factor: float | str = Field(
        default=UNKNOWN, description="Scaling factor (e.g. YaRN factor) — extended/original"
    )
    original_max: int | str = Field(
        default=UNKNOWN,
        description='YaRN-style "original_max_position_embeddings" (the pre-extension RoPE base length)',
    )
    notes: str = ""


class Backbone(_Strict):
    layers: int | str = UNKNOWN
    hidden_dim: int | str = UNKNOWN
    context_window: int | str = Field(
        description="Canonical user-facing max context length (e.g. 131072 for '128K')"
    )
    context_window_notes: str = Field(
        default="",
        description="Free-text for discrepancies (paper vs config), extension method, or caveats",
    )
    context_extension: ContextExtension | None = Field(
        default=None,
        description=(
            "Structured extension record. None when the model uses its trained length "
            "directly without scaling tricks."
        ),
    )


class MoEConfig(_Strict):
    num_experts: int | str = UNKNOWN
    num_active_experts: int | str = UNKNOWN
    shared_experts: int | str = UNKNOWN
    expert_intermediate_size: int | str = Field(
        default=UNKNOWN, description="Per-expert FFN intermediate width"
    )
    routing: str = Field(description="Routing algorithm description (free text)")


class FFN(_Strict):
    ffn_type: FFNType
    dense_intermediate_size: int | str | None = Field(
        default=None,
        description='Dense FFN intermediate size. Required if ffn_type in {"dense","hybrid"}, else None.',
    )
    moe: MoEConfig | None = Field(
        default=None,
        description='Required if ffn_type in {"moe","hybrid"}, else None.',
    )
    layer_partition: str = Field(
        default="",
        description='Free text describing layer split for hybrids, e.g. "first 3 dense, remaining 58 MoE"',
    )


class BaseComponents(_Strict):
    activation: str
    normalization: str
    embedding_notes: str


class Architecture(_Strict):
    backbone: Backbone
    attention: Attention
    ffn: FFN
    components: BaseComponents
    parallelism_notes: str


# ---------- 3. Training ----------


class MTPConfig(_Strict):
    """Multi-Token Prediction objective."""

    depth: int | str = Field(
        description="D in the paper — number of additional tokens predicted beyond next-token"
    )
    loss_weight_schedule: str = Field(
        description='Free-text description of the loss weight, e.g. "0.3 first 10T tokens, then 0.1"'
    )
    shared_modules: str = Field(
        default="",
        description='Which modules are shared with the main model (e.g. "embedding and output head")',
    )


class FIMConfig(_Strict):
    """Fill-in-Middle pre-training augmentation."""

    format: str = Field(description='e.g. "PSM (Prefix-Suffix-Middle)"')
    rate: str = Field(description='e.g. "0.1"')


class TrainingObjectives(_Strict):
    """Beyond next-token-prediction (which is implicit). Add new objectives here over time."""

    multi_token_prediction: MTPConfig | None = None
    fill_in_middle: FIMConfig | None = None
    other: list[str] = Field(
        default_factory=list,
        description="Free-form for novel objectives without a dedicated slot yet",
    )


class AlignmentStage(_Strict):
    """One named stage in a multi-stage post-training pipeline.

    Use the `stages` list when a model runs a structured pipeline (e.g. Qwen3's four-stage
    Long-CoT Cold Start → Reasoning RL → Thinking Mode Fusion → General RL). For simple
    SFT+RL pipelines (DeepSeek-V3 style), the flat `sft`/`rl_method` fields are enough
    and `stages` may be left empty.
    """

    name: str = Field(description='e.g. "Long-CoT Cold Start", "Reasoning RL"')
    method: str = Field(description='e.g. "sft", "rl", "distillation", "rejection_sampling+sft"')
    description: str = Field(description="Data, signals, key recipe details")


class InferenceMode(_Strict):
    """A runtime-switchable behavior produced by post-training.

    Use this for chat-template-driven modes (Qwen3 thinking/non-thinking), thinking-budget
    style controls, or other behaviors that the user toggles at inference time without
    swapping weights.
    """

    name: str = Field(description='e.g. "thinking", "non-thinking", "thinking-budget"')
    trigger: str = Field(
        description='How the user activates this mode, e.g. "/think flag", "system prompt"'
    )
    description: str


class Alignment(_Strict):
    sft: str
    rl_method: str = Field(description='e.g. "PPO", "DPO", "GRPO", "RLHF", or UNKNOWN')
    rlaif: bool | str = Field(
        default=UNKNOWN,
        description=(
            "True only if AI generates the preference labels themselves (e.g. Constitutional AI). "
            "A model-based reward model trained on human preferences is RLHF, NOT RLAIF."
        ),
    )
    stages: list[AlignmentStage] = Field(
        default_factory=list,
        description=(
            "Multi-stage post-training pipeline. Empty list when a flat SFT+RL "
            "description (the sft/rl_method fields above) is sufficient."
        ),
    )
    inference_modes: list[InferenceMode] = Field(
        default_factory=list,
        description=(
            "Runtime-switchable modes the user can toggle at inference. "
            "Empty list when the model has a single mode of operation."
        ),
    )


class Advanced(_Strict):
    self_distillation: str
    mixed_precision: str


class Training(_Strict):
    optimizer: str
    lr_schedule: str
    data_total_tokens: str
    data_mix: dict[str, str] = Field(
        default_factory=dict, description='e.g. {"code": "17%", "math": "10%", "text": "73%"}'
    )
    data_mix_notes: str = Field(
        default="",
        description="Free-text for qualitative descriptions when no percentages are disclosed",
    )
    objectives: TrainingObjectives = Field(default_factory=TrainingObjectives)
    alignment: Alignment
    advanced: Advanced


# ---------- 4. Multimodal ----------


class Multimodal(_Strict):
    vision_encoder: str
    audio_encoder: str
    fusion: FusionType
    fusion_notes: str


# ---------- 5. Top-level ----------


class InferredField(_Strict):
    field: str = Field(
        description="Dotted path of the inferred field, e.g. 'architecture.backbone.layers'"
    )
    basis: str = Field(description="Citation or reasoning for the inference")
    confidence: Confidence


class ExtractedModel(_Strict):
    """Top-level schema. One file per model: data/extracted/<slug>.json validates against this."""

    schema_version: int = SCHEMA_VERSION
    metadata: ModelMetadata
    architecture: Architecture
    training: Training
    multimodal: Multimodal | None = Field(
        default=None, description="Required for multimodal models, None otherwise"
    )
    inferred_fields: list[InferredField] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
