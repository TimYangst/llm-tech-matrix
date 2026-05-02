"""Pydantic models for the extraction schema.

This is the executable version of docs/schema.md. If the two diverge, this file wins
and docs/schema.md must be updated.

Cardinal rule: when source material does not disclose a value, the field MUST hold the
literal string UNKNOWN below. Do not use None, empty string, or invented values.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1
UNKNOWN = "[Unknown/Not Disclosed]"

Openness = Literal["open_source", "open_weights", "closed"]
RoPEType = Literal["standard", "yarn", "ntk", "none", "[Unknown/Not Disclosed]"]
FFNType = Literal["dense", "moe"]
FusionType = Literal["native", "projected", "cross_attention", "other", "[Unknown/Not Disclosed]"]
Confidence = Literal["low", "medium", "high"]


class _Strict(BaseModel):
    """Base model that forbids extra fields — extraction must match the schema exactly."""

    model_config = ConfigDict(extra="forbid")


class ModelMetadata(_Strict):
    name: str
    family: str
    release_date: str = Field(description="YYYY-MM, or UNKNOWN")
    openness: Openness
    params_total: str
    params_active: str
    sources: list[str] = Field(description="URLs the extraction was sourced from")


class RoPEConfig(_Strict):
    type: RoPEType
    base: int | str = UNKNOWN
    scaling: dict | None = None


class Attention(_Strict):
    variant: str = Field(description='e.g. "MHA", "GQA", "MLA", "sliding_window"')
    num_heads: int | str = UNKNOWN
    num_kv_heads: int | str = UNKNOWN
    head_dim: int | str = UNKNOWN
    rope: RoPEConfig


class Backbone(_Strict):
    layers: int | str = UNKNOWN
    hidden_dim: int | str = UNKNOWN
    context_window: int | str = UNKNOWN


class MoEConfig(_Strict):
    num_experts: int | str = UNKNOWN
    num_active_experts: int | str = UNKNOWN
    routing: str
    shared_experts: int | str = UNKNOWN


class FFN(_Strict):
    ffn_type: FFNType
    intermediate_size: int | str = UNKNOWN
    moe: MoEConfig | None = Field(
        default=None, description="Required when ffn_type == 'moe', otherwise None"
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


class Alignment(_Strict):
    sft: str
    rl_method: str = Field(description='e.g. "PPO", "DPO", "GRPO", "RLHF", or UNKNOWN')
    rlaif: bool | str = UNKNOWN


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
    alignment: Alignment
    advanced: Advanced


class Multimodal(_Strict):
    vision_encoder: str
    audio_encoder: str
    fusion: FusionType
    fusion_notes: str


class InferredField(_Strict):
    field: str = Field(description="Dotted path of the inferred field, e.g. 'architecture.backbone.layers'")
    basis: str = Field(description="Citation or reasoning for the inference")
    confidence: Confidence


class ExtractedModel(_Strict):
    """Top-level schema for an extracted model JSON.

    One file per model: data/extracted/<slug>.json validates against this model.
    """

    schema_version: int = SCHEMA_VERSION
    metadata: ModelMetadata
    architecture: Architecture
    training: Training
    multimodal: Multimodal | None = Field(
        default=None, description="Required for multimodal models, None otherwise"
    )
    inferred_fields: list[InferredField] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
