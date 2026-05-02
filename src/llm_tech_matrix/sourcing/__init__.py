"""Layer 1: data sourcing.

Fetches raw inputs (HuggingFace config.json, ArXiv papers, blog HTML) into
data/sources/<model-slug>/, plus a manifest.json recording origin and fetch date.

No interpretation here — sourcing's only job is "get the bytes, record where they
came from." See `manifest.py` for the schema and `fetch.py` for the CLI.
"""

from llm_tech_matrix.sourcing.manifest import Asset, AssetKind, SourceManifest

__all__ = ["Asset", "AssetKind", "SourceManifest"]
