"""Reproducible image-only release; retain all other production bytes."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
from urllib.parse import urljoin, urlsplit
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.page_art import apply_page_art_tree

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}

def build(base, output, sha):
    contract = json.loads((ROOT/'deployment/page-art/baseline.json').read_text(encoding='utf8'))
    assert hashes(base) == contract['assets'], 'Baseline mismatch'
    assert not output.exists(), 'Use a fresh release directory'
    shutil.copytree(base, output/'public')
    changed = apply_page_art_tree(output/'public')
    result = hashes(output/'public')
    art = json.loads((ROOT/'config/page-art.json').read_text(encoding='utf8'))
    for source in art['home_protected']:
        name = source.lstrip('/')
        assert result[name] == contract['assets'][name], f'Homepage asset changed: {name}'
    assert result['index.html'] == contract['assets']['index.html'], 'Homepage changed'
    expected_pages = sorted({p for im in art['images'] for p in im['pages']})
    assert changed == expected_pages, (changed, expected_pages)
    placements = 0
    for page in changed:
        before = BeautifulSoup((base/page).read_text(encoding='utf8'), 'html.parser')
        after = BeautifulSoup((output/'public'/page).read_text(encoding='utf8'), 'html.parser')
        assert before.get_text() == after.get_text(), f'Copy changed: {page}'
        old_links = [a.get('href') for a in before.select('a')]
        new_links = [a.get('href') for a in after.select('a')]
        assert old_links == new_links, f'Navigation changed: {page}'
        if page != 'speaker.html':
            assert [i.get('alt') for i in before.select('img')] == [i.get('alt') for i in after.select('img')], page
        for image in after.select('img[src], video[poster]'):
            src = image.get('src') if image.name == 'img' else image.get('poster')
            if 'paper-20261015' in src or 'paper-20261014' in src:
                local = output/'public'/urlsplit(urljoin('/'+page,src)).path.lstrip('/')
                assert local.is_file(), f'Missing image {local}'
                placements += 1
        assert [v.get('src') for v in before.select('video source')] == [v.get('src') for v in after.select('video source')]
    changed_assets = sorted(k for k in contract['assets'] if result[k] != contract['assets'][k])
    assert changed_assets == changed
    added = sorted(set(result)-set(contract['assets']))
    assert all(k.startswith('design-system/studio/images/paper-20261015/') for k in added)
    expected = {im['target'].lstrip('/') for im in art['images'] if im['mode']=='generate'}
    assert set(added) == expected, 'Missing or unplanned generated images'
    worker = (ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(worker).hexdigest() == contract['worker_sha256']
    report = dict(source_sha=sha, assets=result, changed_assets=changed_assets, added_assets=added,
                  unchanged_assets=len(contract['assets'])-len(changed), image_placements=placements,
                  homepage_unchanged=True, worker_sha256=contract['worker_sha256'])
    (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='assets'},ensure_ascii=False))
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--source-sha',required=True)
    args=parser.parse_args();build(args.baseline,args.output,args.source_sha)
