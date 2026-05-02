"""Layer 1: data sourcing.

Fetches raw inputs (HuggingFace config.json, ArXiv papers, blog HTML) into
data/sources/<model-slug>/, plus a manifest.json recording origin and fetch date.

No interpretation here — sourcing's only job is "get the bytes, record where they
came from." Implementation pending.
"""
