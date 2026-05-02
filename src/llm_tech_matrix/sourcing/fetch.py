"""Fetch CLI for source assets.

Reads data/sources/<slug>/manifest.json, downloads the listed assets into the same
directory, verifies sha256 checksums, and updates the manifest. All cached files are
gitignored; only the manifest is committed.

CLI:
    uv run python -m llm_tech_matrix.sourcing fetch <slug> [--force]
    uv run python -m llm_tech_matrix.sourcing add <slug> --name N --kind K --url U \\
        [--filename F] [--description D] [--archive-url A]
    uv run python -m llm_tech_matrix.sourcing verify <slug>
    uv run python -m llm_tech_matrix.sourcing list
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, get_args

import httpx
from dotenv import load_dotenv

from llm_tech_matrix.sourcing.manifest import Asset, AssetKind, SourceManifest

DATA_SOURCES_DIR = Path("data/sources")
LARGE_FILE_WARN_BYTES = 50 * 1024 * 1024  # 50 MiB
CHUNK_BYTES = 1 << 20  # 1 MiB


# ---------- IO helpers ----------


def manifest_path(slug: str) -> Path:
    return DATA_SOURCES_DIR / slug / "manifest.json"


def load_manifest(slug: str) -> SourceManifest:
    path = manifest_path(slug)
    if not path.exists():
        raise FileNotFoundError(f"No manifest at {path}. Use `add` to create one.")
    return SourceManifest.model_validate_json(path.read_text())


def save_manifest(manifest: SourceManifest) -> None:
    path = manifest_path(manifest.slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2) + "\n")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_BYTES), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- core fetch ----------


def _auth_headers(url: str) -> dict[str, str]:
    """Attach HF_TOKEN when fetching from huggingface.co (handles gated configs)."""
    if "huggingface.co" in url:
        token = os.environ.get("HF_TOKEN")
        if token:
            return {"Authorization": f"Bearer {token}"}
    return {}


def _download(url: str, dest: Path) -> None:
    headers = _auth_headers(url)
    with httpx.stream("GET", url, follow_redirects=True, timeout=60.0, headers=headers) as resp:
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in resp.iter_bytes(CHUNK_BYTES):
                f.write(chunk)


def fetch_asset(asset: Asset, dest_dir: Path, *, force: bool = False) -> Asset:
    """Download asset (if needed), verify sha256, return updated asset.

    - If the local file exists and its sha matches `asset.sha256`, skip download.
    - If `asset.sha256` is None (first fetch), download and record the sha.
    - If a recorded sha mismatches after download, raise — upstream may have changed.
    """
    dest = dest_dir / asset.filename
    if dest.exists() and not force and asset.sha256:
        if sha256_of(dest) == asset.sha256:
            print(f"  cached     {asset.filename}")
            return asset
        print(f"  re-fetch   {asset.filename}  (local sha256 differs from manifest)")
    else:
        verb = "re-fetch  " if dest.exists() else "fetch     "
        print(f"  {verb} {asset.filename}  ←  {asset.url}")

    _download(asset.url, dest)
    new_sha = sha256_of(dest)
    new_size = dest.stat().st_size

    if asset.sha256 and new_sha != asset.sha256:
        raise RuntimeError(
            f"sha256 mismatch for {asset.filename} after download:\n"
            f"  manifest: {asset.sha256}\n"
            f"  fetched:  {new_sha}\n"
            f"Upstream may have changed. Investigate before updating the manifest."
        )

    if new_size > LARGE_FILE_WARN_BYTES:
        print(
            f"  WARN: {asset.filename} is {new_size / 1024 / 1024:.1f} MiB. "
            f"Consider whether it should be a source asset.",
            file=sys.stderr,
        )

    return asset.model_copy(
        update={"sha256": new_sha, "size_bytes": new_size, "fetched_at": date.today()}
    )


# ---------- subcommands ----------


def cmd_fetch(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.slug)
    dest_dir = DATA_SOURCES_DIR / args.slug
    print(f"Fetching {len(manifest.assets)} asset(s) for '{args.slug}' into {dest_dir}")
    new_assets = [fetch_asset(a, dest_dir, force=args.force) for a in manifest.assets]
    save_manifest(manifest.model_copy(update={"assets": new_assets}))
    print(f"Done. Manifest updated: {manifest_path(args.slug)}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    if manifest_path(args.slug).exists():
        manifest = load_manifest(args.slug)
        if any(a.name == args.name for a in manifest.assets):
            print(
                f"Asset name '{args.name}' already in manifest for '{args.slug}'. "
                f"Edit the manifest by hand to update or rename.",
                file=sys.stderr,
            )
            return 1
    else:
        manifest = SourceManifest(slug=args.slug, assets=[])

    asset = Asset(
        name=args.name,
        kind=args.kind,
        url=args.url,
        archive_url=args.archive_url,
        filename=args.filename or args.name,
        description=args.description or args.name,
    )
    dest_dir = DATA_SOURCES_DIR / args.slug
    print(f"Adding '{args.name}' to {args.slug} manifest")
    asset = fetch_asset(asset, dest_dir)
    save_manifest(manifest.model_copy(update={"assets": [*manifest.assets, asset]}))
    print(f"Done. Manifest: {manifest_path(args.slug)}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.slug)
    dest_dir = DATA_SOURCES_DIR / args.slug
    failures = 0
    for asset in manifest.assets:
        path = dest_dir / asset.filename
        if not path.exists():
            print(f"  MISSING    {asset.filename}")
            failures += 1
            continue
        if not asset.sha256:
            print(f"  NO SHA     {asset.filename}  (manifest has no recorded sha256)")
            continue
        actual = sha256_of(path)
        if actual == asset.sha256:
            print(f"  ok         {asset.filename}")
        else:
            print(f"  MISMATCH   {asset.filename}  (expected {asset.sha256[:12]}…, got {actual[:12]}…)")
            failures += 1
    if failures:
        print(f"\n{failures} verification failure(s). Run `fetch {args.slug}` to repair.", file=sys.stderr)
    return 1 if failures else 0


def cmd_list(_args: argparse.Namespace) -> int:
    if not DATA_SOURCES_DIR.exists():
        print("No data/sources/ directory yet.")
        return 0
    slugs = sorted(p.parent.name for p in DATA_SOURCES_DIR.glob("*/manifest.json"))
    if not slugs:
        print("No manifests found.")
        return 0
    for slug in slugs:
        manifest = load_manifest(slug)
        print(f"  {slug}  ({len(manifest.assets)} asset(s))")
    return 0


# ---------- entry point ----------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m llm_tech_matrix.sourcing",
        description="Fetch and verify public source assets backing model extractions.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="Download all assets in a model's manifest")
    p_fetch.add_argument("slug")
    p_fetch.add_argument("--force", action="store_true", help="Re-download even if cached and sha matches")
    p_fetch.set_defaults(func=cmd_fetch)

    p_add = sub.add_parser("add", help="Append a new asset URL to a model's manifest, downloading it")
    p_add.add_argument("slug")
    p_add.add_argument("--name", required=True, help="Logical asset name (e.g. 'config', 'paper')")
    p_add.add_argument("--kind", required=True, choices=list(get_args(AssetKind)))
    p_add.add_argument("--url", required=True)
    p_add.add_argument("--filename", help="Local filename (defaults to --name)")
    p_add.add_argument("--description", help="Human-readable description")
    p_add.add_argument("--archive-url", dest="archive_url", help="web.archive.org snapshot URL")
    p_add.set_defaults(func=cmd_add)

    p_verify = sub.add_parser("verify", help="Verify cached files match recorded sha256")
    p_verify.add_argument("slug")
    p_verify.set_defaults(func=cmd_verify)

    p_list = sub.add_parser("list", help="List all model slugs that have a manifest")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    load_dotenv()
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
