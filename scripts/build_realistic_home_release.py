"""Create the image-led homepage from a verified release, keeping every other asset."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261004-realistic'
PREFIX = '/design-system/studio/images/'
CSS = 'design-system/studio/realistic-home.css'
PHOTOS = {
    'hero': ('cafe', '店主と相談員がコーヒーの写真から告知を作る場面。AI生成の架空の活用イメージ'),
    'agent': ('workshop', '参加者がパソコンを使いながらAIを学ぶ場面。AI生成の架空の活用イメージ'),
    'personal': ('organize', '店主が相談員とノートや予定を整理する場面。AI生成の架空の活用イメージ'),
    'code': ('build', 'パソコンとスマートフォンで予約サイトを確認する場面。AI生成の架空の活用イメージ'),
    'support': ('organize', '仕事の手順を相談し、週間予定にまとめる場面。AI生成の架空の活用イメージ'),
    'site': ('build', '店舗の予約ページを一緒に確認する場面。AI生成の架空の活用イメージ'),
}
NOTE = '<figcaption class="realistic-image-note">写真はAIで作成した活用イメージです。</figcaption>'
OWNED = [CSS] + ['design-system/studio/images/realistic-' + n + '-20261004.webp' for n in ['cafe', 'workshop', 'build', 'organize']]
INPUTS = ['scripts/build_realistic_home_release.py', 'deployment/realistic-home/baseline.json', 'site/templates/ai-news/home.html', 'docs/design/realistic-home-20261004.md', 'docs/design/realistic-home-20261004-prompts.json', 'deployment/ai-news/published-worker.mjs', 'cloudflare-runtime/wrangler-profile-release.jsonc'] + ['site/static/' + p for p in OWNED]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def hashes(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

def attr(tag, key, value):
    return re.sub(r'\b' + key + r'=([\"\']).*?\1', lambda _: key + '="' + value + '"', tag, count=1)

def transform(document):
    document = re.sub(r'<link\b[^>]*id="realistic-home-style"[^>]*>\s*', '', document)
    document = document.replace(NOTE, '')
    document = re.sub(r'(<body\b[^>]*class=")([^"]+)(")', lambda m: m[1] + ' '.join(c for c in m[2].split() if c != 'realistic-home') + ' realistic-home' + m[3], document, count=1)
    def image(match):
        tag = match[0]
        for name, (photo, alt) in PHOTOS.items():
            if re.search(r'/soft-' + name + r'\.webp(?:\?[^\"\']*)?[\"\']', tag):
                tag = attr(tag, 'src', PREFIX + 'realistic-' + photo + '-20261004.webp')
                return attr(tag, 'alt', alt)
        return tag
    document = re.sub(r'<img\b[^>]*>', image, document)
    document, count = re.subn(r'(<figure\b[^>]*id="restored-hero-image"[^>]*>.*?)(</figure>)', lambda m: m[1] + NOTE + m[2], document, count=1, flags=re.S)
    assert count == 1, 'Expected one homepage hero'
    return document.replace('</head>', '<link id="realistic-home-style" rel="stylesheet" href="/' + CSS + '?v=' + VERSION + '">\n</head>')

class Content(HTMLParser):
    def __init__(self, document):
        super().__init__(); self.text = []; self.skip = 0; self.links = []; self.ids = []; self.feed(document)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'a': self.links.append(a.get('href'))
        if 'id' in a and a['id'] != 'realistic-home-style': self.ids.append(a['id'])
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
    def handle_data(self, data):
        if not self.skip and data.strip(): self.text.append(data.strip())

def verify_content(before, after):
    a = Content(before); b = Content(after.replace(NOTE, ''))
    assert a.text == b.text, 'Page copy changed'
    assert a.links == b.links, 'Link destinations changed'
    assert a.ids == b.ids, 'Page anchors or controls changed'
    for tag in ('form', 'script'):
        pattern = r'<' + tag + r'\b[^>]*>.*?</' + tag + '>'
        assert re.findall(pattern, before, re.S) == re.findall(pattern, after, re.S), tag + ' changed'
    assert transform(after) == after, 'Design transform must be idempotent'
    assert len(re.findall(r'/realistic-[a-z]+-20261004.webp', after)) == 6

def build(baseline, output, live=False):
    contract = json.loads((ROOT / 'deployment/realistic-home/baseline.json').read_text(encoding='utf-8'))
    assert sha(baseline / 'verification.json') == contract['verification_sha256']
    prior = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    assets = hashes(baseline / 'public')
    assert assets == prior['assets'], 'Baseline assets were changed'
    assert sha(ROOT / 'deployment/ai-news/published-worker.mjs') == prior['worker_sha256']
    if live:
        for name in ['index.html', 'ai-news/index.html', 'design-system/studio/editorial.css', 'design-system/studio/images/soft-hero.webp']:
            route = {'index.html':'', 'ai-news/index.html':'ai-news/'}.get(name, name)
            # Use the same Node HTTPS stack as the project's Cloudflare tooling.
            script = "const c=require('node:crypto');fetch(process.argv[1],{signal:AbortSignal.timeout(40000)}).then(async r=>console.log(JSON.stringify({status:r.status,sha:c.createHash('sha256').update(Buffer.from(await r.arrayBuffer())).digest('hex')}))).catch(e=>{console.error(e.message);process.exit(1)})"
            response = json.loads(subprocess.check_output(['node','-e',script,'https://aiclimb.aiclimb.workers.dev/' + route],text=True))
            assert response['status'] == 200, response
            assert response['sha'] == assets[name], 'Live baseline changed: ' + name
    assert not output.exists(), 'Use a new output directory'
    before = (baseline / 'public/index.html').read_text(encoding='utf-8')
    after = transform(before)
    verify_content(before, after)
    for source in (baseline / 'public').rglob('*'):
        if not source.is_file(): continue
        rel = source.relative_to(baseline / 'public'); target = output / 'public' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if rel.as_posix() == 'index.html': target.write_text(after, encoding='utf-8', newline='\n')
        else: os.link(source, target)
    for name in OWNED:
        target = output / 'public' / name
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'site/static' / name, target)
    for path in re.findall(r'<img\b[^>]*src=[\"\'](/[^\"\']+)', after):
        assert (output / 'public' / path.lstrip('/').split('?')[0]).is_file(), path
    result_assets = hashes(output / 'public')
    assert set(result_assets) - set(assets) == set(OWNED)
    assert [n for n in assets if result_assets[n] != assets[n]] == ['index.html']
    assert hashes(baseline / 'public') == assets, 'Baseline modified'
    template = (ROOT / 'site/templates/ai-news/home.html').read_text(encoding='utf-8')
    assert 'realistic-home-style' in template and 'realistic-cafe-20261004.webp' in template
    status = subprocess.check_output(['git', '-c', 'core.excludesFile=', 'status', '--porcelain', '--', *INPUTS], cwd=ROOT, text=True)
    result = dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), source_inputs_clean=not status.strip(), inputs=INPUTS, source_inputs={n:sha(ROOT/n) for n in INPUTS}, assets=result_assets, changed_assets=['index.html'], added_assets=OWNED, unchanged_assets=len(assets)-1, baseline_unchanged=True, copy_links_forms_scripts_preserved=True, baseline_live_verified=live, worker_sha256=prior['worker_sha256'])
    (output/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['assets','source_inputs','inputs']},ensure_ascii=False))

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify-live',action='store_true')
    a=p.parse_args();build(a.baseline.resolve(),a.output.resolve(),a.verify_live)
