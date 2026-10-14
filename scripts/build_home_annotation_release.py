"""Apply the approved lead copy and news thumbnail to verified public assets."""
from pathlib import Path
import argparse, hashlib, json, os, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.hero_copy import apply_hero_copy
from core.editorial_feed import integrate_home_news, apply_blog_feed, _news_date, _style

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def build(baseline, output, sha):
    contract = json.loads((ROOT/'deployment/home-copy-news-image/baseline.json').read_text(encoding='utf8'))
    assert hashes(baseline) == contract['assets'], 'Production baseline changed'
    assert not output.exists(), 'Use a fresh output directory'
    css = (ROOT/'site/templates/ai-news/editorial-feed.css').read_text(encoding='utf8')
    home = (baseline/'index.html').read_text(encoding='utf8')
    home = _style(integrate_home_news(apply_hero_copy(home)), css)
    blog = apply_blog_feed((baseline/'blog/index.html').read_text(encoding='utf8'), _news_date(home), css)
    assert _style(integrate_home_news(apply_hero_copy(home)), css) == home
    assert apply_blog_feed(blog, _news_date(home), css) == blog
    for name in contract['assets']:
        dest = output/'public'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if name in ('index.html','blog/index.html'):
            dest.write_text(home if name == 'index.html' else blog, encoding='utf8', newline='\n')
        else:
            os.link(baseline/name, dest)  # Untouched assets remain immutable.
    assets = hashes(output/'public')
    changed = sorted(k for k in assets if assets[k] != contract['assets'][k])
    assert changed == ['blog/index.html','index.html'], changed
    worker = (ROOT/'deployment/admin-workspace/published-worker.mjs').read_bytes().replace(b'\r\n',b'\n')
    digest = hashlib.sha256(worker).hexdigest()
    assert digest == contract['worker_sha256'], 'Admin Worker changed'
    result = dict(source_sha=sha,assets=assets,changed_assets=changed,unchanged_assets=len(assets)-2,worker_sha256=digest)
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k != 'assets'}))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-sha',required=True)
    args=parser.parse_args()
    build(args.baseline,args.output,args.source_sha)
