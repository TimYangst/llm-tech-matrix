r"""Fetch CLI for source assets.

Reads data/sources/<slug>/manifest.json, downloads the listed assets into the same
directory, verifies sha256 checksums, and updates the manifest. All cached files are
gitignored; only the manifest is committed.

`fetch` does not stop at the first failing asset: it caches everything it can, saves the
manifest for the assets that succeeded, and ends with a failure report (one block per asset:
what failed, expected vs fetched sha256, where the fetched copy was kept, and what to do next)
meant to be handed to a person or an agent as-is. A mismatching download never replaces the
cached file; it is kept beside it as `<filename>.fetched`.

`release_notes` assets (GitHub releases API JSON) are normalized before hashing: only the
release `body` is stored, so mutable counters in the API response (download counts,
reactions) cannot break reproducibility while a real edit to the notes still does.

`--track engines` switches the root to data/sources/engines/ (engine snapshots, see
docs/engines/overview.md). The default track is `models`.

CLI:
    uv run python -m llm_tech_matrix.sourcing [--track T] fetch <slug> [--force]
    uv run python -m llm_tech_matrix.sourcing [--track T] add <slug> --name N --kind K --url U \\
        [--filename F] [--description D] [--archive-url A]
    uv run python -m llm_tech_matrix.sourcing [--track T] verify <slug>
    uv run python -m llm_tech_matrix.sourcing [--track T] list
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import get_args

import httpx
from dotenv import load_dotenv

from llm_tech_matrix.sourcing.manifest import Asset, AssetKind, SourceManifest

DATA_SOURCES_DIR = Path("data/sources")
TRACK_ROOTS = {"models": DATA_SOURCES_DIR, "engines": DATA_SOURCES_DIR / "engines"}
LARGE_FILE_WARN_BYTES = 50 * 1024 * 1024  # 50 MiB
CHUNK_BYTES = 1 << 20  # 1 MiB


# ---------- IO helpers ----------


def manifest_path(slug: str, root: Path = DATA_SOURCES_DIR) -> Path:
    return root / slug / "manifest.json"


def load_manifest(slug: str, root: Path = DATA_SOURCES_DIR) -> SourceManifest:
    path = manifest_path(slug, root)
    if not path.exists():
        raise FileNotFoundError(f"No manifest at {path}. Use `add` to create one.")
    return SourceManifest.model_validate_json(path.read_text())


def save_manifest(manifest: SourceManifest, root: Path = DATA_SOURCES_DIR) -> None:
    path = manifest_path(manifest.slug, root)
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


class SourceMismatchError(RuntimeError):
    """A download's sha256 differs from the manifest; the fetched copy is kept for diffing."""

    def __init__(self, asset: Asset, fetched_sha: str, fetched_copy: Path):
        self.asset = asset
        self.fetched_sha = fetched_sha
        self.fetched_copy = fetched_copy
        super().__init__(
            f"sha256 mismatch for {asset.filename}: manifest {asset.sha256}, fetched {fetched_sha}"
        )


def _normalize(asset: Asset, path: Path) -> None:
    """Reduce an asset to its reproducible content before hashing, in place."""
    if asset.kind == "release_notes":
        payload = json.loads(path.read_text(encoding="utf-8"))
        body = payload.get("body") if isinstance(payload, dict) else None
        if not isinstance(body, str):
            raise ValueError(
                f"{asset.filename}: expected GitHub releases API JSON with a string `body`"
            )
        path.write_text(body.rstrip("\n") + "\n", encoding="utf-8")


