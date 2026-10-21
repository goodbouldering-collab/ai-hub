"""Update only the video course and its schema on a pinned public release."""
from pathlib import Path
import argparse, hashlib, json, os, re, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.reel_course import apply_reel_course, START, END, course_data

from bs4 import BeautifulSoup

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def transform(html):
    return apply_reel_course(html)


def build(baseline,output,sha):
    contract=json.loads((ROOT/'deployment/ai-video-course/baseline.json').read_text(encoding='utf8'))
    assert hashes(baseline)==contract['assets'],'Baseline mismatch'
    assert not output.exists(),'Use fresh output'
    before=(baseline/'index.html').read_bytes().decode('utf8');after=transform(before)
    assert transform(after)==after
    old,new=[BeautifulSoup(x,'html.parser') for x in (before,after)]
    def without_course(text):
        text=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',text,flags=re.S)
        return re.sub(r'<script id="reel-course-schema".*?</script>','',text,flags=re.S)
    assert without_course(before)==without_course(after),'Unrelated homepage content changed'
    card=new.select_one('#reel-course')
    assert card.select_one('h3').get_text()==course_data()['name']
    assert card.select_one('button[disabled]').get_text()=='準備中'
    assert not card.select('a[href*="squareup.com"]')
    assert '8,800円（税込）' in card.get_text() and '120分' in card.get_text()
    schema=json.loads(new.select_one('#reel-course-schema').string)
    assert 'offers' not in schema
    assert new.select_one('#reel-course img')['src']==old.select_one('#reel-course img')['src']
    for name in contract['assets']:
        dest=output/'public'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if name=='index.html':dest.write_bytes(after.encode('utf8'))
        else:os.link(baseline/name,dest)
    assets=hashes(output/'public');changed=sorted(k for k in assets if assets[k]!=contract['assets'][k])
    assert changed==['index.html']
    worker=(ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n',b'\n')
    digest=hashlib.sha256(worker).hexdigest();assert digest==contract['worker_sha256']
    result=dict(source_sha=sha,assets=assets,changed_assets=changed,unchanged_assets=len(assets)-1,worker_sha256=digest)
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='assets'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-sha',required=True);a=p.parse_args();build(a.baseline,a.output,a.source_sha)

