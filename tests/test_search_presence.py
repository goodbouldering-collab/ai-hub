import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from core.search_presence import apply_search_presence, enhance_search_html


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config/search-presence.json"
BASE = "https://aiclimb.aiclimb.workers.dev"


def page(schema=None, path="/blog/example.html", extra="", newline="\n"):
    ld = '<script type="application/ld+json">' + json.dumps(schema or {}, ensure_ascii=False) + "</script>"
    return newline.join(['<!doctype html><html lang="ja"><head>', '<meta charset="utf-8">', '<title>AI相談</title>',
        '<meta name="description" content="公開ページの説明">', '<meta property="og:title" content="記事のタイトル">',
        f'<link rel="canonical" href="{BASE}{path}">', '<style>body { color: #123; }</style>',
        '<script>const untouched = "<value>";</script>', extra, ld, '</head><body>',
        '<h1>記事のタイトル</h1><p>既存の本文 &amp; 内容</p>', '<script>window.flag = true;</script>', '</body></html>'])


def graph(html):
    soup = BeautifulSoup(html, "html.parser")
    return json.loads(soup.select_one('script[type="application/ld+json"]').get_text())["@graph"]


class SearchPresenceTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_body_scripts_and_styles_preserved_for_crlf_and_idempotent(self):
        old = page({"@type": "BlogPosting", "headline": "記事", "datePublished": "2026-08-01", "dateModified": "2026-08-21"}, newline="\r\n")
        updated = enhance_search_html(old, "blog/example.html", self.config)
        self.assertEqual(old.split('</head>', 1)[1], updated.split('</head>', 1)[1])
        self.assertIn('<style>body { color: #123; }</style>', updated)
        self.assertIn('<script>const untouched = "<value>";</script>', updated)
        self.assertEqual(updated, enhance_search_html(updated, "blog/example.html", self.config))
        article = next(n for n in graph(updated) if n.get("@type") == "BlogPosting")
        self.assertEqual(article["datePublished"], "2026-08-01")
        self.assertEqual(article["dateModified"], "2026-08-21")
        self.assertEqual(article["headline"], "記事")
        self.assertEqual(article["url"], BASE + "/blog/example")

    def test_publisher_author_ids_and_legacy_graph_references(self):
        schema = {"@graph": [{"@type": "Organization", "@id": BASE + "/#organization", "name": "AI相談"},
            {"@type": ["LearningResource", "Article"], "@id": BASE + "/lectures/example.html#learning-resource", "headline": "講習",
             "author": {"@id": BASE + "/speaker.html#person"}, "publisher": {"@id": BASE + "/#organization"}}]}
        nodes = graph(enhance_search_html(page(schema, "/lectures/example.html"), "lectures/example.html", self.config))
        article = next(n for n in nodes if isinstance(n.get("@type"), list))
        self.assertEqual(article["author"]["@id"], BASE + "/#yui")
        self.assertEqual(article["publisher"]["@id"], BASE + "/#business")
        ids = {n["@id"] for n in nodes}
        self.assertIn(article["mainEntityOfPage"]["@id"], ids)
        self.assertIn(BASE + "/lectures/example#learning-resource", ids)

    def test_real_person_and_archive_type_without_fabricated_fields(self):
        speaker = graph(enhance_search_html(page({"@type": "Person", "name": "講師紹介"}, "/speaker.html"), "speaker.html", self.config))
        person = next(n for n in speaker if n.get("@type") == "Person")
        self.assertEqual(person["name"], "由井 辰美")
        self.assertEqual(person["url"], BASE + "/speaker")
        archive = graph(enhance_search_html(page({"@type": "BlogPosting", "headline": "ブログ"}, "/blog/index.html"), "blog/index.html", self.config))
        self.assertTrue(any(n.get("@type") == "CollectionPage" for n in archive))
        self.assertFalse(any(n.get("@type") == "BlogPosting" for n in archive))
        business = next(n for n in archive if n.get("@type") == "ProfessionalService")
        for field in ("telephone", "openingHours", "aggregateRating", "review", "sameAs", "founder"):
            self.assertNotIn(field, business)

    def test_home_removes_false_breadcrumb_and_preserves_course_offer(self):
        course = {"@type": "Course", "@id": BASE + "/#course", "name": "AI講習", "offers": {"@type": "Offer", "price": "5500", "priceCurrency": "JPY"}}
        old = page({"@graph": [course, {"@type": "BreadcrumbList", "itemListElement": []}]}, "/")
        updated = enhance_search_html(old, "index.html", self.config)
        nodes = graph(updated)
        self.assertFalse(any(n.get("@type") == "BreadcrumbList" for n in nodes))
        self.assertEqual(next(n for n in nodes if n.get("@type") == "Course"), course)
        self.assertEqual(updated, enhance_search_html(updated, "index.html", self.config))

    def test_private_paths_and_existing_noindex_excluded_from_discovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path, source in {"index.html": page(path="/"), "blog/example.html": page({"@type": "BlogPosting", "dateModified": "2026-08-21"}),
                "speed-monitor.html": page(path="/speed-monitor.html"), "design-system/index.html": page(path="/design-system/"),
                "watch/private.html": page(path="/watch/private.html"), "blog/codex-update-log.html": page(path="/blog/codex-update-log.html"),
                "draft.html": page(path="/draft.html", extra='<meta name="robots" content="noindex,follow">')}.items():
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(source.encode())
            original_watch = (root / "watch/private.html").read_bytes()
            result = apply_search_presence(root, CONFIG_PATH)
            self.assertEqual(result["indexed_pages"], 2)
            self.assertEqual((root / "watch/private.html").read_bytes(), original_watch)
            soup = BeautifulSoup((root / "speed-monitor.html").read_text(), "html.parser")
            self.assertEqual(soup.find("meta", attrs={"name": "robots"})["content"], "noindex, nofollow")
            sitemap = ET.parse(root / "sitemap.xml")
            urls = [n.text for n in sitemap.findall('.//{*}loc')]
            self.assertEqual(urls, [BASE + "/", BASE + "/blog/example"])
            self.assertEqual(sitemap.findall('.//{*}lastmod')[0].text, "2026-08-21")
            for name in ("llms.txt", "llms-full.txt"):
                content = (root / name).read_text(encoding="utf-8")
                self.assertNotIn("/watch/", content)
                self.assertNotIn("/speed-monitor", content)
                self.assertNotIn("/draft", content)
            self.assertNotIn("Disallow: /design-system/", (root / "robots.txt").read_text())
            self.assertEqual(apply_search_presence(root, CONFIG_PATH)["changed_files"], [])

    def test_verification_token_opt_in_and_canonical_rejects_other_sites(self):
        original = page()
        self.assertNotIn("google-site-verification", enhance_search_html(original, "blog/example.html", self.config))
        self.config["google_site_verification"] = "PUBLIC-VERIFICATION-ID"
        self.assertIn('content="PUBLIC-VERIFICATION-ID"', enhance_search_html(original, "blog/example.html", self.config))
        with self.assertRaisesRegex(ValueError, "Unexpected canonical"):
            enhance_search_html(original.replace(BASE + "/blog/example.html", "https://example.com/"), "blog/example.html", self.config)

    def test_metadata_order_survives_presentation_style_reappend(self):
        style = '<style id="editorial-home-style">.hero { color: blue; }</style>'
        old = page(path="/", newline="\r\n").replace('</head>', style + '</head>')
        once = enhance_search_html(old, "index.html", self.config)
        presentation_pass = once.replace(style, '').replace('</head>', style + '</head>')
        self.assertEqual(once, enhance_search_html(presentation_pass, "index.html", self.config))
        no_schema = old.replace('<script type="application/ld+json">{}</script>', '')
        new_schema = enhance_search_html(no_schema, "index.html", self.config)
        self.assertIn(b'<meta charset="utf-8">', new_schema.encode('utf-8')[:1024])

    def test_offer_billing_unit_and_minimum_follow_visible_pricing(self):
        support = {"@type": "Service", "@id": BASE + "/#service-ai-support", "name": "AI伴走支援", "offers": {"@type": "Offer", "price": "88000", "priceCurrency": "JPY"}}
        home = enhance_search_html(page({"@graph": [support]}, "/"), "index.html", self.config)
        offer = next(n for n in graph(home) if n.get("@id") == support["@id"])["offers"]
        self.assertNotIn("price", offer)
        self.assertEqual(offer["priceSpecification"]["price"], "88000")
        self.assertEqual(offer["priceSpecification"]["unitText"], "月")
        self.assertEqual(home, enhance_search_html(home, "index.html", self.config))
        app = {"@type": "Service", "name": "AIアプリサイト", "offers": {"@type": "Offer", "price": "99000", "priceCurrency": "JPY"}}
        html = enhance_search_html(page(app, "/ai-app-site/"), "ai-app-site/index.html", self.config)
        offer = next(n for n in graph(html) if n.get("@type") == "Service")["offers"]
        self.assertNotIn("price", offer)
        self.assertEqual(offer["priceSpecification"], {"@type": "PriceSpecification", "minPrice": 99000, "priceCurrency": "JPY"})
        self.assertEqual(html, enhance_search_html(html, "ai-app-site/index.html", self.config))

    def test_unrated_testimonials_stay_visible_without_invalid_review_markup(self):
        testimonial = {"@type": "Review", "reviewBody": "ゼロから自分で作れました。", "author": {"@type": "Person", "name": "受講者（匿名）"}}
        rated = {"@type": "Review", "reviewBody": "役立ちました。", "author": {"@type": "Person", "name": "評価済み受講者"}, "reviewRating": {"@type": "Rating", "ratingValue": 4, "bestRating": 5}}
        courses = [{"@type": "Course", "@id": BASE + "/#unrated-course", "name": "AI講習", "review": [testimonial]},
                   {"@type": "Service", "@id": BASE + "/#unrated-service", "name": "AI相談", "review": testimonial},
                   {"@type": "Course", "@id": BASE + "/#mixed-course", "name": "講習2", "review": [testimonial, rated]}]
        original = page({"@graph": courses}, "/", newline="\r\n").replace('<body>', '<body><blockquote>ゼロから自分で作れました。</blockquote>')
        updated = enhance_search_html(original, "index.html", self.config)
        self.assertEqual(original.split('</head>', 1)[1], updated.split('</head>', 1)[1])
        nodes = {node["@id"]: node for node in graph(updated)}
        self.assertNotIn("review", nodes[BASE + "/#unrated-course"])
        self.assertNotIn("review", nodes[BASE + "/#unrated-service"])
        self.assertEqual(nodes[BASE + "/#mixed-course"]["review"], [rated])
        self.assertNotIn("aggregateRating", json.dumps(nodes))
        self.assertEqual(updated, enhance_search_html(updated, "index.html", self.config))


if __name__ == "__main__":
    unittest.main()
