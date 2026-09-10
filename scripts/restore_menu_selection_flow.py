"""Restore the existing menu chooser entry without rebuilding the public home."""
from pathlib import Path
import re


def restore(text: str) -> str:
    pattern = r"(<div class='hero-diagnose-cta'><span class='hero-diagnose-eyebrow'>).*?(</span>).*?(<small>).*?(</small></div>)"
    replacement = (
        r"\g<1>困りごとから、最初の一歩を決める。\g<2>"
        "<button type='button' class='focus-btn primary diagnose-open' "
        "aria-haspopup='dialog' aria-controls='diagnoseModal'>メニュー選択フロー</button>"
        r"\g<3>3つの質問で、あなたに合う講習・相談メニューをご案内します。\g<4>"
    )
    text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1 or "id='diagnoseModal'" not in text:
        raise ValueError('Expected the existing hero entry and diagnosis dialog')
    text = text.replace("id='diagnose-title'>迷ったら60秒診断", "id='diagnose-title'>メニュー選択フロー")
    return text


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    for relative in ('cloudflare-runtime/public/index.html', 'site/dist/index.html'):
        path = root / relative
        before = path.read_text(encoding='utf-8')
        after = restore(before)
        if before != after:
            path.write_text(after, encoding='utf-8', newline='\n')
        print(f'Restored: {relative}')
