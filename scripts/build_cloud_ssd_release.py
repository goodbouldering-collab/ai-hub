"""Add one article to a verified immutable release without changing other pages."""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'site')]
from core.studio_design import decorate_html
from core.home_updates import latest_published_posts
SLUG = '2026-10-05-codex-cloud-development-environment'
ORIGIN = 'https://aiclimb.aiclimb.workers.dev'
CONTRACT = ROOT / 'deployment/cloudflare-blog/cloud-ssd-20261005.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def hashes(p):
    return {f.relative_to(p).as_posix(): digest(f) for f in sorted(p.rglob('*')) if f.is_file()}

def build(baseline, output):
    baseline, output = baseline.resolve(), output.resolve()
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    before = hashes(baseline)
    assert before == contract['assets'], 'Baseline drift; recheck production'
    assert digest(ROOT/'deployment/ai-news/published-worker.mjs') == contract['worker_sha256']
    assert output.is_relative_to(ROOT) and not output.exists()
    spec = importlib.util.spec_from_file_location('decision_site', ROOT/'site/build_site.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    source = ROOT/f'content/blog/{SLUG}.md'
    meta, body = builder._parse_frontmatter(source.read_text(encoding='utf-8'))
    assert meta['authorship_note'] == '※内容は運営者が考え、AIで整えています。'
    assert meta['status'] == 'published'
    path = f'blog/{SLUG}.html'
    assert path not in before
    rendered = builder._load_markdown().markdown(body, extensions=['extra','sane_lists','attr_list'])
    page = decorate_html(builder.render_content_page(str(meta['title']),meta,rendered,
        builder.render_top_nav(path_prefix='../',current_id='blog',include_run=False),page_path=path,kind='blog'))
    page = page.replace(f'{ORIGIN}/{path}', f'{ORIGIN}/blog/{SLUG}')
    soup = BeautifulSoup(page,'html.parser')
    # This short personal story does not need an auto-generated table of contents.
    toc = soup.select_one('.content-toc')
    assert toc is not None
    toc.decompose()
    page = str(soup)
    content = soup.select_one('.content-wrap')
    h2 = content.select('h2')
    assert len(h2)==4 and all(h.find_next_sibling().name=='figure' for h in h2)
    images=content.select('img')
    assert len(images)==5 and len({i['src'] for i in images})==5
    assert soup.h1.get_text()==meta['title']
    note=soup.select_one('main > p')
    assert note.get_text()==meta['authorship_note'] and not note.attrs
    assert soup.select_one('link[rel="canonical"]')['href']==f'{ORIGIN}/blog/{SLUG}'
    assert soup.select_one('meta[property="og:image"]')['content']==ORIGIN+meta['image']
    assert json.loads(soup.select_one('script[type="application/ld+json"]').string)['headline']==meta['title']
    assert not soup.select('[contenteditable],meta[name="robots"][content*="noindex"]')
    assert [h.get('id') for h in h2] == ['hardware','cloud','github','resale']
    assert 'GitHubを経由して、開発環境のコピーや移動も自動化できる。' in content.get_text()
    assert 'またオークションに出品している。' in content.get_text()
    assert '熱伝導パッドの厚みを調べていた。' in content.get_text()
    assert 'パスワードやAPIキーはGitHubに入れず' in content.get_text()
    assert soup.select_one('a[href="/#contact"]')
    assert len(content.select('details')) == 1
    assert len(content.select('a[href^="https://learn.chatgpt.com/"]')) >= 2
    assert content.find(recursive=False).name == 'figure'
    assert content.select_one('figure img')['src'] == meta['image']
    mutable={'index.html','blog/index.html','sitemap.xml'}
    for rel in before:
        src,dest=baseline/rel,output/'public'/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        if rel in mutable: shutil.copyfile(src,dest)
        else: os.link(src,dest)
    page = page.replace('</head>', '<style>.content-wrap table{display:block;max-width:100%;overflow-x:auto}.content-wrap th,.content-wrap td{min-width:9em}.content-wrap pre{max-width:100%;overflow-x:auto;white-space:pre}.content-wrap figure{margin:20px 0 28px}.content-wrap figure img{display:block;width:100%;height:auto;border-radius:12px}.content-wrap figcaption{font-size:.88rem;color:#526273;line-height:1.6}.content-wrap h2{scroll-margin-top:90px}.content-wrap a{overflow-wrap:anywhere}</style></head>', 1)
    (output/'public'/path).write_text(page,encoding='utf-8',newline='\n')
    image_inputs=[]
    for i in images:
        rel=i['src'].lstrip('/')
        assert rel.startswith('img/blog-cloud-ssd-') and '..' not in rel and i.get('alt')
        p=ROOT/'site/static'/rel
        with Image.open(p) as bitmap:
            assert bitmap.width>bitmap.height
            bitmap.verify()
        assert rel not in before
        os.link(p,output/'public'/rel)
        image_inputs.append(p)
    title,summary,date=[html.escape(str(meta[k]),quote=True) for k in ('title','summary','date')]
    card=f'<a class="tr-card" href="./{SLUG}.html"><div class="tr-title">{title}</div><div class="tr-date">{date}</div><div class="tr-sum">{summary}</div></a>'
    index=(baseline/'blog/index.html').read_text(encoding='utf-8')
    marker="<div class='tr-grid'>"
    assert index.count(marker)==1
    index=index.replace(marker,marker+card,1)
    (output/'public/blog/index.html').write_text(index,encoding='utf-8',newline='\n')
    # Replace only the two latest-blog rows; preserve news, layout and CSS byte for byte.
    home=(baseline/'index.html').read_text(encoding='utf-8')
    pattern=r'(<div id="blog" class="home-updates__blog".*?<ol>)(.*?)(</ol></div>)'
    matches=list(re.finditer(pattern,home,re.S))
    assert len(matches)==1
    rows=''.join(f'<li><a href="{p["href"]}" title="{html.escape(p["title"],quote=True)}"><time datetime="{p["date"]}">{p["date"].replace("-",".")}</time><span>{html.escape(p["title"])}</span><b aria-hidden="true">↗</b></a></li>' for p in latest_published_posts(index))
    assert SLUG in rows
    m=matches[0]
    updated=home[:m.start(2)]+rows+home[m.end(2):]
    assert updated.replace(rows,m[2],1)==home
    (output/'public/index.html').write_text(updated,encoding='utf-8',newline='\n')
    sitemap=(baseline/'sitemap.xml').read_text(encoding='utf-8')
    assert sitemap.count('</urlset>')==1 and SLUG not in sitemap
    entry=f'  <url><loc>{ORIGIN}/blog/{SLUG}</loc><lastmod>{date}</lastmod><priority>0.7</priority></url>\n'
    sitemap=sitemap.replace('</urlset>',entry+'</urlset>')
    ET.fromstring(sitemap)
    (output/'public/sitemap.xml').write_text(sitemap,encoding='utf-8',newline='\n')
    after=hashes(output/'public')
    changed=sorted(n for n in before if after[n]!=before[n])
    added=sorted(after.keys()-before.keys())
    assert changed==sorted(mutable) and len(added)==6
    assert hashes(baseline)==before
    paths=[CONTRACT,Path(__file__).resolve(),source,*image_inputs,ROOT/'deployment/ai-news/published-worker.mjs',ROOT/'cloudflare-runtime/wrangler-profile-release.jsonc']
    for mod in list(sys.modules.values()):
        file=getattr(mod,'__file__',None)
        if file:
            p=Path(file).resolve()
            if p.is_file() and p.is_relative_to(ROOT) and p.relative_to(ROOT).parts[0] in {'core','site','scripts'} and p.suffix=='.py': paths.append(p)
    paths.extend(p for p in (ROOT/'config').glob('*') if p.is_file())
    inputs={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(set(paths))}
    dirty=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*inputs],cwd=ROOT,text=True).splitlines()
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_inputs=inputs,inputs=list(inputs),source_inputs_clean=not dirty,source_input_status=dirty,assets=after,changed_assets=changed,added_assets=added,preserved_assets=len(before)-3,baseline_unchanged=True,worker_sha256=contract['worker_sha256'],baseline_version=contract['cloudflare_version'],article_checks=dict(h2=4,images=5,authorship_note=True,canonical=True,jsonld=True,index_links=True,sitemap=True),deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','changed_assets','added_assets','preserved_assets','article_checks']},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    build(args.baseline,args.output)
