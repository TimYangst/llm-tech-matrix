"""Public-source-only hardware snapshots, independent of model and engine schemas."""

from __future__ import annotations

import ipaddress
from datetime import date
from typing import Annotated, Literal
from urllib.parse import urldefrag, urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

HARDWARE_SCHEMA_VERSION = 1
UNKNOWN = "[Unknown/Not Disclosed]"
Unknown = Literal["[Unknown/Not Disclosed]"]
PositiveNumber = Annotated[float, Field(gt=0, allow_inf_nan=False)]
PositiveCount = Annotated[int, Field(gt=0)]
Scope = Literal["per_accelerator", "system"]


def validate_public_url(url: str) -> str:
    """Reject local, authenticated and obviously private references without network access.

    URL syntax cannot establish publication: extraction and independent review must also
    confirm that the cited content is publicly accessible and contains the claimed fact.
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or not host or parsed.username or parsed.password:
        raise ValueError(f"Expected an unauthenticated public HTTP(S) URL: {url!r}")
    if "." not in host or host.endswith((".local", ".internal", ".localhost", ".ts.net")):
        raise ValueError(f"Private/local source URL is forbidden: {url!r}")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is None and all(part.isdigit() for part in host.split(".")):
        raise ValueError(f"Ambiguous numeric source host is forbidden: {url!r}")
    if address is not None and not address.is_global:
        raise ValueError(f"Private/local source URL is forbidden: {url!r}")
    if parsed.query:
        for key in parsed.query.lower().split("&"):
            if key.split("=", 1)[0] in {
                "token",
                "access_token",
                "auth",
                "authorization",
                "signature",
                "x-amz-signature",
            }:
                raise ValueError("Credential-bearing/signed source URLs are forbidden")
    return url


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("*")
    @classmethod
    def _nonblank(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Use {UNKNOWN!r} for undisclosed scalar fields")
        if isinstance(value, list) and any(isinstance(v, str) and not v.strip() for v in value):
            raise ValueError("List entries cannot be blank")
        return value


class _Evidenced(_Strict):
    evidence: dict[str, list[str]] = Field(default_factory=dict)

    def evidence_errors(self, section: str) -> list[str]:
        populated = {
            name
            for name in type(self).model_fields
            if name not in {"evidence", "sources", "peaks"}
            and getattr(self, name) not in (UNKNOWN, [], {})
        }
        errors = [
            f"{section}.{name}: no evidence"
            for name in sorted(populated)
            if not self.evidence.get(name)
        ]
        errors += [
            f"{section}.evidence[{name!r}]: unknown, empty, or nonexistent field"
            for name in sorted(set(self.evidence) - populated)
        ]
        return errors


class HardwareMetadata(_Evidenced):
    name: str
    vendor: str
    accelerator_type: Literal["GPU", "TPU", "ASIC", "WSE"]
    variant: str
    form_factor: str = UNKNOWN
    record_scope: Scope
    device_count: PositiveCount | Unknown
    snapshot_date: str
    sources: list[str] = Field(min_length=1)

    @field_validator("snapshot_date")
    @classmethod
    def _date(cls, value: str) -> str:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError("snapshot_date must be YYYY-MM-DD")
        return value


class Architecture(_Evidenced):
    family: str = UNKNOWN
    process: str = UNKNOWN
    compute_units: str = UNKNOWN
    cache: str = UNKNOWN
    on_chip_memory: str = UNKNOWN
    execution_model: str = UNKNOWN
    notes: list[str] = Field(default_factory=list)


class Memory(_Evidenced):
    technology: str = UNKNOWN
    capacity_gb: PositiveNumber | Unknown = UNKNOWN
    capacity_gib: PositiveNumber | Unknown = UNKNOWN
    bandwidth_tb_s: PositiveNumber | Unknown = UNKNOWN
    scope: Scope
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _one_capacity_unit(self) -> Memory:
        if self.capacity_gb != UNKNOWN and self.capacity_gib != UNKNOWN:
            raise ValueError(
                "Publish one original capacity unit; retain alternate figures in notes"
            )
        return self


class ComputePeak(_Strict):
    """Vendor-published theoretical rate; precision, operation and scope stay inseparable."""

    precision: str
    operation: Literal["matrix", "vector", "undisclosed"]
    throughput: PositiveNumber
    unit: Literal["TFLOP/s", "TOPS"]
    sparsity: Literal["dense", "structured_sparse", "sparse_unspecified", "undisclosed"]
    scope: Scope
    accumulation: str = UNKNOWN
    conditions: str = UNKNOWN
    fma_counting: str = UNKNOWN
    evidence: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _unit(self) -> ComputePeak:
        if self.precision.upper().startswith(("INT", "UINT")) and self.unit != "TOPS":
            raise ValueError("Integer peaks use TOPS, not TFLOP/s")
        if self.precision.upper().startswith(("FP", "BF", "TF")) and self.unit != "TFLOP/s":
            raise ValueError("Floating-point peaks use TFLOP/s, not TOPS")
        return self


class Compute(_Evidenced):
    peaks: list[ComputePeak] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class Interconnect(_Evidenced):
    host: str = UNKNOWN
    scale_up: str = UNKNOWN
    scale_out: str = UNKNOWN
    topology: str = UNKNOWN


class Power(_Evidenced):
    tdp_w: PositiveNumber | Unknown = UNKNOWN
    scope: Scope
    notes: list[str] = Field(default_factory=list)


class Software(_Evidenced):
    ecosystem: str = UNKNOWN
    isa: str = UNKNOWN
    programming_model: str = UNKNOWN


class PublicMeasurement(_Strict):
    """Optional externally published benchmark; no local receipts or internal results."""

    benchmark: str
    metric: str
    value: PositiveNumber
    unit: str
    scope: Scope
    configuration: str
    conditions: str
    evidence: list[str] = Field(min_length=1)


class HardwareRecord(_Strict):
    hardware_schema_version: Literal[1]
    metadata: HardwareMetadata
    architecture: Architecture
    memory: Memory
    compute: Compute
    interconnect: Interconnect
    power: Power
    software: Software
    public_measurements: list[PublicMeasurement] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _provenance(self) -> HardwareRecord:
        sources = {urldefrag(validate_public_url(url))[0] for url in self.metadata.sources}
        errors = []
        if len(sources) != len(self.metadata.sources):
            errors.append("metadata.sources: duplicate URLs")
        for name in (
            "metadata",
            "architecture",
            "memory",
            "compute",
            "interconnect",
            "power",
            "software",
        ):
            section = getattr(self, name)
            errors += section.evidence_errors(name)
            for field, urls in section.evidence.items():
                for url in urls:
                    validate_public_url(url)
                    if urldefrag(url)[0] not in sources:
                        errors.append(
                            f"{name}.{field}: evidence is not in metadata.sources: {url!r}"
                        )
        for kind, rows in (
            ("compute.peaks", self.compute.peaks),
            ("public_measurements", self.public_measurements),
        ):
            for i, row in enumerate(rows):
                for url in row.evidence:
                    validate_public_url(url)
                    if urldefrag(url)[0] not in sources:
                        errors.append(f"{kind}[{i}]: evidence is not in metadata.sources: {url!r}")
        if self.metadata.record_scope == "per_accelerator" and self.metadata.device_count != 1:
            errors.append("per_accelerator records require device_count=1")
        scopes = [self.memory.scope, self.power.scope] + [p.scope for p in self.compute.peaks]
        if any(scope != self.metadata.record_scope for scope in scopes):
            errors.append(
                "memory/power/peak scopes must match metadata.record_scope; use separate system records"
            )
        if errors:
            raise ValueError("; ".join(errors))
        return self
