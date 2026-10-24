"""Add the recording customer timeline article to a hash-pinned public baseline."""
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'site')]
READ_INPUTS = set()
def record_read(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        try:
            path = Path(args[0]).resolve()
            if path.is_file() and path.is_relative_to(ROOT):
                READ_INPUTS.add(path.relative_to(ROOT).as_posix())
        except (OSError, ValueError, TypeError):
            pass
sys.addaudithook(record_read)
from core.studio_design import decorate_html
from core.editorial_feed import _ElementSpans, _row, _config
SLUG = '2026-10-24-recording-customer-timeline'
ORIGIN = 'https://aiclimb.aiclimb.workers.dev'
def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
def build(baseline, output, require_clean=False):
    contract=json.loads((ROOT/'deployment/recording-customer-timeline/baseline.json').read_text(encoding='utf8'))
    before=hashes(baseline)
    assert before == contract['assets'], 'Baseline drift'
    assert not output.exists()
    spec=importlib.util.spec_from_file_location('article_builder',ROOT/'site/build_site.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    meta,body=builder._parse_frontmatter((ROOT/f'content/blog/{SLUG}.md').read_text(encoding='utf8'))
    assert meta['status']=='published'
    assert 'AIエージェント講習を一度以上受講された方' in body
    assert 'またはCodexを十分に使いこなせる方' in body
    assert '2時間の個別講習' in body
    route=f'blog/{SLUG}.html'
    assert route not in before
    page=decorate_html(builder.render_content_page(str(meta['title']),meta,builder._load_markdown().markdown(body,extensions=['extra','sane_lists','attr_list']),builder.render_top_nav(path_prefix='../',current_id='blog',include_run=False),page_path=route,kind='blog'))
    soup=BeautifulSoup(page,'html.parser')
    assert soup.h1.get_text()==meta['title']
    assert soup.select_one('main > p').get_text()=='※内容は運営者が考え、AIで整えています。'
    assert not soup.select_one('main > p').attrs
    assert soup.select_one('link[rel="canonical"]')['href']==f'{ORIGIN}/{route}'
    headings=soup.select('.content-wrap h2');assert len(headings)==3
    assert all(h.find_next_sibling().name=='figure' for h in headings)
    images=soup.select('.content-wrap img');assert len(images)==4
    assert len({i['src'] for i in images})==4
    owned={'index.html','blog/index.html','sitemap.xml'}
    for rel in before:
        dest=output/'public'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if rel in owned:shutil.copyfile(baseline/rel,dest)
        else:shutil.copyfile(baseline/rel,dest)
    (output/'public'/route).write_text(page,encoding='utf8',newline='\n')
    for img in images:
        rel=img['src'].lstrip('/');assert rel.startswith('img/recording-customer-timeline-') and img.get('alt')
        src=ROOT/'site/static'/rel
        with Image.open(src) as im:assert im.width>im.height;im.verify()
        shutil.copyfile(src,output/'public'/rel)
    post={k:str(meta[k]) for k in ['title','summary','date']};post['href']='/'+route
    for rel in ['index.html','blog/index.html']:
        original=(baseline/rel).read_text(encoding='utf8')
        spans=_ElementSpans(original,class_name='editorial-feed__list').spans
        assert len(spans)==1
        a,b=spans[0];block=original[a:b]
        items=_ElementSpans(block,class_name='editorial-feed__item').spans
        assert items and 'editorial-feed__news' in block[items[0][0]:items[0][1]]
        rows=[block[x:y] for x,y in items]
        assert SLUG not in block
        if rel=='index.html':
            assert len(rows)==4
            rows=rows[:1]+[_row(post,_config(),include_summary=False)]+rows[1:3]
        else:rows=rows[:1]+[_row(post,_config(),heading_level=2)]+rows[1:]
        new=block[:items[0][0]]+''.join(rows)+block[items[-1][1]:]
        updated=original[:a]+new+original[b:]
        (output/'public'/rel).write_text(updated,encoding='utf8',newline='\n')
        assert len(BeautifulSoup(updated,'html.parser').select(f'a[href="/{route}"]'))==1
    original=(baseline/'sitemap.xml').read_text(encoding='utf8');assert original.count('</urlset>')==1
    (output/'public/sitemap.xml').write_text(original.replace('</urlset>',f'<url><loc>{ORIGIN}/{route}</loc><lastmod>2026-10-24</lastmod></url>\n</urlset>'),encoding='utf8',newline='\n')
    assets=hashes(output/'public');changed=sorted(k for k in before if assets[k]!=before[k])
    assert changed==sorted(owned) and len(assets)-len(before)==5
    assert hashes(baseline)==before
    worker=(ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(worker).hexdigest()==contract['worker_sha256']
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),assets=assets,changed_assets=changed,added_assets=sorted(set(assets)-set(before)),preserved_assets=len(before)-3,worker_sha256=contract['worker_sha256'],article_checks=dict(h2=3,images=4,canonical=True,authorship_note=True))
    for module in list(sys.modules.values()):
        source=getattr(module,'__file__',None)
        if source:
            path=Path(source).resolve()
            if path.is_file() and path.is_relative_to(ROOT): READ_INPUTS.add(path.relative_to(ROOT).as_posix())
    tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True,encoding='utf8').splitlines())
    inputs=sorted((READ_INPUTS & tracked) | {f'content/blog/{SLUG}.md', 'scripts/build_recording_customer_timeline_release.py', 'site/build_site.py', 'deployment/recording-customer-timeline/baseline.json', 'deployment/admin-workspace/published-worker.mjs', 'cloudflare-runtime/wrangler-profile-release.jsonc'} | {i['src'].lstrip('/') and 'site/static/'+i['src'].lstrip('/') for i in images})
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*inputs],cwd=ROOT,text=True,encoding='utf8').strip()
    if require_clean: assert not dirty, 'Uncommitted build inputs: '+dirty
    result['inputs']=inputs
    result['inputs_clean']=not bool(dirty)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='assets'},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--require-clean',action='store_true');args=p.parse_args();build(args.baseline.resolve(),args.output.resolve(),args.require_clean)
