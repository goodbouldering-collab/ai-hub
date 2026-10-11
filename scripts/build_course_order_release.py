"""Move the salon last using the verified production assets as the baseline."""
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
from core.course_menu import apply_course_menu
from core.editorial_feed import _ElementSpans

INPUTS = (
    'core/__init__.py', 'core/editorial_feed.py', 'core/course_menu.py',
    'scripts/build_course_order_release.py', 'deployment/course-order/baseline.json',
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
    if before != previous['assets'] or previous['source_sha'] != contract['source_sha']:
        raise ValueError('Baseline assets changed')
    worker = baseline / 'runtime/published-worker.mjs'
    if digest(worker) != previous['worker_sha256']:
        raise ValueError('Baseline Worker changed')
    if output.exists():
        raise ValueError('Use a fresh output directory')
    inputs = {p: digest(ROOT / p) for p in INPUTS}
    document = (baseline / 'public/index.html').read_bytes().decode('utf-8')
    updated = apply_course_menu(document)

    def split_cards(html):
        spans = _ElementSpans(html, 'compact-course-card').spans
        cards = [html[start:end] for start, end in spans]
        for start, end in reversed(spans):
            html = html[:start] + html[end:]
        return cards, html

    old_cards, old_shell = split_cards(document)
    new_cards, new_shell = split_cards(updated)
    if len(old_cards) != 6 or sorted(old_cards) != sorted(new_cards) or old_shell != new_shell:
        raise ValueError('Card content or unrelated homepage content changed')
    page = BeautifulSoup(updated, 'html.parser')
    cards = page.select('#packages .compact-course-card')
    if [c.get('id') for c in cards[-2:]] != ['ai-app-site', 'seven-day-courses']:
        raise ValueError('The salon must follow app site production')
    if [len(g.select('.compact-course-card')) for g in page.select('.compact-course-grid')] != [2, 4]:
        raise ValueError('Course groups changed')
    if apply_course_menu(updated) != updated:
        raise ValueError('Course generation is not idempotent')
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
                  source_inputs_sha256=inputs, card_contents_unchanged=True,
                  course_order=[c.select_one('h3').get_text() for c in cards])
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('assets','source_inputs_sha256')}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    build(args.baseline.resolve(), args.output.resolve(), args.source_sha)
