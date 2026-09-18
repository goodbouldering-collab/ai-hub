"""Publish the approved Cloudflare article while preserving the verified live site."""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.studio_design import decorate_html

CONTRACT = ROOT / "deployment/cloudflare-blog/baseline.json"
ORIGIN = "https://aiclimb.aiclimb.workers.dev"
NOTE = "※内容は運営者が考え、AIで整えています。"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root: Path) -> dict[str, str]:
    paths = sorted(root.rglob("*"))
    assert root.is_dir() and not any(p.is_symlink() for p in paths)
    return {p.relative_to(root).as_posix(): digest(p) for p in paths if p.is_file()}


def insert_once(text: str, marker: str, addition: str) -> str:
    assert text.count(marker) == 1, f"Expected one insertion point: {marker}"
    return text.replace(marker, marker + addition, 1)


def build(baseline: Path, output: Path) -> dict:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    baseline, output = baseline.resolve(), output.resolve()
    assert baseline.name == contract["release_directory"]
    assert digest(baseline / "verification.json") == contract["verification_sha256"]
    manifest = json.loads((baseline / "verification.json").read_text(encoding="utf-8"))
    assert manifest["source_sha"] == contract["source_sha"]
    assert manifest["source_inputs_clean"] is True
    assert hashes(baseline / "public") == manifest["assets"], "Baseline assets changed"
    assert hashes(baseline / "runtime") == manifest["runtime"], "Baseline runtime changed"
    assert output.is_relative_to(ROOT) and not output.exists(), "Use a fresh project-local output"
    assert not output.is_relative_to(baseline)

    spec = importlib.util.spec_from_file_location("blog_release_site", ROOT / "site/build_site.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    assert builder.SITE_URL == ORIGIN
    slug = contract["slug"]
    source = ROOT / f"content/blog/{slug}.md"
    meta, body = builder._parse_frontmatter(source.read_text(encoding="utf-8"))
    assert meta["authorship_note"] == NOTE and meta["status"] == "published"
    title, summary, date = (html.escape(str(meta[k]), quote=True) for k in ("title", "summary", "date"))
    path = f"blog/{slug}.html"
    assert path not in manifest["assets"], "Article already exists in the baseline"
    body_html = builder._load_markdown().markdown(body, extensions=["extra", "sane_lists", "attr_list"])
    page = decorate_html(builder.render_content_page(
        str(meta["title"]), meta, body_html,
        builder.render_top_nav(path_prefix="../", current_id="blog", include_run=False),
        page_path=path, kind="blog"))
    soup = BeautifulSoup(page, "html.parser")
    content = soup.select_one(".content-wrap")
    headings = content.select("h2")
    assert len(headings) == 4
    for heading in headings:
        assert heading.find_next_sibling().name == "figure", "Each H2 needs its explanatory image"
    images = content.select("img")
    assert len(images) == 5 and len({img["src"] for img in images}) == 5
    assert soup.select_one("h1").get_text() == meta["title"]
    assert soup.select_one("main > p").get_text() == NOTE
    assert not soup.select_one("main > p").attrs
    assert soup.select_one('link[rel="canonical"]')["href"] == f"{ORIGIN}/{path}"
    assert soup.select_one('meta[property="og:image"]')["content"] == ORIGIN + meta["image"]
    structured = json.loads(soup.select_one('script[type="application/ld+json"]').string)
    assert structured["headline"] == meta["title"]
    assert not soup.select('[contenteditable],meta[name="robots"][content*="noindex"]')

    shutil.copytree(baseline / "public", output / "public")
    shutil.copytree(baseline / "runtime", output / "runtime")
    (output / "public" / path).write_text(page, encoding="utf-8", newline="\n")
    image_inputs = []
    for image in images:
        relative = image["src"].lstrip("/")
        assert relative.startswith("img/blog-cloudflare-ai-") and ".." not in relative
        image_source = ROOT / "site/static" / relative
        assert image_source.is_file() and image.get("alt")
        image_inputs.append(image_source)
        assert relative not in manifest["assets"]
        shutil.copyfile(image_source, output / "public" / relative)

    image = html.escape(str(meta["image"]), quote=True)
    home_card = (
        f"<a class='blog-card' href='/{path}'>"
        f"<div class='blog-card-media'><img src='{image}' alt='' loading='lazy' decoding='async'></div>"
        "<div class='blog-card-body'>"
        f"<div class='blog-card-meta'><span>{date}</span></div>"
        f"<div class='blog-card-title-row'><h3>{title}</h3><span class='blog-new-badge'>NEW</span></div>"
        f"<p>{summary}</p><span class='blog-card-more'>読む</span></div></a>"
    )
    index_card = (
        f"<a class='tr-card' href='./{slug}.html'><div class='tr-title'>{title}</div>"
        f"<div class='tr-date'>{date}</div><div class='tr-sum'>{summary}</div></a>"
    )
    edits = {
        "index.html": ("<div class='pf-carousel blog-carousel' id='blog-carousel'>", home_card),
        "blog/index.html": ("<div class='tr-grid'>", index_card),
    }
    for filename, (marker, addition) in edits.items():
        original = (baseline / "public" / filename).read_text(encoding="utf-8")
        assert slug not in original
        updated = insert_once(original, marker, addition)
        assert updated.replace(addition, "", 1) == original
        (output / "public" / filename).write_text(updated, encoding="utf-8", newline="\n")

    sitemap_path = output / "public/sitemap.xml"
    original = sitemap_path.read_text(encoding="utf-8")
    assert original.count("</urlset>") == 1 and slug not in original
    entry = f"  <url><loc>{ORIGIN}/{path}</loc><lastmod>{date}</lastmod><priority>0.7</priority></url>\n"
    updated = original.replace("</urlset>", entry + "</urlset>")
    ET.fromstring(updated)
    sitemap_path.write_text(updated, encoding="utf-8", newline="\n")

    assets, runtime = hashes(output / "public"), hashes(output / "runtime")
    added = sorted(assets.keys() - manifest["assets"].keys())
    changed = sorted(k for k in manifest["assets"] if assets.get(k) != manifest["assets"][k])
    assert len(added) == 6 and path in added
    assert changed == ["blog/index.html", "index.html", "sitemap.xml"]
    assert runtime == manifest["runtime"], "Runtime must remain byte-identical"
    source_paths = [CONTRACT, CONTRACT.with_name("requirements.txt"), Path(__file__).resolve(), source, *image_inputs,
                    ROOT / "site/build_site.py", ROOT / "site/build_portal.py",
                    ROOT / "site/public_navigation.py", ROOT / "site/blog_freshness.py",
                    ROOT / "core/daily_news.py", ROOT / "core/studio_design.py"]
    source_inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in source_paths}
    dirty = subprocess.check_output(
        ["git", "-c", "core.excludesFile=", "status", "--porcelain", "--", *source_inputs],
        cwd=ROOT, text=True).splitlines()
    result = {
        "source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_inputs": source_inputs, "source_inputs_clean": not dirty, "source_input_status": dirty,
        "baseline_source_sha": contract["source_sha"], "baseline_version": contract["cloudflare_version"],
        "assets": assets, "runtime": runtime, "changed_assets": changed, "added_assets": added,
        "preserved_assets": len(assets) - len(added) - len(changed), "deployed": False,
        "article_checks": {"h2": 4, "images": 5, "canonical": f"{ORIGIN}/{path}",
                           "authorship_note": True, "jsonld": True, "index_links": True, "sitemap": True},
    }
    (output / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("source_sha", "source_inputs_clean", "added_assets", "changed_assets", "preserved_assets", "article_checks")}, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline, args.output)
