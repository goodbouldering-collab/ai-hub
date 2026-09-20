"""Build the warm line-art release from the verified production snapshot."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.instagram_feed import apply_instagram_feed,strip_instagram_feed
from core.art_direction import decorate_art_direction,LESSONS,EDITORIAL_VERSION,PORTRAIT
NAMES='hero agent personal code support salon site prepare try keep login'.split()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(root):return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
def normalize(text):
    text=re.sub(r'(editorial\.css\?v=)[a-zA-Z0-9-]+',r'\1VERSION',text)
    return re.sub(r'<img\b[^>]*>','<IMAGE>',text)
def build(baseline,output):
    contract_path=ROOT/'deployment/editorial/warm-line-baseline.json'
    contract=json.loads(contract_path.read_text(encoding='utf-8-sig'))
    assert digest(baseline/'verification.json')==contract['verification_sha256']
    old=json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha']==contract['source_sha'] and old['source_inputs_clean']
    assert hashes(baseline/'public')==old['assets'] and hashes(baseline/'runtime')==old['runtime']
    assert output.resolve().is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline/'public',output/'public');shutil.copytree(baseline/'runtime',output/'runtime')
    changed_html=[]
    for p in (output/'public').rglob('*.html'):
        before=p.read_text(encoding='utf-8');after=decorate_art_direction(before)
        if p.name=='index.html' and p.parent==output/'public':after=apply_instagram_feed(after)
        assert normalize(strip_instagram_feed(before))==normalize(strip_instagram_feed(after)),f'Content changed: {p}'
        assert decorate_art_direction(after)==after
        if before!=after:
            p.write_text(after,encoding='utf-8',newline='\n');changed_html.append(p.relative_to(output/'public').as_posix())
    runtime_changed=[]
    for p in (output/'runtime').rglob('*.mjs'):
        before=p.read_text(encoding='utf-8')
        after=re.sub(r'(editorial\.css\?v=)[a-zA-Z0-9-]+',lambda m:m[1]+EDITORIAL_VERSION,before)
        if before!=after:
            p.write_text(after,encoding='utf-8',newline='\n');runtime_changed.append(p.relative_to(output/'runtime').as_posix())
    assert set(runtime_changed)=={'worker/admin-assets.generated.mjs','worker/login-page.mjs'},runtime_changed
    owned=[f'design-system/studio/images/soft-{n}.webp' for n in NAMES]+['design-system/studio/editorial.css','instagram-feed.css']
    additions=[f'design-system/studio/images/{name}.webp' for name,_ in LESSONS.values()]
    for name in owned+additions:
        shutil.copyfile(ROOT/'site/static'/name,output/'public'/name)
    assert digest(ROOT/'site/static'/PORTRAIT.lstrip('/'))==old['assets'][PORTRAIT.lstrip('/')], 'Original portrait must remain untouched'
    assets,runtime=hashes(output/'public'),hashes(output/'runtime')
    changed=sorted(p for p in assets if p in old['assets'] and assets[p]!=old['assets'][p])
    assert set(changed)==set(owned+changed_html)
    assert set(assets)-set(old['assets'])==set(additions) and not set(old['assets'])-set(assets)
    assert {p for p in runtime if runtime[p]!=old['runtime'][p]}==set(runtime_changed)
    from bs4 import BeautifulSoup
    for page in ['index.html','speaker.html']:
        soup=BeautifulSoup((output/'public'/page).read_text(encoding='utf-8'),'html.parser')
        assert len(soup.select('img[src="'+PORTRAIT+'"]'))==1
    soup=BeautifulSoup((output/'public/index.html').read_text(encoding='utf-8'),'html.parser')
    assert len(soup.select('#lecture-carousel img[src^="/design-system/studio/images/lesson-"]'))==7
    assert soup.select_one('#instagram').get_text(strip=True)=='Instagram'
    sources=['core/instagram_feed.py','config/instagram.json','scripts/verify_warm_line_live.py','scripts/build_warm_line_release.py','core/art_direction.py','core/studio_design.py','deployment/editorial/warm-line-baseline.json','cloudflare-runtime/wrangler-profile-release.jsonc','cloudflare-runtime/wrangler-glass-build.jsonc','deployment/profile/package.json','deployment/profile/package-lock.json','site/static'+PORTRAIT]
    sources+=['site/static/'+n for n in owned+additions]
    inputs={p:digest(ROOT/p) for p in sources}
    status=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=dict(source_sha=sha,source_inputs=inputs,source_inputs_clean=not status,source_input_status=status,baseline_source_sha=old['source_sha'],baseline_version=contract['cloudflare_version'],assets=assets,runtime=runtime,changed_assets=changed,added_assets=additions,changed_runtime=runtime_changed,unchanged_assets=len(old['assets'])-len(changed),original_portrait_preserved=True,deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','changed_runtime','unchanged_assets','original_portrait_preserved']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();build(a.baseline.resolve(),a.output.resolve())
