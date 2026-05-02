"""LLM Tech Evolution Matrix.

Schema-driven extraction and synthesis pipeline for analyzing mainstream AI models.
See docs/ for architecture and conventions.
"""

from llm_tech_matrix.schema import SCHEMA_VERSION, UNKNOWN, ExtractedModel

__all__ = ["SCHEMA_VERSION", "UNKNOWN", "ExtractedModel"]
