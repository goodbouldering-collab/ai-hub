"""Build a fresh editorial release from the exact verified deployed snapshot."""
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
from core.studio_design import decorate_public_tree, decorate_runtime
from verify_editorial_release import MANIFEST, hashes, require, validate_baseline, verify


def build(baseline: Path, output: Path) -> dict:
    baseline, output = baseline.resolve(), output.resolve()
    manifest = validate_baseline(baseline)
    require(not output.exists(), "Use a fresh release destination; existing files are never overwritten")
    require(not output.is_relative_to(baseline), "Output cannot be inside the verified baseline")
    source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    shutil.copytree(baseline / "public", output / "public")
    shutil.copytree(baseline / "runtime", output / "runtime")
    decorate_public_tree(output / "public")
    decorate_runtime(output / "runtime")
    checks = verify(baseline, output)
    inputs = [ROOT / "core/studio_design.py", ROOT / "core/soft_studio.py", Path(__file__).resolve(),
              ROOT / "scripts/verify_editorial_release.py", ROOT / "scripts/verify_editorial_live.py", MANIFEST]
    inputs.extend(path for path in (ROOT / "site/static/design-system/studio").rglob("*")
                  if path.is_file() and path.name != "README.md")
    source_inputs = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in sorted(inputs)}
    dirty_inputs = subprocess.check_output(
        ["git", "-c", "core.excludesfile=", "status", "--porcelain", "--", *source_inputs],
        cwd=ROOT, text=True).splitlines()
    result = {"source_sha": source_sha, "source_inputs": source_inputs,
              "source_inputs_clean": not dirty_inputs, "source_input_status": dirty_inputs,
              "baseline_source_sha": manifest["source_sha"], "baseline_version": manifest["version"],
              "assets": hashes(output / "public"), "runtime": hashes(output / "runtime"),
              "verification": checks, "deployed": False}
    (output / "verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha": source_sha, "source_inputs_clean": not dirty_inputs,
                      "assets": len(result["assets"]), "runtime": len(result["runtime"]),
                      "verification": {key: value for key, value in checks.items()
                                       if key != "changed_assets"},
                      "changed_assets": len(checks["changed_assets"])}, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline, args.output)
