"""Keep public search metadata consistent without rebuilding page bodies.

The existing public HTML is the content authority. This final build pass only
changes head metadata, discovery files, and the explicitly approved homepage
business label; it does not infer business facts,
create reviews, or refresh article dates. llms files are an optional reading
guide, not a search-ranking or Google AI inclusion requirement.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

HEAD = re.compile(r"(<head\b[^>]*>)(.*?)(</head\s*>)", re.I | re.S)
JSON_LD = re.compile(r'<script\b(?=[^>]*\btype\s*=\s*[\"\']application/ld\+json[\"\'])[^>]*>.*?</script\s*>', re.I | re.S)
META_TAG = re.compile(r"<meta\b[^>]*>", re.I)
LINK_TAG = re.compile(r"<link\b[^>]*>", re.I)
ARTICLE_TYPES = {"Article", "BlogPosting", "NewsArticle", "LearningResource"}


def _types(node: dict) -> set[str]:
    value = node.get("@type", [])
    return set(value if isinstance(value, list) else [value])


def _nodes(soup: BeautifulSoup) -> list[dict]:
    result = []
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.get_text())
        if isinstance(data, list):
            result.extend(data)
        elif "@graph" in data:
            result.extend(data["@graph"])
        else:
            result.append(data)
    return [deepcopy(node) for node in result if isinstance(node, dict)]


def _meta(soup: BeautifulSoup, key: str, attr: str = "name") -> str:
    tag = soup.find("meta", attrs={attr: key})
    return str(tag.get("content", "")) if tag else ""


def _excluded(path: str, config: dict) -> bool:
    return path in config["noindex_files"] or path in config.get("excluded_files", []) or any(path.startswith(prefix) for prefix in config["excluded_prefixes"])


def _canonical(path: str, soup: BeautifulSoup, config: dict) -> str:
    origin = config["canonical_origin"].rstrip("/")
    if path in config["canonical_paths"]:
        return origin + config["canonical_paths"][path]
    tag = soup.find("link", rel="canonical")
    current = str(tag.get("href", "")) if tag else ""
    if current:
        parsed = urlsplit(current)
        if parsed.scheme != "https" or parsed.netloc != urlsplit(origin).netloc or parsed.query or parsed.fragment:
            raise ValueError(f"Unexpected canonical for {path}: {current}")
        expected = "/" + path
        aliases = {expected, expected.removesuffix(".html")}
        if path.endswith("/index.html"):
            aliases.add(expected.removesuffix("index.html"))
        if parsed.path not in aliases:
            raise ValueError(f"Canonical points to another page for {path}: {current}")
        return origin + (parsed.path.removesuffix("index.html") if parsed.path.endswith("/index.html") else parsed.path.removesuffix(".html"))
    return origin + "/" + (path.removesuffix("index.html") if path.endswith("index.html") else path.removesuffix(".html"))


def _replace_tag(head: str, pattern: re.Pattern, attr: str, key: str, replacement: str, newline: str) -> str:
    seen = False

    def replace(match: re.Match) -> str:
        nonlocal seen
        tag = BeautifulSoup(match.group(), "html.parser").find()
        value = tag.get(attr) if tag else None
        matches = key in value if isinstance(value, list) else value == key
        if not matches:
            return match.group()
        if seen:
            return ""
        seen = True
        return replacement

    updated = pattern.sub(replace, head)
    # Presentation decorators own the end of <head> and may move their styles
    # there on every build. Insert new metadata at the beginning so repeated
    # presentation + search passes retain exactly the same tag order.
    return updated if seen or not replacement else _insert_metadata(updated, replacement, newline)


def _insert_metadata(head: str, tag: str, newline: str) -> str:
    # Preserve the early charset declaration even when adding a large graph.
    for match in META_TAG.finditer(head):
        meta = BeautifulSoup(match.group(), "html.parser").find("meta")
        if meta and (meta.has_attr("charset") or str(meta.get("http-equiv", "")).lower() == "content-type"):
            return head[:match.end()] + newline + tag + head[match.end():]
    return newline + tag + head


def _set_meta(head: str, key: str, value: str, newline: str, attr: str = "name") -> str:
    tag = f'<meta {attr}="{escape(key, quote=True)}" content="{escape(value, quote=True)}">'
    return _replace_tag(head, META_TAG, attr, key, tag, newline)


def _entities(config: dict) -> list[dict]:
    base = config["canonical_origin"].rstrip("/") + "/"
    business = config["business"]
    person = config["person"]
    return [
        {"@type": "ProfessionalService", "@id": base + "#business", "name": business["name"], "url": base,
         "description": business["description"], "email": business["email"], "telephone": business["telephone"], "address": deepcopy(business["address"]),
         "image": urljoin(base, config["default_image"]),
         "areaServed": [{"@type": "Place", "name": area} for area in business["area_served"]]},
        {"@type": "Person", "@id": base + "#yui", "name": person["name"], "jobTitle": person["job_title"],
         "url": urljoin(base, person["path"]), "worksFor": {"@id": base + "#business"}},
        {"@type": "WebSite", "@id": base + "#website", "name": config["site_name"], "url": base,
         "inLanguage": config["language"], "publisher": {"@id": base + "#business"}},
    ]


def _normalize_refs(value, config: dict):
    base = config["canonical_origin"].rstrip("/") + "/"
    aliases = {base + "#organization": base + "#business", base + "speaker.html#person": base + "#yui",
               base + "index.html": base, base + "blog/index.html": base + "blog/", base + "lectures/index.html": base + "lectures/"}
    if isinstance(value, list):
        return [_normalize_refs(item, config) for item in value]
    if not isinstance(value, dict):
        if not isinstance(value, str):
            return value
        value = aliases.get(value, value)
        parsed = urlsplit(value)
        if parsed.scheme == "https" and parsed.netloc == urlsplit(base).netloc and parsed.path.endswith(".html"):
            path = parsed.path.removesuffix("index.html") if parsed.path.endswith("/index.html") else parsed.path.removesuffix(".html")
            value = parsed._replace(path=path).geturl()
        return value
    result = {key: _normalize_refs(item, config) for key, item in value.items()}
    for key in ("author", "publisher", "provider"):
        candidate = result.get(key)
        if not isinstance(candidate, dict):
            continue
        name = candidate.get("name", "").replace(" ", "").replace("　", "")
        if key == "author" and name == config["person"]["name"].replace(" ", ""):
            candidate["@id"] = base + "#yui"
            candidate["url"] = urljoin(base, config["person"]["path"])
        elif key in ("publisher", "provider") and name in {"AI相談", "AIclimb", "AIHub"}:
            candidate["@id"] = base + "#business"
            candidate["name"] = config["site_name"]
            candidate["url"] = base
    return result


def _clarify_offer_price(node: dict, path: str, config: dict) -> None:
    """Express the visible billing unit/minimum without changing the amount."""
    rules = config.get("offer_price_semantics", {})
    monthly = node.get("@id") in {config["canonical_origin"].rstrip("/") + suffix for suffix in rules.get("monthly_ids", [])}
    minimum = path in rules.get("minimum_price_paths", []) and "Service" in _types(node)
    offer = node.get("offers")
    if not (monthly or minimum) or not isinstance(offer, dict) or "price" not in offer:
        return
    amount = offer.pop("price")
    currency = offer.get("priceCurrency", "JPY")
    if monthly:
        offer["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": amount,
            "priceCurrency": currency, "unitText": "月", "unitCode": "MON",
            "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "MON", "unitText": "月"}}
    else:
        number = Decimal(str(amount))
        if not number.is_finite() or number < 0:
            raise ValueError(f"Invalid minimum offer price for {path}")
        offer["priceSpecification"] = {"@type": "PriceSpecification", "minPrice": int(number) if number == int(number) else float(number), "priceCurrency": currency}


def _omit_unrated_testimonials(node: dict) -> None:
    """Keep testimonial prose visible without presenting it as a rated review."""
    if not (_types(node) & {"Course", "Service"}) or "review" not in node:
        return
    reviews = node["review"]
    items = reviews if isinstance(reviews, list) else [reviews]
    rated = [item for item in items if isinstance(item, dict)
             and isinstance(item.get("reviewRating"), dict)
             and item["reviewRating"].get("ratingValue") not in (None, "")]
    if rated:
        node["review"] = rated if isinstance(reviews, list) else rated[0]
    else:
        node.pop("review")


def _graph(path: str, soup: BeautifulSoup, config: dict, canonical: str, title: str, description: str) -> dict:
    base = config["canonical_origin"].rstrip("/") + "/"
    result = _entities(config)
    existing = _nodes(soup)
    page = None
    for original in existing:
        node = _normalize_refs(original, config)
        types = _types(node)
        if types & {"Organization", "ProfessionalService", "LocalBusiness", "Person", "WebSite"}:
            # Existing top-level entities describe this site's publisher/author.
            continue
        if "BreadcrumbList" in types:
            if path == "index.html":  # Sections of one page are not a hierarchy.
                continue
            node.setdefault("@id", canonical + "#breadcrumb")
        if path == "blog/index.html" and "BlogPosting" in types:
            continue  # An archive is a collection, not an article.
        if types & {"WebPage", "CollectionPage", "ProfilePage"}:
            page = node
            continue
        if types & ARTICLE_TYPES:
            node.setdefault("@id", canonical + "#article")
            node["url"] = canonical
            node["mainEntityOfPage"] = {"@id": canonical + "#webpage"}
            node.setdefault("inLanguage", config["language"])
        elif types & {"Service", "WebApplication"} and path != "index.html":
            node.setdefault("@id", canonical + "#" + ("application" if "WebApplication" in types else "service"))
        _clarify_offer_price(node, path, config)
        _omit_unrated_testimonials(node)
        result.append(node)
    kind = "ProfilePage" if path == "speaker.html" else "CollectionPage" if path in {"blog/index.html", "lectures/index.html"} else "WebPage"
    page = page or {}
    page.update({"@type": kind, "@id": canonical + "#webpage", "url": canonical, "name": title,
                 "description": description, "inLanguage": config["language"], "isPartOf": {"@id": base + "#website"}})
    if path == "speaker.html":
        page["mainEntity"] = {"@id": base + "#yui"}
    else:
        principal = next((n for n in result[3:] if _types(n) & (ARTICLE_TYPES | {"Service", "WebApplication"})), None)
        if principal and path != "index.html":
            page["mainEntity"] = {"@id": principal["@id"]}
    if path != "index.html" and not any("BreadcrumbList" in _types(n) for n in result):
        items = [{"@type": "ListItem", "position": 1, "name": "ホーム", "item": base}]
        section = "blog" if path.startswith("blog/") else "lectures" if path.startswith("lectures/") else None
        if section and path != section + "/index.html":
            items.append({"@type": "ListItem", "position": 2, "name": "ブログ" if section == "blog" else "受講資料", "item": base + section + "/"})
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": title, "item": canonical})
        result.append({"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": items})
    breadcrumb = next((n for n in result if "BreadcrumbList" in _types(n)), None)
    if breadcrumb:
        page["breadcrumb"] = {"@id": breadcrumb["@id"]}
    result.append(page)
    for node in result:
        node.pop("@context", None)
    return {"@context": "https://schema.org", "@graph": result}


def _business_telephone(config: dict) -> tuple[str, str]:
    telephone = config["business"]["telephone"]
    match = re.fullmatch(r"\+81-(\d{1,4})-(\d{2,4})-(\d{4})", telephone)
    if not match:
        raise ValueError("Expected the confirmed Japanese business telephone format")
    return "0" + "-".join(match.groups()), "tel:" + telephone.replace("-", "")


def render_business_contact(config: dict) -> str:
    """Render the confirmed address and telephone from one public fact source."""
    business = config["business"]
    address = business["address"]
    location = "".join(address[key] for key in ("addressRegion", "addressLocality", "streetAddress"))
    display, href = _business_telephone(config)
    return (f'<p>〒{escape(address["postalCode"])}<br>{escape(location)}<br>{escape(business["address_note"])}</p>'
            f"<p><a href='{escape(href, quote=True)}'>{escape(display)}</a></p>")


def _independent_home_business(html: str, path: str, config: dict) -> str:
    """Change only the approved identity/contact text in one homepage footer."""
    if path != "index.html":
        return html
    old = "<div class='footer-nap'><span class='footer-nav-head'>運営</span><p>AI相談（彦根 / クライミングコンサル）</p>"
    new = "<div class='footer-nap'><span class='footer-nav-head'>運営</span><p>AI相談（彦根）</p>"
    old_address = "<p>〒522-0043<br>滋賀県彦根市小泉町34-8<br>ビバシティ前</p>"
    contact = render_business_contact(config)
    candidates = []
    for match in re.finditer(r"<footer\b[^>]*>.*?</footer\s*>", html, re.I | re.S):
        tag = BeautifulSoup(match.group(), "html.parser").find("footer")
        if not tag or "site-footer" not in tag.get("class", []):
            continue
        nap_matches = []
        # Scan opening tags independently: other footer columns may contain
        # nested divs. The business block itself contains only inline tags/p.
        for start in re.finditer(r"<div\b[^>]*>", match.group(), re.I | re.S):
            opening = BeautifulSoup(start.group(), "html.parser").find("div")
            if opening and "footer-nap" in opening.get("class", []):
                closing = re.search(r"</div\s*>", match.group()[start.end():], re.I)
                if not closing:
                    raise ValueError("Expected one legacy homepage business footer")
                end = start.end() + closing.end()
                nap_matches.append((start.start(), end))
        if len(nap_matches) > 1:
            raise ValueError("Expected one legacy homepage business footer")
        if nap_matches:
            begin, end = nap_matches[0]
            fragment = match.group()[begin:end]
            if old in fragment or old_address in fragment or contact in fragment:
                if len(re.findall(r"<div\b", fragment, re.I)) != 1:
                    raise ValueError("Expected one legacy homepage business footer")
                candidates.append((match, begin, end, fragment))
    if not candidates:
        return html
    if len(candidates) != 1:
        raise ValueError("Expected one legacy homepage business footer")
    match, begin, end, fragment = candidates[0]
    if fragment.count(old) > 1 or fragment.count(old_address) > 1 or fragment.count(contact) > 1:
        raise ValueError("Expected one legacy homepage business footer")
    updated = fragment.replace(old, new, 1)
    if old_address in fragment:
        if re.search(r"href\s*=\s*['\"]tel:", fragment, re.I):
            raise ValueError("Business footer already has a telephone; refusing duplicate contact")
        updated = updated.replace(old_address, contact, 1)
    elif contact in fragment and len(re.findall(r"href\s*=\s*['\"]tel:", fragment, re.I)) != 1:
        raise ValueError("Expected one business telephone link")
    updated_footer = match.group()[:begin] + updated + match.group()[end:]
    return html[:match.start()] + updated_footer + html[match.end():]


def enhance_search_html(html: str, relative_path: str, config: dict) -> str:
    """Enhance search data plus the approved homepage business identity/contact."""
    path = relative_path.replace("\\", "/")
    html = _independent_home_business(html, path, config)
    match = HEAD.search(html)
    if not match:
        raise ValueError(f"Missing HTML head: {path}")
    newline = "\r\n" if "\r\n" in html else "\n"
    head = match.group(2)
    if _excluded(path, config):
        if path not in config["noindex_files"]:
            return html
        head = _set_meta(head, "robots", "noindex, nofollow", newline)
        return html[:match.start(2)] + head + html[match.end(2):]
    soup = BeautifulSoup(html, "html.parser")
    if "noindex" in _meta(soup, "robots").lower():
        return html
    canonical = _canonical(path, soup, config)
    title = _meta(soup, "og:title", "property") or (soup.h1.get_text(" ", strip=True) if soup.h1 else config["site_name"])
    description = _meta(soup, "description") or _meta(soup, "og:description", "property")
    if path == "index.html":
        title = "AI相談｜彦根・滋賀のAI講習・業務改善"
    elif path == "speaker.html":
        title = "由井辰美の講師紹介｜AI相談"
    tag = f'<link rel="canonical" href="{escape(canonical, quote=True)}">'
    head = _replace_tag(head, LINK_TAG, "rel", "canonical", tag, newline)
    for key, value in {"og:title": title, "og:url": canonical, "og:description": description,
                       "og:site_name": config["site_name"], "og:locale": "ja_JP"}.items():
        head = _set_meta(head, key, value, newline, "property")
    if path in {"speaker.html", "blog/index.html", "lectures/index.html"}:
        head = _set_meta(head, "og:type", "website", newline, "property")
    image = _meta(soup, "og:image", "property")
    if path == "index.html" or not image:
        image = urljoin(config["canonical_origin"] + "/", config["default_image"])
        head = _set_meta(head, "og:image", image, newline, "property")
        head = _set_meta(head, "og:image:alt", config["default_image_alt"], newline, "property")
        # The previous hero dimensions do not describe the new image.
        for key in ("og:image:width", "og:image:height", "og:image:type", "og:image:secure_url"):
            head = _replace_tag(head, META_TAG, "property", key, "", newline)
    for key, value in {"twitter:title": title, "twitter:description": description, "twitter:image": image,
                       "twitter:card": "summary_large_image"}.items():
        head = _set_meta(head, key, value, newline)
    if not _meta(soup, "robots"):
        head = _set_meta(head, "robots", "index, follow, max-image-preview:large", newline)
    if config.get("google_site_verification"):
        head = _set_meta(head, "google-site-verification", config["google_site_verification"], newline)
    graph = _graph(path, soup, config, canonical, title, description)
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    schema = '<script type="application/ld+json" id="search-presence-graph">' + payload + "</script>"
    found = False

    def replace_schema(old: re.Match) -> str:
        nonlocal found
        if found:
            return ""
        found = True
        return schema

    head = JSON_LD.sub(replace_schema, head)
    if not found:
        head = _insert_metadata(head, schema, newline)
    return html[:match.start(2)] + head + html[match.end(2):]


def apply_search_presence(public_dir: str | Path, config_path: str | Path) -> dict:
    """Apply to a COMPLETE public tree; write a canonical, public-only sitemap."""
    public = Path(public_dir)
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    origin = config["canonical_origin"].rstrip("/")
    changed, excluded, pages = [], [], []

    def write(path: str, content: str):
        target = public / path
        data = content.encode("utf-8")
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
            changed.append(path)

    for file in sorted(public.rglob("*.html")):
        path = file.relative_to(public).as_posix()
        html = file.read_bytes().decode("utf-8")
        enhanced = enhance_search_html(html, path, config)
        write(path, enhanced)
        soup = BeautifulSoup(enhanced, "html.parser")
        if _excluded(path, config) or "noindex" in _meta(soup, "robots").lower():
            excluded.append(path)
            continue
        nodes = _nodes(soup)
        dates = [node.get("dateModified") or node.get("datePublished") for node in nodes if _types(node) & ARTICLE_TYPES]
        dates = [date for date in dates if date and re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T[^\s]+)?", date)]
        pages.append({"url": _canonical(path, soup, config), "title": _meta(soup, "og:title", "property"),
                      "description": _meta(soup, "description"), "lastmod": max(dates) if dates else None})
    urls = [page["url"] for page in pages]
    if len(urls) != len(set(urls)):
        raise ValueError("Duplicate public canonical URL")
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    root = ET.Element(f"{{{namespace}}}urlset")
    for page in sorted(pages, key=lambda p: p["url"]):
        item = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(item, f"{{{namespace}}}loc").text = page["url"]
        if page["lastmod"]:
            ET.SubElement(item, f"{{{namespace}}}lastmod").text = page["lastmod"]
    ET.indent(root, space="  ")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n")
    write("robots.txt", "User-agent: *\nAllow: /\n" + "".join(f"Disallow: {path}\n" for path in config["robots_disallow"]) + f"Sitemap: {origin}/sitemap.xml\n")
    lines = [f'# {config["site_name"]}', "", "> " + config["llms_intro"], "",
             f'運営は{config["business"]["name"]}。運営拠点は' + ''.join(config["business"]["address"][key] for key in ("addressRegion", "addressLocality", "streetAddress")) + '。講習の開催場所はトップページの案内で確認できます。', "",
             f'電話: {_business_telephone(config)[0]}', "",
             "内容・料金・受付状況は各公開ページを参照してください。AIオンラインサロンは近日開始・仮運用中です。", ""]
    for section in config["llms_sections"]:
        lines.extend(["## " + section["name"], ""])
        for link in section["links"]:
            url = origin + link["path"]
            if url in urls:
                lines.append(f'- [{link["label"]}]({url}): {link["description"]}')
        lines.append("")
    lines.extend(["## Optional", "", f"- [公開ページの要約一覧]({origin}/llms-full.txt): 公開ページのタイトル・説明・URL。", f"- [サイトマップ]({origin}/sitemap.xml): 検索対象の正規URL一覧。", ""])
    write("llms.txt", "\n".join(lines))
    full = [f'# {config["site_name"]} 公開ページ案内', "", config["llms_intro"], "",
            "各ページの説明をまとめた案内です。最新の内容・料金・受付状況はリンク先を確認してください。", ""]
    for page in sorted(pages, key=lambda p: p["url"]):
        full.extend(["## " + page["title"], "", page["url"], "", page["description"], ""])
    write("llms-full.txt", "\n".join(full))
    return {"changed_files": changed, "indexed_pages": len(pages), "excluded_pages": excluded, "sitemap_urls": sorted(urls)}
