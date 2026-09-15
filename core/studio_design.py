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


def _attribute(tag: str, name: str, value: str) -> str:
    pattern = rf'\b{re.escape(name)}\s*=\s*([\"\']).*?\1'
    replacement = f'{name}="{value}"'
    if re.search(pattern, tag, re.S):
        return re.sub(pattern, lambda _: replacement, tag, count=1, flags=re.S)
    return tag[:-1] + " " + replacement + ">"


def decorate_html(text: str, *, home: bool = False, admin: bool = False, login: bool = False) -> str:
    if not re.search(r"<body\b", text, re.I) or not re.search(r"</head>", text, re.I):
        return text
    classes = ["studio-theme"]
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
    text = re.sub(r'\s*</head>', lambda _: LINK + SCRIPT + "\n</head>", text, count=1, flags=re.I)
    if home:
        def hero(match):
            tag = match.group(2)
            for key, value in {"src": f"{PREFIX}/images/hero.png", "alt": "AI教室で講師と受講者がパソコンを囲み、光の流れが人とAIの可能性をつなぐイメージ", "width": "1536", "height": "1024", "fetchpriority": "high"}.items():
                tag = _attribute(tag, key, value)
            return match.group(1) + tag

        text, count = re.subn(r'(<figure\b[^>]*id=[\"\']restored-hero-image[\"\'][^>]*>\s*)(<img\b[^>]*>)', hero, text, count=1, flags=re.S)
        assert count == 1, "Expected the owned hero image"
        images = iter([
            ("learn", "AI教室で受講者が講師と画面を確認し、パソコンを操作しながら学ぶイメージ"),
            ("learn", "AI教室で受講者が講師と画面を確認し、パソコンを操作しながら学ぶイメージ"),
            ("build", "AI教室で講師と一緒に制作を進め、人のアイデアが光の流れとともに形になるイメージ"),
            ("build", "AI教室で講師と一緒に制作を進め、人のアイデアが光の流れとともに形になるイメージ"),
            ("connect", "AI教室で世代の異なる受講者が学び合い、人とAIの知識が光でつながるイメージ"),
            ("connect", "AI教室で世代の異なる受講者が学び合い、人とAIの知識が光でつながるイメージ"),
        ])

        def course(match):
            name, alt = next(images)
            tag = match.group()
            for key, value in {"src": f"{PREFIX}/images/{name}.png", "alt": alt, "width": "1536", "height": "1024", "loading": "lazy", "decoding": "async"}.items():
                tag = _attribute(tag, key, value)
            return tag

        text, count = re.subn(r'<img\b[^>]*class=[\"\'][^\"\']*\bcompact-course-visual\b[^\"\']*[\"\'][^>]*>', course, text)
        assert count == 6, "Expected six course illustrations"
    # Decorative collage uses the existing authored images and has no controls
    # or accessible text. It never replaces a portrait or a content image.
    def stack(match):
        opening, main_image = match.groups()
        classes = re.search(r'\bclass=[\"\']([^\"\']*)[\"\']', opening)
        values = classes.group(1).split() if classes else []
        opening = _attribute(opening, 'class', ' '.join(dict.fromkeys(values + ['studio-art-stack'])))
        layers = ''.join(
            f'<span class="studio-art-layer studio-art-layer--{kind}" aria-hidden="true"><img src="{PREFIX}/images/{name}.png" alt="" width="1536" height="1024" loading="lazy" decoding="async"></span>'
            for kind, name in [('secondary', 'connect'), ('detail', 'learn')]
        )
        return opening + main_image + layers

    if 'studio-art-layer--secondary' not in text:
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
