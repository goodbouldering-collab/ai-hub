"""Apply the career section to an existing public page without rebuilding its design.

Usage: python scripts/apply-speaker-career.py BASELINE_DIRECTORY
The baseline directory contains index.html and speaker.html from the current site.
"""
from pathlib import Path
import re
import sys

import markdown

ROOT = Path(__file__).resolve().parents[1]


def apply(baseline: Path, output: Path | None = None) -> None:
    source = (ROOT / 'content/speaker.md').read_text(encoding='utf-8')
    career = source.split('## これまでの歩み {#career}', 1)[1].split('## 講習で伝える', 1)[0]
    career_html = markdown.markdown('## これまでの歩み {#career}' + career, extensions=['extra', 'sane_lists'])
    home = (baseline / 'index.html').read_text(encoding='utf-8-sig')
    speaker = (baseline / 'speaker.html').read_text(encoding='utf-8-sig')
    old_link = "href='/speaker.html#achievements'>講師の実績を見る</a>"
    assert home.count(old_link) == 1, 'Unexpected homepage link; inspect before editing'
    home = home.replace(old_link, "href='/speaker.html#career'>講師のプロフィールを見る</a>")
    speaker, count = re.subn(r"<section class='speaker-achievements'[^>]*>.*?</section>", '', speaker, count=1, flags=re.S)
    assert count == 1, 'Expected one existing achievement section'
    speaker = speaker.replace("<a href='#achievements'>公開実績を見る</a>", "<a href='#career'>これまでの歩みを見る</a>")
    speaker = speaker.replace("<a href='#achievements'>実績</a>", '')
    nav = "<a href='#profile'>プロフィール</a>"
    assert speaker.count(nav) == 1
    speaker = speaker.replace(nav, nav + "<a href='#career'>これまでの歩み</a>")
    old_note = '<blockquote>\n<p>活動の詳しい背景は、このページでは「現場で何を支援するか」に絞って整理しています。</p>\n</blockquote>'
    if speaker.count(old_note) == 1:
        speaker = speaker.replace(old_note, career_html)
    else:
        marker = '<section aria-labelledby="principles" class="speaker-principles">'
        assert speaker.count(marker) == 1, 'Unexpected biography insertion point'
        speaker = speaker.replace(marker, '<section aria-labelledby="career" class="speaker-profile">' + career_html + '</section>\n' + marker)
    assert 'href=\'#achievements\'' not in speaker
    for name, text in [('index.html', home), ('speaker.html', speaker)]:
        (output or ROOT / 'cloudflare-runtime/public').joinpath(name).write_text(text, encoding='utf-8')


if __name__ == '__main__':
    apply(Path(sys.argv[1]))
