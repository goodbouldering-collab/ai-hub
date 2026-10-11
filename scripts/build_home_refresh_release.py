"""Release the hero, integrated blog news and brighter homepage from a pinned baseline."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.editorial_feed import _ElementSpans, integrate_home_news
from core.diagnosis_copy import apply_diagnosis_copy
from core.friendly_home import apply_friendly_home, apply_public_logo
from core.news_images import apply_news_images, strip_news_images

INPUTS = ('core/__init__.py', 'core/editorial_feed.py', 'core/diagnosis_copy.py',
          'core/friendly_home.py', 'core/news_images.py', 'config/news-images.json',
          'content/daily-ai-news.json', 'site/templates/ai-news/news-images.css',
          'site/templates/ai-news/friendly-glass.css',
          'scripts/build_home_refresh_release.py', 'deployment/home-refresh/baseline.json',
          'deployment/home-refresh/brand-assets.json')
BRAND_ASSETS = json.loads((ROOT / 'deployment/home-refresh/brand-assets.json').read_text(encoding='utf-8'))
HERO_ASSET = 'design-system/studio/images/photo-20261011/hero-friendly-20261011.webp'
STATIC_ASSETS = [*BRAND_ASSETS, HERO_ASSET]
INPUTS += tuple('site/static/' + name for name in STATIC_ASSETS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(folder):
    return {p.relative_to(folder).as_posix(): digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def transform(document):
    return apply_news_images(apply_friendly_home(integrate_home_news(apply_diagnosis_copy(document))))


def verify_home(document, updated):
    old, new = (BeautifulSoup(html, 'html.parser') for html in (document, strip_news_images(updated)))
    # Unchanged copy, destinations, photos and article cards are checked directly.
    for selector in ('.focus-title', '#hero-advantage-title', '.focus-lead', '.hero-diagnose-cta',
                     '.focus-trust', '#blog > .editorial-feed__list'):
        if str(old.select_one(selector)) != str(new.select_one(selector)):
            raise ValueError(f'Content changed: {selector}')
    old_hero = old.select_one('#restored-hero-image img')
    old_hero['src'] = '/' + HERO_ASSET
    if str(old.select_one('#restored-hero-image')) != str(new.select_one('#restored-hero-image')):
        raise ValueError('Unexpected hero image attributes changed')
    for tag, attr in (('a', 'href'), ('img', 'src')):
        if Counter((str(el.get(attr)), el.get_text(' ', strip=True)) for el in old.select(tag)) != Counter((str(el.get(attr)), el.get_text(' ', strip=True)) for el in new.select(tag)):
            raise ValueError(f'Page {tag} content changed')
    for selector in ('#ai-news time', '#ai-news .ai-news-feature__reading'):
        if str(old.select_one(selector)) != str(new.select_one(selector)):
            raise ValueError(f'News content changed: {selector}')
    # Outside the two requested layout regions, compare the actual HTML bytes.
    def shell(html):
        html = strip_news_images(html)
        html = html.replace("/design-system/studio/images/photo-20261011/hero.webp", "/" + HERO_ASSET)
        for name in ('focus-hero', 'diagnosis-guide-row', 'home-learning-links', 'editorial-feed--home', 'ai-news-feature'):
            for a, b in reversed(_ElementSpans(html, name).spans):
                html = html[:a] + html[b:]
        return re.sub(r'<style id="(?:diagnosis-copy|friendly-glass)-style">.*?</style>', '', html, flags=re.S)
    if shell(document) != shell(updated):
        raise ValueError('Unrelated HTML changed')
    if not new.select_one('#top .focus-lead + .focus-trust + .focus-actions #diagnosis-start'):
        raise ValueError('Hero arrangement is incorrect')
    if not new.select_one('#top + .home-learning-links + #blog'):
        raise ValueError('Learning links must follow the hero')
    if not new.select_one('#blog > .editorial-feed__heading + #ai-news + .editorial-feed__list'):
        raise ValueError('Daily news must be the first blog entry')
    if len(new.select('#diagnosis-start')) != 1 or len(new.select('#ai-news')) != 1:
        raise ValueError('Duplicate featured content')
    if transform(updated) != updated:
        raise ValueError('Homepage transformation must be idempotent')


def build(baseline, output, source_sha):
    if not re.fullmatch('[0-9a-f]{40}', source_sha):
        raise ValueError('Expected a complete source SHA')
    contract = json.loads((ROOT / 'deployment/home-refresh/baseline.json').read_text(encoding='utf-8'))
    if digest(baseline / 'verification.json') != contract['verification_sha256']:
        raise ValueError('Unexpected baseline manifest')
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    if previous['source_sha'] != contract['source_sha']:
        raise ValueError('Unexpected baseline source SHA')
    before = hashes(baseline / 'public')
    if before != previous['assets']:
        raise ValueError('Baseline assets changed')
    worker = baseline / 'runtime/published-worker.mjs'
    if digest(worker) != previous['worker_sha256']:
        raise ValueError('Baseline Worker changed')
    if output.exists():
        raise ValueError('Use a fresh output directory')
    old_css = (baseline / 'public/design-system/studio/studio.css').read_text(encoding='utf-8').strip()
    new_css = (ROOT / 'site/static/design-system/studio/studio.css').read_text(encoding='utf-8')
    if new_css.split('/* ai-sodan-brand:20261011 */')[0].strip() != old_css:
        raise ValueError('Shared styles changed outside the new logo')
    inputs = {p: digest(ROOT / p) for p in INPUTS}
    document = (baseline / 'public/index.html').read_bytes().decode('utf-8')
    updated = transform(document)
    verify_home(document, updated)
    shutil.copytree(baseline / 'public', output / 'public')
    (output / 'runtime').mkdir()
    shutil.copyfile(worker, output / 'runtime/published-worker.mjs')
    (output / 'public/index.html').write_bytes(updated.encode('utf-8'))
    article = (baseline / 'public/ai-news/index.html').read_bytes().decode('utf-8')
    illustrated = apply_news_images(apply_public_logo(article))
    if strip_news_images(illustrated) != apply_public_logo(article) or apply_news_images(illustrated) != illustrated:
        raise ValueError('News text or links changed while adding images')
    (output / 'public/ai-news/index.html').write_bytes(illustrated.encode('utf-8'))
    for name in STATIC_ASSETS:
        target = output / 'public' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'site/static' / name, target)
    after = hashes(output / 'public')
    changed = [name for name in before if after.get(name) != before[name]]
    if set(changed) - {'index.html', 'ai-news/index.html', *STATIC_ASSETS} or set(after) - set(before) - set(STATIC_ASSETS):
        raise ValueError('Unexpected assets changed')
    if set(before) - set(after):
        raise ValueError('Existing assets were removed')
    if not all(after.get(name) == before[name] for name in before if name not in {'index.html', 'ai-news/index.html', *STATIC_ASSETS}):
        raise ValueError('Unrelated assets changed')
    if inputs != {p: digest(ROOT / p) for p in INPUTS}:
        raise ValueError('Build inputs changed during generation')
    report = dict(source_sha=source_sha, baseline_source_sha=previous['source_sha'], assets=after,
                  changed_assets=changed, unchanged_assets=len(before)-len(changed), added_assets=sorted(set(after)-set(before)),
                  worker_sha256=digest(output / 'runtime/published-worker.mjs'),
                  source_inputs_sha256=inputs, unrelated_content_unchanged=True)
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('assets','source_inputs_sha256')}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
