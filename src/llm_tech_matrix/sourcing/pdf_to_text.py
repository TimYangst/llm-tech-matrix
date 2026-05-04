"""Derive plain-text artifacts from cached PDF assets.

Reads each PDF asset (kind: arxiv_pdf or tech_report) listed in a manifest, runs
pypdf text extraction, and writes a sibling .txt file. The .txt is a derived artifact
(gitignored, regenerable from the PDF), but is much cheaper for downstream LLM-driven
extraction than re-rendering pages.

CLI:
    uv run python -m llm_tech_matrix.sourcing.pdf_to_text <slug> [--force]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader

from llm_tech_matrix.sourcing.fetch import DATA_SOURCES_DIR, load_manifest

PDF_KINDS = {"arxiv_pdf", "tech_report"}


def pdf_to_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        parts.append(f"\n\n===== Page {i} =====\n\n")
        parts.append(page.extract_text() or "")
    return "".join(parts)


def derive_for_slug(slug: str, *, force: bool = False) -> int:
    manifest = load_manifest(slug)
    src_dir = DATA_SOURCES_DIR / slug
    derived = 0
    for asset in manifest.assets:
        if asset.kind not in PDF_KINDS:
            continue
        pdf_path = src_dir / asset.filename
        if not pdf_path.exists():
            print(
                f"  SKIP   {asset.filename}  (PDF not cached — run `fetch {slug}` first)",
                file=sys.stderr,
            )
            continue
        txt_path = pdf_path.with_suffix(".txt")
        if txt_path.exists() and not force:
            print(f"  exists  {txt_path.name}  (use --force to regenerate)")
            continue
        print(f"  derive  {pdf_path.name}  →  {txt_path.name}")
        text = pdf_to_text(pdf_path)
        txt_path.write_text(text)
        derived += 1
    print(f"Done. Derived {derived} text file(s).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m llm_tech_matrix.sourcing.pdf_to_text",
        description="Derive .txt artifacts from cached PDF assets in a model's manifest.",
    )
    parser.add_argument("slug")
    parser.add_argument(
        "--force", action="store_true", help="Regenerate even if .txt already exists"
    )
    args = parser.parse_args(argv)
    return derive_for_slug(args.slug, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
