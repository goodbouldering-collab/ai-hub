"""Change homepage copy on the pinned live release, preserving its worker and other assets."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.hero_copy import apply_hero_copy, TITLE, SUBTITLE, BENEFIT, CONCERN


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*') if p.is_file()}


def build(baseline, output):
    contract = json.loads((ROOT/'deployment/hero-copy/baseline.json').read_text(encoding='utf-8'))
    assert baseline.name == contract['release_directory']
    assert digest(baseline/'verification.json') == contract['verification_sha256']
    manifest = json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert manifest['source_sha'] == contract['source_sha']
    assert hashes(baseline/'public') == manifest['assets']
    assert digest(baseline/'compiled/public-entry.js') == contract['worker_sha256']
    assert output.is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline/'public', output/'public')
    shutil.copytree(baseline/'compiled', output/'compiled')
    before = (baseline/'public/index.html').read_text(encoding='utf-8')
    after = apply_hero_copy(before)
    old, new = [BeautifulSoup(s, 'html.parser') for s in (before, after)]
    for selector, expected in [('.focus-title-first', TITLE), ('.focus-title-line strong', SUBTITLE), ('#hero-advantage-title strong', BENEFIT), ('#hero-advantage-title .hero-advantage-outcome', CONCERN)]:
        assert new.select_one(selector).get_text() == expected
    for selector in ['a[href]', 'form', 'img', '#packages', 'script']:
        assert [str(e) for e in old.select(selector)] == [str(e) for e in new.select(selector)], selector
    assert apply_hero_copy(after) == after
    (output/'public/index.html').write_text(after, encoding='utf-8', newline='\n')
    assets = hashes(output/'public')
    changed = [p for p in assets if assets[p] != manifest['assets'][p]]
    assert changed == ['index.html']
    inputs = ['core/hero_copy.py', 'core/focused_ux.py', 'site/build_portal.py', 'scripts/build_ai_news_feature.py', 'scripts/build_hero_copy_release.py', 'deployment/hero-copy/baseline.json', 'cloudflare-runtime/wrangler-profile-release.jsonc']
    status = subprocess.check_output(['git', '-c', 'core.excludesFile=', 'status', '--porcelain', '--', *inputs], cwd=ROOT, text=True)
    result = dict(source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), source_inputs_clean=not status.strip(), inputs=inputs, source_inputs={p:digest(ROOT/p) for p in inputs}, assets=assets, changed_assets=changed, unchanged_assets=len(assets)-1, worker_sha256=contract['worker_sha256'])
    (output/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha', 'source_inputs_clean', 'changed_assets', 'unchanged_assets', 'worker_sha256']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
