"""Build the compact home updates section from the verified public release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.home_updates import apply_home_updates, latest_published_posts

INPUTS = [
    'core/home_updates.py', 'site/templates/ai-news/home-updates.css',
    'scripts/build_home_updates_release.py', 'deployment/home-updates/baseline.json',
    'deployment/ai-news/published-worker.mjs',
    'cloudflare-runtime/wrangler-profile-release.jsonc',
    'scripts/build_ai_news_feature.py', 'scripts/verify_ai_news_feature.py',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(directory):
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in directory.rglob('*') if p.is_file()}


def build(baseline, output):
    contract = json.loads((ROOT / INPUTS[3]).read_text(encoding='utf-8'))
    assert baseline.name == contract['baseline_directory']
    assert digest(baseline / 'verification.json') == contract['baseline_verification_sha256']
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    assert previous['source_sha'] == contract['baseline_source_sha']
    assert hashes(baseline / 'public') == previous['assets']
    assert digest(ROOT / INPUTS[4]) == contract['worker_sha256']
    assert output.is_relative_to(ROOT) and not output.exists()
    before = (baseline / 'public/index.html').read_bytes()
    document = before.decode('utf-8')
    blog = (baseline / 'public/blog/index.html').read_text(encoding='utf-8')
    css = (ROOT / INPUTS[1]).read_text(encoding='utf-8')
    updated = apply_home_updates(document, blog, css)
    assert updated != document
    assert apply_home_updates(updated, blog, css) == updated
    assert '彦根で相談する' not in updated
    assert '講師のプロフィールを見る' in updated
    for post in latest_published_posts(blog):
        assert (baseline / 'public' / post['href'].lstrip('/')).is_file()
    for source in (baseline / 'public').rglob('*'):
        if not source.is_file():
            continue
        relative = source.relative_to(baseline / 'public')
        target = output / 'public' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.as_posix() == 'index.html':
            target.write_bytes(updated.encode('utf-8'))
        else:
            os.link(source, target)
    shutil.copyfile(ROOT / INPUTS[4], output / 'published-worker.mjs')
    assets = hashes(output / 'public')
    changed = [name for name in assets if assets[name] != previous['assets'][name]]
    assert changed == ['index.html']
    assert hashes(baseline / 'public') == previous['assets']
    status = subprocess.check_output(['git', '-c', 'core.excludesFile=', 'status',
                                     '--porcelain', '--', *INPUTS], cwd=ROOT, text=True)
    result = dict(
        source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_inputs_clean=not status.strip(), inputs=INPUTS,
        source_inputs={name: digest(ROOT / name) for name in INPUTS},
        assets=assets, changed_assets=changed, unchanged_assets=len(assets) - 1,
        worker_sha256=digest(output / 'published-worker.mjs'),
        baseline_unchanged=True, latest_blogs=latest_published_posts(blog),
    )
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['assets', 'source_inputs', 'inputs']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
