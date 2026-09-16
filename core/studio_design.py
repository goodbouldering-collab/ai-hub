"""Apply AI相談's shared presentation and its owned speaker summary.

The release and daily-news builders use this layer so a later content rebuild
retains the design. Runtime decoration is limited to static HTML and login markup.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil



ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "site/static/design-system/studio"
PREFIX = "/design-system/studio"
LINK = f'<link id="studio-design" rel="stylesheet" href="{PREFIX}/studio.css?v=20260914-glass">'
SCRIPT = f'<script id="studio-motion" defer src="{PREFIX}/studio.js?v=20260914-glass"></script>'
EDITORIAL_LINK = f'<link id="studio-editorial" rel="stylesheet" href="{PREFIX}/editorial.css?v=20260916">'


def _attribute(tag: str, name: str, value: str) -> str:
    pattern = rf'\b{re.escape(name)}\s*=\s*([\"\']).*?\1'
    replacement = f'{name}="{value}"'
    if re.search(pattern, tag, re.S):
        return re.sub(pattern, lambda _: replacement, tag, count=1, flags=re.S)
    return tag[:-1] + " " + replacement + ">"


def decorate_html(text: str, *, home: bool = False, admin: bool = False, login: bool = False) -> str:
    if not re.search(r"<body\b", text, re.I) or not re.search(r"</head>", text, re.I):
        return text
    classes = ["studio-theme", "studio-editorial"]
    if home:
        classes.append("studio-home")
    if admin:
        classes.append("studio-admin")
    if login:
        classes.append("studio-login")

    def body_tag(match):
        tag = match.group()
        current = re.search(r'\bclass\s*=\s*([\"\'])(.*?)\1', tag, re.S)
        values = current.group(2).split() if current else []
        return _attribute(tag, "class", " ".join(dict.fromkeys(values + classes)))

    text = re.sub(r"<body\b[^>]*>", body_tag, text, count=1, flags=re.I)
    # Replace the owned tags as well as adding them, so dated rebuilds upgrade
    # the shared theme without duplicate scripts or stale browser caches.
    text = re.sub(r'<link\b[^>]*id=[\"\']studio-design[\"\'][^>]*>', '', text)
    text = re.sub(r'<script\b[^>]*id=[\"\']studio-motion[\"\'][^>]*>\s*</script>', '', text)
    text = re.sub(r'<link\b[^>]*id=[\"\']studio-editorial[\"\'][^>]*>', '', text)
    text = re.sub(r'\s*</head>', lambda _: LINK + SCRIPT + EDITORIAL_LINK + "\n</head>", text, count=1, flags=re.I)
    if home:
        def hero(match):
            tag = match.group(2)
            for key, value in {"src": f"{PREFIX}/images/art-hero.webp", "alt": "人の手、琵琶湖の風景、紙と銀の道を重ね、地域の仕事が広がる可能性を表したコラージュ", "width": "1536", "height": "1024", "fetchpriority": "high"}.items():
                tag = _attribute(tag, key, value)
            return match.group(1) + tag

        text, count = re.subn(r'(<figure\b[^>]*id=[\"\']restored-hero-image[\"\'][^>]*>\s*)(<img\b[^>]*>)', hero, text, count=1, flags=re.S)
        assert count == 1, "Expected the owned hero image"
        images = iter([
            ("learn", "人の横顔とノートを重ね、学びの入口を表したアートコラージュ"),
            ("learn", "人の横顔とノートを重ね、学びの入口を表したアートコラージュ"),
            ("build", "キーボードと鉛筆を扱う手から、アイデアが形になるアートコラージュ"),
            ("build", "キーボードと鉛筆を扱う手から、アイデアが形になるアートコラージュ"),
            ("connect", "人物と湖畔の街を銀の道でつなぐ、地域の学び合いのアートコラージュ"),
            ("connect", "人物と湖畔の街を銀の道でつなぐ、地域の学び合いのアートコラージュ"),
        ])

        def course(match):
            name, alt = next(images)
            tag = match.group()
            for key, value in {"src": f"{PREFIX}/images/art-{name}.webp", "alt": alt, "width": "1536", "height": "1024", "loading": "lazy", "decoding": "async"}.items():
                tag = _attribute(tag, key, value)
            return tag

        text, count = re.subn(r'<img\b[^>]*class=[\"\'][^\"\']*\bcompact-course-visual\b[^\"\']*[\"\'][^>]*>', course, text)
        assert count == 6, "Expected six course illustrations"
    # Refresh only owned artwork layers, including already-decorated snapshots.
    text = re.sub(r'<span\b[^>]*class=[\"\'][^\"\']*\bstudio-art-layer\b[^\"\']*[\"\'][^>]*>\s*<img\b[^>]*>\s*</span>', '', text)
    text = re.sub(r'<div class="studio-editorial-person">.*?</div>', '', text, flags=re.S)

    def portrait(match):
        opening, tag = match.groups()
        for key, value in {'src': '/img/speaker.webp', 'alt': 'AI相談講師 由井辰美の本人写真', 'width': '1200', 'height': '900', 'loading': 'lazy', 'decoding': 'async'}.items():
            tag = _attribute(tag, key, value)
        return opening + tag

    text = re.sub(r'(<(?:div|figure)\b[^>]*class=[\"\'][^\"\']*\b(?:speaker-art|speaker-painting)\b[^\"\']*[\"\'][^>]*>\s*)(<img\b[^>]*>)', portrait, text)
    text = re.sub(r'()(<img\b[^>]*class=[\"\'][^\"\']*\bspeaker-painting\b[^\"\']*[\"\'][^>]*>)', portrait, text)

    def stack(match):
        opening, main_image = match.groups()
        classes = re.search(r'\bclass=[\"\']([^\"\']*)[\"\']', opening)
        values = classes.group(1).split() if classes else []
        opening = _attribute(opening, 'class', ' '.join(dict.fromkeys(values + ['studio-art-stack'])))
        if 'restored-hero-image' in opening:
            layers = ('<div class="studio-editorial-person">'
                      '<img class="studio-editorial-portrait" src="/img/speaker.webp" alt="AI相談講師 由井辰美の本人写真" width="1200" height="900" decoding="async">'
                      '<span class="studio-editorial-decoration" aria-hidden="true">由井 辰美 <small>AI相談 講師</small></span></div>')
        else:
            layers = f'<span class="studio-art-layer studio-art-layer--secondary" aria-hidden="true"><img src="{PREFIX}/images/art-build.webp" alt="" width="1536" height="1024" loading="lazy" decoding="async"></span>'
        return opening + main_image + layers

    text = re.sub(r'(<figure\b[^>]*id=[\"\']restored-hero-image[\"\'][^>]*>)(\s*<img\b[^>]*>)', stack, text, count=1)
    text = re.sub(r'(<div\b[^>]*class=[\"\'][^\"\']*\bspeaker-art\b[^\"\']*[\"\'][^>]*>)(\s*<img\b[^>]*>)', stack, text, count=1)
    return text


def decorate_public_tree(output: Path) -> list[str]:
    changed = []
    for target in output.rglob("*.html"):
        relative = target.relative_to(output).as_posix()
        original = target.read_text(encoding="utf-8")
        content = original
        updated = decorate_html(content, home=relative == "index.html", admin=relative.startswith("admin/"))
        if updated != original:
            target.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(relative)
    shutil.copytree(ASSETS, output / "design-system/studio", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("README.md"))
    return sorted(changed)


def decorate_runtime(output: Path) -> list[str]:
    """Change only HTML assets and login presentation in an exported runtime."""
    assets = output / "worker/admin-assets.generated.mjs"
    source = assets.read_text(encoding="utf-8")
    prefix, encoded = source.split("export default ", 1)
    entries = json.loads(encoded.strip().removesuffix(";"))
    for entry in entries.values():
        if entry["type"].startswith("text/html"):
            entry["body"] = decorate_html(entry["body"], admin=True)
    assets.write_text(prefix + "export default " + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    login = output / "worker/login-page.mjs"
    login.write_text(decorate_html(login.read_text(encoding="utf-8"), admin=True, login=True), encoding="utf-8", newline="\n")
    return ["worker/admin-assets.generated.mjs", "worker/login-page.mjs"]
