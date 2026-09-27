"""Add one researched Orca article to an immutable live baseline without duplicating media."""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'site')]
from core.studio_design import decorate_html
CONTRACT = ROOT / 'deployment/cloudflare-blog/orca-ade-20260928.json'
ORIGIN = 'https://aiclimb.aiclimb.workers.dev'
SLUG = '2026-09-28-orca-ade-ai-manager'
NOTE = '※内容は運営者が考え、AIで整えています。'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def hashes(root):
    assert root.is_dir()
    files = sorted(root.rglob('*'))
    assert not any(p.is_symlink() for p in files)
    return {p.relative_to(root).as_posix(): sha(p) for p in files if p.is_file()}

def build(baseline, output):
    baseline, output = baseline.resolve(), output.resolve()
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    before = hashes(baseline)
    assert before == contract['assets'], 'Baseline drift: recheck current production'
    assert sha(ROOT / 'deployment/ai-news/published-worker.mjs') == contract['worker_sha256']
    assert output.is_relative_to(ROOT) and not output.exists(), 'Use a new output directory'
    spec = importlib.util.spec_from_file_location('orca_blog_site', ROOT / 'site/build_site.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    source = ROOT / f'content/blog/{SLUG}.md'
    meta, body = builder._parse_frontmatter(source.read_text(encoding='utf-8'))
    assert meta['authorship_note'] == NOTE and meta['status'] == 'published'
    path = f'blog/{SLUG}.html'
    assert path not in before
    rendered = builder._load_markdown().markdown(body, extensions=['extra', 'sane_lists', 'attr_list'])
    page = decorate_html(builder.render_content_page(str(meta['title']), meta, rendered,
        builder.render_top_nav(path_prefix='../', current_id='blog', include_run=False),
        page_path=path, kind='blog'))
    soup = BeautifulSoup(page, 'html.parser')
    content = soup.select_one('.content-wrap')
    headings = content.select('h2')
    assert len(headings) == 4
    assert all(h.find_next_sibling().name == 'figure' for h in headings)
    images = content.select('img')
    assert len(images) == 5 and len({i['src'] for i in images}) == 5
    assert soup.h1.get_text() == meta['title']
    note = soup.select_one('main > p')
    assert note.get_text() == NOTE and not note.attrs
    assert soup.select_one('link[rel="canonical"]')['href'] == f'{ORIGIN}/{path}'
    assert soup.select_one('meta[property="og:image"]')['content'] == ORIGIN + meta['image']
    ld = json.loads(soup.select_one('script[type="application/ld+json"]').string)
    assert ld['headline'] == meta['title']
    assert 'すべて創作' in content.get_text() and '投稿の要旨' in content.get_text()
    assert len(content.select('a[href^="https://"]')) >= 12
    assert not soup.select('[contenteditable],meta[name="robots"][content*="noindex"]')
    # Immutable assets share disk blocks; the three edited documents are always COPIES.
    owned = {'index.html', 'blog/index.html', 'sitemap.xml'}
    for rel in before:
        src, dest = baseline / rel, output / 'public' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel in owned:
            shutil.copyfile(src, dest)
        else:
            os.link(src, dest)
    (output / 'public' / path).write_text(page, encoding='utf-8', newline='\n')
    image_inputs = []
    for img in images:
        rel = img['src'].lstrip('/')
        assert rel.startswith('img/blog-orca-ade-') and '..' not in rel and img.get('alt')
        p = ROOT / 'site/static' / rel
        with Image.open(p) as bitmap:
            assert bitmap.width > bitmap.height
            bitmap.verify()
        assert rel not in before
        os.link(p, output / 'public' / rel)
        image_inputs.append(p)
    title, summary, date = [html.escape(str(meta[k]), quote=True) for k in ('title','summary','date')]
    image = html.escape(meta['image'], quote=True)
    home_card = (f"<a class='blog-card' href='/{path}'>"
        f"<div class='blog-card-media'><img src='{image}' alt='' loading='lazy' decoding='async'></div>"
        f"<div class='blog-card-body'><div class='blog-card-meta'><span>{date}</span></div>"
        f"<div class='blog-card-title-row'><h3>{title}</h3><span class='blog-new-badge'>NEW</span></div>"
        f"<p>{summary}</p><span class='blog-card-more'>読む</span></div></a>")
    index_card = (f"<a class='tr-card' href='./{SLUG}.html'><div class='tr-title'>{title}</div>"
        f"<div class='tr-date'>{date}</div><div class='tr-sum'>{summary}</div></a>")
    for rel, marker, addition in [
        ('index.html', "<div class='pf-carousel blog-carousel' id='blog-carousel'>", home_card),
        ('blog/index.html', "<div class='tr-grid'>", index_card)]:
        original = (baseline / rel).read_text(encoding='utf-8')
        assert original.count(marker) == 1 and SLUG not in original
        updated = original.replace(marker, marker + addition, 1)
        assert updated.replace(addition, '', 1) == original
        (output / 'public' / rel).write_text(updated, encoding='utf-8', newline='\n')
    original = (baseline / 'sitemap.xml').read_text(encoding='utf-8')
    assert original.count('</urlset>') == 1 and SLUG not in original
    entry = f'<url><loc>{ORIGIN}/{path}</loc><lastmod>{date}</lastmod><priority>0.7</priority></url>\n'
    sitemap = original.replace('</urlset>', entry + '</urlset>')
    ET.fromstring(sitemap)
    (output / 'public/sitemap.xml').write_text(sitemap, encoding='utf-8', newline='\n')
    assets = hashes(output / 'public')
    changed = sorted(p for p in before if assets[p] != before[p])
    added = sorted(assets.keys() - before.keys())
    assert changed == sorted(owned) and len(added) == 6
    assert hashes(baseline) == before, 'Immutable baseline was modified'
    paths = [CONTRACT, Path(__file__).resolve(), source, *image_inputs, ROOT / 'site/build_site.py',
        ROOT / 'deployment/ai-news/published-worker.mjs', ROOT / 'cloudflare-runtime/wrangler-profile-release.jsonc']
    for module in list(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if file:
            p = Path(file).resolve()
            if p.is_file() and p.is_relative_to(ROOT) and p.suffix == '.py':
                paths.append(p)
    paths.extend(p for p in (ROOT/'config').glob('*') if p.is_file())
    inputs = {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}
    dirty = subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*inputs],cwd=ROOT,text=True).splitlines()
    result = dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_inputs=inputs, source_inputs_clean=not dirty, source_input_status=dirty,
        baseline_source_sha=contract['source_sha'], baseline_version=contract['cloudflare_version'],
        assets=assets, changed_assets=changed, added_assets=added, preserved_assets=len(before)-3,
        worker_sha256=contract['worker_sha256'], baseline_unchanged=True,
        article_checks=dict(h2=4,images=5,authorship_note=True,canonical=True,jsonld=True,sitemap=True,fiction_labeled=True),deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','changed_assets','added_assets','preserved_assets','article_checks']},ensure_ascii=False))

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    build(args.baseline,args.output)
