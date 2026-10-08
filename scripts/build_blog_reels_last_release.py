"""Relocate the six published blog videos, preserving all other release bytes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.blog_video_order import move_leading_videos

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def hashes(p):
    return {f.relative_to(p).as_posix(): digest(f) for f in sorted(p.rglob('*')) if f.is_file()}

def build(baseline, output):
    contract = json.loads((ROOT/'deployment/blog-reels-last.json').read_text(encoding='utf-8'))
    assert digest(baseline/'verification.json') == contract['verification_sha256']
    previous = json.loads((baseline/'verification.json').read_text(encoding='utf-8'))
    assert previous['source_sha'] == contract['source_sha']
    assert hashes(baseline/'public') == previous['assets']
    assert output.is_relative_to(ROOT) and not output.exists()
    changed = []
    for relative in previous['assets']:
        source, dest = baseline/'public'/relative, output/'public'/relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if relative.startswith('blog/') and relative.endswith('.html'):
            original = data.decode('utf-8')
            updated = move_leading_videos(original)
            if updated != original:
                before, after = [BeautifulSoup(h,'html.parser') for h in (original,updated)]
                assert [str(v) for v in before.select('video')] == [str(v) for v in after.select('video')]
                assert [str(v) for v in before.select('img')] == [str(v) for v in after.select('img')]
                for soup in (before,after):
                    for video in soup.select('.content-wrap video'):
                        parent = video.parent
                        if parent.name in ('figure','div'): parent.extract()
                        else: video.extract()
                    for tag in soup.select('script,style'): tag.extract()
                    for p in soup.select('p'):
                        if p.get_text() == 'まずは約49秒の動画で、結論をつかんでください。': p.extract()
                assert before.get_text(' ',strip=True) == after.get_text(' ',strip=True)
                assert move_leading_videos(updated) == updated
                data=updated.encode('utf-8'); changed.append(relative)
        if relative in changed: dest.write_bytes(data)
        else: os.link(source,dest)
    assert len(changed)==6, changed
    worker=ROOT/'deployment/ai-news/published-worker.mjs'
    assert digest(worker)==previous['worker_sha256']
    shutil.copyfile(worker,output/'published-worker.mjs')
    assert hashes(baseline/'public')==previous['assets']
    result=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                assets=hashes(output/'public'), changed_assets=changed,
                worker_sha256=digest(worker), baseline_unchanged=True)
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changed_assets':changed,'unchanged_assets':len(result['assets'])-len(changed)},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    build(args.baseline.resolve(),args.output.resolve())
