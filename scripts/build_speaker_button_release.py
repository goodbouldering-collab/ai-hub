"""Remove the instructor consultation button from the pinned public release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUTTON = "<a class='focus-btn secondary' href='#contact'>彦根で相談する</a>".encode()
INPUTS = [
    'site/build_portal.py', 'site/templates/ai-news/home.html',
    'scripts/build_speaker_button_release.py', 'deployment/speaker-button/baseline.json',
    'deployment/ai-news/published-worker.mjs',
    'cloudflare-runtime/wrangler-profile-release.jsonc',
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
    speaker = re.search(rb"<section\b[^>]*id=['\"]speaker['\"][^>]*>.*?</section>", before, re.S)
    assert speaker and speaker[0].count(BUTTON) == before.count(BUTTON) == 1
    after = before.replace(BUTTON, b'')
    assert '講師のプロフィールを見る'.encode() in after
    for name in INPUTS[:2]:
        assert BUTTON not in (ROOT / name).read_bytes(), name
    # Only immutable, unchanged assets share storage with the baseline.
    for source in (baseline / 'public').rglob('*'):
        if not source.is_file():
            continue
        relative = source.relative_to(baseline / 'public')
        target = output / 'public' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.as_posix() == 'index.html':
            target.write_bytes(after)
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
        baseline_unchanged=True, removed_button='彦根で相談する',
    )
    (output / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['assets', 'source_inputs', 'inputs']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve())
