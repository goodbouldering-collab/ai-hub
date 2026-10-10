"""Publish only the approved homepage, article index and 21 new illustrations."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.home_updates import apply_home_updates
from core.editorial_feed import apply_blog_feed, public_posts
from core.editorial_home import ART, IMAGE_ROOT
from scripts.verify_ai_news_feature import verify

CONTRACT = 'deployment/home-updates/editorial-20261011.json'
ART_DIR = 'site/static/design-system/studio/images/editorial-20261011'
INPUTS = [
    CONTRACT, 'core/home_updates.py', 'core/editorial_feed.py', 'core/editorial_home.py',
    'config/editorial-feed.json', 'site/templates/ai-news/home-updates.css',
    'site/templates/ai-news/editorial-feed.css', 'site/templates/ai-news/editorial-home.css',
    'scripts/build_home_editorial_release.py', 'scripts/verify_ai_news_feature.py',
    'scripts/build_ai_news_feature.py', 'cloudflare-runtime/wrangler-profile-release.jsonc',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(directory):
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in directory.rglob('*') if p.is_file()}


def content_signature(document):
    soup = BeautifulSoup(document, 'html.parser')
    for element in soup.select('#ai-news, style, script'):
        element.decompose()
    main = soup.select_one('main')
    return {
        'text': re.sub(r'\s+', ' ', main.get_text(' ', strip=True)),
        'links': [a.get('href') for a in soup.select('a[href]')],
        'details': [str(d) for d in main.select('details')],
        'forms': [str(f) for f in soup.select('form')],
    }


def post_signature(document):
    return [{k: post[k] for k in ('href', 'title', 'date', 'summary')}
            for post in public_posts(document)]


def build(baseline, output):
    contract = json.loads((ROOT / CONTRACT).read_text(encoding='utf-8'))
    assert baseline.name == contract['baseline_directory']
    assert digest(baseline / 'verification.json') == contract['baseline_verification_sha256']
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    assert previous['source_sha'] == contract['baseline_source_sha']
    assert hashes(baseline / 'public') == contract['assets'], 'Published baseline changed'
    assert not output.exists(), 'Use a fresh release directory'
    worker = subprocess.check_output(['git', 'show', 'HEAD:' + contract['worker_source']], cwd=ROOT)
    assert hashlib.sha256(worker).hexdigest() == contract['worker_sha256']
    original_home = (baseline / 'public/index.html').read_bytes().decode('utf-8')
    original_blog = (baseline / 'public/blog/index.html').read_bytes().decode('utf-8')
    templates = ROOT / 'site/templates/ai-news'
    css = (templates / 'home-updates.css').read_text(encoding='utf-8')
    feed_css = (templates / 'editorial-feed.css').read_text(encoding='utf-8')
    home = apply_home_updates(original_home, original_blog, css)
    news_date = BeautifulSoup(home, 'html.parser').select_one('#blog')['data-news-date']
    blog = apply_blog_feed(original_blog, news_date, feed_css)
    assert apply_home_updates(home, blog, css) == home
    assert apply_blog_feed(blog, news_date, feed_css) == blog
    assert content_signature(original_home) == content_signature(home), 'Unrelated content or controls changed'
    assert post_signature(original_blog) == post_signature(blog), 'Published article metadata changed'
    assert len(public_posts(blog)) == contract['public_blog_count']
    home_soup = BeautifulSoup(home, 'html.parser')
    original_art = [img for img in BeautifulSoup(original_home, 'html.parser').select('img')
                    if Path(img.get('src', '').split('?', 1)[0]).stem in ART]
    assert len(original_art) == contract['home_art_count']
    assert len(home_soup.select('img[src^="' + IMAGE_ROOT + '"]')) == len(original_art) + 3
    artwork = sorted((ROOT / ART_DIR).glob('*.webp'))
    assert len(artwork) == contract['new_art_count'], f'Expected 21 finished illustrations, got {len(artwork)}'
    changed_documents = {'index.html': home, 'blog/index.html': blog}
    for source in (baseline / 'public').rglob('*'):
        if not source.is_file():
            continue
        name = source.relative_to(baseline / 'public').as_posix()
        target = output / 'public' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name in changed_documents:
            target.write_bytes(changed_documents[name].encode('utf-8'))
        else:
            os.link(source, target)
    for source in artwork:
        target = output / 'public' / IMAGE_ROOT.lstrip('/') / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    runtime = output / 'runtime/published-worker.mjs'
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_bytes(worker)
    assets = hashes(output / 'public')
    changed = sorted(name for name in contract['assets'] if assets[name] != contract['assets'][name])
    added = sorted(set(assets) - set(contract['assets']))
    assert changed == sorted(changed_documents)
    assert len(added) == contract['new_art_count']
    assert hashes(baseline / 'public') == contract['assets'], 'Baseline must stay immutable'
    for document in (home, blog):
        soup = BeautifulSoup(document, 'html.parser')
        for img in soup.select('img[src^="' + IMAGE_ROOT + '"]'):
            assert (output / 'public' / img['src'].lstrip('/')).is_file()
        for row in soup.select('.editorial-feed__row'):
            path = row['href'].replace('./', '/blog/', 1).lstrip('/')
            assert (output / 'public' / (path + 'index.html' if path.endswith('/') else path)).is_file()
    checks = verify(lambda name: (output / 'public' / name).read_text(encoding='utf-8'))
    inputs = INPUTS + [p.relative_to(ROOT).as_posix() for p in artwork]
    status = subprocess.check_output(['git', 'status', '--porcelain', '--', *inputs], cwd=ROOT, text=True)
    result = {
        'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_inputs_clean': not status.strip(), 'inputs': inputs,
        'source_inputs': {name: digest(ROOT / name) for name in inputs},
        'assets': assets, 'changed_assets': changed, 'added_assets': added,
        'unchanged_assets': len(contract['assets']) - len(changed),
        'worker_sha256': hashlib.sha256(worker).hexdigest(),
        'committed_worker_input': contract['worker_source'],
        'article_assets_unchanged': True, 'course_copy_prices_links_unchanged': True,
        'unrelated_home_content_unchanged': True, 'baseline_unchanged': True, 'checks': checks,
    }
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('assets', 'source_inputs', 'inputs')}, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
