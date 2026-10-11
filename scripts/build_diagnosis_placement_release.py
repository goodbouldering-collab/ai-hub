"""Move the diagnosis invitation above the blog in a verified public baseline."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from core.editorial_feed import _ElementSpans
from core.diagnosis_copy import apply_diagnosis_copy

INPUTS = (
    'core/__init__.py', 'core/editorial_feed.py', 'core/diagnosis_copy.py',
    'scripts/build_diagnosis_placement_release.py', 'deployment/diagnosis-placement/baseline.json',
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(folder):
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def build(baseline, output, source_sha):
    if not re.fullmatch('[0-9a-f]{40}', source_sha):
        raise ValueError('Expected a complete source SHA')
    contract = json.loads((ROOT / INPUTS[-1]).read_text(encoding='utf-8'))
    if digest(baseline / 'verification.json') != contract['verification_sha256']:
        raise ValueError('Unexpected baseline manifest')
    previous = json.loads((baseline / 'verification.json').read_text(encoding='utf-8'))
    before = hashes(baseline / 'public')
    if before != previous['assets']:
        raise ValueError('Baseline assets changed')
    worker = baseline / 'runtime/published-worker.mjs'
    if digest(worker) != previous['worker_sha256']:
        raise ValueError('Baseline Worker changed')
    if output.exists():
        raise ValueError('Use a fresh output directory')
    inputs = {p: digest(ROOT / p) for p in INPUTS}
    document = (baseline / 'public/index.html').read_bytes().decode('utf-8')
    updated = apply_diagnosis_copy(document)
    old, new = (BeautifulSoup(html, 'html.parser') for html in (document, updated))
    for selector in ('#blog', '#ai-news'):
        if str(old.select_one(selector)) != str(new.select_one(selector)):
            raise ValueError(f'Content changed: {selector}')
    # Only the diagnosis group and its own CSS may change; everything else
    # is compared byte-for-byte, including blog, news, scripts and metadata.
    def shell(html):
        start,end = _ElementSpans(html, 'diagnosis-guide-row').spans[0]
        html = html[:start] + html[end:]
        return re.sub(r'<style id="diagnosis-copy-style">.*?</style>', '', html, flags=re.S)
    if shell(document) != shell(updated):
        raise ValueError('Unrelated homepage content changed')
    if not new.select_one('#top + #diagnosis-start + #blog + #ai-news'):
        raise ValueError('Unexpected homepage order')
    for page in (old, new):
        links = [a['href'] for a in page.select('.diagnosis-guide-row > a')]
        if links != ['/ai-agent-readiness/', '/seo-llmo-diagnosis/']:
            raise ValueError('Diagnosis destinations changed')
    if apply_diagnosis_copy(updated) != updated:
        raise ValueError('Diagnosis generation is not idempotent')
    shutil.copytree(baseline / 'public', output / 'public')
    (output / 'runtime').mkdir()
    shutil.copyfile(worker, output / 'runtime/published-worker.mjs')
    (output / 'public/index.html').write_bytes(updated.encode('utf-8'))
    after = hashes(output / 'public')
    changed = [name for name in before if after.get(name) != before[name]]
    if changed != ['index.html'] or set(after) != set(before):
        raise ValueError('Expected only index.html to change')
    if inputs != {p: digest(ROOT / p) for p in INPUTS}:
        raise ValueError('Build inputs changed during generation')
    report = dict(source_sha=source_sha, baseline_source_sha=previous['source_sha'],
                  assets=after, changed_assets=changed, unchanged_assets=len(before)-1,
                  worker_sha256=digest(output / 'runtime/published-worker.mjs'),
                  source_inputs_sha256=inputs, unrelated_content_unchanged=True)
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('assets','source_inputs_sha256')}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
