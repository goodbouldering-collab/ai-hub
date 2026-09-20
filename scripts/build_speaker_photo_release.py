"""Restore only the selected speaker photo over the verified warm-line release."""
from pathlib import Path
import argparse,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.art_direction import decorate_art_direction,PORTRAIT
from build_warm_line_release import digest,hashes

BASELINE_SHA='5c3b88c703fa9c0588c4492b879724039bb6e5cb'
BASELINE_MANIFEST='4f797bd8834957305575b7948433724b71edd77fe61b35321cd53136c38f7f03'
BASELINE_BUNDLE='baab871b7ffa55b70f49098d155bc7dfaad96cedb0fc5742334b9dbe9f305506'
PHOTO_SHA='35e6083eecd6c86c7e12f5ec460d516d518c1981cadc90c63dd47aaaeaf311f7'

def build(baseline,output):
    assert digest(baseline/'verification.json')==BASELINE_MANIFEST
    old=json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert old['source_sha']==BASELINE_SHA and old['source_inputs_clean']
    assert hashes(baseline/'public')==old['assets']
    assert hashes(baseline/'runtime')==old['runtime']
    assert digest(baseline/'compiled/public-entry.js')==BASELINE_BUNDLE
    photo=PORTRAIT.lstrip('/')
    assert digest(ROOT/'site/static'/photo)==old['assets'][photo]==PHOTO_SHA
    assert output.is_relative_to(ROOT) and not output.exists()
    for folder in ['public','runtime']:shutil.copytree(baseline/folder,output/folder)
    (output/'compiled').mkdir()
    shutil.copyfile(baseline/'compiled/public-entry.js',output/'compiled/public-entry.js')
    pages=['index.html','speaker.html']
    for page in pages:
        p=output/'public'/page
        before=p.read_text(encoding='utf-8')
        after=decorate_art_direction(before)
        # One owned image tag per page; all other bytes of HTML remain unchanged.
        tag_pattern=r'<img\b[^>]*src="/img/speaker-anime\.png"[^>]*>'
        matches=list(re.finditer(tag_pattern,before))
        assert len(matches)==1,page
        tag=matches[0][0]
        expected=tag.replace('/img/speaker-anime.png',PORTRAIT).replace('AI相談講師 由井辰美のイラストポートレート','AI相談講師 由井辰美の水彩風ポートレート').replace('height="1536"','height="1254"').replace('width="1024"','width="1254"')
        expected=expected[:-1]+' style="object-fit:cover!important">'
        assert after==before.replace(tag,expected) and after!=before
        assert decorate_art_direction(after)==after
        p.write_text(after,encoding='utf-8',newline='\n')
    assets=hashes(output/'public')
    assert set(assets)==set(old['assets'])
    assert {p for p in assets if assets[p]!=old['assets'][p]}==set(pages)
    assert hashes(output/'runtime')==old['runtime']
    sources=['core/art_direction.py','scripts/build_speaker_photo_release.py','scripts/build_warm_line_release.py','core/instagram_feed.py','config/instagram.json','site/static/'+photo,'cloudflare-runtime/wrangler-profile-release.jsonc']
    inputs={p:digest(ROOT/p) for p in sources}
    status=subprocess.check_output(['git','-c','core.excludesFile=','status','--porcelain','--',*sources],cwd=ROOT,text=True).splitlines()
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=dict(source_sha=sha,source_inputs=inputs,source_inputs_clean=not status,source_input_status=status,baseline_source_sha=BASELINE_SHA,baseline_version='7984ba41-86f0-4b28-9b45-0facad4721fe',assets=assets,runtime=old['runtime'],compiled_sha256=BASELINE_BUNDLE,changed_assets=pages,added_assets=[],unchanged_assets=len(assets)-2,changed_runtime=[],photo=PORTRAIT,photo_sha256=PHOTO_SHA,deployed=False)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['source_sha','source_inputs_clean','changed_assets','unchanged_assets','photo']},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.baseline.resolve(),a.output.resolve())
