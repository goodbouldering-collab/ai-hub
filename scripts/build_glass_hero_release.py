"""Add one responsive hero artwork; preserve all other public assets and Worker."""
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
from core.glass_hero import apply_glass_hero, IMAGES, START, END

INPUTS = ['core/__init__.py', 'core/editorial_feed.py', 'core/glass_hero.py',
          'core/diagnosis_copy.py', 'core/studio_design.py',
          'site/templates/ai-news/glass-hero.css', 'scripts/build_glass_hero_release.py',
          'deployment/glass-hero/baseline.json',
          'cloudflare-runtime/wrangler-profile-release.jsonc',
          'deployment/admin-workspace/published-worker.mjs'] + [
          'site/static/design-system/studio/images/' + name for name in IMAGES]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*') if p.is_file()}


def verify(before, after):
    stripped = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', after, flags=re.S)
    stripped = re.sub(r'<style id="glass-hero-style">.*?</style>', '', stripped, flags=re.S)
    assert stripped == before, 'Only the owned artwork and style may change'
    assert apply_glass_hero(after) == after, 'Repeated builds must not duplicate the artwork'
    soup = BeautifulSoup(after, 'html.parser')
    assert len(soup.select('#hero-glass-art img')) == 1
    assert len(soup.select('#glass-hero-style')) == 1
    assert not soup.select('#restored-hero-image, .home-learning-links, #top .diagnosis-action--site')
    assert len(soup.select('.compact-course-card')) == 7
    assert soup.select_one('#reel-course')
    assert soup.select_one('#top .diagnosis-action')['href'] == '/ai-agent-readiness/'
    assert len(soup.select('#top .diagnose-open')) == 1
    assert 'AIエージェント導入たった6%' in soup.select_one('#top h1').get_text()
    image = soup.select_one('#hero-glass-art img')
    assert image['width'] == image['height'] == '1200'
    assert image['fetchpriority'] == 'high' and '640w' in image['srcset']


def build(baseline, output, source_sha=None):
    contract = json.loads((ROOT / 'deployment/glass-hero/baseline.json').read_text())
    assert baseline.name == contract['release_directory']
    assert digest(baseline / 'verification.json') == contract['verification_sha256']
    manifest = json.loads((baseline / 'verification.json').read_text())
    assert manifest['source_sha'] == contract['source_sha']
    assert hashes(baseline / 'public') == manifest['assets']
    assert digest(baseline / 'runtime/published-worker.mjs') == contract['worker_sha256']
    worker = ROOT / 'deployment/admin-workspace/published-worker.mjs'
    worker_bytes = worker.read_bytes().replace(b'\r\n', b'\n')
    assert hashlib.sha256(worker_bytes).hexdigest() == contract['worker_sha256'], 'Reconcile a newer admin Worker before release'
    assert not output.exists(), 'Release output must be a fresh directory'

    def copy_asset(source, target):
        # Only unchanged files may share storage with the immutable baseline.
        if Path(source) == baseline / 'public/index.html':
            return shutil.copy2(source, target)
        os.link(source, target)
        return target

    shutil.copytree(baseline / 'public', output / 'public', copy_function=copy_asset)
    (output / 'runtime').mkdir()
    (output / 'runtime/published-worker.mjs').write_bytes(worker_bytes)
    before = (baseline / 'public/index.html').read_bytes().decode('utf-8')
    after = apply_glass_hero(before)
    verify(before, after)
    (output / 'public/index.html').write_bytes(after.encode('utf-8'))
    for name in IMAGES:
        shutil.copyfile(ROOT / 'site/static/design-system/studio/images' / name,
                        output / 'public/design-system/studio/images' / name)
    assets = hashes(output / 'public')
    added = sorted(set(assets) - set(manifest['assets']))
    changed = [p for p in manifest['assets'] if assets.get(p) != manifest['assets'][p]]
    assert changed == ['index.html']
    assert added == sorted('design-system/studio/images/' + name for name in IMAGES)
    require_committed = source_sha is not None
    source_sha = source_sha or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    source_inputs = {p: digest(ROOT / p) for p in INPUTS}
    committed = {}
    for p in INPUTS:
        blob = subprocess.run(['git', 'show', f'{source_sha}:{p}'], cwd=ROOT, capture_output=True)
        if blob.returncode == 0:
            committed[p] = hashlib.sha256(blob.stdout).hexdigest()
    clean = source_inputs == committed
    if require_committed:
        assert clean, 'Release inputs differ from committed Git blobs'
    result = dict(source_sha=source_sha, source_inputs_clean=clean, inputs=INPUTS, source_inputs=source_inputs,
                  assets=assets, changed_assets=changed, added_assets=added,
                  unchanged_assets=len(manifest['assets'])-1,
                  worker_sha256=hashlib.sha256(worker_bytes).hexdigest())
    (output / 'verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['source_sha', 'source_inputs_clean', 'changed_assets', 'added_assets', 'unchanged_assets', 'worker_sha256']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-sha')
    args = p.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
