"""Rebuild this scoped release from a hash-verified public baseline."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.diagnosis_copy import apply_diagnosis_copy
from core.editorial_home import replace_home_art
from core.editorial_feed import apply_home_feed, apply_blog_feed, public_posts
from scripts.verify_ai_news_feature import verify


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def build(base, output, source_sha):
    contract = json.loads((ROOT / 'deployment/admin-workspace/release-baseline.json').read_text(encoding='utf-8'))
    if hashes(base) != contract['assets']:
        raise ValueError('Baseline differs from the previously verified public release')
    if output.exists():
        raise ValueError('Use a new output directory; existing release evidence is immutable')
    public = output / 'public'
    shutil.copytree(base, public)
    old_home = (base / 'index.html').read_text(encoding='utf-8')
    old_blog = (base / 'blog/index.html').read_text(encoding='utf-8')
    css = (ROOT / 'site/templates/ai-news/editorial-feed.css').read_text(encoding='utf-8')
    home = apply_diagnosis_copy(replace_home_art(apply_home_feed(old_home, public_posts(old_blog), css)))
    blog = apply_blog_feed(old_blog, '2026-10-11', css)
    (public / 'index.html').write_text(home, encoding='utf-8', newline='')
    (public / 'blog/index.html').write_text(blog, encoding='utf-8', newline='')
    art = 'design-system/studio/images/photo-20261011'
    shutil.copytree(ROOT / 'site/static' / art, public / art)
    runtime = output / 'runtime'
    runtime.mkdir()
    worker = ROOT / 'deployment/admin-workspace/published-worker.mjs'
    shutil.copyfile(worker, runtime / worker.name)

    before, after = BeautifulSoup(old_home, 'html.parser'), BeautifulSoup(home, 'html.parser')
    assert not after.select('#blog .tr-sum'), 'Homepage must contain no blog excerpts'
    assert len(after.select('.diagnosis-guide-row > a')) == 2
    assert not after.select('.diagnosis-guide-row section, .diagnosis-guide-row p')
    for selector in ('#ai-news', '#speaker', '.compact-course-card'):
        a, b = before.select(selector), after.select(selector)
        assert len(a) == len(b)
        for x,y in zip(a,b):
            assert x.get_text() == y.get_text(), f'Unrelated copy changed: {selector}'
            assert [e.get('href') for e in x.select('a')] == [e.get('href') for e in y.select('a')]
    assert [p['summary'] for p in public_posts(old_blog)] == [p['summary'] for p in public_posts(blog)]
    for document in (home, blog):
        assert '/editorial-20261011/' not in str(BeautifulSoup(document,'html.parser').select('img'))
        for image in BeautifulSoup(document,'html.parser').select(f'img[src*="{art}"]'):
            assert (public / image['src'].lstrip('/')).is_file()
    result = hashes(public)
    changed = [p for p,h in contract['assets'].items() if result.get(p) != h]
    assert sorted(changed) == sorted(['index.html','blog/index.html']), changed
    assert len(set(result)-set(contract['assets'])) == 21
    report = {'source_sha':source_sha,'baseline_source_sha':contract['source_sha'],
              'assets':result,'changed_assets':changed,'added_images':21,
              'unchanged_assets':len(contract['assets'])-2,
              'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),
              'verified':verify(lambda name:(public/name).read_text(encoding='utf-8'))}
    (output / 'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='assets'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-assets',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-sha',required=True)
    args=parser.parse_args()
    build(args.base_assets,args.output,args.source_sha)
