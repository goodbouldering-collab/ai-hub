"""Add the homepage carousel to the exact verified production snapshot."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.instagram_feed import apply_instagram_feed, HEAD, START, END
CONTRACT = ROOT / "deployment/instagram/baseline.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


def build(output: Path) -> dict:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    baseline = ROOT / contract["release_directory"]
    manifest_path = baseline / "verification.json"
    assert digest(manifest_path) == contract["verification_sha256"], "Baseline manifest changed"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_sha"] == contract["source_sha"] and manifest["source_inputs_clean"] is True
    assert hashes(baseline / "public") == manifest["assets"], "Baseline public assets changed"
    assert hashes(baseline / "runtime") == manifest["runtime"], "Baseline runtime changed"
    output = output.resolve()
    assert output.is_relative_to(ROOT) and not output.exists(), "Use a fresh project-local output"
    assert not output.is_relative_to(baseline), "Keep the baseline untouched"
    original = (baseline / "public/index.html").read_text(encoding="utf-8")
    updated = apply_instagram_feed(original)
    assert apply_instagram_feed(updated) == updated, "Decoration must be idempotent"
    start, end = updated.index(START), updated.index(END) + len(END)
    assert (updated[:start] + updated[end:]).replace(HEAD, "") == original, "Unrelated homepage markup changed"
    assert updated.index('id="instagram"') < updated.index('id="ai-news"')
    assert updated.count('class="instagram-frame"') == 6
    shutil.copytree(baseline / "public", output / "public")
    shutil.copytree(baseline / "runtime", output / "runtime")
    (output / "public/index.html").write_text(updated, encoding="utf-8", newline="\n")
    additions = {"instagram-feed.css", "instagram-feed.js"}
    for name in additions:
        shutil.copyfile(ROOT / "site/static" / name, output / "public" / name)
    assets, runtime = hashes(output / "public"), hashes(output / "runtime")
    changed = [p for p in assets if p in manifest['assets'] and assets[p] != manifest['assets'][p]]
    assert changed == ["index.html"], "An unrelated page changed"
    assert assets.keys() - manifest['assets'].keys() == additions
    assert manifest['assets'].keys() <= assets.keys()
    assert runtime == manifest["runtime"], "Runtime changed"
    inputs = [CONTRACT, Path(__file__).resolve(), ROOT / "config/instagram.json",
              ROOT / "core/instagram_feed.py", ROOT / "site/build_portal.py",
              ROOT / "cloudflare-runtime/wrangler-profile-release.jsonc",
              ROOT / "deployment/profile/package.json", ROOT / "deployment/profile/package-lock.json",
              *(ROOT / 'site/static' / name for name in sorted(additions))]
    source_inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs}
    dirty = subprocess.check_output(['git', '-c', 'core.excludesFile=', 'status', '--porcelain', '--', *source_inputs], cwd=ROOT, text=True).splitlines()
    result = {
        "source_sha": subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        "source_inputs": source_inputs, "source_inputs_clean": not dirty,
        "source_input_status": dirty, "baseline_source_sha": contract['source_sha'],
        "baseline_version": contract['cloudflare_version'], "assets": assets, "runtime": runtime,
        "changed_assets": changed, "added_assets": sorted(additions),
        "unchanged_assets": len(manifest['assets']) - len(changed), "deployed": False,
    }
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('source_sha', 'source_inputs_clean', 'changed_assets', 'added_assets', 'unchanged_assets')}, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    build(parser.parse_args().output)
