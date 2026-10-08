"""Swap home blog sections and compact the course menu from the verified public release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.home_updates import apply_home_updates, latest_published_posts, published_posts
from bs4 import BeautifulSoup

INPUTS = [
    'core/home_updates.py', 'site/templates/ai-news/home-updates.css',
    'scripts/build_compact_blog_courses_release.py', 'deployment/home-updates/compact-blog-courses-baseline.json',
    'deployment/ai-news/published-worker.mjs',
    'cloudflare-runtime/wrangler-profile-release.jsonc',
    'scripts/build_ai_news_feature.py', 'scripts/verify_ai_news_feature.py',
    'config/home-blog-images.json', 'tests/test_home_updates.py',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(directory):
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in directory.rglob('*') if p.is_file()}


def build(baseline, output):
    contract = json.loads((ROOT / INPUTS[3]).read_text(encoding='utf-8'))
    assert baseline.name == contract['baseline_directory']
    assert digest(baseline / 'verification.json') == contract['baseline_verification_sha256']
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    assert previous['source_sha'] == contract['baseline_source_sha']
    assert hashes(baseline / 'public') == previous['assets']
    assert digest(ROOT / INPUTS[4]) == contract['worker_sha256']
    assert output.is_relative_to(ROOT) and not output.exists()
    before = (baseline / 'public/index.html').read_bytes()
    document = before.decode('utf-8')
    blog = (baseline / 'public/blog/index.html').read_text(encoding='utf-8')
    css = (ROOT / INPUTS[1]).read_text(encoding='utf-8')
    updated = apply_home_updates(document, blog, css)
    inputs = INPUTS + [f'content/blog/{Path(p['href']).stem}.md' for p in published_posts(blog)[:7]
                       if (ROOT / 'content/blog' / (Path(p['href']).stem + '.md')).is_file()]
    old_home, new_home = (BeautifulSoup(html, 'html.parser') for html in (document, updated))
    # Only relocation and the scoped style change: keep every course, link and detail.
    for section in old_home.select('main > section'):
        if section.get('id') not in ('ai-news', 'blog'):
            assert str(section) == str(new_home.select_one('#' + section['id'])), section['id']
    assert len(new_home.select('#packages .compact-course-card')) == 6
    assert new_home.select_one('#ai-news > #blog #blog-carousel')
    assert new_home.select_one('#latest-blog').find_next_sibling()['id'] == 'speaker'
    assert updated != document
    assert apply_home_updates(updated, blog, css) == updated
    assert '彦根で相談する' not in updated
    assert '講師のプロフィールを見る' in updated
    for post in latest_published_posts(blog):
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
    shutil.copyfile(ROOT / INPUTS[4], output / 'published-worker.mjs')
    assets = hashes(output / 'public')
    changed = [name for name in assets if assets[name] != previous['assets'][name]]
    assert changed == ['index.html']
    assert hashes(baseline / 'public') == previous['assets']
    status = subprocess.check_output(['git', '-c', 'core.excludesFile=', 'status',
                                     '--porcelain', '--', *inputs], cwd=ROOT, text=True)
    result = dict(
        source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_inputs_clean=not status.strip(), inputs=inputs,
        source_inputs={name: digest(ROOT / name) for name in inputs},
        assets=assets, changed_assets=changed, unchanged_assets=len(assets) - 1,
        worker_sha256=digest(output / 'published-worker.mjs'),
        baseline_unchanged=True, latest_blogs=latest_published_posts(blog),
    )
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['assets', 'source_inputs', 'inputs']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
