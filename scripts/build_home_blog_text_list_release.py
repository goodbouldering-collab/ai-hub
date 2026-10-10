"""Restore the September 30 home text list without rolling back published content."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.home_updates import apply_home_updates, latest_published_posts

CONTRACT = 'deployment/home-updates/text-list-20261010.json'
INPUTS = [
    'core/home_updates.py', 'site/templates/ai-news/home-updates.css',
    'scripts/build_home_blog_text_list_release.py', CONTRACT,
    'scripts/verify_ai_news_feature.py', 'cloudflare-runtime/wrangler-profile-release.jsonc',
    'tests/test_home_updates.py',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(directory):
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in directory.rglob('*') if p.is_file()}


def outside_blog(document):
    document = re.sub(r'<style id="home-updates-style">.*?</style>', '', document, flags=re.S)
    document = re.sub(r'(<div class="home-updates__news">.*?</div><!-- /home-updates-news -->).*?(</section>)', r'\1\2', document, flags=re.S)
    return re.sub(r'<section\b[^>]*id=[\'\"](?:blog|latest-blog)[\'\"][^>]*>.*?</section>', '', document, flags=re.S)


def build(baseline, output):
    contract = json.loads((ROOT / CONTRACT).read_text(encoding='utf-8'))
    assert baseline.name == contract['baseline_directory']
    assert digest(baseline / 'verification.json') == contract['baseline_verification_sha256']
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    assert previous['source_sha'] == contract['baseline_source_sha']
    assert hashes(baseline / 'public') == contract['assets']
    assert not output.exists(), 'Release output must be a fresh directory'
    worker = subprocess.check_output(['git', 'show', 'HEAD:' + contract['worker_source']], cwd=ROOT)
    assert hashlib.sha256(worker).hexdigest() == contract['worker_sha256']
    raw = (baseline / 'public/index.html').read_bytes()
    # Preserve original line endings and all non-blog markup exactly.
    document = raw.decode('utf-8')
    blog = (baseline / 'public/blog/index.html').read_text(encoding='utf-8')
    css = (ROOT / INPUTS[1]).read_text(encoding='utf-8')
    updated = apply_home_updates(document, blog, css)
    assert updated != document
    assert apply_home_updates(updated, blog, css) == updated
    assert outside_blog(document) == outside_blog(updated), 'Unrelated homepage markup changed'
    before, after = [BeautifulSoup(text, 'html.parser') for text in (document, updated)]
    assert str(before.select_one('#packages')) == str(after.select_one('#packages'))
    old_style = before.select_one('#home-updates-style').string
    course_start = '/* Courses retain'
    assert old_style[old_style.index(course_start):old_style.index('@media (max-width:800px)')] in css
    for rule in (
        'body.studio-home #packages .compact-course-grid {grid-template-columns:minmax(0,1fr)!important}',
        'body.studio-home #packages .compact-course-card {grid-template-columns:64px minmax(0,1fr);gap:6px 10px;padding:12px!important}',
        'body.studio-home #packages .compact-course-visual {width:64px!important;height:64px!important}',
    ):
        assert rule in old_style and rule in css
    assert len(after.select('#ai-news > #blog li a')) == 2
    assert not after.select('#blog-carousel, #latest-blog')
    assert after.select_one('#blog a[href="/blog/"]')
    posts = latest_published_posts(blog)
    assert [a['href'] for a in after.select('#blog li a')] == [p['href'] for p in posts]
    for post in posts:
        assert (baseline / 'public' / post['href'].lstrip('/')).is_file()
    for source in (baseline / 'public').rglob('*'):
        if not source.is_file():
            continue
        relative = source.relative_to(baseline / 'public')
        target = output / 'public' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.as_posix() == 'index.html':
            target.write_bytes(updated.encode('utf-8'))
        else:
            os.link(source, target)
    (output / 'published-worker.mjs').write_bytes(worker)
    assets = hashes(output / 'public')
    changed = [name for name in assets if assets[name] != contract['assets'][name]]
    assert changed == ['index.html']
    assert hashes(baseline / 'public') == contract['assets']
    status = subprocess.check_output(['git', 'status', '--porcelain', '--', *INPUTS], cwd=ROOT, text=True)
    result = dict(
        source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_inputs_clean=not status.strip(), inputs=INPUTS,
        source_inputs={name: digest(ROOT / name) for name in INPUTS},
        committed_worker_input=contract['worker_source'],
        assets=assets, changed_assets=changed, unchanged_assets=len(assets)-1,
        worker_sha256=hashlib.sha256(worker).hexdigest(), baseline_unchanged=True,
        latest_blogs=posts, historical_layout_commit=contract['historical_layout_commit'],
        article_assets_unchanged=True, course_markup_and_styles_unchanged=True,
        unrelated_home_markup_unchanged=True,
    )
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('assets','source_inputs','inputs')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
