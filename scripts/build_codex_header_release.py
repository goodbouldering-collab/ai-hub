"""Replace only the Codex introduction in the verified production snapshot."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from update_codex_update_log import render_header

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "deployment/codex-header/baseline.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): digest(path)
            for path in sorted(root.rglob("*")) if path.is_file()}


def build(output: Path) -> dict:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    baseline = ROOT / contract["release_directory"]
    manifest_path = baseline / "verification.json"
    assert digest(manifest_path) == contract["verification_sha256"], "Unverified release manifest"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_sha"] == contract["source_sha"]
    assert manifest["source_inputs_clean"] is True
    assert hashes(baseline / "public") == manifest["assets"], "Baseline assets changed"
    assert hashes(baseline / "runtime") == manifest["runtime"], "Baseline runtime changed"
    output = output.resolve()
    assert output.is_relative_to(ROOT) and not output.exists(), "Use a fresh project-local destination"
    assert not output.is_relative_to(baseline), "Output cannot be inside the baseline"

    name = contract["changed_asset"]
    original = (baseline / "public" / name).read_text(encoding="utf-8")
    dates = re.findall(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"', original)
    assert len(dates) == 1, "Expected one existing article update date"
    opening = '<section class="codex-update-guide" aria-labelledby="codex-update-guide-title">'
    assert original.count(opening) == 1, "Expected one Codex introduction"
    start = original.index(opening)
    end = original.index('<section class="codex-feature-card ', start)
    old_header = original[start:end]
    assert "公式情報の確認期間" in old_header and "今回の要点" in old_header
    updated = original[:start] + render_header(date.fromisoformat(dates[0])) + "\n\n" + original[end:]
    assert "今日のCodex新機能と活用術" not in updated
    assert "公式情報の確認期間" not in updated and "今回の要点" not in updated

    shutil.copytree(baseline / "public", output / "public")
    shutil.copytree(baseline / "runtime", output / "runtime")
    (output / "public" / name).write_text(updated, encoding="utf-8", newline="\n")
    assets, runtime = hashes(output / "public"), hashes(output / "runtime")
    changed = [key for key in assets if assets[key] != manifest["assets"].get(key)]
    assert assets.keys() == manifest["assets"].keys() and changed == [name]
    assert runtime == manifest["runtime"], "Runtime must remain byte-identical"

    source_paths = [CONTRACT, Path(__file__).resolve(), ROOT / "scripts/update_codex_update_log.py",
                    ROOT / "content/blog/codex-update-log.md"]
    source_inputs = {path.relative_to(ROOT).as_posix(): digest(path) for path in source_paths}
    dirty = subprocess.check_output(
        ["git", "-c", "core.excludesFile=", "status", "--porcelain", "--", *source_inputs],
        cwd=ROOT, text=True).splitlines()
    result = {
        "source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_inputs": source_inputs, "source_inputs_clean": not dirty,
        "source_input_status": dirty, "baseline_source_sha": contract["source_sha"],
        "baseline_version": contract["cloudflare_version"],
        "assets": assets, "runtime": runtime, "changed_assets": changed,
        "preserved_update_date": dates[0], "deployed": False,
    }
    (output / "verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "source_sha", "source_inputs_clean", "changed_assets", "preserved_update_date")}, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    build(parser.parse_args().output)
