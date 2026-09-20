"""Refresh owned artwork and Instagram only in an exact published snapshot."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.instagram_feed import apply_instagram_feed, strip_instagram_feed
NAMES = 'hero agent personal code support salon site mentor profile prepare try keep login'.split()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(root): return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
def build(baseline, output):
    contract_path = ROOT/'deployment/editorial/cool-line-baseline.json'
    contract = json.loads(contract_path.read_text(encoding='utf-8-sig'))
    assert digest(baseline/'verification.json') == contract['verification_sha256'], 'Baseline manifest changed'
    old = json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha'] == contract['source_sha'] and old['source_inputs_clean']
    assert hashes(baseline/'public') == old['assets']
    assert hashes(baseline/'runtime') == old['runtime']
    assert output.resolve().is_relative_to(ROOT) and not output.exists()
    shutil.copytree(baseline/'public', output/'public')
    shutil.copytree(baseline/'runtime', output/'runtime')
    original = (baseline/'public/index.html').read_text(encoding='utf-8')
    updated = apply_instagram_feed(original)
    assert strip_instagram_feed(updated) == strip_instagram_feed(original)
    assert apply_instagram_feed(updated) == updated
    from bs4 import BeautifulSoup
    feed = BeautifulSoup(updated, 'html.parser').select_one('#instagram')
    assert not feed.get_text(strip=True) and not feed.select('iframe,button,h2,h3,p')
    assert len(feed.select('a > img')) == 6
    (output/'public/index.html').write_text(updated,encoding='utf-8',newline='\n')
    owned = [f'design-system/studio/images/soft-{n}.webp' for n in NAMES] + ['instagram-feed.css','instagram-feed.js']
    config = json.loads((ROOT/'config/instagram.json').read_text(encoding='utf-8'))
    additions = [f'instagram/{p["shortcode"]}.webp' for p in config['posts']]
    for name in owned+additions:
        dest = output/'public'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'site/static'/name,dest)
    assets, runtime = hashes(output/'public'), hashes(output/'runtime')
    changed = sorted(p for p in assets if p in old['assets'] and assets[p]!=old['assets'][p])
    assert set(changed) == set(owned+['index.html'])
    assert set(assets)-set(old['assets']) == set(additions)
    assert not set(old['assets'])-set(assets) and runtime==old['runtime']
    assert len({assets[f'design-system/studio/images/soft-{n}.webp'] for n in NAMES})==13
    sources = ['scripts/build_cool_line_release.py','core/instagram_feed.py','config/instagram.json',
        'deployment/editorial/cool-line-baseline.json','cloudflare-runtime/wrangler-profile-release.jsonc',
        'cloudflare-runtime/wrangler-glass-build.jsonc','deployment/profile/package.json','deployment/profile/package-lock.json']
    sources += ['site/static/'+n for n in owned+additions]
    inputs = {p:digest(ROOT/p) for p in sources}
    status = subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    sha = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result = dict(source_sha=sha,source_inputs=inputs,source_inputs_clean=not status,source_input_status=status,
        baseline_source_sha=old['source_sha'],baseline_version=contract['cloudflare_version'],
        assets=assets,runtime=runtime,changed_assets=changed,added_assets=additions,
        unchanged_assets=len(old['assets'])-len(changed),deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','changed_assets','added_assets','unchanged_assets']},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.baseline.resolve(),a.output.resolve())
