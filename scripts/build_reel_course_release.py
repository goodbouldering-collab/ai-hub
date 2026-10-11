"""Add one course to the verified live homepage, retaining every other asset."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.reel_course import apply_reel_course, course_data, START, END


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*') if p.is_file()}


def verify(before, after):
    c = course_data()
    stripped = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', after, flags=re.S)
    stripped = re.sub(r'<script id="reel-course-schema".*?</script>', '', stripped, flags=re.S)
    assert stripped.replace('講習・相談・制作の全7メニュー', '講習・相談・制作の全6メニュー') == before
    assert apply_reel_course(after) == after
    old, new = [BeautifulSoup(s, 'html.parser') for s in (before, after)]
    assert [len(g.select('.compact-course-card')) for g in new.select('.compact-course-grid')] == [2, 5]
    assert [str(n) for n in old.select('.compact-course-card')] == [str(n) for n in new.select('.compact-course-card:not(#reel-course)')]
    assert new.select('.compact-course-card')[-1]['id'] == 'seven-day-courses'
    card = new.select_one('#reel-course')
    assert card.select_one('h3').get_text() == c['name']
    assert card.select_one('.compact-course-meta strong').get_text() == '8,800円（税込）'
    assert card.select_one('.compact-course-action')['href'] == c['square']['booking_url']
    assert c['audience'] in card.get_text()
    assert 'Astra' in card.get_text() and 'シナリオ' in card.get_text()
    assert not card.select('.compact-course-testimonials, blockquote')
    for tag in new.select('script[type="application/ld+json"]'):
        json.loads(tag.string)


def build(baseline, output, source_sha=None):
    contract = json.loads((ROOT/'deployment/reel-course/baseline.json').read_text())
    assert baseline.name == contract['release_directory']
    assert digest(baseline/'verification.json') == contract['verification_sha256']
    manifest = json.loads((baseline/'verification.json').read_text())
    assert manifest['source_sha'] == contract['source_sha']
    assert hashes(baseline/'public') == manifest['assets']
    assert digest(baseline/'runtime/published-worker.mjs') == contract['worker_sha256']
    worker = ROOT/'deployment/admin-workspace/published-worker.mjs'
    assert digest(worker) == contract['worker_sha256'], 'Reconcile a newer admin Worker before release'
    assert not output.exists()
    def copy_asset(source, target):
        # Immutable baseline assets can share disk space; the edited homepage
        # must have its own file so no write can change the verified baseline.
        if Path(source) == baseline/'public/index.html':
            return shutil.copy2(source, target)
        try:
            os.link(source, target)
        except OSError:
            return shutil.copy2(source, target)
        return target
    shutil.copytree(baseline/'public', output/'public', copy_function=copy_asset)
    (output/'runtime').mkdir()
    shutil.copyfile(worker, output/'runtime/published-worker.mjs')
    before = (baseline/'public/index.html').read_bytes().decode('utf-8')
    after = apply_reel_course(before)
    verify(before, after)
    (output/'public/index.html').write_bytes(after.encode('utf-8'))
    assets = hashes(output/'public')
    changed = [p for p in assets if assets[p] != manifest['assets'][p]]
    assert changed == ['index.html']
    assert course_data()['image'].lstrip('/') in assets
    inputs = ['core/__init__.py', 'core/editorial_feed.py', 'core/reel_course.py', 'config/reel-course.json',
              'scripts/build_reel_course_release.py', 'deployment/reel-course/baseline.json',
              'cloudflare-runtime/wrangler-profile-release.jsonc', 'deployment/admin-workspace/published-worker.mjs']
    require_committed = source_sha is not None
    source_sha = source_sha or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    source_inputs = {p: digest(ROOT/p) for p in inputs}
    committed = {}
    for p in inputs:
        blob = subprocess.run(['git', 'show', f'{source_sha}:{p}'], cwd=ROOT, capture_output=True)
        if blob.returncode == 0:
            committed[p] = hashlib.sha256(blob.stdout).hexdigest()
    clean = source_inputs == committed
    if require_committed:
        assert clean, 'Release inputs differ from committed Git blobs'
    result = dict(source_sha=source_sha, source_inputs_clean=clean, inputs=inputs, source_inputs=source_inputs,
                  assets=assets, changed_assets=changed, unchanged_assets=len(assets)-1, worker_sha256=digest(worker))
    (output/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['source_sha', 'source_inputs_clean', 'changed_assets', 'unchanged_assets', 'worker_sha256']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-sha')
    args = p.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
