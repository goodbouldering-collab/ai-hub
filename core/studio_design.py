"""Apply AI相談's shared presentation without using the instructor's portrait.

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
EDITORIAL_LINK = f'<link id="studio-editorial" rel="stylesheet" href="{PREFIX}/editorial.css?v=20260918-human-glass">'


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
            for key, value in {"src": f"{PREFIX}/images/human-hero.webp", "alt": "PCの画面を一緒に確かめ、AIで仕事を改善する相談のイメージ（AI生成）", "width": "1536", "height": "1024", "fetchpriority": "high"}.items():
                tag = _attribute(tag, key, value)
            return match.group(1) + tag

        text, count = re.subn(r'(<figure\b[^>]*id=[\"\']restored-hero-image[\"\'][^>]*>\s*)(<img\b[^>]*>)', hero, text, count=1, flags=re.S)
        assert count == 1, "Expected the owned hero image"
        images = iter([
            ("learn", "ノートPCでAIへの依頼と結果の確認を学ぶ人たちのイメージ（AI生成）"),
            ("learn", "ノートPCでAIへの依頼と結果の確認を学ぶ人たちのイメージ（AI生成）"),
            ("build", "PCでコードとWebアプリの動作を確かめる制作のイメージ（AI生成）"),
            ("build", "PCでコードとWebアプリの動作を確かめる制作のイメージ（AI生成）"),
            ("connect", "PCやタブレットを使い、仕事の手順をチームで整理するイメージ（AI生成）"),
            ("connect", "PCやタブレットを使い、仕事の手順をチームで整理するイメージ（AI生成）"),
        ])

        def course(match):
            name, alt = next(images)
            tag = match.group()
            for key, value in {"src": f"{PREFIX}/images/human-{name}.webp", "alt": alt, "width": "1536", "height": "1024", "loading": "lazy", "decoding": "async"}.items():
                tag = _attribute(tag, key, value)
            return tag

        text, count = re.subn(r'<img\b[^>]*class=[\"\'][^\"\']*\bcompact-course-visual\b[^\"\']*[\"\'][^>]*>', course, text)
        assert count == 6, "Expected six course illustrations"
        # The glass body overlaps its own photograph; links keep their DOM order.
        def course_body(match):
            opening, content, closing = match.groups()
            if 'class="studio-course-body"' in content:
                return match.group(0)
            image = re.search(r'<img\b[^>]*\bcompact-course-visual\b[^>]*>', content)
            assert image, "Expected course image before the glass body"
            end = image.end()
            return opening + content[:end] + '<div class="studio-course-body">' + content[end:] + '</div>' + closing
        text = re.sub(r'(<article\b[^>]*\bcompact-course-card\b[^>]*>)(.*?)(</article>)', course_body, text, flags=re.S)

        steps = iter([("practice", "PCと仕事のノートを持ち込むイメージ（AI生成）"),
                      ("learn", "PCの画面を一緒に確かめながら学ぶイメージ（AI生成）"),
                      ("build", "作ったアプリと手順をPCで確認して残すイメージ（AI生成）")])
        def step_image(match):
            name, alt = next(steps)
            tag = match.group()
            for key, value in {"src": f"{PREFIX}/images/human-{name}.webp", "alt": alt,
                               "width": "1536", "height": "1024", "loading": "lazy", "decoding": "async"}.items():
                tag = _attribute(tag, key, value)
            return tag
        text, count = re.subn(r'<img\b[^>]*class=[\"\'][^\"\']*\bfocus-step-visual\b[^\"\']*[\"\'][^>]*>', step_image, text)
        assert count == 3, "Expected three work process images"
    # Refresh only owned artwork layers, including already-decorated snapshots.
    text = re.sub(r'<span\b[^>]*class=[\"\'][^\"\']*\bstudio-art-layer\b[^\"\']*[\"\'][^>]*>\s*<img\b[^>]*>\s*</span>', '', text)
    text = re.sub(r'<div class="studio-editorial-person">.*?</div>', '', text, flags=re.S)
    text = re.sub(r'<span class="studio-scene-layer" aria-hidden="true">\s*<img\b[^>]*>\s*</span>', '', text)
    if home:
        layer = (f'<span class="studio-scene-layer" aria-hidden="true"><img src="{PREFIX}/images/human-practice.webp" '
                 'alt="" width="1536" height="1024" loading="lazy" decoding="async"></span>')
        text = re.sub(r'(<figure\b[^>]*id=[\"\']restored-hero-image[\"\'][^>]*>\s*<img\b[^>]*>)',
                      lambda match: match.group(1) + layer, text, count=1, flags=re.S)

    def profile_art(match):
        opening, tag = match.groups()
        for key, value in {'src': f'{PREFIX}/images/human-practice.webp', 'alt': 'PCとノートを使い、AIを実際の仕事へ生かす手元のイメージ（AI生成）', 'width': '1536', 'height': '1024', 'loading': 'lazy', 'decoding': 'async'}.items():
            tag = _attribute(tag, key, value)
        return opening + tag

    text = re.sub(r'(<(?:div|figure)\b[^>]*class=[\"\'][^\"\']*\b(?:speaker-art|speaker-painting)\b[^\"\']*[\"\'][^>]*>\s*)(<img\b[^>]*>)', profile_art, text)
    text = re.sub(r'()(<img\b[^>]*class=[\"\'][^\"\']*\bspeaker-painting\b[^\"\']*[\"\'][^>]*>)', profile_art, text)

    # The abstract art is not a person's photograph. Remove only portrait
    # metadata; preserve biography and all other structured information.
    def structured_data(match):
        value = json.loads(match.group(2))
        changed = False
        def visit(node):
            nonlocal changed
            if isinstance(node, dict):
                types = node.get('@type', [])
                if isinstance(types, str):
                    types = [types]
                own_person = ''.join(str(node.get('name', '')).split()) == '由井辰美'
                own_image = '/img/speaker' in str(node.get('image', ''))
                if 'Person' in types and (own_person or own_image) and 'image' in node:
                    del node['image']
                    changed = True
                for child in node.values():
                    visit(child)
            elif isinstance(node, list):
                for child in node:
                    visit(child)
        visit(value)
        if not changed:
            return match.group(0)
        encoded = json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        return match.group(1) + encoded + match.group(3)

    text = re.sub(r'(<script\b[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>)(.*?)(</script>)', structured_data, text, flags=re.S)
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
