"""Remove the requested hero elements from the verified public asset baseline."""
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

INPUTS = ['core/__init__.py', 'core/diagnosis_copy.py', 'core/editorial_feed.py',
          'scripts/build_hero_cleanup_release.py', 'deployment/hero-cleanup/baseline.json',
          'cloudflare-runtime/wrangler-profile-release.jsonc',
          'deployment/admin-workspace/published-worker.mjs']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


def verify_home(before, after):
    old, new = (BeautifulSoup(s, 'html.parser') for s in (before, after))
    removed = '#restored-hero-image, .home-learning-links, .diagnosis-action--site'
    assert len(old.select(removed)) == 3, 'Expected the three requested hero elements'
    assert not new.select(removed), 'Requested elements remain'
    assert new.select_one('#top + #blog'), 'Unexpected gap between hero and blog'
    assert [a['href'] for a in new.select('#diagnosis-start > a')] == ['/ai-agent-readiness/']
    for el in old.select(removed):
        el.decompose()
    # The remaining links, copy and functional controls must be preserved.
    for selector in ('a[href]', 'img', 'form', 'script', '.focus-title', '#hero-advantage-title',
                     '.focus-lead', '.focus-trust', '.hero-diagnose-cta', '#blog', '#packages'):
        assert [str(el) for el in old.select(selector)] == [str(el) for el in new.select(selector)], selector
    def shell(document):
        for class_name in ('focus-hero', 'home-learning-links'):
            for a, b in reversed(_ElementSpans(document, class_name).spans):
                document = document[:a] + document[b:]
        return re.sub(r'<style id="diagnosis-copy-style">.*?</style>', '', document, flags=re.S)
    assert shell(before) == shell(after), 'Unrelated HTML changed'
    assert apply_diagnosis_copy(after) == after, 'Daily regeneration must keep the removal'


def build(baseline, output, source_sha=None):
    contract = json.loads((ROOT/'deployment/hero-cleanup/baseline.json').read_text(encoding='utf-8'))
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
    shutil.copytree(baseline/'public', output/'public')
    (output/'public/index.html').write_bytes(after.encode('utf-8'))
    worker = ROOT/'deployment/admin-workspace/published-worker.mjs'
    (output/'runtime').mkdir()
    shutil.copyfile(worker, output/'runtime/published-worker.mjs')
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
                  unchanged_assets=len(assets)-1, worker_sha256=digest(worker))
    (output/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('source_sha', 'source_inputs_clean', 'changed_assets', 'unchanged_assets', 'worker_sha256')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-sha')
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