def fetch_asset(asset: Asset, dest_dir: Path, *, force: bool = False) -> Asset:
    """Download asset (if needed), verify sha256, return updated asset.

    - If the local file exists and its sha matches `asset.sha256`, skip download.
    - If `asset.sha256` is None (first fetch), download and record the sha.
    - If a recorded sha mismatches after download, raise `SourceMismatchError` — upstream may have
      changed. The cached file is left untouched and the new bytes are kept as
      `<filename>.fetched`.
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

    tmp = dest.with_name(dest.name + ".download")
    try:
        _download(asset.url, tmp)
        _normalize(asset, tmp)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    new_sha = sha256_of(tmp)
    new_size = tmp.stat().st_size

    if asset.sha256 and new_sha != asset.sha256:
        fetched_copy = dest.with_name(dest.name + ".fetched")
        tmp.replace(fetched_copy)
        raise SourceMismatchError(asset, new_sha, fetched_copy)
    tmp.replace(dest)

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


def _failure_report(
    args: argparse.Namespace, total: int, failures: list[tuple[Asset, Exception]]
) -> str:
    """Plain, self-contained failure blocks a person or an agent can act on directly."""
    dest_dir = TRACK_ROOTS[args.track] / args.slug
    lines = [
        f"FETCH REPORT: {len(failures)} of {total} asset(s) failed for '{args.slug}' "
        f"(track: {args.track}).",
        "Assets that succeeded were cached and recorded in the manifest; failed entries are unchanged.",
        "Do not edit a recorded sha256 just to make it pass — find out what changed first "
        "(docs/conventions.md, 'Source assets').",
        "",
    ]
    for asset, err in failures:
        lines += [
            f"- asset: {asset.name}",
            f"  kind: {asset.kind}",
            f"  filename: {asset.filename}",
            f"  url: {asset.url}",
        ]
        if isinstance(err, SourceMismatchError):
            cached = dest_dir / asset.filename
            lines += [
                "  error: sha256 mismatch (upstream content differs from the recorded source)",
                f"  expected_sha256: {asset.sha256}",
                f"  fetched_sha256: {err.fetched_sha}",
                f"  fetched_copy: {err.fetched_copy}",
                f"  cached_copy: {cached if cached.exists() else '(none)'}",
                "  next: diff the fetched copy against the cached copy (or the source at a pinned "
                "revision). If only volatile markup changed, pin the URL to the exact revision the "
                "extraction used; if the content really changed, re-register the asset and "
                "re-check every extracted value that cites it.",
            ]
        else:
            lines += [
                f"  error: {type(err).__name__}: {' '.join(str(err).split())}",
                "  next: check whether the URL still resolves (moved, deleted, rate-limited, "
                "login-gated); prefer a URL pinned to a commit or an archive_url snapshot.",
            ]
    return "\n".join(lines)


def cmd_fetch(args: argparse.Namespace) -> int:
    root = TRACK_ROOTS[args.track]
    manifest = load_manifest(args.slug, root)
    dest_dir = root / args.slug
    print(f"Fetching {len(manifest.assets)} asset(s) for '{args.slug}' into {dest_dir}")
    new_assets: list[Asset] = []
    failures: list[tuple[Asset, Exception]] = []
    for asset in manifest.assets:
        try:
            new_assets.append(fetch_asset(asset, dest_dir, force=args.force))
        except (SourceMismatchError, httpx.HTTPError, OSError, ValueError) as err:
            print(f"  FAILED     {asset.filename}  ({type(err).__name__})")
            new_assets.append(asset)
            failures.append((asset, err))
    save_manifest(manifest.model_copy(update={"assets": new_assets}), root)
    print(f"Manifest saved: {manifest_path(args.slug, root)}")
    if failures:
        print("\n" + _failure_report(args, len(manifest.assets), failures), file=sys.stderr)
        return 1
    print("Done.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    root = TRACK_ROOTS[args.track]
    if manifest_path(args.slug, root).exists():
        manifest = load_manifest(args.slug, root)
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
    dest_dir = root / args.slug
    print(f"Adding '{args.name}' to {args.slug} manifest")
    try:
        asset = fetch_asset(asset, dest_dir)
    except (SourceMismatchError, httpx.HTTPError, OSError, ValueError) as err:
        print("\n" + _failure_report(args, 1, [(asset, err)]), file=sys.stderr)
        return 1
    save_manifest(manifest.model_copy(update={"assets": [*manifest.assets, asset]}), root)
    print(f"Done. Manifest: {manifest_path(args.slug, root)}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    root = TRACK_ROOTS[args.track]
    manifest = load_manifest(args.slug, root)
    dest_dir = root / args.slug
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
            print(
                f"  MISMATCH   {asset.filename}  (expected {asset.sha256[:12]}…, got {actual[:12]}…)"
            )
            failures += 1
    if failures:
        print(
            f"\n{failures} verification failure(s). "
            f"Run `--track {args.track} fetch {args.slug}` to repair.",
            file=sys.stderr,
        )
    return 1 if failures else 0


def cmd_list(args: argparse.Namespace) -> int:
    root = TRACK_ROOTS[args.track]
    if not root.exists():
        print(f"No {root}/ directory yet.")
        return 0
    slugs = sorted(p.parent.name for p in root.glob("*/manifest.json"))
    if not slugs:
        print("No manifests found.")
        return 0
    for slug in slugs:
        manifest = load_manifest(slug, root)
        print(f"  {slug}  ({len(manifest.assets)} asset(s))")
    return 0


# ---------- entry point ----------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m llm_tech_matrix.sourcing",
        description="Fetch and verify public source assets backing model and engine extractions.",
    )
    parser.add_argument(
        "--track",
        choices=sorted(TRACK_ROOTS),
        default="models",
        help="Which source tree to use: data/sources/ (models) or data/sources/engines/",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="Download all assets in a model's manifest")
    p_fetch.add_argument("slug")
    p_fetch.add_argument(
        "--force", action="store_true", help="Re-download even if cached and sha matches"
    )
    p_fetch.set_defaults(func=cmd_fetch)

    p_add = sub.add_parser(
        "add", help="Append a new asset URL to a model's manifest, downloading it"
    )
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
