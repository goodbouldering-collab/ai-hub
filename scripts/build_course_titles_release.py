"""Apply the two configured course names to a verified published baseline."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, os

ROOT=Path(__file__).resolve().parents[1]
def hashes(root):
 return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def build(baseline, output):
 v=json.loads((baseline/'verification.json').read_text(encoding='utf8'))
 before=hashes(baseline/'public');assert before==v['assets']
 document=(baseline/'public/index.html').read_bytes().decode('utf8')
 old_names=['AI動画制作・投稿自動化講座','AI音声メモ講座｜録音を仕事の記録に変える']
 names=[json.loads((ROOT/f'config/{f}.json').read_text(encoding='utf8'))['name'] for f in ('reel-course','voice-memo-course')]
 original=document
 for old,new in zip(old_names,names):
  assert old in document, old
  document=document.replace(old,new)
 document=document.replace('AI音声メモ講座を予約','AI録音講座を予約')
 for old,new in zip(old_names,names):assert old not in document and new in document
 assert original.count('href=')==document.count('href=')
 assert not output.exists()
 for p in (baseline/'public').rglob('*'):
  if p.is_file():
   target=output/'public'/p.relative_to(baseline/'public');target.parent.mkdir(parents=True,exist_ok=True)
   if p.name=='index.html' and p.parent==baseline/'public':target.write_bytes(document.encode('utf8'))
   else:shutil.copy2(p,target)
 (output/'runtime').mkdir()
 worker=ROOT/'deployment/meo-diagnosis/published-worker.mjs'
 worker_bytes=subprocess.check_output(['git','show','HEAD:deployment/meo-diagnosis/published-worker.mjs'],cwd=ROOT)
 assert hashlib.sha256(worker_bytes).hexdigest()==v['worker_sha256']
 (output/'runtime/published-worker.mjs').write_bytes(worker_bytes)
 after=hashes(output/'public');changed=[n for n in before if before[n]!=after[n]]
 assert changed==['index.html'] and before.keys()==after.keys()
 report=dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),assets=after,changed_assets=changed,unchanged_assets=len(before)-1,worker_sha256=v['worker_sha256'],names=names)
 (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='assets'},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.baseline,a.output)
