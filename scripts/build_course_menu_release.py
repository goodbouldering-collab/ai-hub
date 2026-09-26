"""Rebuild only the home menu from the verified published asset snapshot."""
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
from core.course_menu import apply_course_menu, NOTICE


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*') if p.is_file()}


def verify(before, after):
    old, new = (BeautifulSoup(value, 'html.parser') for value in (before, after))
    assert [len(g.select('.compact-course-card')) for g in new.select('.compact-course-grid')] == [2, 4]
    assert new.select_one('#course-time-note').get_text().endswith(NOTICE)
    assert 'AI個別講習' not in after
    cards = new.select('.compact-course-card')
    assert [c.select_one('.compact-course-heading h3').get_text() for c in cards[:3]] == ['AIエージェント講習', 'AI個別相談', 'AIコーディング講習']
    for card, price, time in [(cards[0], '5,500円', '120分'), (cards[1], '5,500円', '60分')]:
        assert card.select_one('.compact-course-meta strong').get_text() == price
        assert card.select_one('.compact-course-meta span').get_text() == time
    assert '毎週水曜・複数人' in cards[0].get_text()
    assert '時間を指定・マンツーマン' in cards[1].get_text()
    for selector, attr in [('a[href]', 'href'), ('form[action]', 'action'), ('img[src]', 'src')]:
        assert [e[attr] for e in old.select(selector)] == [e[attr] for e in new.select(selector)], selector
    assert [e.get('id') for e in old.select('main section[id]')] == [e.get('id') for e in new.select('main section[id]')]
    for node in new.select('script[type="application/ld+json"]'):
        json.loads(node.string)
    assert apply_course_menu(after) == after


def build(baseline, output):
    contract = json.loads((ROOT / 'deployment/course-menu/baseline.json').read_text())
    assert baseline.name == contract['release_directory']
    assert digest(baseline / 'verification.json') == contract['verification_sha256']
    manifest = json.loads((baseline / 'verification.json').read_text())
    assert manifest['source_sha'] == contract['source_sha']
    assert hashes(baseline / 'public') == manifest['assets'], 'Published baseline changed'
    assert output.resolve().is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline / 'public', output / 'public')
    before = (baseline / 'public/index.html').read_text(encoding='utf-8')
    after = apply_course_menu(before)
    verify(before, after)
    (output / 'public/index.html').write_text(after, encoding='utf-8', newline='\n')
    assets = hashes(output / 'public')
    changed = [n for n in assets if assets[n] != manifest['assets'][n]]
    assert changed == ['index.html']
    inputs = ['core/course_menu.py', 'scripts/build_course_menu_release.py', 'deployment/course-menu/baseline.json',
              'deployment/ai-news/published-worker.mjs', 'cloudflare-runtime/wrangler-profile-release.jsonc']
    status = subprocess.check_output(['git', '-c', 'core.excludesFile=', 'status', '--porcelain', '--', *inputs], cwd=ROOT, text=True)
    result = dict(source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  source_inputs_clean=not status.strip(), inputs=inputs, source_inputs={p:digest(ROOT/p) for p in inputs},
                  assets=assets, changed_assets=changed, unchanged_assets=len(assets)-1,
                  worker_sha256=digest(ROOT/'deployment/ai-news/published-worker.mjs'))
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['source_sha', 'source_inputs_clean', 'changed_assets', 'unchanged_assets']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
