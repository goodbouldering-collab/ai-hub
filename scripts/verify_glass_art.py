"""Verify a glass-art release against the immediately preceding public release."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.studio_design import decorate_html

PRESENTATION_ASSETS = {
    "design-system/studio/studio.css",
    "design-system/studio/studio.js",
}


def semantics(text: str) -> dict:
    soup = BeautifulSoup(text, "html.parser")
    for added in soup.select("#studio-design, #studio-motion, .studio-art-layer"):
        added.decompose()
    scripts = [str(element) for element in soup.find_all("script")]
    images = [dict(element.attrs) for element in soup.select("img, source")]
    for element in soup.select("script, style"):
        element.decompose()
    controls = [
        {"tag": element.name, **dict(element.attrs)}
        for element in soup.select("a,button,input,textarea,select,option,form,details,iframe")
    ]
    return {"text": soup.get_text(" ", strip=True), "controls": controls,
            "scripts": scripts, "images": images}


def files(root: Path) -> dict[str, Path]:
    return {path.relative_to(root).as_posix(): path for path in root.rglob("*") if path.is_file()}


def check_html(before: str, after: str, name: str, **flags) -> None:
    assert semantics(before) == semantics(after), f"Content, controls, images or existing scripts changed: {name}"
    assert decorate_html(before, **flags) == after, f"Changes beyond the presentation decorator: {name}"
    assert decorate_html(after, **flags) == after, f"Non-idempotent decoration: {name}"
    if "<body" in after.lower() and "</head>" in after.lower():
        soup = BeautifulSoup(after, "html.parser")
        assert len(soup.select("#studio-design")) == 1, f"Missing or duplicate CSS: {name}"
        assert len(soup.select("#studio-motion")) == 1, f"Missing or duplicate motion script: {name}"


def runtime_assets(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").split("export default ", 1)[1].strip().removesuffix(";"))


def verify(baseline: Path, release: Path, baseline_runtime: Path, runtime: Path) -> dict:
    before_files, after_files = files(baseline), files(release)
    assert before_files.keys() == after_files.keys(), "Public file set changed"
    html_count = unchanged_assets = 0
    changed_presentation = []
    for name, before in before_files.items():
        after = after_files[name]
        if name.endswith(".html"):
            check_html(before.read_text(encoding="utf-8"), after.read_text(encoding="utf-8"), name,
                       home=name == "index.html", admin=name.startswith("admin/"))
            html_count += 1
        elif name in PRESENTATION_ASSETS:
            if before.read_bytes() != after.read_bytes():
                changed_presentation.append(name)
        else:
            assert before.read_bytes() == after.read_bytes(), f"Non-presentation asset changed: {name}"
            unchanged_assets += 1
    old_runtime, new_runtime = files(baseline_runtime), files(runtime)
    assert old_runtime.keys() == new_runtime.keys(), "Runtime file set changed"
    admin_count = unchanged_runtime = 0
    for name, before in old_runtime.items():
        after = new_runtime[name]
        if name == "worker/admin-assets.generated.mjs":
            old_entries, new_entries = runtime_assets(before), runtime_assets(after)
            assert old_entries.keys() == new_entries.keys(), "Admin asset set changed"
            for key, entry in old_entries.items():
                updated = new_entries[key]
                if entry["type"].startswith("text/html"):
                    assert {k: v for k, v in entry.items() if k != "body"} == {k: v for k, v in updated.items() if k != "body"}, f"Admin asset metadata changed: {key}"
                    check_html(entry["body"], updated["body"], f"admin:{key}", admin=True)
                    admin_count += 1
                else:
                    assert entry == updated, f"Admin behavior or settings changed: {key}"
        elif name == "worker/login-page.mjs":
            old, new = before.read_text(encoding="utf-8"), after.read_text(encoding="utf-8")
            assert decorate_html(old, admin=True, login=True) == new, "Login changed beyond decoration"
            assert decorate_html(new, admin=True, login=True) == new, "Login decoration is not idempotent"
        else:
            assert before.read_bytes() == after.read_bytes(), f"Runtime behavior changed: {name}"
            unchanged_runtime += 1
    return {"public_documents_preserved": html_count, "unchanged_non_html_assets": unchanged_assets,
            "changed_presentation_assets": sorted(changed_presentation),
            "admin_documents_preserved": admin_count, "runtime_modules_unchanged": unchanged_runtime,
            "login_behavior_preserved": True, "decoration_idempotent": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline", "release", "baseline-runtime", "runtime"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.baseline, args.release, args.baseline_runtime, args.runtime), ensure_ascii=False))
