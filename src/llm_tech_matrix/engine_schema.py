"""Pydantic models for the engine snapshot schema (engine schema v1).

Engines (vLLM, SGLang, verl, VeOmni) are a second record type, parallel to the model
records validated by `schema.py`. Records live at `data/extracted/engines/<slug>.json`.
Design and rationale: docs/engines/overview.md. Field spec: docs/engines/schema.md.

The version is independent of the model schema's SCHEMA_VERSION; bumps are logged in the
"Engine schema changelog" section of docs/conventions.md.

Cardinal rules carried over from the model track, tightened for engines:

- Missing information is the literal string UNKNOWN below.
- Every support claim carries evidence: URLs pinned to the snapshot commit (GitHub `blob/<sha>`
  URLs with `#L` line anchors where possible) or the tag's release notes. `EngineRecord`
  enforces that populated serving fields, parallelism entries, model rows and technique rows
  all cite something.
- v1 implements only the `inference` role. `training` and `rl_post_training` are part of the
  vocabulary but their subobjects arrive with the first snapshot that needs them (E3), so a
  record claiming those roles fails validation for now instead of silently carrying nothing.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ENGINE_SCHEMA_VERSION = 1
UNKNOWN = "[Unknown/Not Disclosed]"

EngineRole = Literal["inference", "training", "rl_post_training"]
IMPLEMENTED_ROLES: frozenset[str] = frozenset({"inference"})
IntegrationRelation = Literal[
    "kernel_library", "kv_transfer", "rollout_backend", "training_backend", "other"
]


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


class Serving(_Strict):
    """The `inference` role: what the serving engine offers at this snapshot.

    List fields record the engine's own registries at the pinned commit (method literals,
    enum members, parser registries), so they are reproducible rather than curated. Prose
    fields summarize the design docs. `evidence` maps each populated field name to the URLs
    that back it; validation requires an entry for every populated field.
    """

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

    def populated_fields(self) -> list[str]:
        out = []
        for name in type(self).model_fields:
            if name in ("notes", "evidence"):
                continue
            value = getattr(self, name)
            if value and value != UNKNOWN:
                out.append(name)
        return out


# ---------- 4. Cross-links ----------


class Integration(_Strict):
    name: str = Field(description='e.g. "FlashInfer", "NIXL"')
    relation: IntegrationRelation
    engine_slug: str | None = Field(
        default=None, description="Engine snapshot slug when the counterpart is itself tracked"
    )
    notes: str = ""
    evidence: list[str] = Field(min_length=1)


class ModelSupport(_Strict):
    """One model architecture as the engine sees it at this snapshot.

    Absence is recorded too: an architecture missing from an exhaustive native registry is a
    fact about the snapshot. It is not a claim that the model cannot run (fallback backends
    or plugins may exist), which is why the field is `in_native_registry`, not `supported`.
    """

    hf_architecture: str = Field(description="HF `architectures[0]`, the join key to models")
    model_slugs: list[str] = Field(
        default_factory=list,
        description="data/extracted/<slug>.json records using this architecture",
    )
    in_native_registry: bool
    implementation: str = Field(
        default=UNKNOWN, description="Module / class the registry maps to; UNKNOWN when absent"
    )
    documented: bool | str = Field(
        default=UNKNOWN,
        description="Listed in the engine's supported-models documentation at this snapshot",
    )
    features: dict[str, str] = Field(
        default_factory=dict,
        description="Per-model feature columns from the docs, e.g. {'lora': 'marked', 'pp': 'marked'}",
    )
    speculative_decoding: list[str] = Field(
        default_factory=list,
        description="Methods with model-specific handling in code or docs (e.g. 'mtp', 'dspark')",
    )
    reasoning_parser: str = Field(
        default=UNKNOWN, description="Only when the engine's docs map this model to a parser"
    )
    tool_call_parser: str = Field(
        default=UNKNOWN, description="Only when the engine's docs map this model to a parser"
    )
    since_version: str = Field(
        default=UNKNOWN, description="Only when release notes or history state it"
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
    integrations: list[Integration] = Field(default_factory=list)
    model_support: list[ModelSupport] = Field(default_factory=list)
    technique_support: list[TechniqueSupport] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _roles_and_evidence(self) -> "EngineRecord":
        roles = set(self.metadata.roles)
        unimplemented = roles - IMPLEMENTED_ROLES
        if unimplemented:
            raise ValueError(
                f"roles {sorted(unimplemented)} have no subobject in engine schema v1 "
                "(training / rl subobjects land with the first snapshot that needs them)"
            )
        if ("inference" in roles) != (self.serving is not None):
            raise ValueError("`serving` must be present exactly when roles include 'inference'")
        if self.serving is not None:
            missing = [
                f for f in self.serving.populated_fields() if not self.serving.evidence.get(f)
            ]
            if missing:
                raise ValueError(f"serving fields without evidence: {missing}")
            stray = sorted(set(self.serving.evidence) - set(self.serving.populated_fields()))
            if stray:
                raise ValueError(f"serving.evidence keys for unpopulated fields: {stray}")
        for name in type(self.parallelism).model_fields:
            entry: ParallelismEntry = getattr(self.parallelism, name)
            if entry.supported != UNKNOWN and not entry.evidence:
                raise ValueError(f"parallelism.{name}: a known `supported` value needs evidence")
        return self
