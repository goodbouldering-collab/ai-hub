"""Revise the existing Orca article while preserving every unrelated live asset."""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
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
CONTRACT = ROOT / 'deployment/cloudflare-blog/orca-ade-evidence-20260928.json'
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
    assert path in before
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
    assert '導入・接続までの記録' in content.get_text() and '自己申告' in content.get_text()
    source_links = {a['href'] for a in content.select('a[href^="https://"]')}
    assert {'https://www.onorca.dev/docs', 'https://www.onorca.dev/docs/model/worktrees',
        'https://www.onorca.dev/docs/browser/design-mode',
        'https://www.reddit.com/r/ClaudeCode/comments/1vwjgyv/orca_ade_is_incredible/',
        'https://www.onorca.dev/docs/recipes/parallel-agents'} <= source_links
    assert not soup.select('[contenteditable],meta[name="robots"][content*="noindex"]')
    visible_length = len(re.sub(r'\s+', '', BeautifulSoup(rendered, 'html.parser').get_text()))
    assert 2000 < visible_length < 3300, 'Keep the revised story concise'
    assert all('-evidence-' in i['src'] for i in images)
    # Immutable assets share disk blocks; the three edited documents are always COPIES.
    owned = {'index.html', 'blog/index.html', path}
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
    card_pattern = re.compile(r'<a\b[^>]*href=[\'\"][^\'\"]*' + re.escape(SLUG) + r'\.html[\'\"][^>]*>.*?</a>', re.S)
    for rel, replacement in [('index.html', home_card), ('blog/index.html', index_card)]:
        original = (baseline / rel).read_text(encoding='utf-8')
        matches = list(card_pattern.finditer(original))
        assert len(matches) == 1, f'Expected one existing article card in {rel}'
        match = matches[0]
        updated = original[:match.start()] + replacement + original[match.end():]
        assert updated.replace(replacement, match.group(0), 1) == original
        (output / 'public' / rel).write_text(updated, encoding='utf-8', newline='\n')
    sitemap = (baseline / 'sitemap.xml').read_text(encoding='utf-8')
    assert sitemap.count(f'<loc>{ORIGIN}/{path}</loc>') == 1
    ET.fromstring(sitemap)
    assets = hashes(output / 'public')
    changed = sorted(p for p in before if assets[p] != before[p])
    added = sorted(assets.keys() - before.keys())
    assert changed == sorted(owned) and len(added) == 5
    assert hashes(baseline) == before, 'Immutable baseline was modified'
    paths = [CONTRACT, Path(__file__).resolve(), ROOT / 'scripts/plot_orca_evidence.py', ROOT / 'docs/blog/2026-09-28-orca-evidence/data.json', source, *image_inputs, ROOT / 'site/build_site.py',
        ROOT / 'deployment/ai-news/published-worker.mjs', ROOT / 'cloudflare-runtime/wrangler-profile-release.jsonc']
    for module in list(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if file:
            p = Path(file).resolve()
            if p.is_file() and p.is_relative_to(ROOT) and p.relative_to(ROOT).parts[0] in {'core','site','scripts'} and p.suffix == '.py':
                paths.append(p)
    paths.extend(p for p in (ROOT/'config').glob('*') if p.is_file())
    inputs = {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}
    dirty = subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*inputs],cwd=ROOT,text=True).splitlines()
    result = dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_inputs=inputs, source_inputs_clean=not dirty, source_input_status=dirty,
        baseline_source_sha=contract['source_sha'], baseline_version=contract['cloudflare_version'],
        assets=assets, changed_assets=changed, added_assets=added, preserved_assets=len(before)-3,
        worker_sha256=contract['worker_sha256'], baseline_unchanged=True,
        article_checks=dict(h2=4,images=5,authorship_note=True,canonical=True,jsonld=True,sitemap=True,evidence_scopes_labeled=True,
            visible_body_characters=visible_length, previous_body_characters=contract['body_length_before'],
            reduction_percent=round((1-visible_length/contract['body_length_before'])*100,1)),deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','changed_assets','added_assets','preserved_assets','article_checks']},ensure_ascii=False))

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    build(args.baseline,args.output)
