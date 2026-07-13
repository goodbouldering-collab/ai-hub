#!/usr/bin/env python3
"""Vercel と公開フックから AI相談の実績台帳を同期する。"""

from __future__ import annotations

import argparse
import copy
import html
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "config" / "portfolio.yaml"
DEFAULT_CONFIG = ROOT / "config" / "portfolio-sync.yaml"
PORTFOLIO_HEADER = """# AI相談 — 実績サイト
# scripts/sync_portfolio.py が Vercel の公開サイトと手動登録フックを統合する正本。
# 同名・同slug・同URL・同Vercel project IDは1件へ統合し、旧URLは aliases に残す。
# status: live の項目だけが公開トップ「すべての実績」に表示される。

"""
SERIALIZED_KEYS = (
    "name",
    "slug",
    "url",
    "aliases",
    "status",
    "category",
    "tech",
    "summary",
    "since",
    "thumbnail",
    "source",
    "source_id",
    "source_project",
)


class PageMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self.in_title = True
            return
        if tag.lower() != "meta":
            return
        values = {str(key).lower(): value or "" for key, value in attrs}
        meta_key = (values.get("name") or values.get("property") or "").lower()
        if meta_key in {"description", "og:description"} and not self.description:
            self.description = values.get("content", "").strip()

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def normalize_identity(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return "".join(ch for ch in text if ch.isalnum())


def normalize_url(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    scheme = (parsed.scheme or "https").lower()
    host = (parsed.hostname or "").lower()
    if not host:
        return raw.rstrip("/")
    port = f":{parsed.port}" if parsed.port else ""
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, host + port, path, "", parsed.query, ""))


def domain_url(domain: str) -> str:
    return normalize_url(f"https://{domain.strip().lower()}")


def slug_from(value: str, fallback_url: str = "") -> str:
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if slug:
        return slug
    host = urlparse(normalize_url(fallback_url)).hostname or "site"
    return re.sub(r"[^a-z0-9]+", "-", host.lower()).strip("-") or "site"


def infer_public_name(title: str, project_name: str) -> str:
    cleaned = html.unescape(" ".join((title or "").split())).strip()
    if not cleaned:
        return project_name
    for separator in ("｜", " | ", " — ", " – "):
        if separator in cleaned:
            head = cleaned.split(separator, 1)[0].strip()
            if 2 <= len(head) <= 60:
                return head
    return cleaned[:80]


def choose_canonical_url(domains: list[str], project_name: str, override: str = "") -> str:
    if override:
        return normalize_url(override)
    urls = [domain_url(domain) for domain in domains if domain]
    custom = [url for url in urls if not (urlparse(url).hostname or "").endswith(".vercel.app")]
    if custom:
        return sorted(custom, key=lambda url: ((urlparse(url).hostname or "").startswith("www."), len(url)))[0]
    preferred = normalize_url(f"https://{project_name}.vercel.app")
    if preferred in urls:
        return preferred
    return sorted(urls, key=len)[0] if urls else ""


def item_urls(item: dict[str, Any]) -> set[str]:
    values = [item.get("url"), *(item.get("aliases") or [])]
    return {normalize_url(value) for value in values if normalize_url(value)}


def _match_index(items: list[dict[str, Any]], candidate: dict[str, Any]) -> int | None:
    source_id = str(candidate.get("source_id") or "")
    slugs = {
        normalize_identity(candidate.get("slug")),
        normalize_identity(candidate.get("_match_slug")),
    } - {""}
    name = normalize_identity(candidate.get("name"))
    urls = item_urls(candidate)
    for index, item in enumerate(items):
        if source_id and source_id == str(item.get("source_id") or ""):
            return index
        if slugs and normalize_identity(item.get("slug")) in slugs:
            return index
        if name and name == normalize_identity(item.get("name")):
            return index
        if urls and urls.intersection(item_urls(item)):
            return index
    return None


