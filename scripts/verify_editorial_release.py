"""Verify an editorial release preserves the verified site's content and runtime."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.studio_design import decorate_html

MANIFEST = ROOT / "deployment/editorial/baseline.json"
SHARED_THEME_IDS = ("studio-design", "studio-motion", "studio-editorial")
PLAYGROUND_TAGS = {
    "soft-playground-style": ("link", "href", "/design-system/studio/soft-playground.css?v=20260918"),
    "soft-playground-script": ("script", "src", "/design-system/studio/soft-playground.js?v=20260918"),
}
THEME_IDS = SHARED_THEME_IDS + tuple(PLAYGROUND_TAGS)
SOFT_IMAGE_NAMES = ("hero", "agent", "personal", "code", "support", "salon", "site",
                    "mentor", "profile", "prepare", "try", "keep", "login")
SOFT_IMAGES = {f"design-system/studio/images/soft-{name}.webp" for name in SOFT_IMAGE_NAMES}
EDITORIAL_HREF = "/design-system/studio/editorial.css?v=20260918-soft-studio"
LEGACY_ART = re.compile(r"(?:/|[\"'()\s])(?:design-system/studio/)?images/(?:human|flow|art)-[^\s\"'<>)]*", re.I)
PRESENTATION_ASSETS = {
    "design-system/studio/studio.css",
    "design-system/studio/studio.js",
    "design-system/studio/editorial.css",
}
NEW_ASSETS = SOFT_IMAGES | {"design-system/studio/soft-playground.css", "design-system/studio/soft-playground.js"}
DECORATIONS = ".studio-art-layer, .studio-editorial-decoration, .studio-scene-layer"
CONTROL_SELECTOR = "a,button,input,textarea,select,option,form,details,summary,iframe"
PHOTO_URL = re.compile(r'/img/speaker(?:[-a-z0-9]*)\.(?:webp|png|jpe?g)', re.I)
INSTRUCTOR_ART = {"/design-system/studio/images/human-practice.webp",
                  "/design-system/studio/images/soft-mentor.webp",
                  "/design-system/studio/images/soft-profile.webp"}


def assert_playground(soup: BeautifulSoup, name: str, *, expected: bool) -> None:
    sections = soup.select("#studio-playground")
    require(len(sections) == int(expected), f"Missing, duplicate or misplaced playground: {name}")
    for identity, (tag_name, attribute, value) in PLAYGROUND_TAGS.items():
        tags = soup.select(f"#{identity}")
        require(len(tags) == int(expected), f"Missing or unexpected playground tag {identity}: {name}")
        if tags:
            tag = tags[0]
            require(tag.name == tag_name and tag.get(attribute) == value,
                    f"Incorrect playground resource: {identity}")
            require(tag_name != "script" or tag.has_attr("defer"), "Playground script must be deferred")
            require(tag_name != "link" or tag.get("rel") == ["stylesheet"], "Playground CSS must be a stylesheet")
    if not expected:
        return
    section = sections[0]
    previous = section.find_previous_sibling()
    require(section.name == "section" and previous is not None and previous.get("id") == "ai-news",
            "Playground must be a section immediately after AI news")
    require(not section.select("a,form,textarea,select,iframe,script,style"),
            "The local playground must not add submission, embedded or inline executable content")
    require(all(button.get("type") == "button" for button in section.select("button")),
            "Playground buttons must not submit a form")
    require(len(section.select('button[role="tab"]')) == 3 and len(section.select('[role="tablist"]')) == 1,
            "Expected three local work tabs")
    inputs = section.select("input")
    require(len(inputs) == 2 and {element.get("value") for element in inputs} == {"manual", "ai"} and
            all(element.get("type") == "radio" and element.get("name") == "studio-playground-mode"
                for element in inputs), "Expected only the two local mode radios")
    require(len(section.select("article[data-sp-panel]")) == 3 and
            len(section.select("div[data-sp-mode]")) == 6, "Expected six readable local examples")


def without_person_image(value):
    """Normalize only the removed portrait of a Person, preserving all other data."""
    if isinstance(value, list):
        return [without_person_image(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: without_person_image(item) for key, item in value.items()}
    types = value.get("@type", [])
    types = [types] if isinstance(types, str) else types
    if "Person" in types and PHOTO_URL.search(str(value.get("image", ""))):
        result.pop("image", None)
    return result


def assert_no_personal_images(soup: BeautifulSoup, name: str) -> None:
    """Retained photo files must never be referenced by rendered pages or metadata."""
    require(not soup.select(".studio-editorial-person, .studio-editorial-portrait, .studio-art-layer"),
            f"Removed portrait/decorative frame still rendered: {name}")
    require(not PHOTO_URL.search(str(soup).replace("\\/", "/")),
            f"Personal photo still referenced in DOM, CSS, social metadata or script: {name}")
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.string or script.get_text())
        require(not PHOTO_URL.search(json.dumps(data, ensure_ascii=False)),
                f"Personal photo still referenced by JSON-LD: {name}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def files(root: Path) -> dict[str, Path]:
    require(root.is_dir(), f"Missing directory: {root}")
    result = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), f"Symlink is not a release input: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path
    return result


def hashes(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in files(root).items()}


def validate_baseline(baseline: Path) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key, directory in (("assets", "public"), ("runtime", "runtime")):
        actual, expected = hashes(baseline / directory), manifest[key]
        added, missing = sorted(actual.keys() - expected.keys()), sorted(expected.keys() - actual.keys())
        changed = sorted(name for name in actual.keys() & expected.keys()
                         if actual[name] != expected[name])
        require(not (added or missing or changed),
                f"Unverified baseline {directory}: added={added}, missing={missing}, changed={changed}")
    return manifest


def remove_theme_tags(text: str) -> str:
    """Keep runtime bytes except owned tags/class and adjacent head whitespace."""
    for identity in THEME_IDS:
        text = re.sub(rf'<link\b[^>]*\bid=[\"\']{identity}[\"\'][^>]*>', "", text)
        text = re.sub(rf'<script\b[^>]*\bid=[\"\']{identity}[\"\'][^>]*>\s*</script>', "", text)
    def body_class(match):
        start, quote, classes, end = match.groups()
        values = [value for value in classes.split() if value != "studio-editorial"]
        return start + quote + " ".join(values) + quote + end
    text = re.sub(r'(<body\b[^>]*\bclass=)([\"\'])(.*?)[\"\']([^>]*>)', body_class, text, flags=re.I)
    return re.sub(r"\s*</head>", "\n</head>", text, flags=re.I)


def semantics(text: str, name: str) -> dict:
    soup = BeautifulSoup(text, "html.parser")
    may_change_images = name in {"index.html", "speaker.html"}
    if soup.select("#studio-playground"):
        require(name == "index.html", f"Unexpected playground outside homepage: {name}")
        assert_playground(soup, name, expected=True)
        soup.select_one("#studio-playground").decompose()
    for added in list(soup.select(DECORATIONS)):
        # A nested decoration may have been removed with its parent.
        if added.parent is None:
            continue
        require(may_change_images, f"Unexpected decoration on {name}")
        require(added.get("aria-hidden") == "true", f"Decoration must be hidden from AT: {name}")
        require(not added.select(CONTROL_SELECTOR), f"Decoration contains controls: {name}")
        require(all(image.get("alt") == "" for image in added.select("img")),
                f"Decorative image must have an empty alt: {name}")
        added.decompose()
    portraits = soup.select("img.studio-editorial-portrait")
    require(len(portraits) <= 1, f"Duplicate new real portrait: {name}")
    for portrait in portraits:
        require(may_change_images, f"New portrait on unrelated page: {name}")
        require(portrait.get("src") == "/img/speaker.webp" and bool(portrait.get("alt", "").strip()),
                f"New portrait must use the existing real photograph and meaningful alt: {name}")
        require(portrait.find_parent(["a", "button"]) is None,
                f"New portrait unexpectedly changes interaction: {name}")
        portrait.decompose()
    for identity in THEME_IDS:
        for owned in soup.select(f"#{identity}"):
            owned.decompose()
    owned_images = set()
    if may_change_images:
        owned_images = {id(element) for element in soup.select(
            "#restored-hero-image > img, img.compact-course-visual, img.focus-step-visual, .speaker-art > img, #speaker img.speaker-painting")}
    images = [({"owned_image": True} if id(element) in owned_images else dict(element.attrs))
              for element in soup.select("img,source")]
    scripts = []
    for element in soup.find_all("script"):
        if may_change_images and element.get("type") == "application/ld+json":
            data = json.loads(element.string or element.get_text())
            scripts.append({"attributes": dict(element.attrs),
                            "json": without_person_image(data)})
        else:
            scripts.append(str(element))
    styles = [str(element) for element in soup.find_all("style")]
    if may_change_images:
        for element in soup.select("head meta"):
            image_key = element.get("property") or element.get("name") or ""
            value = element.get("content", "")
            if image_key in {"og:image", "og:image:secure_url", "twitter:image"} and (
                    PHOTO_URL.search(value) or any(value.endswith(art) for art in INSTRUCTOR_ART)):
                element["content"] = "__owned_instructor_image__"
    metadata = [str(element) for element in soup.select("head meta, head title, head link")]
    controls = [{"tag": element.name, **dict(element.attrs)}
                for element in soup.select(CONTROL_SELECTOR)]
    headings = [(element.name, element.get("id"), element.get_text(" ", strip=True))
                for element in soup.select("h1,h2,h3,h4,h5,h6")]
    sections = [(element.name, element.get("id")) for element in soup.select("main,section,article")]
    for element in soup.select("script,style"):
        element.decompose()
    return {"text": soup.get_text(" ", strip=True), "controls": controls,
            "headings": headings, "sections": sections, "scripts": scripts,
            "inline_styles": styles, "metadata": metadata, "images": images}


def check_html(before: str, after: str, name: str, *, runtime: bool = False, **flags) -> None:
    old, new = semantics(before, name), semantics(after, name)
    changed = [key for key in old if old[key] != new[key]]
    require(not changed, f"Content changed outside presentation ({', '.join(changed)}): {name}")
    if runtime:
        require(remove_theme_tags(before) == remove_theme_tags(after),
                f"Runtime HTML changed beyond shared presentation tags: {name}")
    require(decorate_html(before, **flags) == after, f"Unexpected transformation outside decorator: {name}")
    require(decorate_html(after, **flags) == after, f"Decoration is not idempotent: {name}")
    if "<body" in after.lower() and "</head>" in after.lower():
        soup = BeautifulSoup(after, "html.parser")
        assert_no_personal_images(soup, name)
        require(not soup.select(".studio-scene-layer"), f"Removed hero inset still rendered: {name}")
        require(not LEGACY_ART.search(str(soup).replace("\\/", "/")), f"Retired artwork still referenced: {name}")
        assert_playground(soup, name, expected=name == "index.html")
        for identity in SHARED_THEME_IDS:
            require(len(soup.select(f"#{identity}")) == 1, f"Missing or duplicated theme tag {identity}: {name}")
        require(soup.select_one("#studio-editorial").get("href") == EDITORIAL_HREF,
                f"Missing current soft studio stylesheet version: {name}")


def assert_soft_image_placement(soup: BeautifulSoup, name: str) -> list[str]:
    """Each visible design frame has its own meaningful image; content images stay separate."""
    expected = []
    if name == "index.html":
        expected = [("#restored-hero-image > img", ("hero",)),
                    ("img.compact-course-visual", ("agent", "personal", "code", "support", "salon", "site")),
                    ("#speaker img.speaker-painting", ("mentor",)),
                    ("img.focus-step-visual", ("prepare", "try", "keep"))]
        bodies = soup.select(".compact-course-card > .studio-course-body")
        require(len(bodies) == 6 and all(body.select_one('.compact-course-heading') and
                body.select_one('.compact-course-tail') for body in bodies),
                "Each course must retain its readable body, title and actions")
    elif name == "speaker.html":
        expected = [(".speaker-art > img", ("profile",))]
    paths = []
    for selector, names in expected:
        images = soup.select(selector)
        wanted = [f"/design-system/studio/images/soft-{kind}.webp" for kind in names]
        require([image.get("src") for image in images] == wanted,
                f"Incorrect soft artwork placement/order at {selector}: {name}")
        require(all(image.get("alt", "").strip() for image in images),
                f"Design artwork needs meaningful alt text: {name} {selector}")
        paths.extend(wanted)
    require(len(paths) == len(set(paths)), f"Repeated design artwork path: {name}")
    return paths


def assert_soft_login_background(css: str) -> str:
    login_art = "/design-system/studio/images/soft-login.webp"
    references = re.findall(r'url\(\s*[\"\']?([^\s\"\')]+)', css)
    paths = []
    for reference in references:
        if "images/soft-" not in reference:
            continue
        resolved = urlsplit(urljoin("/design-system/studio/editorial.css", reference))
        require(not resolved.netloc, "Design artwork must load from a local site asset")
        paths.append(resolved.path)
    rules = [(selector, declarations) for selector, declarations in re.findall(r'([^{}]+)\{([^{}]*)\}', css)
             if "images/soft-login.webp" in declarations]
    require(set(paths) == {login_art} and rules and
            all(all(".studio-login" in part for part in selector.split(",")) for selector, _ in rules),
            "The dedicated login artwork must be confined to the login background")
    return login_art


def runtime_assets(path: Path) -> tuple[str, dict]:
    prefix, encoded = path.read_text(encoding="utf-8").split("export default ", 1)
    return prefix, json.loads(encoded.strip().removesuffix(";"))


def verify(baseline: Path, release: Path) -> dict:
    manifest = validate_baseline(baseline)
    old_files, new_files = files(baseline / "public"), files(release / "public")
    require(old_files.keys() <= new_files.keys(), "An existing public asset was removed")
    additions = set(new_files) - set(old_files)
    require(additions == NEW_ASSETS, f"Unexpected new public assets: {sorted(additions ^ NEW_ASSETS)}")
    changed_assets, html_count, unchanged_assets = [], 0, 0
    for name, before in old_files.items():
        after = new_files[name]
        if before.read_bytes() != after.read_bytes():
            changed_assets.append(name)
        if name.endswith(".html"):
            check_html(before.read_text(encoding="utf-8"), after.read_text(encoding="utf-8"), name,
                       home=name == "index.html", admin=name.startswith("admin/"))
            html_count += 1
        elif name not in PRESENTATION_ASSETS:
            require(before.read_bytes() == after.read_bytes(), f"Non-presentation asset changed: {name}")
            unchanged_assets += 1
    for name in PRESENTATION_ASSETS | NEW_ASSETS:
        source = ROOT / "site/static" / name
        require(source.is_file() and source.read_bytes() == new_files[name].read_bytes(),
                f"Presentation asset differs from its source: {name}")
    image_paths = []
    for name in ("index.html", "speaker.html"):
        soup = BeautifulSoup(new_files[name].read_text(encoding="utf-8"), "html.parser")
        image_paths.extend(assert_soft_image_placement(soup, name))
    css = new_files["design-system/studio/editorial.css"].read_text(encoding="utf-8")
    require(not LEGACY_ART.search(css), "The stylesheet still references retired artwork")
    image_paths.append(assert_soft_login_background(css))
    require(len(image_paths) == 13 and set(path.lstrip("/") for path in image_paths) == SOFT_IMAGES,
            "The 13 design frames must use 13 distinct artwork paths")
    image_hashes = [hashlib.sha256(new_files[path.lstrip("/")].read_bytes()).hexdigest()
                    for path in image_paths]
    require(len(set(image_hashes)) == 13, "Two design images have identical contents")
    for name in SOFT_IMAGES:
        content = new_files[name].read_bytes()
        require(content[:4] == b"RIFF" and content[8:12] == b"WEBP", f"Invalid WebP image: {name}")
    for name in PRESENTATION_ASSETS | (NEW_ASSETS - SOFT_IMAGES):
        require(not LEGACY_ART.search(new_files[name].read_text(encoding="utf-8")),
                f"Retired artwork still referenced in presentation asset: {name}")
    old_runtime, new_runtime = files(baseline / "runtime"), files(release / "runtime")
    require(old_runtime.keys() == new_runtime.keys(), "Runtime file set changed")
    admin_count = unchanged_runtime = 0
    for name, before in old_runtime.items():
        after = new_runtime[name]
        if name == "worker/admin-assets.generated.mjs":
            old_prefix, old_entries = runtime_assets(before)
            new_prefix, new_entries = runtime_assets(after)
            require(old_prefix == new_prefix, "Admin runtime code prefix changed")
            require(old_entries.keys() == new_entries.keys(), "Admin asset inventory changed")
            for key, entry in old_entries.items():
                updated = new_entries[key]
                if entry["type"].startswith("text/html"):
                    require({k: v for k, v in entry.items() if k != "body"} ==
                            {k: v for k, v in updated.items() if k != "body"},
                            f"Admin asset metadata changed: {key}")
                    check_html(entry["body"], updated["body"], f"admin:{key}", runtime=True, admin=True)
                    admin_count += 1
                else:
                    require(entry == updated, f"Admin behavior or settings changed: {key}")
        elif name == "worker/login-page.mjs":
            check_html(before.read_text(encoding="utf-8"), after.read_text(encoding="utf-8"),
                       "login", runtime=True, admin=True, login=True)
        else:
            require(before.read_bytes() == after.read_bytes(), f"Runtime behavior changed: {name}")
            unchanged_runtime += 1
    return {"baseline_source_sha": manifest["source_sha"], "baseline_version": manifest["version"],
            "public_documents_preserved": html_count, "unchanged_non_html_assets": unchanged_assets,
            "new_assets": sorted(additions), "changed_assets": sorted(changed_assets),
            "admin_documents_preserved": admin_count, "runtime_modules_unchanged": unchanged_runtime,
            "login_behavior_preserved": True, "decoration_idempotent": True,
            "personal_photo_rendering_removed": True, "unique_design_image_paths": 13,
            "unique_design_image_hashes": 13, "legacy_art_references_removed": True,
            "playground_after_news": True, "existing_content_outside_playground_preserved": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--release", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.baseline.resolve(), args.release.resolve()), ensure_ascii=False, indent=2))
