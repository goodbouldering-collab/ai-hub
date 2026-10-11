"""Build a metadata-only release from the exact, verified public asset baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.search_presence import apply_search_presence

CONTRACT = ROOT / "deployment/search-presence/release-baseline.json"
CONFIG = ROOT / "config/search-presence.json"
DISCOVERY_FILES = frozenset({"robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt"})
SOURCE_INPUTS = (
    "scripts/build_search_presence_release.py",
    "core/search_presence.py",
    "config/search-presence.json",
    "deployment/search-presence/release-baseline.json",
)
HEAD = re.compile(r"(<head\b[^>]*>)(.*?)(</head\s*>)", re.I | re.S)
JSON_LD = re.compile(r"<script\b(?=[^>]*\btype\s*=\s*['\"]application/ld\+json['\"])[^>]*>.*?</script\s*>", re.I | re.S)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(folder: Path) -> dict[str, str]:
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(folder.rglob("*")) if p.is_file()}


def _presentation_head(head: str) -> str:
    """Remove only SEO tags; keep the order and text of all presentation tags."""
    head = JSON_LD.sub("", head)
    head = re.sub(r"<title\b[^>]*>.*?</title\s*>", "", head, flags=re.I | re.S)
    head = re.sub(r"<meta\b[^>]*>", "", head, flags=re.I)

    def link(match: re.Match) -> str:
        tag = BeautifulSoup(match.group(0), "html.parser").find("link")
        return "" if tag and "canonical" in tag.get("rel", []) else match.group(0)

    head = re.sub(r"<link\b[^>]*>", link, head, flags=re.I)
    # SEO tag insertions/removals can leave blank lines between existing tags.
    # Inline script/style content is checked byte-for-byte separately below.
    return re.sub(r">\s+<", "><", head).strip()


def assert_metadata_only(before: bytes, after: bytes, name: str) -> None:
    old, new = before.decode("utf-8"), after.decode("utf-8")
    a, b = HEAD.search(old), HEAD.search(new)
    if not a or not b:
        raise ValueError(f"Changed HTML must have a single document head: {name}")
    if len(HEAD.findall(old)) != 1 or len(HEAD.findall(new)) != 1:
        raise ValueError(f"Expected exactly one document head: {name}")
    if old[:a.start()] != new[:b.start()] or a.group(1) != b.group(1) or a.group(3) != b.group(3):
        raise ValueError(f"HTML outside the head metadata changed: {name}")
    if old[a.end():] != new[b.end():]:
        raise ValueError(f"HTML body or trailing content changed: {name}")
    if _presentation_head(a.group(2)) != _presentation_head(b.group(2)):
        raise ValueError(f"Non-metadata head content changed: {name}")
    presentation = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.I | re.S)
    old_assets = [m.group(0) for m in presentation.finditer(JSON_LD.sub("", a.group(2)))]
    new_assets = [m.group(0) for m in presentation.finditer(JSON_LD.sub("", b.group(2)))]
    if old_assets != new_assets:
        raise ValueError(f"Inline JavaScript or CSS changed: {name}")


def build(base_assets: Path, output: Path, source_sha: str,
          base_worker: Path | None = None) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise ValueError("source-sha must be the complete 40-character Git commit SHA")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    base_assets, output = base_assets.resolve(), output.resolve()
    base_worker = (base_worker or base_assets.parent / "runtime/published-worker.mjs").resolve()
    before = hashes(base_assets)
    if before != contract["assets"]:
        raise ValueError("Public baseline differs from the verified live release")
    if not base_worker.is_file() or digest(base_worker) != contract["worker_sha256"]:
        raise ValueError("Worker baseline differs from the verified live release")
    if output.exists():
        raise ValueError("Use a fresh output directory; release evidence is immutable")
    if output == base_assets or base_assets in output.parents:
        raise ValueError("Output must be outside the immutable public baseline")
    inputs = {name: digest(ROOT / name) for name in SOURCE_INPUTS}
    public = output / "public"
    shutil.copytree(base_assets, public)
    runtime = output / "runtime"
    runtime.mkdir()
    worker = runtime / "published-worker.mjs"
    shutil.copyfile(base_worker, worker)
    search = apply_search_presence(public, CONFIG)
    after = hashes(public)
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(name for name in before if after.get(name) != before[name])
    if removed:
        raise ValueError(f"Search release removed assets: {removed}")
    if not set(added) <= DISCOVERY_FILES:
        raise ValueError(f"Unexpected new assets: {added}")
    html_changes = []
    for name in changed:
        if name.endswith(".html"):
            assert_metadata_only((base_assets / name).read_bytes(), (public / name).read_bytes(), name)
            html_changes.append(name)
        elif name not in DISCOVERY_FILES:
            raise ValueError(f"Non-search asset changed: {name}")
    actual_changes = set(changed) | set(added)
    if actual_changes != set(search["changed_files"]):
        raise ValueError("Search postprocessor report differs from actual changed files")
    if digest(worker) != contract["worker_sha256"]:
        raise ValueError("Runtime changed during the search release")
    if inputs != {name: digest(ROOT / name) for name in SOURCE_INPUTS}:
        raise ValueError("Search build source changed while producing the release")
    report = {
        "source_sha": source_sha,
        "baseline_source_sha": contract["source_sha"],
        "baseline_cloudflare_version": contract["cloudflare_version"],
        "assets": after,
        "changed_assets": changed,
        "added_assets": added,
        "removed_assets": removed,
        "unchanged_assets": len(before) - len(changed),
        "metadata_only_documents": html_changes,
        "discovery_assets": sorted(actual_changes & DISCOVERY_FILES),
        "worker_sha256": digest(worker),
        "worker_unchanged": True,
        "source_inputs_sha256": inputs,
        "search_presence": search,
    }
    (output / "verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-assets", required=True, type=Path)
    parser.add_argument("--base-worker", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    result = build(args.base_assets, args.output, args.source_sha, args.base_worker)
    print(json.dumps({k: v for k, v in result.items() if k != "assets"}, ensure_ascii=False, indent=2))