def ordered_item(item: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in SERIALIZED_KEYS:
        value = item.get(key)
        if value not in (None, "", []):
            result[key] = value
    for key, value in item.items():
        if not key.startswith("_") and key not in result and value not in (None, "", []):
            result[key] = value
    return result


def merge_aliases(*groups: Any, canonical_url: str = "") -> list[str]:
    canonical = normalize_url(canonical_url)
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        values = group if isinstance(group, (list, tuple, set)) else [group]
        for value in values:
            url = normalize_url(value)
            if not url or url == canonical or url in seen:
                continue
            seen.add(url)
            result.append(url)
    return result


def upsert_item(items: list[dict[str, Any]], candidate: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    index = _match_index(items, candidate)
    if index is None:
        item = ordered_item(copy.deepcopy(candidate))
        aliases = merge_aliases(item.get("aliases") or [], canonical_url=item.get("url", ""))
        if aliases:
            item["aliases"] = aliases
        items.append(ordered_item(item))
        return "added", items[-1]

    current = copy.deepcopy(items[index])
    before = copy.deepcopy(current)
    old_url = normalize_url(current.get("url"))
    for key in SERIALIZED_KEYS:
        if key == "aliases":
            continue
        value = candidate.get(key)
        if value not in (None, "", []):
            if key == "source" and current.get("source_id") and value == "site-published-hook":
                continue
            current[key] = copy.deepcopy(value)
    current["url"] = normalize_url(current.get("url"))
    aliases = merge_aliases(
        before.get("aliases") or [],
        candidate.get("aliases") or [],
        old_url if old_url and old_url != current.get("url") else "",
        canonical_url=current.get("url", ""),
    )
    if aliases:
        current["aliases"] = aliases
    else:
        current.pop("aliases", None)
    if old_url != current.get("url") and str(current.get("thumbnail") or "").startswith("https://s.wordpress.com/mshots/"):
        current.pop("thumbnail", None)
    items[index] = ordered_item(current)
    return ("updated" if items[index] != ordered_item(before) else "unchanged"), items[index]


def deduplicate_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    result: list[dict[str, Any]] = []
    removed = 0
    for item in items:
        index = _match_index(result, item)
        if index is None:
            result.append(ordered_item(copy.deepcopy(item)))
            continue
        kept = result[index]
        kept["aliases"] = merge_aliases(
            kept.get("aliases") or [],
            item.get("aliases") or [],
            item.get("url"),
            canonical_url=kept.get("url", ""),
        )
        for key, value in item.items():
            if key not in kept and value not in (None, "", []):
                kept[key] = copy.deepcopy(value)
        result[index] = ordered_item(kept)
        removed += 1
    return result, removed


def fetch_page_metadata(session: requests.Session, url: str, timeout: float = 20.0) -> dict[str, Any]:
    try:
        response = session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 AIConsult-PortfolioSync/1.0"},
        )
        content_type = response.headers.get("content-type", "").lower()
        if response.status_code != 200 or "html" not in content_type:
            return {"status": response.status_code, "title": "", "description": ""}
        parser = PageMetadataParser()
        parser.feed(response.text[:500_000])
        return {
            "status": response.status_code,
            "title": parser.title,
            "description": html.unescape(" ".join(parser.description.split()))[:220],
        }
    except requests.RequestException as exc:
        return {"status": 0, "title": "", "description": "", "error": str(exc)}


def _vercel_get(session: requests.Session, token: str, path: str, team_id: str) -> dict[str, Any]:
    response = session.get(
        f"https://api.vercel.com{path}",
        params={"teamId": team_id, "limit": 100},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def vercel_candidates(config: dict[str, Any], token: str, session: requests.Session) -> tuple[list[dict[str, Any]], list[str]]:
    vercel = config.get("vercel") or {}
    team_id = str(vercel.get("team_id") or "")
    if not team_id:
        raise ValueError("config/portfolio-sync.yaml: vercel.team_id is required")
    project_rules = vercel.get("projects") or {}
    patterns = [re.compile(pattern, re.I) for pattern in vercel.get("exclude_name_patterns") or []]
    default_category = str(vercel.get("default_category") or "Webサイト")
    default_tech = list(vercel.get("default_tech") or ["Vercel"])
    projects = _vercel_get(session, token, "/v9/projects", team_id).get("projects") or []
    candidates: list[dict[str, Any]] = []
    logs: list[str] = []

    for project in projects:
        project_name = str(project.get("name") or "").strip()
        project_id = str(project.get("id") or "").strip()
        if not project_name or not project_id:
            continue
        rule = dict(project_rules.get(project_name) or {})
        if rule.get("include") is False or (not rule and any(pattern.search(project_name) for pattern in patterns)):
            logs.append(f"excluded {project_name}: {rule.get('reason') or 'name pattern'}")
            continue

        domain_data = _vercel_get(session, token, f"/v9/projects/{project_id}/domains", team_id)
        domains = [
            str(domain.get("name") or "")
            for domain in domain_data.get("domains") or []
            if domain.get("verified") is not False and domain.get("name")
        ]
        canonical_url = choose_canonical_url(domains, project_name, str(rule.get("canonical_url") or ""))
        if not canonical_url:
            logs.append(f"skipped {project_name}: no verified domain")
            continue

        metadata: dict[str, Any] = {}
        if not rule:
            metadata = fetch_page_metadata(session, canonical_url)
            if metadata.get("status") != 200 or not metadata.get("title"):
                logs.append(f"skipped {project_name}: public HTML not confirmed ({metadata.get('status')})")
                continue

        name = str(rule.get("name") or infer_public_name(str(metadata.get("title") or ""), project_name))
        summary = str(rule.get("summary") or metadata.get("description") or f"{name}の公開Webサイト")
        candidate = {
            "name": name,
            "slug": str(rule.get("slug") or project_name),
            "url": canonical_url,
            "aliases": [domain_url(domain) for domain in domains],
            "status": "live",
            "category": str(rule.get("category") or default_category),
            "tech": list(rule.get("tech") or default_tech),
            "summary": summary,
            "since": str(rule.get("since") or datetime.now(timezone.utc).strftime("%Y-%m")),
            "source": "vercel",
            "source_id": project_id,
            "source_project": project_name,
            "_match_slug": str(rule.get("match_slug") or ""),
        }
        candidate["aliases"] = merge_aliases(
            candidate["aliases"], rule.get("aliases") or [], canonical_url=canonical_url
        )
        candidates.append(candidate)
    return candidates, logs


def manual_candidate(args: argparse.Namespace, session: requests.Session) -> dict[str, Any] | None:
    if not args.register_name and not args.register_url:
        return None
    if not args.register_name or not args.register_url:
        raise ValueError("--register-name and --register-url must be supplied together")
    url = normalize_url(args.register_url)
    metadata = fetch_page_metadata(session, url) if not args.register_summary else {}
    tech = [part.strip() for part in (args.register_tech or "").split(",") if part.strip()]
    return {
        "name": args.register_name.strip(),
        "slug": args.register_slug or slug_from(args.register_name, url),
        "url": url,
        "status": "live",
        "category": args.register_category or "Webサイト",
        "tech": tech or ["Web"],
        "summary": args.register_summary or metadata.get("description") or f"{args.register_name}の公開Webサイト",
        "since": args.register_since or datetime.now(timezone.utc).strftime("%Y-%m"),
        "source": "site-published-hook",
    }


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def save_portfolio(path: Path, data: dict[str, Any]) -> None:
    dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    path.write_text(PORTFOLIO_HEADER + dumped, encoding="utf-8", newline="\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI相談の実績サイト台帳を同期")
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write", action="store_true", help="portfolio.yamlへ反映。未指定時はdry-run")
    parser.add_argument("--no-vercel", action="store_true", help="Vercel API同期を止め、手動登録だけ実行")
    parser.add_argument("--register-name", default="")
    parser.add_argument("--register-url", default="")
    parser.add_argument("--register-slug", default="")
    parser.add_argument("--register-category", default="")
    parser.add_argument("--register-tech", default="")
    parser.add_argument("--register-summary", default="")
    parser.add_argument("--register-since", default="")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_yaml(args.config)
    portfolio = load_yaml(args.portfolio)
    items = list(portfolio.get("portfolio") or [])
    original = copy.deepcopy(items)
    session = requests.Session()
    report: list[str] = []

    if not args.no_vercel:
        token = os.environ.get("VERCEL_TOKEN", "").strip()
        if not token:
            report.append("VERCEL_TOKEN not set: skipped Vercel inventory; site-published hook remains available")
        else:
            candidates, logs = vercel_candidates(config, token, session)
            report.extend(logs)
            for candidate in candidates:
                action, item = upsert_item(items, candidate)
                if action != "unchanged":
                    report.append(f"{action} {item.get('name')} -> {item.get('url')}")

    try:
        registered = manual_candidate(args, session)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if registered:
        action, item = upsert_item(items, registered)
        if action != "unchanged":
            report.append(f"{action} {item.get('name')} -> {item.get('url')}")

    items, removed = deduplicate_items(items)
    if removed:
        report.append(f"deduplicated {removed} item(s)")
    changed = items != original
    portfolio["portfolio"] = items

    for line in report:
        print(line)
    print(f"portfolio: {len(original)} -> {len(items)} items; changed={str(changed).lower()}")
    if changed and args.write:
        save_portfolio(args.portfolio, portfolio)
        print(f"wrote {args.portfolio}")
    elif changed:
        print("dry-run: add --write to save")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
