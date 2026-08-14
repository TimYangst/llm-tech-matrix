"""Pydantic models for the extraction schema (v7).

This is the executable version of docs/schema.md. If the two diverge, this file wins
and docs/schema.md must be updated.

Cardinal rule: when source material does not disclose a value, the field MUST hold the
literal string UNKNOWN below. Do not use None, empty string, or invented values.

Schema changelog: see docs/conventions.md.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 7
UNKNOWN = "[Unknown/Not Disclosed]"

Openness = Literal["open_source", "open_weights", "closed"]
RoPEType = Literal["standard", "yarn", "ntk", "mrope", "none", "[Unknown/Not Disclosed]"]
FFNType = Literal["dense", "moe", "hybrid"]
FusionType = Literal[
    "native_early",  # text and vision tokens share the same backbone+vocab from pre-training (Qwen3.5/3.6)
    "projection_mlp",  # vision encoder + MLP projector mapping into LM hidden_size (Qwen2-VL, LLaVA)
    "cross_attention",  # vision tokens attended-to via dedicated cross-attn layers (Flamingo)
    "resampler",  # Q-Former / Perceiver Resampler downsampling to fixed query count (BLIP-2, MiniCPM-V)
    "other",
    "[Unknown/Not Disclosed]",
]
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
    variant_policy: str = Field(
        default=UNKNOWN,
        description=(
            "How the vendor partitions capabilities across weight checkpoints vs. runtime modes. "
            'E.g. Qwen3.5/3.6: "unified weights per (size, dense/MoE); thinking/non-thinking and '
            "preserve_thinking exposed via chat-template kwargs; coding emphasis via post-training "
            'plus a serving-time tool-call parser; no separate Math/Coder/VL siblings." '
            'vs Qwen2.5: "separate Instruct/Math/Coder/VL/Audio/Omni checkpoints per capability." '
            "Free-text — vendor strategies vary too much to enum. UNKNOWN when not disclosed."
        ),
    )


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


class AttentionVariant(_Strict):
    """One attention variant in a hybrid stack.

    Used when a model interleaves multiple attention types per layer (e.g. Qwen3.5/3.6
    interleave 3 Gated DeltaNet layers with 1 Gated Attention layer in repeating blocks).
    For non-hybrid models, leave Attention.variants empty and use the top-level fields.
    """

    name: str = Field(description='Logical name, e.g. "gated_attention", "gated_deltanet"')
    family: str = Field(
        description='Family: "mha"|"gqa"|"mqa"|"mla"|"linear_attention"|"sliding_window"|"other"'
    )
    num_query_heads: int | str = UNKNOWN
    num_kv_heads: int | str = UNKNOWN
    head_dim: int | str = UNKNOWN
    rope: str = Field(default="", description="Per-variant RoPE description if it differs")
    notes: str = Field(
        default="",
        description=(
            "Variant-specific knobs not covered by other fields, e.g. "
            "'v_heads=32, conv_kernel_dim=4' for Gated DeltaNet"
        ),
    )


class SparseAttentionConfig(_Strict):
    """Content-dependent sparsification and/or KV compression layered on top of an attention variant.

    Distinct from `Attention.variants` / `layer_pattern`, which model a *hybrid stack* of
    different attention types across layers. This subobject models a *modifier* applied to
    an attention variant — e.g. DeepSeek-V3.2-Exp's DSA sits on top of MLA uniformly across
    all 61 layers, and GLM-5 applies the same mechanism on its own MLA. For hybrid stacks
    where only some layers carry the modifier (DeepSeek-V4's CSA layers), populate this with
    the modifier's parameters and describe the layer split in `Attention.layer_pattern`.

    None when the model uses dense attention (the common case). Sliding-window attention is
    NOT sparse attention in this sense — it is content-blind and belongs in `variants`.
    """

    kind: str = Field(
        description=(
            'Mechanism name, e.g. "dsa" (DeepSeek Sparse Attention), "csa" (compressed sparse '
            'attention), "hca" (heavily compressed attention), "nsa" (native sparse attention), '
            '"other".'
        )
    )
    selection: str = Field(
        default=UNKNOWN,
        description=(
            "How the retained entries are chosen, e.g. "
            '"top-k by lightning-indexer score ReLU(q_I . k_I)", "learned block routing". '
            "UNKNOWN when undisclosed."
        ),
    )
    top_k: int | str = Field(
        default=UNKNOWN,
        description="Number of key-value entries retained per query (HF key: index_topk).",
    )
    indexer_heads: int | str = Field(
        default=UNKNOWN, description="Scoring-path head count (HF key: index_n_heads)."
    )
    indexer_head_dim: int | str = Field(
        default=UNKNOWN, description="Scoring-path per-head dim (HF key: index_head_dim)."
    )
    kv_compression_ratio: str = Field(
        default=UNKNOWN,
        description=(
            "Sequence-dimension KV compression applied before/with selection, as a string so "
            'per-variant values fit, e.g. "4 (CSA) / 128 (HCA)". UNKNOWN when the mechanism '
            "selects over uncompressed KV entries (plain DSA)."
        ),
    )
    training_recipe: str = Field(
        default="",
        description=(
            "How the mechanism was trained in, if it was retrofitted onto a dense checkpoint "
            "(warm-up steps/tokens, adaptation budget, frozen-parameter scheme). Empty when "
            "trained from scratch or undisclosed."
        ),
    )
    notes: str = ""


class Attention(_Strict):
    variant: str = Field(description='e.g. "MHA", "GQA", "MLA", "sliding_window", "hybrid"')
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
    variants: list[AttentionVariant] = Field(
        default_factory=list,
        description=(
            "Per-variant detail when the stack interleaves multiple attention variants. "
            "Empty for single-variant models. When non-empty, the top-level "
            "num_heads/num_kv_heads/head_dim should describe the dominant or "
            "full-attention variant for back-compat readers."
        ),
    )
    layer_pattern: str = Field(
        default="",
        description=(
            'Layer ordering pattern for hybrid stacks, e.g. "(L,L,L,F)x10 with '
            'L=gated_deltanet, F=gated_attention". Empty for single-variant stacks.'
        ),
    )
    sparse_attention: SparseAttentionConfig | None = Field(
        default=None,
        description=(
            "Content-dependent sparsification / KV-compression modifier layered on the variant "
            "above (DSA, CSA, HCA, NSA). None for dense attention."
        ),
    )
    notes: str = Field(
        default="",
        description=(
            "Free text for attention-level details with no dedicated field — output gates, "
            "NoPE decisions, per-head QK normalization, attention sinks, training-precision "
            "choices. Empty when the structured fields say everything."
        ),
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
    latent_dim: int | str = Field(
        default=UNKNOWN,
        description=(
            "Width of the latent space the ROUTED experts operate in, when it is narrower than "
            "the model hidden dim (LatentMoE-style designs: a down-projection feeds the routed "
            "branch and an up-projection returns to model width, so dispatch traffic and expert "
            "weights scale with this instead of hidden_dim). Kimi K3: 3584 = 0.5x hidden 7168 "
            "(HF key: routed_expert_hidden_size). UNKNOWN for conventional MoE, where routed "
            "experts read and write full model width."
        ),
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


class ResidualConfig(_Strict):
    """Inter-layer residual-stream topology.

    None / omitted means the model uses standard residual connections (the common case
    before DeepSeek-V4's Manifold-Constrained Hyper-Connections / Hyper-Connections
    family of techniques). Populate when a model expands the residual stream beyond
    R^d into R^(n_hc x d) or otherwise structurally modifies the residual mapping
    between layers.
    """

    kind: str = Field(
        description=(
            'Topology kind, e.g. "standard", "hyper-connections", "mhc" '
            '(manifold-constrained hyper-connections), "other"'
        )
    )
    expansion_factor: int | str = Field(
        default=UNKNOWN,
        description=(
            "Width expansion of the residual stream (n_hc in the HC/mHC papers). "
            "1 for standard residual."
        ),
    )
    constraint: str = Field(
        default="",
        description=(
            "Constraint applied to the residual mapping, e.g. "
            '"doubly stochastic via Sinkhorn-Knopp", "non-expansive Sigmoid". '
            "Empty for standard residual."
        ),
    )
    iterations: int | str = Field(
        default=UNKNOWN,
        description="Solver iterations (e.g. Sinkhorn-Knopp t_max). UNKNOWN if not applicable.",
    )
    dynamic_parameterization: bool | str = Field(
        default=UNKNOWN,
        description=(
            "True when the residual mappings are input-dependent (dynamic), "
            "False when they are static learnable weights only."
        ),
    )
    notes: str = ""


class AuxiliaryModule(_Strict):
    """A trained, weight-bearing module that is not part of the main backbone stack.

    Speculative-decoding drafts (DeepSeek's DSpark, EAGLE-3 heads), MTP heads viewed as
    shipped weights, and similar attachments. These have no home in `backbone` (they are not
    layers of the main stack) or in `training.objectives` (they are modules, not objectives),
    and before v7 they smeared across parallelism_notes / layer_partition / MTP.shared_modules.

    Note the deliberate overlap with `TrainingObjectives.multi_token_prediction`: MTP is an
    objective *and* (sometimes) shipped weights. Record the objective there and the module
    here when both apply.
    """

    name: str = Field(description='e.g. "DSpark draft model", "EAGLE-3 draft head", "MTP head"')
    purpose: str = Field(
        description=(
            'What it is for, e.g. "speculative_decoding", "multi_token_prediction", '
            '"reward_model", "other".'
        )
    )
    architecture: str = Field(
        default=UNKNOWN,
        description=(
            "Shape of the module, e.g. '3 MoE layers with mHC and sliding-window attention "
            "of 128, plus a rank-256 Markov head'. UNKNOWN when undisclosed."
        ),
    )
    shipped_in_checkpoint: bool | str = Field(
        default=UNKNOWN,
        description=(
            "True when the module's weights are in the released checkpoint, False when it was "
            "trained but withheld (Kimi K3's draft layer: config num_nextn_predict_layers=0). "
            "UNKNOWN when the sources do not say."
        ),
    )
    activation: str = Field(
        default="",
        description=(
            "How a deployment turns it on, e.g. "
            '\'vLLM --speculative-config {"method":"dspark"}; SGLang --speculative-algorithm '
            "DSPARK (no separate draft path — same checkpoint)'. Empty when not applicable."
        ),
    )
    notes: str = ""


class Architecture(_Strict):
    backbone: Backbone
    attention: Attention
    ffn: FFN
    components: BaseComponents
    residual_connections: ResidualConfig | None = Field(
        default=None,
        description=(
            "Structured residual-stream topology. None when the model uses standard "
            "residual connections (the common case)."
        ),
    )
    auxiliary_modules: list[AuxiliaryModule] = Field(
        default_factory=list,
        description=(
            "Trained, weight-bearing modules outside the main backbone stack "
            "(speculative-decoding drafts, MTP heads as shipped weights). Empty for models "
            "that ship only the backbone."
        ),
    )
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
    method: str = Field(
        description=(
            'e.g. "sft", "rl", "distillation", "rejection_sampling+sft", '
            '"continued_pretraining" (a pre-training stage that is part of an ordered pipeline '
            "— DeepSeek-V3.2-Exp's DSA warm-up and sparse-adaptation stages), "
            '"quantization_aware_training".'
        )
    )
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
    kwargs: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Machine-readable chat-template kwargs / API parameters that activate this mode. "
            "Values are stringified for portability across JSON booleans / Python booleans "
            '(e.g. {"enable_thinking": "false"}, {"preserve_thinking": "true"}). Empty when '
            "the mode is the default, is triggered by prompt content (e.g. soft-switch tokens "
            "in user message), or has no toggle. Do NOT invent kwargs — only fill from sources."
        ),
    )
    sampling_recommended: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Vendor-recommended sampling parameters when this mode is active "
            "(temperature, top_p, top_k, min_p, presence_penalty, repetition_penalty, etc.). "
            "Values stringified. Empty when the vendor does not disclose per-mode recommendations."
        ),
    )


class ToolCallProtocol(_Strict):
    """Wire format the model emits for tool calls, plus the serving-stack parsers that decode it.

    Captures the *syntactic* protocol (delimiter tokens, argument encoding) — distinct from
    "the model can call tools" (yes/no). Lets synthesis compare e.g. Qwen3-Coder XML-like vs
    JSON-only protocols across vendors. None at the Alignment level when the model has no
    documented tool-calling protocol or when the protocol is undisclosed in source material.
    """

    format: str = Field(
        description=(
            "Family of the wire format. Suggested values: "
            '"xml-like" (Qwen3-Coder: <tool_call><function=NAME><parameter=ARG>VALUE</parameter></function></tool_call>); '
            '"json-only" (a single JSON object inside a special-token pair); '
            '"json-in-text" (JSON object inline in normal text, no special tokens); '
            '"function-call-token" (single special token followed by JSON args); '
            '"other".'
        )
    )
    start_token: str = Field(
        default="",
        description='Special token / delimiter starting a tool call (e.g. "<tool_call>"). Empty if no delimiters.',
    )
    end_token: str = Field(
        default="",
        description='End-of-tool-call delimiter (e.g. "</tool_call>"). Empty if N/A.',
    )
    arguments_schema: str = Field(
        default="",
        description=(
            'How arguments are encoded inside one call. Examples: "JSON object as the function body"; '
            '"per-arg <parameter=name>VALUE</parameter> blocks (string-typed values; non-string '
            'scalars are JSON-encoded in Qwen3.6, str()-stringified in Qwen3.5)"; "key=value lines".'
        ),
    )
    parser_flags: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Serving-stack parser flag(s) that decode this protocol, keyed by serving stack. "
            'E.g. {"vllm": "--tool-call-parser qwen3_coder", '
            '"sglang": "--tool-call-parser qwen3_coder"}. Empty when no published parser flag.'
        ),
    )
    notes: str = Field(
        default="",
        description=(
            "Free-text — multi-tool-per-turn handling, version differences, known issues, "
            "tool-result protocol if it differs from the call protocol, etc."
        ),
    )


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
    tool_call_protocol: ToolCallProtocol | None = Field(
        default=None,
        description=(
            "Structured wire format the model uses for tool calls. None when the model has "
            "no documented tool-calling protocol (or it is undisclosed in source material). "
            "The model can still support tool calling without this being populated — populate "
            "only when the *wire format* is documented."
        ),
    )


class QuantizationConfig(_Strict):
    """Low-precision deployment recipe, distinct from training-time mixed precision.

    `Advanced.mixed_precision` describes what the TRAINING ran in (FP8 GEMMs, BF16 master
    weights). This subobject describes what the SHIPPED WEIGHTS are, which by 2026 is a
    separate design axis with its own cross-vendor story: DeepSeek-V4 MXFP4 expert weights,
    the Kimi K2 family's native INT4, Kimi K3's MXFP4 weights + MXFP8 activations, GLM-5's
    INT4 QAT during SFT. None when the model ships in its training precision.
    """

    weight_format: str = Field(
        description='e.g. "mxfp4", "int4", "fp8-e4m3", "nvfp4". UNKNOWN if undisclosed.'
    )
    activation_format: str = Field(
        default=UNKNOWN,
        description='e.g. "mxfp8", "bf16", "fp8-e4m3 dynamic". UNKNOWN if undisclosed.',
    )
    method: str = Field(
        default=UNKNOWN,
        description='"qat" (quantization-aware training), "ptq" (post-training quantization), "other".',
    )
    scope: str = Field(
        default=UNKNOWN,
        description=(
            "Which parameters are quantized, e.g. 'routed MoE expert weights only; attention "
            "projections, shared experts, routers, lm_head and vision tower excluded'."
        ),
    )
    granularity: str = Field(
        default=UNKNOWN,
        description='Block/group structure, e.g. "group_size=32, symmetric", "block 128x128".',
    )
    stage: str = Field(
        default="",
        description=(
            "When in the pipeline quantization is applied, e.g. 'QAT from SFT onward through "
            "all of RL; rollout and training share the scheme, so no train-inference mismatch'. "
            "Empty when not disclosed."
        ),
    )
    notes: str = ""


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
    quantization: QuantizationConfig | None = Field(
        default=None,
        description=(
            "Low-precision recipe of the SHIPPED weights (vs Advanced.mixed_precision, which "
            "describes training precision). None when the model ships in training precision."
        ),
    )
    stability_notes: str = Field(
        default="",
        description=(
            "Training-stability tricks distinct from optimizer / lr_schedule / mixed_precision. "
            "E.g. DeepSeek-V4's Anticipatory Routing (decoupled routing-net sync) and "
            "SwiGLU Clamping. Empty when none reported."
        ),
    )


# ---------- 4. Multimodal ----------


class VisionEncoder(_Strict):
    """Structured vision-encoder details.

    Field names follow HF `vision_config` conventions where they exist (depth,
    hidden_size, intermediate_size, num_heads, patch_size, in_channels, spatial_merge_size,
    temporal_patch_size). Use UNKNOWN for fields not exposed in source material.
    """

    architecture: str = Field(
        description='Architecture family, e.g. "ViT", "ViT with window attention", "EVA-CLIP"'
    )
    depth: int | str = UNKNOWN
    hidden_size: int | str = UNKNOWN
    intermediate_size: int | str = UNKNOWN
    num_heads: int | str = UNKNOWN
    patch_size: int | str = UNKNOWN
    in_channels: int | str = UNKNOWN
    output_dim: int | str = Field(
        default=UNKNOWN,
        description=(
            "Projected output dim that feeds into the LM hidden stream. For native VL, "
            "this typically equals LM hidden_size after spatial_merge."
        ),
    )
    spatial_merge_size: int | str = UNKNOWN
    temporal_patch_size: int | str = Field(
        default=UNKNOWN, description="Temporal patch size for video frames"
    )
    notes: str = Field(
        default="",
        description=(
            "Free-form notes — window-attention layout, special block indexes, "
            "training data origin, etc."
        ),
    )


class VisionTokenAnchors(_Strict):
    """Token IDs in the LM vocab where vision data attaches.

    Native-VL models reuse the LM vocab for vision (specific token IDs are reserved
    for image patches and surround markers); projection-fusion models may not need
    these and can leave them UNKNOWN.
    """

    image_token_id: int | str = UNKNOWN
    video_token_id: int | str = UNKNOWN
    vision_start_token_id: int | str = UNKNOWN
    vision_end_token_id: int | str = UNKNOWN


class Multimodal(_Strict):
    """Multimodal architecture details.

    Required when the model handles non-text modalities. For text-only LMs, the
    top-level `multimodal` field stays None.
    """

    modalities: list[str] = Field(
        default_factory=list,
        description='e.g. ["text"], ["text","image"], ["text","image","video"], ["text","image","video","audio"]',
    )
    fusion: FusionType
    fusion_notes: str = Field(
        default="",
        description="Free text describing fusion specifics (early vs late, projector shape, training stage timing)",
    )
    vision_encoder: VisionEncoder | None = None
    vision_token_anchors: VisionTokenAnchors | None = None
    audio_encoder: str = Field(
        default=UNKNOWN,
        description=(
            "Free-form audio encoder description for now. When we extract a serious "
            "audio model, lift this to a structured AudioEncoder subobject."
        ),
    )
    audio_notes: str = ""


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
