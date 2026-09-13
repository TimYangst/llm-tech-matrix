"""Pydantic models for the engine snapshot schema (engine schema v2).

Engines (vLLM, SGLang, verl, VeOmni) are a second record type, parallel to the model
records validated by `schema.py`. Records live at `data/extracted/engines/<slug>.json`.
Design and rationale: docs/engines/overview.md. Field spec: docs/engines/schema.md.

The version is independent of the model schema's SCHEMA_VERSION; bumps are logged in the
"Engine schema changelog" section of docs/conventions.md.

Cardinal rules carried over from the model track, tightened for engines:

- Missing information is the literal string UNKNOWN below.
- Every support claim carries evidence: URLs pinned to the snapshot commit (GitHub `blob/<sha>`
  URLs with `#L` line anchors where possible) or the tag's release notes. `EngineRecord`
  enforces that populated role-subobject fields, parallelism entries, integrations, model
  rows and technique rows all cite something.
- Each role has exactly one subobject: `inference` -> `serving`, `training` -> `training`,
  `rl_post_training` -> `rl`. A subobject is present exactly when its role is claimed.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ENGINE_SCHEMA_VERSION = 2
UNKNOWN = "[Unknown/Not Disclosed]"

EngineRole = Literal["inference", "training", "rl_post_training"]
ROLE_SUBOBJECTS: dict[str, str] = {
    "inference": "serving",
    "training": "training",
    "rl_post_training": "rl",
}
# The counterpart's role relative to THIS engine: verl's record lists vLLM as its
# `rollout_backend`; VeOmni's record lists verl as `used_by`.
IntegrationRelation = Literal[
    "kernel_library", "kv_transfer", "rollout_backend", "training_backend", "used_by", "other"
]
SupportLevel = Literal["registered", "model_specific", "not_found"]


class _Strict(BaseModel):
    """Forbid extra fields, as in the model schema."""

    model_config = ConfigDict(extra="forbid")


# ---------- 1. Metadata ----------


class EngineMetadata(_Strict):
    name: str = Field(description='Display name, e.g. "vLLM"')
    engine: str = Field(description='Lowercase engine id used in slugs, e.g. "vllm"')
    organization: str = Field(description='Upstream GitHub org, e.g. "vllm-project"')
    repository: str = Field(description="Upstream repository URL (never a fork)")
    license: str = Field(description='SPDX id, e.g. "Apache-2.0"')
    release_tag: str = Field(description='The snapshot tag, e.g. "v0.29.0"')
    commit_sha: str = Field(description="Full 40-character commit the tag resolves to")
    release_date: str = Field(description="YYYY-MM-DD the release was published, or UNKNOWN")
    snapshot_date: str = Field(description="YYYY-MM-DD the snapshot was taken")
    roles: list[EngineRole]
    hardware: list[str] = Field(
        default_factory=list,
        description="Accelerator platforms the snapshot's own sources name (NVIDIA, AMD ROCm, ...)",
    )
    sources: list[str] = Field(description="Every URL in the snapshot's manifest")


# ---------- 2. Parallelism ----------


class ParallelismEntry(_Strict):
    """One parallelism dimension. `supported` is True only with evidence; UNKNOWN otherwise."""

    supported: bool | str = UNKNOWN
    implementation: str = Field(
        default="", description="Config keys / flags / mechanism, e.g. 'tensor_parallel_size'"
    )
    notes: str = ""
    evidence: list[str] = Field(default_factory=list)


class Parallelism(_Strict):
    tensor: ParallelismEntry = Field(default_factory=ParallelismEntry)
    pipeline: ParallelismEntry = Field(default_factory=ParallelismEntry)
    data: ParallelismEntry = Field(default_factory=ParallelismEntry)
    expert: ParallelismEntry = Field(default_factory=ParallelismEntry)
    context: ParallelismEntry = Field(
        default_factory=ParallelismEntry,
        description="Context parallelism over the sequence (prefill and/or decode variants)",
    )
    sequence: ParallelismEntry = Field(
        default_factory=ParallelismEntry,
        description="Activation sequence parallelism (Megatron-style SP / Ulysses)",
    )


# ---------- 3. Role subobjects ----------


class _EvidencedSection(_Strict):
    """A role subobject whose populated fields each carry evidence.

    List fields record the engine's own registries at the pinned commit (method literals,
    enum members, config choices), so they are reproducible rather than curated. Prose fields
    summarize the design docs. `evidence` maps each populated field name to the URLs that back
    it; validation requires an entry for every populated field and no entries for empty ones.
    """

    def populated_fields(self) -> list[str]:
        out = []
        for name in type(self).model_fields:
            if name in ("notes", "evidence"):
                continue
            value = getattr(self, name)
            if value and value != UNKNOWN:
                out.append(name)
        return out

    def evidence_errors(self, section: str) -> list[str]:
        populated = self.populated_fields()
        evidence: dict[str, list[str]] = getattr(self, "evidence")  # noqa: B009
        errors = [f"{section}.{f}: no evidence" for f in populated if not evidence.get(f)]
        errors += [
            f"{section}.evidence[{k!r}]: field is not populated"
            for k in sorted(set(evidence) - set(populated))
        ]
        return errors


class Serving(_EvidencedSection):
    """The `inference` role: what the serving engine offers at this snapshot."""

    api_surfaces: list[str] = Field(default_factory=list)
    scheduler: str = UNKNOWN
    kv_cache_management: str = UNKNOWN
    prefix_caching: str = UNKNOWN
    disaggregation: str = Field(
        default=UNKNOWN, description="Prefill/decode and encoder disaggregation, KV connectors"
    )
    speculative_decoding_methods: list[str] = Field(default_factory=list)
    quantization_methods: list[str] = Field(default_factory=list)
    kv_cache_dtypes: list[str] = Field(default_factory=list)
    attention_backends: list[str] = Field(default_factory=list)
    reasoning_parsers: list[str] = Field(default_factory=list)
    tool_call_parsers: list[str] = Field(default_factory=list)
    notes: str = ""
    evidence: dict[str, list[str]] = Field(default_factory=dict)


class Training(_EvidencedSection):
    """The `training` role: what a training framework offers at this snapshot (added in v2).

    Driven by VeOmni v0.1.12 (a training framework) and verl v0.9.0 (whose SFT trainer and
    training engines are documented alongside its RL loop).
    """

    workloads: list[str] = Field(
        default_factory=list,
        description="Training workloads the sources document, e.g. 'pre-training', 'sft', 'dpo'",
    )
    backends: list[str] = Field(
        default_factory=list,
        description="Selectable training backends / engines as the config names them",
    )
    optimizers: list[str] = Field(default_factory=list)
    mixed_precision: str = UNKNOWN
    quantization_aware_training: str = UNKNOWN
    checkpointing: str = UNKNOWN
    lora: str = UNKNOWN
    kernels: str = Field(
        default=UNKNOWN, description="Kernel libraries / fused ops and how they are selected"
    )
    notes: str = ""
    evidence: dict[str, list[str]] = Field(default_factory=dict)


class RLPostTraining(_EvidencedSection):
    """The `rl_post_training` role: what an RL post-training framework offers (added in v2).

    Driven by verl v0.9.0. `rollout_backends` names inference engines, which may themselves be
    tracked snapshots — the version constraints live on `integrations[]`.
    """

    algorithms: list[str] = Field(
        default_factory=list,
        description="Algorithm / advantage-estimator identifiers as the code names them",
    )
    policy_losses: list[str] = Field(default_factory=list)
    rollout_backends: list[str] = Field(default_factory=list)
    trainer_modes: list[str] = Field(
        default_factory=list, description="Sync / async trainer modes as the config names them"
    )
    weight_sync: str = Field(
        default=UNKNOWN, description="How trained weights reach the rollout engine"
    )
    weight_sync_backends: list[str] = Field(default_factory=list)
    routing_replay: str = Field(
        default=UNKNOWN, description="MoE routing replay between rollout and training"
    )
    reward: str = UNKNOWN
    distillation: str = Field(default=UNKNOWN, description="On-policy distillation support")
    notes: str = ""
    evidence: dict[str, list[str]] = Field(default_factory=dict)


# ---------- 4. Cross-links ----------


class Integration(_Strict):
    name: str = Field(description='e.g. "FlashInfer", "NIXL"')
    relation: IntegrationRelation
    engine_slug: str | None = Field(
        default=None, description="Engine snapshot slug when the counterpart is itself tracked"
    )
    version_constraints: list[str] = Field(
        default_factory=list,
        description=(
            "Versions of the counterpart this snapshot requires or was tested with, each naming "
            "its source, e.g. 'setup.py: vllm>=0.18.0', 'Dockerfile.stable.vllm: 0.24.0'. Record "
            "disagreeing sources side by side (added in v2)."
        ),
    )
    notes: str = ""
    evidence: list[str] = Field(min_length=1)


class ModelDetail(_Strict):
    """Facts about one model record that do not follow from its architecture.

    Two models can share an HF architecture yet differ here: SGLang v0.5.19 maps Kimi K2
    Thinking (DeepseekV3ForCausalLM) to the `kimi_k2` parsers while DeepSeek-V3 gets none, and
    lists Qwen3.8-27B as new in that release although its Qwen3_5ForConditionalGeneration
    architecture was already supported.
    """

    model_slug: str = Field(description="Must be one of the parent row's `model_slugs`")
    since_version: str = Field(
        default=UNKNOWN, description="Only when release notes or history state it for this model"
    )
    reasoning_parser: str = Field(
        default=UNKNOWN, description="Only when the engine's docs map this model to a parser"
    )
    tool_call_parser: str = Field(
        default=UNKNOWN, description="Only when the engine's docs map this model to a parser"
    )
    notes: str = ""
    evidence: list[str] = Field(min_length=1)


class ModelSupport(_Strict):
    """One model architecture as the engine sees it at this snapshot.

    `support` (v2, replacing v1's `in_native_registry: bool`):
    - `registered` — in the engine's built-in model registry, whatever form it takes: vLLM's
      static `registry.py` table, SGLang's `EntryClass` declarations, VeOmni's
      `MODELING_REGISTRY` keyed by model_type.
    - `model_specific` — no registry entry (or the engine has no registry, like verl), but the
      snapshot carries code or docs written for this architecture / its model_type.
    - `not_found` — neither. This is a fact about the snapshot, not a claim the model cannot run:
      generic loading paths (HF Transformers backends, FSDP on any HF model) may still work.
    """

    hf_architecture: str = Field(description="HF `architectures[0]`, the join key to models")
    model_slugs: list[str] = Field(
        default_factory=list,
        description="data/extracted/<slug>.json records using this architecture",
    )
    support: SupportLevel
    implementation: str = Field(
        default=UNKNOWN,
        description="Module / class / patch that implements it; UNKNOWN when not found",
    )
    documented: bool | str = Field(
        default=UNKNOWN,
        description=(
            "Covered by the engine's supported-models documentation at this snapshot. Docs may be "
            "architecture-level (vLLM) or family-level (SGLang); `notes` says which."
        ),
    )
    features: dict[str, str] = Field(
        default_factory=dict,
        description="Per-model feature columns from the docs, e.g. {'lora': 'marked', 'pp': 'marked'}",
    )
    speculative_decoding: list[str] = Field(
        default_factory=list,
        description="Methods with architecture-specific handling in code or docs (e.g. 'mtp', 'dspark')",
    )
    model_details: list[ModelDetail] = Field(
        default_factory=list,
        description="Per-model facts: since_version and doc-stated parser mappings",
    )
    notes: str = ""
    evidence: list[str] = Field(min_length=1)


class TechniqueSupport(_Strict):
    """An engine-side implementation of a glossary technique (an assertion, not a mention)."""

    glossary_slug: str = Field(description="Must exist in docs/glossary/")
    implementation: str
    flags: list[str] = Field(default_factory=list)
    since_version: str = UNKNOWN
    notes: str = ""
    evidence: list[str] = Field(min_length=1)


# ---------- 5. Top-level ----------


class EngineRecord(_Strict):
    """One engine snapshot. data/extracted/engines/<slug>.json validates against this."""

    engine_schema_version: int = ENGINE_SCHEMA_VERSION
    metadata: EngineMetadata
    parallelism: Parallelism = Field(default_factory=Parallelism)
    serving: Serving | None = None
    training: Training | None = None
    rl: RLPostTraining | None = None
    integrations: list[Integration] = Field(default_factory=list)
    model_support: list[ModelSupport] = Field(default_factory=list)
    technique_support: list[TechniqueSupport] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _roles_and_evidence(self) -> "EngineRecord":
        roles = set(self.metadata.roles)
        errors: list[str] = []
        for role, attr in ROLE_SUBOBJECTS.items():
            section = getattr(self, attr)
            if (role in roles) != (section is not None):
                errors.append(f"`{attr}` must be present exactly when roles include {role!r}")
            if section is not None:
                errors += section.evidence_errors(attr)
        if errors:
            raise ValueError("; ".join(errors))
        for row in self.model_support:
            slugs = [d.model_slug for d in row.model_details]
            stray = sorted(set(slugs) - set(row.model_slugs))
            if stray:
                raise ValueError(
                    f"{row.hf_architecture}: model_details for non-member slugs {stray}"
                )
            if len(slugs) != len(set(slugs)):
                raise ValueError(f"{row.hf_architecture}: duplicate model_details entries")
        for name in type(self.parallelism).model_fields:
            entry: ParallelismEntry = getattr(self.parallelism, name)
            if entry.supported != UNKNOWN and not entry.evidence:
                raise ValueError(f"parallelism.{name}: a known `supported` value needs evidence")
        return self
