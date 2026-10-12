"""Restore three compact hero actions while preserving all other public assets."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.diagnosis_copy import apply_diagnosis_copy
from core.editorial_feed import _ElementSpans

INPUTS = ['core/__init__.py', 'core/diagnosis_copy.py', 'core/editorial_feed.py', 'core/glass_hero.py', 'site/templates/ai-news/glass-hero.css',
          'scripts/build_hero_actions_release.py', 'deployment/hero-actions/baseline.json',
          'cloudflare-runtime/wrangler-profile-release.jsonc',
          'deployment/admin-workspace/published-worker.mjs']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


def verify_home(before, after):
    old, new = (BeautifulSoup(s, 'html.parser') for s in (before, after))
    group = new.select_one('#top .focus-actions #diagnosis-start')
    assert group is not None
    assert [el.get_text(' ', strip=True) for el in group.select('.diagnosis-action')] == [
        '何からはじめれば？ メニュー選択フロー', 'AIに表示されてる？ サイト診断', 'ほんとにAI使えてる？ AI実力診断']
    assert [a['href'] for a in group.select('a')] == ['/seo-llmo-diagnosis/', '/ai-agent-readiness/']
    assert len(new.select('#top .diagnose-open')) == 1
    assert len(group.select('svg[aria-hidden="true"]')) == 3
    assert group.select_one('button')['aria-controls'] == 'diagnoseModal'
    assert not new.select('.hero-diagnose-cta, .diagnosis-intro, #restored-hero-image, .home-learning-links')
    for selector in ('script', '.focus-title', '.focus-lead', '.focus-trust', '#hero-glass-art', '#blog', '#ai-news', '#packages', '#diagnoseModal'):
        assert [str(el) for el in old.select(selector)] == [str(el) for el in new.select(selector)], selector
    assert len(new.select('.compact-course-card')) == 7
    def shell(document):
        for a, b in reversed(_ElementSpans(document, 'focus-actions').spans):
            document = document[:a] + document[b:]
        return re.sub(r'<style id="diagnosis-copy-style">.*?</style>', '', document, flags=re.S)
    assert shell(before) == shell(after), 'Unrelated HTML changed'
    assert apply_diagnosis_copy(after) == after, 'Repeated daily builds must retain exactly three actions'


def build(baseline, output, source_sha=None):
    contract = json.loads((ROOT/'deployment/hero-actions/baseline.json').read_text(encoding='utf-8'))
    assert baseline.name == contract['release_directory']
    assert digest(baseline/'verification.json') == contract['verification_sha256']
    previous = json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert previous['source_sha'] == contract['source_sha']
    assert hashes(baseline/'public') == previous['assets']
    assert digest(baseline/'runtime/published-worker.mjs') == contract['worker_sha256']
    before = (baseline/'public/index.html').read_bytes().decode('utf-8')
    after = apply_diagnosis_copy(before)
    verify_home(before, after)
    assert not output.exists(), 'Use a fresh output directory'
    def copy_asset(src, dst):
        if Path(src) == baseline/'public/index.html':
            return shutil.copy2(src, dst)
        import os
        shutil.copyfile(src, dst)
        return dst
    shutil.copytree(baseline/'public', output/'public', copy_function=copy_asset)
    (output/'public/index.html').write_bytes(after.encode('utf-8'))
    worker = ROOT/'deployment/admin-workspace/published-worker.mjs'
    (output/'runtime').mkdir()
    worker_bytes = worker.read_bytes().replace(b'\r\n', b'\n')
    assert hashlib.sha256(worker_bytes).hexdigest() == contract['worker_sha256'], 'Worker changed; reconcile before release'
    (output/'runtime/published-worker.mjs').write_bytes(worker_bytes)
    assets = hashes(output/'public')
    changed = [p for p in assets if assets[p] != previous['assets'][p]]
    assert changed == ['index.html']
    require_committed = source_sha is not None
    source_sha = source_sha or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert re.fullmatch('[0-9a-f]{40}', source_sha)
    inputs = {p: digest(ROOT/p) for p in INPUTS}
    committed = {p: hashlib.sha256(subprocess.check_output(['git', 'show', f'{source_sha}:{p}'], cwd=ROOT)).hexdigest()
                 for p in INPUTS} if require_committed else {}
    if require_committed:
        assert inputs == committed, 'Release inputs differ from committed Git blobs'
    result = dict(source_sha=source_sha, source_inputs_clean=inputs == committed, inputs=INPUTS,
                  source_inputs=inputs, assets=assets, changed_assets=changed,
                  unchanged_assets=len(assets)-1, worker_sha256=hashlib.sha256(worker_bytes).hexdigest())
    (output/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('source_sha', 'source_inputs_clean', 'changed_assets', 'unchanged_assets', 'worker_sha256')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-sha')
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
