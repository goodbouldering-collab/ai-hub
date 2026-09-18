"""Read-only HTTP verification of the committed editorial release on Workers."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
import requests

from verify_editorial_release import (EDITORIAL_HREF, LEGACY_ART, SOFT_IMAGE_NAMES,
                                     assert_no_personal_images, assert_playground,
                                     assert_soft_image_placement)


PRODUCTION_URL = "https://aiclimb.aiclimb.workers.dev"
PUBLIC_ROUTES = (
    ("/", "index.html"),
    ("/speaker.html", "speaker.html"),
    ("/ai-news/", "ai-news/index.html"),
    ("/blog/", "blog/index.html"),
    ("/blog/2026-08-30-switchbot-ai-mind-clip.html", "blog/2026-08-30-switchbot-ai-mind-clip.html"),
    ("/blog/2026-09-18-cloudflare-emdash-webmcp.html", "blog/2026-09-18-cloudflare-emdash-webmcp.html"),
    ("/lectures/2026-04-ai-kihon.html", "lectures/2026-04-ai-kihon.html"),
    ("/instagram-feed.css", "instagram-feed.css"),
    ("/instagram-feed.js", "instagram-feed.js"),
    ("/design-system/studio/editorial.css", "design-system/studio/editorial.css"),
    ("/design-system/studio/studio.css", "design-system/studio/studio.css"),
    ("/design-system/studio/studio.js", "design-system/studio/studio.js"),
    ("/design-system/studio/soft-playground.css", "design-system/studio/soft-playground.css"),
    ("/design-system/studio/soft-playground.js", "design-system/studio/soft-playground.js"),
    *((f"/design-system/studio/images/soft-{name}.webp", f"design-system/studio/images/soft-{name}.webp")
      for name in SOFT_IMAGE_NAMES),
)
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def route_identity(path: str) -> str:
    """Cloudflare can serve index.html, directory and clean .html URLs alike."""
    if path.endswith("/index.html"):
        path = path[:-len("index.html")]
    elif path.endswith(".html"):
        path = path[:-len(".html")]
    return path.rstrip("/") or "/"


def same_origin(url: str, base_url: str) -> bool:
    target, origin = urlsplit(url), urlsplit(base_url)
    return (target.scheme, target.netloc) == (origin.scheme, origin.netloc)


def fetch(session: requests.Session, base_url: str, path: str, *, follow: bool = True):
    """Only GET; refuse redirects to another host or another public resource."""
    url, redirects = base_url + path, []
    for _ in range(6):
        response = session.get(url, allow_redirects=False, timeout=(10, 30))
        require(same_origin(response.url, base_url), f"Response origin changed: {path}")
        if not follow or response.status_code not in REDIRECT_STATUSES:
            return response, redirects
        location = response.headers.get("Location")
        require(bool(location), f"Redirect without Location: {path}")
        next_url = urljoin(url, location)
        next_parts = urlsplit(next_url)
        require(same_origin(next_url, base_url), f"Cross-origin redirect refused: {path}")
        require(not next_parts.query and not next_parts.fragment and
                route_identity(next_parts.path) == route_identity(path),
                f"Redirect to another resource refused: {path}")
        redirects.append({"status": response.status_code, "from": url, "to": next_url})
        url = next_url
    raise ValueError(f"Too many redirects: {path}")


def response_summary(response, path: str, redirects: list) -> dict:
    return {"path": path, "status": response.status_code, "final_url": response.url,
            "redirects": redirects, "sha256": digest(response.content),
            "content_type": response.headers.get("Content-Type", ""),
            "cache_control": response.headers.get("Cache-Control", ""),
            "cf_ray": response.headers.get("CF-Ray", "")}


def editorial_tag(soup: BeautifulSoup, base_url: str) -> bool:
    tags = soup.select('link#studio-editorial[rel="stylesheet"]')
    if len(tags) != 1:
        return False
    target = urljoin(base_url + "/", tags[0].get("href", ""))
    parts = urlsplit(target)
    return (same_origin(target, base_url) and parts.path == "/design-system/studio/editorial.css"
            and parts.query == urlsplit(EDITORIAL_HREF).query and not parts.fragment)


def verify(release: Path, base_url: str, *, session=None) -> dict:
    proof = {"checked_at": datetime.now(timezone.utc).isoformat(), "base_url": base_url,
             "release": str(release.resolve()), "passed": False, "results": [], "errors": []}
    try:
        require(base_url.rstrip("/") == PRODUCTION_URL,
                f"Only the registered production origin is allowed: {PRODUCTION_URL}")
        base_url = base_url.rstrip("/")
        manifest = json.loads((release / "verification.json").read_text(encoding="utf-8"))
        proof["source_sha"] = manifest.get("source_sha")
        require(bool(re.fullmatch(r"[0-9a-f]{40}", manifest.get("source_sha", ""))),
                "Release source SHA is missing or invalid")
        require(manifest.get("source_inputs_clean") is True, "Release was not built from clean committed inputs")
        for _, name in PUBLIC_ROUTES:
            expected = manifest["assets"].get(name)
            require(expected and digest((release / "public" / name).read_bytes()) == expected,
                    f"Local release asset does not match its manifest: {name}")
        image_hashes = [manifest["assets"][f"design-system/studio/images/soft-{name}.webp"]
                        for name in SOFT_IMAGE_NAMES]
        require(len(set(image_hashes)) == 13, "The 13 design image contents must be distinct")
    except (ValueError, KeyError, OSError, TypeError) as error:
        proof["errors"].append(str(error))
        return proof

    owns_session = session is None
    if owns_session:
        session = requests.Session()
        session.trust_env = False  # Never load netrc credentials for public checks.
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; AIConsultReleaseVerifier/1.0)",
                                "Cache-Control": "no-cache"})
    try:
        for path, name in PUBLIC_ROUTES:
            result = {"path": path, "asset": name, "passed": False}
            try:
                response, redirects = fetch(session, base_url, path)
                result.update(response_summary(response, path, redirects))
                require(response.status_code == 200, f"Expected HTTP 200, got {response.status_code}")
                result["matches_release"] = result["sha256"] == manifest["assets"][name]
                require(result["matches_release"], "Production bytes differ from the release manifest")
                if name.endswith(".html"):
                    soup = BeautifulSoup(response.content, "html.parser")
                    assert_no_personal_images(soup, name)
                    require(not soup.select(".studio-scene-layer"), "Removed hero inset is still present")
                    require(not LEGACY_ART.search(str(soup).replace("\\/", "/")), "Retired artwork is still referenced")
                    assert_playground(soup, name, expected=name == "index.html")
                    assert_soft_image_placement(soup, name)
                    result["personal_photo_not_rendered"] = True
                    canonicals = soup.select('link[rel="canonical"]')
                    canonical = canonicals[0].get("href", "") if len(canonicals) == 1 else ""
                    canonical_parts = urlsplit(canonical)
                    result["canonical"] = canonical
                    result["canonical_valid"] = (same_origin(canonical, base_url) and
                        not canonical_parts.query and not canonical_parts.fragment and
                        route_identity(canonical_parts.path) == route_identity(path))
                    require(result["canonical_valid"], "Missing or incorrect production canonical")
                    result["editorial_tag_present"] = editorial_tag(soup, base_url)
                    require(result["editorial_tag_present"], "Editorial stylesheet tag missing or incorrect")
                    if name == "index.html":
                        result["playground_after_news"] = True
                        result["distinct_frame_images"] = 11
                elif name.endswith((".css", ".js")):
                    require(not LEGACY_ART.search(response.content.decode("utf-8")),
                            "Retired artwork is still referenced in the presentation asset")
                result["passed"] = True
            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                result["error"] = str(error)
                proof["errors"].append(f"{path}: {error}")
            proof["results"].append(result)

        for path in ("/health", "/admin", "/admin/login", "/api/admin/ping"):
            result = {"path": path, "passed": False}
            try:
                response, redirects = fetch(session, base_url, path, follow=False)
                result.update(response_summary(response, path, redirects))
                expected_status = {"/admin": 303, "/api/admin/ping": 401}.get(path, 200)
                require(response.status_code == expected_status,
                        f"Expected HTTP {expected_status}, got {response.status_code}")
                if path == "/health":
                    health = response.json()
                    require(isinstance(health, dict), "Health response is not a JSON object")
                    result["json_object_valid"] = True
                elif path == "/admin":
                    target = urljoin(base_url + path, response.headers.get("Location", ""))
                    result["location"] = target
                    result["login_redirect_valid"] = (same_origin(target, base_url) and
                        urlsplit(target).path == "/admin/login")
                    require(result["login_redirect_valid"], "Admin redirect does not lead to the local login")
                elif path == "/admin/login":
                    result["editorial_tag_present"] = editorial_tag(BeautifulSoup(response.content, "html.parser"), base_url)
                    require(result["editorial_tag_present"], "Login editorial stylesheet tag missing or incorrect")
                result["passed"] = True
            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                result["error"] = str(error)
                proof["errors"].append(f"{path}: {error}")
            proof["results"].append(result)
    finally:
        if owns_session:
            session.close()
    proof["passed"] = not proof["errors"]
    return proof


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, type=Path)
    parser.add_argument("--base-url", default=PRODUCTION_URL)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    proof = verify(args.release.resolve(), args.base_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": proof["passed"], "source_sha": proof.get("source_sha"),
                      "checked": len(proof["results"]), "errors": proof["errors"],
                      "proof": str(args.output.resolve())}, ensure_ascii=False, indent=2))
    return 0 if proof["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
