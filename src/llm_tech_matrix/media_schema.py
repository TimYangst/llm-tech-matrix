"""Independent schema v1 for image, video and audio generation model releases.

Media records do not participate in the causal-LM architecture or engine joins. Every
populated field cites the official source set; prose retains component and variant scope.
"""

from __future__ import annotations

from typing import Literal
from urllib.parse import urldefrag, urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MEDIA_SCHEMA_VERSION = 1
UNKNOWN = "[Unknown/Not Disclosed]"
Modality = Literal["text", "image", "video", "audio"]
Openness = Literal["open_weights", "closed", "mixed", "[Unknown/Not Disclosed]"]


class _Evidenced(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    evidence: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("*")
    @classmethod
    def _no_blank_values(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Use {UNKNOWN!r} for undisclosed scalar fields")
        if isinstance(value, list) and any(isinstance(v, str) and not v.strip() for v in value):
            raise ValueError("List entries must not be blank")
        return value

    def evidence_errors(self, section: str) -> list[str]:
        populated = {
            name
            for name in type(self).model_fields
            if name not in {"evidence", "sources"} and getattr(self, name) not in (UNKNOWN, [], {})
        }
        errors = [
            f"{section}.{name}: no evidence"
            for name in sorted(populated)
            if not self.evidence.get(name)
        ]
        errors += [
            f"{section}.evidence[{name!r}]: field is unknown, empty, or does not exist"
            for name in sorted(set(self.evidence) - populated)
        ]
        return errors


class MediaMetadata(_Evidenced):
    name: str
    family: str
    organization: str
    release_date: str
    openness: Openness
    license: str
    sources: list[str] = Field(min_length=1)
    variant_policy: str = Field(
        description="Which checkpoints share this record and which hosted components are excluded"
    )


class Generation(_Evidenced):
    input_modalities: list[Modality] = Field(min_length=1)
    output_modalities: list[Modality] = Field(min_length=1)
    tasks: list[str] = Field(default_factory=list)
    objective: str = UNKNOWN
    scheduler: str = UNKNOWN
    sampling: str = UNKNOWN


class Architecture(_Evidenced):
    backbone: str = UNKNOWN
    parameters: str = UNKNOWN
    attention: str = UNKNOWN
    conditioning: str = UNKNOWN
    vae: str = UNKNOWN
    audio_codec: str = UNKNOWN
    multimodal_coupling: str = UNKNOWN
    implementation: str = UNKNOWN


class Output(_Evidenced):
    resolution: str = UNKNOWN
    frame_rate: str = UNKNOWN
    duration: str = UNKNOWN
    sample_rate: str = UNKNOWN
    channels: str = UNKNOWN
    formats: list[str] = Field(default_factory=list)


class Training(_Evidenced):
    data: str = UNKNOWN
    pretraining: str = UNKNOWN
    post_training: str = UNKNOWN


class Precision(_Evidenced):
    weights: str = UNKNOWN
    compute: str = UNKNOWN
    quantization: str = UNKNOWN


class Release(_Evidenced):
    artifacts: list[str] = Field(default_factory=list)
    hosted_scope: str = UNKNOWN
    limitations: list[str] = Field(default_factory=list)


class MediaRecord(BaseModel):
    """One release family, with all factual claims tied to its registered sources."""

    model_config = ConfigDict(extra="forbid", strict=True)

    media_schema_version: Literal[1]
    metadata: MediaMetadata
    generation: Generation
    architecture: Architecture
    output: Output
    training: Training
    precision: Precision
    release: Release
    open_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _evidence(self) -> MediaRecord:
        errors: list[str] = []
        sources = {urldefrag(url)[0] for url in self.metadata.sources}
        for url in self.metadata.sources:
            parsed = urlparse(url)
            if parsed.scheme not in {"https", "http"} or not parsed.netloc:
                errors.append(f"metadata.sources: invalid public URL {url!r}")
        if len(sources) != len(self.metadata.sources):
            errors.append("metadata.sources: duplicate source URLs")
        for name in (
            "metadata",
            "generation",
            "architecture",
            "output",
            "training",
            "precision",
            "release",
        ):
            section: _Evidenced = getattr(self, name)
            errors += section.evidence_errors(name)
            for field, urls in section.evidence.items():
                for url in urls:
                    if urldefrag(url)[0] not in sources:
                        errors.append(f"{name}.{field}: evidence not in metadata.sources: {url!r}")
        if errors:
            raise ValueError("; ".join(errors))
        return self
