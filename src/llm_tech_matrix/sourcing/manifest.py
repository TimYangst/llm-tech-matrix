"""Source manifest schema.

A manifest is the *committed* record of which public assets back a model's extraction —
URLs, sha256 checksums, and metadata. Cached files (the actual bytes) live alongside the
manifest under data/sources/<slug>/ but are gitignored. This makes a fresh clone able to
reproduce the source set without bloating the repo.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AssetKind = Literal[
    "hf_config",     # config.json from HuggingFace
    "arxiv_pdf",     # PDF from arxiv.org
    "tech_report",   # PDF hosted by the lab/vendor (non-arxiv)
    "blog_html",     # blog post / release notes (HTML)
    "model_card",    # HuggingFace model card or vendor model card
    "other",         # everything else; describe in `description`
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Asset(_Strict):
    name: str = Field(description="Logical name for cross-referencing, e.g. 'config', 'paper'")
    kind: AssetKind
    url: str = Field(description="Public URL — must be openly accessible (no paywall, no login)")
    archive_url: str | None = Field(
        default=None, description="Optional web.archive.org snapshot for URL-rot protection"
    )
    filename: str = Field(description="Local filename relative to data/sources/<slug>/")
    description: str
    sha256: str | None = Field(default=None, description="Populated after first successful fetch")
    size_bytes: int | None = Field(default=None, description="Populated after first successful fetch")
    fetched_at: date | None = Field(default=None, description="Date of last successful fetch")


class SourceManifest(_Strict):
    """One per model. Lives at data/sources/<slug>/manifest.json."""

    slug: str
    assets: list[Asset]
