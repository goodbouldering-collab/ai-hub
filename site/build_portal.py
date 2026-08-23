"""
CEO ポータルトップページを生成する。

outputs/portal_index.html → site/dist/index.html を上書き。

呼び出し方:
    python site/build_portal.py           # ポータルトップのみ再生成
    python site/build_portal.py --dry-run # dist に書かず標準出力（確認用）

run.py から末尾ステップで呼ばれる（[7/6] CEOポータル生成）。
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    class _MiniYaml:
        """Small fallback for this site's simple config/frontmatter YAML."""

        @staticmethod
        def _value(raw: str):
            value = raw.strip()
            if not value:
                return ""
            if value in {"null", "NULL", "~"}:
                return None
            if value in {"true", "True"}:
                return True
            if value in {"false", "False"}:
                return False
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
            if value.startswith("[") and value.endswith("]"):
                body = value[1:-1].strip()
                if not body:
                    return []
                return [_MiniYaml._value(part.strip()) for part in body.split(",")]
            return value

        @classmethod
        def safe_load(cls, text: str):
            data: dict = {}
            section_key = ""
            current_item: dict | None = None
            pending_list_key = ""
            for raw_line in text.splitlines():
                if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                    continue
                line = raw_line.rstrip()
                indent = len(line) - len(line.lstrip(" "))
                stripped = line.strip()
                if indent == 0 and stripped.endswith(":"):
                    section_key = stripped[:-1].strip()
                    data[section_key] = []
                    current_item = None
                    pending_list_key = ""
                    continue
                if section_key and indent <= 2 and stripped.startswith("- "):
                    value = stripped[2:].strip()
                    if ":" in value:
                        key, item_value = value.split(":", 1)
                        current_item = {key.strip(): cls._value(item_value)}
                        data[section_key].append(current_item)
                        pending_list_key = key.strip() if not item_value.strip() else ""
                    else:
                        data[section_key].append(cls._value(value))
                    continue
                if indent == 0 and ":" in stripped:
                    key, value = stripped.split(":", 1)
                    data[key.strip()] = cls._value(value)
                    continue
                if current_item is not None and indent >= 2:
                    if stripped.startswith("- ") and pending_list_key:
                        current_item.setdefault(pending_list_key, []).append(cls._value(stripped[2:].strip()))
                    elif ":" in stripped:
                        key, value = stripped.split(":", 1)
                        key = key.strip()
                        if value.strip():
                            current_item[key] = cls._value(value)
                            pending_list_key = ""
                        else:
                            current_item[key] = []
                            pending_list_key = key
            return data

    yaml = _MiniYaml()

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_navigation import render_desktop_navigation, render_mobile_navigation
from blog_freshness import blog_date_label, effective_blog_date, is_new_blog

BUSINESSES_YAML = ROOT / "config" / "businesses.yaml"
PROFILE_YAML = ROOT / "config" / "profile.yaml"
PORTFOLIO_YAML = ROOT / "config" / "portfolio.yaml"
SPEAKER_MD = ROOT / "content" / "speaker.md"
DIST = ROOT / "site" / "dist"
LECTURES_DIR = ROOT / "content" / "lectures"
BLOG_DIR = ROOT / "content" / "blog"

SITE_URL = os.environ.get("AIHUB_SITE_URL", os.environ.get("AIWATCH_SITE_URL", "https://aiclimb.vercel.app")).rstrip("/")

OWNER_NAME = "由井 辰美"
OWNER_EMAIL = "goodbouldering@gmail.com"
SITE_BRAND = "AI相談"
SITE_LEGACY_NAME = "AIハブ"
SITE_BROWSER_TITLE = "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】"
OWNER_SUBTITLE = "クライミング歴30年・9事業を回す滋賀のAI講師"
OWNER_TAGLINE = "AIの今と、次の一手がわかる。"
DIAGNOSIS_FREE_CONSULT_BOOK_URL = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
AI_AGENT_COURSE_URL = "https://goodbouldering.com/?pid=188553378"
AI_APP_SELFBUILD_BOOK_URL = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
MONTHLY_SUPPORT_BOOK_URL = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/V57YTNICA2KV2TN7ENARAVQE"
MONTHLY_SUPPORT_PRICE_YEN = 88_000
MONTHLY_SUPPORT_PRICE_JPY = str(MONTHLY_SUPPORT_PRICE_YEN)
MONTHLY_SUPPORT_PRICE_LABEL = "月額88,000円"
MONTHLY_SUPPORT_PRICE_DETAIL = f"{MONTHLY_SUPPORT_PRICE_LABEL}（税込）×6ヶ月"
AI_SALON_CHECKOUT_URL = "/api/square/ai-salon-checkout"


COLOR_MAP = {
    "blue":   ("rgba(122,162,255,.45)", "rgba(100,140,255,.20)"),
    "purple": ("rgba(199,125,255,.45)", "rgba(180,100,255,.20)"),
    "green":  ("rgba(100,220,160,.45)", "rgba(80,200,140,.20)"),
    "orange": ("rgba(255,165,80,.45)",  "rgba(240,145,60,.20)"),
    "pink":   ("rgba(255,122,182,.45)", "rgba(240,100,160,.20)"),
    "teal":   ("rgba(80,220,210,.45)",  "rgba(60,200,190,.20)"),
    "yellow": ("rgba(255,210,80,.45)",  "rgba(240,190,60,.20)"),
    "red":    ("rgba(255,100,100,.45)", "rgba(240,80,80,.20)"),
    "cyan":   ("rgba(80,210,240,.45)",  "rgba(60,190,220,.20)"),
    "gray":   ("rgba(160,160,180,.30)", "rgba(140,140,160,.15)"),
}

FAVICON_HEAD_HTML = (
    "<link rel='icon' type='image/svg+xml' href='/favicon-20260725.svg'>"
    "<link rel='icon' type='image/png' sizes='32x32' href='/favicon-20260725-32x32.png'>"
    "<link rel='icon' type='image/png' sizes='16x16' href='/favicon-20260725-16x16.png'>"
    "<link rel='shortcut icon' href='/favicon-20260725.ico'>"
    "<link rel='apple-touch-icon' sizes='180x180' href='/apple-touch-icon-20260725.png'>"
    "<link rel='manifest' href='/site-20260725.webmanifest'>"
    "<link rel='mask-icon' href='/favicon-20260725.svg' color='#5367D9'>"
    "<meta name='application-name' content='AI相談'>"
    "<meta name='apple-mobile-web-app-title' content='AI相談'>"
    "<meta name='apple-mobile-web-app-capable' content='yes'>"
    "<meta name='mobile-web-app-capable' content='yes'>"
    "<meta name='theme-color' content='#172033'>"
)

ADMIN_BUTTON_HTML = """
<script>
(function(){
  function reveal(){
    var h = location.hostname;
    if (h !== "localhost" && h !== "127.0.0.1" && h !== "0.0.0.0" && !h.endsWith(".localhost")) return;
    document.querySelectorAll("[data-localhost-only]").forEach(function(el){
      el.style.display = "";
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", reveal);
  } else {
    reveal();
  }
})();
</script>
"""


OG_IMAGE_URL = SITE_URL + "/img/hero-codex-claude-imagegen-20260616.png"


def _build_ogp(title: str, description: str, page_url: str, *, image: str | None = None) -> str:
    img = image or OG_IMAGE_URL
    return "".join([
        f"<meta property='og:title' content='{html.escape(title, quote=True)}'>",
        f"<meta property='og:description' content='{html.escape(description, quote=True)}'>",
        f"<meta property='og:url' content='{html.escape(page_url, quote=True)}'>",
        "<meta property='og:type' content='website'>",
        f"<meta property='og:site_name' content='{html.escape(SITE_BRAND, quote=True)}'>",
        "<meta property='og:locale' content='ja_JP'>",
        f"<meta property='og:image' content='{html.escape(img, quote=True)}'>",
        "<meta property='og:image:width' content='1672'>",
        "<meta property='og:image:height' content='941'>",
        f"<meta property='og:image:alt' content='{html.escape(title, quote=True)}'>",
        "<meta name='twitter:card' content='summary_large_image'>",
        f"<meta name='twitter:title' content='{html.escape(title, quote=True)}'>",
        f"<meta name='twitter:description' content='{html.escape(description, quote=True)}'>",
        f"<meta name='twitter:image' content='{html.escape(img, quote=True)}'>",
    ])


def _testimonial_reviews(course_key: str) -> list[dict]:
    for group in COURSE_TESTIMONIALS + (SALON_TESTIMONIAL_GROUP,):
        if group["key"] != course_key:
            continue
        return [
            {
                "@type": "Review",
                "name": testimonial["title"],
                "reviewBody": testimonial["body"],
                "author": {
                    "@type": "Person",
                    "name": testimonial["author_label"],
                },
            }
            for testimonial in group["testimonials"]
        ]
    return []


def _build_jsonld_website() -> str:
    """TOPで表示している事業・講師・サービス情報だけを@graphで出力する。

    FAQのリッチリザルト対応終了後はFAQPageを検索施策として出力せず、
    現在の集約トップに表示されていない旧セクションのデータも含めない。
    """
    org_id = SITE_URL + "/#business"
    person_id = SITE_URL + "/#yui"
    web_id = SITE_URL + "/#website"

    local_business = {
        "@type": ["ProfessionalService", "LocalBusiness"],
        "@id": org_id,
        "name": SITE_BRAND,
        "alternateName": [SITE_LEGACY_NAME, "AI相談。彦根", "AI Hub Hikone", "AI講習 彦根"],
        "url": SITE_URL,
        "image": OG_IMAGE_URL,
        "email": OWNER_EMAIL,
        "priceRange": "¥¥",
        "founder": {"@id": person_id},
        "areaServed": [
            {"@type": "City", "name": "彦根市"},
            {"@type": "AdministrativeArea", "name": "滋賀県湖東地域"},
            {"@type": "AdministrativeArea", "name": "滋賀県"},
        ],
        "address": {
            "@type": "PostalAddress",
            "postalCode": "522-0043",
            "addressRegion": "滋賀県",
            "addressLocality": "彦根市",
            "streetAddress": "小泉町34-8",
            "addressCountry": "JP",
        },
        "description": "滋賀県彦根市を拠点に、中小事業者・地域団体・個人事業者向けのAI相談、AIエージェント講習、近日開始で現在仮運用中の有料AIオンラインサロン、Codex・Claude Code実践、画像生成、受講資料公開、実例紹介、Web/業務システム制作、補助金を使ったAI導入支援を行う。9事業を実際に回す現役オーナーが、相談から講習、実装、公開、運用定着まで伴走する。",
        "knowsAbout": [
            "AI相談", "AIエージェント講習", "AIオンラインサロン", "ChatGPT", "Claude Code", "Codex", "画像生成", "AI業務改善",
            "LLMO（AI検索最適化）", "SEO", "MEO", "YouTube SEO", "Reels導線",
            "業務自動化", "AI導入補助金", "デジタル化補助金", "中小企業DX",
        ],
        "slogan": OWNER_TAGLINE,
    }

    person = {
        "@type": "Person",
        "@id": person_id,
        "name": OWNER_NAME,
        "jobTitle": "AI講師 / Web経営コンサルタント / 複数事業オーナー",
        "email": OWNER_EMAIL,
        "url": SITE_URL + "/speaker.html",
        "image": SITE_URL + "/img/speaker-portrait-v2.webp",
        "worksFor": {"@id": org_id},
        "knowsAbout": ["生成AI", "クライミング", "店舗経営", "マーケティング", "補助金活用"],
        "description": "クライミング歴30年。ボルダリングカフェ「グッぼる」をはじめ9事業を経営しながら、滋賀・彦根の中小事業者にAI相談、AIエージェント講習、SNS/LLMO導線づくりを教える。経営者でありコードを書く実装者でもある二重性が強み。",
    }

    website = {
        "@type": "WebSite",
        "@id": web_id,
        "name": SITE_BRAND,
        "url": SITE_URL,
        "inLanguage": "ja",
        "publisher": {"@id": org_id},
        "description": "滋賀・彦根の中小事業者向けAI相談、AIエージェント講習、近日開始・現在仮運用中の有料オンラインサロン、受講資料、実例、講師紹介の資料センター。増え続けるAI情報から、仕事に使えるものと今やることを整理する。",
    }

    ai_agent_title = "AIエージェント講習 120分"
    selfbuild_title = "AIアプリサイト自作講習・相談 120分"
    salon_title = "AIオンラインサロン｜近日開始"
    support_title = "AI伴走支援 いっしょに導入"

    # 受講プランを Service + Offer として構造化（_render_packages の items と整合）
    plans = [
        (ai_agent_title, "Codexを使い、仕事を小さく分けて頼む、変更点を確かめる、必要なら直す、次回も使える手順として残すAIエージェント講習。資料、告知、業務改善、Web制作を題材に、人が判断しながら成果物を完成させる型を120分で身につける。", "5500", "5500", "Course"),
        (salon_title, "月額2,200円（税込）。正式開始に向けて現在は仮運用中で、登録中の方にはテスト運用へご協力いただいています。Square決済後にLINE参加案内を表示します。", "2200", "2200", "CommunityService"),
        (support_title, "組織がAIアプリサイトを自作・改善・運用できるまで学ぶ6ヶ月。上の制作サービスで行う課題整理、設計、公開、改善を、組織の担当者がAIと進められる状態を目指す。", MONTHLY_SUPPORT_PRICE_JPY, MONTHLY_SUPPORT_PRICE_JPY, "Service"),
        (selfbuild_title, "作りたいAIアプリサイトを題材に、目的整理、AIへの頼み方、コード確認、修正、安全な公開までを個別に進める講習・相談。相談だけで終わらず、自分で作って直せる状態を120分で目指す。", "11000", "11000", "Course"),
    ]
    plan_schema = {
        ai_agent_title: {
            "@id": SITE_URL + "/#course-ai-agent",
            "@type": "Course",
            "testimonial_key": "ai-agent",
            "timeRequired": "PT2H",
            "courseMode": ["onsite", "online"],
            "inLanguage": "ja",
            "teaches": [
                "AIエージェントのインストールと基本操作",
                "IDEを使ったAIエージェント実践",
                "依頼、確認、修正、次回手順への保存",
            ],
        },
        salon_title: {
            "@id": SITE_URL + "/#service-ai-salon",
            "@type": "Service",
            "testimonial_key": "ai-salon",
        },
        support_title: {
            "@id": SITE_URL + "/#service-ai-support",
            "@type": "Service",
            "testimonial_key": "ai-support",
        },
        selfbuild_title: {
            "@id": SITE_URL + "/#course-ai-app-selfbuild",
            "@type": "Course",
            "testimonial_key": "ai-app-selfbuild",
            "timeRequired": "PT2H",
            "courseMode": ["onsite", "online"],
            "inLanguage": "ja",
            "teaches": [
                "AIアプリサイトの目的整理と小さな仕様設計",
                "AIへの依頼、変更差分、データ、セキュリティの確認",
                "修正、PC・スマホ確認、GitHubとクラウドを使った公開工程",
            ],
        },
    }
    services = []
    for name, desc, lo, hi, stype in plans:
        schema = plan_schema.get(name, {})
        node_type = schema.get("@type", "Service")
        service = {
            "@type": node_type,
            "name": name,
            "description": desc,
            "provider": {"@id": org_id},
        }
        if schema.get("@id"):
            service["@id"] = schema["@id"]
        if node_type == "Course":
            service.update({
                "timeRequired": schema["timeRequired"],
                "courseMode": schema["courseMode"],
                "inLanguage": schema["inLanguage"],
                "teaches": schema["teaches"],
            })
        else:
            service["serviceType"] = stype
            service["areaServed"] = {"@type": "AdministrativeArea", "name": "滋賀県"}
        testimonial_key = schema.get("testimonial_key")
        if testimonial_key:
            service["review"] = _testimonial_reviews(testimonial_key)
        if lo is not None and hi is not None:
            offer = {
                "@type": "Offer",
                "priceCurrency": "JPY",
                "availability": "https://schema.org/InStock",
            }
            if lo == hi:
                offer["price"] = lo
            else:
                offer["priceSpecification"] = {
                    "@type": "PriceSpecification",
                    "minPrice": lo, "maxPrice": hi, "priceCurrency": "JPY",
                }
            service["offers"] = offer
        if name == salon_title:
            service["url"] = SITE_URL + AI_SALON_CHECKOUT_URL
            offer["url"] = SITE_URL + AI_SALON_CHECKOUT_URL
            offer["priceSpecification"] = {
                "@type": "UnitPriceSpecification",
                "price": "2200",
                "priceCurrency": "JPY",
                "valueAddedTaxIncluded": True,
                "billingDuration": "P1M",
            }
        if name == ai_agent_title:
            offer["url"] = AI_AGENT_COURSE_URL
            service["url"] = AI_AGENT_COURSE_URL
        if name == selfbuild_title:
            offer["url"] = AI_APP_SELFBUILD_BOOK_URL
            service["url"] = AI_APP_SELFBUILD_BOOK_URL
        if name == support_title:
            offer["url"] = MONTHLY_SUPPORT_BOOK_URL
            service["url"] = MONTHLY_SUPPORT_BOOK_URL
        services.append(service)

    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "講習・相談コース", "item": SITE_URL + "/#packages"},
            {"@type": "ListItem", "position": 3, "name": "講師紹介", "item": SITE_URL + "/#speaker"},
            {"@type": "ListItem", "position": 4, "name": "受講資料", "item": SITE_URL + "/#lectures"},
            {"@type": "ListItem", "position": 5, "name": "FAQ", "item": SITE_URL + "/#faq"},
        ],
    }

    graph = {"@context": "https://schema.org", "@graph": [local_business, person, website, *services, breadcrumb]}
    return json.dumps(graph, ensure_ascii=False)


def _load_businesses() -> list[dict]:
    if not BUSINESSES_YAML.exists():
        return []
    try:
        data = yaml.safe_load(BUSINESSES_YAML.read_text(encoding="utf-8")) or {}
        return data.get("businesses") or []
    except Exception as e:
        print(f"[!] businesses.yaml load error: {e}")
        return []


def _load_recent_lectures(limit: int = 3) -> list[dict]:
    if not LECTURES_DIR.exists():
        return []
    items: list[dict] = []
    for f in sorted(LECTURES_DIR.glob("*.md"), reverse=True):
        raw = f.read_text(encoding="utf-8")
        meta: dict = {}
        if raw.startswith("---"):
            try:
                end = raw.index("\n---", 3)
                fm = raw[3:end].strip()
                meta = yaml.safe_load(fm) or {}
            except Exception:
                pass
        if meta.get("listed") is False:
            continue
        items.append({
            "slug": f.stem,
            "title": str(meta.get("title") or f.stem),
            "date": str(meta.get("date") or ""),
            "summary": str(meta.get("summary") or ""),
        })
        if len(items) >= limit:
            break
    return items


def _load_speaker() -> dict:
    """speaker.md の frontmatter + 「プロフィール」段落だけ取り出す（LP要約用）。
    本文の全文は詳細ページ speaker.html 側が担う。ソースは改変しない。"""
    if not SPEAKER_MD.exists():
        return {}
    raw = SPEAKER_MD.read_text(encoding="utf-8")
    meta: dict = {}
    body = raw
    if raw.startswith("---"):
        try:
            end = raw.index("\n---", 3)
            meta = yaml.safe_load(raw[3:end].strip()) or {}
            body = raw[end + 4:]
        except Exception:
            pass
    # 「## プロフィール」直後〜次の「## 」までを要約段落として抽出
    intro = ""
    lines = body.splitlines()
    capture = False
    buf: list[str] = []
    for ln in lines:
        if ln.strip().startswith("## プロフィール"):
            capture = True
            continue
        if capture and ln.strip().startswith("## "):
            break
        if capture and ln.strip() and not ln.strip().startswith(">"):
            buf.append(ln.strip())
    intro = " ".join(buf).strip()
    top_intro = str(meta.get("top_intro") or "").strip()
    if top_intro in {">", "|"}:
        top_intro = ""
    return {
        "name": str(meta.get("name") or OWNER_NAME),
        "role": str(meta.get("role") or ""),
        "intro": top_intro or intro,
        "avatar_url": str(meta.get("avatar_url") or "").strip(),
    }


def _load_profile() -> dict:
    if not PROFILE_YAML.exists():
        return {}
    try:
        return yaml.safe_load(PROFILE_YAML.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"[!] profile.yaml load error: {e}")
        return {}


def _load_portfolio() -> list[dict]:
    if not PORTFOLIO_YAML.exists():
        return []
    try:
        data = yaml.safe_load(PORTFOLIO_YAML.read_text(encoding="utf-8")) or {}
        items = data.get("portfolio") or []
        display_order = [str(slug) for slug in (data.get("display_order") or [])]
        if not display_order:
            return items
        rank = {slug: index for index, slug in enumerate(display_order)}
        return sorted(
            items,
            key=lambda item: rank.get(str(item.get("slug") or ""), len(rank)),
        )
    except Exception as e:
        print(f"[!] portfolio.yaml load error: {e}")
        return []


def _load_all_lectures() -> list[dict]:
    """公開対象の受講資料を読み込み、LP の入口カード用に返す。"""
    if not LECTURES_DIR.exists():
        return []
    items: list[dict] = []
    for f in sorted(LECTURES_DIR.glob("*.md"), reverse=True):
        raw = f.read_text(encoding="utf-8")
        meta: dict = {}
        if raw.startswith("---"):
            try:
                end = raw.index("\n---", 3)
                meta = yaml.safe_load(raw[3:end].strip()) or {}
            except Exception:
                pass
        if meta.get("listed") is False:
            continue
        items.append({
            "slug": f.stem,
            "title": str(meta.get("title") or f.stem),
            "date": str(meta.get("date") or ""),
            "summary": str(meta.get("summary") or ""),
            "image": str(meta.get("image") or ""),
            "image_alt": str(meta.get("image_alt") or ""),
            "learning_order": int(meta.get("learning_order") or 999),
            "category": str(meta.get("category") or "other"),
            "level": str(meta.get("level") or ""),
            "duration": str(meta.get("duration") or ""),
        })
    return sorted(items, key=lambda item: (str(item.get("category") or ""), int(item.get("learning_order") or 999), str(item.get("title") or "")))


PORTAL_CSS = """
/* ===== Light Hub System =====
   講習会・相談サービスとして読みやすい、自然で落ち着いたライト基調。 */
:root {
  /* ===== デフォルト=ライト（初心者に「難しそう」を与えない）。dark は data-theme=dark で。 ===== */
  /* --- 共有トークン（テーマ非依存） --- */
  --cyan: #2F8EAD;
  --blue: #1F5F8B;
  --sage: #6FAF98;
  --emerald: #2C8C78;
  --amber: #B7791F;
  --coral: #D65E4B;
  --glass-blur: 8px;
  --radius: 8px;
  --radius-sm: 8px;
  --serif: "Inter", -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
  --mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
  --bg-base: #F7FAF8;
  --bg-white: #FFFFFF;
  --bg-elev: #FFFFFF;
  --text: #122033;
  --text-soft: #405166;
  --muted: #728093;
  --line: rgba(18,32,51,0.12);
  --line-strong: rgba(18,32,51,0.22);
  --primary: #1F6E8C;
  --primary-soft: #3C9CAD;
  --violet: #61758F;
  --primary-bg: rgba(47,142,173,0.09);
  --grad: linear-gradient(120deg, #1F6E8C 0%, #3C9CAD 54%, #6FAF98 100%);
  --grad-soft: linear-gradient(120deg, rgba(31,110,140,.09), rgba(60,156,173,.08), rgba(111,175,152,.10));
  --glass-bg: rgba(255,255,255,0.90);
  --glass-border: rgba(18,32,51,0.12);
  --glass-hi: rgba(255,255,255,0.94);
  --shadow-card: 0 1px 2px rgba(18,32,51,0.04), 0 10px 26px rgba(18,32,51,0.07);
  --shadow-card-hover: 0 7px 18px rgba(18,32,51,0.08), 0 20px 46px rgba(31,110,140,0.12);
  --glow: 0 18px 48px rgba(47,142,173,0.14);
  --grad-glow-a: rgba(31,110,140,.10);
  --grad-glow-b: rgba(60,156,173,.10);
  --grad-glow-c: rgba(183,121,31,.06);
}
:root[data-theme="dark"] {
  --bg-base: #0B1120;
  --bg-white: #111827;
  --bg-elev: #162033;
  --text: #E8F2FF;
  --text-soft: #A6AEC4;
  --muted: #707A92;
  --line: rgba(255,255,255,0.07);
  --line-strong: rgba(255,255,255,0.13);
  --primary: #38BDF8;
  --primary-soft: #7DD3FC;
  --violet: #A78BFA;
  --primary-bg: rgba(56,189,248,0.12);
  --grad: linear-gradient(120deg, #38BDF8 0%, #60A5FA 48%, #86EFAC 100%);
  --grad-soft: linear-gradient(120deg, rgba(56,189,248,.16), rgba(134,239,172,.14));
  --emerald: #5BE0B0;
  --glass-bg: rgba(23,26,43,0.64);
  --glass-border: rgba(255,255,255,0.09);
  --glass-hi: rgba(255,255,255,0.05);
  --shadow-card: 0 2px 10px rgba(0,0,0,0.24), 0 18px 50px rgba(0,0,0,0.40);
  --shadow-card-hover: 0 6px 20px rgba(0,0,0,0.30), 0 30px 76px rgba(0,0,0,0.52), 0 0 0 1px rgba(139,160,255,0.20);
  --glow: 0 0 60px rgba(110,139,255,0.32);
  --grad-glow-a: rgba(56,189,248,.22);
  --grad-glow-b: rgba(134,239,172,.14);
  --grad-glow-c: rgba(245,158,11,.08);
}
:root { color-scheme: light; }
:root[data-theme="dark"] { color-scheme: dark; }
html, body, .hero, .biz-card, .service-card, .pkg-card, .faq-item, .stat,
.site-header, .menu-drop, .mobile-nav, .diagnose-box {
  transition: background-color .3s ease, color .3s ease, border-color .3s ease;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; overflow-x: clip; overflow-y: visible; }
html { scroll-behavior: auto; }
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  color: var(--text);
  line-height: 1.82;            /* しっとり: ゆったり読める日本語行間 */
  min-height: 100vh;
  background:
    linear-gradient(110deg, rgba(111,175,152,.08) 0%, transparent 34%),
    linear-gradient(180deg, #FFFFFF 0%, #F8FBF9 48%, #F1F7F5 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
  letter-spacing: 0;
}
body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(18,32,51,.022) 1px, transparent 1px),
    linear-gradient(180deg, rgba(18,32,51,.016) 1px, transparent 1px);
  background-size: 88px 88px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,.22), transparent 58%);
}
::selection { background: rgba(40,84,197,.22); color: var(--text); }

/* ---- glassmorphism helpers (再利用) ----
   カード/ヘッダー/ドロップに共通で当てる「ガラス質感」。
   半透明背景 + backdrop blur + 1px光彩ボーダー + 上端の内側ハイライト。 */
.biz-card, .service-card, .pkg-card, .faq-item, .stat,
.lecture-card, .pf-card, .voice-card, .explore-card, .contact-choice,
.menu-drop, .diagnose-box, .hero-quiz {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(6px) saturate(108%);
  -webkit-backdrop-filter: blur(6px) saturate(108%);
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card);
}

/* スクロールでふわっと現れる reveal（JSが .is-in を付与） */
.reveal { opacity: 0; transform: translateY(18px); transition: opacity .7s cubic-bezier(.22,1,.36,1), transform .7s cubic-bezier(.22,1,.36,1); }
.reveal.is-in { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) {
  .reveal { opacity: 1 !important; transform: none !important; transition: none; }
}

/* ---- layout ---- */
.container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 96px 24px 80px;  /* top: header height */
}
html { scroll-padding-top: 96px; }
[id] { scroll-margin-top: 96px; }

/* ---- header (fixed N-デザイン風) ---- */
header.site-header {
  position: fixed; inset: 0 0 auto 0; z-index: 50;
  background: linear-gradient(90deg, rgba(255,255,255,.985) 0%, rgba(244,250,251,.975) 100%);
  border-bottom: 1px solid rgba(18,32,51,.16);
  box-shadow: 0 10px 30px rgba(18,32,51,.08), inset 0 1px 0 rgba(255,255,255,.92);
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  transition: background .3s, box-shadow .3s, backdrop-filter .3s;
}
header.site-header.scrolled {
  background: rgba(255,255,255,.985);
  box-shadow: 0 14px 34px rgba(18,32,51,.12), inset 0 1px 0 rgba(255,255,255,.94);
}
.site-header-inner {
  max-width: 1280px; margin: 0 auto;
  padding: 10px 24px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px;
}
.site-logo {
  font-size: 18px; font-weight: 800; letter-spacing: 0;
  color: var(--text); text-decoration: none;
  display: inline-flex; align-items: center; gap: 8px;
}
.site-logo .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--grad); box-shadow: 0 0 12px rgba(40,84,197,.42); display: inline-block; }
.brand-mark {
  width: 44px; height: 36px; border-radius: 8px;
  display: inline-flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #FFFFFF 0%, #E8F8F5 52%, #F2F9E8 100%);
  border: 1px solid rgba(15,143,114,.22);
  box-shadow: 0 10px 24px rgba(15,143,114,.13), inset 0 1px 0 rgba(255,255,255,.95);
  color: #0F172A; font-family: var(--mono); font-weight: 900; line-height: 1;
}
.brand-mark .brand-a { font-size: 14px; letter-spacing: 0; color: var(--primary); }
.brand-mark .brand-ha { font-size: 16px; margin-left: -2px; color: var(--emerald); transform: translateY(1px); }
.wordmark {
  display: inline-flex; align-items: baseline; gap: 3px;
  font-weight: 900; letter-spacing: 0;
}
.wordmark .word-ai {
  font-family: var(--mono); color: var(--primary); letter-spacing: 0;
}
.wordmark .word-hub {
  color: var(--text); font-weight: 900;
}
.wordmark .word-en {
  margin-left: 8px; color: var(--muted); font-family: var(--mono);
  font-size: 11px; font-weight: 700; letter-spacing: .08em;
}
.site-logo-by {
  color: #0F5F78;
  font-weight: 850;
  font-size: 11.5px;
  margin-left: 4px;
  padding: 4px 7px;
  border: 1px solid rgba(14,165,198,.22);
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(232,248,245,.88), rgba(255,255,255,.72));
  white-space: nowrap;
}
@media (max-width: 720px) {
  .wordmark .word-en, .site-logo-by { display: none; }
}
.site-nav {
  display: flex; align-items: center; gap: 8px;
  padding: 4px;
  border: 1px solid rgba(18,32,51,.10);
  border-radius: 10px;
  background: rgba(255,255,255,.78);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.96);
}
.site-nav a.nav-link {
  padding: 8px 10px; border-radius: 8px;
  font-size: 12.5px; font-weight: 850; color: #26364D;
  text-decoration: none; transition: color .2s, background .2s, border-color .2s;
  border: 1px solid transparent;
}
.site-nav a.nav-link:hover {
  background: #EAF6F8; color: #0F5F78; border-color: rgba(31,110,140,.20);
}
.site-nav .menu-wrap { position: relative; }
.site-nav .menu-toggle {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,.72); border: 1px solid transparent; cursor: pointer;
  border-radius: 8px;
  font: inherit; font-size: 13px; font-weight: 850; color: #26364D;
  padding: 8px 10px;
}
.site-nav .menu-toggle:hover,
.site-nav .menu-toggle[aria-expanded="true"] {
  background: #EAF6F8; color: #0F5F78; border-color: rgba(31,110,140,.20);
}
.site-nav .menu-toggle .chev { transition: transform .2s; }
.site-nav .menu-toggle[aria-expanded="true"] .chev { transform: rotate(180deg); }
.site-nav .menu-drop {
  position: absolute; right: 0; top: calc(100% + 14px);
  min-width: 240px; padding: 8px;
  background: #FEFFFF !important; border: 1px solid rgba(18,32,51,.18);
  border-radius: var(--radius-sm);
  box-shadow: 0 18px 44px rgba(18,32,51,.16), inset 0 1px 0 rgba(255,255,255,.95);
  backdrop-filter: none;
  display: none;
}
.site-nav .menu-drop.open { display: block; }
.site-nav .menu-drop-label {
  display: block; padding: 7px 14px 4px;
  font-size: 10px; font-weight: 900; letter-spacing: .14em;
  color: #526070; text-transform: uppercase;
}
.site-nav .menu-drop a {
  display: block; padding: 9px 14px; border-radius: 10px;
  font-size: 13px; font-weight: 750; color: #203045;
  text-decoration: none;
}
.site-nav .menu-drop a:hover { background: #EAF6F8; color: #0F5F78; }
.site-nav .nav-admin {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 9px 12px; border-radius: var(--radius-sm);
  border: 1px solid rgba(18,32,51,.14);
  background: rgba(255,255,255,.78);
  color: #223148;
  font-size: 12.5px; font-weight: 850;
  text-decoration: none;
}
.site-nav .nav-admin:hover {
  background: #EAF6F8;
  color: #0F5F78;
  border-color: rgba(31,110,140,.24);
}
/* ヘッダー右端の主CTA: 個別相談 */
.site-nav .nav-cta {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #0F5F78 0%, #117E69 100%); color: #fff;
  font-size: 13px; font-weight: 800;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(15,95,120,.28), inset 0 1px 0 rgba(255,255,255,.25);
  transition: transform .2s, box-shadow .2s, filter .2s;
}
.site-nav .nav-cta:hover { transform: translateY(-1px); filter: brightness(1.08); box-shadow: 0 12px 36px rgba(15,143,114,.22), inset 0 1px 0 rgba(255,255,255,.30); }
.mobile-nav .mobile-admin-link {
  color: #0F5F78;
  font-weight: 850;
}

.mobile-toggle {
  display: none; padding: 8px; border-radius: var(--radius-sm);
  background: #fff; border: 1px solid rgba(18,32,51,.18);
  box-shadow: 0 6px 16px rgba(18,32,51,.08);
  cursor: pointer;
}
.mobile-nav {
  display: none; padding: 16px 24px 24px;
  background: #fff; backdrop-filter: blur(18px);
  border-top: 1px solid rgba(18,32,51,.16);
  box-shadow: 0 18px 34px rgba(18,32,51,.12);
}
.mobile-nav.open { display: block; }
.mobile-nav a {
  display: block; padding: 12px 4px; font-size: 15px; font-weight: 600;
  color: var(--text); text-decoration: none; border-bottom: 1px solid var(--line);
}
.mobile-nav a:last-child { border-bottom: none; }
.mobile-nav .mobile-nav-label {
  display: block; padding: 14px 4px 6px;
  font-size: 11px; font-weight: 900; letter-spacing: .14em;
  color: var(--muted); text-transform: uppercase;
}
.mobile-nav .login-btn-mobile {
  display: block; margin-top: 14px; padding: 12px 18px; border-radius: 999px;
  background: var(--grad); color: #fff; text-align: center;
  font-size: 14px; font-weight: 600; text-decoration: none;
}

@media (max-width: 900px) {
  .site-nav { display: none; }
  .mobile-toggle { display: inline-flex; }
}

/* ---- hero ---- */
.hero {
  padding: 54px 0 52px;
  min-height: 590px;
  display: grid; grid-template-columns: minmax(0, .94fr) minmax(440px, 1.06fr); gap: 44px; align-items: center;
  position: relative;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 0 calc(50% - 50vw) 0;
  z-index: -1;
  background:
    linear-gradient(90deg, #FFFFFF 0%, rgba(255,255,255,.96) 38%, rgba(241,248,246,.82) 100%);
  border-top: 1px solid rgba(18,32,51,.05);
  border-bottom: 1px solid rgba(18,32,51,.08);
}
.hero-text { text-align: left; min-width: 0; max-width: 100%; }
@media (max-width: 900px) { .hero { grid-template-columns: 1fr; gap: 28px; }
  .hero-text { text-align: center; }
}
.hero .eyebrow {
  display: block;
  padding: 0;
  background: transparent; color: var(--primary);
  font-family: var(--mono); font-size: 11.5px; font-weight: 800; letter-spacing: .14em;
  border: 0;
  box-shadow: none;
  max-width: 100%;
}
@media (max-width: 560px) {
  .hero .eyebrow {
    display: flex; text-align: left; line-height: 1.5;
    padding: 8px 12px; font-size: 10.5px;
  }
}
.hero h1 {
  margin: 18px 0 14px; font-size: clamp(42px, 6vw, 76px);
  font-family: var(--serif); font-weight: 900; letter-spacing: 0;
  color: var(--text); line-height: 1.04;
  overflow-wrap: anywhere; word-break: normal;
}
.hero h1 .accent {
  color: var(--primary);
}
.hero h1 .underline {
  position: relative;
}
.hero h1 .underline::after {
  content:''; position: absolute; left: 0; right: 0; bottom: 2px; height: 8px;
  background: rgba(155,228,58,.32);
  border-radius: 999px; z-index: -1;
}
.hero-brand { display: block; max-width: 680px; }
.fusion-logo-large {
  display: inline-flex; align-items: baseline; gap: .08em;
  letter-spacing: 0;
}
.fusion-logo-large .ai {
  font-family: var(--mono); color: var(--primary); letter-spacing: 0;
}
.fusion-logo-large .hub {
  color: var(--text); letter-spacing: 0;
}
.fusion-logo-large .pipe {
  display: none;
  font-family: var(--mono); color: rgba(14,165,233,.45);
  font-size: .62em; margin: 0 .08em; transform: translateY(-.08em);
}
.hero-title-sub {
  display: block; margin-top: 14px;
  font-size: clamp(22px, 2.7vw, 34px);
  line-height: 1.24; color: var(--text); letter-spacing: 0;
}
.hero-title-sub strong {
  color: var(--primary);
  background: transparent;
}
.hero .sub-catch {
  max-width: 560px; margin: 0 0 18px;
  font-size: clamp(15px, 1.7vw, 18px); font-weight: 800; color: var(--text); line-height: 1.7;
}
.hero .sub-catch strong { color: var(--primary); }
@media (max-width: 900px) { .hero .sub-catch { margin: 0 auto 18px; } }
.hero .lead {
  max-width: 560px; margin: 0 0 28px;
  font-size: clamp(14px, 1.5vw, 16px); color: var(--text-soft); line-height: 1.9;
}
.hero .lead strong { color: var(--text); font-weight: 700; }
@media (max-width: 900px) { .hero .lead { margin: 0 auto 28px; } }
.hero-actions {
  display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px;
}
@media (max-width: 900px) { .hero-actions { justify-content: center; } }
.btn-lg { padding: 16px 32px; font-size: 16px; }
/* 主CTAは静かに強調。過度な脈動はクールな印象を崩すため使わない。 */
.hero-actions .btn-primary { animation: none; }
@keyframes cta-pulse {
  0%,100% { box-shadow: 0 8px 26px rgba(40,84,197,.28), inset 0 1px 0 rgba(255,255,255,.25); }
  50% { box-shadow: 0 12px 34px rgba(15,143,114,.25), inset 0 1px 0 rgba(255,255,255,.30); }
}
@media (prefers-reduced-motion: reduce) { .hero-actions .btn-primary { animation: none; } }
.hero-trust {
  list-style: none; padding: 0; margin: 18px 0 0;
  display: flex; flex-wrap: wrap; gap: 8px 18px;
  font-size: 13px; color: var(--text-soft);
}
.hero-trust li { display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; }
.hero-trust strong { color: var(--text); }
@media (max-width: 900px) { .hero-trust { justify-content: center; } }

.hero-entry-strip {
  margin-top: 22px;
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px; max-width: 620px;
}
.entry-chip {
  min-height: 74px; padding: 12px;
  border-radius: var(--radius-sm); border: 1px solid var(--line);
  background: var(--glass-bg);
  backdrop-filter: blur(14px) saturate(130%);
  -webkit-backdrop-filter: blur(14px) saturate(130%);
  text-decoration: none; color: var(--text);
  display: flex; flex-direction: column; justify-content: center; gap: 4px;
  transition: transform .18s ease, border-radius .28s ease, border-color .18s ease, box-shadow .18s ease, background .18s ease;
}
.entry-chip:hover,
.entry-chip:focus-visible {
  transform: translateY(-3px);
  border-radius: var(--radius-sm);
  border-color: rgba(40,84,197,.34);
  box-shadow: 0 14px 32px rgba(40,84,197,.12);
  background: #fff;
  outline: none;
}
.entry-chip b { font-size: 13.5px; line-height: 1.25; }
.entry-chip span { font-size: 11.5px; color: var(--muted); line-height: 1.35; }
@media (max-width: 680px) { .hero-entry-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

/* ヒーロー直下の補助金訴求バナー（advisor推奨の最優先軸を front-and-center に） */
.hero-photo-card {
  position: relative;
  justify-self: end;
  width: min(100%, 640px);
  aspect-ratio: 16 / 10.4;
  padding: 8px;
  border-radius: var(--radius);
  background: rgba(255,255,255,.92);
  border: 1px solid rgba(18,32,51,.12);
  box-shadow: 0 18px 46px rgba(18,32,51,.12), inset 0 1px 0 var(--glass-hi);
  backdrop-filter: blur(6px) saturate(112%);
  -webkit-backdrop-filter: blur(6px) saturate(112%);
  overflow: hidden;
}
.hero-photo-card img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center;
  border-radius: 6px;
}
.hero-photo-card::after {
  content: "";
  position: absolute;
  inset: 8px;
  border-radius: 6px;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(255,255,255,.02) 0%, rgba(18,32,51,.08) 100%),
    linear-gradient(120deg, rgba(31,110,140,.06), rgba(111,175,152,.05), transparent 64%);
}
.hero-photo-note {
  position: absolute;
  left: 24px;
  top: 24px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 10px 13px;
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,.94);
  border: 1px solid rgba(18,32,51,.10);
  box-shadow: 0 10px 24px rgba(21,32,50,.10);
  color: var(--text);
  font-size: 12px;
  font-weight: 800;
}
.hero-photo-note i {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--emerald);
  box-shadow: 0 0 0 4px rgba(15,143,114,.14);
}
.hero-photo-map {
  position: absolute;
  right: 20px;
  top: 20px;
  z-index: 3;
  width: min(48%, 260px);
  padding: 12px;
  border-radius: var(--radius-sm);
  background: rgba(18,32,51,.72);
  border: 1px solid rgba(255,255,255,.18);
  color: #fff;
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 14px 34px rgba(11,16,32,.18);
}
.hero-photo-map svg {
  display: block;
  width: 100%;
  height: auto;
}
.hero-photo-map path,
.hero-photo-map line,
.hero-photo-map circle,
.hero-photo-map rect {
  vector-effect: non-scaling-stroke;
}
.hero-photo-map .route-line {
  stroke-dasharray: 8 10;
  animation: route-dash 4.8s linear infinite;
}
@keyframes route-dash { to { stroke-dashoffset: -72; } }
.hero-mini-routes {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 20px;
  z-index: 4;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 7px;
}
.hero-mini-routes a {
  min-height: 66px;
  padding: 9px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255,255,255,.62);
  background: rgba(255,255,255,.90);
  color: var(--text);
  text-decoration: none;
  box-shadow: 0 10px 24px rgba(16,24,39,.11);
  backdrop-filter: blur(8px) saturate(112%);
  -webkit-backdrop-filter: blur(8px) saturate(112%);
  transition: transform .18s ease, border-color .18s ease, background .18s ease;
}
.hero-mini-routes a:hover,
.hero-mini-routes a:focus-visible {
  transform: translateY(-3px);
  border-color: rgba(6,167,216,.44);
  background: rgba(255,255,255,.94);
  outline: none;
}
.hero-mini-routes b {
  display: block;
  font-size: 12px;
  line-height: 1.25;
}
.hero-mini-routes small {
  display: block;
  margin-top: 3px;
  color: var(--muted);
  font-size: 10px;
  line-height: 1.25;
}
@media (max-width: 900px) {
  .hero-photo-card {
    justify-self: center;
    width: min(100%, 560px);
    aspect-ratio: 4 / 3;
  }
}
@media (max-width: 560px) {
  .hero-photo-card { padding: 7px; }
  .hero-photo-card::after { inset: 7px; }
  .hero-photo-note {
    left: 16px;
    top: 16px;
    max-width: calc(100% - 32px);
    font-size: 11.5px;
  }
  .hero-mini-routes { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero-photo-map { width: 48%; right: 14px; top: 14px; }
}
@media (max-width: 900px) {
  .hero-mini-routes { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero-photo-map { width: 48%; right: 14px; top: 14px; }
}
@media (max-width: 560px) {
  .hero-photo-map {
    display: none;
  }
  .hero-mini-routes {
    left: 12px;
    right: 12px;
    bottom: 12px;
  }
  .hero-mini-routes a {
    min-height: 58px;
    padding: 8px;
  }
}

.hero-subsidy-banner {
  display: inline-flex; align-items: center; gap: 12px;
  margin: 14px 0 18px; padding: 10px 14px 10px 12px;
  border-radius: 999px; text-decoration: none;
  background: var(--grad-soft);
  border: 1px solid rgba(40,84,197,.22);
  box-shadow: 0 4px 18px rgba(40,84,197,.12);
  transition: transform .2s, box-shadow .2s, border-color .2s;
  max-width: 100%;
}
.hero-subsidy-banner:hover {
  transform: translateY(-1px);
  border-color: rgba(15,143,114,.40);
  box-shadow: 0 8px 24px rgba(15,143,114,.16);
}
.hero-subsidy-banner .hsb-tag {
  flex: 0 0 auto;
  padding: 3px 10px; border-radius: 999px;
  background: var(--grad); color: #fff;
  font-family: var(--mono); font-size: 10.5px; font-weight: 800; letter-spacing: .06em;
  box-shadow: 0 4px 14px rgba(40,84,197,.24);
}
.hero-subsidy-banner .hsb-text { display: flex; flex-direction: column; line-height: 1.35; min-width: 0; }
.hero-subsidy-banner .hsb-text strong { font-size: 14.5px; color: var(--text); }
.hero-subsidy-banner .hsb-text span { font-size: 12px; color: var(--text-soft); }
.hero-subsidy-banner .hsb-arrow { flex: 0 0 auto; font-size: 18px; font-weight: 700; color: var(--primary); }
@media (max-width: 560px) {
  .hero-subsidy-banner { gap: 10px; padding: 10px 12px; }
  .hero-subsidy-banner .hsb-text strong { font-size: 13.5px; }
  .hero-subsidy-banner .hsb-text span { font-size: 11.5px; }
}

/* ヒーロー起点の AIレベル診断（第1問・主役） */
.hero-quiz {
  margin-top: 16px; padding: 26px; border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  background:
    radial-gradient(140% 160% at 100% 0%, rgba(155,123,255,.12), transparent 55%),
    var(--bg-elev);
  box-shadow: var(--shadow-card), inset 0 1px 0 var(--glass-hi);
}
.hq-label {
  font-size: 16.5px; font-weight: 700; color: var(--text); margin-bottom: 16px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap; line-height: 1.5;
}
.hq-mono {
  font-family: var(--mono); font-size: 10.5px; font-weight: 700; letter-spacing: .08em;
  color: var(--primary-soft); background: var(--primary-bg);
  border: 1px solid var(--glass-border); padding: 3px 10px; border-radius: 999px;
}
.hq-opts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
@media (max-width: 560px) { .hq-opts { grid-template-columns: 1fr; } }
.hq-opt {
  display: flex; flex-direction: column; align-items: flex-start; gap: 6px;
  padding: 15px 15px; background: var(--bg-base); border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  color: var(--text); font-size: 13.5px; font-weight: 600; text-align: left;
  cursor: pointer; transition: border-color .15s, transform .12s, background .15s, box-shadow .15s;
}
.hq-opt:hover { border-color: var(--primary); transform: translateY(-2px); background: var(--primary-bg); box-shadow: 0 12px 28px rgba(40,84,197,.12); }
.hq-lv {
  font-family: var(--mono); font-size: 10px; font-weight: 700; letter-spacing: .06em;
  color: var(--primary-soft); background: var(--primary-bg);
  border: 1px solid var(--glass-border); padding: 2px 9px; border-radius: 999px;
}
.hq-sub {
  display: inline-block; margin-top: 12px; font-size: 11.5px; color: var(--muted);
  text-decoration: none;
}
.hq-sub:hover { color: var(--primary); }
@media (max-width: 900px) { .hero-quiz { text-align: left; } .hq-label { justify-content: flex-start; } }

/* hero visual (右側ビジュアル) */
.hero-visual {
  position: relative; aspect-ratio: 4/5; max-width: 460px; justify-self: end;
  border-radius: var(--radius); overflow: hidden; isolation: isolate;
  box-shadow: 0 40px 100px rgba(0,0,0,.42), 0 0 0 1px var(--glass-border);
  transition: transform .6s cubic-bezier(.22,1,.36,1);
}
@media (max-width: 900px) { .hero-visual { justify-self: center; max-width: 380px; } }
/* モバイル: SVGをヒーロー最上部の背景に敷き、その上にテキストを重ねる */
@media (max-width: 900px) {
  .hero { padding-top: 8px; position: relative; }
  .hero-visual:not(.hub-visual) {
    position: absolute; top: 0; left: 0; right: 0; transform: none;
    width: 100%; max-width: none; aspect-ratio: auto; height: 360px;
    border-radius: 0; box-shadow: none; z-index: 0; opacity: .92;
    -webkit-mask-image: linear-gradient(180deg, #000 42%, rgba(0,0,0,.30) 72%, transparent 100%);
    mask-image: linear-gradient(180deg, #000 42%, rgba(0,0,0,.30) 72%, transparent 100%);
    pointer-events: none;
  }
  .hero-svg { object-fit: cover; }  /* 人物が中央に来るよう全幅カバー */
  .hero-visual:not(.hub-visual):hover { transform: none; }
  .hero-visual:not(.hub-visual) .hero-flow { display: none; }  /* 背景化時は3ステップ帯を隠す */
  .hero-text { position: relative; z-index: 1; }
  .hero:has(.hero-visual:not(.hub-visual)) .hero-text { padding-top: 250px; }
}
.hero-visual:hover { transform: translateY(-4px); }
.hero-visual img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 1.2s ease; }
.hero-visual:hover img { transform: scale(1.04); }
.hero-visual:not(.hero-visual-svg)::after {
  content:''; position: absolute; inset: 0;
  background:
    linear-gradient(160deg, rgba(110,139,255,.10) 0%, rgba(199,125,255,.12) 50%, transparent 70%),
    linear-gradient(0deg, rgba(11,13,20,.40) 0%, rgba(11,13,20,0) 42%);
  pointer-events: none;
}
.hub-visual {
  aspect-ratio: 1 / 1; max-width: 500px; min-height: 0;
  padding: 22px; justify-self: end;
  background:
    linear-gradient(145deg, rgba(255,255,255,.92), rgba(240,249,255,.88)),
    radial-gradient(70% 70% at 80% 10%, rgba(163,230,53,.16), transparent 70%);
  box-shadow: 0 28px 80px rgba(15,23,42,.12), 0 0 0 1px rgba(14,165,233,.14);
}
.hub-visual::before {
  content:''; position: absolute; inset: 64px; z-index: 0;
  background:
    linear-gradient(90deg, transparent 49%, rgba(14,165,233,.18) 49.5%, rgba(14,165,233,.18) 50.5%, transparent 51%),
    linear-gradient(0deg, transparent 49%, rgba(34,197,94,.16) 49.5%, rgba(34,197,94,.16) 50.5%, transparent 51%);
  border-radius: 32px; pointer-events: none;
}
.hub-visual::after { display: none; }
.hub-core {
  position: absolute; z-index: 2; inset: 50%; width: 168px; height: 168px;
  transform: translate(-50%, -50%);
  border-radius: 42px;
  background: linear-gradient(145deg, #FFFFFF, #E0F7FF 62%, #ECFCCB);
  border: 1px solid rgba(14,165,233,.20);
  box-shadow: 0 24px 58px rgba(37,99,235,.16), inset 0 1px 0 rgba(255,255,255,.95);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center;
  transition: border-radius .45s cubic-bezier(.22,1,.36,1), transform .45s cubic-bezier(.22,1,.36,1);
}
.hub-visual:hover .hub-core { border-radius: 58px; transform: translate(-50%, -50%) scale(1.03); }
.hub-core-logo {
  display: inline-flex; align-items: baseline; gap: 3px;
  font-size: 28px; font-weight: 900; line-height: 1;
}
.hub-core-logo .ai { font-family: var(--mono); color: var(--primary); letter-spacing: 0; }
.hub-core-logo .hub { color: var(--text); letter-spacing: 0; }
.hub-core small { margin-top: 10px; color: var(--text-soft); font-size: 12px; font-weight: 700; line-height: 1.35; }
.hub-route {
  position: absolute; z-index: 3;
  width: 178px; min-height: 116px;
  padding: 16px;
  border-radius: 24px;
  background: rgba(255,255,255,.86);
  border: 1px solid rgba(15,23,42,.10);
  box-shadow: 0 14px 42px rgba(15,23,42,.08);
  text-decoration: none; color: var(--text);
  display: flex; flex-direction: column; justify-content: center; gap: 6px;
  transition: transform .22s ease, border-radius .34s cubic-bezier(.22,1,.36,1), border-color .2s ease, box-shadow .2s ease, background .2s ease;
}
.hub-route:hover,
.hub-route:focus-visible {
  transform: translateY(-5px) scale(1.02);
  border-radius: 32px;
  border-color: rgba(14,165,233,.42);
  background: #fff;
  box-shadow: 0 24px 58px rgba(14,165,233,.16);
  outline: none;
}
.hub-route .route-kicker {
  font-family: var(--mono); font-size: 10px; font-weight: 800; letter-spacing: .10em;
  color: var(--primary-soft);
}
.hub-route b { font-size: 18px; line-height: 1.25; }
.hub-route small { font-size: 12px; color: var(--muted); line-height: 1.45; }
.route-consult { top: 22px; left: 22px; }
.route-works { top: 22px; right: 22px; }
.route-learn { bottom: 22px; left: 22px; }
.route-watch { bottom: 22px; right: 22px; }
.hub-status {
  position: absolute; left: 50%; bottom: 148px; z-index: 4;
  transform: translateX(-50%);
  min-width: 210px; padding: 9px 14px; border-radius: 999px;
  background: rgba(15,23,42,.86); color: #fff;
  font-size: 12px; font-weight: 700; text-align: center;
  box-shadow: 0 16px 38px rgba(15,23,42,.18);
}
@media (max-width: 1020px) {
  .hub-route { width: 160px; min-height: 108px; }
  .hub-core { width: 150px; height: 150px; }
}
@media (max-width: 900px) {
  .hub-visual { justify-self: center; width: min(100%, 500px); margin-top: 8px; }
}
@media (max-width: 560px) {
  .hub-visual { padding: 16px; }
  .hub-visual::before { inset: 52px; }
  .hub-route {
    width: calc(50% - 22px); min-height: 104px; padding: 13px;
  }
  .hub-route b { font-size: 16px; }
  .hub-route small { font-size: 11.5px; }
  .hub-core { width: 128px; height: 128px; border-radius: 34px; }
  .hub-core-logo { font-size: 24px; }
  .hub-core small { font-size: 11px; }
  .hub-status { bottom: 126px; min-width: 188px; font-size: 11px; }
}
@media (prefers-reduced-motion: reduce) {
  .hub-core, .hub-route, .entry-chip { transition: none; }
}
/* 線画ヒーローSVG */
.hero-svg { width: 100%; height: 100%; display: block; }
.hsvg-glow { transform-box: fill-box; transform-origin: center; animation: hsvg-breathe 4s ease-in-out infinite; }
@keyframes hsvg-breathe { 0%,100% { opacity: .8; transform: scale(1); } 50% { opacity: 1; transform: scale(1.07); } }
.hsvg-stream path { stroke-dasharray: 10 14; animation: hsvg-flow 3s linear infinite; animation-delay: var(--d, 0s); }
@keyframes hsvg-flow { to { stroke-dashoffset: -48; } }
.hsvg-p { transform-box: fill-box; transform-origin: center; animation: hsvg-pulse 2.4s ease-in-out infinite; animation-delay: var(--pd, 0s); }
@keyframes hsvg-pulse { 0%,100% { opacity: .55; transform: scale(.8); } 50% { opacity: 1; transform: scale(1.25); } }
.hsvg-dot { animation: hsvg-blink 1.4s ease-in-out infinite; }
@keyframes hsvg-blink { 0%,100% { opacity: 1; } 50% { opacity: .3; } }
@media (prefers-reduced-motion: reduce) {
  .hsvg-glow, .hsvg-stream path, .hsvg-p, .hsvg-dot { animation: none; }
}
.hero-blob {
  position: absolute; width: 260px; height: 260px; border-radius: 50%;
  filter: blur(60px); opacity: .55; z-index: -1; pointer-events: none;
}
.hero-blob.b1 { background: #2BA7C8; top: -40px; right: -40px; }
.hero-blob.b2 { background: #7AA58A; bottom: -40px; left: 30%; width: 200px; height: 200px; }

/* AI lesson hero illustration */
.hero-visual-photo {
  background: #f8fafc;
  width: 100%;
  min-height: 480px;
}
.hero-visual-photo .hero-bg {
  position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; display: block; z-index: 0;
  transition: transform 1.4s cubic-bezier(.22,1,.36,1);
}
.hero-visual-photo:hover .hero-bg { transform: scale(1.06); }
.hero-visual-photo::after {
  content:''; position: absolute; inset: 0; z-index: 1; pointer-events: none;
  background:
    radial-gradient(90% 64% at 76% 18%, rgba(255,255,255,.46), transparent 70%),
    linear-gradient(180deg, rgba(248,250,252,0) 48%, rgba(248,250,252,.16) 100%),
    linear-gradient(90deg, rgba(37,99,235,.06), rgba(139,92,246,.06));
}
@media (prefers-reduced-motion: reduce) {
  .hero-visual-photo .hero-bg { transition: none; }
}
@media (max-width: 900px) {
  .hero-visual-photo { min-height: 360px; }
  .hero-visual-photo .hero-bg { object-position: center 42%; }
}
@media (max-width: 560px) {
  .hero-blob { width: 180px; height: 180px; opacity: .4; }
  .hero-blob.b1 { top: -20px; right: -20px; }
  .hero-blob.b2 { width: 140px; height: 140px; bottom: -20px; left: 20%; }
}

/* 3-step flow overlay over hero image */
.hero-flow {
  position: absolute; left: 16px; right: 16px; bottom: 16px; z-index: 2;
  display: flex; align-items: stretch; gap: 6px;
  padding: 12px 12px; border-radius: var(--radius-sm);
  background: rgba(255,255,255,.86); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,.7);
  box-shadow: 0 14px 40px rgba(15,23,42,.22);
}
.hflow-step {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px;
  text-align: center; padding: 8px 4px; border-radius: 12px;
  animation: hflow-pop .5s ease both;
}
.hflow-step.accent { background: var(--primary-bg); }
.hflow-step.done { background: rgba(16,185,129,.12); }
.hflow-step:nth-child(1) { animation-delay: .15s; }
.hflow-step.accent { animation-delay: .45s; }
.hflow-step.done { animation-delay: .75s; }
.hflow-ico { font-size: 24px; line-height: 1; }
.hflow-txt b { display: block; font-size: 12px; font-weight: 800; color: var(--text); line-height: 1.3; }
.hflow-txt small { display: block; font-size: 10px; color: var(--muted); margin-top: 2px; line-height: 1.3; }
.hflow-arrow {
  align-self: center; font-size: 16px; font-weight: 800; color: var(--primary);
  flex: 0 0 auto; animation: hflow-fade 1.6s ease-in-out infinite;
}
@keyframes hflow-pop {
  from { opacity: 0; transform: translateY(10px) scale(.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes hflow-fade { 0%,100% { opacity: .4; } 50% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) {
  .hflow-step, .hflow-arrow { animation: none; opacity: 1; }
}
@media (max-width: 900px) {
  .hero-flow { left: 10px; right: 10px; bottom: 10px; gap: 4px; padding: 10px 8px; }
  .hflow-txt b { font-size: 11px; }
  .hflow-txt small { font-size: 9px; }
  .hflow-ico { font-size: 20px; }
  .hflow-arrow { font-size: 13px; }
}
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 13px 26px; border-radius: var(--radius-sm);
  font-size: 14.5px; font-weight: 800; text-decoration: none;
  transition: transform .2s, box-shadow .2s, background .2s, filter .2s;
  cursor: pointer; border: none; letter-spacing: 0;
}
.btn-primary {
  background: var(--grad); color: #fff;
  box-shadow: 0 10px 28px rgba(0,95,158,.24), inset 0 1px 0 rgba(255,255,255,.25);
}
.btn-primary:hover { transform: translateY(-2px); filter: brightness(1.06); box-shadow: 0 16px 42px rgba(0,152,200,.22), inset 0 1px 0 rgba(255,255,255,.30); }
.btn-secondary {
  background: rgba(255,255,255,.84); color: var(--text);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 var(--glass-hi);
}
.btn-secondary:hover { border-color: var(--line-strong); transform: translateY(-2px); box-shadow: 0 14px 30px rgba(21,32,50,.10); }
.btn-ghost { background: transparent; color: var(--text-soft); padding: 9px 16px; }
.btn-ghost:hover { color: var(--primary); }

/* ---- stats strip ---- */
.stats-strip {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 0;
  margin: 0 0 56px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255,255,255,.76);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}
@media (max-width: 720px) { .stats-strip { grid-template-columns: repeat(2, 1fr); } }
.stat {
  text-align: center; padding: 22px 18px; border-radius: 0;
  background: transparent; border: 0;
  border-right: 1px solid var(--line);
  box-shadow: none;
}
.stat:last-child { border-right: 0; }
@media (max-width: 720px) {
  .stat:nth-child(2n) { border-right: 0; }
  .stat:nth-child(n+3) { border-top: 1px solid var(--line); }
}
.stat .num {
  font-size: clamp(26px, 3.4vw, 38px); font-weight: 800;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent;
  line-height: 1.1; letter-spacing: 0;
}
.stat .label { font-size: 12.5px; color: var(--muted); margin-top: 6px; font-weight: 600; }
.stat .stat-sub { font-size: 10.5px; color: var(--muted); margin-top: 3px; font-style: italic; opacity: .8; }

/* ---- section frame ---- */
section.block { padding: 70px 0; scroll-margin-top: 96px; }
section.block + section.block { border-top: 1px solid var(--line); }
.section-title {
  font-family: var(--serif);
  font-size: clamp(28px, 4vw, 44px); font-weight: 900; letter-spacing: 0;
  color: var(--text); text-align: center; margin: 0 0 14px; line-height: 1.15;
  overflow-wrap: anywhere;
}
.packages-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
.packages-title span {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  background: var(--grad);
  color: #fff;
  font-family: var(--mono);
  font-size: clamp(13px, 1.5vw, 16px);
  font-weight: 900;
  line-height: 1;
  box-shadow: 0 10px 24px rgba(0,95,158,.18);
}
#packages .section-sub { margin-bottom: 26px; }
.section-sub {
  text-align: center; color: var(--text-soft);
  font-size: 14.5px; width: 100%; max-width: 640px; margin: 0 auto 48px; line-height: 1.8;
  overflow-wrap: anywhere;
}
.section-heading {
  font-family: var(--mono);
  font-size: 11px; font-weight: 800; letter-spacing: .16em;
  text-transform: uppercase;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent;
  margin: 0 0 14px; text-align: center;
}
.lv-flow { display: inline-flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 10px; }
.lv-flow-step {
  font-family: var(--mono); font-size: 11.5px; font-weight: 700; letter-spacing: .04em;
  color: var(--primary-soft); background: var(--primary-bg);
  border: 1px solid var(--glass-border); padding: 5px 14px; border-radius: 999px;
}
.lv-flow-arr { color: var(--primary); font-weight: 800; }

/* ---- services grid ---- */
.services-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
}
@media (max-width: 900px) { .services-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .services-grid { grid-template-columns: 1fr; } }
.service-card {
  position: relative; overflow: hidden;
  border-radius: var(--radius-sm);
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  transition: transform .35s cubic-bezier(.22,1,.36,1), box-shadow .35s, border-color .25s;
  display: flex; flex-direction: column;
}
.service-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-card-hover); border-color: rgba(40,84,197,.24); }
.service-image {
  position: relative; aspect-ratio: 16/9; overflow: hidden;
}
.service-image img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .9s ease; }
.service-card:hover .service-image img { transform: scale(1.08); }
.service-image::after {
  content:''; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(15,23,42,0) 30%, rgba(15,23,42,.55) 100%);
}
.service-body { padding: 22px 22px 24px; }
.service-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--primary-bg); color: var(--primary);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 22px; margin-bottom: 12px;
  position: relative; z-index: 2;
}
.service-card .service-icon-float {
  position: absolute; top: -22px; right: 18px;
  width: 56px; height: 56px; border-radius: var(--radius-sm);
  background: #fff; color: var(--primary);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 26px; box-shadow: 0 10px 24px rgba(15,23,42,.10);
  border: 1px solid var(--line); z-index: 3;
}
.service-name { font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
.service-desc { font-size: 13.5px; color: var(--text-soft); line-height: 1.7; }

/* ---- biz grid (事業ポートフォリオ) ---- */
.biz-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.biz-card {
  display: flex; flex-direction: column; gap: 0;
  border-radius: var(--radius-sm);
  background: var(--bg-white); border: 1px solid var(--line);
  text-decoration: none; color: inherit;
  box-shadow: var(--shadow-card);
  transition: transform .35s cubic-bezier(.22,1,.36,1), box-shadow .35s, border-color .25s;
  position: relative; overflow: hidden;
}
.biz-card-body {
  display: flex; flex-direction: column; gap: 8px;
  padding: 22px 22px 20px; flex: 1;
}
.biz-card-image {
  position: relative; aspect-ratio: 16/9; overflow: hidden;
  background: #f1f5f9;
}
.biz-card-image img {
  width: 100%; height: 100%; object-fit: cover; display: block;
  transition: transform .9s ease;
}
.biz-card:hover .biz-card-image img { transform: scale(1.06); }
.biz-card-image::after {
  content:''; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(15,23,42,0) 50%, rgba(15,23,42,.45) 100%);
}
.biz-card-image-icon {
  position: absolute; top: 12px; left: 12px;
  width: 38px; height: 38px; border-radius: 12px;
  background: rgba(255,255,255,.94); backdrop-filter: blur(8px);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 20px; line-height: 1;
  box-shadow: 0 4px 12px rgba(15,23,42,.16);
  z-index: 1;
}
.biz-card::before {
  content:''; position: absolute; inset: 0;
  background: linear-gradient(120deg, var(--card-glow, rgba(40,84,197,.08)) 0%, transparent 48%);
  opacity: 0; transition: opacity .35s; pointer-events: none;
}
.biz-card:hover::before { opacity: 1; }
.biz-card:hover {
  transform: translateY(-6px);
  border-color: var(--card-border, rgba(40,84,197,.28));
  box-shadow: var(--shadow-card-hover);
}
.biz-card.no-link { cursor: default; opacity: .65; }
.biz-card.no-link:hover { transform: none; box-shadow: var(--shadow-card); border-color: var(--line); }
.biz-card.self-card { border-color: rgba(40,84,197,.30); background: var(--primary-bg); }
.biz-card-icon { font-size: 28px; line-height: 1; margin-bottom: 2px; }
.biz-card-name { font-size: 16.5px; font-weight: 700; color: var(--text); line-height: 1.3; }
.biz-card-tagline { font-size: 12px; color: var(--muted); letter-spacing: .02em; font-weight: 600; }
.biz-card-desc { font-size: 13px; color: var(--text-soft); line-height: 1.65; flex: 1; }
.biz-card-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
.biz-badge {
  display: inline-block; padding: 3px 10px; border-radius: var(--radius-sm);
  font-size: 10.5px; font-weight: 700; letter-spacing: .04em;
}
.biz-badge.live { background: rgba(16,185,129,.12); color: #047857; border: 1px solid rgba(16,185,129,.25); }
.biz-badge.coming-soon { background: rgba(245,158,11,.15); color: #b45309; border: 1px solid rgba(245,158,11,.30); }
.biz-badge.empty { background: rgba(100,116,139,.10); color: var(--muted); border: 1px solid rgba(100,116,139,.20); }
.biz-badge.self { background: rgba(40,84,197,.10); color: var(--primary); border: 1px solid rgba(40,84,197,.22); }
.biz-arrow { font-size: 14px; color: var(--muted); transition: color .2s, transform .2s; }
.biz-card:not(.no-link):hover .biz-arrow { color: var(--primary); transform: translateX(3px); }

/* ---- gallery (事例ギャラリー) ---- */
.gallery-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
}
@media (max-width: 900px) { .gallery-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .gallery-grid { grid-template-columns: 1fr; } }
.gallery-item {
  position: relative; border-radius: var(--radius-sm); overflow: hidden;
  aspect-ratio: 4/5; isolation: isolate;
  box-shadow: var(--shadow-card);
  transition: transform .4s cubic-bezier(.22,1,.36,1), box-shadow .35s;
  cursor: pointer;
}
.gallery-item:hover { transform: translateY(-5px) scale(1.01); box-shadow: var(--shadow-card-hover); }
.gallery-item img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .9s ease, filter .3s; filter: saturate(.95); }
.gallery-item:hover img { transform: scale(1.08); filter: saturate(1.05); }
.gallery-item::after {
  content:''; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(15,23,42,0) 30%, rgba(15,23,42,.78) 100%);
}
.gallery-caption {
  position: absolute; left: 16px; right: 16px; bottom: 16px; z-index: 1; color: #fff;
}
.gallery-caption .tag {
  display: inline-block; padding: 3px 10px; border-radius: var(--radius-sm);
  background: rgba(255,255,255,.20); backdrop-filter: blur(6px);
  font-size: 10.5px; font-weight: 700; letter-spacing: .04em; margin-bottom: 6px;
}
.gallery-caption .title { font-size: 14.5px; font-weight: 800; line-height: 1.4; text-shadow: 0 2px 12px rgba(0,0,0,.40); }
.gallery-caption .meta { font-size: 11.5px; opacity: .85; margin-top: 4px; }

/* ---- fade-up animation ---- */
.fade-up {
  opacity: 0; transform: translateY(28px);
  transition: opacity .7s cubic-bezier(.22,1,.36,1), transform .7s cubic-bezier(.22,1,.36,1);
}
.fade-up.is-visible { opacity: 1; transform: translateY(0); }
.fade-up.d1 { transition-delay: .08s; }
.fade-up.d2 { transition-delay: .16s; }
.fade-up.d3 { transition-delay: .24s; }
.fade-up.d4 { transition-delay: .32s; }
.fade-up.d5 { transition-delay: .40s; }
.fade-up.d6 { transition-delay: .48s; }
@media (prefers-reduced-motion: reduce) {
  .fade-up { opacity: 1; transform: none; transition: none; }
}

/* ---- packages ---- */
.packages-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}
/* 診断結果で該当レベル以外を減光（.pkg-filter-active 時のみ） */
.packages-grid.pkg-filter-active .pkg-card { opacity: .34; transition: opacity .35s ease; }
.packages-grid.pkg-filter-active .pkg-card.pkg-match { opacity: 1; outline: 2px solid var(--primary); outline-offset: 2px; }
.pkg-card {
  grid-column: auto;
  min-height: 100%;
  min-width: 0;
  background:
    linear-gradient(145deg, rgba(255,255,255,.95), rgba(255,255,255,.78)),
    var(--glass-bg) !important;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,.86);
  transition: transform .25s cubic-bezier(.22,1,.36,1), box-shadow .25s, border-color .2s;
  position: relative;
  overflow: hidden;
}
.pkg-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(90deg, rgba(47,142,173,.08), transparent 44%, rgba(111,175,152,.05));
  opacity: .55;
}
.pkg-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,.85);
  border-color: rgba(0,152,200,.24);
}
.pkg-featured { grid-column: auto; }
.pkg-wide { grid-column: 1 / -1; }
.pkg-featured {
  background:
    linear-gradient(135deg, rgba(255,255,255,.82), rgba(238,247,255,.7) 42%, rgba(240,248,236,.76)),
    var(--glass-bg) !important;
}
.pkg-body {
  position: relative;
  z-index: 1;
  padding: 20px 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.pkg-topline { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.pkg-cat {
  font-size: 10.5px;
  font-weight: 800;
  letter-spacing: .08em;
  color: var(--primary);
  background: rgba(255,255,255,.56);
  border: 1px solid rgba(0,95,158,.14);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}
.pkg-head { display: block; }
.pkg-title {
  font-size: clamp(22px, 2.6vw, 30px);
  font-weight: 900;
  color: var(--text);
  line-height: 1.22;
  margin: 0;
  flex: 1;
  letter-spacing: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.pkg-meta { font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pkg-level {
  font-family: var(--mono); font-size: 10.5px; font-weight: 800; letter-spacing: .06em;
  padding: 3px 10px; border: 1px solid var(--glass-border); color: var(--primary);
  background: var(--primary-bg); border-radius: var(--radius-sm);
}
.pkg-price {
  font-size: 20px; font-weight: 900;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent;
}
.pkg-subsidy {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 800; color: #047857;
  background: rgba(209,250,229,.74); padding: 4px 10px; border-radius: var(--radius-sm);
  width: fit-content;
}
.pkg-desc { font-size: 13px; line-height: 1.78; color: var(--text-soft); flex: 1; margin: 0; }
.pkg-content,
.pkg-fit,
.pkg-req {
  display: grid;
  gap: 6px;
  margin: 2px 0 0;
  padding: 0;
  list-style: none;
}
.pkg-content li,
.pkg-fit li,
.pkg-req li {
  position: relative;
  padding-left: 18px;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text);
}
.pkg-content li::before,
.pkg-fit li::before,
.pkg-req li::before {
  content: "";
  position: absolute;
  left: 0;
  top: .66em;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--primary-soft);
  box-shadow: 0 0 0 4px rgba(43,167,200,.12);
}
.pkg-content-box {
  margin-top: 2px;
  padding: 12px 13px;
  border-radius: var(--radius-sm);
  background: rgba(47,142,173,.08);
  border: 1px solid rgba(47,142,173,.16);
}
.pkg-content-title {
  display: block;
  margin-bottom: 7px;
  font-size: 12px;
  font-weight: 900;
  color: var(--primary);
}
.pkg-req-box {
  margin-top: 4px;
  padding: 12px 13px;
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,.54);
  border: 1px solid rgba(40,84,197,.12);
}
.pkg-req-title {
  display: block;
  margin-bottom: 7px;
  font-size: 12px;
  font-weight: 900;
  color: var(--primary);
}
.pkg-verify {
  margin: 8px 0 0;
  font-size: 12px;
  line-height: 1.65;
  color: var(--muted);
}
.pkg-cta {
  display: inline-flex; align-items: center; justify-content: center;
  margin-top: auto; padding: 12px 16px;
  background: var(--grad);
  color: #fff; font-weight: 800; font-size: 14px;
  text-decoration: none; border-radius: var(--radius-sm);
  box-shadow: 0 6px 22px rgba(40,84,197,.22), inset 0 1px 0 rgba(255,255,255,.22);
  transition: opacity .15s ease, transform .15s ease;
}
.pkg-cta:hover { opacity: .92; transform: translateY(-1px); }
.pkg-material-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(40,84,197,.14);
  background: rgba(255,255,255,.62);
  color: var(--primary);
  font-size: 12.5px;
  font-weight: 800;
  text-decoration: none;
}
.pkg-material-link:hover { border-color: rgba(40,84,197,.28); }
.packages-note {
  margin-top: 22px; padding: 16px 20px;
  background: var(--grad-soft); border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  font-size: 13px; line-height: 1.75; color: var(--text);
}
@media (max-width: 1060px) {
  .pkg-card, .pkg-featured { grid-column: auto; }
  .pkg-wide { grid-column: 1 / -1; }
}
@media (max-width: 680px) {
  .pkg-card {
    min-width: 0;
    max-width: 100%;
  }
  #packages .section-sub { padding: 0 4px; }
  .packages-grid { grid-template-columns: 1fr; }
  .pkg-card, .pkg-featured, .pkg-wide { grid-column: auto; }
  .pkg-title { font-size: 22px; }
  #packages .section-title { font-size: 28px; line-height: 1.2; }
  #packages .section-title .title-line { display: block; }
}


/* ---- theme toggle ---- */
.theme-toggle {
  width: 38px; height: 38px; border-radius: var(--radius-sm);
  border: 1px solid var(--line); background: rgba(255,255,255,.84);
  font-size: 16px; cursor: pointer; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
  transition: transform .15s ease, border-color .15s ease, background .3s ease;
}
.theme-toggle:hover { transform: translateY(-1px); border-color: var(--primary); }
.theme-toggle-mobile { display: none; }
@media (max-width: 900px) {
  .theme-toggle-mobile { display: inline-flex; margin-right: 8px; }
}

/* ---- カード/パネル面は変数化 ---- */
.service-card, .biz-card { background: var(--bg-elev); }
.pkg-subsidy { background: var(--primary-bg); color: var(--primary-soft); }

/* ---- diagnose modal ---- */
.btn-diagnose {
  background: var(--primary); color: #fff;
  border: none; cursor: pointer; font-weight: 800; font-size: 15px;
  padding: 14px 26px; border-radius: var(--radius-sm);
  box-shadow: 0 10px 30px rgba(40,84,197,.22);
  transition: transform .15s ease, box-shadow .15s ease;
}
.btn-diagnose:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(15,143,114,.24); }
.packages-cta-row { display: flex; flex-direction: column; align-items: center; gap: 8px; margin-top: 28px; text-align: center; }
.packages-cta-hint { font-size: 12.5px; color: var(--muted); }
.diagnose-modal {
  position: fixed; inset: 0; z-index: 200; display: none;
  align-items: center; justify-content: center; padding: 20px;
  background: rgba(15,23,42,.55); backdrop-filter: blur(6px);
}
.diagnose-modal.open { display: flex; animation: diag-fade .2s ease; }
@keyframes diag-fade { from { opacity: 0; } to { opacity: 1; } }
.diagnose-box {
  background: var(--bg-white); border-radius: var(--radius-sm); max-width: 460px; width: 100%;
  padding: 28px 26px 26px; position: relative; box-shadow: 0 30px 80px rgba(0,0,0,.4);
  border: 1px solid var(--line);
}
.diagnose-close {
  position: absolute; top: 14px; right: 16px; border: none; background: none;
  font-size: 26px; line-height: 1; color: var(--muted); cursor: pointer;
}
.diagnose-head { font-size: 18px; font-weight: 800; color: var(--text); margin-bottom: 6px; }
.diagnose-intro { margin: 0 34px 16px 0; color: var(--text-soft); font-size: 13px; font-weight: 650; line-height: 1.65; }
.diag-progress { font-size: 12px; font-weight: 700; color: var(--primary); margin-bottom: 8px; }
.diag-q { font-size: 17px; font-weight: 800; color: var(--text); margin: 0 0 16px; line-height: 1.5; }
.diag-opts { display: flex; flex-direction: column; gap: 10px; }
.diag-opt {
  text-align: left; padding: 14px 16px; border-radius: 12px;
  border: 1.5px solid var(--line); background: var(--bg-base);
  font-size: 14px; font-weight: 600; color: var(--text); cursor: pointer;
  transition: border-color .15s ease, background .15s ease, transform .1s ease;
}
.diag-opt:hover { border-color: var(--primary); background: var(--primary-bg); transform: translateX(2px); }
.diag-result { text-align: center; }
.diag-result-badge { font-family: var(--mono); font-size: 11px; font-weight: 700; letter-spacing: .08em; color: var(--primary-soft); background: var(--primary-bg); border: 1px solid var(--glass-border); display: inline-block; padding: 5px 14px; border-radius: 999px; margin-bottom: 12px; }
.diag-result-lv { font-size: 14px; font-weight: 700; color: var(--primary); margin-bottom: 4px; }
.diag-result-name { font-family: var(--serif); font-size: 26px; font-weight: 900; color: var(--text); margin: 6px 0; line-height: 1.3; overflow-wrap: anywhere; }
.diag-result-desc { font-size: 14px; line-height: 1.8; color: var(--text-soft); margin: 0 0 18px; }
.diag-result-meta { color: var(--primary); font-size: 13px; font-weight: 800; margin: -8px 0 16px; }
.diag-result .btn { display: flex; width: 100%; justify-content: center; margin-bottom: 8px; }
.diag-result .btn { display: inline-flex; }
.diag-restart { display: block; margin: 14px auto 0; border: none; background: none; color: var(--muted); font-size: 12.5px; text-decoration: underline; cursor: pointer; }

/* ---- parallax band ---- */
.parallax-band {
  position: relative; margin: 64px calc(50% - 50vw); width: 100vw;
  min-height: 420px; display: flex; align-items: center; justify-content: center;
  overflow: hidden; isolation: isolate;
}
.parallax-bg {
  position: absolute; inset: -10% 0; z-index: -2;
  background-size: cover; background-position: center;
  will-change: transform;
}
.parallax-overlay {
  position: absolute; inset: 0; z-index: -1;
  background: linear-gradient(120deg, rgba(10,15,28,.88) 0%, rgba(10,15,28,.55) 55%, rgba(139,160,255,.30) 100%);
}
.parallax-content { max-width: 720px; padding: 64px 24px; text-align: center; color: #fff; }
.parallax-eyebrow { font-size: 13px; font-weight: 800; letter-spacing: .2em; color: #c7d6ff; margin: 0 0 12px; }
.parallax-title { font-size: clamp(24px, 4vw, 40px); font-weight: 900; line-height: 1.3; margin: 0 0 16px; color: #fff; }
.parallax-sub { font-size: clamp(14px, 1.6vw, 17px); line-height: 1.8; margin: 0 0 26px; color: rgba(255,255,255,.92); }
.parallax-content .btn-primary { box-shadow: 0 14px 40px rgba(0,0,0,.3); }
@media (max-width: 560px) { .parallax-band { min-height: 340px; } }

/* ---- flow steps ---- */
.flow-list {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  counter-reset: step;
}
@media (max-width: 900px) { .flow-list { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .flow-list { grid-template-columns: 1fr; } }
.flow-step {
  padding: 24px 22px; border-radius: var(--radius-sm);
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  position: relative;
}
.flow-step::before {
  counter-increment: step;
  content: "0" counter(step);
  position: absolute; top: 14px; right: 18px;
  font-size: 26px; font-weight: 800; color: rgba(139,160,255,.18);
  letter-spacing: 0;
}
.flow-step h3 { font-size: 15px; font-weight: 700; color: var(--text); margin: 0 0 8px; }
.flow-step p { font-size: 13px; color: var(--text-soft); margin: 0; line-height: 1.7; }

/* ---- use cases / growth plan ---- */
.usecase-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
@media (max-width: 900px) { .usecase-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .usecase-grid { grid-template-columns: 1fr; } }
.usecase-card {
  min-height: 190px;
  padding: 24px 22px;
  border-radius: var(--radius);
  background:
    linear-gradient(145deg, rgba(255,255,255,.94), rgba(245,252,249,.84)),
    var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,.82);
}
.usecase-label {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background: var(--primary-bg);
  color: var(--primary);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
}
.usecase-card h3 {
  margin: 14px 0 8px;
  font-size: 18px;
  line-height: 1.35;
  color: var(--text);
}
.usecase-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.78;
  color: var(--text-soft);
}
.growth-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
  gap: 18px;
}
@media (max-width: 900px) { .growth-layout { grid-template-columns: 1fr; } }
.growth-panel {
  padding: 26px;
  border-radius: var(--radius);
  background: rgba(255,255,255,.88);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card);
}
.growth-panel h3 {
  margin: 0 0 16px;
  font-size: 20px;
  color: var(--text);
}
.growth-table {
  display: grid;
  gap: 10px;
}
.growth-row {
  display: grid;
  grid-template-columns: minmax(120px, .72fr) minmax(0, 1fr) minmax(0, 1.18fr);
  gap: 12px;
  align-items: start;
  padding: 14px 0;
  border-top: 1px solid var(--line);
}
.growth-row:first-child { border-top: 0; }
.growth-row strong {
  font-size: 13px;
  line-height: 1.55;
  color: var(--primary);
}
.growth-row span,
.growth-row em {
  font-size: 12.5px;
  line-height: 1.65;
  color: var(--text-soft);
  font-style: normal;
}
.growth-row em {
  color: var(--text);
  font-weight: 700;
}
@media (max-width: 680px) {
  .growth-row { grid-template-columns: 1fr; gap: 4px; }
}
.growth-actions {
  background:
    radial-gradient(140% 110% at 100% 0%, rgba(47,142,173,.14), transparent 58%),
    rgba(255,255,255,.90);
}
.growth-action {
  padding: 15px 0;
  border-top: 1px solid var(--line);
}
.growth-action:first-of-type { border-top: 0; }
.growth-action b {
  display: block;
  color: var(--primary);
  font-size: 14px;
  margin-bottom: 4px;
}
.growth-action p {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.75;
}

/* ---- lecture preview ---- */
.lecture-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px;
}
.lecture-carousel-wrap {
  margin-top: 8px;
}
.pf-carousel.lecture-carousel {
  grid-auto-columns: minmax(260px, 300px);
}
.pf-carousel.lecture-carousel > .lecture-card {
  scroll-snap-align: start;
}
.lecture-card {
  display: flex; flex-direction: column; gap: 0;
  padding: 0; border-radius: var(--radius-sm); overflow: hidden;
  background: var(--bg-white); border: 1px solid var(--line);
  text-decoration: none; color: inherit;
  box-shadow: var(--shadow-card);
  transition: transform .2s, border-color .2s, box-shadow .2s;
}
.lecture-card-media {
  display: block; width: 100%; aspect-ratio: 1200 / 630; overflow: hidden;
  background: #edf4fb; border-bottom: 1px solid var(--line);
}
.lecture-card-media img {
  display: block; width: 100%; height: 100%; object-fit: cover;
  transition: transform .35s ease;
}
.lecture-card:hover .lecture-card-media img { transform: scale(1.025); }
.lecture-card-body { display: flex; flex: 1; flex-direction: column; gap: 6px; padding: 18px 20px 20px; }
.lecture-card:hover { transform: translateY(-3px); border-color: rgba(40,84,197,.26); box-shadow: var(--shadow-card-hover); }
.lecture-title { font-size: 14.5px; font-weight: 800; color: var(--primary); line-height: 1.4; }
.lecture-date { font-size: 11.5px; color: var(--muted); font-weight: 600; }
.lecture-summary {
  font-size: 12.5px; color: var(--text-soft); line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.see-all {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 13px; font-weight: 700; color: var(--primary);
  text-decoration: none; margin-top: 16px;
}
.see-all:hover { text-decoration: underline; }

/* ---- speaker section intro grid (PC: 2col, mobile: 1col) ---- */
.speaker-intro-grid {
  display: grid; grid-template-columns: 1fr 280px; gap: 36px; align-items: center;
}
@media (max-width: 720px) {
  .speaker-intro-grid { grid-template-columns: 1fr; gap: 24px; text-align: center; }
  .speaker-intro-grid .profile-avatar { margin: 0 auto; }
}
@media (max-width: 760px) {
  .pf-carousel.lecture-carousel { grid-auto-columns: 78%; }
}
/* 講師ビジュアル（本人写真を自然な丸いポートレートとして表示） */
.speaker-art {
  position: relative;
  overflow: hidden;
  width: min(100%, 300px);
  min-height: 0;
  aspect-ratio: 1 / 1;
  align-self: center;
  justify-self: center;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 38%, #FFFFFF 0 42%, #F5F7F4 72%, #E7EEE9 100%);
  border: 10px solid #fff;
  box-shadow: 0 16px 38px rgba(18,32,51,.12), 0 0 0 1px rgba(18,32,51,.08);
}
.speaker-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 50%;
  display: block;
  transform: scale(1.02);
  transform-origin: center;
  filter: saturate(.94) contrast(1.02) brightness(1.01);
}
.speaker-art-animated { animation: none; isolation: auto; }
.speaker-art::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(255,255,255,.12), rgba(255,255,255,0) 36%, rgba(18,32,51,.04) 100%);
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.34);
}
.speaker-art-orbit,
.speaker-art-chip,
.speaker-art-spark { display: none; }
@media (max-width: 720px) {
  .speaker-art { max-width: 260px; margin: 0 auto; }
}
.speaker-page-visual {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 300px);
  gap: 28px;
  align-items: center;
  margin: 0 0 34px;
  padding: 28px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: linear-gradient(140deg, rgba(255,255,255,.96), rgba(247,250,248,.92));
  box-shadow: var(--shadow-card);
}
.speaker-page-copy {
  min-width: 0;
}
.speaker-page-copy p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.85;
}
.speaker-page-role {
  color: var(--primary) !important;
  font-weight: 900;
  margin: 0 0 10px !important;
}
.speaker-page-visual .speaker-art {
  min-height: 0;
  width: min(100%, 260px);
}
@media (max-width: 760px) {
  .speaker-page-visual {
    grid-template-columns: 1fr;
    padding: 20px;
    text-align: left;
  }
}
/* CSSプレースホルダ: クライミング×テクノロジーの抽象アート */
.speaker-art-ph {
  background:
    radial-gradient(120% 80% at 80% 10%, rgba(139,160,255,.20), transparent 55%),
    radial-gradient(100% 90% at 0% 100%, rgba(139,160,255,.10), transparent 50%),
    linear-gradient(160deg, #0C1424 0%, #0A0F1C 100%);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px;
}
.speaker-art-ph .sa-grid {
  position: absolute; inset: 0; pointer-events: none; opacity: .5;
  background-image:
    linear-gradient(rgba(139,160,255,.10) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139,160,255,.10) 1px, transparent 1px);
  background-size: 28px 28px;
  -webkit-mask-image: radial-gradient(80% 80% at 70% 30%, #000, transparent 75%);
  mask-image: radial-gradient(80% 80% at 70% 30%, #000, transparent 75%);
}
.speaker-art-ph .sa-glow {
  position: absolute; width: 200px; height: 200px; border-radius: 50%;
  background: radial-gradient(circle, rgba(139,160,255,.45), transparent 65%);
  filter: blur(40px); top: 8%; right: -10%;
}
.speaker-art-ph .sa-mark {
  position: relative; z-index: 1;
  font-family: var(--serif); font-weight: 900; font-size: 96px; line-height: 1;
  color: var(--primary);
  text-shadow: 0 0 40px rgba(139,160,255,.5);
}
.speaker-art-ph .sa-cap {
  position: relative; z-index: 1; text-align: center;
  font-size: 12.5px; color: var(--text-soft); line-height: 1.7; padding: 0 18px;
}
.speaker-art-ph .sa-mono {
  font-family: var(--mono); font-size: 11px; letter-spacing: .18em; color: var(--primary-soft);
}

/* ---- profile section ---- */
.profile-block {
  display: grid; grid-template-columns: minmax(0, 1fr) 220px; gap: 32px;
  align-items: center;
  padding: 32px; border-radius: var(--radius-sm);
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
}
@media (max-width: 720px) { .profile-block { grid-template-columns: 1fr; text-align: center; } }
.profile-block h3 { font-size: 22px; font-weight: 700; margin: 0 0 10px; color: var(--text); }
.profile-block p { font-size: 14px; color: var(--text-soft); line-height: 1.85; margin: 0 0 10px; }
.profile-avatar {
  width: 200px; height: 200px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-bg), #fce7f3);
  display: flex; align-items: center; justify-content: center;
  font-size: 88px; box-shadow: 0 12px 36px rgba(15,23,42,.10);
  border: 6px solid #fff;
  justify-self: center;
  overflow: hidden;
}
.profile-avatar img { width: 100%; height: 100%; object-fit: cover; object-position: center 30%; display: block; }

/* ---- FAQ ---- */
.faq-list { max-width: 760px; margin: 0 auto; }
.faq-item {
  border: 1px solid var(--line); border-radius: var(--radius-sm);
  background: var(--bg-white); margin-bottom: 10px;
  box-shadow: var(--shadow-card);
}
.faq-item summary {
  padding: 16px 20px; cursor: pointer; font-size: 14.5px; font-weight: 700;
  color: var(--text); list-style: none; display: flex; justify-content: space-between; align-items: center;
}
.faq-item summary::-webkit-details-marker { display: none; }
.faq-item summary::after { content: "+"; font-size: 22px; color: var(--primary); font-weight: 300; transition: transform .2s; }
.faq-item[open] summary::after { transform: rotate(45deg); }
.faq-item p {
  padding: 0 20px 18px; font-size: 13.5px; color: var(--text-soft); margin: 0; line-height: 1.75;
}

/* ---- contact ---- */
.contact-block {
  margin-top: 16px;
  padding: 48px 32px; border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
  color: #fff; text-align: center;
}
.contact-block h2 { font-size: clamp(22px, 3vw, 30px); font-weight: 800; margin: 0 0 10px; color: #fff; }
.contact-block p { font-size: 14px; opacity: .85; margin: 0 0 24px; }
.contact-mail {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 32px; border-radius: var(--radius-sm);
  background: #fff; color: var(--primary);
  font-size: 14.5px; font-weight: 800; text-decoration: none;
  box-shadow: 0 8px 24px rgba(0,0,0,.18);
  transition: transform .2s, box-shadow .2s;
}
.contact-mail:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(0,0,0,.24); }

/* ---- explore (メニュー集約カード) ---- */
.explore-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;
}
@media (max-width: 760px) { .explore-grid { grid-template-columns: 1fr; } }
.section-more { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 28px; }
/* スクリーンリーダー/クローラには読ませるが視覚的には隠す（SEOキーワード補強用） */
.visually-hidden {
  position: absolute !important; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0);
  white-space: nowrap; border: 0;
}
.explore-card {
  display: flex; flex-direction: column; gap: 10px;
  padding: 26px 22px; background: var(--bg-elev); border: 1px solid var(--line);
  border-radius: var(--radius-sm); text-decoration: none; color: var(--text);
  transition: border-color .18s, transform .15s, background .18s;
}
.explore-card:hover { border-color: var(--primary); transform: translateY(-4px); }
.explore-ico { font-size: 30px; line-height: 1; }
.explore-title { font-size: 16px; font-weight: 800; color: var(--text); margin: 4px 0 0; line-height: 1.4; }
.explore-desc { font-size: 13px; color: var(--text-soft); line-height: 1.8; margin: 0; flex: 1; }
.explore-cta { font-family: var(--mono); font-size: 12px; font-weight: 700; color: var(--primary-soft); margin-top: 6px; }

/* ---- contact choices (メール / LINE の2導線) ---- */
/* 主導線: 個別相談の予約カード */
.contact-primary {
  display: flex; align-items: center; gap: 18px;
  max-width: 680px; margin: 0 auto; padding: 22px 26px;
  border-radius: var(--radius); text-decoration: none;
  background: var(--grad); color: #fff;
  box-shadow: 0 14px 38px rgba(40,84,197,.24), inset 0 1px 0 rgba(255,255,255,.25);
  transition: transform .2s, filter .2s, box-shadow .2s;
}
.contact-primary:hover { transform: translateY(-2px); filter: brightness(1.06); box-shadow: 0 20px 46px rgba(15,143,114,.22); }
.cp-ico { font-size: 34px; flex: 0 0 auto; }
.cp-body { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.cp-title { font-size: 19px; font-weight: 800; }
.cp-desc { font-size: 13px; opacity: .92; line-height: 1.6; }
.cp-cta { flex: 0 0 auto; font-weight: 700; white-space: nowrap; }
@media (max-width: 560px) {
  .contact-primary { flex-wrap: wrap; gap: 10px; padding: 18px 18px; }
  .cp-cta { width: 100%; text-align: center; padding-top: 8px; border-top: 1px solid rgba(255,255,255,.25); }
}
.contact-or { text-align: center; color: var(--muted); font-size: 13px; margin: 22px 0 14px; }
/* 受講者の声 */
.voices-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; max-width: 960px; margin: 0 auto; }
.voice-card { background: var(--bg-white); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px 22px; box-shadow: var(--shadow-card); display: flex; flex-direction: column; gap: 12px; }
.voice-quote { margin: 0; font-size: 15px; font-weight: 700; line-height: 1.8; color: var(--text); }
.voice-ba { align-self: flex-start; font-size: 12px; font-weight: 700; color: var(--primary); background: var(--primary-bg); border: 1px solid var(--glass-border); border-radius: 999px; padding: 4px 12px; }
.voice-who { font-size: 12.5px; color: var(--muted); }
.voices-sample-note { text-align: center; font-size: 12px; color: var(--muted); margin: -24px auto 28px; }
.contact-choices {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  max-width: 680px; margin: 0 auto;
}
@media (max-width: 680px) { .contact-choices { grid-template-columns: 1fr; } }
.contact-choice {
  display: flex; flex-direction: column; gap: 8px;
  padding: 28px 24px; text-decoration: none;
  background: var(--bg-elev); border: 1px solid var(--line); border-radius: var(--radius-sm);
  transition: border-color .18s, transform .15s;
}
.contact-choice:hover { transform: translateY(-4px); }
.contact-choice.cc-mail:hover { border-color: var(--primary); }
.contact-choice.cc-line:hover { border-color: #06C755; }
.cc-ico {
  font-size: 30px; line-height: 1;
  width: 56px; height: 56px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
}
.cc-mail .cc-ico { background: var(--primary-bg); }
.cc-line .cc-ico { background: rgba(6,199,85,.14); }
.cc-title { font-size: 17px; font-weight: 800; color: var(--text); margin-top: 4px; }
.cc-desc { font-size: 13px; color: var(--text-soft); line-height: 1.8; flex: 1; }
.cc-cta { font-family: var(--mono); font-size: 12px; font-weight: 700; margin-top: 6px; }
.cc-mail .cc-cta { color: var(--primary-soft); }
.cc-line .cc-cta { color: #06C755; }
.contact-sub-note { text-align: center; font-size: 13px; color: var(--text-soft); margin: 22px 0 0; }
.link-btn {
  background: none; border: none; padding: 0; cursor: pointer;
  font: inherit; font-weight: 700; color: var(--primary); text-decoration: underline;
}
.link-btn:hover { color: var(--primary-soft); }

/* ---- footer (リッチ: ナビ + NAP + CTA) ---- */
footer.site-footer {
  margin-top: 64px; padding: 48px 0 16px;
  color: var(--text-soft); font-size: 13px;
  border-top: 1px solid var(--line);
}
.footer-grid {
  display: grid; grid-template-columns: 1.6fr 1fr 1.2fr; gap: 32px;
  max-width: 1000px; margin: 0 auto 32px;
}
@media (max-width: 760px) { .footer-grid { grid-template-columns: 1fr; gap: 28px; text-align: left; } }
.footer-logo { display: inline-flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 800; color: var(--text); }
.footer-logo .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--grad); box-shadow: 0 0 12px rgba(40,84,197,.42); }
.footer-tagline { margin: 12px 0 16px; line-height: 1.8; color: var(--text-soft); max-width: 380px; }
.footer-cta {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 11px 22px; border-radius: 999px;
  background: var(--grad); color: #fff; font-weight: 700; font-size: 13.5px;
  text-decoration: none; box-shadow: 0 6px 22px rgba(40,84,197,.24);
  transition: transform .2s, filter .2s;
}
.footer-cta:hover { transform: translateY(-1px); filter: brightness(1.08); }
.footer-nav, .footer-nap { display: flex; flex-direction: column; gap: 9px; }
.footer-nav-head { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: 4px; }
.footer-nav a { color: var(--text-soft); text-decoration: none; transition: color .2s; }
.footer-nav a:hover { color: var(--primary); }
.footer-nap p { margin: 0; line-height: 1.7; }
.footer-nap a { color: var(--primary-soft); text-decoration: none; }
.footer-area { margin-top: 6px !important; font-size: 12px; color: var(--muted); }
.footer-copy { text-align: center; font-size: 12px; color: var(--muted); padding-top: 20px; border-top: 1px solid var(--line); }

/* ---- sticky モバイルCTA（スクロール中も常時相談導線）---- */
.sticky-cta {
  position: fixed; left: 12px; right: 12px; bottom: 12px; z-index: 90;
  display: none; align-items: center; justify-content: space-between; gap: 12px;
  padding: 10px 12px 10px 18px; border-radius: 999px;
  background: var(--glass-bg); border: 1px solid var(--glass-border);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 12px 40px rgba(0,0,0,.45);
}
.sticky-cta-text { display: flex; flex-direction: column; line-height: 1.25; }
.sticky-cta-text strong { font-size: 13px; color: var(--text); }
.sticky-cta-text span { font-size: 11px; color: var(--text-soft); }
.sticky-cta-btn {
  flex: 0 0 auto; padding: 11px 18px; border-radius: 999px;
  background: var(--grad); color: #fff; font-weight: 700; font-size: 13.5px;
  text-decoration: none; white-space: nowrap;
  box-shadow: 0 6px 18px rgba(40,84,197,.25), inset 0 1px 0 rgba(255,255,255,.25);
}
@media (max-width: 760px) { .sticky-cta { display: flex; } }
@media (prefers-reduced-motion: no-preference) { .sticky-cta { transition: transform .3s ease, opacity .3s ease; } }

/* ---- Portfolio cards (kept for non-public internal reuse; not linked from the top page) ---- */
.pf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 8px;
}
/* Portfolio carousel */
.pf-carousel-wrap { position: relative; margin: 16px 0 8px; }
.pf-carousel {
  display: grid; grid-auto-flow: column;
  grid-auto-columns: minmax(260px, 300px);
  gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory;
  scroll-behavior: smooth; padding: 6px 4px 18px;
  -ms-overflow-style: none; scrollbar-width: thin;
}
.pf-carousel > .pf-card { scroll-snap-align: start; }
.pf-carousel::-webkit-scrollbar { height: 8px; }
.pf-carousel::-webkit-scrollbar-thumb { background: var(--line-strong); border-radius: 999px; }
.pf-arrow {
  position: absolute; top: 50%; transform: translateY(-50%); z-index: 3;
  width: 44px; height: 44px; border-radius: 50%; cursor: pointer;
  border: 1px solid var(--glass-border); background: var(--glass-bg);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: var(--text); font-size: 26px; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow-card); transition: transform .15s, border-color .15s, box-shadow .15s;
}
.pf-arrow:hover { transform: translateY(-50%) scale(1.08); border-color: var(--primary); box-shadow: 0 14px 28px rgba(40,84,197,.16); }
.pf-prev { left: -10px; }
.pf-next { right: -10px; }
@media (max-width: 760px) { .pf-arrow { display: none; } .pf-carousel { grid-auto-columns: 78%; } }
.pf-card {
  display: flex; flex-direction: column;
  background: var(--bg-white);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 14px 16px 12px;
  box-shadow: var(--shadow-card);
  transition: transform .25s, border-color .25s, box-shadow .25s;
  text-decoration: none; color: inherit;
  min-height: 150px;
}
.pf-card:hover {
  transform: translateY(-4px);
  border-color: rgba(40,84,197,.24);
  box-shadow: var(--shadow-card-hover);
}
.pf-card .pf-thumb {
  position: relative;
  display: block; margin: -14px -16px 12px; /* カード内パディングを打ち消して全幅バナーに */
  border-radius: var(--radius-sm) var(--radius-sm) 0 0; overflow: hidden;
  aspect-ratio: 16 / 9; background: var(--bg-elev);
}
.pf-card .pf-thumb svg, .pf-card .pf-thumb img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: top center; }
.pf-card .pf-thumb.is-site-shot { box-shadow: inset 0 1px 0 rgba(255,255,255,.82); }
.pf-card .pf-thumb.is-site-shot::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  z-index: 2;
  height: 18px;
  background:
    radial-gradient(circle at 10px 9px, #EF6864 0 3px, transparent 3.4px),
    radial-gradient(circle at 22px 9px, #F5B445 0 3px, transparent 3.4px),
    linear-gradient(180deg, rgba(255,255,255,.94), rgba(244,248,249,.76));
  border-bottom: 1px solid rgba(18,32,51,.10);
  pointer-events: none;
}
.pf-card .pf-thumb.is-site-shot::after {
  content: "";
  position: absolute;
  inset: 18px 0 0;
  z-index: 2;
  background: linear-gradient(180deg, transparent 62%, rgba(7,20,38,.16));
  pointer-events: none;
}
.pf-card .pf-title { font-weight: 800; font-size: 15px; color: var(--text); }
.pf-card .pf-host { font-size: 11.5px; color: var(--muted); margin-top: 2px; word-break: break-all; }
.pf-card .pf-sum { font-size: 13px; color: var(--text-soft); line-height: 1.55; margin: 8px 0 10px; flex: 1; }
.pf-card .pf-meta { display: flex; flex-wrap: wrap; gap: 6px; font-size: 11px; }
.pf-card .pf-chip {
  padding: 2px 8px; border-radius: var(--radius-sm);
  background: rgba(40,84,197,.08); color: var(--primary);
  border: 1px solid rgba(40,84,197,.16);
}
.pf-card .pf-chip.cat { background: rgba(40,84,197,.08); color: var(--primary); border-color: rgba(40,84,197,.16); }
.pf-card .pf-chip.retired { background: rgba(120,120,120,.2); color: var(--muted); }
.pf-card .pf-chip.dev { background: rgba(245,158,11,.15); color: #b45309; border-color: rgba(245,158,11,.35); }

/* ---- 経歴タイムライン（LP #profile。build_site CONTENT_CSS から移植・PORTALトークン化）---- */
.profile-timeline {
  position: relative;
  margin: 16px 0 8px;
  padding-left: 28px;
  border-left: 2px solid var(--line);
}
.profile-tl-item {
  position: relative;
  margin-bottom: 28px;
  padding: 16px 18px;
  background: var(--bg-white);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-card);
  transition: border-color .2s ease, transform .2s ease;
}
.profile-tl-item:hover { border-color: rgba(40,84,197,.22); transform: translateX(2px); }
.profile-tl-item::before {
  content: ''; position: absolute; left: -36px; top: 22px;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--primary); border: 3px solid #fff;
  box-shadow: 0 0 0 3px rgba(40,84,197,.14);
}
.profile-tl-year { font-size: 13px; font-weight: 700; color: var(--primary); letter-spacing: .03em; margin-bottom: 4px; }
.profile-tl-role { font-size: 16px; font-weight: 800; color: var(--text); margin-bottom: 8px; line-height: 1.4; }
.profile-tl-desc { font-size: 14px; color: var(--text-soft); line-height: 1.75; margin-bottom: 10px; }
.profile-tl-desc strong { color: var(--primary); }
@media (max-width: 640px) {
  .profile-timeline { padding-left: 22px; }
  .profile-tl-item::before { left: -30px; }
}
"""

PORTAL_CSS += """

/* ---- AI seminar landing redesign (Figma/community inspired, original implementation) ---- */
:root {
  --bg-base: #F8FAFC;
  --bg-white: #FFFFFF;
  --bg-elev: #FFFFFF;
  --text: #0B1B33;
  --text-soft: #35475E;
  --muted: #6C7A8C;
  --line: rgba(11,27,51,.12);
  --line-strong: rgba(11,27,51,.24);
  --primary: #007F8F;
  --primary-soft: #0E9BA8;
  --emerald: #86A81E;
  --coral: #E8654D;
  --primary-bg: rgba(0,127,143,.08);
  --grad: linear-gradient(135deg, #007F8F 0%, #0B9B96 64%, #6F9E27 100%);
  --grad-soft: linear-gradient(135deg, rgba(0,127,143,.09), rgba(134,168,30,.08));
  --radius: 8px;
  --radius-sm: 8px;
  --shadow-card: 0 1px 2px rgba(11,27,51,.05), 0 14px 38px rgba(11,27,51,.07);
  --shadow-card-hover: 0 8px 20px rgba(11,27,51,.08), 0 24px 54px rgba(0,127,143,.13);
}

body {
  background:
    linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 58%, #EEF7F7 100%);
  overflow-x: hidden;
}

.container {
  max-width: 1280px;
  padding: 0 28px 80px;
}

.site-header-inner { max-width: 1280px; }
.site-header.scrolled,
.site-header:hover {
  background: rgba(255,255,255,.92);
  border-bottom-color: rgba(11,27,51,.10);
}
.nav-cta { border-radius: 8px; }
.menu-toggle,
.theme-toggle,
.mobile-toggle { border-radius: 8px; }

.hero {
  min-height: min(748px, calc(100svh - 18px));
  padding: 92px 0 44px;
  grid-template-columns: minmax(0, .9fr) minmax(460px, 1.1fr);
  gap: 54px;
}
.hero .fade-up {
  opacity: 1;
  transform: none;
}
.hero::before {
  background:
    linear-gradient(90deg, #FFFFFF 0%, rgba(255,255,255,.98) 42%, rgba(239,248,249,.88) 100%),
    linear-gradient(180deg, rgba(0,127,143,.035), transparent 40%);
  border-top: 0;
  border-bottom: 1px solid rgba(11,27,51,.10);
}
.hero .eyebrow {
  display: inline-flex;
  max-width: fit-content;
  color: var(--primary);
  font-size: 13px;
  font-family: var(--serif);
  font-weight: 900;
  letter-spacing: 0;
}
.hero h1 {
  margin: 14px 0 18px;
  font-size: clamp(46px, 6.2vw, 82px);
  line-height: 1.02;
}
.fusion-logo-large {
  display: inline-flex;
  align-items: baseline;
  gap: .18em;
}
.fusion-logo-large .ai,
.fusion-logo-large .hub {
  color: var(--text);
}
.hero-title-sub {
  margin-top: 10px;
  font-size: clamp(24px, 2.9vw, 38px);
  color: var(--text);
}
.hero-title-sub strong { color: var(--primary); }
.hero .sub-catch {
  max-width: 640px;
  font-size: clamp(16px, 1.7vw, 20px);
  line-height: 1.65;
}
.hero .lead {
  max-width: 640px;
  font-size: 15.5px;
  line-height: 1.95;
}
.hero-actions { gap: 14px; }
.btn-lg { padding: 15px 24px; }
.hero-proof-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 28px 0 0;
  max-width: 650px;
}
.hero-proof {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  padding: 12px 10px;
  border-top: 1px solid rgba(11,27,51,.12);
  color: var(--text);
}
.hero-proof .proof-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary);
  color: #fff;
  font-size: 15px;
  font-weight: 900;
}
.hero-proof b {
  display: block;
  font-size: 13.5px;
  line-height: 1.25;
}
.hero-proof span {
  display: block;
  margin-top: 2px;
  color: var(--muted);
  font-size: 11.5px;
  line-height: 1.4;
}
.hero-entry-strip { display: none; }

.hero-photo-card {
  width: min(100%, 690px);
  aspect-ratio: 16 / 10;
  padding: 0;
  border-radius: 0;
  border: 0;
  background: #EAF4F5;
  box-shadow: 0 26px 74px rgba(11,27,51,.14);
}
.hero-photo-card img {
  border-radius: 0;
  object-position: center;
}
.hero-photo-card::after {
  inset: 0;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(255,255,255,.50) 0%, rgba(255,255,255,.06) 34%, rgba(11,27,51,.06) 100%),
    linear-gradient(180deg, rgba(255,255,255,0) 58%, rgba(11,27,51,.22) 100%);
}
.hero-photo-note,
.hero-photo-map,
.hero-mini-routes { display: none; }
.hero-lesson-board {
  position: absolute;
  right: 24px;
  top: 24px;
  z-index: 5;
  width: min(43%, 286px);
  padding: 18px;
  border: 1px solid rgba(11,27,51,.10);
  border-radius: 8px;
  background: rgba(255,255,255,.94);
  box-shadow: 0 18px 46px rgba(11,27,51,.13);
  backdrop-filter: blur(12px) saturate(130%);
  -webkit-backdrop-filter: blur(12px) saturate(130%);
}
.lesson-board-title {
  margin: 0 0 14px;
  color: var(--text);
  font-size: 15px;
  font-weight: 900;
  line-height: 1.45;
}
.lesson-board-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.lesson-board-item {
  min-height: 72px;
  padding: 10px 8px;
  border: 1px solid rgba(0,127,143,.16);
  border-radius: 8px;
  background: #F8FCFC;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  text-align: center;
}
.lesson-board-item svg {
  display: block;
  width: 24px;
  height: 24px;
  margin: 0 auto;
  color: var(--primary);
}
.lesson-board-item span {
  color: var(--text-soft);
  font-size: 10.5px;
  font-weight: 800;
  line-height: 1.25;
}
.hero-class-caption {
  position: absolute;
  left: 22px;
  bottom: 22px;
  z-index: 5;
  max-width: 300px;
  padding: 13px 15px;
  border-radius: 8px;
  background: rgba(255,255,255,.92);
  border: 1px solid rgba(255,255,255,.70);
  box-shadow: 0 14px 34px rgba(11,27,51,.12);
}
.hero-class-caption b {
  display: block;
  color: var(--text);
  font-size: 13px;
  line-height: 1.35;
}
.hero-class-caption span {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  font-size: 11px;
  line-height: 1.45;
}

section.block { padding: 72px 0; }
#packages { padding-top: 66px; }
.section-title {
  font-size: clamp(30px, 4vw, 46px);
}
.section-heading {
  font-size: 12px;
  color: var(--primary);
  background: none;
  -webkit-background-clip: initial;
  background-clip: initial;
}
.section-sub {
  max-width: 760px;
  font-size: 15px;
}

.packages-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}
.pkg-card,
.pkg-featured {
  grid-column: auto;
}
.pkg-wide { grid-column: 1 / -1; }
.pkg-card {
  border: 1px solid rgba(11,27,51,.13);
  background: #fff !important;
  box-shadow: 0 1px 2px rgba(11,27,51,.04);
}
.pkg-card::before {
  background: linear-gradient(90deg, rgba(0,127,143,.07), transparent 52%, rgba(232,101,77,.045));
}
.pkg-card:hover {
  border-color: rgba(0,127,143,.28);
  box-shadow: var(--shadow-card-hover);
}
.pkg-body {
  padding: 26px 24px 24px;
  gap: 12px;
}
.pkg-cat {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--primary);
}
.pkg-title {
  font-size: clamp(23px, 2.4vw, 31px);
}
.pkg-meta {
  gap: 10px;
}
.pkg-level,
.pkg-subsidy {
  border-radius: 8px;
}
.pkg-price {
  color: var(--text);
  background: none;
  -webkit-background-clip: initial;
  background-clip: initial;
}
.pkg-content-box,
.pkg-req-box {
  background: #F8FBFC;
  border-color: rgba(0,127,143,.13);
}
.pkg-fit {
  padding-top: 2px;
}
.pkg-fit li {
  color: var(--text-soft);
}
.pkg-cta {
  border-radius: 8px;
}
.packages-note {
  background: #F5FAFA;
  border-color: rgba(0,127,143,.15);
}

.usecase-card,
.lecture-card,
.growth-panel,
.profile-block,
.flow-step,
.faq-item {
  border-radius: 8px;
  background: #fff;
  border-color: rgba(11,27,51,.12);
  box-shadow: 0 1px 2px rgba(11,27,51,.04);
}
.usecase-card {
  min-height: 214px;
  padding: 26px 22px;
  text-align: center;
}
.usecase-label {
  display: inline-flex;
  min-width: 58px;
  min-height: 58px;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  border: 2px solid rgba(0,127,143,.78);
  border-radius: 8px;
  color: var(--primary);
  font-weight: 900;
  background: #F8FCFC;
}
.usecase-card h3 {
  font-size: 16px;
  color: var(--text);
}
.usecase-card p {
  color: var(--text-soft);
}
.lecture-card {
  min-height: 170px;
  border-top: 4px solid var(--primary);
}
.lecture-title {
  color: var(--text);
  font-size: 15px;
}
.growth-layout { gap: 22px; }
.growth-action {
  border-radius: 8px;
}
.contact-primary {
  border-radius: 8px;
  background: linear-gradient(135deg, #007F8F 0%, #0B9B96 100%);
}

@media (max-width: 1040px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: 0;
    padding-top: 92px;
  }
  .hero-text { text-align: left; }
  .hero .sub-catch,
  .hero .lead { margin-left: 0; }
  .hero-actions { justify-content: flex-start; }
  .hero-photo-card { justify-self: stretch; width: 100%; }
}

@media (max-width: 900px) {
  .container { padding-left: 18px; padding-right: 18px; }
  .hero {
    gap: 28px;
    padding-top: 86px;
  }
  .hero-text { text-align: left; }
  .hero .sub-catch,
  .hero .lead { margin-left: 0; margin-right: 0; }
  .hero-actions,
  .hero-trust { justify-content: flex-start; }
  .packages-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 680px) {
  .container { padding-left: 16px; padding-right: 16px; }
  .hero { padding-top: 78px; }
  .hero {
    width: min(100%, 356px);
    max-width: min(100%, 356px);
    margin-left: 0;
    margin-right: auto;
    min-width: 0;
  }
  .hero-text,
  .hero-actions,
  .hero-photo-card {
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }
  .hero h1 { font-size: clamp(39px, 12vw, 54px); }
  .hero-title-sub { font-size: clamp(21px, 7vw, 28px); }
  .hero .sub-catch,
  .hero .lead,
  .hero h1,
  .hero-title-sub {
    width: 100%;
    max-width: 100%;
    overflow-wrap: anywhere;
  }
  .hero-actions {
    display: grid;
    grid-template-columns: 1fr;
    width: 100%;
  }
  .hero-actions .btn {
    justify-content: center;
    width: 100%;
    min-width: 0;
    padding-left: 18px;
    padding-right: 18px;
    white-space: normal;
  }
  .hero-proof-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .hero-photo-card {
    max-width: 100%;
    aspect-ratio: 4 / 3.35;
  }
  .hero-lesson-board {
    left: 14px;
    right: 14px;
    top: 14px;
    width: auto;
    max-width: calc(100% - 28px);
    padding: 13px;
  }
  .lesson-board-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
  }
  .lesson-board-item {
    min-height: 60px;
    padding: 7px 4px;
  }
  .lesson-board-item svg { width: 19px; height: 19px; }
  .lesson-board-item span { font-size: 9.5px; }
  .hero-class-caption {
    left: 14px;
    right: 14px;
    bottom: 14px;
    max-width: none;
  }
  .packages-grid { grid-template-columns: 1fr; }
  .sticky-cta {
    left: 16px;
    right: auto;
    width: min(100%, 356px);
    max-width: calc(100% - 32px);
  }
  .sticky-cta-btn {
    min-width: 0;
    white-space: normal;
    text-align: center;
  }
}

@media (max-width: 520px) {
  .hero {
    width: min(100%, 356px);
    max-width: min(100%, 356px);
    margin-left: 0;
    margin-right: auto;
  }
  .hero-text,
  .hero .sub-catch,
  .hero .lead,
  .hero-actions,
  .hero-proof-grid,
  .hero-photo-card {
    width: 100%;
    max-width: 100%;
  }
}
"""

PORTAL_CSS += """

/* ---- Bento glass morphing redesign: light-only, generated-photo led ---- */
:root,
:root[data-theme="dark"] {
  color-scheme: light;
  --bg-base: #F5FBFF;
  --bg-white: rgba(255,255,255,.76);
  --bg-elev: rgba(255,255,255,.64);
  --text: #07172C;
  --text-soft: #314763;
  --muted: #6E7F92;
  --line: rgba(7,23,44,.14);
  --line-strong: rgba(0,136,171,.32);
  --primary: #008CAC;
  --primary-soft: #00B8D4;
  --emerald: #8AAE18;
  --coral: #FF6D4F;
  --violet: #725CFF;
  --primary-bg: rgba(0,184,212,.12);
  --grad: linear-gradient(135deg, #008CAC 0%, #00B8D4 44%, #8AAE18 100%);
  --grad-soft: linear-gradient(135deg, rgba(0,184,212,.16), rgba(114,92,255,.10), rgba(255,109,79,.10));
  --glass-bg: rgba(255,255,255,.55);
  --glass-hi: rgba(255,255,255,.82);
  --glass-border: rgba(255,255,255,.68);
  --shadow-card: 0 1px 0 rgba(255,255,255,.70) inset, 0 18px 50px rgba(16,55,84,.11);
  --shadow-card-hover: 0 1px 0 rgba(255,255,255,.80) inset, 0 26px 70px rgba(0,140,172,.18);
}

html,
body {
  background:
    linear-gradient(112deg, rgba(0,184,212,.20) 0 12%, transparent 12% 58%, rgba(255,109,79,.11) 58% 70%, transparent 70%),
    linear-gradient(24deg, rgba(114,92,255,.10) 0 18%, transparent 18% 54%, rgba(138,174,24,.13) 54% 66%, transparent 66%),
    linear-gradient(180deg, #FFFFFF 0%, #F4FBFF 45%, #EBFAF7 100%);
}

body {
  color: var(--text);
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background:
    linear-gradient(rgba(0,140,172,.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,140,172,.06) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,.80), rgba(0,0,0,.18) 78%, transparent);
}

.theme-toggle,
.theme-toggle-mobile {
  display: none !important;
}

.container,
.site-header-inner {
  max-width: 1360px;
}

.site-header {
  background: rgba(255,255,255,.62);
  border-bottom: 1px solid rgba(255,255,255,.64);
  box-shadow: 0 10px 34px rgba(16,55,84,.07);
  backdrop-filter: blur(22px) saturate(170%);
  -webkit-backdrop-filter: blur(22px) saturate(170%);
}

.site-header.scrolled,
.site-header:hover {
  background: rgba(255,255,255,.76);
  border-bottom-color: rgba(0,140,172,.16);
}

.brand-mark,
.nav-cta,
.menu-toggle,
.mobile-toggle {
  border-radius: 8px;
  background: rgba(255,255,255,.70);
  border: 1px solid rgba(255,255,255,.78);
  box-shadow: 0 1px 0 rgba(255,255,255,.8) inset, 0 12px 30px rgba(0,140,172,.12);
  backdrop-filter: blur(14px) saturate(150%);
  -webkit-backdrop-filter: blur(14px) saturate(150%);
}

.nav-cta {
  background: linear-gradient(135deg, rgba(0,140,172,.96), rgba(139,174,24,.92));
  color: #fff;
}

.hero {
  min-height: min(840px, calc(100svh - 10px));
  grid-template-columns: minmax(430px, .88fr) minmax(560px, 1.12fr);
  gap: 62px;
  padding: 108px 0 64px;
  perspective: 1400px;
}

.hero::before {
  background:
    linear-gradient(122deg, rgba(255,255,255,.90) 0 34%, rgba(226,250,255,.66) 34% 54%, rgba(255,255,255,.82) 54%),
    linear-gradient(24deg, rgba(114,92,255,.10), transparent 46%, rgba(255,109,79,.10));
  border-bottom: 1px solid rgba(0,140,172,.16);
}

.hero::after {
  content: "";
  position: absolute;
  inset: 104px calc(50% - 50vw) 48px;
  z-index: -1;
  pointer-events: none;
  background:
    linear-gradient(90deg, transparent 0 49%, rgba(0,140,172,.12) 49% 50%, transparent 50%),
    linear-gradient(0deg, transparent 0 49%, rgba(114,92,255,.10) 49% 50%, transparent 50%);
  background-size: 168px 168px;
  opacity: .46;
  transform: skewY(-3deg);
}

.hero .eyebrow {
  display: none;
}

.hero h1 {
  margin: 0 0 22px;
  font-size: clamp(52px, 6.9vw, 98px);
  line-height: .94;
  letter-spacing: 0;
}

.fusion-logo-large {
  display: grid;
  gap: 0;
}

.fusion-logo-large .ai,
.fusion-logo-large .hub {
  color: var(--text);
  text-shadow: 0 12px 34px rgba(0,140,172,.16);
}

.hero-title-sub {
  margin-top: 22px;
  padding: 0;
  font-size: clamp(25px, 3.1vw, 43px);
  line-height: 1.12;
}

.hero-title-sub strong {
  color: transparent;
  background: linear-gradient(95deg, #008CAC 0%, #00B8D4 36%, #725CFF 70%, #FF6D4F 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.hero .sub-catch {
  max-width: 690px;
  margin-bottom: 16px;
  color: #007A94;
  font-size: clamp(17px, 1.8vw, 22px);
  line-height: 1.58;
}

.hero .lead {
  max-width: 660px;
  font-size: 16px;
  line-height: 2;
}

.hero-actions {
  gap: 12px;
}

.hero-actions .btn,
.pkg-cta,
.contact-primary,
.footer-cta {
  border-radius: 8px;
}

.hero-actions .btn-primary,
.contact-primary {
  background: linear-gradient(135deg, #008CAC, #00B8D4 48%, #8AAE18);
  box-shadow: 0 16px 40px rgba(0,140,172,.25), 0 1px 0 rgba(255,255,255,.42) inset;
}

.hero-actions .btn-secondary {
  background: rgba(255,255,255,.54);
  border: 1px solid rgba(255,255,255,.86);
  box-shadow: 0 12px 32px rgba(16,55,84,.09), 0 1px 0 rgba(255,255,255,.76) inset;
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
}

.hero-proof-grid {
  max-width: 720px;
  margin-top: 30px;
  padding: 10px;
  gap: 10px;
  border: 1px solid rgba(255,255,255,.70);
  border-radius: 8px;
  background: rgba(255,255,255,.42);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
}

.hero-proof {
  min-height: 92px;
  padding: 14px;
  border: 1px solid rgba(0,140,172,.14);
  border-radius: 8px;
  background:
    linear-gradient(145deg, rgba(255,255,255,.70), rgba(255,255,255,.34)),
    linear-gradient(135deg, rgba(0,184,212,.10), rgba(114,92,255,.06));
  box-shadow: 0 1px 0 rgba(255,255,255,.72) inset;
}

.hero-proof .proof-icon {
  border-radius: 8px;
  background: linear-gradient(135deg, #008CAC, #00B8D4);
}

.hero-photo-card {
  width: min(100%, 760px);
  aspect-ratio: 16 / 10.7;
  border: 1px solid rgba(255,255,255,.78);
  border-radius: 8px;
  background: rgba(255,255,255,.36);
  box-shadow: 0 34px 90px rgba(16,55,84,.18), 0 1px 0 rgba(255,255,255,.82) inset;
  overflow: visible;
  transform: rotateY(-8deg) rotateX(3deg) translateZ(0);
  transform-origin: center;
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
}

.hero-photo-card img {
  border-radius: 8px;
  transform: translate(12px, -10px);
  width: calc(100% - 6px);
  height: calc(100% - 6px);
  object-fit: cover;
  object-position: center;
  box-shadow: 0 24px 60px rgba(0,140,172,.16);
}

.hero-photo-card::after {
  inset: -1px;
  border-radius: 8px;
  background:
    linear-gradient(126deg, rgba(255,255,255,.42) 0 18%, transparent 18% 58%, rgba(255,255,255,.26) 58% 72%, transparent 72%),
    linear-gradient(180deg, rgba(255,255,255,0) 50%, rgba(7,23,44,.18));
}

.hero-lesson-board,
.hero-class-caption {
  border: 1px solid rgba(255,255,255,.78);
  border-radius: 8px;
  background: rgba(255,255,255,.58);
  box-shadow: 0 18px 52px rgba(16,55,84,.16), 0 1px 0 rgba(255,255,255,.78) inset;
  backdrop-filter: blur(22px) saturate(180%);
  -webkit-backdrop-filter: blur(22px) saturate(180%);
}

.hero-lesson-board {
  right: 20px;
  top: 22px;
  width: min(42%, 310px);
  padding: 16px;
}

.lesson-board-title {
  font-size: 17px;
  letter-spacing: 0;
}

.lesson-board-list {
  gap: 8px;
}

.lesson-board-item {
  min-height: 82px;
  border-color: rgba(0,184,212,.22);
  background: linear-gradient(145deg, rgba(255,255,255,.64), rgba(239,252,255,.42));
  box-shadow: 0 1px 0 rgba(255,255,255,.78) inset;
}

.lesson-board-item:nth-child(2) {
  background: linear-gradient(145deg, rgba(255,255,255,.66), rgba(246,255,218,.48));
}

.lesson-board-item:nth-child(3) {
  background: linear-gradient(145deg, rgba(255,255,255,.66), rgba(246,236,255,.48));
}

.lesson-board-item:nth-child(4) {
  background: linear-gradient(145deg, rgba(255,255,255,.66), rgba(255,239,233,.50));
}

.hero-class-caption {
  left: 24px;
  bottom: 24px;
  max-width: 370px;
}

section.block {
  padding: 82px 0;
}

.section-heading {
  display: inline-flex;
  padding: 6px 10px;
  border: 1px solid rgba(255,255,255,.70);
  border-radius: 8px;
  background: rgba(255,255,255,.52);
  box-shadow: 0 1px 0 rgba(255,255,255,.72) inset;
  backdrop-filter: blur(14px) saturate(150%);
  -webkit-backdrop-filter: blur(14px) saturate(150%);
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.pkg-card {
  grid-column: auto;
  min-height: 100%;
  border: 1px solid rgba(255,255,255,.70);
  background: rgba(255,255,255,.55) !important;
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(18px) saturate(155%);
  -webkit-backdrop-filter: blur(18px) saturate(155%);
}

.pkg-wide {
  grid-column: 1 / -1;
}

.pkg-card::before {
  background:
    linear-gradient(90deg, rgba(0,184,212,.16), transparent 38%, rgba(114,92,255,.10) 62%, rgba(255,109,79,.12));
}

.pkg-content-box,
.pkg-req-box,
.packages-note,
.usecase-card,
.lecture-card,
.growth-panel,
.profile-block,
.flow-step,
.faq-item,
.voice-card,
.biz-card,
.service-card {
  border: 1px solid rgba(255,255,255,.66);
  border-radius: 8px;
  background: rgba(255,255,255,.52);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(18px) saturate(155%);
  -webkit-backdrop-filter: blur(18px) saturate(155%);
}

.usecase-grid,
.lecture-grid,
.voices-grid,
.flow-list {
  gap: 18px;
}

.usecase-card {
  text-align: left;
  min-height: 238px;
}

.usecase-label {
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(255,255,255,.72), rgba(226,250,255,.55));
  box-shadow: 0 1px 0 rgba(255,255,255,.80) inset;
}

.lecture-card {
  border-top: 0;
}

.lecture-card::before,
.usecase-card::before,
.flow-step::before {
  content: "";
  display: block;
  width: 54px;
  height: 4px;
  margin-bottom: 16px;
  border-radius: 8px;
  background: linear-gradient(90deg, #00B8D4, #8AAE18, #FF6D4F);
}

.sticky-cta {
  border: 1px solid rgba(255,255,255,.78);
  border-radius: 8px;
  background: rgba(255,255,255,.58);
  box-shadow: 0 18px 54px rgba(16,55,84,.18), 0 1px 0 rgba(255,255,255,.82) inset;
}

.sticky-cta-btn {
  border-radius: 8px;
  background: linear-gradient(135deg, #008CAC, #00B8D4 48%, #8AAE18);
}

@media (max-width: 1040px) {
  .hero {
    grid-template-columns: 1fr;
    perspective: none;
  }

  .hero-photo-card {
    transform: none;
    width: 100%;
  }
}

@media (max-width: 900px) {
  .packages-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pkg-card,
  .pkg-featured {
    grid-column: auto;
  }
}

@media (max-width: 680px) {
  .hero {
    width: calc(100vw - 32px);
    max-width: calc(100vw - 32px);
    overflow: hidden;
  }

  .hero h1 {
    font-size: clamp(40px, 11vw, 50px);
  }

  .hero-title-sub {
    display: block;
    font-size: clamp(22px, 6.2vw, 27px);
    line-height: 1.2;
  }

  .hero-title-sub strong,
  .hero .sub-catch strong,
  .hero .lead {
    display: block;
    max-width: 100%;
    overflow-wrap: anywhere;
    word-break: break-all;
  }

  .hero .sub-catch {
    font-size: 16px;
  }

  .hero .lead {
    font-size: 14.5px;
    line-height: 1.9;
  }

  .hero-photo-card {
    aspect-ratio: 4 / 3.6;
    overflow: hidden;
  }

  .hero-photo-card img {
    transform: none;
    width: 100%;
    height: 100%;
  }

  .hero-lesson-board {
    width: auto;
  }

  .packages-grid {
    grid-template-columns: 1fr;
  }
}
"""

PORTAL_CSS += """

/* ---- Agent-grown design pass: 2026-06-12 ---- */
:root,
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg-base: #090807;
  --bg-white: rgba(255,253,244,.09);
  --bg-elev: rgba(255,253,244,.12);
  --text: #F8F4E8;
  --text-soft: #D8D0BD;
  --muted: #9E9788;
  --line: rgba(248,244,232,.16);
  --line-strong: rgba(0,238,255,.42);
  --primary: #00E6FF;
  --primary-soft: #75F0FF;
  --emerald: #D7F75D;
  --coral: #FF6347;
  --violet: #C887FF;
  --primary-bg: rgba(0,230,255,.13);
  --grad: linear-gradient(118deg, #00E6FF 0%, #D7F75D 38%, #FF6347 68%, #C887FF 100%);
  --grad-soft: linear-gradient(118deg, rgba(0,230,255,.18), rgba(215,247,93,.12), rgba(255,99,71,.13), rgba(200,135,255,.12));
  --glass-bg: rgba(14,13,11,.74);
  --glass-hi: rgba(255,253,244,.12);
  --glass-border: rgba(248,244,232,.18);
  --shadow-card: 0 1px 0 rgba(255,253,244,.12) inset, 0 24px 72px rgba(0,0,0,.34);
  --shadow-card-hover: 0 1px 0 rgba(255,253,244,.18) inset, 0 34px 92px rgba(0,230,255,.16);
}

html,
body {
  background:
    repeating-linear-gradient(112deg, rgba(255,253,244,.045) 0 1px, transparent 1px 42px),
    linear-gradient(90deg, rgba(0,230,255,.12), transparent 32%, rgba(255,99,71,.10) 62%, transparent 100%),
    linear-gradient(180deg, #090807 0%, #13100D 44%, #0B0A09 100%);
}

body {
  color: var(--text);
}

body::before {
  background:
    linear-gradient(rgba(0,230,255,.065) 1px, transparent 1px),
    linear-gradient(90deg, rgba(248,244,232,.04) 1px, transparent 1px);
  background-size: 78px 78px, 78px 78px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,.72), rgba(0,0,0,.20) 70%, transparent);
}

.site-header,
.site-header.scrolled,
.site-header:hover {
  background: rgba(9,8,7,.76);
  border-bottom-color: rgba(248,244,232,.13);
  box-shadow: 0 12px 46px rgba(0,0,0,.36);
}

.site-logo,
.nav-link,
.menu-link,
.mobile-nav a {
  color: var(--text);
}

.brand-mark,
.menu-toggle,
.mobile-toggle,
.nav-cta {
  background: rgba(255,253,244,.10);
  border-color: rgba(248,244,232,.18);
  color: var(--text);
}

.nav-cta,
.login-btn-mobile {
  background: var(--grad);
  color: #080806;
  font-weight: 900;
}

.hero {
  min-height: min(860px, calc(100svh - 8px));
  grid-template-columns: minmax(0, .92fr) minmax(520px, 1.08fr);
  gap: 58px;
  padding: 116px 0 64px;
}

.hero::before {
  background:
    linear-gradient(112deg, rgba(9,8,7,.97) 0 45%, rgba(30,21,16,.90) 45% 61%, rgba(9,8,7,.90) 61% 100%),
    repeating-linear-gradient(90deg, rgba(255,253,244,.06) 0 1px, transparent 1px 118px);
  border-bottom: 1px solid rgba(248,244,232,.13);
}

.hero::after {
  inset: 88px calc(50% - 50vw) 34px;
  background:
    linear-gradient(90deg, transparent 0 49%, rgba(0,230,255,.22) 49% 50%, transparent 50%),
    linear-gradient(0deg, transparent 0 49%, rgba(215,247,93,.13) 49% 50%, transparent 50%),
    repeating-linear-gradient(145deg, transparent 0 22px, rgba(255,99,71,.09) 22px 23px, transparent 23px 46px);
  background-size: 190px 190px, 190px 190px, 190px 190px;
  opacity: .66;
  transform: skewY(-2deg);
}

.fusion-logo-large {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.fusion-logo-large .pipe {
  display: none;
}

.fusion-logo-large .ai {
  color: var(--text);
  font-size: clamp(58px, 8vw, 112px);
  line-height: .86;
}

.fusion-logo-large .hub {
  width: fit-content;
  padding: 4px 10px 5px;
  color: #090807;
  background: var(--emerald);
  font-family: var(--mono);
  font-size: clamp(15px, 1.4vw, 22px);
  line-height: 1.1;
  text-transform: uppercase;
}

.hero h1 {
  margin-bottom: 20px;
}

.hero-title-sub {
  max-width: 760px;
  color: var(--text);
  font-size: clamp(25px, 3.1vw, 45px);
  line-height: 1.14;
}

.hero-title-sub strong {
  background: var(--grad);
  -webkit-background-clip: text;
  background-clip: text;
}

.hero .sub-catch {
  color: var(--primary-soft);
  font-size: clamp(17px, 1.7vw, 22px);
  line-height: 1.68;
}

.hero .lead {
  color: var(--text-soft);
  font-size: 15.5px;
  line-height: 2.02;
}

.hero-actions .btn-primary,
.pkg-cta,
.contact-primary,
.sticky-cta-btn {
  background: var(--grad);
  color: #090807;
  border: 0;
  box-shadow: 0 18px 46px rgba(0,230,255,.18), 0 1px 0 rgba(255,253,244,.30) inset;
}

.hero-actions .btn-secondary,
.btn-secondary {
  color: var(--text);
  background: rgba(248,244,232,.09);
  border: 1px solid rgba(248,244,232,.20);
  box-shadow: var(--shadow-card);
}

.hero-proof-grid {
  background: rgba(9,8,7,.58);
  border: 1px solid rgba(248,244,232,.16);
  box-shadow: 0 1px 0 rgba(248,244,232,.10) inset, 0 18px 50px rgba(0,0,0,.28);
}

.hero-proof {
  background:
    linear-gradient(180deg, rgba(248,244,232,.12), rgba(248,244,232,.055)),
    repeating-linear-gradient(90deg, rgba(0,230,255,.09) 0 1px, transparent 1px 18px);
  border-color: rgba(248,244,232,.14);
}

.hero-proof .proof-icon {
  background: #F8F4E8;
  color: #090807;
  font-family: var(--mono);
}

.hero-proof b,
.hero-proof span {
  color: var(--text);
}

.hero-proof span span {
  color: var(--muted);
}

.hero-photo-card {
  width: min(100%, 790px);
  aspect-ratio: 16 / 10.4;
  padding: 8px;
  border: 1px solid rgba(248,244,232,.20);
  background: linear-gradient(135deg, rgba(248,244,232,.16), rgba(0,230,255,.08), rgba(255,99,71,.09));
  box-shadow: 0 38px 110px rgba(0,0,0,.48), 0 1px 0 rgba(248,244,232,.16) inset;
  transform: rotate(-1.4deg) translateZ(0);
  overflow: hidden;
}

.hero-photo-card img {
  width: 100%;
  height: 100%;
  transform: none;
  border-radius: 8px;
  object-fit: cover;
  object-position: center top;
  filter: saturate(1.08) contrast(1.02);
}

.hero-photo-card::after {
  inset: 8px;
  border-radius: 8px;
  background:
    linear-gradient(90deg, rgba(0,0,0,.10), transparent 34%, rgba(0,0,0,.20)),
    repeating-linear-gradient(0deg, rgba(255,253,244,.12) 0 1px, transparent 1px 39px);
}

.hero-lesson-board,
.hero-class-caption {
  color: var(--text);
  background: rgba(9,8,7,.72);
  border-color: rgba(248,244,232,.20);
  box-shadow: 0 18px 64px rgba(0,0,0,.40), 0 1px 0 rgba(248,244,232,.12) inset;
}

.lesson-board-title {
  color: var(--text);
  font-family: var(--mono);
}

.lesson-board-item {
  background: rgba(248,244,232,.09);
  border-color: rgba(248,244,232,.17);
}

.lesson-board-item svg {
  color: var(--primary-soft);
}

.lesson-board-item span,
.hero-class-caption b {
  color: var(--text);
}

.hero-class-caption span {
  color: var(--text-soft);
}

section.block {
  position: relative;
}

.section-heading {
  color: #090807;
  background: var(--emerald);
  border: 0;
  font-family: var(--mono);
  font-weight: 900;
}

.section-title {
  color: var(--text);
}

.section-sub {
  color: var(--text-soft);
}

.pkg-card,
.pkg-content-box,
.pkg-req-box,
.packages-note,
.lecture-card,
.growth-panel,
.profile-block,
.flow-step,
.faq-item,
.voice-card,
.biz-card,
.service-card,
.contact-choice,
.explore-card {
  color: var(--text);
  background:
    linear-gradient(180deg, rgba(248,244,232,.12), rgba(248,244,232,.07)) !important;
  border-color: rgba(248,244,232,.16) !important;
  box-shadow: var(--shadow-card);
}

.pkg-card::before {
  height: 5px;
  background: var(--grad);
}

.pkg-cat,
.pkg-content-title,
.pkg-req-title,
.growth-row strong,
.growth-action b,
.lecture-title {
  color: var(--primary-soft);
}

.pkg-title,
.pkg-price,
.flow-step h3,
.faq-item summary,
.profile-block h3 {
  color: var(--text);
}

.pkg-desc,
.pkg-fit li,
.pkg-content li,
.pkg-req li,
.pkg-verify,
.growth-row span,
.growth-row em,
.growth-action p,
.lecture-summary,
.faq-item p,
.voice-who {
  color: var(--text-soft);
}

.pkg-level,
.pkg-subsidy,
.voice-ba {
  color: #090807;
  background: var(--primary-soft);
  border: 0;
}

.pkg-card:nth-child(2n) .pkg-level,
.pkg-card:nth-child(2n) .pkg-subsidy,
.voice-ba {
  background: var(--emerald);
}

.growth-layout {
  align-items: stretch;
}

.growth-row,
.growth-action {
  border-top-color: rgba(248,244,232,.13);
}

.faq-item[open] {
  border-color: rgba(0,230,255,.34) !important;
}

.sticky-cta {
  color: var(--text);
  background: rgba(9,8,7,.78);
  border-color: rgba(248,244,232,.18);
}

@media (prefers-reduced-motion: no-preference) {
  .hero-photo-card {
    animation: agentPosterDrift 8s ease-in-out infinite alternate;
  }

  .lesson-board-item svg {
    animation: agentSignal 2.8s ease-in-out infinite;
  }

  .lesson-board-item:nth-child(2) svg { animation-delay: .35s; }
  .lesson-board-item:nth-child(3) svg { animation-delay: .70s; }
  .lesson-board-item:nth-child(4) svg { animation-delay: 1.05s; }
}

@keyframes agentPosterDrift {
  from { transform: rotate(-1.4deg) translateY(0); }
  to { transform: rotate(.6deg) translateY(-10px); }
}

@keyframes agentSignal {
  0%, 100% { transform: translateY(0); opacity: .72; }
  50% { transform: translateY(-3px); opacity: 1; }
}

@media (max-width: 1040px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .hero-photo-card {
    transform: none;
    width: 100%;
  }
}

@media (max-width: 680px) {
  .hero {
    width: calc(100vw - 32px);
    max-width: calc(100vw - 32px);
    padding-top: 94px;
  }

  .fusion-logo-large .ai {
    font-size: clamp(49px, 15vw, 66px);
  }

  .fusion-logo-large .hub {
    font-size: 13px;
  }

  .hero-title-sub {
    font-size: clamp(23px, 7.2vw, 31px);
  }

  .hero .sub-catch strong,
  .hero .lead {
    word-break: normal;
    overflow-wrap: anywhere;
  }

  .hero-photo-card {
    aspect-ratio: 4 / 3.7;
    padding: 5px;
  }

  .hero-photo-card::after {
    inset: 5px;
  }

  .hero-lesson-board {
    padding: 12px;
  }

  .hero-class-caption {
    max-height: 104px;
    overflow: hidden;
  }
}
"""

PORTAL_CSS += """

/* ---- Calm shared design guardrails: 2026-06-12 ----
   Public fixed menu and mobile menu must keep explicit background/text pairs.
   Keep the palette restrained: white, slate, teal, and one soft green accent. */
:root,
:root[data-theme="dark"] {
  color-scheme: light;
  --bg-base: #F7FAF8;
  --bg-white: #FFFFFF;
  --bg-elev: #FFFFFF;
  --text: #122033;
  --text-soft: #405166;
  --muted: #66758A;
  --line: rgba(18,32,51,.12);
  --line-strong: rgba(18,32,51,.22);
  --primary: #1F6E8C;
  --primary-soft: #2F8EAD;
  --emerald: #6FAF98;
  --coral: #B7791F;
  --violet: #61758F;
  --primary-bg: rgba(31,110,140,.08);
  --grad: linear-gradient(135deg, #1F6E8C 0%, #2F8EAD 58%, #6FAF98 100%);
  --grad-soft: linear-gradient(135deg, rgba(31,110,140,.10), rgba(111,175,152,.08));
  --glass-bg: rgba(255,255,255,.92);
  --glass-hi: rgba(255,255,255,.96);
  --glass-border: rgba(18,32,51,.12);
  --shadow-card: 0 1px 2px rgba(18,32,51,.04), 0 12px 30px rgba(18,32,51,.08);
  --shadow-card-hover: 0 8px 22px rgba(18,32,51,.10), 0 22px 54px rgba(31,110,140,.12);
}

html,
body {
  background:
    linear-gradient(115deg, rgba(111,175,152,.08) 0%, transparent 36%),
    linear-gradient(180deg, #FFFFFF 0%, #F8FBF9 50%, #F2F7F5 100%) !important;
}

body {
  color: var(--text) !important;
}

body::before {
  background:
    linear-gradient(90deg, rgba(18,32,51,.018) 1px, transparent 1px),
    linear-gradient(180deg, rgba(18,32,51,.014) 1px, transparent 1px) !important;
  background-size: 96px 96px !important;
  mask-image: linear-gradient(180deg, rgba(0,0,0,.18), transparent 56%) !important;
}

.site-header,
.site-header.scrolled,
.site-header:hover {
  background: rgba(255,255,255,.985) !important;
  border-bottom-color: rgba(18,32,51,.14) !important;
  box-shadow: 0 12px 34px rgba(18,32,51,.10), inset 0 1px 0 rgba(255,255,255,.94) !important;
}

.site-logo,
.nav-link,
.menu-link {
  color: var(--text) !important;
}

.brand-mark,
.menu-toggle,
.mobile-toggle {
  background: #FFFFFF !important;
  border-color: rgba(18,32,51,.16) !important;
  color: var(--text) !important;
}

.site-nav {
  background: rgba(255,255,255,.82) !important;
  border-color: rgba(18,32,51,.10) !important;
}

.site-nav a.nav-link,
.site-nav .menu-toggle {
  color: #26364D !important;
}

.site-nav a.nav-link:hover,
.site-nav .menu-toggle:hover,
.site-nav .menu-toggle[aria-expanded="true"] {
  background: #EAF6F8 !important;
  color: #0F5F78 !important;
  border-color: rgba(31,110,140,.22) !important;
}

.site-nav .menu-drop {
  background: #FFFFFF !important;
  color: #122033 !important;
  border-color: rgba(18,32,51,.16) !important;
  box-shadow: 0 18px 44px rgba(18,32,51,.16), inset 0 1px 0 rgba(255,255,255,.95) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.site-nav .menu-drop a,
.site-nav .menu-drop a.menu-drop-sep,
.site-nav .menu-drop a.admin-drop-link {
  color: #203045 !important;
}

.site-nav .menu-drop a:hover {
  background: #EAF6F8 !important;
  color: #0F5F78 !important;
}

.site-nav .nav-cta,
.login-btn-mobile {
  background: linear-gradient(135deg, #1F6E8C 0%, #2C8C78 100%) !important;
  color: #FFFFFF !important;
  font-weight: 900 !important;
}

.mobile-nav {
  background: #FFFFFF !important;
  color: #122033 !important;
  border-top: 1px solid rgba(18,32,51,.14) !important;
  box-shadow: 0 18px 34px rgba(18,32,51,.14) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.mobile-nav a,
.mobile-nav .mobile-admin-link {
  color: #122033 !important;
  border-bottom: 1px solid rgba(18,32,51,.10) !important;
}

.mobile-nav a:hover,
.mobile-nav a:focus-visible {
  color: #0F5F78 !important;
  background: #EAF6F8 !important;
}

.mobile-nav .mobile-nav-label {
  color: #66758A !important;
}

.mobile-toggle svg path {
  stroke: #122033 !important;
}

.hero {
  min-height: min(780px, calc(100svh - 12px)) !important;
  grid-template-columns: minmax(0, .94fr) minmax(480px, 1.06fr) !important;
  gap: 52px !important;
  padding: 110px 0 58px !important;
}

.hero::before {
  background:
    linear-gradient(90deg, #FFFFFF 0%, rgba(255,255,255,.97) 42%, rgba(242,248,246,.88) 100%) !important;
  border-bottom: 1px solid rgba(18,32,51,.08) !important;
}

.hero::after {
  display: none !important;
}

.fusion-logo-large {
  display: inline-flex !important;
  flex-direction: row !important;
  align-items: baseline !important;
  gap: .08em !important;
}

.fusion-logo-large .ai {
  color: var(--text) !important;
  font-size: clamp(52px, 7vw, 88px) !important;
  line-height: .94 !important;
}

.fusion-logo-large .hub {
  width: auto !important;
  padding: 0 !important;
  color: var(--primary) !important;
  background: transparent !important;
  font-family: var(--serif) !important;
  font-size: inherit !important;
  text-transform: none !important;
}

.hero-title-sub,
.hero .sub-catch,
.hero .lead,
.section-title {
  color: var(--text) !important;
}

.hero-title-sub strong,
.hero .sub-catch strong {
  color: var(--primary) !important;
  background: transparent !important;
  -webkit-text-fill-color: currentColor !important;
}

.hero .lead,
.section-sub,
.pkg-desc,
.lecture-summary,
.faq-item p,
.voice-who {
  color: var(--text-soft) !important;
}

.hero-actions .btn-primary,
.pkg-cta,
.contact-primary,
.sticky-cta-btn {
  background: linear-gradient(135deg, #1F6E8C 0%, #2C8C78 100%) !important;
  color: #FFFFFF !important;
  border: 0 !important;
  box-shadow: 0 14px 34px rgba(31,110,140,.20), inset 0 1px 0 rgba(255,255,255,.28) !important;
}

.hero-actions .btn-secondary,
.btn-secondary {
  color: var(--text) !important;
  background: #FFFFFF !important;
  border: 1px solid rgba(18,32,51,.14) !important;
}

.hero-proof-grid,
.hero-proof,
.pkg-card,
.pkg-content-box,
.pkg-req-box,
.packages-note,
.lecture-card,
.growth-panel,
.profile-block,
.flow-step,
.faq-item,
.voice-card,
.biz-card,
.service-card,
.contact-choice,
.explore-card {
  color: var(--text) !important;
  background: rgba(255,255,255,.94) !important;
  border-color: rgba(18,32,51,.12) !important;
  box-shadow: var(--shadow-card) !important;
}

.hero-proof .proof-icon,
.section-heading,
.pkg-level,
.pkg-subsidy,
.voice-ba {
  color: #0F172A !important;
  background: #EAF6F8 !important;
  border: 1px solid rgba(31,110,140,.14) !important;
}

.pkg-cat,
.pkg-content-title,
.pkg-req-title,
.growth-row strong,
.growth-action b,
.lecture-title {
  color: var(--primary) !important;
}

.hero-photo-card {
  transform: none !important;
  background: #FFFFFF !important;
  border: 1px solid rgba(18,32,51,.12) !important;
  box-shadow: 0 20px 58px rgba(18,32,51,.13), inset 0 1px 0 rgba(255,255,255,.96) !important;
}

.hero-photo-card img {
  filter: saturate(1) contrast(1) !important;
}

.hero-photo-card::after {
  display: none !important;
}

.hero-lesson-board,
.hero-class-caption,
.sticky-cta {
  color: var(--text) !important;
  background: rgba(255,255,255,.92) !important;
  border-color: rgba(18,32,51,.12) !important;
  box-shadow: var(--shadow-card) !important;
}

.lesson-board-title,
.lesson-board-item span,
.hero-class-caption b {
  color: var(--text) !important;
}

.lesson-board-item {
  background: #F7FAF8 !important;
  border-color: rgba(18,32,51,.10) !important;
}

.lesson-board-item svg {
  color: var(--primary) !important;
}

@media (max-width: 1040px) {
  .hero {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 680px) {
  .hero {
    width: calc(100vw - 32px) !important;
    max-width: calc(100vw - 32px) !important;
    padding-top: 88px !important;
  }

  .fusion-logo-large {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
  }

  .fusion-logo-large .ai {
    font-size: clamp(46px, 14vw, 62px) !important;
  }

  .fusion-logo-large .hub {
    font-size: clamp(28px, 9vw, 40px) !important;
  }
}

section.block.block-tight {
  padding-top: 38px !important;
}

.path-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.path-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 220px;
  padding: 22px;
  text-decoration: none;
  color: var(--text) !important;
  background: rgba(255,255,255,.96) !important;
  border: 1px solid rgba(18,32,51,.12) !important;
  border-radius: 14px;
  box-shadow: var(--shadow-card) !important;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}

.path-card:hover,
.path-card:focus-visible {
  transform: translateY(-3px);
  border-color: rgba(31,110,140,.28) !important;
  box-shadow: 0 20px 44px rgba(18,32,51,.12) !important;
  outline: none;
}

.path-kicker,
.path-meta {
  display: inline-flex;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  background: #EAF6F8;
  border: 1px solid rgba(31,110,140,.14);
  color: #0F172A;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
}

.path-card strong {
  font-size: 22px;
  line-height: 1.28;
}

.path-card p {
  margin: 0;
  color: var(--text-soft) !important;
  line-height: 1.8;
  flex: 1;
}

.path-cta {
  color: var(--primary) !important;
  font-weight: 800;
}

@media (max-width: 980px) {
  .path-grid {
    grid-template-columns: 1fr;
  }
}
"""

PORTAL_CSS += """

/* ---- Service atlas hero: image-led + interactive, 2026-06-14 ---- */
.hero.hero-atlas {
  isolation: isolate;
  overflow: hidden;
  min-height: min(760px, calc(100svh - 8px)) !important;
  grid-template-columns: minmax(0, .92fr) minmax(420px, .88fr) !important;
  gap: 44px !important;
  padding: 104px 0 46px !important;
}

.hero.hero-atlas::before {
  display: none !important;
}

.hero.hero-atlas::after {
  content: "";
  display: block !important;
  position: absolute;
  inset: 0 calc(50% - 50vw);
  z-index: -2;
  pointer-events: none;
  background:
    radial-gradient(circle at calc(var(--mx, .58) * 100%) calc(var(--my, .45) * 100%), rgba(0,184,212,.18), transparent 28rem),
    linear-gradient(90deg, rgba(255,255,255,.98) 0%, rgba(255,255,255,.92) 33%, rgba(255,255,255,.42) 63%, rgba(255,255,255,.10) 100%),
    linear-gradient(180deg, rgba(255,255,255,.72) 0%, rgba(247,250,248,.88) 100%);
}

.hero-bg-layer {
  position: absolute;
  inset: 0 calc(50% - 50vw);
  z-index: -3;
  overflow: hidden;
  background: #F8FBF8;
}

.hero-bg-layer img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center;
  filter: saturate(1.04) contrast(1.02);
  transform: scale(1.025) translate3d(calc((var(--mx, .58) - .5) * -18px), calc((var(--my, .45) - .5) * -12px), 0);
  transform-origin: center;
  transition: transform .18s ease-out;
}

.hero.hero-atlas .hero-text {
  position: relative;
  z-index: 2;
  max-width: 720px;
  padding: 18px 0 12px;
}

.hero.hero-atlas .fusion-logo-large .ai {
  font-size: 86px !important;
}

.hero.hero-atlas .fusion-logo-large .hub {
  color: #0F8F72 !important;
}

.hero.hero-atlas .hero-title-sub {
  max-width: 690px;
  text-wrap: balance;
}

.hero.hero-atlas .hero-title-sub strong {
  color: transparent !important;
  background: linear-gradient(105deg, #1F6E8C 0%, #0F8F72 42%, #B7791F 100%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
}

.hero.hero-atlas .lead {
  max-width: 660px;
  color: #334155 !important;
}

.hero.hero-atlas .hero-proof-grid {
  background: rgba(255,255,255,.64) !important;
  border: 1px solid rgba(255,255,255,.86) !important;
  box-shadow: 0 20px 54px rgba(18,32,51,.10), inset 0 1px 0 rgba(255,255,255,.9) !important;
  backdrop-filter: blur(18px) saturate(140%);
  -webkit-backdrop-filter: blur(18px) saturate(140%);
}

.hero.hero-atlas .hero-proof {
  background: rgba(255,255,255,.66) !important;
}

.hero-atlas-panel {
  position: relative;
  justify-self: stretch;
  align-self: stretch;
  width: min(100%, 620px) !important;
  min-height: 468px;
  aspect-ratio: auto !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  overflow: visible !important;
  transform: none !important;
  perspective: 1100px;
}

.atlas-pathlines {
  position: absolute;
  inset: 10% 3% 8% 4%;
  border-radius: 8px;
  pointer-events: none;
  opacity: .82;
  transform: rotateX(calc((var(--my, .45) - .5) * 7deg)) rotateY(calc((var(--mx, .58) - .5) * -9deg));
  transition: transform .18s ease-out;
}

.atlas-pathlines::before,
.atlas-pathlines::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background:
    linear-gradient(110deg, transparent 0 18%, rgba(31,110,140,.24) 18.4%, transparent 19.2% 37%, rgba(15,143,114,.20) 37.4%, transparent 38.2% 62%, rgba(183,121,31,.18) 62.4%, transparent 63.2%),
    linear-gradient(22deg, transparent 0 31%, rgba(31,110,140,.20) 31.4%, transparent 32.2% 54%, rgba(0,184,212,.18) 54.4%, transparent 55.2%),
    radial-gradient(circle at 40% 35%, rgba(31,110,140,.22) 0 2px, transparent 3px),
    radial-gradient(circle at 64% 24%, rgba(15,143,114,.22) 0 2px, transparent 3px),
    radial-gradient(circle at 71% 52%, rgba(0,184,212,.22) 0 2px, transparent 3px),
    radial-gradient(circle at 50% 68%, rgba(183,121,31,.20) 0 2px, transparent 3px),
    radial-gradient(circle at 83% 72%, rgba(31,110,140,.22) 0 2px, transparent 3px);
}

.atlas-pathlines::after {
  inset: 12% 8% 12% 10%;
  opacity: .56;
  filter: blur(.2px);
  animation: atlas-drift 8s linear infinite;
}

@keyframes atlas-drift {
  from { transform: translateX(-10px); }
  to { transform: translateX(10px); }
}

.atlas-node {
  position: absolute;
  left: var(--x);
  top: var(--y);
  z-index: 4;
  width: min(210px, 40vw);
  min-height: 70px;
  padding: 10px 12px 10px 11px;
  border: 1px solid rgba(255,255,255,.88);
  border-radius: 8px;
  background: rgba(255,255,255,.70);
  color: #122033;
  box-shadow: 0 18px 44px rgba(18,32,51,.12), inset 0 1px 0 rgba(255,255,255,.95);
  backdrop-filter: blur(18px) saturate(155%);
  -webkit-backdrop-filter: blur(18px) saturate(155%);
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 9px;
  align-items: center;
  text-align: left;
  cursor: pointer;
  transform: translate(-50%, -50%) translateZ(0);
  transition: transform .2s ease, background .2s ease, border-color .2s ease, box-shadow .2s ease;
}

.atlas-node:hover,
.atlas-node:focus-visible,
.atlas-node.is-active {
  transform: translate(-50%, -50%) translateY(-4px);
  background: rgba(255,255,255,.92);
  border-color: rgba(31,110,140,.34);
  box-shadow: 0 24px 58px rgba(18,32,51,.16), 0 0 0 4px rgba(31,110,140,.08);
  outline: none;
}

.atlas-dot {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  background: #0F8F72;
  box-shadow: 0 0 0 5px rgba(15,143,114,.13), 0 0 20px rgba(0,184,212,.45);
}

.atlas-node:nth-of-type(2) .atlas-dot { background: #1F6E8C; }
.atlas-node:nth-of-type(3) .atlas-dot { background: #00A5C8; }
.atlas-node:nth-of-type(4) .atlas-dot { background: #B7791F; }
.atlas-node:nth-of-type(5) .atlas-dot { background: #61758F; }

.atlas-node-copy {
  display: block;
  min-width: 0;
}

.atlas-node-copy b {
  display: block;
  font-size: 14px;
  line-height: 1.25;
}

.atlas-node-copy small {
  display: block;
  margin-top: 3px;
  color: #52647A;
  font-size: 11px;
  line-height: 1.3;
}

.atlas-live-card {
  position: absolute;
  left: 0;
  bottom: 18px;
  z-index: 5;
  width: min(360px, 78%);
  padding: 18px 18px 16px;
  border: 1px solid rgba(255,255,255,.86);
  border-radius: 8px;
  background: rgba(255,255,255,.78);
  color: #122033;
  box-shadow: 0 26px 64px rgba(18,32,51,.14), inset 0 1px 0 rgba(255,255,255,.92);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
}

.atlas-live-kicker {
  display: block;
  color: #1F6E8C;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.atlas-live-title {
  display: block;
  margin-top: 6px;
  font-size: 22px;
  line-height: 1.25;
}

.atlas-live-desc {
  margin: 8px 0 14px;
  color: #405166;
  font-size: 13.5px;
  line-height: 1.7;
}

.atlas-live-cta {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 9px 13px;
  border-radius: 8px;
  color: #FFFFFF;
  background: linear-gradient(135deg, #1F6E8C, #0F8F72);
  font-size: 13px;
  font-weight: 900;
  text-decoration: none;
  box-shadow: 0 12px 28px rgba(31,110,140,.20);
}

.block {
  position: relative;
}

.block::before {
  content: "";
  position: absolute;
  left: max(0px, calc(50% - 560px));
  right: max(0px, calc(50% - 560px));
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(31,110,140,.22), rgba(15,143,114,.18), transparent);
  pointer-events: none;
}

.path-card,
.pkg-card,
.lecture-card,
.pf-card,
.flow-step,
.faq-item {
  position: relative;
  overflow: hidden;
}

.path-card::after,
.pkg-card::after,
.lecture-card::after,
.pf-card::after,
.flow-step::after,
.faq-item::after {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, rgba(31,110,140,.42), rgba(0,184,212,.18), rgba(183,121,31,.20));
  opacity: .55;
  pointer-events: none;
}

@media (max-width: 1040px) {
  .hero.hero-atlas {
    min-height: auto !important;
    grid-template-columns: 1fr !important;
  }

  .hero.hero-atlas .fusion-logo-large .ai {
    font-size: 72px !important;
  }

  .hero-atlas-panel {
    justify-self: center;
    width: min(100%, 680px) !important;
    min-height: 440px;
  }
}

@media (max-width: 680px) {
  .hero.hero-atlas {
    width: calc(100vw - 32px) !important;
    max-width: calc(100vw - 32px) !important;
    padding-top: 78px !important;
    gap: 24px !important;
  }

  .hero.hero-atlas::after {
    background:
      linear-gradient(180deg, rgba(255,255,255,.96) 0%, rgba(255,255,255,.92) 45%, rgba(255,255,255,.72) 100%),
      radial-gradient(circle at 76% 28%, rgba(0,184,212,.16), transparent 18rem);
  }

  .hero-bg-layer img {
    object-position: 68% center;
    opacity: .72;
  }

  .hero.hero-atlas .fusion-logo-large .ai {
    font-size: 56px !important;
  }

  .hero.hero-atlas .fusion-logo-large .hub {
    font-size: 38px !important;
  }

  .hero.hero-atlas .hero-title-sub {
    font-size: 28px;
    line-height: 1.16;
  }

  .hero.hero-atlas .sub-catch {
    font-size: 18px;
    line-height: 1.55;
  }

  .hero.hero-atlas .lead {
    font-size: 14.5px;
    line-height: 1.8;
  }

  .hero.hero-atlas .hero-proof-grid {
    display: none !important;
  }

  .hero-atlas-panel {
    min-height: auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .atlas-pathlines {
    display: none;
  }

  .atlas-node,
  .atlas-live-card {
    position: relative;
    left: auto;
    top: auto;
    bottom: auto;
    width: 100%;
    transform: none;
  }

  .atlas-node:hover,
  .atlas-node:focus-visible,
  .atlas-node.is-active {
    transform: translateY(-2px);
  }

  .atlas-live-card {
    order: -1;
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-bg-layer img,
  .atlas-pathlines,
  .atlas-node {
    transition: none !important;
  }

  .atlas-pathlines::after {
    animation: none !important;
  }
}
"""

PORTAL_CSS += """

/* ---- Website production showroom: presentation-ready homepage offer ---- */
.web-showcase-block {
  padding-top: 62px;
}

.web-showcase {
  --show-accent: #00A5C8;
  --show-ink: #07162B;
  --show-muted: #40536F;
  --show-cyan: oklch(72% .18 210);
  --show-jade: oklch(67% .17 158);
  --show-coral: oklch(69% .19 31);
  --show-lime: oklch(78% .20 125);
  --show-ochre: oklch(72% .15 78);
  position: relative;
  isolation: isolate;
  overflow: hidden;
  margin-top: 28px;
  border: 1px solid rgba(18,32,51,.13);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.96), rgba(248,252,252,.88)),
    #FFFFFF;
  box-shadow: 0 26px 76px rgba(18,32,51,.11), inset 0 1px 0 rgba(255,255,255,.94);
}

.web-showcase::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -3;
  background: url("img/web-production-showroom-kinetic-20260614.png") center / cover no-repeat;
  opacity: .44;
  filter: saturate(1.14) contrast(1.03);
  transform: scale(1.035) translate3d(calc((var(--sx, .5) - .5) * -22px), calc((var(--sy, .45) - .5) * -14px), 0);
  transition: transform .2s ease-out, opacity .2s ease-out;
}

.web-showcase::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  background:
    radial-gradient(circle at calc(var(--sx, .54) * 100%) calc(var(--sy, .42) * 100%), color-mix(in srgb, var(--show-accent, #00A5C8) 30%, transparent), transparent 24rem),
    conic-gradient(from 140deg at 79% 21%, transparent 0 20%, color-mix(in srgb, var(--show-coral) 20%, transparent) 28%, transparent 39%, color-mix(in srgb, var(--show-cyan) 22%, transparent) 52%, transparent 66%),
    linear-gradient(90deg, rgba(255,255,255,.965) 0%, rgba(255,255,255,.64) 46%, rgba(255,255,255,.90) 100%),
    linear-gradient(180deg, rgba(255,255,255,.62), rgba(244,250,250,.88));
  background-size: 100% 100%, 140% 140%, 100% 100%, 100% 100%;
  background-position: center, calc(var(--sx, .5) * 9%) calc(var(--sy, .45) * 9%), center, center;
}

.web-showcase-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(230px, .42fr) minmax(0, 1fr);
  gap: 22px;
  padding: clamp(18px, 3vw, 34px);
}

.web-showcase-intro {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.web-showcase-badge {
  width: fit-content;
  padding: 8px 10px;
  border: 1px solid color-mix(in srgb, var(--show-cyan) 28%, rgba(18,32,51,.12));
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(255,255,255,.78), color-mix(in srgb, var(--show-cyan) 10%, rgba(255,255,255,.82)));
  color: #075C71;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
  box-shadow: 0 10px 26px color-mix(in srgb, var(--show-cyan) 13%, transparent);
}

.web-showcase-lead {
  margin: 0;
  color: #334155;
  font-size: 14px;
  line-height: 1.85;
}

.web-showcase-tabs {
  display: grid;
  gap: 9px;
}

.web-show-tab {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  align-items: center;
  gap: 9px;
  min-height: 58px;
  padding: 9px 10px;
  border: 1px solid rgba(18,32,51,.13);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(255,255,255,.86), rgba(255,255,255,.68)),
    color-mix(in srgb, var(--accent, #00A5C8) 5%, #FFFFFF);
  color: #122033;
  box-shadow: 0 10px 28px rgba(18,32,51,.06), inset 0 1px 0 rgba(255,255,255,.88);
  cursor: pointer;
  text-align: left;
  transition: transform .18s ease, border-color .18s ease, background .18s ease, box-shadow .18s ease;
}

.web-show-tab::before {
  content: "";
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 3px;
  border-radius: 0 999px 999px 0;
  background: linear-gradient(180deg, var(--accent, #00A5C8), color-mix(in srgb, var(--accent, #00A5C8) 38%, #FFFFFF));
  opacity: .18;
  transition: opacity .18s ease, transform .18s ease;
}

.web-show-tab::after {
  content: "";
  position: absolute;
  inset: -2px -46px;
  pointer-events: none;
  background: linear-gradient(110deg, transparent 0 34%, rgba(255,255,255,.78) 48%, transparent 62%);
  opacity: 0;
  transform: translateX(-48%);
}

.web-show-tab:hover,
.web-show-tab:focus-visible,
.web-show-tab.is-active {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--accent, #00A5C8) 50%, rgba(18,32,51,.08));
  background:
    linear-gradient(135deg, rgba(255,255,255,.96), color-mix(in srgb, var(--accent, #00A5C8) 7%, #FFFFFF));
  box-shadow: 0 16px 34px rgba(18,32,51,.10), 0 0 0 4px color-mix(in srgb, var(--accent, #00A5C8) 12%, transparent);
  outline: none;
}

.web-show-tab:hover::before,
.web-show-tab:focus-visible::before,
.web-show-tab.is-active::before {
  opacity: 1;
  transform: scaleY(1.2);
}

.web-tab-num {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--accent, #00A5C8) 16%, #FFFFFF);
  color: color-mix(in srgb, var(--accent, #00A5C8) 78%, #122033);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.76);
}

.web-tab-title {
  display: block;
  font-size: 13.5px;
  font-weight: 900;
  line-height: 1.3;
}

.web-tab-sub {
  display: block;
  margin-top: 2px;
  color: #617085;
  font-size: 11.5px;
  line-height: 1.3;
}

.web-stage {
  min-width: 0;
  display: grid;
  grid-template-rows: minmax(330px, auto) auto;
  gap: 14px;
}

.web-preview-board {
  position: relative;
  min-height: 330px;
  border: 1px solid rgba(18,32,51,.13);
  border-radius: 8px;
  background:
    radial-gradient(circle at 88% 16%, color-mix(in srgb, var(--show-accent, #00A5C8) 14%, transparent), transparent 16rem),
    rgba(255,255,255,.82);
  box-shadow:
    0 24px 64px rgba(18,32,51,.12),
    0 0 0 1px color-mix(in srgb, var(--show-accent, #00A5C8) 9%, transparent),
    inset 0 1px 0 rgba(255,255,255,.92);
  overflow: hidden;
}

.web-preview-board::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(18,32,51,.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(18,32,51,.025) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,.42), transparent 72%);
  pointer-events: none;
}

.web-preview-board::after {
  content: "";
  position: absolute;
  inset: -45%;
  z-index: 0;
  pointer-events: none;
  opacity: .30;
  background:
    conic-gradient(from 80deg at 50% 50%, transparent 0 12%, color-mix(in srgb, var(--show-accent, #00A5C8) 42%, transparent) 17%, transparent 25% 48%, color-mix(in srgb, var(--show-lime) 26%, transparent) 58%, transparent 68%),
    radial-gradient(circle, color-mix(in srgb, var(--show-coral) 16%, transparent), transparent 35%);
  mix-blend-mode: multiply;
}

.web-browser {
  position: absolute;
  inset: 24px;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(210px, .34fr);
  gap: 18px;
  padding: 52px 22px 20px;
  border: 1px solid rgba(18,32,51,.16);
  border-radius: 8px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--show-accent, #00A5C8) 14%, #FFFFFF) 0%, rgba(255,255,255,.965) 44%, #FFFFFF 100%);
  box-shadow: 0 18px 44px rgba(18,32,51,.10), 0 16px 46px color-mix(in srgb, var(--show-accent, #00A5C8) 8%, transparent);
}

.web-browser-bar {
  position: absolute;
  inset: 0 0 auto;
  height: 34px;
  border-bottom: 1px solid rgba(18,32,51,.11);
  background: rgba(255,255,255,.82);
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
}

.web-browser-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #E8654D;
}

.web-browser-dot:nth-child(2) { background: #D7B928; }
.web-browser-dot:nth-child(3) { background: #0F8F72; }

.web-preview-copy {
  align-self: center;
}

.web-preview-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 5px 9px;
  border-radius: 8px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--show-accent, #00A5C8) 17%, #FFFFFF), rgba(255,255,255,.82));
  color: color-mix(in srgb, var(--show-accent, #00A5C8) 76%, #123044);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.82);
}

.web-preview-title {
  margin: 14px 0 8px;
  color: var(--show-ink);
  font-size: clamp(26px, 4vw, 48px);
  line-height: 1.08;
  letter-spacing: 0;
}

.web-preview-desc {
  max-width: 610px;
  margin: 0;
  color: var(--show-muted);
  font-size: 15px;
  line-height: 1.85;
}

.web-preview-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 17px;
}

.web-preview-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 6px 9px;
  border-radius: 8px;
  border: 1px solid rgba(18,32,51,.10);
  background:
    linear-gradient(135deg, rgba(255,255,255,.90), color-mix(in srgb, var(--show-accent, #00A5C8) 5%, #FFFFFF));
  color: #1A2A42;
  font-size: 12px;
  font-weight: 850;
}

.web-mini-site {
  align-self: stretch;
  display: grid;
  gap: 10px;
}

.web-mini-panel {
  min-height: 78px;
  border: 1px solid rgba(18,32,51,.10);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(255,255,255,.84), rgba(255,255,255,.66));
  padding: 10px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.88);
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}

.web-mini-panel span {
  display: block;
  height: 7px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--show-accent, #00A5C8) 34%, #D8E4E8);
}

.web-mini-panel span + span {
  width: 72%;
  margin-top: 8px;
  opacity: .62;
}

.web-mini-panel strong {
  display: block;
  margin-top: 14px;
  color: #122033;
  font-size: 13px;
  line-height: 1.35;
}

.web-spec-card {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  align-content: start;
}

.web-spec-row {
  padding: 12px 13px;
  border: 1px solid rgba(18,32,51,.11);
  border-radius: 8px;
  background: rgba(255,255,255,.76);
  box-shadow: 0 10px 24px rgba(18,32,51,.06), inset 0 1px 0 rgba(255,255,255,.86);
}

.web-spec-row b {
  display: block;
  color: #122033;
  font-size: 12px;
  line-height: 1.35;
}

.web-spec-row span {
  display: block;
  margin-top: 4px;
  color: #52647A;
  font-size: 12px;
  line-height: 1.5;
}

.web-proof-rail {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.web-proof-step {
  min-height: 88px;
  padding: 13px;
  border: 1px solid rgba(18,32,51,.11);
  border-radius: 8px;
  background: rgba(255,255,255,.78);
  box-shadow: 0 10px 24px rgba(18,32,51,.06), inset 0 1px 0 rgba(255,255,255,.88);
}

.web-proof-step small {
  display: block;
  color: color-mix(in srgb, var(--show-accent, #00A5C8) 72%, #1F6E8C);
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .08em;
}

.web-proof-step b {
  display: block;
  margin-top: 5px;
  color: #122033;
  font-size: 13px;
  line-height: 1.35;
}

.web-proof-step span {
  display: block;
  margin-top: 5px;
  color: #52647A;
  font-size: 11.5px;
  line-height: 1.45;
}

.web-showcase-cta {
  margin-top: 16px;
  display: inline-flex;
  width: fit-content;
  align-items: center;
  min-height: 42px;
  padding: 10px 14px;
  border-radius: 8px;
  color: #fff;
  background: linear-gradient(135deg, color-mix(in srgb, var(--show-accent, #00A5C8) 74%, #0B1B33), #0F8F72);
  font-size: 13px;
  font-weight: 900;
  text-decoration: none;
  box-shadow: 0 14px 32px rgba(31,110,140,.20), 0 0 0 1px rgba(255,255,255,.18) inset;
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

.web-showcase-cta:hover,
.web-showcase-cta:focus-visible {
  transform: translateY(-2px);
  filter: saturate(1.08);
  box-shadow: 0 18px 40px color-mix(in srgb, var(--show-accent, #00A5C8) 24%, rgba(18,32,51,.14)), 0 0 0 1px rgba(255,255,255,.22) inset;
  outline: none;
}

.web-showcase.is-switching .web-browser {
  animation: web-panel-switch .42s cubic-bezier(.2, .8, .2, 1);
}

.web-showcase.is-switching .web-mini-panel {
  animation: web-mini-rise .46s cubic-bezier(.2, .8, .2, 1);
}

@keyframes web-panel-switch {
  0% { transform: translateY(0) scale(1); filter: saturate(1); }
  38% { transform: translateY(-6px) scale(.992); filter: saturate(1.18); }
  100% { transform: translateY(0) scale(1); filter: saturate(1); }
}

@keyframes web-mini-rise {
  0% { transform: translateY(8px); opacity: .72; }
  100% { transform: translateY(0); opacity: 1; }
}

@media (prefers-reduced-motion: no-preference) {
  .web-showcase::after {
    animation: web-color-field 12s ease-in-out infinite alternate;
  }

  .web-preview-board::after {
    animation: web-route-spin 18s linear infinite;
  }

  .web-show-tab.is-active::after {
    animation: web-tab-sweep 1.8s ease-in-out infinite;
  }
}

@keyframes web-color-field {
  from { transform: translate3d(-1.2%, -.6%, 0) scale(1); }
  to { transform: translate3d(1.2%, .6%, 0) scale(1.025); }
}

@keyframes web-route-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes web-tab-sweep {
  0% { opacity: 0; transform: translateX(-52%); }
  34% { opacity: .42; }
  72% { opacity: 0; transform: translateX(52%); }
  100% { opacity: 0; transform: translateX(52%); }
}

@media (max-width: 1060px) {
  .web-showcase-shell {
    grid-template-columns: 1fr;
  }

  .web-showcase-tabs {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .web-showcase-block {
    padding-top: 40px;
  }

  .web-showcase-shell {
    padding: 14px;
  }

  .web-showcase-tabs {
    grid-template-columns: 1fr;
  }

  .web-stage {
    grid-template-rows: auto auto;
  }

  .web-preview-board {
    min-height: 0;
  }

  .web-browser {
    position: relative;
    inset: auto;
    min-height: 0;
    grid-template-columns: 1fr;
    padding: 52px 16px 16px;
  }

  .web-mini-site {
    grid-template-columns: 1fr 1fr;
  }

  .web-proof-rail {
    grid-template-columns: 1fr 1fr;
  }

  .web-spec-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .web-mini-site,
  .web-proof-rail {
    grid-template-columns: 1fr;
  }
}
"""

PORTAL_CSS += """

/* ---- Bright growth campaign layer: Codex era + acquisition booster ---- */
:root {
  --bright-teal: #00B8D4;
  --bright-cyan: #21D4FD;
  --bright-lime: #9BE22D;
  --bright-yellow: #FFD84D;
  --bright-coral: #FF5D73;
  --bright-pink: #FF7AB6;
  --bright-ink: #07162B;
}

body {
  background:
    linear-gradient(115deg, rgba(33,212,253,.10) 0 14%, transparent 14% 34%, rgba(155,226,45,.10) 34% 48%, transparent 48% 67%, rgba(255,216,77,.10) 67% 76%, transparent 76%),
    linear-gradient(180deg, #FFFFFF 0%, #F8FEFF 30%, #FFFFFF 100%) !important;
}

.site-header {
  background: rgba(255,255,255,.86) !important;
  border-bottom-color: rgba(7,22,43,.10) !important;
}

.hero.hero-atlas {
  min-height: min(810px, calc(100svh - 8px)) !important;
}

.hero.hero-atlas::after {
  background:
    linear-gradient(116deg, rgba(33,212,253,.30) 48%, transparent 48.3% 55%, rgba(155,226,45,.28) 55.3% 66%, transparent 66.3% 72%, rgba(255,216,77,.30) 72.3% 82%, transparent 82.3%),
    linear-gradient(92deg, rgba(255,255,255,.995) 0%, rgba(255,255,255,.95) 31%, rgba(255,255,255,.72) 56%, rgba(255,255,255,.30) 100%),
    linear-gradient(180deg, rgba(255,255,255,.76) 0%, rgba(246,253,253,.88) 100%) !important;
}

.hero-bg-layer img {
  filter: saturate(1.24) contrast(1.04) brightness(1.08) !important;
}

.hero.hero-atlas .fusion-logo-large .ai {
  color: #07162B !important;
}

.hero.hero-atlas .fusion-logo-large .hub {
  color: #00A676 !important;
}

.hero.hero-atlas .hero-title-sub strong {
  background: linear-gradient(100deg, #07162B 0%, #00A5C8 32%, #7CC414 60%, #FF4F67 100%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
}

.hero.hero-atlas .sub-catch {
  color: #07162B !important;
}

.hero.hero-atlas .sub-catch strong {
  display: inline;
  background: linear-gradient(transparent 58%, rgba(255,216,77,.50) 58%);
}

.hero.hero-atlas .lead {
  color: #223044 !important;
}

.hero.hero-atlas .btn-primary {
  background: linear-gradient(135deg, #FF4F67 0%, #FF8A3D 56%, #FFD84D 100%) !important;
  color: #FFFFFF !important;
  box-shadow: 0 18px 44px rgba(255,79,103,.22), 0 0 0 1px rgba(255,255,255,.48) inset !important;
}

.hero.hero-atlas .btn-secondary {
  background: rgba(255,255,255,.88) !important;
  border-color: rgba(0,184,212,.36) !important;
  color: #075C71 !important;
  box-shadow: 0 14px 34px rgba(0,184,212,.12) !important;
}

.hero.hero-atlas .hero-proof-grid {
  background: rgba(255,255,255,.82) !important;
  border-color: rgba(255,255,255,.96) !important;
}

.hero.hero-atlas .hero-proof {
  background:
    linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,255,255,.72)),
    linear-gradient(120deg, rgba(33,212,253,.14), rgba(255,216,77,.14)) !important;
  border-color: rgba(7,22,43,.08) !important;
}

.hero-proof:nth-child(2) {
  background:
    linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,255,255,.72)),
    linear-gradient(120deg, rgba(155,226,45,.16), rgba(33,212,253,.12)) !important;
}

.hero-proof:nth-child(3) {
  background:
    linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,255,255,.72)),
    linear-gradient(120deg, rgba(255,93,115,.16), rgba(255,216,77,.16)) !important;
}

.atlas-node {
  background: rgba(255,255,255,.82) !important;
  border-color: rgba(255,255,255,.98) !important;
}

.atlas-node:hover,
.atlas-node:focus-visible,
.atlas-node.is-active {
  background: #FFFFFF !important;
  box-shadow: 0 26px 60px rgba(7,22,43,.16), 0 0 0 4px color-mix(in srgb, var(--node-accent, #00B8D4) 16%, transparent) !important;
}

.atlas-node:nth-of-type(1) { --node-accent: #00B8D4; }
.atlas-node:nth-of-type(2) { --node-accent: #9BE22D; }
.atlas-node:nth-of-type(3) { --node-accent: #FF5D73; }
.atlas-node:nth-of-type(4) { --node-accent: #FFD84D; }
.atlas-node:nth-of-type(5) { --node-accent: #21D4FD; }

.atlas-live-card {
  background:
    linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,255,255,.76)),
    linear-gradient(120deg, rgba(33,212,253,.18), rgba(255,216,77,.16), rgba(255,93,115,.12)) !important;
}

.boost-block {
  position: relative;
  padding: 34px 0 72px;
}

.boost-lab {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(7,22,43,.12);
  border-radius: 8px;
  background:
    linear-gradient(108deg, rgba(33,212,253,.28) 0 22%, transparent 22.3% 34%, rgba(155,226,45,.25) 34.3% 50%, transparent 50.3% 61%, rgba(255,216,77,.28) 61.3% 76%, transparent 76.3%),
    linear-gradient(180deg, rgba(255,255,255,.97), rgba(255,255,255,.90));
  box-shadow: 0 28px 72px rgba(7,22,43,.11), inset 0 1px 0 rgba(255,255,255,.92);
}

.boost-lab::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    repeating-linear-gradient(110deg, transparent 0 34px, rgba(7,22,43,.045) 34px 36px, transparent 36px 68px),
    radial-gradient(circle at 86% 18%, rgba(255,93,115,.18), transparent 18rem);
  opacity: .86;
}

.boost-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(260px, .42fr) minmax(0, 1fr);
  gap: clamp(18px, 3vw, 34px);
  padding: clamp(20px, 4vw, 42px);
}

.boost-copy {
  display: flex;
  flex-direction: column;
  gap: 18px;
  justify-content: center;
}

.boost-copy h2 {
  margin: 0;
  color: var(--bright-ink);
  font-size: clamp(32px, 5vw, 64px);
  line-height: 1.02;
  letter-spacing: 0;
}

.boost-copy h2 strong {
  color: transparent;
  background: linear-gradient(100deg, #00A5C8 0%, #00A676 36%, #FF4F67 72%, #FF8A3D 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.boost-copy p {
  margin: 0;
  max-width: 560px;
  color: #334155;
  font-size: 15.5px;
  line-height: 1.9;
}

.boost-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.boost-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(7,22,43,.13);
  background: rgba(255,255,255,.86);
  color: #07162B;
  font-size: 13px;
  font-weight: 900;
  text-decoration: none;
  box-shadow: 0 12px 28px rgba(7,22,43,.08);
}

.boost-action.primary {
  color: #FFFFFF;
  border-color: transparent;
  background: linear-gradient(135deg, #FF4F67, #FF8A3D);
}

.boost-stage {
  min-width: 0;
  display: grid;
  gap: 14px;
}

.boost-route-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.boost-route {
  position: relative;
  overflow: hidden;
  min-height: 134px;
  padding: 16px;
  border: 1px solid rgba(7,22,43,.11);
  border-radius: 8px;
  background: rgba(255,255,255,.82);
  box-shadow: 0 14px 34px rgba(7,22,43,.08), inset 0 1px 0 rgba(255,255,255,.9);
  color: #07162B;
  cursor: pointer;
  text-align: left;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.boost-route::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 5px;
  background: var(--route-color, #00B8D4);
}

.boost-route:hover,
.boost-route:focus-visible,
.boost-route.is-active {
  transform: translateY(-4px);
  border-color: color-mix(in srgb, var(--route-color, #00B8D4) 46%, rgba(7,22,43,.08));
  box-shadow: 0 22px 48px rgba(7,22,43,.13), 0 0 0 4px color-mix(in srgb, var(--route-color, #00B8D4) 14%, transparent);
  outline: none;
}

.boost-route b {
  display: block;
  margin-top: 8px;
  font-size: 16px;
  line-height: 1.35;
}

.boost-route span {
  display: block;
  margin-top: 7px;
  color: #52647A;
  font-size: 12.5px;
  line-height: 1.55;
}

.boost-route small {
  display: inline-flex;
  min-height: 26px;
  align-items: center;
  padding: 4px 8px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--route-color, #00B8D4) 13%, #FFFFFF);
  color: color-mix(in srgb, var(--route-color, #00B8D4) 78%, #07162B);
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 900;
}

.boost-output {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 170px;
  gap: 14px;
  padding: 18px;
  border: 1px solid rgba(7,22,43,.10);
  border-radius: 8px;
  background: rgba(255,255,255,.84);
  box-shadow: 0 14px 34px rgba(7,22,43,.08), inset 0 1px 0 rgba(255,255,255,.88);
}

.boost-output h3 {
  margin: 0;
  color: #07162B;
  font-size: clamp(21px, 2.8vw, 32px);
  line-height: 1.2;
}

.boost-output p {
  margin: 8px 0 0;
  color: #40536F;
  font-size: 14px;
  line-height: 1.75;
}

.boost-output ul {
  display: grid;
  gap: 7px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.boost-output li {
  display: flex;
  gap: 8px;
  color: #122033;
  font-size: 13px;
  line-height: 1.5;
}

.boost-output li::before {
  content: "";
  width: 9px;
  height: 9px;
  margin-top: 5px;
  flex: 0 0 auto;
  border-radius: 2px;
  background: var(--active-boost, #00B8D4);
  transform: rotate(45deg);
}

.boost-meter {
  align-self: stretch;
  display: grid;
  align-content: center;
  gap: 10px;
  min-height: 170px;
  padding: 14px;
  border-radius: 8px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--active-boost, #00B8D4) 22%, #FFFFFF), rgba(255,255,255,.78));
  border: 1px solid color-mix(in srgb, var(--active-boost, #00B8D4) 28%, rgba(7,22,43,.08));
}

.boost-meter b {
  color: #07162B;
  font-size: 32px;
  line-height: 1;
}

.boost-meter span {
  color: #334155;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.45;
}

@media (max-width: 980px) {
  .boost-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .boost-block { padding-top: 18px; }
  .boost-route-grid,
  .boost-output {
    grid-template-columns: 1fr;
  }
  .boost-meter {
    min-height: 0;
  }
}
"""


PORTAL_CSS += """

/* ---- Agent-voted Bento Growth Lab command layer ---- */
:root {
  --hub-ink: #071426;
  --hub-text: #122033;
  --hub-muted: #526174;
  --hub-line: rgba(7,20,38,.13);
  --hub-glass: rgba(255,255,255,.86);
  --hub-glass-strong: rgba(255,255,255,.95);
  --hub-cyan: #0EA5C6;
  --hub-teal: #11A37F;
  --hub-lime: #92C83E;
  --hub-coral: #F26655;
  --hub-amber: #D99A20;
  --hub-shadow: 0 18px 46px rgba(7,20,38,.10), inset 0 1px 0 rgba(255,255,255,.92);
}

html { scroll-padding-top: 76px; }
[id] { scroll-margin-top: 76px; }

body {
  background:
    linear-gradient(90deg, rgba(14,165,198,.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.03) 1px, transparent 1px),
    linear-gradient(120deg, rgba(14,165,198,.10), transparent 30%),
    linear-gradient(230deg, rgba(146,200,62,.10), transparent 36%),
    linear-gradient(180deg, #FFFFFF 0%, #F6FBFC 44%, #FFFFFF 100%) !important;
  background-size: 84px 84px, 84px 84px, auto, auto, auto !important;
}

.container {
  max-width: 1240px;
  padding-top: 78px !important;
}

.site-header,
.site-header.scrolled,
.site-header:hover {
  min-height: 62px !important;
  background: linear-gradient(135deg, rgba(255,255,255,.90), rgba(247,252,253,.82)) !important;
  border-bottom: 1px solid var(--hub-line) !important;
  box-shadow: 0 10px 34px rgba(7,20,38,.08), inset 0 1px 0 rgba(255,255,255,.92) !important;
  backdrop-filter: blur(20px) saturate(150%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
}

.site-header-inner {
  min-height: 62px !important;
  padding: 8px 20px !important;
  gap: 12px !important;
}

.site-logo {
  flex: 0 1 auto;
  min-width: 0;
}

.brand-mark {
  width: 40px !important;
  height: 34px !important;
}

.site-nav {
  flex: 1 1 auto;
  justify-content: flex-end;
  flex-wrap: nowrap !important;
  gap: 6px !important;
  padding: 3px !important;
  border-radius: 8px !important;
  border-color: rgba(7,20,38,.10) !important;
  background: rgba(255,255,255,.58) !important;
  backdrop-filter: blur(14px) saturate(140%);
  -webkit-backdrop-filter: blur(14px) saturate(140%);
}

.site-nav a.nav-link,
.site-nav .menu-toggle,
.site-nav .nav-admin {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  padding: 0 10px !important;
  border-radius: 8px !important;
  color: #223148 !important;
  font-size: 12.5px !important;
  font-weight: 850 !important;
  white-space: nowrap;
}

.site-nav a.nav-link[href="/lectures/2026-04-ai-kihon.html"] {
  color: #075E67 !important;
  background: rgba(14,165,198,.10) !important;
  border-color: rgba(14,165,198,.20) !important;
}

.site-nav .nav-cta {
  min-height: 38px;
  padding: 0 14px !important;
  border-radius: 8px !important;
  background: linear-gradient(135deg, var(--hub-coral), var(--hub-amber)) !important;
  box-shadow: 0 12px 28px rgba(242,102,85,.20), inset 0 1px 0 rgba(255,255,255,.28) !important;
  white-space: nowrap;
}

.site-nav .nav-admin {
  border-color: rgba(7,20,38,.12) !important;
  background: rgba(255,255,255,.72) !important;
  color: #075E67 !important;
  box-shadow: none !important;
}

.site-nav .menu-drop {
  max-height: calc(100vh - 78px);
  overflow-y: auto;
  min-width: 240px !important;
  background: rgba(255,255,255,.96) !important;
  border-color: rgba(7,20,38,.12) !important;
  box-shadow: 0 24px 62px rgba(7,20,38,.15), inset 0 1px 0 rgba(255,255,255,.96) !important;
}

.hero.hero-atlas {
  min-height: min(760px, calc(100svh - 62px)) !important;
  padding-top: clamp(28px, 5vw, 54px) !important;
}

.hero-route-bento {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 22px 0 0;
  max-width: 760px;
}

.hero-route-card {
  position: relative;
  overflow: hidden;
  min-height: 116px;
  padding: 14px;
  border-radius: 8px;
  border: 1px solid var(--hub-line);
  background: var(--hub-glass);
  color: var(--hub-text);
  text-decoration: none;
  box-shadow: var(--hub-shadow);
  backdrop-filter: blur(18px) saturate(145%);
  -webkit-backdrop-filter: blur(18px) saturate(145%);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}

.hero-route-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 5px;
  background: var(--route-accent, var(--hub-cyan));
}

.hero-route-card:hover,
.hero-route-card:focus-visible {
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--route-accent, var(--hub-cyan)) 46%, rgba(7,20,38,.12));
  box-shadow: 0 22px 54px rgba(7,20,38,.14), 0 0 0 4px color-mix(in srgb, var(--route-accent, var(--hub-cyan)) 14%, transparent);
  outline: none;
}

.hero-route-card small {
  display: inline-flex;
  min-height: 24px;
  align-items: center;
  padding: 3px 8px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--route-accent, var(--hub-cyan)) 12%, #FFFFFF);
  color: color-mix(in srgb, var(--route-accent, var(--hub-cyan)) 78%, #071426);
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 900;
}

.hero-route-card b {
  display: block;
  margin-top: 10px;
  color: var(--hub-ink);
  font-size: 15.5px;
  line-height: 1.35;
}

.hero-route-card span {
  display: block;
  margin-top: 6px;
  color: var(--hub-muted);
  font-size: 12px;
  line-height: 1.5;
}

.route-consult { --route-accent: var(--hub-coral); }
.route-plan { --route-accent: var(--hub-teal); }
.route-code { --route-accent: var(--hub-cyan); }
.route-material { --route-accent: var(--hub-lime); }

.pkg-card,
.lecture-card,
.blog-feature,
.blog-card,
.web-showcase,
.boost-lab,
.hero-proof,
.atlas-live-card {
  border-radius: 8px !important;
}

a:focus-visible,
button:focus-visible {
  outline: 3px solid rgba(14,165,198,.26) !important;
  outline-offset: 3px;
}

@media (max-width: 1120px) {
  .site-nav a.nav-link:not(.nav-essential) {
    display: none !important;
  }
}

@media (max-width: 900px) {
  .container {
    padding-top: 66px !important;
  }

  .site-header-inner {
    min-height: 60px !important;
    padding: 8px 14px !important;
  }

  .mobile-toggle {
    display: inline-flex;
    width: 42px;
    height: 42px;
    align-items: center;
    justify-content: center;
    border-radius: 8px !important;
    background: rgba(255,255,255,.88) !important;
  }

  .mobile-nav {
    max-height: calc(100dvh - 60px);
    overflow-y: auto;
    padding: 10px 16px 18px !important;
    background: rgba(255,255,255,.96) !important;
  }

  .mobile-nav a {
    min-height: 42px;
    padding: 10px 4px !important;
    font-size: 14px !important;
    font-weight: 750 !important;
  }

  .mobile-nav a[href="/lectures/2026-04-ai-kihon.html"] {
    color: #075E67 !important;
    font-weight: 900 !important;
  }

  .hero-route-bento {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin-left: auto;
    margin-right: auto;
  }
}

@media (max-width: 520px) {
  .wordmark {
    font-size: 15px !important;
  }

  .brand-mark {
    width: 36px !important;
    height: 32px !important;
  }

  .hero-route-bento {
    gap: 8px;
  }

  .hero-route-card {
    min-height: 112px;
    padding: 12px;
  }
}
"""


PORTAL_CSS += """

/* ---- Mobile hero/menu cleanup, 2026-06-20 ---- */
.hero.hero-atlas {
  overflow: visible !important;
}

.site-nav .menu-drop {
  min-width: 260px !important;
}

.site-nav .menu-drop-label {
  margin-top: 6px;
}

.site-nav .menu-drop-label:first-child {
  margin-top: 0;
}

.mobile-nav-panel {
  width: min(100%, 720px);
  margin: 0 auto;
  display: grid;
  gap: 10px;
}

.mobile-nav-primary,
.mobile-link-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.mobile-nav a,
.mobile-nav .mobile-admin-link,
.mobile-nav .login-btn-mobile,
.mobile-nav .mobile-main-link {
  min-height: 44px;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  padding: 9px 10px !important;
  border: 1px solid rgba(18,32,51,.12) !important;
  border-radius: 8px !important;
  background: rgba(255,255,255,.82) !important;
  color: #122033 !important;
  text-align: center;
  text-decoration: none;
  line-height: 1.35;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.86);
}

.mobile-nav .login-btn-mobile {
  margin: 0 !important;
  background: linear-gradient(135deg, #F26655, #D99A20) !important;
  color: #fff !important;
  border-color: transparent !important;
  font-weight: 900 !important;
}

.mobile-nav .mobile-main-link,
.mobile-nav a[href="/lectures/2026-04-ai-kihon.html"] {
  background: rgba(14,165,198,.10) !important;
  color: #075E67 !important;
  font-weight: 900 !important;
}

.mobile-nav .mobile-admin-link {
  grid-column: 1 / -1;
  background: rgba(7,20,38,.05) !important;
  color: #223148 !important;
}

.mobile-nav .mobile-nav-label {
  padding: 2px 2px 0 !important;
  color: #5D6C80 !important;
  line-height: 1.2;
}

@media (max-width: 900px) {
  .site-header-inner {
    width: 100%;
  }

  .site-logo {
    min-width: 0;
    max-width: calc(100% - 54px);
    overflow: hidden;
  }

  .wordmark {
    min-width: 0;
  }

  .mobile-toggle {
    flex: 0 0 42px;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-left: auto;
    border: 1px solid rgba(18,32,51,.20) !important;
    background: rgba(255,255,255,.96) !important;
    color: #122033 !important;
    box-shadow: 0 8px 18px rgba(18,32,51,.10);
  }

  .mobile-toggle svg {
    display: block;
  }

  .mobile-toggle svg path {
    stroke: #122033 !important;
  }

  .mobile-nav {
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    max-height: calc(100dvh - 60px);
    padding: 12px max(16px, env(safe-area-inset-left)) calc(18px + env(safe-area-inset-bottom)) max(16px, env(safe-area-inset-right)) !important;
    overflow-y: auto;
    overscroll-behavior: contain;
  }
}

@media (max-width: 680px) {
  .container {
    padding-left: 16px !important;
    padding-right: 16px !important;
  }

  .hero.hero-atlas {
    width: 100vw !important;
    max-width: 100vw !important;
    min-height: min(700px, calc(100svh - 24px)) !important;
    margin-left: calc(50% - 50vw) !important;
    margin-right: calc(50% - 50vw) !important;
    padding: clamp(28px, 8vw, 48px) max(18px, env(safe-area-inset-left)) 30px max(18px, env(safe-area-inset-right)) !important;
    align-content: center;
    gap: 18px !important;
  }

  .hero-bg-layer,
  .hero.hero-atlas::after {
    inset: 0 !important;
  }

  .hero-bg-layer img {
    object-position: 62% center !important;
    opacity: .88 !important;
    transform: scale(1.05) !important;
  }

  .hero.hero-atlas::after {
    background:
      linear-gradient(180deg, rgba(255,255,255,.94) 0%, rgba(255,255,255,.86) 44%, rgba(255,255,255,.66) 100%),
      linear-gradient(90deg, rgba(255,255,255,.98) 0%, rgba(255,255,255,.70) 58%, rgba(255,255,255,.20) 100%) !important;
  }

  .hero.hero-atlas .hero-text {
    max-width: 100%;
    padding: 0 !important;
    text-align: left !important;
  }

  .hero.hero-atlas .lead {
    max-width: 36em;
  }

  .hero-actions {
    width: 100%;
    display: grid !important;
    grid-template-columns: 1fr;
    gap: 10px !important;
    margin-top: 18px;
  }

  .hero-actions .btn {
    width: 100%;
    min-width: 0 !important;
    max-width: 100%;
    min-height: 48px;
    justify-content: center;
    padding: 11px 10px !important;
    white-space: normal;
    line-height: 1.35;
    font-size: 13.5px !important;
  }

  .hero-route-bento,
  .hero-atlas-panel,
  .hero.hero-atlas .hero-proof-grid {
    display: none !important;
  }

  section.block {
    padding: 48px 0 !important;
  }

  section.block.block-tight {
    padding-top: 34px !important;
  }

  .section-sub {
    margin-bottom: 28px !important;
  }
}

@media (max-width: 430px) {
  .hero-actions {
    grid-template-columns: 1fr;
  }

  .mobile-nav a,
  .mobile-nav .mobile-admin-link,
  .mobile-nav .login-btn-mobile,
  .mobile-nav .mobile-main-link {
    min-height: 42px;
    padding-left: 8px !important;
    padding-right: 8px !important;
    font-size: 13px !important;
  }
}
"""


PORTAL_CSS += """

/* ---- Decision-first header and path selector, 2026-06-21 ---- */
.site-header,
.site-header.scrolled,
.site-header:hover {
  background: linear-gradient(135deg, rgba(255,255,255,.97), rgba(244,251,253,.93)) !important;
  border-bottom-color: rgba(7,20,38,.18) !important;
  box-shadow: 0 14px 38px rgba(7,20,38,.12), inset 0 1px 0 rgba(255,255,255,.98) !important;
}

.site-nav {
  flex: 0 0 auto !important;
  margin-left: auto !important;
  background: rgba(255,255,255,.78) !important;
  border: 1px solid rgba(7,20,38,.13) !important;
}

.site-nav a.nav-link:hover,
.site-nav a.nav-link:focus-visible,
.site-nav .menu-toggle:hover,
.site-nav .menu-toggle:focus-visible {
  background: #071426 !important;
  color: #FFFFFF !important;
  border-color: #071426 !important;
  box-shadow: 0 12px 24px rgba(7,20,38,.14) !important;
}

.site-nav a.nav-link.nav-essential[href="#packages"] {
  background: rgba(7,20,38,.92) !important;
  color: #FFFFFF !important;
  border-color: rgba(7,20,38,.92) !important;
}

.site-nav a.nav-link.nav-essential[href="#lesson-bridge"] {
  background: rgba(230,0,18,.10) !important;
  color: #8C0010 !important;
  border-color: rgba(230,0,18,.24) !important;
}

.site-nav a.nav-link.nav-essential[href="#lectures"] {
  background: rgba(146,200,62,.14) !important;
  color: #35560F !important;
  border-color: rgba(146,200,62,.26) !important;
}

.mobile-nav.open {
  border-top: 1px solid rgba(7,20,38,.14);
  box-shadow: 0 22px 46px rgba(7,20,38,.16);
}

.path-grid {
  align-items: stretch;
}

.path-card {
  min-height: 248px !important;
  padding: 20px !important;
  border-color: rgba(7,20,38,.14) !important;
  box-shadow: 0 18px 42px rgba(7,20,38,.09), inset 0 1px 0 rgba(255,255,255,.94) !important;
}

.path-card:nth-child(1) { --path-accent: #F26655; }
.path-card:nth-child(2) { --path-accent: #0EA5C6; }
.path-card:nth-child(3) { --path-accent: #92C83E; }

.path-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 6px;
  background: var(--path-accent, #0EA5C6);
}

.path-card:hover,
.path-card:focus-visible {
  border-color: color-mix(in srgb, var(--path-accent, #0EA5C6) 44%, rgba(7,20,38,.14)) !important;
  box-shadow: 0 24px 58px rgba(7,20,38,.14), 0 0 0 4px color-mix(in srgb, var(--path-accent, #0EA5C6) 14%, transparent) !important;
}

.path-persona {
  display: inline-flex;
  width: fit-content;
  margin-top: -2px;
  color: #071426;
  font-size: 13px;
  font-weight: 900;
  line-height: 1.35;
}

.path-meta,
.path-proof {
  border-radius: 8px !important;
}

.path-meta {
  background: color-mix(in srgb, var(--path-accent, #0EA5C6) 12%, #FFFFFF) !important;
  border-color: color-mix(in srgb, var(--path-accent, #0EA5C6) 25%, rgba(7,20,38,.12)) !important;
  color: color-mix(in srgb, var(--path-accent, #0EA5C6) 70%, #071426) !important;
}

.path-proof {
  display: inline-flex;
  width: fit-content;
  padding: 5px 9px;
  background: rgba(7,20,38,.045);
  border: 1px solid rgba(7,20,38,.08);
  color: #405166;
  font-size: 11.5px;
  font-weight: 800;
}

.path-cta {
  margin-top: 2px;
}

.path-card:hover .path-cta,
.path-card:focus-visible .path-cta {
  color: color-mix(in srgb, var(--path-accent, #0EA5C6) 78%, #071426) !important;
}

.choice-lens {
  margin-top: 18px;
  display: grid;
  grid-template-columns: .78fr 1fr .92fr;
  gap: 0;
  overflow: hidden;
  border: 1px solid rgba(7,20,38,.13);
  border-radius: 8px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 18px 42px rgba(7,20,38,.08), inset 0 1px 0 rgba(255,255,255,.96);
}

.choice-lens-head,
.choice-lens-row {
  display: contents;
}

.choice-lens-head span,
.choice-lens-row > * {
  padding: 12px 14px;
  border-right: 1px solid rgba(7,20,38,.09);
  border-bottom: 1px solid rgba(7,20,38,.09);
}

.choice-lens-head span {
  background: #071426;
  color: #FFFFFF;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
}

.choice-lens-row:last-child > * {
  border-bottom: 0;
}

.choice-lens-head span:last-child,
.choice-lens-row > *:last-child {
  border-right: 0;
}

.choice-lens-state {
  color: #071426;
  font-size: 13.5px;
  font-weight: 900;
  line-height: 1.55;
}

.choice-lens-reco {
  display: flex;
  flex-direction: column;
  gap: 3px;
  color: #102033;
  font-size: 13px;
  font-weight: 850;
  line-height: 1.5;
}

.choice-lens-reco small {
  color: #0F5F78;
  font-family: var(--mono);
  font-size: 10.5px;
  font-weight: 900;
  letter-spacing: .06em;
}

.choice-lens-proof {
  color: #405166;
  font-size: 12.5px;
  line-height: 1.65;
}

@media (max-width: 760px) {
  .choice-lens {
    grid-template-columns: 1fr;
  }

  .choice-lens-head {
    display: none;
  }

  .choice-lens-row {
    display: grid;
    gap: 0;
    padding: 12px;
    border-bottom: 1px solid rgba(7,20,38,.09);
  }

  .choice-lens-row:last-child {
    border-bottom: 0;
  }

  .choice-lens-row > * {
    padding: 3px 0;
    border: 0;
  }

  .choice-lens-reco {
    margin-top: 4px;
  }
}

@media (max-width: 680px) {
  .path-card {
    min-height: 0 !important;
    padding: 18px !important;
  }

  .path-card strong {
    font-size: 20px !important;
  }

  .path-card p {
    line-height: 1.7 !important;
  }
}
"""


PORTAL_CSS += """

/* ---- Shared solid menu surfaces, 2026-06-24 ---- */
:root {
  --menu-surface: #FFFFFF;
  --menu-surface-soft: #F7FBFC;
  --menu-border: rgba(7,20,38,.18);
  --menu-text: #122033;
  --menu-muted: #536276;
  --menu-accent: #0EA5C6;
  --menu-strong: #071426;
  --menu-focus: #EAF6F8;
  --menu-shadow: 0 16px 42px rgba(7,20,38,.13), inset 0 1px 0 rgba(255,255,255,.96);
}

header.site-header,
.site-header,
.site-header.scrolled,
.site-header:hover {
  background: linear-gradient(135deg, var(--menu-surface) 0%, var(--menu-surface-soft) 100%) !important;
  border-bottom: 1px solid var(--menu-border) !important;
  box-shadow: var(--menu-shadow) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.site-nav,
nav.top-nav {
  background: var(--menu-surface) !important;
  border: 1px solid var(--menu-border) !important;
  box-shadow: 0 10px 26px rgba(7,20,38,.08), inset 0 1px 0 rgba(255,255,255,.96) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.site-nav a.nav-link,
nav.top-nav .nav-link,
.site-nav .menu-toggle,
.site-nav .nav-admin {
  background: #FFFFFF !important;
  color: var(--menu-text) !important;
  border: 1px solid rgba(7,20,38,.12) !important;
}

.site-nav a.nav-link:hover,
.site-nav a.nav-link:focus-visible,
nav.top-nav .nav-link:hover,
nav.top-nav .nav-link:focus-visible,
.site-nav .menu-toggle:hover,
.site-nav .menu-toggle:focus-visible,
.site-nav .menu-toggle[aria-expanded="true"],
.site-nav .nav-admin:hover,
.site-nav .nav-admin:focus-visible {
  background: var(--menu-focus) !important;
  color: #075E67 !important;
  border-color: rgba(14,165,198,.32) !important;
  box-shadow: none !important;
}

.site-nav a.nav-link.nav-essential[href="#packages"],
.site-nav a.nav-link.nav-essential[href="/#packages"],
nav.top-nav .nav-link.nav-essential[href="/#packages"] {
  background: var(--menu-strong) !important;
  color: #FFFFFF !important;
  border-color: var(--menu-strong) !important;
}

.site-nav a.nav-link.nav-essential[href="#lectures"],
.site-nav a.nav-link.nav-essential[href="/#lectures"],
nav.top-nav .nav-link.nav-essential[href="/#lectures"],
.site-nav a.nav-link.nav-essential[href="#lesson-bridge"],
.site-nav a.nav-link.nav-essential[href="/#lesson-bridge"],
nav.top-nav .nav-link.nav-essential[href="/#lesson-bridge"],
.site-nav a.nav-link[href="/lectures/2026-04-ai-kihon.html"],
nav.top-nav .nav-link[href="/lectures/2026-04-ai-kihon.html"] {
  background: rgba(14,165,198,.10) !important;
  color: #075E67 !important;
  border-color: rgba(14,165,198,.24) !important;
}

.site-nav a.nav-link.nav-essential[href="#lesson-bridge"],
.site-nav a.nav-link.nav-essential[href="/#lesson-bridge"],
nav.top-nav .nav-link.nav-essential[href="/#lesson-bridge"] {
  background: rgba(230,0,18,.10) !important;
  color: #8C0010 !important;
  border-color: rgba(230,0,18,.26) !important;
}

.site-nav .menu-drop {
  background: var(--menu-surface) !important;
  color: var(--menu-text) !important;
  border: 1px solid var(--menu-border) !important;
  box-shadow: 0 24px 62px rgba(7,20,38,.16), inset 0 1px 0 rgba(255,255,255,.98) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.site-nav .menu-drop-label,
.mobile-nav .mobile-nav-label {
  color: var(--menu-muted) !important;
}

.site-nav .menu-drop a {
  background: #FFFFFF !important;
  color: var(--menu-text) !important;
  border-radius: 8px !important;
}

.site-nav .menu-drop a:hover,
.site-nav .menu-drop a:focus-visible {
  background: var(--menu-focus) !important;
  color: #075E67 !important;
  outline: none !important;
}

.mobile-toggle,
.generated-mobile-toggle {
  background: #FFFFFF !important;
  color: var(--menu-text) !important;
  border: 1px solid var(--menu-border) !important;
  box-shadow: 0 10px 24px rgba(7,20,38,.12) !important;
}

.mobile-nav,
.generated-mobile-nav,
.mobile-nav.open {
  background: var(--menu-surface) !important;
  color: var(--menu-text) !important;
  border-top: 1px solid var(--menu-border) !important;
  box-shadow: 0 24px 52px rgba(7,20,38,.18) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.mobile-nav a,
.mobile-nav .mobile-admin-link,
.mobile-nav .login-btn-mobile,
.mobile-nav .mobile-main-link {
  background: #FFFFFF !important;
  color: var(--menu-text) !important;
  border: 1px solid rgba(7,20,38,.13) !important;
}

.mobile-nav a:hover,
.mobile-nav a:focus-visible {
  background: var(--menu-focus) !important;
  color: #075E67 !important;
  outline: none !important;
}

.mobile-nav .login-btn-mobile,
.site-nav .nav-cta,
.nav-cta {
  background: linear-gradient(135deg, #F26655, #D99A20) !important;
  color: #FFFFFF !important;
  border-color: transparent !important;
}

.mobile-nav .mobile-main-link,
.mobile-nav a[href="/lectures/2026-04-ai-kihon.html"] {
  background: rgba(14,165,198,.10) !important;
  color: #075E67 !important;
  border-color: rgba(14,165,198,.24) !important;
}

.mobile-nav .mobile-admin-link {
  background: #F7FBFC !important;
}
"""


PORTAL_CSS += """

/* ---- Mac glass bento refresh, 2026-06-24 ---- */
:root {
  --mac-ink: #071426;
  --mac-text: #122033;
  --mac-muted: #536276;
  --mac-line: rgba(7,20,38,.13);
  --mac-line-strong: rgba(7,20,38,.20);
  --mac-glass: rgba(255,255,255,.66);
  --mac-glass-strong: rgba(255,255,255,.88);
  --mac-cyan: #0EA5C6;
  --mac-teal: #11A37F;
  --mac-lime: #92C83E;
  --mac-coral: #F26655;
  --mac-amber: #D99A20;
  --mac-shadow: 0 18px 48px rgba(7,20,38,.10), inset 0 1px 0 rgba(255,255,255,.92);
}

body {
  background:
    linear-gradient(90deg, rgba(7,20,38,.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.025) 1px, transparent 1px),
    linear-gradient(120deg, rgba(14,165,198,.10), transparent 32%),
    linear-gradient(240deg, rgba(242,102,85,.08), transparent 34%),
    linear-gradient(180deg, #FFFFFF 0%, #F5FBFC 46%, #FFFFFF 100%) !important;
  background-size: 92px 92px, 92px 92px, auto, auto, auto !important;
}

.fusion-logo-large {
  gap: 10px !important;
  align-items: baseline !important;
}

.hero.hero-atlas .fusion-logo-large .ai {
  color: var(--mac-ink) !important;
  text-shadow: 0 1px 0 rgba(255,255,255,.72);
}

.hero.hero-atlas .fusion-logo-large .hub {
  align-self: center;
  padding: 7px 12px;
  border: 1px solid rgba(7,20,38,.14);
  border-radius: 999px;
  background: rgba(255,255,255,.72) !important;
  color: #075E67 !important;
  font-size: clamp(15px, 1.5vw, 18px) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.9);
}

.hero-title-sub {
  max-width: 680px;
}

.hero-proof,
.atlas-live-card,
.hero-route-card,
.path-card,
.choice-lens,
.pkg-card,
.lecture-card,
.pf-card,
.biz-card,
.service-card,
.voice-card,
.faq-item,
.growth-panel,
.flow-step,
.contact-primary,
.blog-feature,
.blog-card,
.web-showcase {
  background: var(--mac-glass) !important;
  border: 1px solid rgba(255,255,255,.74) !important;
  box-shadow: var(--mac-shadow) !important;
  backdrop-filter: blur(18px) saturate(145%) !important;
  -webkit-backdrop-filter: blur(18px) saturate(145%) !important;
}

section.block {
  position: relative;
  padding: clamp(58px, 7vw, 92px) 0 !important;
  border-top: 0 !important;
  scroll-margin-top: 92px;
}

section.block + section.block {
  border-top: 0 !important;
}

section.block::before {
  content: "";
  position: absolute;
  z-index: 0;
  top: 18px;
  bottom: 18px;
  left: calc(50% - 50vw);
  width: 100vw;
  border-top: 1px solid rgba(7,20,38,.08);
  border-bottom: 1px solid rgba(7,20,38,.08);
  background:
    linear-gradient(120deg, color-mix(in srgb, var(--section-accent, var(--mac-cyan)) 10%, transparent), transparent 34%),
    linear-gradient(180deg, rgba(255,255,255,.56), rgba(255,255,255,.38));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.88), 0 24px 70px rgba(7,20,38,.045);
  backdrop-filter: blur(14px) saturate(130%);
  -webkit-backdrop-filter: blur(14px) saturate(130%);
}

section.block > * {
  position: relative;
  z-index: 1;
}

#start { --section-accent: var(--mac-coral); }
#packages { --section-accent: var(--mac-cyan); }
#web-showcase { --section-accent: var(--mac-amber); }
#flow { --section-accent: var(--mac-lime); }
#lectures { --section-accent: var(--mac-cyan); }
#speaker { --section-accent: var(--mac-coral); }
#voices { --section-accent: var(--mac-lime); }
#faq { --section-accent: var(--mac-teal); }
#growth { --section-accent: var(--mac-amber); }
#contact { --section-accent: var(--mac-coral); }

.section-heading {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 5px 11px;
  margin-left: 50% !important;
  transform: translateX(-50%);
  border: 1px solid color-mix(in srgb, var(--section-accent, var(--mac-cyan)) 26%, rgba(7,20,38,.10));
  border-radius: 999px;
  background: color-mix(in srgb, var(--section-accent, var(--mac-cyan)) 10%, rgba(255,255,255,.78));
  color: color-mix(in srgb, var(--section-accent, var(--mac-cyan)) 78%, #071426) !important;
  background-clip: border-box !important;
  -webkit-background-clip: border-box !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.86);
}

.section-title {
  max-width: 880px;
  margin-left: auto !important;
  margin-right: auto !important;
}

.section-title::after {
  content: "";
  display: block;
  width: 56px;
  height: 4px;
  margin: 16px auto 0;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--section-accent, var(--mac-cyan)), color-mix(in srgb, var(--section-accent, var(--mac-cyan)) 45%, #FFFFFF));
}

.section-sub {
  max-width: 760px !important;
  margin-bottom: clamp(28px, 4vw, 44px) !important;
}

.packages-grid,
.path-grid,
.lecture-grid,
.portfolio-grid,
.voices-grid,
.growth-layout,
.blog-list {
  gap: clamp(14px, 2vw, 22px) !important;
}

.hero-route-card,
.path-card,
.pkg-card,
.lecture-card,
.blog-card,
.voice-card,
.faq-item {
  border-radius: 14px !important;
}

.hero-route-card::before,
.path-card::before {
  height: 4px !important;
}

.pkg-card:hover,
.lecture-card:hover,
.blog-card:hover,
.hero-route-card:hover,
.path-card:hover,
.faq-item:hover {
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--section-accent, var(--mac-cyan)) 34%, rgba(7,20,38,.13)) !important;
  box-shadow: 0 24px 62px rgba(7,20,38,.13), inset 0 1px 0 rgba(255,255,255,.94) !important;
}

@media (max-width: 680px) {
  section.block {
    padding: 48px 0 !important;
  }

  section.block::before {
    top: 8px;
    bottom: 8px;
  }

  .hero.hero-atlas .fusion-logo-large {
    display: flex !important;
    flex-wrap: wrap;
    gap: 8px !important;
  }

  .hero.hero-atlas .fusion-logo-large .hub {
    font-size: 13px !important;
    padding: 5px 9px;
  }
}
"""


PORTAL_CSS += """

/* ---- Pop line-art refresh inspired by Sakana AI's airy homepage, 2026-06-25 ---- */
:root {
  --linepop-ink: #071426;
  --linepop-text: #122033;
  --linepop-muted: #536276;
  --linepop-line: rgba(7,20,38,.18);
  --linepop-cyan: #00A5C8;
  --linepop-lime: #A6D83F;
  --linepop-coral: #F26655;
  --linepop-yellow: #FFD84D;
  --linepop-shadow: 7px 7px 0 rgba(7,20,38,.045), 0 18px 42px rgba(7,20,38,.075);
}

body {
  color: var(--linepop-text) !important;
  background:
    radial-gradient(circle at 10% 18%, rgba(255,216,77,.18), transparent 20rem),
    radial-gradient(circle at 88% 9%, rgba(0,165,200,.14), transparent 22rem),
    radial-gradient(circle at 78% 82%, rgba(242,102,85,.12), transparent 24rem),
    linear-gradient(180deg, #FFFFFF 0%, #F9FDFF 46%, #FFFFFF 100%) !important;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: .42;
  background-image:
    url("data:image/svg+xml,%3Csvg width='460' height='260' viewBox='0 0 460 260' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23071426' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' opacity='.18'%3E%3Cpath d='M24 162c54-82 122-82 176 0s122 82 176 0'/%3E%3Cpath d='M56 96c34-38 74-38 108 0s74 38 108 0'/%3E%3Ccircle cx='92' cy='96' r='8'/%3E%3Ccircle cx='202' cy='162' r='9'/%3E%3Ccircle cx='334' cy='96' r='7'/%3E%3Cpath d='M390 138l28-12-8 28zM132 183l22-10-6 22z'/%3E%3C/g%3E%3C/svg%3E"),
    linear-gradient(90deg, rgba(7,20,38,.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.025) 1px, transparent 1px);
  background-size: 460px 260px, 104px 104px, 104px 104px;
  background-position: 8% 118px, 0 0, 0 0;
}

.site-header,
.container,
.sticky-cta {
  position: relative;
  z-index: 1;
}

header.site-header,
.site-header,
.site-header.scrolled,
.site-header:hover,
.site-nav,
nav.top-nav {
  background: rgba(255,255,255,.96) !important;
  border-color: var(--linepop-line) !important;
  box-shadow: 0 10px 30px rgba(7,20,38,.07) !important;
}

.hero.hero-atlas::after {
  background:
    linear-gradient(100deg, rgba(255,255,255,.98) 0%, rgba(255,255,255,.92) 58%, rgba(255,255,255,.52) 100%),
    radial-gradient(circle at calc(var(--mx, .72) * 100%) calc(var(--my, .36) * 100%), rgba(0,165,200,.16), transparent 20rem) !important;
}

.hero.hero-atlas .fusion-logo-large .hub,
.site-nav a.nav-link,
.site-nav .menu-toggle,
.site-nav .nav-admin,
.mobile-nav a {
  border-radius: 999px !important;
}

.hero.hero-atlas .hero-title-sub strong,
.boost-copy h2 strong {
  background: linear-gradient(100deg, var(--linepop-ink) 0%, var(--linepop-cyan) 34%, var(--linepop-lime) 66%, var(--linepop-coral) 100%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
}

section.block::before {
  border-top: 1.5px solid rgba(7,20,38,.11) !important;
  border-bottom: 1.5px solid rgba(7,20,38,.10) !important;
  background:
    url("data:image/svg+xml,%3Csvg width='420' height='180' viewBox='0 0 420 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%2300A5C8' stroke-width='2' stroke-linecap='round' opacity='.16'%3E%3Cpath d='M18 118c48-58 96-58 144 0s96 58 144 0 72-44 96-18'/%3E%3Cpath d='M72 62c28-22 56-22 84 0s56 22 84 0'/%3E%3C/g%3E%3C/svg%3E") right 12% top 18px / 420px 180px no-repeat,
    linear-gradient(180deg, rgba(255,255,255,.84), rgba(255,255,255,.62)) !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.section-heading {
  border-color: rgba(7,20,38,.18) !important;
  background: #FFFFFF !important;
  color: var(--linepop-ink) !important;
  box-shadow: 4px 4px 0 color-mix(in srgb, var(--section-accent, var(--linepop-cyan)) 28%, transparent) !important;
}

.section-title {
  color: var(--linepop-ink) !important;
}

.section-title::after {
  width: 74px !important;
  height: 5px !important;
  border-radius: 0 !important;
  background: linear-gradient(90deg, var(--linepop-cyan), var(--linepop-lime) 48%, var(--linepop-coral)) !important;
  box-shadow: 0 5px 0 rgba(255,216,77,.38);
}

.hero-proof,
.atlas-live-card,
.hero-route-card,
.path-card,
.choice-lens,
.pkg-card,
.lecture-card,
.pf-card,
.biz-card,
.service-card,
.voice-card,
.faq-item,
.growth-panel,
.flow-step,
.contact-primary,
.blog-feature,
.blog-card,
.web-showcase,
.boost-lab {
  background: rgba(255,255,255,.94) !important;
  border: 1.5px solid var(--linepop-line) !important;
  box-shadow: var(--linepop-shadow) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.pf-card,
.blog-card {
  border-radius: 12px !important;
}

.pf-card::after,
.blog-card::after,
.pkg-card::after,
.lecture-card::after,
.path-card::after {
  height: 4px !important;
  background: linear-gradient(90deg, var(--linepop-cyan), var(--linepop-lime), var(--linepop-yellow), var(--linepop-coral)) !important;
  opacity: .9 !important;
}

.pf-card .pf-thumb,
.blog-card-media {
  border-bottom: 1.5px solid rgba(7,20,38,.14);
}

.pf-card .pf-chip,
.blog-card-meta span {
  border-radius: 999px !important;
  background: #FFFFFF !important;
  border-color: rgba(7,20,38,.16) !important;
  color: var(--linepop-ink) !important;
}

.pf-arrow {
  background: #FFFFFF !important;
  border: 1.5px solid var(--linepop-line) !important;
  color: var(--linepop-ink) !important;
  box-shadow: 4px 4px 0 rgba(7,20,38,.08), 0 10px 24px rgba(7,20,38,.10) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.pf-arrow:hover {
  border-color: var(--linepop-cyan) !important;
  box-shadow: 4px 4px 0 rgba(0,165,200,.18), 0 14px 28px rgba(7,20,38,.12) !important;
}

@media (max-width: 760px) {
  body::before {
    opacity: .28;
    background-size: 360px 204px, 88px 88px, 88px 88px;
  }
}
"""


PORTAL_CSS += """

/* ---- AI data + lesson bridge, 2026-06-25 ---- */
:root {
  --lesson-red: #E60012;
  --lesson-blue: #0877C6;
  --lesson-green: #00A676;
  --lesson-amber: #F5B83D;
  --lesson-ink: #071426;
  --lesson-muted: #52647A;
}

#why-now { --section-accent: var(--lesson-blue); }
#lesson-bridge { --section-accent: var(--lesson-blue); }

.ai-impact-board,
.lesson-bridge-shell {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.74);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(255,255,255,.82), rgba(255,255,255,.50)),
    radial-gradient(circle at 12% 18%, rgba(8,119,198,.16), transparent 18rem),
    radial-gradient(circle at 86% 12%, rgba(0,166,118,.12), transparent 17rem),
    rgba(255,255,255,.56);
  box-shadow: 0 28px 78px rgba(7,20,38,.12), inset 0 1px 0 rgba(255,255,255,.92);
  backdrop-filter: blur(24px) saturate(155%);
  -webkit-backdrop-filter: blur(24px) saturate(155%);
}

.ai-impact-board::before,
.lesson-bridge-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: .45;
  background-image:
    linear-gradient(90deg, rgba(7,20,38,.045) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.035) 1px, transparent 1px);
  background-size: 44px 44px;
}

.ai-impact-shell,
.lesson-bridge-inner {
  position: relative;
  z-index: 1;
  padding: clamp(18px, 3vw, 32px);
}

.ai-impact-top {
  display: grid;
  grid-template-columns: minmax(0, .88fr) minmax(280px, 1fr);
  gap: 18px;
  align-items: stretch;
}

.ai-impact-copy {
  display: flex;
  min-height: 100%;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
  padding: 18px;
  border: 1px solid rgba(7,20,38,.10);
  border-radius: 8px;
  background: rgba(255,255,255,.72);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.88);
}

.ai-impact-kicker,
.lesson-bridge-kicker {
  width: fit-content;
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(7,20,38,.92);
  color: #fff;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .08em;
}

.ai-impact-copy h3,
.lesson-bridge-copy h3 {
  margin: 0;
  color: var(--lesson-ink);
  font-size: clamp(24px, 3.2vw, 38px);
  line-height: 1.16;
  letter-spacing: 0;
}

.ai-impact-copy p,
.lesson-bridge-copy p {
  margin: 0;
  color: #32455E;
  font-size: 14px;
  line-height: 1.85;
}

.ai-impact-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.ai-impact-card {
  min-height: 142px;
  padding: 14px;
  border: 1px solid rgba(255,255,255,.72);
  border-radius: 8px;
  background:
    linear-gradient(145deg, rgba(255,255,255,.78), rgba(255,255,255,.48)),
    color-mix(in srgb, var(--card-color, var(--lesson-blue)) 10%, transparent);
  box-shadow: 0 16px 38px rgba(7,20,38,.10), inset 0 1px 0 rgba(255,255,255,.86);
  backdrop-filter: blur(16px) saturate(150%);
  -webkit-backdrop-filter: blur(16px) saturate(150%);
}

.ai-impact-card b {
  display: block;
  color: color-mix(in srgb, var(--card-color, var(--lesson-blue)) 84%, #071426);
  font-family: var(--mono);
  font-size: clamp(28px, 4.8vw, 48px);
  line-height: 1;
}

.ai-impact-card span {
  display: block;
  margin-top: 10px;
  color: var(--lesson-ink);
  font-size: 13px;
  font-weight: 900;
  line-height: 1.35;
}

.ai-impact-card small {
  display: block;
  margin-top: 7px;
  color: var(--lesson-muted);
  font-size: 11.5px;
  line-height: 1.5;
}

.ai-benefit-table {
  margin-top: 18px;
  display: grid;
  border: 1px solid rgba(7,20,38,.11);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255,255,255,.72);
}

.ai-benefit-row {
  display: grid;
  grid-template-columns: .82fr 1.05fr 1fr .78fr;
}

.ai-benefit-row > * {
  padding: 12px 14px;
  border-right: 1px solid rgba(7,20,38,.09);
  border-bottom: 1px solid rgba(7,20,38,.09);
  color: #2E4058;
  font-size: 12.5px;
  line-height: 1.55;
}

.ai-benefit-row > *:last-child {
  border-right: 0;
}

.ai-benefit-row:last-child > * {
  border-bottom: 0;
}

.ai-benefit-head > * {
  background: rgba(7,20,38,.94);
  color: #fff;
  font-family: var(--mono);
  font-size: 10.5px;
  font-weight: 900;
  letter-spacing: .06em;
}

.ai-benefit-row strong {
  color: var(--lesson-ink);
  font-weight: 900;
}

.ai-source-note {
  margin-top: 12px;
  color: var(--lesson-muted);
  font-size: 11.5px;
  line-height: 1.7;
}

.ai-source-note a {
  color: #075C71;
  font-weight: 800;
}

.lesson-bridge-inner {
  display: grid;
  grid-template-columns: minmax(240px, .42fr) minmax(0, 1fr);
  gap: 20px;
}

.lesson-bridge-copy {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.lesson-track-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.lesson-track-card {
  position: relative;
  overflow: hidden;
  min-height: 250px;
  padding: 18px;
  border: 1px solid rgba(255,255,255,.70);
  border-radius: 8px;
  background:
    linear-gradient(145deg, rgba(255,255,255,.78), rgba(255,255,255,.48)),
    color-mix(in srgb, var(--track-color) 11%, transparent);
  box-shadow: 0 18px 44px rgba(7,20,38,.10), inset 0 1px 0 rgba(255,255,255,.88);
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
}

.lesson-track-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 6px;
  background: var(--track-color);
}

.lesson-track-card.material { --track-color: var(--lesson-green); }
.lesson-track-card.ai { --track-color: var(--lesson-blue); }

.lesson-track-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  padding: 5px 9px;
  border-radius: 999px;
  color: #fff;
  background: var(--track-color);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .06em;
}

.lesson-track-card h3 {
  margin: 16px 0 8px;
  color: var(--lesson-ink);
  font-size: clamp(22px, 2.8vw, 34px);
  line-height: 1.15;
}

.lesson-track-card p {
  margin: 0;
  color: #334155;
  font-size: 13.5px;
  line-height: 1.75;
}

.lesson-track-list {
  margin: 14px 0 0;
  display: grid;
  gap: 8px;
}

.lesson-track-list span {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  color: #233349;
  font-size: 12.5px;
  line-height: 1.45;
}

.lesson-track-list b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 28px;
  border-radius: 8px;
  color: color-mix(in srgb, var(--track-color) 78%, #071426);
  background: color-mix(in srgb, var(--track-color) 14%, #FFFFFF);
  font-family: var(--mono);
  font-size: 11px;
}

.lesson-tabs {
  margin-top: 16px;
  border: 1px solid rgba(7,20,38,.11);
  border-radius: 8px;
  background: rgba(255,255,255,.70);
  overflow: hidden;
}

.lesson-tab-controls {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
}

.lesson-tab {
  min-height: 48px;
  padding: 10px 8px;
  border: 0;
  border-right: 1px solid rgba(7,20,38,.09);
  border-bottom: 1px solid rgba(7,20,38,.09);
  background: rgba(255,255,255,.58);
  color: #24364D;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}

.lesson-tab:last-child {
  border-right: 0;
}

.lesson-tab.is-active {
  color: #fff;
  background: var(--tab-color, var(--lesson-blue));
}

.lesson-tab-panel {
  display: none;
  padding: 16px;
}

.lesson-tab-panel.is-active {
  display: grid;
  gap: 12px;
}

.lesson-tab-panel h4 {
  margin: 0;
  color: var(--lesson-ink);
  font-size: 18px;
}

.lesson-tab-panel p {
  margin: 0;
  color: #32455E;
  font-size: 13px;
  line-height: 1.75;
}

.lesson-outcome-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.lesson-outcome-grid span {
  min-height: 82px;
  padding: 12px;
  border: 1px solid rgba(7,20,38,.09);
  border-radius: 8px;
  background: rgba(255,255,255,.68);
  color: #2A3A51;
  font-size: 12px;
  line-height: 1.5;
}

.lesson-outcome-grid b {
  display: block;
  margin-bottom: 4px;
  color: var(--lesson-ink);
  font-family: var(--mono);
  font-size: 15px;
}

@media (max-width: 980px) {
  .ai-impact-top,
  .lesson-bridge-inner {
    grid-template-columns: 1fr;
  }

  .ai-impact-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .ai-impact-shell,
  .lesson-bridge-inner {
    padding: 14px;
  }

  .lesson-track-grid,
  .lesson-outcome-grid {
    grid-template-columns: 1fr;
  }

  .ai-benefit-table {
    display: block;
    overflow: visible;
  }

  .ai-benefit-row {
    grid-template-columns: 1fr;
    border-bottom: 1px solid rgba(7,20,38,.10);
  }

  .ai-benefit-row:last-child {
    border-bottom: 0;
  }

  .ai-benefit-row > * {
    border-right: 0;
    border-bottom: 1px solid rgba(7,20,38,.07);
  }

  .ai-benefit-row > *:last-child {
    border-bottom: 0;
  }

  .ai-benefit-head {
    display: none;
  }

  .ai-benefit-row > *::before {
    content: attr(data-label);
    display: block;
    margin-bottom: 3px;
    color: var(--lesson-muted);
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 900;
    letter-spacing: .06em;
  }

  .lesson-tab-controls {
    grid-template-columns: 1fr;
  }

  .lesson-tab {
    border-right: 0;
  }
}

@media (max-width: 520px) {
  .ai-impact-stats {
    grid-template-columns: 1fr;
  }
}
"""


BLOG_TEASER_CSS = """
.blog-feature {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, .95fr);
  gap: clamp(18px, 3vw, 34px);
  align-items: center;
  padding: clamp(18px, 3vw, 30px);
  border: 1px solid var(--line);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(239,248,246,.86));
  box-shadow: var(--shadow-card);
}
.blog-feature-copy h3 {
  margin: 0 0 10px;
  color: var(--text);
  font-size: clamp(26px, 3.2vw, 42px);
  line-height: 1.18;
  letter-spacing: 0;
}
.blog-feature-copy p {
  margin: 0 0 16px;
  color: var(--text-soft);
  line-height: 1.9;
}
.blog-feature-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}
.blog-feature-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 5px 11px;
  border-radius: 999px;
  border: 1px solid rgba(47,142,173,.22);
  background: rgba(255,255,255,.76);
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}
.blog-feature-visual img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 14px;
  border: 1px solid rgba(16,24,39,.12);
  box-shadow: 0 18px 46px rgba(16,24,39,.14);
}
.blog-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(12px, 2vw, 18px);
}
.blog-card {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255,255,255,.92);
  color: var(--text);
  text-decoration: none;
  box-shadow: var(--shadow-card);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.blog-card:hover,
.blog-card:focus-visible {
  transform: translateY(-2px);
  border-color: rgba(14,165,198,.34);
  box-shadow: 0 20px 54px rgba(16,24,39,.14);
  outline: none;
}
.blog-card-media {
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, rgba(14,165,198,.10), rgba(17,163,127,.12));
}
.blog-card-media img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
.blog-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
}
.blog-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  color: var(--muted);
  font-size: 11.5px;
  font-weight: 800;
}
.blog-card-title-row {
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:8px;
}
.blog-card-title-row h3 { min-width:0; }
.blog-new-badge {
  display:inline-flex;
  align-items:center;
  justify-content:center;
  flex:0 0 auto;
  min-height:22px;
  padding:3px 8px;
  border-radius:999px;
  background:#b42318;
  color:#fff;
  font-size:10px;
  font-weight:900;
  line-height:1;
  letter-spacing:.08em;
}
.blog-card h3 {
  margin: 0;
  color: var(--text);
  font-size: 17px;
  line-height: 1.45;
  letter-spacing: 0;
}
.blog-card p {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.7;
}
.blog-card-more {
  margin-top: auto;
  color: var(--primary);
  font-size: 12.5px;
  font-weight: 900;
}
.blog-carousel-wrap {
  margin-top: 8px;
}
.pf-carousel.blog-carousel {
  grid-auto-columns: minmax(260px, 300px);
}
.pf-carousel.blog-carousel > .blog-card {
  scroll-snap-align: start;
}
.blog-card-media {
  position: relative;
  overflow: hidden;
}
.blog-card-media--line {
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 22% 24%, rgba(255,216,77,.42), transparent 5.4rem),
    radial-gradient(circle at 82% 72%, rgba(242,102,85,.18), transparent 6rem),
    linear-gradient(135deg, rgba(0,165,200,.12), rgba(166,216,63,.12));
}
.blog-card-media--line svg {
  width: 82%;
  max-width: 250px;
  height: auto;
}
.blog-card-media--line path,
.blog-card-media--line circle {
  fill: none;
  stroke: var(--linepop-ink, #071426);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}
@media (max-width: 820px) {
  .blog-feature {
    grid-template-columns: 1fr;
  }
  .blog-list {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 760px) {
  .pf-carousel.blog-carousel {
    grid-auto-columns: 78%;
  }
}
"""


PORTAL_CSS += """

/* ---- Minimal white identity system pass: white space, ink lines, one red CTA, 2026-06-28 ---- */
:root {
  --sakana-ink: #071426;
  --sakana-text: #132033;
  --sakana-muted: #58677A;
  --sakana-line: rgba(7,20,38,.18);
  --sakana-line-soft: rgba(7,20,38,.10);
  --sakana-red: #E60012;
  --sakana-cyan: #00A5C8;
  --sakana-lime: #A6D83F;
  --sakana-yellow: #FFD84D;
  --sakana-radius: 8px;
  --sakana-shadow: 5px 5px 0 rgba(7,20,38,.035), 0 14px 34px rgba(7,20,38,.065);
}

html,
body {
  background: #FFFFFF !important;
  color: var(--sakana-text) !important;
}

body::before {
  opacity: .25 !important;
}

.site-header,
.site-header.scrolled,
header.site-header,
header.site-header.scrolled,
.site-nav,
nav.top-nav,
.menu-drop,
.mobile-nav,
.mobile-nav-panel {
  background: #FFFFFF !important;
  color: var(--sakana-ink) !important;
  border-color: var(--sakana-line) !important;
  box-shadow: 0 10px 26px rgba(7,20,38,.07) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.site-header-inner {
  min-height: 62px !important;
}

.wordmark .word-ai,
.brand-mark .brand-ha {
  color: var(--sakana-red) !important;
}

.wordmark .word-en,
.site-logo-by {
  color: var(--sakana-muted) !important;
}

.site-nav a.nav-link,
.site-nav .menu-toggle,
.site-nav .nav-admin,
.mobile-nav a,
.menu-drop a,
nav.top-nav .nav-link {
  min-height: 36px !important;
  border: 1px solid var(--sakana-line-soft) !important;
  border-radius: var(--sakana-radius) !important;
  background: #FFFFFF !important;
  color: var(--sakana-ink) !important;
  box-shadow: none !important;
}

.site-nav a.nav-link:hover,
.site-nav a.nav-link:focus-visible,
.site-nav .menu-toggle:hover,
.site-nav .menu-toggle:focus-visible,
.mobile-nav a:hover,
.mobile-nav a:focus-visible,
.menu-drop a:hover,
.menu-drop a:focus-visible,
nav.top-nav .nav-link:hover,
nav.top-nav .nav-link:focus-visible {
  background: #FFF6F6 !important;
  border-color: rgba(230,0,18,.36) !important;
  color: var(--sakana-red) !important;
  outline: none !important;
}

.nav-cta,
.login-btn-mobile,
.contact-primary,
.sticky-cta-btn,
.footer-cta,
.btn.btn-primary,
.atlas-live-cta,
.boost-action.primary,
.pkg-card .pkg-cta-primary {
  border: 1px solid var(--sakana-red) !important;
  border-radius: var(--sakana-radius) !important;
  background: var(--sakana-red) !important;
  color: #FFFFFF !important;
  box-shadow: 4px 4px 0 rgba(230,0,18,.16) !important;
  letter-spacing: 0 !important;
}

.nav-cta:hover,
.login-btn-mobile:hover,
.contact-primary:hover,
.sticky-cta-btn:hover,
.footer-cta:hover,
.btn.btn-primary:hover,
.atlas-live-cta:hover,
.boost-action.primary:hover,
.pkg-card .pkg-cta-primary:hover {
  background: var(--sakana-ink) !important;
  border-color: var(--sakana-ink) !important;
  color: #FFFFFF !important;
  transform: translateY(-1px);
}

.section-heading {
  min-height: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  color: var(--sakana-red) !important;
  font-size: 12px !important;
  letter-spacing: 0 !important;
}

.section-title::after {
  height: 3px !important;
  width: 64px !important;
  border-radius: 0 !important;
  background: linear-gradient(90deg, var(--sakana-red), var(--sakana-cyan), var(--sakana-lime)) !important;
  box-shadow: none !important;
}

.hero-proof,
.atlas-live-card,
.hero-route-card,
.path-card,
.choice-lens,
.pkg-card,
.lecture-card,
.pf-card,
.biz-card,
.service-card,
.voice-card,
.faq-item,
.growth-panel,
.flow-step,
.contact-primary,
.blog-feature,
.blog-card,
.web-showcase,
.boost-lab,
.ai-impact-board,
.lesson-bridge-shell,
.lesson-track-card,
.ai-impact-copy,
.ai-impact-card {
  border-radius: var(--sakana-radius) !important;
  border: 1px solid var(--sakana-line) !important;
  background: rgba(255,255,255,.96) !important;
  box-shadow: var(--sakana-shadow) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.contact-primary,
.contact-primary .cp-ico,
.contact-primary .cp-title,
.contact-primary .cp-desc {
  color: var(--sakana-ink) !important;
}

.contact-primary .cp-cta {
  color: var(--sakana-red) !important;
}

.contact-primary:hover,
.contact-primary:hover .cp-ico,
.contact-primary:hover .cp-title,
.contact-primary:hover .cp-desc,
.contact-primary:hover .cp-cta {
  color: #FFFFFF !important;
}

@media (max-width: 560px) {
  .contact-primary .cp-cta {
    border-top-color: var(--sakana-line-soft) !important;
  }
  .contact-primary:hover .cp-cta {
    border-top-color: rgba(255,255,255,.35) !important;
  }
}

.hero-route-card::before,
.path-card::before,
.pf-card::after,
.blog-card::after,
.pkg-card::after,
.lecture-card::after,
.path-card::after {
  background: linear-gradient(90deg, var(--sakana-red), var(--sakana-cyan), var(--sakana-lime)) !important;
}

section.block::before {
  background:
    url("data:image/svg+xml,%3Csvg width='420' height='180' viewBox='0 0 420 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23071426' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' opacity='.11'%3E%3Cpath d='M18 118c48-58 96-58 144 0s96 58 144 0 72-44 96-18'/%3E%3Cpath d='M76 64c28-22 56-22 84 0s56 22 84 0'/%3E%3Ccircle cx='114' cy='64' r='5'/%3E%3Cpath d='M342 92l24-10-7 24z'/%3E%3C/g%3E%3C/svg%3E") right 8% top 18px / min(420px, 72vw) auto no-repeat,
    linear-gradient(180deg, rgba(255,255,255,.90), rgba(255,255,255,.72)) !important;
  border-top: 1px solid var(--sakana-line-soft) !important;
  border-bottom: 1px solid var(--sakana-line-soft) !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.sticky-cta {
  border: 1px solid var(--sakana-line) !important;
  border-radius: var(--sakana-radius) var(--sakana-radius) 0 0 !important;
  background: #FFFFFF !important;
  color: var(--sakana-ink) !important;
  box-shadow: 0 -10px 30px rgba(7,20,38,.09) !important;
}

@media (max-width: 820px) {
  .site-nav {
    display: none !important;
  }

  .mobile-toggle {
    display: inline-flex !important;
    background: #FFFFFF !important;
    border-color: var(--sakana-line) !important;
    color: var(--sakana-ink) !important;
  }
}
"""

PORTAL_CSS += """

/* ---- AI compass identity pass: guide mark, 2026-06-28 ---- */
:root {
  --ai-compass-red: #E60012;
  --ai-compass-ink: #071426;
  --ai-compass-cyan: #00A5C8;
  --ai-compass-lime: #A6D83F;
}

.brand-mark,
.compass-mark {
  position: relative !important;
  width: 42px !important;
  height: 42px !important;
  flex: 0 0 42px !important;
  border-radius: 50% !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: #FFFFFF !important;
  border: 2px solid var(--ai-compass-ink) !important;
  box-shadow: 4px 4px 0 rgba(230,0,18,.13) !important;
  overflow: hidden !important;
}

.brand-mark .brand-a,
.brand-mark .brand-ha {
  opacity: 0 !important;
  width: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
}

.brand-mark::before,
.compass-mark::before {
  content: "" !important;
  position: absolute !important;
  inset: 7px !important;
  border-radius: 50% !important;
  border: 2px solid var(--ai-compass-ink) !important;
  background:
    radial-gradient(circle at 50% 50%, #FFFFFF 0 27%, transparent 29%),
    conic-gradient(from 45deg, rgba(0,165,200,.18), transparent 18%, rgba(166,216,63,.18) 38%, transparent 58%, rgba(230,0,18,.16) 78%, transparent);
}

.brand-mark::after,
.compass-mark::after {
  content: "" !important;
  position: absolute !important;
  left: 50% !important;
  top: 50% !important;
  width: 20px !important;
  height: 20px !important;
  background: linear-gradient(135deg, var(--ai-compass-red) 0 50%, var(--ai-compass-ink) 50% 100%) !important;
  clip-path: polygon(50% 0, 63% 40%, 100% 50%, 63% 60%, 50% 100%, 37% 60%, 0 50%, 37% 40%) !important;
  transform: translate(-50%, -50%) rotate(34deg) !important;
}

.site-logo:hover .brand-mark,
.site-logo:focus-visible .brand-mark {
  box-shadow: 4px 4px 0 rgba(230,0,18,.22) !important;
  transform: translateY(-1px);
}

.atlas-node,
.atlas-live-card {
  z-index: 3;
}
"""

PORTAL_CSS += """

/* ---- Cross-business consultation compass, 2026-06-29 ---- */
#business-compass { --section-accent: var(--mac-teal); }

.business-compass {
  display: grid;
  gap: 18px;
}

.business-compass-lead {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr);
  gap: 18px;
  align-items: stretch;
}

.business-compass-copy,
.agent-review-panel,
.business-compass-card {
  border-radius: 8px;
  border: 1px solid rgba(7,20,38,.13);
  background: #FFFFFF;
  box-shadow: 0 16px 40px rgba(7,20,38,.07);
}

.business-compass-copy {
  padding: clamp(22px, 4vw, 34px);
}

.business-compass-copy h3 {
  margin: 0 0 12px;
  font-size: clamp(22px, 3vw, 34px);
  line-height: 1.25;
  color: var(--text);
  letter-spacing: 0;
}

.business-compass-copy p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.9;
  font-size: 15px;
}

.business-compass-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.agent-review-panel {
  padding: 20px;
}

.agent-review-panel h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: var(--text);
}

.agent-review-list {
  display: grid;
  gap: 9px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.agent-review-list li {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 9px 0;
  border-top: 1px solid rgba(7,20,38,.08);
  color: var(--text-soft);
  font-size: 13px;
}

.agent-review-list li:first-child { border-top: 0; }
.agent-review-list b { color: var(--text); font-size: 13.5px; }
.agent-review-list em {
  grid-column: 1 / -1;
  font-style: normal;
  line-height: 1.55;
}
.agent-review-list span { font-weight: 800; color: var(--mac-teal); white-space: nowrap; }

.business-compass-decision {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 8px;
  background: rgba(245,184,61,.14);
  color: var(--text);
  font-size: 13px;
  line-height: 1.7;
}

.business-compass-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.business-compass-card {
  min-height: 100%;
  padding: 18px;
  display: grid;
  gap: 12px;
  align-content: start;
}

.business-compass-kicker {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  gap: 6px;
  padding: 5px 9px;
  border-radius: 999px;
  border: 1px solid rgba(7,20,38,.12);
  background: rgba(14,165,233,.07);
  color: var(--text);
  font-size: 11px;
  font-weight: 800;
}

.business-compass-card h3 {
  margin: 0;
  font-size: 18px;
  line-height: 1.35;
  color: var(--text);
}

.business-compass-card p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.75;
  font-size: 13.5px;
}

.business-compass-map {
  display: grid;
  gap: 7px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.business-compass-map li {
  display: grid;
  grid-template-columns: 82px 1fr;
  gap: 10px;
  padding: 8px 0;
  border-top: 1px solid rgba(7,20,38,.08);
  font-size: 12.5px;
  color: var(--text-soft);
}

.business-compass-map li:first-child { border-top: 0; }
.business-compass-map b { color: var(--text); }

.business-compass-card a {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 9px 13px;
  border-radius: 8px;
  background: var(--text);
  color: #FFFFFF;
  font-size: 12.5px;
  font-weight: 800;
  text-decoration: none;
}

.business-compass-note {
  margin: 0;
  padding: 14px 16px;
  border-left: 4px solid var(--mac-teal);
  background: rgba(0,166,118,.07);
  color: var(--text-soft);
  font-size: 13px;
  line-height: 1.8;
}

@media (max-width: 980px) {
  .business-compass-lead,
  .business-compass-grid {
    grid-template-columns: 1fr;
  }
}
"""

PORTAL_CSS += """

/* ---- AI fish line motion pass: shared top/admin motif, 2026-06-28 ---- */
:root {
  --ai-fish-ink: #071426;
  --ai-fish-red: #E60012;
  --ai-fish-cyan: #00A5C8;
  --ai-fish-green: #00A676;
  --ai-fish-yellow: #F5B83D;
  --ai-fish-line: rgba(7,20,38,.18);
}

.brand-mark,
.fish-mark {
  position: relative !important;
  width: 50px !important;
  height: 34px !important;
  flex: 0 0 50px !important;
  border-radius: 999px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  background:
    linear-gradient(135deg, rgba(0,165,200,.12), rgba(245,184,61,.16) 48%, rgba(230,0,18,.10)),
    #FFFFFF !important;
  border: 2px solid var(--ai-fish-ink) !important;
  box-shadow: 5px 5px 0 rgba(230,0,18,.12) !important;
  overflow: visible !important;
}

.brand-mark .brand-a,
.brand-mark .brand-ha {
  opacity: 0 !important;
  width: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
}

.brand-mark::before,
.fish-mark::before {
  content: "" !important;
  position: absolute !important;
  left: 8px !important;
  top: 50% !important;
  width: 27px !important;
  height: 14px !important;
  border: 2px solid var(--ai-fish-ink) !important;
  border-radius: 54% 46% 46% 54% / 58% 50% 50% 58% !important;
  background:
    radial-gradient(circle at 74% 42%, var(--ai-fish-red) 0 2px, transparent 2.4px),
    #FFFFFF !important;
  transform: translateY(-50%) !important;
}

.brand-mark::after,
.fish-mark::after {
  content: "" !important;
  position: absolute !important;
  right: 5px !important;
  top: 50% !important;
  width: 14px !important;
  height: 18px !important;
  border: 2px solid var(--ai-fish-ink) !important;
  border-left: 0 !important;
  clip-path: polygon(0 50%, 100% 4%, 82% 50%, 100% 96%) !important;
  background: #FFFFFF !important;
  transform: translateY(-50%) !important;
}

.site-logo:hover .brand-mark,
.site-logo:focus-visible .brand-mark {
  box-shadow: 5px 5px 0 rgba(230,0,18,.22) !important;
  transform: translateY(-1px);
}

.hero-fish-card {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  max-width: 520px;
  margin: 0 0 20px;
  padding: 10px 12px;
  border: 1px solid var(--sakana-line);
  border-radius: var(--sakana-radius);
  background: #FFFFFF;
  box-shadow: 4px 4px 0 rgba(7,20,38,.04);
  cursor: pointer;
  font: inherit;
  text-align: left;
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
  position: relative;
  isolation: isolate;
}

.hero-fish-card::after {
  content: "";
  position: absolute;
  left: 72px;
  right: 14px;
  bottom: 9px;
  height: 2px;
  background: linear-gradient(90deg, var(--ai-fish-cyan), var(--ai-fish-green), var(--ai-fish-yellow), transparent);
  opacity: .72;
  transform-origin: left center;
  animation: fishLineSweep 4.6s ease-in-out infinite;
  z-index: -1;
}

.hero-fish-card:hover,
.hero-fish-card:focus-visible {
  transform: translateY(-2px);
  border-color: rgba(0,165,200,.42);
  box-shadow: 8px 8px 0 rgba(245,184,61,.18), 0 18px 42px rgba(0,165,200,.16);
  outline: none;
}

.hero-fish-card .fish-mark {
  width: 48px !important;
  height: 34px !important;
  flex-basis: 48px !important;
}

.hero-fish-card b {
  display: block;
  color: var(--sakana-ink);
  font-weight: 900;
  letter-spacing: 0;
}

.hero-fish-card small {
  display: block;
  color: var(--sakana-muted);
  font-weight: 750;
  letter-spacing: 0;
}

@keyframes fishLineSweep {
  0%, 100% { transform: scaleX(.38); opacity: .35; }
  48%, 72% { transform: scaleX(1); opacity: .82; }
}

.atlas-fish-core {
  position: absolute;
  left: 50%;
  top: 50%;
  z-index: 2;
  transform: translate(-50%, -50%);
  width: min(420px, 72%);
  aspect-ratio: 2 / 1;
  display: grid;
  place-items: center;
  pointer-events: none;
}

.ai-fish-stage {
  position: relative;
  width: 100%;
  height: 100%;
  border: 1px solid var(--sakana-line);
  border-radius: var(--sakana-radius);
  background:
    linear-gradient(135deg, rgba(0,165,200,.16), rgba(0,166,118,.10) 36%, rgba(245,184,61,.18) 68%, rgba(230,0,18,.12)),
    linear-gradient(90deg, rgba(7,20,38,.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.028) 1px, transparent 1px),
    rgba(255,255,255,.94);
  background-size: auto, 36px 36px, 36px 36px, auto;
  box-shadow: 6px 6px 0 rgba(7,20,38,.04), 0 18px 42px rgba(7,20,38,.09);
  overflow: hidden;
}

.ai-fish-stage::before {
  content: "";
  position: absolute;
  inset: 13px;
  border: 2px solid rgba(7,20,38,.10);
  border-radius: 999px;
  clip-path: polygon(0 38%, 83% 38%, 100% 0, 88% 50%, 100% 100%, 83% 62%, 0 62%);
  opacity: .84;
}

.ai-fish-stage::after {
  content: "AI相談";
  position: absolute;
  left: 14px;
  bottom: 11px;
  color: rgba(7,20,38,.48);
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0;
}

.ai-fish-video {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.fish-flow,
.fish-outline,
.fish-spine,
.fish-circuit,
.fish-tail {
  fill: none;
  stroke: var(--ai-fish-ink);
  stroke-linecap: round;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}

.fish-flow {
  stroke-width: 1.4;
  opacity: .32;
  stroke-dasharray: 16 18;
  animation: fishFlow 8s linear infinite;
}

.fish-flow:nth-of-type(1) {
  stroke: var(--ai-fish-cyan);
}

.fish-flow:nth-of-type(2) {
  stroke: var(--ai-fish-green);
  animation-duration: 10s;
}

.fish-outline {
  stroke-width: 3;
  stroke-dasharray: 760;
  stroke-dashoffset: 760;
  animation: fishDraw 5.8s ease-in-out infinite;
}

.fish-tail {
  stroke-width: 3;
  stroke: var(--ai-fish-red);
  stroke-dasharray: 340;
  stroke-dashoffset: 340;
  animation: fishDraw 5.8s .18s ease-in-out infinite;
}

.fish-spine {
  stroke-width: 2;
  stroke: var(--ai-fish-cyan);
  stroke-dasharray: 240;
  stroke-dashoffset: 240;
  animation: fishDraw 5.8s .32s ease-in-out infinite;
}

.fish-circuit {
  stroke-width: 1.8;
  stroke: var(--ai-fish-yellow);
  opacity: .88;
  stroke-dasharray: 180;
  stroke-dashoffset: 180;
  animation: fishDraw 5.8s .55s ease-in-out infinite;
}

.fish-dot {
  fill: #FFFFFF;
  stroke: var(--ai-fish-ink);
  stroke-width: 2;
  transform-origin: center;
  animation: fishPulse 3.4s ease-in-out infinite;
}

.fish-dot.is-red { fill: var(--ai-fish-red); stroke: var(--ai-fish-red); }
.fish-dot.is-cyan { fill: var(--ai-fish-cyan); stroke: var(--ai-fish-cyan); }
.fish-dot.is-green { fill: var(--ai-fish-green); stroke: var(--ai-fish-green); }

@keyframes fishDraw {
  0% { stroke-dashoffset: 760; opacity: .25; }
  22%, 72% { stroke-dashoffset: 0; opacity: 1; }
  100% { stroke-dashoffset: -760; opacity: .20; }
}

@keyframes fishFlow {
  to { stroke-dashoffset: -180; }
}

@keyframes fishPulse {
  0%, 100% { transform: scale(.86); opacity: .55; }
  45%, 70% { transform: scale(1.08); opacity: 1; }
}

section.block::before {
  background:
    url("data:image/svg+xml,%3Csvg width='420' height='180' viewBox='0 0 420 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23071426' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' opacity='.12'%3E%3Cpath d='M42 92C100 42 210 42 286 92C210 142 100 142 42 92Z'/%3E%3Cpath d='M286 92l78-42c-28 34-28 50 0 84z'/%3E%3Cpath d='M94 92c50-18 102-18 160 0'/%3E%3Cpath d='M156 76v34m42-42v48m-84-8h86'/%3E%3Ccircle cx='238' cy='82' r='5'/%3E%3Ccircle cx='150' cy='76' r='4'/%3E%3Ccircle cx='198' cy='116' r='4'/%3E%3C/g%3E%3C/svg%3E") right 8% top 18px / min(420px, 72vw) auto no-repeat,
    linear-gradient(180deg, rgba(255,255,255,.90), rgba(255,255,255,.72)) !important;
}

@media (prefers-reduced-motion: reduce) {
  .fish-flow,
  .fish-outline,
  .fish-spine,
  .fish-circuit,
  .fish-tail,
  .fish-dot,
  .hero-fish-card::after {
    animation: none !important;
    stroke-dashoffset: 0 !important;
  }
}

@media (max-width: 900px) {
  .hero-fish-card {
    margin-left: auto;
    margin-right: auto;
  }
}

@media (max-width: 680px) {
  .atlas-fish-core {
    width: min(310px, 84%);
    opacity: .90;
  }
}

/* ---- Compact top-page recomposition, 2026-06-29 ---- */
section.block {
  padding-top: clamp(42px, 6vw, 64px) !important;
  padding-bottom: clamp(42px, 6vw, 64px) !important;
}

section.block.block-tight {
  padding-top: clamp(34px, 5vw, 52px) !important;
  padding-bottom: clamp(34px, 5vw, 52px) !important;
}

.merged-section .section-sub {
  margin-bottom: clamp(22px, 4vw, 34px);
}

.section-cluster {
  margin-top: clamp(30px, 5vw, 54px);
  padding-top: clamp(24px, 4vw, 38px);
  border-top: 1px solid rgba(7,20,38,.10);
  scroll-margin-top: 112px;
}

.section-mini-head {
  display: grid;
  grid-template-columns: minmax(180px, .62fr) minmax(0, 1fr);
  gap: 8px clamp(18px, 4vw, 38px);
  align-items: end;
  margin: 0 0 clamp(16px, 3vw, 24px);
}

.section-mini-head p,
.section-mini-head h3,
.section-mini-head span {
  margin: 0;
}

.section-mini-head p {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .14em;
  color: var(--primary);
  text-transform: uppercase;
}

.section-mini-head h3 {
  color: var(--text);
  font-size: clamp(21px, 2.6vw, 30px);
  line-height: 1.25;
  font-weight: 900;
  letter-spacing: 0;
}

.section-mini-head span {
  grid-column: 2;
  color: var(--text-soft);
  font-size: 14px;
  line-height: 1.75;
}

#lectures #speaker .profile-block,
#web-showcase #business-compass .business-compass {
  margin-top: 0;
}

@media (max-width: 760px) {
  .section-mini-head {
    grid-template-columns: 1fr;
  }
  .section-mini-head span {
    grid-column: auto;
  }
}

.ai-course-video-block {
  padding-top: clamp(28px, 5vw, 48px);
}

.ai-course-video-feature {
  display: grid;
  grid-template-columns: minmax(280px, .62fr) minmax(540px, 1.38fr);
  gap: clamp(18px, 2.6vw, 30px);
  align-items: center;
  padding: clamp(16px, 2.6vw, 26px);
  border: 1px solid rgba(7, 20, 38, .12);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(255,255,255,.94), rgba(248,252,255,.88)),
    radial-gradient(circle at 8% 14%, rgba(14,165,168,.16), rgba(14,165,168,0) 34%),
    radial-gradient(circle at 88% 76%, rgba(124,58,237,.12), rgba(124,58,237,0) 36%);
  box-shadow: 10px 10px 0 rgba(7,20,38,.045), 0 24px 70px rgba(7,20,38,.10);
}

.ai-course-video-copy {
  min-width: 0;
}

.ai-course-video-copy .section-heading,
.ai-course-video-copy .section-title,
.ai-course-video-copy .section-sub {
  text-align: left;
  margin-left: 0;
  margin-right: 0;
}

.ai-course-video-copy .section-title {
  max-width: 720px;
}

.ai-course-video-copy .section-sub {
  max-width: 700px;
}

.ai-course-video-points {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  padding: 0;
  margin: 18px 0 20px;
  list-style: none;
}

.ai-course-video-points li {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid rgba(7,20,38,.10);
  border-radius: 8px;
  background: rgba(255,255,255,.76);
  color: var(--text);
  font-size: 13px;
  font-weight: 850;
  line-height: 1.45;
}

.ai-course-video-points li::before {
  content: "";
  width: 9px;
  height: 9px;
  flex: 0 0 9px;
  border-radius: 999px;
  background: var(--primary);
  box-shadow: 0 0 0 4px rgba(14,165,168,.12);
}

.ai-course-video-panel {
  min-width: 0;
}

.ai-course-video-frame {
  margin: 0;
  padding: 10px;
  border-radius: 8px;
  background: #071426;
  box-shadow: 0 18px 52px rgba(7,20,38,.20);
}

.ai-course-video-frame video {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 6px;
  background: #000;
}

.ai-course-video-frame figcaption {
  margin: 8px 4px 2px;
  color: rgba(230,241,255,.82);
  font-size: 12px;
  line-height: 1.6;
}

.ai-course-video-panel {
  width: 100%;
}

@media (max-width: 980px) {
  .ai-course-video-feature {
    grid-template-columns: 1fr;
  }
  .ai-course-video-panel {
    order: -1;
  }
}

@media (max-width: 560px) {
  .hero.hero-atlas {
    min-height: auto !important;
    padding-bottom: 24px !important;
    align-content: start !important;
  }
  .ai-course-video-block {
    width: 100vw !important;
    max-width: 100vw !important;
    margin-left: calc(50% - 50vw) !important;
    margin-right: calc(50% - 50vw) !important;
    padding-top: 0 !important;
    padding-bottom: 44px !important;
  }
  .ai-course-video-feature {
    padding: 0 0 18px;
    border-left: 0;
    border-right: 0;
    border-radius: 0;
    box-shadow: 0 14px 36px rgba(7,20,38,.08);
  }
  .ai-course-video-copy {
    padding: 0 16px;
  }
  .ai-course-video-frame {
    width: 100vw;
    margin-left: 0;
    padding: 0;
    border-radius: 0;
    box-shadow: none;
  }
  .ai-course-video-frame video {
    width: 100vw;
    border-radius: 0;
  }
  .ai-course-video-frame figcaption {
    margin: 8px 16px 0;
  }
  .ai-course-video-points {
    grid-template-columns: 1fr;
  }
}
"""


PORTAL_CSS += """

/* ---- Refinement from user review: remove fish/icon noise, crop intro video, raise readability ---- */
body::before {
  background-image:
    linear-gradient(90deg, rgba(7,20,38,.032) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.024) 1px, transparent 1px) !important;
  background-size: 96px 96px, 96px 96px !important;
  background-position: 0 0, 0 0 !important;
}

section.block::before {
  background:
    linear-gradient(120deg, color-mix(in srgb, var(--section-accent, #00A5C8) 9%, transparent), transparent 36%),
    linear-gradient(180deg, rgba(255,255,255,.72), rgba(255,255,255,.48)) !important;
}

.hero-fish-card,
.atlas-fish-core,
.ai-fish-stage,
.fish-mark {
  display: none !important;
}

.hero.hero-refined {
  min-height: calc(100svh - 18px) !important;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 460px) !important;
  gap: clamp(28px, 4vw, 52px) !important;
  align-items: center !important;
  padding: clamp(86px, 9vw, 108px) 0 clamp(26px, 4vw, 44px) !important;
}

.hero.hero-refined::before {
  background:
    linear-gradient(110deg, #FFFFFF 0%, rgba(255,255,255,.96) 52%, rgba(236,249,251,.86) 100%),
    radial-gradient(circle at 84% 20%, rgba(0,165,200,.16), transparent 30%),
    radial-gradient(circle at 14% 82%, rgba(242,102,85,.12), transparent 28%) !important;
}

.hero.hero-refined::after {
  opacity: .18 !important;
  transform: none !important;
}

.hero-refined .hero-bg-layer img {
  opacity: .24 !important;
  filter: saturate(.88) contrast(.92) brightness(1.08) !important;
}

.site-logo .brand-mark {
  display: none !important;
}

.hero-refined .eyebrow {
  font-size: 14px !important;
  color: #007A94 !important;
}

.hero-refined .fusion-logo-large {
  gap: 10px !important;
}

.hero-refined .fusion-logo-large .ai {
  font-size: clamp(46px, 5.7vw, 76px) !important;
  line-height: .92 !important;
  letter-spacing: 0 !important;
  color: #071426 !important;
}

.hero-refined .fusion-logo-large .hub {
  width: fit-content;
  padding: 6px 12px !important;
  border: 1px solid rgba(7,20,38,.12);
  border-radius: 999px;
  background: #EAF8FA !important;
  color: #007A94 !important;
  font-size: clamp(18px, 1.8vw, 25px) !important;
  line-height: 1.1 !important;
}

.hero-refined .hero-title-sub {
  margin-top: 18px !important;
  max-width: 840px !important;
  color: #071426 !important;
  font-size: clamp(36px, 4.2vw, 56px) !important;
  line-height: 1.12 !important;
}

.hero-refined .hero-title-sub strong {
  color: #007A94 !important;
  background: transparent !important;
  -webkit-text-fill-color: currentColor !important;
}

.hero-refined .sub-catch {
  max-width: 680px !important;
  margin: 20px 0 8px !important;
  color: #0F5132 !important;
  font-size: clamp(18px, 1.7vw, 23px) !important;
  line-height: 1.55 !important;
}

.hero-refined .lead {
  max-width: 600px !important;
  color: #324256 !important;
  font-size: clamp(16px, 1.24vw, 18px) !important;
  line-height: 1.7 !important;
}

.hero-refined .hero-actions {
  margin-top: 22px !important;
}

.hero-refined .btn-lg {
  min-height: 52px;
  padding: 15px 22px !important;
  font-size: 16px !important;
}

.hero-refined .hero-route-bento {
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 12px !important;
  max-width: 720px !important;
  margin-top: 26px !important;
}

.hero-refined .hero-route-card {
  min-height: 118px !important;
  padding: 18px !important;
  border-radius: 12px !important;
  background: rgba(255,255,255,.86) !important;
}

.hero-refined .hero-route-card small {
  font-size: 12px !important;
  letter-spacing: .08em !important;
}

.hero-refined .hero-route-card b {
  font-size: 21px !important;
  line-height: 1.25 !important;
}

.hero-refined .hero-route-card span {
  font-size: 14.5px !important;
  line-height: 1.55 !important;
}

.hero-decision-panel {
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  gap: 18px !important;
  min-height: 500px !important;
  aspect-ratio: auto !important;
  padding: clamp(22px, 3.2vw, 34px) !important;
  overflow: hidden !important;
  transform: none !important;
  border-radius: 18px !important;
  border: 1px solid rgba(7,20,38,.12) !important;
  background:
    linear-gradient(145deg, rgba(255,255,255,.96), rgba(244,252,253,.90)),
    radial-gradient(circle at 88% 12%, rgba(0,165,200,.18), transparent 30%),
    radial-gradient(circle at 18% 88%, rgba(242,102,85,.13), transparent 34%) !important;
  box-shadow: 0 28px 74px rgba(7,20,38,.13), inset 0 1px 0 rgba(255,255,255,.96) !important;
}

.hero-decision-panel::after {
  display: none !important;
}

.decision-panel-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(7,20,38,.10);
}

.decision-panel-head span,
.decision-output-card small,
.hero-flow-card small {
  color: #007A94;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .08em;
}

.decision-panel-head b {
  max-width: 260px;
  color: #071426;
  font-size: clamp(20px, 1.9vw, 27px);
  line-height: 1.25;
  text-align: right;
}

.hero-flow-stack {
  display: grid;
  gap: 0;
}

.hero-flow-card {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 5px 14px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(7,20,38,.10);
}

.hero-flow-card:last-child {
  border-bottom: 0;
}

.hero-flow-card small {
  grid-row: span 2;
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 999px;
  background: #071426;
  color: #FFFFFF;
  letter-spacing: 0;
}

.hero-flow-card b {
  color: #071426;
  font-size: clamp(18px, 1.65vw, 23px);
  line-height: 1.25;
}

.hero-flow-card span {
  color: #344256;
  font-size: 14px;
  line-height: 1.45;
}

.decision-output-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border-radius: 14px;
  background: #071426;
  color: #FFFFFF;
}

.decision-output-card b {
  color: #FFFFFF;
  font-size: clamp(20px, 1.8vw, 25px);
  line-height: 1.25;
}

.decision-output-card span {
  color: rgba(255,255,255,.78);
  font-size: 14px;
  line-height: 1.45;
}

.decision-output-card a {
  width: fit-content;
  color: #A6D83F;
  font-weight: 900;
  text-decoration: none;
}

.section-sub {
  font-size: clamp(16px, 1.25vw, 18px) !important;
  line-height: 1.72 !important;
}

.ai-course-video-feature {
  grid-template-columns: minmax(280px, .68fr) minmax(520px, 1.32fr) !important;
  align-items: stretch !important;
  padding: clamp(18px, 2.8vw, 32px) !important;
  border-radius: 18px !important;
}

.ai-course-video-copy .section-title {
  font-size: clamp(32px, 3.7vw, 50px) !important;
}

.ai-course-video-copy .section-sub {
  font-size: clamp(16px, 1.35vw, 19px) !important;
}

.ai-course-video-points {
  gap: 8px !important;
}

.ai-course-video-points li {
  padding: 11px 0 11px 14px !important;
  border: 0 !important;
  border-left: 4px solid #00A5C8 !important;
  background: transparent !important;
  font-size: 15px !important;
  line-height: 1.55 !important;
}

.ai-course-video-points li::before {
  display: none !important;
}

.ai-course-video-frame {
  display: grid;
  align-content: start;
  gap: 10px;
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 16px !important;
  background: transparent !important;
  box-shadow: none !important;
}

.ai-course-video-crop {
  width: 100%;
  aspect-ratio: 16 / 7.1;
  overflow: hidden;
  border: 1px solid rgba(7,20,38,.12);
  border-radius: 16px;
  background: #FFFFFF;
  box-shadow: 0 22px 58px rgba(7,20,38,.16);
}

.ai-course-video-frame video {
  display: block;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  object-position: center 62% !important;
  transform: none;
  border-radius: 0 !important;
  background: #FFFFFF !important;
}

.ai-course-video-frame figcaption {
  margin: 0 2px !important;
  color: #536276 !important;
  font-size: 14px !important;
}

.speaker-modern {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 360px);
  gap: clamp(24px, 4vw, 44px);
  align-items: center;
  padding: clamp(26px, 4vw, 42px) !important;
}

.speaker-modern-copy h3 {
  margin: 8px 0 6px;
  color: #071426;
  font-size: clamp(34px, 4vw, 54px);
  line-height: 1.12;
}

.speaker-modern-kicker {
  color: #007A94;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .10em;
}

.speaker-modern-role {
  margin: 0 0 16px;
  color: #007A94;
  font-size: 17px;
  font-weight: 900;
}

.speaker-modern-lead {
  max-width: 720px;
  margin: 0;
  color: #2F3E52;
  font-size: clamp(17px, 1.4vw, 20px);
  line-height: 1.74;
}

.speaker-modern-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 22px;
}

.speaker-modern-point {
  padding: 14px 0 0;
  border-top: 3px solid #00A5C8;
}

.speaker-modern-point small {
  display: block;
  color: #071426;
  font-size: 15px;
  font-weight: 900;
  line-height: 1.3;
}

.speaker-modern-point span {
  display: block;
  margin-top: 8px;
  color: #536276;
  font-size: 14.5px;
  line-height: 1.62;
}

.speaker-modern-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.speaker-modern .speaker-art {
  max-width: 360px !important;
  justify-self: center;
  border-radius: 16px !important;
}

@media (max-width: 1040px) {
  .hero.hero-refined {
    grid-template-columns: 1fr !important;
  }
  .hero-decision-panel {
    min-height: 0 !important;
  }
  .ai-course-video-feature {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 760px) {
  .hero-refined .hero-route-bento,
  .speaker-modern-grid {
    grid-template-columns: 1fr !important;
  }
  .speaker-modern {
    grid-template-columns: 1fr;
  }
  .speaker-modern .speaker-art {
    order: -1;
    max-width: 260px !important;
  }
}

@media (max-width: 560px) {
  .hero.hero-refined {
    width: calc(100vw - 32px) !important;
    max-width: calc(100vw - 32px) !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-top: 86px !important;
  }
  .hero-refined .fusion-logo-large .ai {
    font-size: clamp(46px, 13vw, 58px) !important;
  }
  .hero-refined .hero-title-sub {
    font-size: clamp(29px, 9vw, 40px) !important;
  }
  .hero-flow-card {
    grid-template-columns: 44px minmax(0, 1fr);
    padding: 14px 0;
  }
  .hero-flow-card small {
    width: 36px;
    height: 36px;
  }
  .ai-course-video-block {
    width: auto !important;
    max-width: none !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding: 44px 0 !important;
  }
  .ai-course-video-feature {
    padding: 16px !important;
    border-radius: 18px !important;
  }
  .ai-course-video-copy {
    padding: 0 !important;
  }
  .ai-course-video-frame {
    width: 100% !important;
  }
  .ai-course-video-crop {
    aspect-ratio: 16 / 7.1;
    border-radius: 14px;
  }
}
"""


PORTAL_CSS += """

/* ---- Bright polish pass: cleaner white background and lighter cards, 2026-06-30 ---- */
:root {
  --bright-ink: #071426;
  --bright-text: #182437;
  --bright-muted: #566579;
  --bright-line: rgba(7,20,38,.105);
  --bright-line-soft: rgba(7,20,38,.065);
  --bright-surface: rgba(255,255,255,.985);
  --bright-surface-soft: rgba(249,253,255,.96);
  --bright-cyan: #00A5C8;
  --bright-teal: #0F8F72;
  --bright-lime: #A6D83F;
  --bright-shadow: 0 16px 40px rgba(7,20,38,.07), inset 0 1px 0 rgba(255,255,255,.98);
  --bright-shadow-hover: 0 22px 54px rgba(7,20,38,.10), inset 0 1px 0 rgba(255,255,255,.98);
}

html,
body {
  background: #FFFFFF !important;
  color: var(--bright-text) !important;
}

body {
  background:
    linear-gradient(180deg, #FFFFFF 0%, #FBFEFF 36%, #FFFFFF 74%) !important;
  background-size: auto !important;
}

body::before {
  opacity: .42 !important;
  background-image:
    linear-gradient(90deg, rgba(7,20,38,.014) 1px, transparent 1px),
    linear-gradient(180deg, rgba(7,20,38,.010) 1px, transparent 1px) !important;
  background-size: 112px 112px, 112px 112px !important;
}

.site-header,
.site-header.scrolled,
header.site-header,
header.site-header.scrolled,
.sticky-cta {
  border-color: var(--bright-line-soft) !important;
  background: rgba(255,255,255,.975) !important;
  box-shadow: 0 12px 32px rgba(7,20,38,.055) !important;
}

.hero.hero-refined {
  min-height: calc(100svh - 34px) !important;
}

.hero.hero-refined::before {
  background:
    linear-gradient(112deg, #FFFFFF 0%, rgba(255,255,255,.985) 54%, rgba(244,252,253,.94) 100%) !important;
}

.hero.hero-refined::after {
  opacity: .10 !important;
}

.hero-refined .hero-bg-layer img {
  opacity: .16 !important;
  filter: saturate(.82) contrast(.92) brightness(1.14) !important;
}

.hero-refined .fusion-logo-large .hub,
.hero-refined .hero-route-card,
.hero-decision-panel,
.decision-output-card,
.ai-course-video-feature,
.blog-feature,
.web-showcase,
.choice-lens,
.ai-impact-board,
.lesson-bridge-shell,
.business-compass-copy,
.agent-review-panel,
.business-compass-card,
.speaker-modern,
.pkg-card,
.lecture-card,
.pf-card,
.biz-card,
.service-card,
.voice-card,
.faq-item,
.growth-panel,
.flow-step,
.blog-card {
  border-color: var(--bright-line) !important;
  background: var(--bright-surface) !important;
  box-shadow: var(--bright-shadow) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.hero-refined .hero-route-card:hover,
.pkg-card:hover,
.lecture-card:hover,
.pf-card:hover,
.biz-card:hover,
.service-card:hover,
.blog-card:hover {
  border-color: rgba(0,165,200,.20) !important;
  box-shadow: var(--bright-shadow-hover) !important;
}

section.block {
  padding-top: clamp(62px, 7vw, 96px) !important;
  padding-bottom: clamp(62px, 7vw, 96px) !important;
}

section.block::before {
  top: 22px !important;
  bottom: 22px !important;
  border-color: rgba(7,20,38,.055) !important;
  background:
    linear-gradient(120deg, color-mix(in srgb, var(--section-accent, var(--bright-cyan)) 5%, transparent), transparent 38%),
    linear-gradient(180deg, rgba(255,255,255,.94), rgba(250,253,255,.78)) !important;
  box-shadow: 0 18px 52px rgba(7,20,38,.035) !important;
}

#packages::before {
  background:
    linear-gradient(120deg, rgba(0,165,200,.055), transparent 34%),
    linear-gradient(180deg, rgba(255,255,255,.97), rgba(248,253,255,.86)) !important;
}

.section-heading {
  color: color-mix(in srgb, var(--section-accent, var(--bright-cyan)) 76%, var(--bright-ink)) !important;
}

.section-title {
  color: var(--bright-ink) !important;
}

.section-sub,
.pkg-desc,
.hero-refined .lead,
.hero-flow-card span,
.speaker-modern-lead,
.blog-card p {
  color: var(--bright-muted) !important;
}

.hero-decision-panel {
  border-radius: 16px !important;
  background:
    linear-gradient(145deg, #FFFFFF, #F8FDFF) !important;
}

.decision-output-card {
  background: #071426 !important;
  box-shadow: none !important;
}

.hero-flow-card {
  border-bottom-color: rgba(7,20,38,.075) !important;
}

.packages-grid {
  gap: clamp(16px, 2.4vw, 26px) !important;
  margin-top: 22px !important;
}

.pkg-card {
  border-radius: 12px !important;
  overflow: hidden !important;
}

.pkg-card::before {
  opacity: .22 !important;
  background: linear-gradient(90deg, rgba(0,165,200,.055), transparent 48%, rgba(166,216,63,.045)) !important;
}

.pkg-card::after,
.hero-route-card::before,
.path-card::before,
.lecture-card::after,
.pf-card::after,
.blog-card::after {
  background: linear-gradient(90deg, var(--ai-compass-red, #E60012), var(--bright-cyan), var(--bright-lime)) !important;
}

.pkg-cat,
.pkg-level,
.packages-note,
.decision-panel-head,
.hero-refined .fusion-logo-large .hub {
  border-color: rgba(0,165,200,.16) !important;
  background: rgba(244,252,253,.92) !important;
}

.pkg-price {
  background: linear-gradient(90deg, #071426, #007A94) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
}

.packages-note {
  color: var(--bright-muted) !important;
  box-shadow: none !important;
}

.ai-course-video-crop {
  border-color: var(--bright-line) !important;
  box-shadow: 0 16px 42px rgba(7,20,38,.08) !important;
}

.sticky-cta {
  color: var(--bright-ink) !important;
  box-shadow: 0 -10px 28px rgba(7,20,38,.07) !important;
}

@media (max-width: 560px) {
  body::before {
    background-size: 88px 88px, 88px 88px !important;
  }

  section.block::before {
    top: 14px !important;
    bottom: 14px !important;
  }
}
"""


PORTAL_CSS += """

/* ---- Public mobile menu: section-order, borderless right rail, 2026-07-01 ---- */
@media (max-width: 900px) {
  .mobile-toggle,
  .generated-mobile-toggle {
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #122033 !important;
  }

  .mobile-toggle:hover,
  .mobile-toggle:focus-visible,
  .generated-mobile-toggle:hover,
  .generated-mobile-toggle:focus-visible {
    background: transparent !important;
    color: #0F5F78 !important;
    outline: none !important;
  }

  .mobile-nav {
    padding: 8px max(16px, env(safe-area-inset-left)) calc(12px + env(safe-area-inset-bottom)) max(16px, env(safe-area-inset-right)) !important;
  }

  .mobile-nav-panel--public,
  .mobile-nav-panel {
    width: min(100%, 640px) !important;
    gap: 2px !important;
    justify-items: stretch !important;
  }

  .mobile-nav-primary {
    display: none !important;
  }

  .mobile-link-list {
    display: grid !important;
    gap: 0 !important;
  }

  .mobile-link-list a,
  .mobile-nav .mobile-link-list a,
  .mobile-nav .mobile-admin-link {
    min-height: 34px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 0 !important;
    padding: 7px 2px !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #122033 !important;
    text-align: left !important;
    text-decoration: none !important;
  }

  .mobile-link-list a:hover,
  .mobile-link-list a:focus-visible,
  .mobile-nav .mobile-admin-link:hover,
  .mobile-nav .mobile-admin-link:focus-visible {
    background: #F7FBFC !important;
    color: #0F5F78 !important;
    outline: none !important;
  }

  .mobile-link-title {
    display: block !important;
    font-size: 14px !important;
    font-weight: 900 !important;
    line-height: 1.15 !important;
  }

  .mobile-link-list small {
    display: none !important;
    color: #64748b !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    line-height: 1.35 !important;
  }

  .mobile-nav .mobile-nav-label {
    padding: 6px 2px 3px !important;
    color: #0F5F78 !important;
    font-size: 10px !important;
    font-weight: 900 !important;
    letter-spacing: .08em !important;
    line-height: 1.2 !important;
    text-align: left !important;
    text-transform: uppercase !important;
  }
}
"""


def _render_header() -> str:
    """N デザイン風 fixed ヘッダー。スクロールで white/90 + blur に切替。"""
    return (
        "<header class='site-header' id='site-header'>"
        "<div class='site-header-inner'>"
        "<a class='site-logo' href='/' aria-label='AI相談 トップへ'>"
        "<span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>相</span></span>"
        "<span class='wordmark'><span class='word-ai'>AI相談</span><span class='word-hub'>彦根</span><span class='word-en'>AI CONSULT</span></span>"
        "<span class='site-logo-by'>滋賀・彦根</span>"
        "</a>"
        "<nav class='site-nav' aria-label='公開ページメニュー'>"
        "<a class='nav-link nav-essential' href='/'>ホーム</a>"
        "<a class='nav-link nav-essential' href='#packages'>講習</a>"
        "<a class='nav-link nav-essential' href='#web-showcase'>制作</a>"
        "<a class='nav-link nav-essential' href='/blog/index.html'>ブログ</a>"
        "<a class='nav-link nav-essential' href='#lectures'>資料</a>"
        "<a class='nav-link nav-essential' href='#faq'>FAQ</a>"
        "<a class='nav-cta' href='#contact'>無料相談</a>"
        "<a class='nav-link nav-essential nav-salon' href='#seven-day-courses'>サロン</a>"
        "</nav>"
        "<a class='header-member-login' href='/admin'>会員ログイン</a>"
        "<button class='mobile-toggle' id='mobile-toggle' aria-label='メニュー' aria-controls='mobile-nav' aria-expanded='false'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'><path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg>"
        "</button>"
        "</div>"
        "<div class='mobile-nav' id='mobile-nav'>"
        "<div class='mobile-nav-panel mobile-nav-panel--public'>"
        "<span class='mobile-nav-label'>ホームメニュー</span>"
        "<div class='mobile-link-list'>"
        "<a href='/'><span class='mobile-link-title'>ホーム</span><small>最初に戻る</small></a>"
        "<a href='#packages'><span class='mobile-link-title'>講習</span><small>AI講習を選ぶ</small></a>"
        "<a href='#web-showcase'><span class='mobile-link-title'>制作</span><small>HP制作と運用を見る</small></a>"
        "<a href='/blog/index.html'><span class='mobile-link-title'>ブログ</span><small>実践知を読む</small></a>"
        "<a href='#lectures'><span class='mobile-link-title'>資料</span><small>復習と手順を見る</small></a>"
        "<a href='#speaker'><span class='mobile-link-title'>講師</span><small>誰が支援するか</small></a>"
        "<a href='#faq'><span class='mobile-link-title'>FAQ</span><small>不安を先に解消</small></a>"
        "<a href='#contact'><span class='mobile-link-title'>無料相談</span><small>初回の入口整理を予約</small></a>"
        "<a href='#seven-day-courses'><span class='mobile-link-title'>AIオンラインサロン</span><small>月額2,200円・毎週火曜21時</small></a>"
        "</div>"
        "</div>"
        "</div>"
        "</header>"
    )


HEADER_JS = """
<script>
(function(){
  var header = document.getElementById('site-header');
  var toggle = document.getElementById('menu-toggle');
  var drop = document.getElementById('menu-drop');
  var mobileToggle = document.getElementById('mobile-toggle');
  var mobileNav = document.getElementById('mobile-nav');
  var mobileToggleText = mobileToggle ? mobileToggle.querySelector('.mobile-toggle-text') : null;

  function onScroll(){
    if (window.scrollY > 20) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toggle && drop) {
    toggle.addEventListener('click', function(e){
      e.stopPropagation();
      var open = drop.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function(e){
      if (!drop.contains(e.target) && !toggle.contains(e.target)) {
        drop.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape') {
        drop.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function setMobileMenu(open) {
    if (!mobileToggle || !mobileNav) return;
    if (!open && (mobileNav.contains(document.activeElement) || document.activeElement === mobileToggle)) {
      var focusTarget = window.matchMedia('(min-width: 901px)').matches
        ? document.querySelector('.site-logo')
        : mobileToggle;
      if (focusTarget) focusTarget.focus({ preventScroll: true });
    }
    mobileNav.classList.toggle('open', open);
    mobileNav.setAttribute('aria-hidden', open ? 'false' : 'true');
    mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    mobileToggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    if (mobileToggleText) mobileToggleText.textContent = open ? '閉じる' : 'メニュー';
    document.body.classList.toggle('mobile-menu-open', open);
  }

  if (mobileToggle && mobileNav) {
    var desktopMenuQuery = window.matchMedia('(min-width: 901px)');
    mobileToggle.addEventListener('click', function(){
      setMobileMenu(!mobileNav.classList.contains('open'));
    });
    mobileNav.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){ setMobileMenu(false); });
    });
    mobileNav.addEventListener('click', function(e){
      if (e.target === mobileNav) setMobileMenu(false);
    });
    function closeMobileAtDesktop(e) {
      if (e.matches) setMobileMenu(false);
    }
    if (desktopMenuQuery.addEventListener) {
      desktopMenuQuery.addEventListener('change', closeMobileAtDesktop);
    } else if (desktopMenuQuery.addListener) {
      desktopMenuQuery.addListener(closeMobileAtDesktop);
    }
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape') {
        setMobileMenu(false);
        return;
      }
      if (e.key !== 'Tab' || !mobileNav.classList.contains('open')) return;
      var focusable = [mobileToggle].concat(
        Array.prototype.slice.call(mobileNav.querySelectorAll('a[href]'))
      );
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });
  }

  // ---- Scroll fade-up / counter via IntersectionObserver
  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window && !prefersReduced) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (!en.isIntersecting) return;
        en.target.classList.add('is-visible');
        if (en.target.classList.contains('num')) animateCounter(en.target);
        // counter 要素が直接 fade-up に含まれる場合
        en.target.querySelectorAll && en.target.querySelectorAll('.num[data-count]').forEach(animateCounter);
        io.unobserve(en.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    document.querySelectorAll('.fade-up').forEach(function(el){ io.observe(el); });
    document.querySelectorAll('.num[data-count]').forEach(function(el){ io.observe(el); });
  } else {
    // IntersectionObserver 非対応 / reduced motion: 即可視化
    document.querySelectorAll('.fade-up').forEach(function(el){ el.classList.add('is-visible'); });
    document.querySelectorAll('.num[data-count]').forEach(function(el){
      var target = parseInt(el.getAttribute('data-count'), 10);
      var suffix = el.querySelector('span') ? el.querySelector('span').outerHTML : '';
      el.innerHTML = String(target) + suffix;
    });
  }

  function animateCounter(el){
    if (el.dataset.counted === '1') return;
    el.dataset.counted = '1';
    var target = parseInt(el.getAttribute('data-count'), 10);
    if (isNaN(target)) return;
    var suffix = el.querySelector('span') ? el.querySelector('span').outerHTML : '';
    var duration = 1400, start = performance.now();
    function tick(now){
      var t = Math.min((now - start) / duration, 1);
      // easeOutCubic
      var eased = 1 - Math.pow(1 - t, 3);
      var val = Math.round(target * eased);
      el.innerHTML = String(val) + suffix;
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // ---- Hero parallax (subtle)
  var hv = document.querySelector('.hero-visual');
  if (hv && !prefersReduced) {
    window.addEventListener('scroll', function(){
      var y = window.scrollY;
      if (y < 400) hv.style.transform = 'rotate(' + (0.5 - y / 1000) + 'deg) translateY(' + (y * 0.04) + 'px)';
    }, { passive: true });
  }

  // ---- Parallax band 背景のスクロール連動（要素が画面内のときだけ動かす）
  var pbg = document.querySelector('.parallax-bg');
  if (pbg && !prefersReduced) {
    var pband = pbg.closest('.parallax-band');
    var ticking = false;
    function updateParallax(){
      var rect = pband.getBoundingClientRect();
      if (rect.bottom > 0 && rect.top < window.innerHeight) {
        var progress = (window.innerHeight - rect.top) / (window.innerHeight + rect.height);
        pbg.style.transform = 'translateY(' + ((progress - 0.5) * 60) + 'px)';
      }
      ticking = false;
    }
    window.addEventListener('scroll', function(){
      if (!ticking) { window.requestAnimationFrame(updateParallax); ticking = true; }
    }, { passive: true });
    updateParallax();
  }

  // ---- Light-only. 夜モードは使わない。
  (function(){
    var root = document.documentElement;
    root.removeAttribute('data-theme');
    try { localStorage.removeItem('aihub-theme'); } catch(e) {}
  })();

  // ---- 迷ったら60秒診断（3問で、いまの仕事に合う入口を整理）
  (function(){
    var modal = document.getElementById('diagnoseModal');
    if (!modal) return;
    var body = modal.querySelector('.diagnose-body');

    var QUESTIONS = [
      { q: 'いま一番近い悩みは？', a: [
        { label: 'AIを使う前に、何から頼めるか知りたい', key: 'start' },
        { label: '告知や集客を、もっと伝わる形にしたい', key: 'promotion' },
        { label: '事務や返信にかかる時間を減らしたい', key: 'office' },
        { label: 'サイト・予約・業務の流れを整えたい', key: 'flow' },
      ]},
      { q: '今日、どこまで進めたい？', a: [
        { label: 'まず話して、優先順位を決めたい', key: 'start' },
        { label: '投稿文や画像などを一つ作りたい', key: 'promotion' },
        { label: '自分用の手順にして残したい', key: 'office' },
        { label: '関係者と進め方を決めたい', key: 'flow' },
      ]},
      { q: '最初の一歩は、どう進めたい？', a: [
        { label: '無料相談で入口を整理したい', key: 'free' },
        { label: '講習で作りながら学びたい', key: 'promotion' },
        { label: '相談しながらAIアプリサイトを作りたい', key: 'office' },
        { label: '長く使える仕組みにしたい', key: 'flow' },
      ]},
    ];
    var RESULT = {
      start: {
        badge: '自作講習・相談', title: 'まずは、作りたいものを一つ決める',
        desc: '今の課題を聞き、AIアプリサイトで最初に作る一機能と進め方を一緒に整理します。',
        bookingMeta: '120分・11,000円',
        bookingLabel: 'AIアプリサイト自作講習・相談を予約する',
        bookingUrl: '__AI_APP_SELFBUILD_BOOK_URL__'
      },
      promotion: {
        badge: '告知・集客', title: '告知・集客の型を一つ作る',
        desc: '誰に何を伝えるかを決め、投稿文・画像・次回の告知手順まで形にします。',
        bookingMeta: '120分・5,500円',
        bookingLabel: 'AIエージェント講習を予約する',
        bookingUrl: '__AI_AGENT_COURSE_URL__'
      },
      office: {
        badge: '業務改善', title: '重い事務を一つ軽くする',
        desc: '返信、要約、報告、引き継ぎなどから一つ選び、小さなAIアプリサイトとして作ります。',
        bookingMeta: '120分・11,000円',
        bookingLabel: 'AIアプリサイト自作講習・相談を予約する',
        bookingUrl: '__AI_APP_SELFBUILD_BOOK_URL__'
      },
      flow: {
        badge: '仕組みづくり', title: 'サイト・業務改善の道筋を決める',
        desc: '予約、問い合わせ、更新の流れを整理し、自分で作って直す順番を決めます。',
        bookingMeta: '120分・11,000円',
        bookingLabel: 'AIアプリサイト自作講習・相談を予約する',
        bookingUrl: '__AI_APP_SELFBUILD_BOOK_URL__'
      },
      free: {
        badge: '診断内限定', title: 'まずは、無料相談で入口を整理する',
        desc: '診断後に、AIを何に使うかと次の一歩だけを無料で整理します。',
        bookingMeta: '診断後の入口整理',
        bookingLabel: '無料相談の日程を選ぶ',
        bookingUrl: '__DIAGNOSIS_FREE_CONSULT_BOOK_URL__'
      }
    };
    var ORDER = ['start','promotion','office','flow'];

    var step = 0, scores = { start:0, promotion:0, office:0, flow:0, free:0 };
    var forcedResult = null;
    var lastTrigger = null;

    function render(){
      if (step < QUESTIONS.length) {
        var Q = QUESTIONS[step];
        var h = '<div class="diag-progress">STEP ' + (step+1) + ' / ' + QUESTIONS.length + '</div>';
        h += '<h3 class="diag-q">' + Q.q + '</h3><div class="diag-opts">';
        Q.a.forEach(function(opt){ h += '<button class="diag-opt" type="button" data-key="' + opt.key + '">' + opt.label + '</button>'; });
        h += '</div>';
        body.innerHTML = h;
      } else {
        var best = ORDER[0], bestScore = -1;
        ORDER.forEach(function(k){ if (scores[k] >= bestScore) { bestScore = scores[k]; best = k; } });
        if (forcedResult) best = forcedResult;
        var r = RESULT[best];
        body.innerHTML =
          '<div class="diag-result">' +
          '<div class="diag-result-badge">あなたは ' + r.badge + ' タイプ</div>' +
          '<div class="diag-result-lv">' + r.title + '</div>' +
          '<p class="diag-result-desc">' + r.desc + '</p>' +
          '<p class="diag-result-meta">' + r.bookingMeta + '</p>' +
          '<a class="btn btn-primary" href="' + r.bookingUrl + '" target="_blank" rel="noopener" data-close-diag>' + r.bookingLabel + '</a>' +
          '<a class="btn btn-secondary" href="#packages" data-close-diag>講習・相談コースを見る</a>' +
          '<button class="diag-restart" type="button">もう一度診断する</button>' +
          '</div>';
      }
    }
    function start(){
      step = 0;
      scores = { start:0, promotion:0, office:0, flow:0, free:0 };
      forcedResult = null;
      render();
    }
    function open(trigger){
      lastTrigger = trigger || document.activeElement;
      start();
      modal.classList.add('open');
      modal.querySelector('.diagnose-close').focus();
    }
    function close(){
      modal.classList.remove('open');
      if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
    }

    document.addEventListener('click', function(e){
      var dOpen = e.target.closest('.diagnose-open');
      if (dOpen) { e.preventDefault(); open(dOpen); return; }
    });
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape' && modal.classList.contains('open')) close();
    });
    modal.addEventListener('click', function(e){
      if (e.target === modal || e.target.closest('.diagnose-close')) { close(); return; }
      if (e.target.closest('[data-close-diag]')) { close(); return; }
      var opt = e.target.closest('.diag-opt');
      if (opt) {
        var key = opt.getAttribute('data-key');
        scores[key]++;
        if (key === 'free') forcedResult = 'free';
        step++;
        render();
        return;
      }
      if (e.target.closest('.diag-restart')) { start(); }
    });
  })();


  /* スクロールで要素をふわっと出す（reduced-motion は即表示） */
  (function(){
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var sel = '.biz-card, .service-card, .pkg-card, .faq-item, .stat, .profile-tl-item, .profile-app-card, .profile-tech-card, .profile-biz-card';
    var els = Array.prototype.slice.call(document.querySelectorAll(sel));
    if (!els.length || !('IntersectionObserver' in window)) return;
    els.forEach(function(el, i){ el.classList.add('reveal'); el.style.transitionDelay = Math.min(i * 40, 240) + 'ms'; });
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function(el){ io.observe(el); });
  })();

  // スティッキーCTA: ヒーロー通過後に出し、問い合わせ/フッター付近で引っ込める
  (function(){
    var bar = document.getElementById('sticky-cta');
    if (!bar) return;
    var contact = document.getElementById('contact');
    function update(){
      var y = window.scrollY || document.documentElement.scrollTop;
      var show = y > 520;
      if (contact){
        var r = contact.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) show = false; // 問い合わせ表示中は隠す
      }
      bar.classList.toggle('is-visible', show);
      bar.setAttribute('aria-hidden', show ? 'false' : 'true');
      if ('inert' in bar) bar.inert = !show;
    }
    window.addEventListener('scroll', update, { passive: true });
    update();
  })();

  // Portfolio/blog carousel arrows
  (function(){
    document.querySelectorAll('.pf-carousel-wrap').forEach(function(wrap){
      var track = wrap.querySelector('.pf-carousel');
      if (!track) return;
      wrap.querySelectorAll('.pf-arrow').forEach(function(btn){
        btn.addEventListener('click', function(){
          var dir = parseInt(btn.getAttribute('data-dir'), 10) || 1;
          if (track.classList.contains('salon-timeline')) {
            var cards = Array.prototype.slice.call(track.querySelectorAll('.salon-timeline-card'));
            if (!cards.length) return;
            var nearest = 0;
            var best = Infinity;
            cards.forEach(function(card, index){
              var left = card.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
              var distance = Math.abs(left - track.scrollLeft);
              if (distance < best) { best = distance; nearest = index; }
            });
            var target = Math.max(0, Math.min(cards.length - 1, nearest + dir));
            var targetLeft = cards[target].getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
            track.scrollTo({ left: targetLeft, behavior: 'smooth' });
            return;
          }
          track.scrollBy({ left: dir * Math.round(track.clientWidth * 0.8), behavior: 'smooth' });
        });
      });
    });
  })();

  // AIオンラインサロン時系列: スワイプ位置をSTEP表示・ドット・カード強調へ同期
  (function(){
    document.querySelectorAll('[data-salon-timeline]').forEach(function(wrap){
      var track = wrap.querySelector('.salon-timeline');
      var cards = Array.prototype.slice.call(wrap.querySelectorAll('.salon-timeline-card'));
      var dots = Array.prototype.slice.call(wrap.querySelectorAll('[data-salon-go]'));
      var status = wrap.querySelector('.salon-timeline-status');
      if (!track || !cards.length) return;
      var ticking = false;

      function cardLeft(card){
        return card.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
      }
      function currentIndex(){
        var nearest = 0;
        var best = Infinity;
        cards.forEach(function(card, index){
          var distance = Math.abs(cardLeft(card) - track.scrollLeft);
          if (distance < best) { best = distance; nearest = index; }
        });
        return nearest;
      }
      function update(){
        var active = currentIndex();
        cards.forEach(function(card, index){ card.classList.toggle('is-active', index === active); });
        dots.forEach(function(dot, index){
          if (index === active) dot.setAttribute('aria-current', 'step');
          else dot.removeAttribute('aria-current');
        });
        if (status) status.textContent = (active + 1) + ' / ' + cards.length;
        ticking = false;
      }
      function go(index){
        var target = Math.max(0, Math.min(cards.length - 1, index));
        track.scrollTo({ left: cardLeft(cards[target]), behavior: 'smooth' });
      }

      track.addEventListener('scroll', function(){
        if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
      }, { passive: true });
      track.addEventListener('keydown', function(event){
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
        event.preventDefault();
        go(currentIndex() + (event.key === 'ArrowRight' ? 1 : -1));
      });
      dots.forEach(function(dot){
        dot.addEventListener('click', function(){ go(parseInt(dot.getAttribute('data-salon-go'), 10) || 0); });
      });
      update();
    });
  })();

  // 公開ヒーロー: カーソル位置に合わせて背景の光だけを穏やかに動かす
  (function(){
    var featuredHero = document.querySelector('[data-interactive-hero]');
    if (!featuredHero || prefersReduced) return;
    featuredHero.addEventListener('pointermove', function(event){
      var rect = featuredHero.getBoundingClientRect();
      featuredHero.style.setProperty('--hero-x', Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)).toFixed(3));
      featuredHero.style.setProperty('--hero-y', Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)).toFixed(3));
    }, { passive:true });
    featuredHero.addEventListener('pointerleave', function(){
      featuredHero.style.setProperty('--hero-x', '.72');
      featuredHero.style.setProperty('--hero-y', '.28');
    });
  })();

  // ヒーローのサービス地図: ホットスポット選択 + 背景の軽い奥行き
  (function(){
    var hero = document.querySelector('[data-hero-atlas]');
    if (!hero) return;
    var nodes = Array.prototype.slice.call(hero.querySelectorAll('.atlas-node'));
    var kicker = hero.querySelector('.atlas-live-kicker');
    var title = hero.querySelector('.atlas-live-title');
    var desc = hero.querySelector('.atlas-live-desc');
    var cta = hero.querySelector('.atlas-live-cta');
    if (!nodes.length || !kicker || !title || !desc || !cta) return;

    function selectNode(node){
      nodes.forEach(function(n){
        var active = n === node;
        n.classList.toggle('is-active', active);
        n.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      kicker.textContent = 'Service ' + (node.getAttribute('data-index') || '');
      title.textContent = node.getAttribute('data-title') || '';
      desc.textContent = node.getAttribute('data-desc') || '';
      cta.textContent = node.getAttribute('data-cta') || '詳しく見る';
      cta.setAttribute('href', node.getAttribute('data-href') || '#contact');
    }

    nodes.forEach(function(node){
      node.addEventListener('pointerenter', function(){ selectNode(node); });
      node.addEventListener('focus', function(){ selectNode(node); });
      node.addEventListener('click', function(){ selectNode(node); });
    });

    if (!prefersReduced) {
      hero.addEventListener('pointermove', function(e){
        var r = hero.getBoundingClientRect();
        hero.style.setProperty('--mx', Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)).toFixed(3));
        hero.style.setProperty('--my', Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)).toFixed(3));
      }, { passive: true });
    }
  })();

  // AI講習ブリッジ: タブで到達点を切り替える
  (function(){
    var root = document.querySelector('[data-lesson-bridge]');
    if (!root) return;
    var tabs = Array.prototype.slice.call(root.querySelectorAll('.lesson-tab'));
    var panels = Array.prototype.slice.call(root.querySelectorAll('.lesson-tab-panel'));
    if (!tabs.length || !panels.length) return;

    function select(tab){
      var target = tab.getAttribute('data-lesson-tab');
      tabs.forEach(function(btn){
        var active = btn === tab;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
        btn.setAttribute('tabindex', active ? '0' : '-1');
      });
      panels.forEach(function(panel){
        var active = panel.getAttribute('data-lesson-panel') === target;
        panel.classList.toggle('is-active', active);
        panel.hidden = !active;
      });
    }

    tabs.forEach(function(tab){
      tab.addEventListener('click', function(){ select(tab); });
      tab.addEventListener('keydown', function(e){
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        var index = tabs.indexOf(tab);
        var next = e.key === 'ArrowRight'
          ? (index + 1) % tabs.length
          : (index - 1 + tabs.length) % tabs.length;
        tabs[next].focus();
        select(tabs[next]);
      });
    });
  })();

  // ホームページ制作ショールーム: 用途別の提案プレビューを切り替える
  // ---- Growth booster: route selector below the hero
  (function(){
    var root = document.querySelector('[data-boost-lab]');
    if (!root) return;
    var routes = Array.prototype.slice.call(root.querySelectorAll('.boost-route'));
    var title = root.querySelector('.boost-output-title');
    var desc = root.querySelector('.boost-output-desc');
    var list = root.querySelector('.boost-output-list');
    var meterValue = root.querySelector('.boost-meter b');
    var meterLabel = root.querySelector('.boost-meter span');
    if (!routes.length || !title || !desc || !list || !meterValue || !meterLabel) return;

    function escapeText(value){
      return String(value || '').replace(/[&<>"']/g, function(c){
        return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
      });
    }

    function splitBullets(value){
      return String(value || '').split('|').map(function(item){ return item.trim(); }).filter(Boolean);
    }

    function selectRoute(route){
      routes.forEach(function(btn){
        var active = btn === route;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      var color = route.getAttribute('data-color') || '#00B8D4';
      root.style.setProperty('--active-boost', color);
      title.textContent = route.getAttribute('data-title') || '';
      desc.textContent = route.getAttribute('data-desc') || '';
      meterValue.textContent = (route.getAttribute('data-score') || '90') + '%';
      meterLabel.textContent = route.getAttribute('data-label') || '集客力';
      list.innerHTML = splitBullets(route.getAttribute('data-bullets')).map(function(item){
        return '<li>' + escapeText(item) + '</li>';
      }).join('');
    }

    routes.forEach(function(route){
      route.addEventListener('click', function(){ selectRoute(route); });
      route.addEventListener('focus', function(){ selectRoute(route); });
    });

    if (!prefersReduced) {
      root.addEventListener('pointermove', function(e){
        var r = root.getBoundingClientRect();
        root.style.setProperty('--boost-x', Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)).toFixed(3));
        root.style.setProperty('--boost-y', Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)).toFixed(3));
      }, { passive: true });
    }
  })();

  (function(){
    var root = document.querySelector('[data-web-showcase]');
    if (!root) return;
    var tabs = Array.prototype.slice.call(root.querySelectorAll('.web-show-tab'));
    var kicker = root.querySelector('.web-preview-kicker');
    var title = root.querySelector('.web-preview-title');
    var desc = root.querySelector('.web-preview-desc');
    var chips = root.querySelector('.web-preview-chips');
    var cta = root.querySelector('.web-showcase-cta');
    var target = root.querySelector('.web-spec-target');
    var primary = root.querySelector('.web-spec-primary');
    var secondary = root.querySelector('.web-spec-secondary');
    var minis = Array.prototype.slice.call(root.querySelectorAll('.web-mini-panel strong'));
    if (!tabs.length || !kicker || !title || !desc || !chips || !cta) return;

    function splitList(value){
      return (value || '').split('|').map(function(item){ return item.trim(); }).filter(Boolean);
    }

    function setText(el, value){
      if (el) el.textContent = value || '';
    }

    function selectTab(tab){
      tabs.forEach(function(btn){
        var active = btn === tab;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      root.style.setProperty('--show-accent', tab.getAttribute('data-accent') || '#00A5C8');
      setText(kicker, tab.getAttribute('data-kicker'));
      setText(title, tab.getAttribute('data-title'));
      setText(desc, tab.getAttribute('data-desc'));
      setText(target, tab.getAttribute('data-target'));
      setText(primary, tab.getAttribute('data-primary'));
      setText(secondary, tab.getAttribute('data-secondary'));
      cta.textContent = tab.getAttribute('data-cta') || '相談する';
      cta.setAttribute('href', tab.getAttribute('data-href') || '#contact');
      chips.innerHTML = splitList(tab.getAttribute('data-chips')).map(function(chip){
        return '<span class="web-preview-chip">' + chip.replace(/[&<>"']/g, function(c){
          return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
        }) + '</span>';
      }).join('');
      splitList(tab.getAttribute('data-mini')).forEach(function(text, index){
        if (minis[index]) minis[index].textContent = text;
      });
      if (!prefersReduced) {
        root.classList.remove('is-switching');
        void root.offsetWidth;
        root.classList.add('is-switching');
        window.setTimeout(function(){ root.classList.remove('is-switching'); }, 520);
      }
    }

    tabs.forEach(function(tab){
      tab.addEventListener('click', function(){ selectTab(tab); });
      tab.addEventListener('focus', function(){ selectTab(tab); });
    });

    if (!prefersReduced) {
      root.addEventListener('pointermove', function(e){
        var r = root.getBoundingClientRect();
        root.style.setProperty('--sx', Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)).toFixed(3));
        root.style.setProperty('--sy', Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)).toFixed(3));
      }, { passive: true });
    }
  })();
})();
</script>
""".replace("__AI_APP_SELFBUILD_BOOK_URL__", AI_APP_SELFBUILD_BOOK_URL).replace("__AI_AGENT_COURSE_URL__", AI_AGENT_COURSE_URL).replace("__DIAGNOSIS_FREE_CONSULT_BOOK_URL__", DIAGNOSIS_FREE_CONSULT_BOOK_URL)


HERO_IMG = "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=1200&q=70"

# 線画ヒーローSVG（designer設計仕様 2026-05-27 を実装）。
# 7レイヤー: 背景グラデ→glowリング→データストリーム→書類スタック(✓)→
# 人物(IT苦手だが前向きな経営者の安堵の笑み)→データ粒子→ラベルバッジ。
# フラットカラー+統一アウトライン(#F0F4FF)。ロボット要素は出さない。
HERO_SVG = """
<svg class="hero-svg" viewBox="0 0 460 575" role="img"
  aria-label="線画イラスト: 彦根の経営者がAIの光と一緒に山積みの業務を片付けて軽くなっていく様子"
  xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="hbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#11162a"/><stop offset="1" stop-color="#0B0D14"/>
    </linearGradient>
    <linearGradient id="hgrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2BA7C8"/><stop offset="0.55" stop-color="#7AA58A"/><stop offset="1" stop-color="#D9852B"/>
    </linearGradient>
    <radialGradient id="hglow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#8AA0FF" stop-opacity="0.55"/><stop offset="1" stop-color="#8AA0FF" stop-opacity="0"/>
    </radialGradient>
    <filter id="hblur" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>
  </defs>

  <rect width="460" height="575" fill="url(#hbg)"/>

  <!-- 透視グリッド（床・消失点 230,150）-->
  <g stroke="#2BA7C8" stroke-opacity="0.12" stroke-width="1.2">
    <path d="M-40 430 L210 165"/><path d="M120 430 L222 165"/><path d="M300 430 L238 165"/><path d="M500 430 L250 165"/>
    <path d="M0 350 H460" stroke-opacity="0.07"/><path d="M0 400 H460" stroke-opacity="0.07"/>
  </g>

  <!-- glow リング（呼吸）-->
  <ellipse class="hsvg-glow" cx="230" cy="215" rx="140" ry="150" fill="url(#hglow)" filter="url(#hblur)"/>

  <!-- データストリーム（流れ）-->
  <g class="hsvg-stream" fill="none" stroke="url(#hgrad)" stroke-width="2.4" stroke-linecap="round" stroke-opacity="0.85">
    <path style="--d:0s" d="M40 70 C150 45 210 120 300 72"/>
    <path style="--d:.5s" d="M60 120 C160 96 250 165 360 108"/>
    <path style="--d:1s" d="M40 185 C140 178 250 140 340 188"/>
  </g>

  <!-- 書類スタック（左・✓で片付き）-->
  <g stroke="#F0F4FF" stroke-width="2.2" stroke-linejoin="round">
    <rect x="40" y="372" width="116" height="24" rx="6" fill="#222C46"/>
    <rect x="48" y="352" width="116" height="24" rx="6" fill="#2A3656"/>
    <rect x="56" y="332" width="116" height="24" rx="6" fill="#33406A"/>
    <path d="M72 344 l7 7 l14 -16" fill="none" stroke="#5BE0B0" stroke-width="3.4" stroke-linecap="round"/>
  </g>

  <!-- 人物（中央やや右・安堵の笑み）-->
  <g stroke="#F0F4FF" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">
    <!-- 胴・ジャケット -->
    <path d="M178 405 C182 320 204 286 244 286 C284 286 306 320 310 405 Z" fill="#1C2840"/>
    <path d="M244 286 L244 392" stroke-opacity="0.5"/>
    <path d="M228 290 L244 322 L260 290" fill="#F4F6FB"/>
    <!-- 首 -->
    <rect x="232" y="268" width="24" height="24" rx="8" fill="#F1C9A5"/>
    <!-- 顔 -->
    <ellipse cx="244" cy="240" rx="33" ry="36" fill="#F6D3B0"/>
    <!-- 髪（白髪混じりショート）-->
    <path d="M211 234 C209 197 229 184 244 184 C259 184 280 197 277 234 C271 219 259 211 244 211 C229 211 217 219 211 234 Z" fill="#54607A"/>
    <!-- 目（やや大きめ）-->
    <circle cx="232" cy="241" r="3.4" fill="#2A3142" stroke="none"/>
    <circle cx="256" cy="241" r="3.4" fill="#2A3142" stroke="none"/>
    <!-- 安堵の笑み -->
    <path d="M235 255 Q244 261 253 255" fill="none" stroke="#B5805A" stroke-width="2.4"/>
    <!-- 上げた右手（粒子を受け止める）-->
    <path d="M304 326 C334 306 348 262 344 238" fill="none" stroke="#1C2840" stroke-width="14" stroke-linecap="round"/>
    <circle cx="344" cy="234" r="11" fill="#F1C9A5"/>
  </g>

  <!-- データ粒子（手・頭上で脈動）-->
  <g fill="url(#hgrad)">
    <circle class="hsvg-p" cx="344" cy="210" r="6" style="--pd:0s"/>
    <circle class="hsvg-p" cx="366" cy="186" r="4" style="--pd:.4s"/>
    <circle class="hsvg-p" cx="322" cy="176" r="5" style="--pd:.8s"/>
    <circle class="hsvg-p" cx="390" cy="220" r="3.5" style="--pd:1.2s"/>
    <circle class="hsvg-p" cx="300" cy="140" r="4" style="--pd:1.6s"/>
    <circle class="hsvg-p" cx="358" cy="130" r="3" style="--pd:2s"/>
  </g>

  <!-- ラベルバッジ -->
  <g font-family="Inter, sans-serif" font-weight="700">
    <g transform="translate(290,96)">
      <rect width="118" height="30" rx="15" fill="#161925" stroke="#2BA7C8" stroke-opacity="0.5"/>
      <circle class="hsvg-dot" cx="17" cy="15" r="4" fill="#5BE0B0"/>
      <text x="30" y="20" fill="#A6AEC4" font-size="12">自動化中…</text>
    </g>
    <g transform="translate(40,294)">
      <rect width="92" height="30" rx="15" fill="#161925" stroke="#5BE0B0" stroke-opacity="0.6"/>
      <text x="14" y="20" fill="#5BE0B0" font-size="12">✓ 業務完了</text>
    </g>
  </g>
</svg>
"""


def _render_fish_line_video() -> str:
    return (
        "<div class='ai-fish-stage'>"
        "<svg class='ai-fish-video' viewBox='0 0 520 260' role='img' aria-label='魚の線画がゆっくり描かれるAIモーション'>"
        "<path class='fish-flow' d='M22 132 C88 96 168 88 246 126 S394 170 498 112'/>"
        "<path class='fish-flow' d='M34 170 C116 206 230 206 326 160 S426 112 504 146'/>"
        "<path class='fish-outline' d='M72 134 C150 72 272 76 362 134 C272 194 150 198 72 134 Z'/>"
        "<path class='fish-tail' d='M360 134 L456 82 C426 124 426 144 456 186 Z'/>"
        "<path class='fish-spine' d='M126 134 C188 114 262 116 334 134'/>"
        "<path class='fish-circuit' d='M154 116 V88 H216 V112 M214 154 V184 H282 V150 M246 104 V78 H306'/>"
        "<circle class='fish-dot is-red' cx='300' cy='116' r='6'/>"
        "<circle class='fish-dot is-cyan' cx='216' cy='88' r='5'/>"
        "<circle class='fish-dot is-green' cx='282' cy='184' r='5'/>"
        "<circle class='fish-dot' cx='132' cy='132' r='5'/>"
        "</svg>"
        "</div>"
    )


def _render_hero() -> str:
    atlas_items = [
        {
            "index": "01",
            "title": "無料相談",
            "sub": "課題を整理",
            "desc": "課題を聞き、無料相談・講習・伴走のどれから始めるかを一緒に決めます。",
            "cta": "無料相談の日程を見る",
            "href": "#contact",
            "x": "42%",
            "y": "35%",
        },
        {
            "index": "02",
            "title": "AI講習",
            "sub": "目的別に迷わせない",
            "desc": "無料相談、個別相談、AIエージェント講習、伴走支援を目的別に並べます。",
            "cta": "受講プランを見る",
            "href": "#packages",
            "x": "64%",
            "y": "24%",
        },
        {
            "index": "03",
            "title": "受講資料",
            "sub": "あとから見返せる",
            "desc": "講習内容、AI活用、SNS、LLMOを資料センターとして整理します。",
            "cta": "資料を見る",
            "href": "#lectures",
            "x": "71%",
            "y": "52%",
        },
        {
            "index": "04",
            "title": "進め方",
            "sub": "相談から手順化",
            "desc": "自慢として見せるのではなく、相談、講習、資料、公開前確認の順番を見せます。",
            "cta": "流れを見る",
            "href": "#flow",
            "x": "50%",
            "y": "68%",
        },
        {
            "index": "05",
            "title": "SNS / AI観測",
            "sub": "毎朝チューニング",
            "desc": "競合、国内トレンド、YouTube、SNS反応を見て入口を更新します。",
            "cta": "改善ループを見る",
            "href": "#growth",
            "x": "83%",
            "y": "72%",
        },
    ]
    atlas_buttons: list[str] = []
    for i, item in enumerate(atlas_items):
        active = " is-active" if i == 0 else ""
        atlas_buttons.append(
            "<button type='button' "
            f"class='atlas-node{active}' "
            f"aria-pressed='{'true' if i == 0 else 'false'}' "
            f"data-index='{html.escape(item['index'], quote=True)}' "
            f"data-title='{html.escape(item['title'], quote=True)}' "
            f"data-desc='{html.escape(item['desc'], quote=True)}' "
            f"data-cta='{html.escape(item['cta'], quote=True)}' "
            f"data-href='{html.escape(item['href'], quote=True)}' "
            f"style='--x:{item['x']};--y:{item['y']}'>"
            "<span class='atlas-dot' aria-hidden='true'></span>"
            "<span class='atlas-node-copy'>"
            f"<b>{html.escape(item['title'])}</b>"
            f"<small>{html.escape(item['sub'])}</small>"
            "</span>"
            "</button>"
        )
    flow_steps = [
        ("01", "悩みを整理", "課題を1行にする"),
        ("02", "講習で触る", "画面を見ながら試す"),
        ("03", "資料に残す", "手順として残す"),
        ("04", "発信へ回す", "各媒体へ再編集"),
    ]
    flow_html = "".join(
        "<div class='hero-flow-card'>"
        f"<small>{html.escape(num)}</small>"
        f"<b>{html.escape(title)}</b>"
        f"<span>{html.escape(body)}</span>"
        "</div>"
        for num, title, body in flow_steps
    )
    return (
        "<section class='hero hero-atlas hero-refined' id='top'>"
        "<div class='hero-bg-layer' aria-hidden='true'>"
        "<img src='img/hero-codex-claude-imagegen-20260616.png' alt='' decoding='async' fetchpriority='high'>"
        "</div>"
        "<div class='hero-text fade-up'>"
        "<span class='eyebrow'>滋賀・彦根 / AI相談と実践講座</span>"
        "<h1 class='hero-brand'>"
        "<span class='fusion-logo-large'><span class='ai'>AI相談</span><span class='hub'>彦根</span></span>"
        "<span class='hero-title-sub'><strong>AIで、仕事を整える。</strong></span>"
        "<span class='visually-hidden'>｜彦根 AI相談、滋賀 生成AI講習、Codex講習、Claude Code併用、ChatGPT講座、画像生成講習、AI導入支援、補助金申請サポート、LLMO対策、YouTube SEO、SNS集客</span>"
        "</h1>"
        "<p class='sub-catch'>"
        "<strong>相談、講習、資料化、発信まで一気に。</strong>"
        "</p>"
        "<p class='lead'>"
        "時間がない、告知が苦手、AIが分からない。身近な困りごとを、今日から使える形に変えます。"
        "</p>"
        "<div class='hero-actions'>"
        "<a class='btn btn-primary btn-lg' href='#contact'>まず無料相談</a>"
        "<a class='btn btn-secondary btn-lg' href='#ai-course-video'>動画で見る</a>"
        "</div>"
        "<div class='hero-route-bento' aria-label='最初に選ぶ3つの入口'>"
        "<a class='hero-route-card route-consult' href='#contact'><small>FREE CONSULT</small><b>無料相談</b><span>今の課題を整理</span></a>"
        "<a class='hero-route-card route-code' href='#packages'><small>LESSON</small><b>講習</b><span>画面を見ながら実践</span></a>"
        "<a class='hero-route-card route-material' href='#lectures'><small>MATERIAL</small><b>資料</b><span>手順を残して復習</span></a>"
        "</div>"
        "</div>"
        "<div class='hero-photo-card hero-atlas-panel hero-decision-panel fade-up d2' aria-label='AI相談の進め方'>"
        "<div class='decision-panel-head'>"
        "<span>AI CONSULT FLOW</span>"
        "<b>1つの悩みを、4媒体へ展開</b>"
        "</div>"
        f"<div class='hero-flow-stack'>{flow_html}</div>"
        "<div class='decision-output-card'>"
        "<small>OUTPUT</small>"
        "<b>相談メモ / 講習資料 / 投稿文 / 公開ページ</b>"
        "<span>一度の実践知を、媒体ごとに使い回せる形にします。</span>"
        "<a href='#flow'>進め方を見る →</a>"
        "</div>"
        "</div>"
        "</section>"
    )


def _render_ai_course_video_feature() -> str:
    video_src = "/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm"
    poster_src = "/media/ai-consult-hikone-20260629/ai-consult-hikone-poster.png"
    captions_src = "/media/ai-consult-hikone-20260629/ai-consult-hikone-captions.vtt"
    return (
        "<section class='block ai-course-video-block' id='ai-course-video'>"
        "<div class='ai-course-video-feature'>"
        "<div class='ai-course-video-copy fade-up'>"
        "<p class='section-heading'>INTRO MOVIE</p>"
        "<h2 class='section-title'>紹介動画で、講座の空気をつかむ</h2>"
        "<p class='section-sub'>"
        "難しいAIの話から入らず、毎日の困りごとをどう講習・資料・発信へ変えるかだけに絞りました。"
        "</p>"
        "<ul class='ai-course-video-points'>"
        "<li>時間がない、告知が苦手、AIが分からない人向け</li>"
        "<li>講習後に手順と資料が残る進め方</li>"
        "<li>SNS投稿・HP改善・業務アプリまで展開</li>"
        "</ul>"
        "<div class='section-more'>"
        "<a class='btn btn-primary' href='/blog/2026-06-29-ai-consult-hikone-practical-ai-course.html'>ブログで詳しく読む →</a>"
        "<a class='btn btn-secondary' href='#packages'>受講プランを見る</a>"
        "</div>"
        "</div>"
        "<div class='ai-course-video-panel fade-up d2'>"
        "<figure class='ai-course-video-frame'>"
        "<div class='ai-course-video-crop'>"
        f"<video autoplay muted loop playsinline preload='metadata' poster='{poster_src}' aria-label='AI講座紹介動画'>"
        f"<source src='{video_src}' type='video/webm'>"
        f"<track src='{captions_src}' kind='captions' srclang='ja' label='日本語字幕' default>"
        "</video>"
        "</div>"
        "<figcaption>目的、対象者、成果物を短く確認できます。</figcaption>"
        "</figure>"
        "</div>"
        "</div>"
        "</section>"
    )


def _render_growth_booster() -> str:
    """Render a bright interactive acquisition booster below the hero."""
    routes = [
        {
            "code": "ROUTE 01",
            "title": "Codexで直す",
            "copy": "見出し、導線、FAQをその場で改善",
            "output": "ページを直して、その日に集客へ戻す",
            "desc": "Codexで現在のページを読み、問い合わせに近い順に見出し、CTA、FAQ、構造化データを更新します。",
            "bullets": ["予約ボタンと問い合わせ導線を先に固定", "差分確認で余計な崩れを防ぐ", "公開前チェックまで一気に進める"],
            "score": "91",
            "label": "即日改善度",
            "color": "#00B8D4",
        },
        {
            "code": "ROUTE 02",
            "title": "Claude Codeで詰める",
            "copy": "設計と文章の穴を別視点で見る",
            "output": "AI同士の役割分担で、打ち手を太くする",
            "desc": "Codexで実装し、Claude Codeで構造、コピー、抜け漏れを詰める流れにすると、公開物の説得力が上がります。",
            "bullets": ["ページ構造と訴求の弱点を再確認", "講習内容と予約導線を矛盾なく接続", "AI任せにせず人が採用判断する"],
            "score": "87",
            "label": "説得力",
            "color": "#2F80ED",
        },
        {
            "code": "ROUTE 03",
            "title": "画像生成で見せる",
            "copy": "文章だけでなく視覚で期待値を作る",
            "output": "一目で「何ができるか」が伝わる",
            "desc": "講習や制作の成果を、抽象的なAI感ではなく、現場で使う画面、資料、投稿イメージとして見せます。",
            "bullets": ["ヒーロー画像とOGPを明るく更新", "SNS用の派生ビジュアルを作る", "講習後の成果物を見える化する"],
            "score": "94",
            "label": "第一印象",
            "color": "#FF5D73",
        },
        {
            "code": "ROUTE 04",
            "title": "SNSへ流す",
            "copy": "Reels、Shorts、投稿の入口を作る",
            "output": "ページから投稿へ、投稿からページへ戻す",
            "desc": "1つのテーマを短い投稿、動画台本、FAQ、講習資料へ展開して、検索とSNSの入口を同時に増やします。",
            "bullets": ["短尺動画の台本に分解", "投稿後に戻るLPを用意", "反応を見てFAQと見出しを育てる"],
            "score": "89",
            "label": "回遊力",
            "color": "#FFB000",
        },
        {
            "code": "ROUTE 05",
            "title": "AI検索へ残す",
            "copy": "LLMOとFAQで引用されやすくする",
            "output": "AIが答えに使える一次情報を増やす",
            "desc": "料金、場所、講師、実例、受講内容を明確にし、検索エンジンとAI回答の両方が読み取りやすい形に整えます。",
            "bullets": ["地域名と料金を曖昧にしない", "FAQとJSON-LDを同期", "一次経験と実例を本文に残す"],
            "score": "86",
            "label": "AI発見性",
            "color": "#00A676",
        },
        {
            "code": "ROUTE 06",
            "title": "HPへ着地",
            "copy": "無料相談、講習、制作へ迷わず進める",
            "output": "見て楽しいだけでなく、予約までつなぐ",
            "desc": "明るい色と動きで興味を作り、最後は無料相談、受講プラン、制作相談のどれかに着地させます。",
            "bullets": ["無料相談を迷わない位置へ置く", "講習と制作の違いを選べる形にする", "スマホでもCTAを押しやすくする"],
            "score": "93",
            "label": "予約導線",
            "color": "#FF8A3D",
        },
    ]
    route_html: list[str] = []
    for index, route in enumerate(routes):
        active = " is-active" if index == 0 else ""
        bullets = "|".join(route["bullets"])
        route_html.append(
            "<button type='button' "
            f"class='boost-route{active}' "
            f"aria-pressed='{'true' if index == 0 else 'false'}' "
            f"style='--route-color:{html.escape(route['color'], quote=True)}' "
            f"data-color='{html.escape(route['color'], quote=True)}' "
            f"data-score='{html.escape(route['score'], quote=True)}' "
            f"data-label='{html.escape(route['label'], quote=True)}' "
            f"data-title='{html.escape(route['output'], quote=True)}' "
            f"data-desc='{html.escape(route['desc'], quote=True)}' "
            f"data-bullets='{html.escape(bullets, quote=True)}'>"
            f"<small>{html.escape(route['code'])}</small>"
            f"<b>{html.escape(route['title'])}</b>"
            f"<span>{html.escape(route['copy'])}</span>"
            "</button>"
        )
    first = routes[0]
    first_bullets = "".join(f"<li>{html.escape(item)}</li>" for item in first["bullets"])
    return (
        "<section class='boost-block' id='boost'>"
        "<div class='boost-lab fade-up' data-boost-lab "
        f"style='--active-boost:{html.escape(first['color'], quote=True)}'>"
        "<div class='boost-shell'>"
        "<div class='boost-copy'>"
        "<p class='section-heading'>GROWTH BOOST</p>"
        "<h2>集客ブースターを、<strong>斜め上</strong>に回す</h2>"
        "<p><strong>時代はCodex。Claude Codeと併用、画像も生成。</strong>"
        "暗いAIサイトではなく、触ってわかる明るい入口に変えて、無料相談、講習、HP制作、SNS集客へ迷わず進めます。</p>"
        "<div class='boost-actions'>"
        "<a class='boost-action primary' href='#contact'>無料相談へ進む</a>"
        "<a class='boost-action' href='#packages'>講習プランを見る</a>"
        "<a class='boost-action' href='#web-showcase'>HP制作を見る</a>"
        "</div>"
        "</div>"
        "<div class='boost-stage'>"
        "<div class='boost-route-grid' aria-label='集客ルートを選ぶ'>"
        f"{''.join(route_html)}"
        "</div>"
        "<div class='boost-output' aria-live='polite'>"
        "<div>"
        f"<h3 class='boost-output-title'>{html.escape(first['output'])}</h3>"
        f"<p class='boost-output-desc'>{html.escape(first['desc'])}</p>"
        f"<ul class='boost-output-list'>{first_bullets}</ul>"
        "</div>"
        "<div class='boost-meter'>"
        f"<b>{html.escape(first['score'])}%</b>"
        f"<span>{html.escape(first['label'])}</span>"
        "</div>"
        "</div>"
        "</div>"
        "</div>"
        "</div>"
        "</section>"
    )


def _render_web_showcase() -> str:
    """ホームページ制作の提案力を、用途別に切り替えて見せるショールーム。"""
    items = [
        {
            "title": "店舗・予約LP",
            "sub": "来店、予約、LINE相談",
            "kicker": "Site 01 / 店舗集客",
            "desc": "メニュー、料金、空き状況、口コミ、Googleマップ、LINE導線を一画面で整理。初めて見た人が「行けそう」と感じる入口を作ります。",
            "target": "予約、問い合わせ、来店前の不安解消",
            "primary": "スマホ最優先のLP、予約CTA、口コミブロック",
            "secondary": "Googleビジネスプロフィール、LINE、SNS投稿との接続",
            "cta": "店舗サイトの相談をする",
            "href": "#contact",
            "chips": ["予約導線", "料金表", "口コミ", "地図", "LINE"],
            "mini": ["メニューと料金", "空き状況", "お客様の声"],
            "accent": "#00B8D4",
        },
        {
            "title": "企業サイト",
            "sub": "信頼、採用、問い合わせ",
            "kicker": "Site 02 / 会社の見せ方",
            "desc": "会社概要だけで終わらせず、強み、施工事例、採用情報、代表メッセージを読みやすく配置。紹介先に送れる名刺代わりのサイトへ整えます。",
            "target": "紹介先や採用候補に、安心して見せられること",
            "primary": "トップ、事業紹介、サービス、採用、問い合わせ",
            "secondary": "写真整理、文章作成、公開後の更新しやすさ",
            "cta": "企業サイトを相談する",
            "href": "#contact",
            "chips": ["会社案内", "サービス", "採用", "代表紹介", "FAQ"],
            "mini": ["強みの整理", "事例一覧", "採用導線"],
            "accent": "#3F6E9A",
        },
        {
            "title": "EC・商品LP",
            "sub": "商品理解から購入まで",
            "kicker": "Site 03 / 売れる商品導線",
            "desc": "商品の世界観、使い方、比較、FAQ、購入ボタンを分断せずに設計。Shopify、カラーミー、既存カートとの接続まで見据えて作れます。",
            "target": "商品価値を伝え、購入前の迷いを減らすこと",
            "primary": "商品LP、カテゴリ導線、レビュー、購入CTA",
            "secondary": "Shopify、カラーミー、在庫・記事・SNSとの連携",
            "cta": "商品サイトを相談する",
            "href": "#contact",
            "chips": ["商品LP", "EC連携", "レビュー", "FAQ", "在庫"],
            "mini": ["商品写真", "比較表", "購入ボタン"],
            "accent": "#FF6B4A",
        },
        {
            "title": "講習・資料サイト",
            "sub": "教材、講座、会員向け資料",
            "kicker": "Site 04 / 学びの導線",
            "desc": "講習ページ、受講資料、動画、PDF、申し込み導線をまとめ、受講前後に見返せる場所を作ります。AI講習サイトの実例をそのまま教材にできます。",
            "target": "説明会、講座販売、受講後フォローを楽にすること",
            "primary": "講座LP、資料一覧、個別ページ、予約導線",
            "secondary": "Markdown更新、PDF配布、管理画面、検索導線",
            "cta": "講習サイトを相談する",
            "href": "#contact",
            "chips": ["講座LP", "資料一覧", "PDF", "動画", "予約"],
            "mini": ["受講プラン", "資料ライブラリ", "復習ページ"],
            "accent": "#00A676",
        },
        {
            "title": "AI業務システム",
            "sub": "管理画面、Bot、自動化",
            "kicker": "Site 05 / 裏側まで作る",
            "desc": "見た目のホームページだけでなく、管理画面、記事生成、問い合わせ整理、LINE Bot、データベースまで接続。日々の作業を減らすサイトにします。",
            "target": "更新、集計、返信、社内確認をサイト内で回すこと",
            "primary": "管理画面、AI生成、DB、認証、通知",
            "secondary": "Vercel、Supabase、GitHub Actions、LINE連携",
            "cta": "業務システムを相談する",
            "href": "#contact",
            "chips": ["管理画面", "AI生成", "DB", "LINE Bot", "自動化"],
            "mini": ["管理メニュー", "自動生成", "通知と集計"],
            "accent": "#A6D70F",
        },
        {
            "title": "SNS・改善導線",
            "sub": "公開してから育てる",
            "kicker": "Site 06 / 運用と改善",
            "desc": "サイト公開で終わらせず、SNS投稿、AI検索対策、FAQ追加、記事化、反応の確認まで一緒に設計。毎月育つホームページに変えます。",
            "target": "検索、SNS、AI回答から見つけられる入口を増やすこと",
            "primary": "記事、FAQ、ショート動画導線、LLMO対策",
            "secondary": "RSS観測、SNS分析、問い合わせ改善、導線更新",
            "cta": "改善運用を相談する",
            "href": "#growth",
            "chips": ["SNS", "LLMO", "FAQ", "記事化", "改善"],
            "mini": ["反応を見る", "記事にする", "導線を育てる"],
            "accent": "#D09B1E",
        },
    ]

    first = items[0]
    tabs: list[str] = []
    for i, item in enumerate(items, start=1):
        active = " is-active" if i == 1 else ""
        pressed = "true" if i == 1 else "false"
        chips = "|".join(item["chips"])
        mini = "|".join(item["mini"])
        tabs.append(
            "<button type='button' "
            f"class='web-show-tab{active}' "
            f"aria-pressed='{pressed}' "
            f"style='--accent:{html.escape(item['accent'], quote=True)}' "
            f"data-title='{html.escape(item['title'], quote=True)}' "
            f"data-kicker='{html.escape(item['kicker'], quote=True)}' "
            f"data-desc='{html.escape(item['desc'], quote=True)}' "
            f"data-target='{html.escape(item['target'], quote=True)}' "
            f"data-primary='{html.escape(item['primary'], quote=True)}' "
            f"data-secondary='{html.escape(item['secondary'], quote=True)}' "
            f"data-cta='{html.escape(item['cta'], quote=True)}' "
            f"data-href='{html.escape(item['href'], quote=True)}' "
            f"data-chips='{html.escape(chips, quote=True)}' "
            f"data-mini='{html.escape(mini, quote=True)}' "
            f"data-accent='{html.escape(item['accent'], quote=True)}'>"
            f"<span class='web-tab-num'>{i:02d}</span>"
            "<span>"
            f"<span class='web-tab-title'>{html.escape(item['title'])}</span>"
            f"<span class='web-tab-sub'>{html.escape(item['sub'])}</span>"
            "</span>"
            "</button>"
        )

    chips_html = "".join(f"<span class='web-preview-chip'>{html.escape(chip)}</span>" for chip in first["chips"])
    mini_html = "".join(
        "<div class='web-mini-panel'>"
        "<span></span><span></span>"
        f"<strong>{html.escape(text)}</strong>"
        "</div>"
        for text in first["mini"]
    )
    proof_steps = [
        ("01", "構成案", "誰に、何を、どの順番で見せるかを先に決める"),
        ("02", "見た目", "写真、余白、導線、スマホ表示まで整える"),
        ("03", "実装", "Vercel / Shopify / CMS / 管理画面に接続する"),
        ("04", "改善", "SNS、FAQ、記事、AI検索まで公開後に育てる"),
    ]
    proof_html = "".join(
        f"<div class='web-proof-step'><small>{num}</small><b>{html.escape(title)}</b><span>{html.escape(desc)}</span></div>"
        for num, title, desc in proof_steps
    )

    return (
        f"<div class='web-showcase fade-up d2' data-web-showcase style='--show-accent:{html.escape(first['accent'], quote=True)}'>"
        "<div class='web-showcase-shell'>"
        "<div class='web-showcase-intro'>"
        "<span class='web-showcase-badge'>WEB PRODUCTION SHOWROOM</span>"
        "<p class='web-showcase-lead'>作りたいサイトの種類を押すと、画面の見せ方、必要な導線、裏側の仕組みまで切り替わります。商談の場で「こんなものもできます」と一緒に見せられる、制作メニューの見本帳です。</p>"
        f"<div class='web-showcase-tabs' aria-label='作れるホームページの種類'>{''.join(tabs)}</div>"
        "</div>"
        "<div class='web-stage' aria-live='polite'>"
        "<div class='web-preview-board'>"
        "<div class='web-browser'>"
        "<div class='web-browser-bar' aria-hidden='true'><span class='web-browser-dot'></span><span class='web-browser-dot'></span><span class='web-browser-dot'></span></div>"
        "<div class='web-preview-copy'>"
        f"<span class='web-preview-kicker'>{html.escape(first['kicker'])}</span>"
        f"<h3 class='web-preview-title'>{html.escape(first['title'])}</h3>"
        f"<p class='web-preview-desc'>{html.escape(first['desc'])}</p>"
        f"<div class='web-preview-chips'>{chips_html}</div>"
        f"<a class='web-showcase-cta' href='{html.escape(first['href'], quote=True)}'>{html.escape(first['cta'])}</a>"
        "</div>"
        f"<div class='web-mini-site' aria-hidden='true'>{mini_html}</div>"
        "</div>"
        "</div>"
        "<div class='web-spec-card'>"
        f"<div class='web-spec-row'><b>狙う成果</b><span class='web-spec-target'>{html.escape(first['target'])}</span></div>"
        f"<div class='web-spec-row'><b>表に出すもの</b><span class='web-spec-primary'>{html.escape(first['primary'])}</span></div>"
        f"<div class='web-spec-row'><b>裏側でつなぐもの</b><span class='web-spec-secondary'>{html.escape(first['secondary'])}</span></div>"
        "</div>"
        f"<div class='web-proof-rail'>{proof_html}</div>"
        "</div>"
        "</div>"
        "</div>"
    )


def _render_path_selector() -> str:
    cards = [
        (
            "迷っている人",
            "無料相談から始める",
            "今の課題を整理して、受講プランか伴走かを決める入口です。",
            "無料相談を予約する",
            "#contact",
            "相談前メモ",
            "次に: 課題メモだけ持参",
        ),
        (
            "講習を選びたい人",
            "AI講習と資料を並べて見る",
            "無料相談、個別相談、AIエージェント講習、伴走支援を目的と到達点で確認できます。",
            "講習導線を見る",
            "#packages",
            "相談 / 講習 / 資料",
            "次に: 相談・講習・伴走支援へ",
        ),
        (
            "プランを選びたい人",
            "受講プランを比べる",
            "無料相談、個別相談、AIエージェント講習、伴走支援を、料金と到達点で比べられます。",
            "受講プランを見る",
            "#packages",
            "相談 / 60分 / 120分",
            "次に: 関連資料を確認",
        ),
    ]
    parts = ["<div class='path-grid'>"]
    for persona, title, desc, cta, href, meta, proof in cards:
        parts.append(
            "<a class='path-card fade-up' href='{href}'>"
            "<span class='path-kicker'>FIRST STEP</span>"
            f"<span class='path-persona'>{html.escape(persona)}</span>"
            f"<strong>{html.escape(title)}</strong>"
            f"<p>{html.escape(desc)}</p>"
            f"<span class='path-meta'>{html.escape(meta)}</span>"
            f"<span class='path-proof'>{html.escape(proof)}</span>"
            f"<span class='path-cta'>{html.escape(cta)} →</span>"
            "</a>".format(href=html.escape(href, quote=True))
        )
    parts.append("</div>")
    return "".join(parts)


def _render_choice_lens() -> str:
    rows = [
        (
            "AIを始めたいが、何から聞けばよいか分からない",
            "無料相談",
            "課題を聞いて、講習・伴走のどちらに進むかをその場で切り分けます。",
        ),
        (
            "AI講習の内容や復習先を、参加者に分かりやすく見せたい",
            "AI講習導線",
            "講習前の確認、当日の実践、復習資料、予約導線までを1つに整理します。",
        ),
        (
            "CodexやClaude Codeで、自分の資料やページを作りたい",
            "AIエージェント講習",
            "持ち込み課題を成果物にし、差分確認と公開前チェックまで練習します。",
        ),
        (
            "社内や店舗にAI運用を定着させたい",
            "AI伴走支援",
            "6ヶ月の導入計画、補助金相談、HP・事務・SNSの実装をまとめて扱います。",
        ),
    ]
    parts = [
        "<div class='choice-lens fade-up d3' aria-label='今の状態から選ぶAI講習の入口'>",
        "<div class='choice-lens-head'><span>いまの状態</span><span>おすすめ入口</span><span>判断材料</span></div>",
    ]
    for state, reco, proof in rows:
        parts.append(
            "<div class='choice-lens-row'>"
            f"<div class='choice-lens-state'>{html.escape(state)}</div>"
            f"<div class='choice-lens-reco'><small>NEXT</small>{html.escape(reco)}</div>"
            f"<div class='choice-lens-proof'>{html.escape(proof)}</div>"
            "</div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_ai_impact_board() -> str:
    """AI導入の現在地を、講習に進む理由として数字で見せる。"""
    stats = [
        ("88%", "AI利用", "McKinsey 2025: 1業務以上で定常利用", "#0877C6"),
        ("約1/3", "全社展開", "多くはまだ実験・試行段階", "#00A676"),
        ("62%", "Agent実験", "AIエージェントを試す企業が増加", "#F5B83D"),
        ("47%", "AI研修あり", "使っているのに教わっていない人が多い", "#E60012"),
    ]
    stat_html = "".join(
        f"<div class='ai-impact-card' style='--card-color:{html.escape(color, quote=True)}'>"
        f"<b>{html.escape(num)}</b>"
        f"<span>{html.escape(label)}</span>"
        f"<small>{html.escape(note)}</small>"
        "</div>"
        for num, label, note, color in stats
    )
    rows = [
        ("受付・問い合わせ", "AIで返信文、FAQ、電話メモを整える", "相談で課題を3つに絞る", "返信の迷いを減らす"),
        ("講習案内", "予習、当日、復習の資料リンクを1本化", "AI講習と資料リンクで表示", "参加前後の迷子を減らす"),
        ("広報・SNS", "動画台本、投稿文、画像案、FAQへ展開", "1テーマから3本の発信案", "週1更新に落とす"),
        ("サイト・業務", "CodexでLP、資料、フォーム、管理画面を作る", "120分で原型と確認手順", "6ヶ月で定着させる"),
    ]
    row_html = [
        "<div class='ai-benefit-row ai-benefit-head'><span>場面</span><span>AIで変えること</span><span>講習で作るもの</span><span>目標</span></div>"
    ]
    for scene, change, output, goal in rows:
        row_html.append(
            "<div class='ai-benefit-row'>"
            f"<strong data-label='場面'>{html.escape(scene)}</strong>"
            f"<span data-label='AIで変えること'>{html.escape(change)}</span>"
            f"<span data-label='講習で作るもの'>{html.escape(output)}</span>"
            f"<span data-label='目標'>{html.escape(goal)}</span>"
            "</div>"
        )
    return (
        "<div class='ai-impact-board fade-up d2'>"
        "<div class='ai-impact-shell'>"
        "<div class='ai-impact-top'>"
        "<div class='ai-impact-copy'>"
        "<span class='ai-impact-kicker'>2025 DATA / WHY NOW</span>"
        "<h3>使うだけでは、成果にならない。</h3>"
        "<p>AI利用は急増しています。ただし全社で使い切れている企業はまだ少なく、研修や検証の型が追いついていません。だから講習では、ツール名よりも「何を作り、どう確認し、どこへ戻るか」を先に決めます。</p>"
        "</div>"
        f"<div class='ai-impact-stats'>{stat_html}</div>"
        "</div>"
        f"<div class='ai-benefit-table'>{''.join(row_html)}</div>"
        "<p class='ai-source-note'>Sources: "
        "<a href='https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai' target='_blank' rel='noopener'>McKinsey, The state of AI in 2025</a>"
        " / "
        "<a href='https://www.businessinsider.com/kpmg-trust-in-ai-study-2025-how-employees-use-ai-2025-4' target='_blank' rel='noopener'>KPMG + University of Melbourne global AI trust study reporting</a>"
        "。数字は講習設計の参考値で、個別の成果を保証するものではありません。</p>"
        "</div>"
        "</div>"
    )


def _render_lesson_bridge() -> str:
    """AI講習と受講資料を、目的別の導線で並べる。"""
    panels = [
        (
            "starter",
            "AI講習",
            "#0877C6",
            "ChatGPT、Codex、Claude Code、画像生成を、仕事の文章、資料、広報、サイト改善に接続します。",
            [("01", "無料相談で整理"), ("02", "個別相談で具体化"), ("03", "講習で実践")],
        ),
        (
            "material",
            "受講資料",
            "#00A676",
            "講習後に自分で再現できるように、プロンプト、手順、確認ポイント、関連ページを残します。",
            [("読", "先に確認"), ("戻", "講習後に復習"), ("使", "仕事に転用")],
        ),
        (
            "outcome",
            "実例化",
            "#00A676",
            "講習で終わらせず、1テーマからFAQ、配布資料、予約導線、SNS投稿、サイト内ページまで展開します。",
            [("3", "入口を選ぶ"), ("1", "復習先を作る"), ("6", "ヶ月で定着")],
        ),
    ]
    tab_buttons = []
    tab_panels = []
    for i, (key, label, color, body, outcomes) in enumerate(panels):
        active = i == 0
        tab_buttons.append(
            "<button type='button' "
            f"class='lesson-tab{' is-active' if active else ''}' "
            f"style='--tab-color:{html.escape(color, quote=True)}' "
            "role='tab' "
            f"aria-selected='{'true' if active else 'false'}' "
            f"tabindex='{'0' if active else '-1'}' "
            f"data-lesson-tab='{html.escape(key, quote=True)}'>"
            f"{html.escape(label)}</button>"
        )
        outcome_html = "".join(
            f"<span><b>{html.escape(num)}</b>{html.escape(text)}</span>"
            for num, text in outcomes
        )
        tab_panels.append(
            "<div "
            f"class='lesson-tab-panel{' is-active' if active else ''}' "
            "role='tabpanel' "
            f"data-lesson-panel='{html.escape(key, quote=True)}' "
            f"{'' if active else 'hidden'}>"
            f"<h4>{html.escape(label)}で見せること</h4>"
            f"<p>{html.escape(body)}</p>"
            f"<div class='lesson-outcome-grid'>{outcome_html}</div>"
            "</div>"
        )
    return (
        "<div class='lesson-bridge-shell fade-up d2' data-lesson-bridge>"
        "<div class='lesson-bridge-inner'>"
        "<div class='lesson-bridge-copy'>"
        "<span class='lesson-bridge-kicker'>AI LESSON / MATERIAL</span>"
        "<h3>AI講習と資料を、迷わず選ぶ。</h3>"
        "<p>講習を受ける前、受けた後、仕事に使う段階で、押すべき場所が変わります。無料相談、個別相談、AIエージェント講習、受講資料を目的別に並べます。</p>"
        "<div class='lesson-tabs'>"
        f"<div class='lesson-tab-controls' role='tablist' aria-label='AI講習と受講資料の切り替え'>{''.join(tab_buttons)}</div>"
        f"{''.join(tab_panels)}"
        "</div>"
        "</div>"
        "<div class='lesson-track-grid'>"
        "<article class='lesson-track-card ai'>"
        "<span class='lesson-track-label'>AI講習</span>"
        "<h3>相談から実践へ</h3>"
        "<p>AIを何に使うかを無料相談で整理し、個別相談またはAIエージェント講習へ進めます。</p>"
        "<div class='lesson-track-list'>"
        "<span><b>相</b>無料相談で課題を切り分け</span>"
        "<span><b>60</b>個別相談で使い方を整理</span>"
        "<span><b>120</b>AIエージェント講習で実践</span>"
        "</div>"
        "</article>"
        "<article class='lesson-track-card material'>"
        "<span class='lesson-track-label'>資料</span>"
        "<h3>あとから見返せる</h3>"
        "<p>講習の内容を、資料、チェックリスト、実例ページ、予約導線として残します。</p>"
        "<div class='lesson-track-list'>"
        "<span><b>読</b>受講前に概要を見る</span>"
        "<span><b>復</b>講習後に手順を復習</span>"
        "<span><b>使</b>仕事の型に転用</span>"
        "</div>"
        "</article>"
        "</div>"
        "</div>"
        "<p class='ai-source-note'>AI講習は、相談、準備、実践、復習を分けるほど継続しやすくなります。まずは無料相談で目的を絞り、必要な資料と講習を選びます。</p>"
        "</div>"
    )


def _render_stats() -> str:
    items = [
        ("9", "", "同時運営事業", ""),
        ("30", "年", "クライミング歴", "経営よりずっと長い"),
        ("100", "%", "Web 自社構築", "外注ゼロ・全部自前"),
        ("2027", "", "育成就労 移行支援", ""),
    ]
    parts = ["<div class='stats-strip'>"]
    for i, (num, suffix, label, sub) in enumerate(items):
        cls = f"stat fade-up d{i+1}"
        suf_html = f"<span style='font-size:.6em'>{html.escape(suffix)}</span>" if suffix else ""
        sub_html = f"<div class='stat-sub'>{html.escape(sub)}</div>" if sub else ""
        parts.append(
            f"<div class='{cls}'><div class='num' data-count='{html.escape(num)}'>0{suf_html}</div>"
            f"<div class='label'>{html.escape(label)}</div>{sub_html}</div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_gallery() -> str:
    """事例ギャラリー：4 枚の画像で異なるサービスを視覚的に提示。"""
    items = [
        ("LP / コーポレートサイト",
         "Next.js + Supabase + Vercel",
         "https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&w=900&q=70"),
        ("クライミングジム EC",
         "カラーミー + Shopify",
         "https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&w=900&q=70"),
        ("LINE Bot / SNS 自動化",
         "Cloudflare Workers + D1",
         "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=900&q=70"),
        ("AI / 社内 RAG",
         "Claude + Supabase Vector",
         "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=70"),
    ]
    parts = ["<div class='gallery-grid'>"]
    for i, (title, meta, src) in enumerate(items):
        cls = f"gallery-item fade-up d{i+1}"
        parts.append(
            f"<div class='{cls}'>"
            f"<img src='{html.escape(src, quote=True)}' alt='{html.escape(title)}' loading='lazy' decoding='async'>"
            "<div class='gallery-caption'>"
            f"<span class='tag'>WORK</span>"
            f"<div class='title'>{html.escape(title)}</div>"
            f"<div class='meta'>{html.escape(meta)}</div>"
            "</div>"
            "</div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_services() -> str:
    items = [
        ("📈", "Webマーケティング・LP制作",
         "Next.js + Supabase でランディングと業務システムを一体運用。PR プレビュー付きでクライアントと一緒に磨ける開発体制。",
         "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=70"),
        ("🤖", "AI 業務活用・社内RAG",
         "Claude / GPT を使った業務自動化、社内ドキュメントを参照する RAG チャットの設計と構築。",
         "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=800&q=70"),
        ("📚", "経営勉強会・社内研修",
         "現役オーナーの目線で、現場で使える Web / AI / SNS の使い方を社員研修・経営者勉強会として開催。",
         "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=800&q=70"),
        ("🛡️", "補助金活用・2027 移行支援",
         "ものづくり / IT導入 / 育成就労（特定技能 2027 移行）など、補助金と法令対応をセットで動かす伴走型支援。",
         "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=70&sat=-30"),
        ("🛒", "EC・予約・LINE 自動化",
         "カラーミー・Shopify・Stripe・LINE Bot を組み合わせて、注文〜接客〜配信の業務を 1 つの動線にまとめる。",
         "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=70"),
        ("📊", "数字根拠の経営レビュー",
         "現役オーナーとして月次決算 / KPI を回している立場から、コンサルではなく一緒に数字を見るパートナー型レビュー。",
         "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=70"),
    ]
    parts = ["<div class='services-grid'>"]
    for i, (icon, name, desc, img) in enumerate(items):
        parts.append(
            f"<div class='service-card fade-up d{(i % 3) + 1}'>"
            f"<div class='service-image'><img src='{html.escape(img, quote=True)}' alt='{html.escape(name)}' loading='lazy' decoding='async'></div>"
            "<div class='service-body'>"
            f"<div class='service-icon-float'>{html.escape(icon)}</div>"
            f"<div class='service-name'>{html.escape(name)}</div>"
            f"<div class='service-desc'>{html.escape(desc)}</div>"
            "</div>"
            "</div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_courses_packages() -> str:
    """講習・相談プランのカード一覧。"""
    selfbuild_title = "AIアプリサイト自作講習・相談 120分"
    free_consult_title = "AI無料相談 入口整理"
    support_title = "AI伴走支援 いっしょに導入"
    items = [
        {
            "icon": "○",
            "cat": "無料相談",
            "level": "入口",
            "level_id": "beginner",
            "title": free_consult_title,
            "price": "無料",
            "duration": "初回 / 無料",
            "subsidy": False,
            "desc": "来店またはオンラインで、講習・AI導入・補助金の入口を整理します。",
            "content": [
                "今の課題とAIで試したいことを聞き取り",
                "基本講習、自作講習・相談、伴走支援の入口を切り分け",
                "補助金、交流会、次回予約の導線を確認",
            ],
            "fit": ["まず話を聞きたい", "講習か伴走か迷う", "来店またはオンラインで相談したい"],
            "url": DIAGNOSIS_FREE_CONSULT_BOOK_URL,
            "cta": "無料相談を予約する",
            "material_url": "#lectures",
            "material_cta": "受講資料で選び方を見る",
        },
        {
            "icon": "◇",
            "cat": "伴走",
            "level": "上級",
            "level_id": "advanced",
            "title": support_title,
            "price": MONTHLY_SUPPORT_PRICE_DETAIL,
            "duration": "初回相談予約",
            "subsidy": True,
            "desc": "HP公開、事務自動化、AI導入、デザイン内製化、経理、マーケを6ヶ月で定着させます。",
            "content": [
                "AIホームページ、書類作成、営業効率化を設計",
                "経理・バックオフィス自動化、専用AIツール作成を支援",
                "補助金用のカリキュラム案、見積、導入計画まで並走",
            ],
            "fit": ["社内にAI運用を定着させたい", "複数業務をまとめて仕組み化したい", "補助金前提で導入計画を組みたい"],
            "url": MONTHLY_SUPPORT_BOOK_URL,
            "cta": "伴走支援を申し込む",
            "material_url": "#lectures",
            "material_cta": "受講資料で導入の流れを見る",
            "variant": "wide",
        },
        {
            "icon": "▧",
            "cat": "個別実装",
            "level": "実装",
            "level_id": "implementation",
            "title": selfbuild_title,
            "price": "11,000円",
            "duration": "120分 / 少人数",
            "subsidy": False,
            "desc": "作りたいAIアプリサイトを題材に、相談、設計、AIへの依頼、確認、修正、公開までを個別に進めます。",
            "content": [
                "作りたい機能と利用者を整理し、小さな仕様へ分ける",
                "依頼文、差分、データ、セキュリティ、PC・スマホ表示を確認する",
                "エラーを直し、GitHubとクラウドで公開して本番URLを確かめる",
            ],
            "fit": ["AIアプリサイトを自分で作りたい", "相談しながら最初の一機能を完成させたい", "公開後も自分で確認・修正できるようになりたい"],
            "req_title": "このプランで使う受講資料",
            "requirements": [
                "AIアプリサイトの資料をもとに、仕事の分解、依頼、確認、修正、成果物の保存を通しで学ぶ",
                "受講後は小さな制作物を作り、説明できない変更を公開前に止める判断まで練習する",
            ],
            "verify": "予約ページでは120分の講習メニューを選んでください。",
            "url": AI_APP_SELFBUILD_BOOK_URL,
            "cta": "AIアプリサイト自作講習・相談を予約する",
            "material_url": "/programming-map.html",
            "material_cta": "AIアプリサイト自作の受講資料を見る",
            "variant": "featured",
        },
    ]
    parts = ["<div class='packages-grid'>"]
    for i, it in enumerate(items):
        subsidy_badge = (
            "<span class='pkg-subsidy'>✓ 補助金対応</span>" if it["subsidy"] else ""
        )
        lvl = it.get("level", "")
        lvl_id = it.get("level_id", "")
        level_badge = f"<span class='pkg-level' data-level='{html.escape(lvl_id)}'>{html.escape(lvl)}</span>" if lvl else ""
        content_items = "".join(f"<li>{html.escape(v)}</li>" for v in it.get("content", []))
        content_html = ""
        if content_items:
            content_html = (
                "<div class='pkg-content-box'>"
                "<strong class='pkg-content-title'>受講内容</strong>"
                f"<ul class='pkg-content'>{content_items}</ul>"
                "</div>"
            )
        fit_items = "".join(f"<li>{html.escape(v)}</li>" for v in it.get("fit", []))
        fit_html = f"<ul class='pkg-fit'>{fit_items}</ul>" if fit_items else ""
        req_items = "".join(f"<li>{html.escape(v)}</li>" for v in it.get("requirements", []))
        req_html = ""
        if req_items:
            req_html = (
                "<div class='pkg-req-box'>"
                f"<strong class='pkg-req-title'>{html.escape(it.get('req_title') or '条件')}</strong>"
                f"<ul class='pkg-req'>{req_items}</ul>"
                f"<p class='pkg-verify'>{html.escape(it.get('verify') or '')}</p>"
                "</div>"
            )
        variant = str(it.get("variant") or "")
        variant_cls = " pkg-featured" if variant == "featured" else (" pkg-wide" if variant == "wide" else "")
        # 外部URL(http)は別タブ、mailtoは同タブ
        is_ext = it["url"].startswith("http")
        target_attr = " target='_blank' rel='noopener'" if is_ext else ""
        material_url = str(it.get("material_url") or "")
        material_html = ""
        if material_url:
            material_target = " target='_blank' rel='noopener'" if material_url.startswith("http") else ""
            material_html = (
                f"<a class='pkg-material-link' href='{html.escape(material_url, quote=True)}'{material_target}>"
                f"{html.escape(str(it.get('material_cta') or '関連する受講資料を見る'))} →</a>"
            )
        parts.append(
            f"<div class='pkg-card{variant_cls} fade-up d{(i % 3) + 1}' data-level='{html.escape(lvl_id)}'>"
            f"<div class='pkg-body'>"
            f"<div class='pkg-topline'><span class='pkg-cat'>{html.escape(it['cat'])}</span></div>"
            f"<div class='pkg-head'>"
            f"<h3 class='pkg-title'>{html.escape(it['title'])}</h3>"
            f"</div>"
            f"<div class='pkg-meta'>{level_badge}<span>⏱ {html.escape(it['duration'])}</span></div>"
            f"<div class='pkg-price'>{html.escape(it['price'])}</div>"
            f"{subsidy_badge}"
            f"<p class='pkg-desc'>{html.escape(it['desc'])}</p>"
            f"{content_html}"
            f"{fit_html}"
            f"{req_html}"
            f"<a class='pkg-cta' href='{html.escape(it['url'], quote=True)}'{target_attr}>{html.escape(it['cta'])} →</a>"
            f"{material_html}"
            f"</div>"
            f"</div>"
        )
    parts.append("</div>")
    parts.append(
        "<p class='packages-note fade-up d4'>"
        "<strong>AIアプリサイト自作講習・相談:</strong> 作りたいものの相談から、AIへの依頼、コード確認、修正、安全な公開までを120分11,000円で個別に進めます。"
        "<br><strong>無料相談:</strong> AI無料相談は、講習・伴走のどちらから始めるかを無料で整理する入口です。"
        "<br><strong>伴走支援:</strong> 6ヶ月伴走は既存のSquare予約ページから初回相談を申し込めます。"
        "<br><strong>補助金:</strong> 講習と伴走支援は、滋賀県・彦根市のデジタル化/AI導入系補助金と組み合わせて相談できます。"
        "</p>"
    )
    return "".join(parts)


COURSE_TESTIMONIALS: tuple[dict, ...] = (
    {
        "key": "ai-agent",
        "course_name": "AIエージェント講習",
        "anchor_id": "voice-ai-agent",
        "heading": "ゼロからでも、AIエージェントが仕事の相棒になった",
        "testimonials": (
            {
                "title": "インストールから、実際に作れるところまで",
                "body": "インストールから一つずつ説明してもらい、IDEもAIエージェントもゼロから触れました。最後は自分で実際に作れるところまで進めたので、とても分かりやすかったです。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "基礎がストーリーでつながり、記憶に残った",
                "body": "本当に使えるレベルになるには基礎が大事だと、ストーリー仕立てでみっちり教えてもらえました。覚えやすい言い回しも面白く、内容がすっと頭に入りました。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "使うほど、手になじむ感覚があった",
                "body": "エンジニア向けに見えるツールなのに、楽しみながら使えました。使うほど手になじみ、自分の仕事でも続けられそうだと感じました。",
                "author_label": "受講者（匿名）",
            },
        ),
    },
    {
        "key": "ai-app-selfbuild",
        "course_name": "AIアプリサイト自作講習・相談",
        "anchor_id": "voice-ai-app-selfbuild",
        "heading": "相談から公開までつながり、自分で直せる形になった",
        "testimonials": (
            {
                "title": "会社の業務を、そのまま相談できた",
                "body": "会社で使っているツールと実際の業務をそのまま相談でき、疑問点を一つずつ整理しながら、その場で解決策を見つけられたのがよかったです。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "「役立ちそう」ではなく、その場で成果が見えた",
                "body": "これまでAIが実際の業務に役立つと感じたことはありませんでしたが、今回は本当に使える成果を見せてもらえました。作業のスピード感もあり、すぐに導入したいと思いました。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "社内に導入できる形まで落とし込めた",
                "body": "解決策が事業の中で形になっていくのを実感できました。会社へ導入しやすいところまで整理でき、今度は自分がほかの人へ伝えられることも増えたと思います。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "手打ちより、仕様と順序が効率を決めると分かった",
                "body": "これまではコードを手で打つことに集中していましたが、プロジェクトの目的や仕様書に沿って進めることが、結果的に大きな効率化につながると分かりました。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "設計・セキュリティ・公開工程まで見えた",
                "body": "AIはコードを書くだけでなく、ワークフローやデザイン、必要なデータ、セキュリティ、公開までの順序も提案できると知りました。プロの進め方を一つずつ理解できました。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "チーム開発と採用にも使える、新しい進め方だった",
                "body": "部下と共同作業するときのAI活用フローがとても分かりやすかったです。GitHubやワークツリー、低コストのクラウドサービスも学べて、自動化や費用削減だけでなく、今後の採用にも役立つと感じました。",
                "author_label": "受講者（匿名）",
            },
        ),
    },
    {
        "key": "ai-support",
        "course_name": "AI伴走支援",
        "anchor_id": "voice-ai-support",
        "heading": "社内の理解が進み、AI導入が動き出した",
        "testimonials": (
            {
                "title": "上司への説明まで支えてもらい、導入が早まった",
                "body": "会社の上司との話し合いにも入っていただき、新しい提案を分かりやすく説明してもらえたので、社内でのAI導入がとても早く進みました。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "自分たちでは見えなかった問題を洗い出せた",
                "body": "私たちだけでは気づけなかった問題点を見つけてもらい、何から解決するかまで整理できました。社内でAIを活用できる可能性が見えたことがうれしかったです。",
                "author_label": "受講者（匿名）",
            },
            {
                "title": "明日やることが増えた分、仕事が前へ進み始めた",
                "body": "YouTubeで見るだけとは違い、目の前で問題が解決していく様子は見ていて気持ちがよかったです。明日からやることは増えましたが、その分、業務がどんどん進む感覚がありました。",
                "author_label": "受講者（匿名）",
            },
        ),
    },
)

SALON_TESTIMONIAL_GROUP: dict = {
    "key": "ai-salon",
    "course_name": "AIオンラインサロン｜近日開始",
    "anchor_id": "voice-ai-salon",
    "heading": "情報に追われず、仕事で試す一歩が毎週決まった",
    "disclosure": "現在の仮運用で寄せられた内容をもとに、個人が特定されないよう表現を整えて掲載しています。",
    "testimonials": (
        {
            "title": "新機能を全部追わなくても、必要なことが分かった",
            "body": "AIの情報が多すぎて追い切れませんでしたが、自分の仕事に関係する変化だけを短く整理してもらえたので、焦らず判断できるようになりました。",
            "author_label": "仮運用参加者（匿名）",
        },
        {
            "title": "ほかの参加者の質問が、自分の仕事のヒントになった",
            "body": "業種の違う参加者の質問や改善例から、自分では気づかなかった使い方が見えました。その場で聞けるので、一人で調べ続ける時間も減りました。",
            "author_label": "仮運用参加者（匿名）",
        },
        {
            "title": "聞くだけの週でも、次に試すことが決まった",
            "body": "忙しい日はマイクを切って聞くだけで参加できました。最後に次の一歩が整理されるので、翌日から小さく試せて続けやすかったです。",
            "author_label": "仮運用参加者（匿名）",
        },
    ),
}


def _render_course_testimonials() -> str:
    parts = [
        "<section class='course-voices' id='course-voices' aria-labelledby='course-voices-title'>",
        "<div class='focus-section-head'><small>COURSE VOICES</small>",
        "<h2 id='course-voices-title'>受講された方の感想</h2></div>",
        "<p class='course-voices-disclosure'>実際に受講された方の感想を、個人が特定されないよう一部表現を整えて掲載しています。</p>",
        "<div class='course-voices-grid'>",
    ]
    for group in COURSE_TESTIMONIALS:
        course_name = html.escape(str(group["course_name"]))
        anchor_id = html.escape(str(group["anchor_id"]), quote=True)
        heading = html.escape(str(group["heading"]))
        parts.extend([
            f"<article class='course-voice-group' id='{anchor_id}'>",
            f"<p class='course-voice-course'>{course_name}</p>",
            f"<h3>{heading}</h3>",
            "<div class='course-voice-list'>",
        ])
        for testimonial in group["testimonials"]:
            title = html.escape(str(testimonial["title"]))
            body = html.escape(str(testimonial["body"]))
            author_label = html.escape(str(testimonial["author_label"]))
            parts.append(
                "<figure class='course-voice-card'>"
                f"<h4>{title}</h4>"
                f"<blockquote><p>「{body}」</p></blockquote>"
                f"<figcaption>— {author_label}</figcaption>"
                "</figure>"
            )
        parts.append("</div></article>")
    parts.append("</div></section>")
    return "".join(parts)


def _render_course_testimonial_details(course_key: str) -> str:
    """指定コースの実在する感想3件を、カード内の展開欄として描画する。"""
    group = next(
        item
        for item in COURSE_TESTIMONIALS + (SALON_TESTIMONIAL_GROUP,)
        if item["key"] == course_key
    )
    disclosure = html.escape(
        str(
            group.get(
                "disclosure",
                "実際に受講された方の感想を、個人が特定されないよう一部表現を整えて掲載しています。",
            )
        )
    )
    cards = "".join(
        "<figure class='compact-course-voice-card'>"
        f"<h4>{html.escape(str(testimonial['title']))}</h4>"
        f"<blockquote><p>「{html.escape(str(testimonial['body']))}」</p></blockquote>"
        f"<figcaption>— {html.escape(str(testimonial['author_label']))}</figcaption>"
        "</figure>"
        for testimonial in group["testimonials"]
    )
    return (
        "<details class='compact-course-details compact-course-testimonials' "
        f"id='{html.escape(str(group['anchor_id']), quote=True)}'>"
        "<summary>受講された方の感想を見る</summary>"
        "<div class='compact-course-testimonials-body'>"
        f"<h3>{html.escape(str(group['heading']))}</h3>"
        f"<p class='compact-course-testimonials-note'>{disclosure}</p>"
        f"<div class='compact-course-testimonials-list'>{cards}</div>"
        "</div></details>"
    )


def _render_compact_course_cards() -> str:
    """メイン講習を先頭にし、講習・相談の全コースを並べる申込カード。"""
    items = [
        {
            "cat": "基本講習",
            "title": "AIエージェント講習",
            "audience": "少数",
            "image": "/img/blog-ai-agent-course-section-2-20260714.webp",
            "image_alt": "AIエージェントと人が仕事を分担し、成果物を確認する流れ",
            "price": "5,500円",
            "duration": "120分",
            "desc": "Codexを初めて使う人の基本講習。仕事を1件に絞り、依頼、変更確認、修正、取り消し、次回手順まで実践します。",
            "url": AI_AGENT_COURSE_URL,
            "cta": "まずこの講習を予約",
            "material_url": "/lectures/2026-04-ai-kihon.html",
            "material_cta": "AIエージェント講習の受講資料を見る",
            "testimonial_key": "ai-agent",
            "details_lead": "この講習で得られること",
            "details": [
                ("実際の仕事を1つ完成へ", "告知文、資料、調査、集計、業務ツール、サイト改善など、今の課題を題材に使える成果物まで進めます。"),
                ("Codex初級をその場で実践", "作業用コピーを使い、目的、対象、完成形、守る条件を伝えて、1ファイル・1か所の小さな修正から始めます。"),
                ("結果を自分で確認できる", "根拠、差分、画面、誤りを確かめ、AIの答えをそのまま使わず判断する力を養います。"),
                ("修正の伝え方まで練習", "思った結果と違うときに、どこをどう直すかを具体的に伝え、完成度を上げます。"),
                ("次回も使える手順が残る", "うまくいった依頼文、確認項目、修正内容を保存し、一度きりで終わらない仕事の手順にします。"),
                ("参加方法", "予約ページから日時を選び、WindowsまたはMacのPCと、実際に進めたい資料や課題をお持ちください。対面・オンラインに対応します。"),
            ],
        },
        {
            "cat": "個別講習",
            "title": "AI自作講習",
            "audience": "個別",
            "image": "/img/course-path-coding.webp",
            "image_alt": "相談しながらAIアプリサイトを作り、確認して公開する様子",
            "price": "11,000円",
            "duration": "120分",
            "desc": "サイトやアプリを自分で作って直せるようになる。作りたいAIアプリサイトを題材に、公開できるまで個別に進めます。",
            "url": AI_APP_SELFBUILD_BOOK_URL,
            "cta": "AI自作講習を予約",
            "material_url": "/programming-map.html",
            "material_cta": "AIアプリサイト自作の受講資料を見る",
            "testimonial_key": "ai-app-selfbuild",
            "details_lead": "制作サービスと同じ流れを、自分で進める",
            "details": [
                ("課題と完成形を決める", "誰が、どの作業で、何ができれば完成かを整理し、最初に作る一機能へ絞ります。"),
                ("画面と機能を設計する", "入力、結果、ボタン、利用者の流れを並べ、AIに作らせる前の短い設計図を作ります。"),
                ("AIへ制作を依頼する", "目的、利用者、完成形、守る条件を整理し、CodexやClaude Codeへ伝わる依頼にします。"),
                ("変更を自分で確かめる", "差分、画面、リンク、入力、データを確認し、意図どおりの変更か判断します。"),
                ("直したい点をAIへ伝える", "表示や動きが違うときに、場所、期待する結果、守る条件を伝えて修正します。"),
                ("公開前の安全確認をする", "PC・スマホ表示、リンク、入力、エラー、秘密情報を確認し、公開してよい状態か判断します。"),
                ("本番へ公開する", "GitHubとクラウドへ反映し、本番URLで画面と機能が動くところまで個別に進めます。"),
                ("次も自分で直せる形に残す", "目的、依頼文、確認項目、設定、次の修正を保存し、受講後も続けられる資産にします。"),
                ("参加方法", "WindowsまたはMacのPCと、作りたいものや直したいページをお持ちください。対面・オンラインに対応します。"),
            ],
        },
        {
            "cat": "6ヶ月伴走",
            "title": "AI伴走支援",
            "audience": "組織",
            "image": "/img/course-path-workflow.webp",
            "image_alt": "複雑な業務をAIで整理し、続けられる仕組みに変える様子",
            "price": MONTHLY_SUPPORT_PRICE_LABEL,
            "duration": "6ヶ月",
            "desc": "組織がAIアプリサイトを自作・改善・運用できるまで学ぶ6ヶ月。",
            "url": MONTHLY_SUPPORT_BOOK_URL,
            "cta": "伴走支援を申し込む",
            "material_url": "/lectures/2026-06-ai-agent-rag-design.html",
            "material_cta": "AI導入・RAG設計の資料を見る",
            "testimonial_key": "ai-support",
            "details_lead": "上の制作代行を、組織の実践力へ変える",
            "details": [
                ("上のAIアプリサイト制作を自分たちの力へ", "制作サービスで行う課題整理、設計、AIへの制作依頼、確認、公開、改善を、組織の担当者と一緒に繰り返します。"),
                ("AIアプリサイトを一つ自作", "見積もり、問い合わせ、予約受付、社内検索などから優先度の高い機能を選び、自社の仕事で動く形まで作ります。"),
                ("小さく試して毎月改善", "最初から大きな仕組みにせず、現場で使い、反応と数字を見ながら無理なく育てます。"),
                ("社内に手順と資産が残る", "担当者が変わっても続けられるように、確認項目、運用ルール、資料、次回手順を整理します。"),
                ("経営者の作業時間を減らす", "毎回の告知、転記、集計、返信など、判断が不要な繰り返し作業を減らす仕組みを作ります。"),
                ("公開後まで一緒に確認", "PC・スマホ表示、申込導線、公開URLを確認し、作っただけで使われない状態を防ぎます。"),
                ("参加方法", "申込後に初回面談で対象業務、優先順位、6ヶ月の範囲と日程を確認してから開始します。"),
            ],
        },
    ]
    cards = []
    for item in items:
        is_ext = item["url"].startswith("http")
        target_attr = " target='_blank' rel='noopener'" if is_ext else ""
        material_url = str(item.get("material_url") or "")
        material_is_ext = material_url.startswith("http")
        material_target_attr = " target='_blank' rel='noopener'" if material_is_ext else ""
        material_html = (
            "<p class='compact-course-material-row'>"
            f"<a class='compact-course-material' href='{html.escape(material_url, quote=True)}'{material_target_attr}>"
            f"{html.escape(item['material_cta'])} →</a>"
            "</p>"
            if material_url else ""
        )
        audience_html = (
            f"<span class='offer-audience' aria-label='受講人数：{html.escape(item['audience'], quote=True)}'>"
            "<span class='offer-audience-label'>受講人数</span>"
            f"<strong>{html.escape(item['audience'])}</strong></span>"
        )
        title_html = (
            "<div class='compact-course-heading'>"
            f"<h3>{html.escape(item['title'])}</h3>{audience_html}</div>"
        )
        role_html = (
            "<div class='offer-role-row offer-role-row--course'>"
            "<div class='offer-role-copy'><span class='offer-role-badge'>学ぶ</span>"
            f"<span class='offer-role-note'>{html.escape(item['cat'])}</span></div></div>"
        )
        details = item.get("details") or []
        details_html = ""
        if details:
            details_lead = html.escape(str(item.get("details_lead") or "このコースで得られること"))
            detail_rows = "".join(
                "<li>"
                f"<strong>{html.escape(str(label))}</strong>"
                f"<span>{html.escape(str(description))}</span>"
                "</li>"
                for label, description in details
            )
            details_html = (
                "<details class='compact-course-details'>"
                "<summary>メリット・内容・参加方法を見る</summary>"
                f"<p class='compact-course-details-lead'>{details_lead}</p>"
                f"<ul>{detail_rows}</ul>"
                "</details>"
            )
        testimonial_html = _render_course_testimonial_details(str(item["testimonial_key"]))
        if item.get("post"):
            main_action_html = (
                f"<form class='compact-course-checkout' method='post' action='{html.escape(item['url'], quote=True)}'>"
                f"<button class='offer-action compact-course-action' type='submit'>{html.escape(item['cta'])} →</button></form>"
            )
        else:
            main_action_html = (
                f"<a class='offer-action compact-course-action' href='{html.escape(item['url'], quote=True)}'{target_attr}>{html.escape(item['cta'])} →</a>"
            )
        cards.append(
            "<article class='compact-course-card offer-card'>"
            f"{role_html}"
            f"<img class='compact-course-visual' src='{html.escape(item['image'], quote=True)}' alt='{html.escape(item['image_alt'], quote=True)}' loading='lazy' decoding='async'>"
            f"{title_html}"
            f"<div class='compact-course-meta'><strong>{html.escape(item['price'])}</strong><span>{html.escape(item['duration'])}</span></div>"
            f"<p>{html.escape(item['desc'])}</p>"
            f"{details_html}"
            f"{testimonial_html}"
            f"{main_action_html}"
            f"{material_html}"
            "</article>"
        )
    return "<div class='compact-course-grid'>" + "".join(cards) + "</div>"


def _render_live_talk_guide() -> str:
    """LINEライブトークへの参加方法を、短い図解と3手順で案内する。"""
    return (
        "<div class='salon-participation' aria-labelledby='salon-live-guide-title'>"
        "<figure class='salon-live-figure'>"
        "<img src='/img/ai-salon-live-talk-guide-20260722.svg' "
        "alt='LINEライブトークにリスナーとして参加し、話すときだけ挙手する流れ' "
        "width='640' height='480' loading='lazy' decoding='async'>"
        "<figcaption>マイクOFFで参加できます</figcaption>"
        "</figure>"
        "<div class='salon-live-guide-copy'>"
        "<span class='salon-live-badge'><i aria-hidden='true'></i>LINE LIVE TALK</span>"
        "<h3 id='salon-live-guide-title'>聞くだけOK。話すときだけ挙手</h3>"
        "<ol class='salon-live-steps'>"
        "<li><b>01</b><span><strong>Squareで月額決済</strong><small>月額2,200円・毎月自動更新</small></span></li>"
        "<li><b>02</b><span><strong>火曜21時に入室</strong><small>ライブトークを開く</small></span></li>"
        "<li><b>03</b><span><strong>聞くだけ／挙手</strong><small>話すときだけマイクON</small></span></li>"
        "</ol>"
        "<div class='salon-live-guide-foot'><span>マイクOFF・途中参加・途中退出OK</span>"
        "<span>決済確認後にLINE参加案内を表示</span></div>"
        "</div></div>"
    )


def _render_salon_menu() -> str:
    """上下に分かれていたサロン案内を、講習メニュー内の1パネルへ統合する。"""
    benefits = [
        ("AI情報を全部追わなくていい", "増え続ける新機能や発表から、地域事業や日々の仕事に関係する変化だけを短く整理します。"),
        ("今やる・待つを判断できる", "新しいから飛びつくのではなく、今すぐ試すもの、様子を見るもの、使わないものを実例で分けます。"),
        ("実際の仕事で確かめられる", "参加者の告知、資料、事務、Web改善などを題材に、AIへの依頼、確認、修正まで画面を見ながら進めます。"),
        ("ほかの人の事例も学びになる", "自分とは違う業種の困りごとや改善例から、自分の仕事へ応用できるヒントを持ち帰れます。"),
        ("その場で質問できる", "一人で調べ続けず、分からない点や導入の迷いを質問し、次に試す小さな一歩を決められます。"),
        ("忙しい週は聞くだけでOK", "LINEライブトークはマイクOFF、途中参加、途中退出に対応。発言したいときだけ挙手できます。"),
        ("終了後も要点を見返せる", "講師が内容を確認した「火曜AIノート」で、重要点と次の行動を振り返れます。"),
        ("参加方法", "Squareで月額2,200円を決済後、表示される招待URLからLINEへ進みます。毎週火曜21時の案内から参加できます。"),
    ]
    benefit_rows = "".join(
        "<li class='salon-benefit'>"
        f"<strong>{html.escape(title)}</strong>"
        f"<span>{html.escape(description)}</span>"
        "</li>"
        for title, description in benefits
    )
    return (
        "<section class='salon-section salon-section--integrated' id='seven-day-courses' aria-labelledby='salon-title'>"
        "<div class='salon-panel'>"
        "<div class='salon-eyebrow-row salon-card-eyebrow'><small>MENU 05 · SQUARE MONTHLY</small>"
        "<span class='compact-course-badge'><i aria-hidden='true'></i>現在は仮運用中</span></div>"
        "<div class='salon-intro salon-intro--fused salon-card-overview'>"
        "<figure class='salon-main-visual'><img src='/img/blog-ai-agent-course-section-4-20260714.webp' "
        "alt='毎週火曜にLINEライブトークでAIの今と次の一手を整理するオンラインサロン' "
        "loading='lazy' decoding='async'><figcaption>仕事で次に試すことを、一緒に決める60分</figcaption></figure>"
        "<div class='salon-intro-copy'>"
        "<small class='salon-card-category'>月額サロン</small>"
        "<h2 class='salon-detail-title' id='salon-title'>AIオンラインサロン｜近日開始</h2>"
        "<div class='compact-course-meta salon-card-meta'><strong>月額2,200円（税込）</strong><span>毎週火曜21:00</span></div>"
        "<p class='salon-intro-tagline'>AIの最新も疑問もその場で解決できる。</p>"
        "<p class='salon-intro-description'>正式開始に向けて現在は仮運用中です。登録中の方にはテスト運用へご協力いただいています。Squareで月額決済後、LINEライブトークの参加案内を表示します。</p></div>"
        "<div class='salon-value-list' role='list' aria-label='サロンで得られること'>"
        "<div class='salon-value' role='listitem'><b>01</b><div><small>UPDATE</small><strong>新機能を毎週知る</strong></div></div>"
        "<div class='salon-value' role='listitem'><b>02</b><div><small>BEST PRACTICE</small><strong>一流の活用事例を聞く</strong></div></div>"
        "<div class='salon-value' role='listitem'><b>03</b><div><small>NEXT ACTION</small><strong>次に試すことを決める</strong></div></div>"
        "</div></div>"
        "<details class='compact-course-details salon-all-details--complete' id='salon-details'><summary>メリット・内容・参加方法を見る</summary>"
        "<div class='salon-details-complete'>"
        "<div class='salon-facts' aria-label='開催情報'><div class='salon-fact'><small>WHEN</small><strong>火曜21:00</strong></div><div class='salon-fact'><small>PLACE</small><strong>LINEライブ</strong></div><div class='salon-fact'><small>FEE</small><strong>月2,200円</strong></div><div class='salon-fact'><small>STYLE</small><strong>聞くだけOK</strong></div></div>"
        "<p class='salon-benefits-title'>このサロンに参加するメリット</p><ul>"
        f"{benefit_rows}</ul>"
        f"{_render_live_talk_guide()}"
        "</div></details>"
        f"{_render_course_testimonial_details('ai-salon')}"
        "<p class='salon-simple-note'>月額2,200円（税込）・毎月自動更新。決済確認後にLINE参加案内を表示します</p>"
        f"<form class='compact-course-checkout salon-card-checkout' method='post' action='{html.escape(AI_SALON_CHECKOUT_URL, quote=True)}'><button type='submit'>Squareで決済して仮運用に参加 →</button></form>"
        "<p class='salon-material-row'><a class='compact-course-material salon-material-link' href='/lectures/2026-07-ai-online-salon-practice.html'>オンラインサロン受講資料を見る →</a></p>"
        "</div></section>"
    )


def _render_footer(today: str) -> str:
    """リッチフッター: 屋号+一言 / ナビ / NAP(ローカルSEOの住所明示) / CTA。"""
    year = today[:4]
    return (
        "<footer class='site-footer'>"
        "<div class='footer-grid'>"
        "<div class='footer-brand'>"
        "<div class='footer-logo'><span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>相</span></span><span class='wordmark'><span class='word-ai'>AI相談</span><span class='word-hub'>彦根</span><span class='word-en'>AI CONSULT</span></span></div>"
        "<p class='footer-tagline'>滋賀・彦根の中小事業者向けに、AI相談・AIエージェント講習・近日開始で現在仮運用中の月額2,200円AIオンラインサロン・受講資料・Web集客支援を行う"
        "資料センター型の相談サイト。増え続けるAI情報を、仕事で使える次の一手に変えます。</p>"
        "<a class='footer-cta' href='#contact'>AIアプリサイト自作を相談する</a>"
        "</div>"
        "<nav class='footer-nav' aria-label='フッターナビ'>"
        "<span class='footer-nav-head'>メニュー</span>"
        "<a href='#packages'>講習・相談</a>"
        "<a href='/ai-app-site/'>AIアプリサイト</a>"
        "<a href='#flow'>進め方</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='#lectures'>受講資料</a>"
        "<a href='#faq'>よくある質問</a>"
        "<a href='#seven-day-courses'>AIオンラインサロン</a>"
        "</nav>"
        "<div class='footer-nap'>"
        "<span class='footer-nav-head'>運営</span>"
        "<p>AI相談（彦根 / クライミングコンサル）</p>"
        "<p>代表 由井 辰美</p>"
        "<p>〒522-0043<br>滋賀県彦根市小泉町34-8<br>ビバシティ前</p>"
        f"<p><a href='mailto:{OWNER_EMAIL}'>{OWNER_EMAIL}</a></p>"
        "<p class='footer-area'>対応: 彦根・湖東・滋賀県全域 / 出張・オンライン全国</p>"
        "</div>"
        "</div>"
        f"<div class='footer-copy'>© {year} 由井 辰美 / AI相談 — 滋賀・彦根のAI相談・受講資料</div>"
        "</footer>"
    )


def _render_sticky_cta() -> str:
    """モバイルでスクロール後に現れる、自作講習・相談と基本講習の固定CTA。"""
    return (
        "<nav class='sticky-cta' id='sticky-cta' aria-label='AI自作講習とAIエージェント講習の固定CTA' aria-hidden='true'>"
        f"<a class='sticky-cta-btn sticky-cta-btn--consult' href='{AI_APP_SELFBUILD_BOOK_URL}' target='_blank' rel='noopener'><span>AI自作講習</span><small>120分・11,000円</small></a>"
        f"<a class='sticky-cta-btn sticky-cta-btn--agent' href='{AI_AGENT_COURSE_URL}' target='_blank' rel='noopener'><span>AIエージェント講習</span><small>120分・5,500円</small></a>"
        "</nav>"
    )


def _render_diagnose_modal() -> str:
    return (
        "<div class='diagnose-modal' id='diagnoseModal' role='dialog' aria-modal='true' aria-labelledby='diagnose-title'>"
        "<div class='diagnose-box'>"
        "<button type='button' class='diagnose-close' aria-label='閉じる'>&times;</button>"
        "<div class='diagnose-head' id='diagnose-title'>迷ったら60秒診断</div>"
        "<p class='diagnose-intro'>いまの仕事に合う入口を、3つの質問で整理します。</p>"
        "<div class='diagnose-body' aria-live='polite'></div>"
        "</div>"
        "</div>"
    )


def _render_explore() -> str:
    """メニュー集約: 受講資料 / ブログ をカードで（詳細は各ページへ）。
    ※ SNSポータル(AI Watch /watch/)は管理ページ(/admin)へ移行したため公開側には出さない。"""
    cards = [
        ("📚", "受講資料",
         "AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）の講習で使う資料。AIエージェント講習も。",
         "/lectures/index.html", "資料を見る"),
        ("📝", "ブログ",
         "相談、講習、SNS、AI活用の考え方をあとから見返せる記事として整理します。",
         "/blog/index.html", "ブログを見る"),
        ("📈", "自宅サーバー速度",
         "AI活用や業務アプリを支える回線速度を6時間ごとに記録し、成功も失敗も実測で公開します。",
         "/speed-monitor.html", "速度を見る"),
    ]
    parts = ["<div class='explore-grid'>"]
    for icon, title, desc, href, cta in cards:
        parts.append(
            f"<a class='explore-card fade-up' href='{html.escape(href, quote=True)}'>"
            f"<span class='explore-ico'>{icon}</span>"
            f"<h3 class='explore-title'>{html.escape(title)}</h3>"
            f"<p class='explore-desc'>{html.escape(desc)}</p>"
            f"<span class='explore-cta'>{html.escape(cta)} →</span>"
            f"</a>"
        )
    parts.append("</div>")
    return "".join(parts)


# AIアプリサイト自作講習・相談のSquare予約導線へ一本化。


def _render_contact_form() -> str:
    """申込導線は「AIアプリサイト自作講習・相談」に一本化。"""
    return (
        f"<a class='contact-primary fade-up' href='{AI_APP_SELFBUILD_BOOK_URL}' target='_blank' rel='noopener'>"
        "<span class='cp-ico'>📅</span>"
        "<span class='cp-body'>"
        "<span class='cp-title'>AIアプリサイト自作講習・相談を予約する</span>"
        "<span class='cp-desc'>作りたいものを持ち込み、相談、AIへの依頼、確認、修正、公開まで120分で個別に進めます。対面・オンラインに対応します。</span>"
        "</span>"
        "<span class='cp-cta'>日程を選ぶ →</span>"
        "</a>"
        "<p class='contact-sub-note fade-up'>"
        "どんなプランが合うか迷う方は、まず "
        "<button type='button' class='link-btn diagnose-open'>🔍 30秒AI診断</button>"
        " から。あなたに合うプランをご提案します。"
        "</p>"
    )

def _render_parallax_band() -> str:
    img = "https://images.unsplash.com/photo-1531973576160-7125cd663d86?auto=format&fit=crop&w=1600&q=70"
    return (
        "<div class='parallax-band'>"
        f"<div class='parallax-bg' style=\"background-image:url('{img}')\"></div>"
        "<div class='parallax-overlay'></div>"
        "<div class='parallax-content fade-up'>"
        "<p class='parallax-eyebrow'>LOCAL × AI</p>"
        "<h2 class='parallax-title'>彦根から、地域のビジネスを<br>ひとつ先のステージへ。</h2>"
        "<p class='parallax-sub'>ツールを売るのではなく、現場が回る「仕組み」を一緒に作る。地域の仲間とつながりながら。</p>"
        "<a class='btn btn-primary' href='#packages'>受講プランを見る →</a>"
        "</div>"
        "</div>"
    )


def _render_flow() -> str:
    steps = [
        ("① 無料相談", "彦根・湖東の仕事で困っていること、SNSで伸ばしたいこと、AIで試したいことを整理します。"),
        ("② 講習で一緒に触る", "ChatGPT / Codex / Claude Code / NotebookLM / 画像生成などを、画面を見ながら実際の仕事に当てはめます。"),
        ("③ 資料として残す", "受講で使った手順、プロンプト、動画、実例を資料センターに残し、あとから復習できるようにします。"),
        ("④ 集客へつなげる", "Reels、YouTube、ブログ、Googleビジネスプロフィール、LLMO向けFAQへ展開し、検索とAI回答に残します。"),
    ]
    parts = ["<div class='flow-list'>"]
    for title, body in steps:
        parts.append(
            f"<div class='flow-step'><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_growth_plan_section() -> str:
    """競合・国内トレンド・SNS反応から逆算した、デザイン育成ループ。"""
    rows = [
        ("公的DX相談・商工支援", "信頼は強いが、画面・成果物・講習後の復習導線が静的になりやすい", "毎朝の調査で、講座の入口・FAQ・資料リンクを最新の不安と需要に合わせて更新する"),
        ("一般パソコン教室", "初心者対応は強いが、AIエージェント、SNS反響、AI検索まで横断しにくい", "ChatGPT/Codex/Claude Code/画像生成/SNS/動画/LLMOを1つの操縦席で選べるデザインにする"),
        ("大手AI/DX研修", "体系化は強いが、受講者の持ち込み課題や地元商売への変換が弱くなりやすい", "彦根の現場感、少人数、即日成果物、予約導線を目立たせて「ここで動かせる」印象を作る"),
        ("制作会社・SEO会社", "制作やSEOは強いが、本人がAIを使えるようになる講習導線が薄い", "相談・講習・資料・予約を同じページに置き、内製化と外注の境目を選べる構造にする"),
    ]
    actions = [
        ("08:00 Research", "競合、国内Web/UIトレンド、AI講習の検索意図、YouTubeとSNS反響を確認する。"),
        ("Design Mutation", "ヒーロー画像、見出し、講習カード、FAQ、集客施策の見せ方を1回分だけ更新する。"),
        ("Function Gate", "予約リンク、受講資料、診断モーダル、管理導線、OGP、構造化データが壊れていないか確認する。"),
        ("Deploy & Verify", "ビルド後に本番へ反映し、公開URLで新しい文言・画像・主要リンクを検証する。"),
    ]
    parts = ["<div class='growth-layout'>"]
    parts.append("<div class='growth-panel fade-up'><h3>競合から見た勝ち筋</h3><div class='growth-table'>")
    for competitor, gap, move in rows:
        parts.append(
            "<div class='growth-row'>"
            f"<strong>{html.escape(competitor)}</strong>"
            f"<span>{html.escape(gap)}</span>"
            f"<em>{html.escape(move)}</em>"
            "</div>"
        )
    parts.append("</div></div>")
    parts.append("<div class='growth-panel growth-actions fade-up d2'><h3>毎日の育成ループ</h3>")
    for title, body in actions:
        parts.append(
            "<article class='growth-action'>"
            f"<b>{html.escape(title)}</b>"
            f"<p>{html.escape(body)}</p>"
            "</article>"
        )
    parts.append("</div></div>")
    return "".join(parts)


# 旧レイアウト用のFAQ素材。現在の集約トップでは、画面に出す質問だけを
# _render_focused_main で管理し、FAQPage構造化データは出力しない。
FAQ_QA = [
    ("彦根・滋賀でAIの講習や相談はできますか？",
     "はい。滋賀県彦根市を拠点に、彦根・湖東・東近江を中心とした対面のAI講習・個別相談を行っています。京都・大阪・名古屋までは出張可、リモートなら全国対応します。"),
    ("AIエージェント講習では何を学びますか？",
     "Codexで実際の仕事を1つ完成させる入門講習です。仕事を小さく分け、伝わる依頼を作り、変更点と画面を確認し、必要なら修正や取り消しを行い、成果物と次回手順を保存するところまで120分で通します。料金は5,500円で、専用の予約ページから申し込めます。"),
    ("AIオンラインサロンでは、何がわかりますか？",
     "AIオンラインサロンは近日開始で、現在は仮運用中です。登録中の方にはテスト運用へご協力いただいています。月額2,200円（税込）で、Square決済は毎月自動更新し、決済確認後にLINE参加案内を表示します。"),
    ("受講資料はあとから見返せますか？",
     "はい。受講で使った資料、プロンプト、実例、動画、スライドは資料センターとして整理し、あとから復習できるようにします。受講前に内容を確認したい方も、受講資料ページから雰囲気を見られます。"),
    ("Reels や YouTube の集客にも使えますか？",
     "使えます。1つの講習テーマから、Reels/Shorts用の短い台本、YouTubeタイトル・説明欄・チャプター、サイト内の動画専用ページ、FAQ、ブログ要約まで展開する流れを作ります。"),
    ("LLMO やAI検索に強いサイトにできますか？",
     "できます。地域名、講師の一次経験、料金、対応範囲、実例、FAQ、構造化データを整理し、AIが回答に引用しやすい形で公開します。大量の自動生成ではなく、講習と実例に基づく一次情報を重視します。"),
    ("料金はどれくらいですか？",
     f"AI無料相談の入口整理は無料、AIエージェント講習120分は5,500円、AIアプリサイト自作講習・相談120分は11,000円です。AI伴走支援 いっしょに導入は{MONTHLY_SUPPORT_PRICE_LABEL}×6ヶ月が目安で、既存のSquare予約ページから初回相談を申し込めます。"),
    ("補助金は使えますか？滋賀の事業者でも対象ですか？",
     "講習・伴走パックは「デジタル化・AI導入補助金」や滋賀県・彦根市の補助金の対象になります。補助率は小規模事業者で最大4/5、実質負担が1/3以下になるケースが多いです。申請からツール選定・実装・定着まで一気通貫で支援します。"),
    ("パソコンやスマホが苦手ですが、大丈夫ですか？",
     "大丈夫です。スマホで文字が打てれば始められます。専門用語は使わず、画面を一緒に見ながら進めます。「こんなことも聞いていいの？」というレベルから歓迎します。"),
    ("AI を仕事で使いたいのですが、何から始めれば？",
     "毎日やっている作業で「これ、同じような文章を毎回書いてるな」と思うものを1つ思い浮かべてください。問い合わせの返信・見積の文面・日報など、決まり文句の多い仕事から始めると、最初の相談でAIが役に立つのを実感できます。むずかしいことは後でOKです。"),
    ("特定の人しかできない仕事が多くて困っています。効きますか？",
     "そこが得意分野です。「あの人がいないと回らない」作業をAIと手順書に置き換え、誰でもできる形にします。たとえば請求書づくりが月8時間→1時間に減った例があります。"),
    ("出張やオンラインだけの依頼も可能ですか？",
     "可能です。滋賀県外への出張AI研修、オンライン完結の伴走、単発の講演・登壇いずれも対応します。まずは無料相談でご要望をお聞かせください。"),
]


# 旧レイアウト向けの補助データも、公開中の実際の感想から生成する。
# 表示文と構造化データの出典を COURSE_TESTIMONIALS に一本化し、仮の声が再表示されるのを防ぐ。
VOICES_ARE_SAMPLE = False
VOICES: list[dict] = [
    {
        "quote": testimonial["body"],
        "who": testimonial["author_label"],
        "before_after": testimonial["title"],
    }
    for group in COURSE_TESTIMONIALS
    for testimonial in group["testimonials"]
]


def _render_voices() -> str:
    if not VOICES:
        return ""
    parts = ["<div class='voices-grid'>"]
    for v in VOICES:
        quote = html.escape(str(v.get("quote") or ""))
        who = html.escape(str(v.get("who") or ""))
        ba = html.escape(str(v.get("before_after") or ""))
        ba_html = f"<span class='voice-ba'>{ba}</span>" if ba else ""
        parts.append(
            "<figure class='voice-card'>"
            f"<blockquote class='voice-quote'>「{quote}」</blockquote>"
            f"{ba_html}"
            f"<figcaption class='voice-who'>— {who}</figcaption>"
            "</figure>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_faq() -> str:
    qa = FAQ_QA
    parts = ["<div class='faq-list'>"]
    for q, a in qa:
        parts.append(
            f"<details class='faq-item'><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_speaker_section() -> str:
    """講師紹介の要約セクション。詳細は speaker.html へ誘導する。"""
    sp = _load_speaker()
    name = html.escape(sp.get("name") or OWNER_NAME)
    role = html.escape(sp.get("role") or "")
    role_html = f"<p class='speaker-modern-role'>{role}</p>" if role else ""
    highlights = [
        ("現場で使う", "AIを説明だけで終わらせず、返信文、資料、投稿、ページへ落とします。"),
        ("作って確認する", "CodexやClaude Codeで作り、差分と公開前チェックまで見ます。"),
        ("地域で続ける", "彦根・滋賀の事業者、学校、福祉、個人事業主の継続運用を支えます。"),
    ]
    highlight_html = "".join(
        "<div class='speaker-modern-point'>"
        f"<small>{html.escape(title)}</small>"
        f"<span>{html.escape(body)}</span>"
        "</div>"
        for title, body in highlights
    )

    parts = [
        "<div class='profile-block speaker-modern'>"
        "<div class='speaker-modern-copy'>"
        "<span class='speaker-modern-kicker'>TEACHER / OPERATOR</span>"
        f"<h3>{name}</h3>"
        f"{role_html}"
        "<p class='speaker-modern-lead'>AI講習、Web制作、ボルダリング指導、複数事業運営をつなぎ、現場で使える手順に変える講師です。</p>"
        f"<div class='speaker-modern-grid'>{highlight_html}</div>"
        "<div class='speaker-modern-actions'>"
        "<a class='btn btn-primary' href='/speaker.html'>詳しい講師紹介を見る</a>"
        "<a class='btn btn-secondary' href='#contact'>相談する</a>"
        "</div>"
        "</div>"
        + (
            f"<div class='speaker-art speaker-art-animated'>"
            f"<img src='{html.escape(sp.get('avatar_url') or '', quote=True)}' alt='{name} の講師写真' "
            f"loading='lazy' decoding='async'>"
            "</div>"
            if sp.get("avatar_url")
            # 画像未設定時は CSS アート（クライミング×テクノロジーの抽象ビジュアル）を表示
            else (
                "<div class='speaker-art speaker-art-ph' role='img' aria-label='講師ビジュアル（生成画像で差し替え予定）'>"
                "<div class='sa-grid'></div>"
                "<div class='sa-glow'></div>"
                "<div class='sa-mark'>由</div>"
                "<div class='sa-cap'><span class='sa-mono'>CLIMBER × CODER</span><br>クライミング歴30年 × 実装する経営者</div>"
                "</div>"
            )
        ) +
        "</div>"
    ]
    parts.append("</div>")
    return "".join(parts)

def _render_portfolio_section() -> str:
    """Retired public portfolio section. Kept as a no-op for older call sites."""
    return ""


# URLがある実績はサイト画面キャプチャを使う。URLがない場合だけカテゴリ別SVGをフォールバックにする。
# (絵柄, 上グラデ色1, 上グラデ色2) を category 文字列で引く。未知カテゴリは default。
_WORKS_THUMB = {
    "コミュニティ":        ("👥", "#2854C5", "#D95B43"),
    "店舗EC":              ("🛍️", "#0F8F72", "#D9852B"),
    "店舗LP":              ("✨", "#2854C5", "#0F8F72"),
    "商品LP":              ("📦", "#2BA7C8", "#7AA58A"),
    "生成LP":              ("⚡", "#D95B43", "#D9852B"),
    "企業サイト":          ("🏢", "#152032", "#0F8F72"),
    "動画アプリ":          ("🎬", "#2BA7C8", "#D9852B"),
    "マッチング":          ("🤝", "#2854C5", "#7AA58A"),
    "業務システム":        ("⚙️", "#152032", "#D95B43"),
    "ポートフォリオ":      ("🧭", "#2854C5", "#D9852B"),
    "インディーハッカーツール": ("🛠️", "#0F8F72", "#D9852B"),
}
_WORKS_THUMB_DEFAULT = ("🚀", "#2854C5", "#D95B43")


def _portfolio_thumb_url(thumbnail: str, url: str) -> str:
    thumbnail = (thumbnail or "").strip()
    if thumbnail:
        return thumbnail
    return ""


def _works_thumb_svg(category: str, name: str) -> str:
    icon, c1, c2 = _WORKS_THUMB.get(category, _WORKS_THUMB_DEFAULT)
    # gradient id を name から安全に生成（重複しても描画は問題ないが一応ユニーク化）
    gid = "g" + str(abs(hash((category, name))) % 100000)
    return (
        f"<span class='pf-thumb' aria-hidden='true'>"
        f"<svg viewBox='0 0 320 180' preserveAspectRatio='xMidYMid slice' xmlns='http://www.w3.org/2000/svg'>"
        f"<defs><linearGradient id='{gid}' x1='0' y1='0' x2='1' y2='1'>"
        f"<stop offset='0' stop-color='{c1}'/><stop offset='1' stop-color='{c2}'/></linearGradient></defs>"
        f"<rect width='320' height='180' fill='url(#{gid})'/>"
        # 軽い光のドット（装飾）
        f"<circle cx='270' cy='30' r='46' fill='#fff' opacity='0.10'/>"
        f"<circle cx='40' cy='152' r='34' fill='#fff' opacity='0.08'/>"
        f"<text x='160' y='108' font-size='54' text-anchor='middle'>{icon}</text>"
        f"</svg></span>"
    )


def _render_works_section() -> str:
    """公開済みの全実績をURLとサイト画面付きで表示する。"""
    items = [p for p in _load_portfolio() if str(p.get("status") or "") == "live"]
    if not items:
        return ""
    # 横スライド（カルーセル）。左右の矢印 + scroll-snap で見やすく。
    parts = [
        "<div class='pf-carousel-wrap'>"
        "<button type='button' class='pf-arrow pf-prev' aria-label='前へ' data-dir='-1'>‹</button>"
        "<div class='pf-carousel' id='works-carousel'>"
    ]
    for p in items:
        name_raw = str(p.get("name") or p.get("slug") or "")
        name = html.escape(name_raw)
        url = str(p.get("url") or "").strip()
        host = html.escape(url.replace("https://", "").replace("http://", "").rstrip("/")) if url else ""
        cat = html.escape(str(p.get("category") or ""))
        summary = html.escape(str(p.get("summary") or ""))
        status = str(p.get("status") or "live")
        techs = p.get("tech") or []
        chips = [f"<span class='pf-chip cat'>{cat}</span>"] if cat else []
        for t in list(techs)[:3]:
            chips.append(f"<span class='pf-chip'>{html.escape(str(t))}</span>")
        if status == "dev":
            chips.append("<span class='pf-chip dev'>開発中</span>")
        href = html.escape(url, quote=True) if url else "#flow"
        target = " target='_blank' rel='noopener'" if url else ""
        thumb_url = _portfolio_thumb_url(str(p.get("thumbnail") or ""), url)
        if thumb_url:
            thumb_alt = html.escape(f"{name_raw}のサイト画面", quote=True)
            thumb = (f"<span class='pf-thumb is-site-shot'>"
                     f"<img src='{html.escape(thumb_url, quote=True)}' alt='{thumb_alt}' loading='lazy' decoding='async' referrerpolicy='no-referrer' onerror=\"this.style.display='none'\"></span>")
        else:
            thumb = _works_thumb_svg(str(p.get("category") or ""), str(p.get("name") or ""))
        parts.append(
            f"<a class='pf-card' href='{href}'{target}>"
            + thumb
            + f"<div class='pf-title'>{name}</div>"
            + (f"<div class='pf-host'>{host}</div>" if host else "")
            + (f"<div class='pf-sum'>{summary}</div>" if summary else "")
            + (f"<div class='pf-meta'>{''.join(chips)}</div>" if chips else "")
            + "</a>"
        )
    parts.append("</div>")  # .pf-carousel
    parts.append("<button type='button' class='pf-arrow pf-next' aria-label='次へ' data-dir='1'>›</button>")
    parts.append("</div>")  # .pf-carousel-wrap
    return "".join(parts)


def _render_lectures_section() -> str:
    """公開中の受講資料をLPでもすべて見せる。"""
    pmap_card = {
        "title": "AIアプリサイト自作講習・相談 120分",
        "icon": "🧭",
        "date": "2026-06-06",
        "summary": "作りたいAIアプリサイトを題材に、相談、AIへの依頼、変更確認、修正、安全な公開までを順番に進める個別講習。",
        "category": "ai-build",
        "level": "実践",
        "duration": "120分",
        "route_label": "AIと作る",
        "image": "/img/course-path-coding.webp",
        "image_alt": "AIが変更したコードを人が確認し、AIアプリサイトを自作して公開する講習・相談",
        "href": "/programming-map.html",
    }
    all_lectures = list(_load_all_lectures())
    route_labels = {
        "ai-start": "AIが初めて",
        "ai-work": "自社資料を使う",
        "ai-build": "AIと作る",
        "ai-salon": "サロンで実践",
        "climbing": "AI資料作成例",
    }
    lecs: list[dict] = []
    pmap_added = False
    category_order = {category: index for index, category in enumerate(("ai-start", "ai-work", "ai-build", "ai-salon", "climbing"))}
    ordered_lectures = sorted(
        all_lectures,
        key=lambda item: (category_order.get(str(item.get("category") or ""), 99), int(item.get("order") or 999)),
    )
    for item in ordered_lectures:
        category = str(item.get("category") or "")
        if category == "ai-build" and not pmap_added:
            lecs.append(pmap_card)
            pmap_added = True
        lecs.append({**item, "route_label": route_labels.get(category, "受講資料")})
    if not pmap_added:
        lecs.append(pmap_card)
    parts: list[str] = [
        "<div class='pf-carousel-wrap lecture-carousel-wrap'>"
        "<button type='button' class='pf-arrow pf-prev' aria-label='前の受講資料へ' data-dir='-1'>‹</button>"
        "<div class='pf-carousel lecture-carousel' id='lecture-carousel' role='region' aria-label='受講資料カード' tabindex='0'>"
    ]
    for lec in lecs:
        parts.append(_render_lecture_card(lec))
    parts.append("</div>")  # .pf-carousel
    parts.append("<button type='button' class='pf-arrow pf-next' aria-label='次の受講資料へ' data-dir='1'>›</button>")
    parts.append("</div>")  # .pf-carousel-wrap
    return "".join(parts)


def _parse_md_frontmatter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    try:
        end = raw.index("\n---", 3)
    except ValueError:
        return {}, raw
    try:
        meta = yaml.safe_load(raw[3:end].strip()) or {}
    except Exception:
        meta = {}
    body = raw[end + 4:].lstrip("\n")
    return (meta if isinstance(meta, dict) else {}), body


def _first_markdown_image(body: str) -> str:
    for marker in ("<img src=\"", "<img src='"):
        start = body.find(marker)
        if start >= 0:
            quote = marker[-1]
            start += len(marker)
            end = body.find(quote, start)
            if end > start:
                return body[start:end].strip()
    return ""


def _plain_summary_from_body(body: str, limit: int = 128) -> str:
    for line in body.splitlines():
        text = line.strip()
        if not text:
            continue
        if text.startswith(("#", "<figure", "</figure", "<img", "<figcaption", "![", "- [")):
            continue
        return text[:limit] + ("…" if len(text) > limit else "")
    return ""


def _load_recent_blog_posts(limit: int = 3) -> list[dict]:
    if not BLOG_DIR.exists():
        return []
    items: list[dict] = []
    for f in sorted(BLOG_DIR.glob("*.md"), reverse=True):
        try:
            raw = f.read_text(encoding="utf-8")
        except Exception:
            continue
        meta, body = _parse_md_frontmatter(raw)
        title = str(meta.get("title") or f.stem)
        summary = str(meta.get("summary") or "").strip() or _plain_summary_from_body(body)
        items.append({
            "slug": f.stem,
            "title": title,
            "date": str(meta.get("date") or ""),
            "date_modified": str(meta.get("date_modified") or ""),
            "summary": summary,
            "image": str(meta.get("image") or "").strip() or _first_markdown_image(body),
            "href": f"/blog/{f.stem}.html",
        })
    items.sort(key=lambda item: effective_blog_date(item) or date.min, reverse=True)
    return items[:limit]


def _render_blog_card(post: dict, *, extra_class: str = "") -> str:
    title = html.escape(str(post.get("title") or "ブログ記事"))
    href = html.escape(str(post.get("href") or "/blog/index.html"), quote=True)
    date = html.escape(str(post.get("date") or ""))
    update_label = html.escape(blog_date_label(post))
    display_date = update_label if post.get("date_modified") else date
    fresh = is_new_blog(post)
    summary = html.escape(str(post.get("summary") or ""))
    image = str(post.get("image") or "").strip()
    cls = "blog-card" + (f" {extra_class}" if extra_class else "")
    media = ""
    if image:
        safe_image = html.escape(image, quote=True)
        media = f"<div class='blog-card-media'><img src='{safe_image}' alt='' loading='lazy' decoding='async'></div>"
    else:
        media = (
            "<div class='blog-card-media blog-card-media--line' aria-hidden='true'>"
            "<svg viewBox='0 0 320 180' role='img' focusable='false'>"
            "<path d='M38 112 C72 52 135 52 162 102 C188 151 248 146 286 82'/>"
            "<circle cx='84' cy='72' r='12'/><circle cx='164' cy='101' r='10'/><circle cx='245' cy='102' r='14'/>"
            "<path d='M58 129 l18 -11 l-3 22 Z M218 63 l22 -10 l-6 23 Z'/>"
            "</svg>"
            "</div>"
        )
    return (
        f"<a class='{cls}' href='{href}'>"
        f"{media}"
        "<div class='blog-card-body'>"
        f"<div class='blog-card-meta'><span>{display_date or 'BLOG'}</span></div>"
        "<div class='blog-card-title-row'>"
        f"<h3>{title}</h3>"
        + ("<span class='blog-new-badge'>NEW</span>" if fresh else "")
        + "</div>"
        + (f"<p>{summary}</p>" if summary else "")
        + "<span class='blog-card-more'>読む</span>"
        "</div>"
        "</a>"
    )


def _render_blog_teaser() -> str:
    posts = _load_recent_blog_posts(limit=6)
    if not posts:
        return ""
    cards = [_render_blog_card(post, extra_class="fade-up d2") for post in posts]
    if len(cards) == 1:
        cards.append(
            "<a class='blog-card fade-up d3' href='/blog/index.html'>"
            "<div class='blog-card-body'>"
            "<div class='blog-card-meta'><span>BLOG INDEX</span></div>"
            "<h3>ブログ一覧</h3>"
            "<p>AI相談の実践記録を一覧で確認できます。新しい記事を追加すると、このトップにも自動で並びます。</p>"
            "<span class='blog-card-more'>一覧を見る</span>"
            "</div>"
            "</a>"
        )
    return (
        "<section class='block' id='blog'>"
        "<p class='section-heading fade-up'>BLOG</p>"
        "<h2 class='section-title fade-up d1'>最近のブログ</h2>"
        "<div class='pf-carousel-wrap blog-carousel-wrap'>"
        "<button type='button' class='pf-arrow pf-prev' aria-label='前へ' data-dir='-1'>‹</button>"
        "<div class='pf-carousel blog-carousel' id='blog-carousel'>"
        + "".join(cards) +
        "</div>"
        "<button type='button' class='pf-arrow pf-next' aria-label='次へ' data-dir='1'>›</button>"
        "</div>"
        "</section>"
    )


def _business_compass_routes() -> list[dict]:
    return [
        {
            "kicker": "彦根・湖東の地域事業者",
            "title": "告知が苦手、予約や問い合わせが増えない",
            "pain": "忙しくて発信が後回し。何を直せば来店や相談につながるか分からない。",
            "route": "AI無料相談 -> HP/LP改善 -> SNS/ブログ再編集",
            "light": "投稿文作成 / 問い合わせ返信 / 予約導線の見直し",
            "decide": "直すページ、使う媒体、最初の投稿テーマ",
            "assets": "AI相談、N-デザイン、みんなのWA、グッぼる",
            "cta": "この悩みを無料相談で整理する",
        },
        {
            "kicker": "学校・福祉・支援者",
            "title": "AIを使いたいが、説明責任と安全面が不安",
            "pain": "便利そうでも、個人情報、教材化、職員への伝え方で止まりやすい。",
            "route": "初心者向け講習 -> 受講資料 -> 現場手順書",
            "light": "説明資料 / 職員向け手順 / 公開前確認",
            "decide": "同席者、本人同意、教材化する範囲",
            "assets": "AI相談、トラスト、受講資料、講師紹介",
            "cta": "学校・福祉の相談を整理する",
        },
        {
            "kicker": "店舗・EC・商品",
            "title": "商品や店の良さが、購入前に伝わりきらない",
            "pain": "写真、料金、比較、レビュー、買う理由がページ内で分断されている。",
            "route": "商品LP -> FAQ -> 購入/予約CTA -> 投稿素材化",
            "light": "商品説明 / FAQ / 比較表 / 予約CTA",
            "decide": "見せる商品、買う理由、公開前に確認する文言",
            "assets": "グッぼる、カラッと、Notエステ、プロギング",
            "cta": "商品・店舗ページを相談する",
        },
        {
            "kicker": "スポーツ・若手・習慣",
            "title": "続けたい人を、練習・回復・挑戦へ導きたい",
            "pain": "魅力はあるのに、初心者が次に何をすればよいか分かりにくい。",
            "route": "体験導線 -> 継続プラン -> 動画/記録 -> コミュニティ",
            "light": "体験案内 / 練習メモ / 動画説明 / 継続連絡",
            "decide": "初心者の入口、継続プラン、次に見る実例",
            "assets": "グッぼる、ClimbHero、スポーツ睡眠ラボ、HYROX",
            "cta": "体験・継続導線を相談する",
        },
        {
            "kicker": "業務アプリ・管理画面",
            "title": "事務作業が重く、特定の人しか回せない",
            "pain": "シフト、問い合わせ、記事作成、マッチング、報告が属人化している。",
            "route": "業務棚卸し -> 管理画面 -> AI下書き -> 確認フロー",
            "light": "シフト作成 / 問い合わせ下書き / 報告書下書き",
            "decide": "相談で済むか、講習か、制作か、管理画面化か",
            "assets": "トラスト、ビジネス21、リビルドマッチ、AI Hub管理",
            "cta": "業務改善を無料相談する",
        },
        {
            "kicker": "発信・YouTube・note",
            "title": "1つの実践知を、媒体ごとに使い回せていない",
            "pain": "動画、SNS、note、Webが別々になり、投稿後に問い合わせへ戻らない。",
            "route": "YouTube母材 -> Shorts/SNS3本 -> note -> Web/LINE/申込",
            "light": "動画台本 / 投稿文 / note構成 / 申込導線",
            "decide": "週テーマ、短尺化する素材、申込へ戻すURL",
            "assets": "AI相談ブログ、AI Watch、受講資料、SNS改善",
            "cta": "YouTube・note再編集を相談する",
        },
    ]


def _build_business_compass_jsonld() -> str:
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "全事業を悩みから選ぶ入口",
        "description": "彦根・滋賀の事業者、学校、福祉、店舗、スポーツ、発信の悩みからAI相談・講習・制作・業務改善へ進むための案内。",
        "itemListElement": [],
    }
    for idx, item in enumerate(_business_compass_routes(), start=1):
        item_list["itemListElement"].append({
            "@type": "ListItem",
            "position": idx,
            "item": {
                "@type": "Service",
                "name": item["title"],
                "audience": {
                    "@type": "Audience",
                    "audienceType": item["kicker"],
                },
                "areaServed": ["彦根", "湖東", "滋賀"],
                "description": item["pain"],
                "serviceType": item["route"],
                "provider": {
                    "@type": "LocalBusiness",
                    "name": "AI相談 彦根",
                    "url": SITE_URL,
                },
                "potentialAction": {
                    "@type": "ContactAction",
                    "name": item["cta"],
                    "target": f"{SITE_URL}/#contact",
                },
                "additionalProperty": [
                    {"@type": "PropertyValue", "name": "軽くなる作業", "value": item["light"]},
                    {"@type": "PropertyValue", "name": "相談で決めること", "value": item["decide"]},
                    {"@type": "PropertyValue", "name": "関連事業", "value": item["assets"]},
                ],
            },
        })
    return json.dumps(item_list, ensure_ascii=False)


def _render_business_compass() -> str:
    """Render a cross-business guide that routes common pains to the right offer."""
    assurances = [
        ("初回無料", "まず悩み、URL、困っている作業、使っているSNSだけ持参すれば相談できます。", "安心"),
        ("無理な営業なし", "無料相談 -> 選択肢提示 -> 持ち帰りOK -> 同意後に見積・実施の順で進めます。", "明確"),
        ("個人情報に配慮", "相談内容は課題整理と提案のみに使い、本人確認なく外部公開・教材化しません。", "保護"),
        ("学校・福祉も対応", "保護者・担当職員同席、本人同意、公開前確認を前提に進めます。", "配慮"),
    ]
    assurance_html = "".join(
        f"<li><b>{html.escape(name)}</b><span>{html.escape(label)}</span><em>{html.escape(text)}</em></li>"
        for name, text, label in assurances
    )
    card_html = []
    for item in _business_compass_routes():
        card_html.append(
            "<article class='business-compass-card fade-up'>"
            f"<span class='business-compass-kicker'>{html.escape(item['kicker'])}</span>"
            f"<h3>{html.escape(item['title'])}</h3>"
            f"<p>{html.escape(item['pain'])}</p>"
            "<ul class='business-compass-map'>"
            f"<li><b>軽くなる作業</b><span>{html.escape(item['light'])}</span></li>"
            f"<li><b>相談で決める</b><span>{html.escape(item['decide'])}</span></li>"
            f"<li><b>行動</b><span>{html.escape(item['route'])}</span></li>"
            f"<li><b>関連</b><span>{html.escape(item['assets'])}</span></li>"
            "</ul>"
            f"<a href='#contact'>{html.escape(item['cta'])}</a>"
            "</article>"
        )
    return (
        "<div class='business-compass'>"
        "<div class='business-compass-lead'>"
        "<div class='business-compass-copy fade-up'>"
        "<h3>彦根・湖東の小さな事業者も、悩みから選べる</h3>"
        "<p>全事業を一覧で見せるだけでは、初めての人は動けません。"
        "ここでは、時間がない、告知が苦手、AIが分からない、事務作業が重い、学び直しが不安という入口から、"
        "相談・講習・制作・業務アプリ・発信へ迷わず進めるように整理しています。</p>"
        "<p class='business-compass-decision'><b>迷ったら:</b> 相談=整理 / 講習=自分で使う / 制作=公開物を作る / "
        "業務アプリ=毎月の作業を減らす。2〜3分で日時を選べて、対面・Zoom・LINEから選べます。</p>"
        "<div class='business-compass-actions'>"
        "<a class='btn btn-primary' href='#contact'>AI無料相談を予約する</a>"
        "<a class='btn btn-secondary' href='#web-showcase'>HP制作の種類を見る</a>"
        "</div>"
        "<p class='business-compass-note'>相談前に不安が出やすい個人情報、未成年・高齢者・福祉利用者への配慮、"
        "安全面、苦情窓口、無理な営業をしない流れは、各事業のページへ横展開する前提で整理します。</p>"
        "</div>"
        "<aside class='agent-review-panel fade-up d2' aria-label='初めてでも安心な理由'>"
        "<h3>初めてでも安心な理由</h3>"
        f"<ul class='agent-review-list'>{assurance_html}</ul>"
        "</aside>"
        "</div>"
        f"<div class='business-compass-grid'>{''.join(card_html)}</div>"
        "<p class='business-compass-note fade-up d3'>この型は各事業で「誰向け・悩み・軽くなる業務・次の行動」として再利用します。"
        "公開やDB変更が必要な事業は、ビルド、差分確認、本番URL確認を通してから反映します。</p>"
        "</div>"
    )


def _render_profile() -> str:
    avatar = (_load_speaker() or {}).get("avatar_url") or ""
    if avatar:
        avatar_html = (
            f"<div class='profile-avatar'><img src='{html.escape(avatar, quote=True)}' "
            f"alt='{html.escape(OWNER_NAME)}' loading='lazy' decoding='async'></div>"
        )
    else:
        avatar_html = "<div class='profile-avatar'>🧗</div>"
    return (
        "<div class='profile-block'>"
        "<div>"
        f"<h3>{html.escape(OWNER_NAME)} / 由井（ゆい）</h3>"
        "<p>滋賀県を拠点に、クライミングジム『グッぼる』『カラッと』『ClimbHero』を運営しながら、"
        "建設・エステ・コンサル・LINE-CRM など合計 9 事業を回す経営者。</p>"
        "<p>サイトはすべて自分で Next.js + Supabase + Vercel で構築。デザイン・コード・運用まで現役で手を動かすため、"
        "「コンサルだけする人」ではなく「実際に経営している同業」として相談に乗ります。</p>"
        "<p style='font-weight:700;color:var(--text);'>「異端OK、数字根拠で経営を変える」</p>"
        "</div>"
        f"{avatar_html}"
        "</div>"
    )


def _render_biz_card(biz: dict, fade_class: str = "") -> str:
    status = biz.get("status", "live")
    url = biz.get("url") or ""
    is_self = bool(biz.get("self"))
    has_link = bool(url) and status not in ("coming_soon", "empty")

    color_key = biz.get("color", "blue")
    c_border, c_glow = COLOR_MAP.get(color_key, COLOR_MAP["blue"])

    icon = html.escape(str(biz.get("icon", "?")))
    name = html.escape(str(biz.get("name", "")))
    tagline = html.escape(str(biz.get("tagline", "")))
    desc = html.escape(str(biz.get("description", "")))
    image_url = biz.get("image") or ""

    status_label_map = {
        "live": "稼働中",
        "coming_soon": "準備中",
        "empty": "空き枠",
    }
    badge_class_map = {
        "live": "live",
        "coming_soon": "coming-soon",
        "empty": "empty",
    }

    if is_self:
        badge_html = "<span class='biz-badge self'>あなたはここ</span>"
    else:
        badge_text = html.escape(status_label_map.get(status, status))
        badge_cls = badge_class_map.get(status, "live")
        badge_html = f"<span class='biz-badge {badge_cls}'>{badge_text}</span>"

    card_extra = ""
    if is_self:
        card_extra += " self-card"
    if not has_link:
        card_extra += " no-link"
    if fade_class:
        card_extra += " " + fade_class

    image_html = ""
    if image_url:
        safe_img = html.escape(image_url, quote=True)
        image_html = (
            f"<div class='biz-card-image'>"
            f"<img src='{safe_img}' alt='{name}' loading='lazy' decoding='async'>"
            f"<span class='biz-card-image-icon'>{icon}</span>"
            f"</div>"
        )
        # 画像がある場合はカード内のアイコンを抑制
        icon_block = ""
    else:
        icon_block = f"<div class='biz-card-icon'>{icon}</div>"

    inner = (
        f"{image_html}"
        f"<div class='biz-card-body'>"
        f"{icon_block}"
        f"<div class='biz-card-name'>{name}</div>"
        f"<div class='biz-card-tagline'>{tagline}</div>"
        f"<div class='biz-card-desc'>{desc}</div>"
        f"<div class='biz-card-footer'>"
        f"{badge_html}"
        + (f"<span class='biz-arrow'>→</span>" if has_link else "")
        + "</div>"
        f"</div>"
    )

    # 白基調用に枠色を弱め、card-glow を hover ハイライト用に使う
    style = f"--card-border:{c_border};--card-glow:{c_glow};"

    if has_link:
        safe_url = html.escape(url, quote=True)
        return (
            f"<a class='biz-card{card_extra}' href='{safe_url}' target='_blank' rel='noopener' "
            f"style='{style}'>"
            f"{inner}</a>"
        )
    return f"<div class='biz-card{card_extra}' style='{style}'>{inner}</div>"


def _render_lecture_card(lec: dict) -> str:
    title = html.escape(lec.get("title") or lec.get("slug", ""))
    date = html.escape(lec.get("date", ""))
    summary = html.escape(lec.get("summary", ""))
    href_raw = lec.get("href") or f"/lectures/{lec.get('slug', '')}.html"
    href = html.escape(href_raw, quote=True)
    icon = html.escape(lec.get("icon", ""))
    image_path = str(lec.get("image") or "").strip()
    image_alt = html.escape(str(lec.get("image_alt") or lec.get("title") or ""), quote=True)
    route_label = html.escape(str(lec.get("route_label") or ""))
    level = html.escape(str(lec.get("level") or ""))
    duration = html.escape(str(lec.get("duration") or ""))
    icon_html = f"<span class='lecture-icon'>{icon}</span>" if icon else ""
    route_meta = route_label if route_label == "AI資料作成例" else (f"{route_label}向け" if route_label else "")
    duration_meta = f"目安 {duration}" if duration else ""
    meta_label = " · ".join(part for part in (route_meta, level, duration_meta) if part)
    if not meta_label and date:
        meta_label = f"📅 {date}"
    date_html = f"<div class='lecture-date'>{meta_label}</div>" if meta_label else ""
    summary_html = f"<div class='lecture-summary'>{summary}</div>" if summary else ""
    media_html = ""
    if image_path:
        media_html = (
            "<span class='lecture-card-media'>"
            f"<img src='{html.escape(image_path, quote=True)}' alt='{image_alt}' "
            "width='1200' height='630' loading='lazy' decoding='async'>"
            "</span>"
        )
    return (
        f"<a class='lecture-card' href='{href}'>"
        f"{media_html}<div class='lecture-card-body'>"
        f"<span class='lecture-title'>{icon_html}{title}</span>"
        f"{date_html}{summary_html}</div></a>"
    )


FOCUSED_PORTAL_CSS = r"""
/* ---- Consultation-first redesign, light editorial direction, 2026-07-22 ---- */
:root {
  /* Static values keep legacy/offline contrast tooling deterministic. */
  --focus-blue: #4261c7;
  --focus-lavender: #f1eeff;
  --focus-rose-soft: #fff0f3;
  --focus-muted: #606d83;
  --focus-surface: #f8fbff;
  /* Runtime values are rebound to the shared semantic design tokens. */
  --focus-blue: var(--ai-color-brand-600, #4261c7);
  --focus-blue-dark: var(--ai-color-brand-700, #3e58b8);
  --focus-cyan: var(--ai-color-brand-100, #e9efff);
  --focus-lavender: var(--ai-color-accent-soft, #f1eeff);
  --focus-violet: var(--ai-color-accent, #786bbd);
  --focus-rose: var(--ai-color-danger, #a23a4c);
  --focus-rose-soft: var(--ai-color-danger-soft, #fff0f3);
  --focus-ink: var(--ai-color-ink, #172033);
  --focus-muted: var(--ai-color-muted, #606d83);
  --focus-line: var(--ai-color-line, #dce4f2);
  --focus-line-strong: var(--ai-color-line-strong, #b9c7db);
  --focus-surface: var(--ai-color-canvas, #f8fbff);
  --focus-shell-x: max(18px, calc((100vw - 1400px) / 2));
  --focus-footer-y: clamp(36px, 5vw, 48px);
  --focus-footer-gap: clamp(24px, 3vw, 32px);
}
html { scroll-behavior: auto; }
body { background: #f8fbff !important; color: var(--focus-ink) !important; }
body::before { display: none !important; }
.container {
  max-width: none !important;
  padding: 74px 0 0 !important;
  overflow: hidden;
}
header.site-header,
header.site-header.scrolled,
header.site-header:hover {
  background: rgba(255,255,255,.97) !important;
  border: 0 !important;
  box-shadow: 0 8px 24px rgba(10,23,40,.045) !important;
}
.site-header-inner { max-width: 1400px !important; min-height: 74px; padding: 10px 18px !important; }
.site-logo { gap: 4px !important; }
.brand-mark { display: none !important; }
.wordmark { font-size: 23px !important; gap: 5px !important; }
.wordmark .word-ai { color: var(--focus-blue) !important; }
.wordmark .word-en, .site-logo-by { display: none !important; }
.site-nav { gap: 18px !important; background: transparent !important; border: 0 !important; box-shadow: none !important; }
.site-nav a.nav-link { padding: 10px 2px !important; color: var(--focus-ink) !important; background: transparent !important; border: 0 !important; font-size: 14px !important; }
.site-nav a.nav-link:hover { color: var(--focus-blue) !important; }
.site-nav a.nav-link.nav-essential[href],
.site-nav a.nav-link[href="/lectures/2026-04-ai-kihon.html"],
.site-nav .menu-toggle {
  padding: 10px 3px !important;
  color: var(--focus-ink) !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}
.site-nav a.nav-link.nav-essential[href]:hover,
.site-nav a.nav-link[href="/lectures/2026-04-ai-kihon.html"]:hover,
.site-nav .menu-toggle:hover {
  color: var(--focus-blue) !important;
  background: transparent !important;
}
.site-nav .nav-cta { background: var(--focus-blue) !important; background-image: none !important; border-radius: 8px !important; padding: 12px 20px !important; box-shadow: 0 10px 24px rgba(7,95,200,.18) !important; }
.header-member-login {
  min-height: 40px;
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  border: 1.5px solid var(--focus-blue);
  border-radius: 8px;
  background: #fff;
  color: var(--focus-blue);
  font-size: 13px;
  font-weight: 900;
  line-height: 1;
  text-decoration: none;
  white-space: nowrap;
  transition: background .2s, color .2s, transform .2s;
}
.header-member-login:hover,
.header-member-login:focus-visible {
  background: var(--focus-blue);
  color: #fff;
  outline: none;
  transform: translateY(-1px);
}
.focus-hero {
  --hero-x:.72;
  --hero-y:.28;
  position:relative;
  isolation:isolate;
  min-height:650px;
  overflow:hidden;
  background:
    linear-gradient(96deg,rgba(249,250,255,.99) 0%,rgba(249,250,255,.96) 46%,rgba(249,250,255,.68) 66%,rgba(249,250,255,.20) 100%),
    url('/img/hero-ai-consult-hikone.png') 66% center/cover no-repeat;
  background-color:#f6f7fc;
}
.focus-hero::before {
  content:"";
  position:absolute;
  inset:0;
  z-index:-2;
  background-image:linear-gradient(rgba(83,103,217,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(83,103,217,.055) 1px,transparent 1px);
  background-size:38px 38px;
  mask-image:linear-gradient(90deg,#000 0%,rgba(0,0,0,.5) 56%,transparent 100%);
}
.focus-hero::after {
  content:"";
  position:absolute;
  inset:auto -7% -32% auto;
  z-index:-1;
  width:min(860px,62vw);
  aspect-ratio:1;
  border-radius:50%;
  background:radial-gradient(circle,rgba(164,174,244,.32) 0%,rgba(164,174,244,.10) 44%,transparent 72%);
  opacity:.72;
  filter:blur(3px);
}
.hero-orb { position:absolute; z-index:-1; border-radius:50%; filter:blur(2px); pointer-events:none; }
.hero-orb-one { width:240px; height:240px; top:-90px; left:42%; background:rgba(83,103,217,.10); animation:hero-float 9s ease-in-out infinite; }
.hero-orb-two { width:160px; height:160px; right:5%; bottom:-55px; background:rgba(232,182,218,.16); animation:hero-float 11s ease-in-out -3s infinite reverse; }
@keyframes hero-float { 0%,100%{ transform:translate3d(0,0,0) } 50%{ transform:translate3d(18px,22px,0) } }
.focus-hero-shell { width:min(1400px,100%); min-height:650px; margin:0 auto; padding:68px 28px; display:grid; grid-template-columns:minmax(0,760px); justify-content:start; align-items:center; }
.focus-hero-copy { position:relative; z-index:1; min-width:0; display:flex; flex-direction:column; justify-content:center; }
.hero-salon-launch {
  width:min(590px,100%);
  min-height:64px;
  display:grid;
  grid-template-columns:auto 1fr auto;
  align-items:center;
  gap:13px;
  margin:0 0 25px;
  padding:10px 13px 10px 11px;
  color:var(--focus-ink);
  background:rgba(255,255,255,.84);
  border:1px solid rgba(7,95,200,.2);
  border-radius:16px;
  box-shadow:0 15px 42px rgba(10,62,112,.1);
  text-decoration:none;
  backdrop-filter:blur(16px);
  transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
}
.hero-salon-launch:hover,.hero-salon-launch:focus-visible { transform:translateY(-3px); border-color:var(--focus-blue); box-shadow:0 20px 50px rgba(7,95,200,.16); outline:none; }
.hero-salon-live { display:inline-flex; align-items:center; gap:6px; padding:7px 9px; color:#fff; background:#e2394f; border-radius:999px; font:900 10px/1 Inter,sans-serif; letter-spacing:.08em; }
.hero-salon-live i { width:7px; height:7px; border-radius:50%; background:#fff; box-shadow:0 0 0 0 rgba(255,255,255,.7); animation:hero-pulse 1.8s infinite; }
@keyframes hero-pulse { 70%{ box-shadow:0 0 0 7px rgba(255,255,255,0) } 100%{ box-shadow:0 0 0 0 rgba(255,255,255,0) } }
.hero-salon-copy { min-width:0; display:flex; flex-direction:column; gap:2px; }
.hero-salon-copy strong { font-size:15px; line-height:1.3; }
.hero-salon-copy small { color:var(--focus-muted); font-size:11px; font-weight:750; }
.hero-salon-launch > b { color:var(--focus-blue); font-size:12px; white-space:nowrap; }
.focus-kicker { margin:0 0 12px; color:var(--focus-blue); font:900 13px/1.4 Inter,'Noto Sans JP',sans-serif; letter-spacing:.09em; text-transform:uppercase; }
.focus-title { margin:0; max-width:680px; color:#050b14; font-size:clamp(48px,4.45vw,66px); line-height:1.06; letter-spacing:-.055em; }
.focus-title-first { display:inline-block; white-space:nowrap; }
.focus-title strong { color: var(--focus-blue); position: relative; white-space: nowrap; }
.focus-title-line { display:inline-block; white-space:nowrap; }
.focus-title strong::after { content:""; position:absolute; left:0; right:0; bottom:-7px; height:4px; background:var(--focus-blue); transform:rotate(-1.5deg); }
.focus-lead { max-width:600px; margin:27px 0 0; color:#24344a; font-size:clamp(16px,1.3vw,19px); line-height:1.85; font-weight:650; }
.focus-actions { display:flex; align-items:center; gap:13px; margin-top:30px; flex-wrap:wrap; }
.hero-diagnose-cta { display:flex; flex-direction:column; gap:6px; min-width:min(100%,310px); }
.hero-diagnose-eyebrow { color:var(--focus-blue); font-size:13px; font-weight:900; line-height:1.35; }
.hero-diagnose-cta small { color:var(--focus-muted); font-size:12px; font-weight:700; line-height:1.5; }
.hero-diagnose-button { cursor:pointer; }
.focus-btn { min-height: 54px; display: inline-flex; align-items: center; justify-content: center; padding: 0 28px; border-radius: 8px; border: 1.5px solid var(--focus-blue); font-weight: 900; text-decoration: none; transition: transform .2s, box-shadow .2s; }
.focus-btn:hover { transform: translateY(-2px); }
.focus-btn.primary { background: var(--focus-blue); color: #fff; box-shadow: 0 12px 28px rgba(7,95,200,.2); }
.focus-btn.secondary { background: #fff; color: var(--focus-blue); }
.hero-line-cta { gap:9px; }
.hero-text-link { display:inline-flex; align-items:center; gap:5px; padding:12px 3px; color:var(--focus-ink); font-size:13px; font-weight:900; text-decoration:none; border-bottom:1px solid rgba(7,95,200,.25); }
.hero-text-link:hover { color:var(--focus-blue); }
.focus-trust { display:flex; gap:16px; margin:22px 0 0; padding:0; list-style:none; color:var(--focus-muted); font-size:15px; font-weight:750; line-height:1.5; flex-wrap:wrap; }
.focus-trust li::before { content:"✓"; margin-right:6px; color:var(--focus-blue); font-weight:950; }
.focus-hero .focus-kicker { color:var(--focus-blue); }
.focus-hero .focus-title { color:var(--focus-ink); text-shadow:none; }
.focus-hero .focus-title strong { color:var(--focus-blue); }
.focus-hero .focus-title strong::after { background:#b9c3ff; }
.focus-hero .focus-lead { color:var(--focus-muted); text-shadow:none; }
.focus-hero .focus-btn.primary { color:#fff; background:var(--focus-blue); border-color:var(--focus-blue); box-shadow:0 14px 32px rgba(83,103,217,.22); }
.focus-hero .focus-btn.secondary { color:var(--focus-blue); background:rgba(255,255,255,.88); border-color:rgba(83,103,217,.36); }
.focus-hero .hero-text-link { color:var(--focus-ink); border-bottom-color:rgba(83,103,217,.32); }
.focus-hero .hero-text-link:hover { color:var(--focus-blue); }
.focus-hero .focus-trust { color:var(--focus-muted); }
.focus-hero .focus-trust li::before { color:var(--focus-blue); }
@media (prefers-reduced-motion:reduce) { .hero-orb,.hero-salon-live i { animation:none !important; } }
.hero-advantage {
  width:min(680px,100%);
  display:grid;
  grid-template-columns:clamp(124px,10.5vw,154px) minmax(0,1fr);
  grid-template-areas:"number copy" "number pillars";
  align-items:end;
  gap:11px 22px;
  margin:26px 0 0;
  padding:0;
  color:var(--focus-ink);
  background:none;
  border:0;
  border-radius:0;
  box-shadow:none;
  backdrop-filter:none;
}
.hero-advantage-number { grid-area:number; align-self:center; display:block; color:var(--focus-blue); }
.hero-advantage-number strong {
  display:block;
  width:max-content;
  color:var(--focus-blue);
  background:linear-gradient(135deg,var(--focus-blue) 8%,#7d8ff5 92%);
  background-clip:text;
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  filter:drop-shadow(0 8px 16px rgba(83,103,217,.16));
  font:900 clamp(78px,7.6vw,108px)/.74 Inter,sans-serif;
  letter-spacing:-.09em;
}
.hero-advantage-number span { display:block; margin-bottom:9px; padding:0; font-size:13px; font-weight:900; line-height:1.2; letter-spacing:.15em; white-space:nowrap; }
.hero-advantage-copy { grid-area:copy; min-width:0; }
.hero-advantage-copy small { display:flex; align-items:center; flex-wrap:wrap; gap:5px 8px; margin:0 0 7px; color:var(--focus-blue); font:900 13px/1.35 Inter,sans-serif; letter-spacing:.08em; }
.hero-advantage-copy small strong { display:inline-flex; align-items:center; min-height:22px; padding:3px 8px; color:var(--focus-blue); background:rgba(83,103,217,.09); border:1px solid rgba(83,103,217,.18); border-radius:999px; font:inherit; letter-spacing:.08em; }
.hero-advantage-copy small span { color:var(--focus-ink); letter-spacing:.03em; }
.hero-advantage-copy p { max-width:500px; display:flex; align-items:baseline; flex-wrap:wrap; gap:2px 8px; margin:0; font-size:clamp(22px,2.1vw,28px); font-weight:900; line-height:1.3; letter-spacing:-.04em; text-wrap:balance; }
.hero-advantage-equation { display:inline-flex; align-items:center; gap:7px; color:var(--focus-blue); font-size:1.12em; white-space:nowrap; }
.hero-advantage-equation strong { font-weight:950; }
.hero-advantage-equation span { color:#8996e9; font-size:.72em; font-weight:900; letter-spacing:0; }
.hero-advantage-outcome { color:var(--focus-ink); white-space:nowrap; }
.hero-advantage-pillars { grid-area:pillars; display:flex; flex-wrap:wrap; gap:0; margin:0; padding:0; list-style:none; }
.hero-advantage-pillars li { position:relative; padding:0 15px; color:var(--focus-ink); background:none; border:0; border-radius:0; font-size:14px; font-weight:850; line-height:1.45; white-space:nowrap; }
.hero-advantage-pillars li:first-child { padding-left:0; }
.hero-advantage-pillars li + li::before { content:"／"; position:absolute; left:-4px; color:rgba(83,103,217,.48); font-weight:500; }
.hero-advantage-pillars b { margin-right:5px; color:var(--focus-blue); }
@media (forced-colors:active) { .hero-advantage-number strong { background:none; -webkit-text-fill-color:currentColor; filter:none; } }
.focus-hub { padding:52px max(18px,calc((100vw - 1400px)/2)) 66px; background:#fff; border-top:1px solid var(--focus-line); }
.focus-hub-head { max-width:1400px; margin:0 auto 24px; display:flex; align-items:end; justify-content:space-between; gap:24px; }
.focus-hub-head small { color:var(--focus-blue); font-size:12px; font-weight:900; letter-spacing:.14em; }
.focus-hub-head h2 { margin:7px 0 0; font-size:clamp(28px,3vw,42px); letter-spacing:-.04em; }
.focus-hub-head p { max-width:520px; margin:0; color:var(--focus-muted); line-height:1.75; font-size:14px; }
.focus-hub-grid { max-width:1400px; margin:0 auto; display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; }
.focus-hub-card { position:relative; min-height:210px; display:flex; flex-direction:column; padding:24px; overflow:hidden; color:var(--focus-ink); text-decoration:none; background:var(--focus-surface); border:1px solid var(--focus-line); border-radius:14px; transition:transform .2s,border-color .2s,box-shadow .2s; }
.focus-hub-card::before { content:""; position:absolute; inset:0 auto 0 0; width:5px; background:var(--focus-blue); }
.focus-hub-card:hover { transform:translateY(-4px); border-color:var(--focus-blue); box-shadow:0 18px 42px rgba(10,40,80,.11); }
.focus-hub-card small { color:var(--focus-blue); font-size:11px; font-weight:900; letter-spacing:.11em; }
.focus-hub-card h3 { margin:16px 0 8px; font-size:23px; line-height:1.35; letter-spacing:-.025em; }
.focus-hub-card p { margin:0; color:var(--focus-muted); font-size:13px; line-height:1.7; }
.focus-hub-meta { display:flex; align-items:baseline; gap:7px; margin-top:auto; padding-top:18px; color:var(--focus-blue); }
.focus-hub-meta strong { font-size:28px; line-height:1; }
.focus-hub-meta span { font-size:12px; font-weight:800; }
.focus-outcomes { padding: 54px max(18px,calc((100vw - 1400px)/2)); background: linear-gradient(180deg,#d9efff,#edf8ff); }
.focus-section-head { max-width:1400px; margin:0 auto 30px; text-align:center; }
.focus-section-head small { display:block; color:var(--focus-blue); font-size:12px; font-weight:900; letter-spacing:.14em; }
.focus-section-head h2 { margin:8px 0 0; font-size:clamp(30px,3vw,46px); line-height:1.2; letter-spacing:-.04em; }
.outcome-grid { max-width:1400px; margin:auto; display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:18px; }
.outcome-item { min-height:210px; padding:24px; background:#fff; border:1px solid rgba(7,95,200,.18); border-radius:12px; box-shadow:0 14px 36px rgba(7,54,105,.08); }
.outcome-num { color:var(--focus-blue); font:900 12px/1 Inter,sans-serif; letter-spacing:.1em; }
.outcome-item h3 { margin:25px 0 10px; font-size:21px; }
.outcome-item p { margin:0; color:var(--focus-muted); line-height:1.7; font-size:14px; }
.focus-block { padding:72px max(18px,calc((100vw - 1400px)/2)); }
.focus-block.soft { background:var(--focus-surface); }
.focus-block.main-course {
  padding-top:64px;
  padding-bottom:64px;
  background:linear-gradient(145deg,#f4f3ff 0%,#fff 48%,#f5f7ff 100%);
  border-top:1px solid rgba(83,103,217,.14);
  border-bottom:1px solid rgba(83,103,217,.14);
}
.main-course .focus-section-head small {
  width:max-content;
  margin:0 auto;
  padding:7px 12px;
  color:#fff;
  background:var(--focus-blue);
  border-radius:999px;
}
.main-course > .focus-section-head { margin-bottom:18px; }
.main-course > .focus-section-lead { margin-bottom:20px; }
.compact-course-testimonials {
  margin-top:2px;
  scroll-margin-top:96px;
}
.compact-course-testimonials-body { padding:0 0 8px; }
.compact-course-testimonials-body h3 {
  margin:2px 0 7px;
  color:var(--focus-ink);
  font-size:16px;
  line-height:1.5;
}
.compact-course-testimonials-note {
  margin:0 0 10px !important;
  color:var(--focus-muted) !important;
  font-size:11px !important;
  line-height:1.6 !important;
}
.compact-course-testimonials-list {
  display:grid;
  gap:9px;
}
.compact-course-voice-card {
  margin:0;
  padding:12px;
  border:1px solid var(--focus-line);
  border-left:3px solid var(--focus-blue);
  border-radius:0 10px 10px 0;
  background:#fff;
}
.compact-course-voice-card h4 {
  margin:0 0 6px;
  color:var(--focus-blue-dark);
  font-size:13px;
  line-height:1.5;
}
.compact-course-voice-card blockquote { margin:0; }
.compact-course-voice-card p {
  margin:0 !important;
  color:var(--focus-ink) !important;
  font-size:12px !important;
  line-height:1.75 !important;
}
.compact-course-voice-card figcaption {
  margin-top:7px;
  color:var(--focus-ink);
  font-size:10px;
  font-weight:800;
}
.course-venue-common {
  max-width:860px;
  margin:24px auto 0;
  display:grid;
  grid-template-columns:128px minmax(0,1fr);
  align-items:center;
  gap:18px;
  padding:18px 0 0;
  border:0;
  border-top:1px solid rgba(7,95,200,.16);
  border-radius:0;
  background:transparent;
}
.course-venue-common img { display:block; width:100%; aspect-ratio:16/10; object-fit:cover; border-radius:8px; }
.course-venue-common small { display:block; color:var(--focus-blue); font-size:10px; font-weight:900; letter-spacing:.1em; }
.course-venue-common h3 { margin:4px 0 3px; color:var(--focus-ink); font-size:17px; line-height:1.4; }
.course-venue-common p { margin:0; color:var(--focus-muted); font-size:12px; line-height:1.6; }
.course-venue-map {
  grid-column:1 / -1;
  overflow:hidden;
  margin-top:2px;
  border:1px solid rgba(7,95,200,.16);
  border-radius:10px;
  background:#fff;
}
.course-venue-map iframe { display:block; width:100%; height:220px; border:0; }
.course-venue-map-link { grid-column:1 / -1; margin:-6px 0 0; text-align:center; }
.course-venue-map-link a { color:var(--focus-blue); font-size:12px; font-weight:900; text-underline-offset:3px; }
.compact-course-grid {
  max-width:1180px;
  margin:0 auto;
  padding:0 !important;
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  align-items:start;
  gap:14px;
  text-align:left;
}
.compact-course-card {
  grid-column:span 1;
  min-width:0;
  min-height:0;
  display:flex;
  flex-direction:column;
  padding:15px;
  background:rgba(255,255,255,.94);
  border:1px solid var(--focus-line);
  border-radius:16px;
  box-shadow:0 10px 28px rgba(42,53,105,.06);
}
.compact-course-badge {
  align-self:flex-start;
  display:inline-flex;
  align-items:center;
  gap:6px;
  margin:0 0 9px;
  padding:5px 9px;
  color:var(--focus-blue);
  background:#edf5ff;
  border:1px solid rgba(7,95,200,.18);
  border-radius:999px;
  font-size:10px;
  line-height:1.2;
  font-weight:900;
  letter-spacing:.04em;
}
.compact-course-badge i {
  width:7px;
  height:7px;
  border-radius:50%;
  background:#e2394f;
  box-shadow:0 0 0 4px rgba(226,57,79,.10);
}
.compact-course-title-row {
  display:flex;
  align-items:center;
  gap:6px;
  flex-wrap:nowrap;
  margin:7px 0 8px;
}
.compact-course-title-row .compact-course-badge {
  flex:0 0 auto;
  gap:3px;
  margin:0;
  padding:3px 4px;
  font-size:7.5px;
  white-space:nowrap;
}
.compact-course-title-row .compact-course-badge i { width:5px; height:5px; box-shadow:0 0 0 3px rgba(226,57,79,.10); }
.compact-course-card small { color:var(--focus-blue); font-size:10px; font-weight:900; letter-spacing:.08em; }
.compact-course-visual {
  display:block;
  width:100%;
  height:auto;
  aspect-ratio:16/9;
  margin:8px 0 9px;
  object-fit:cover;
  object-position:center;
  border-radius:10px;
  background:#eef1ff;
}
.compact-course-card h3 { margin:7px 0 8px; font-size:19px; line-height:1.3; letter-spacing:-.025em; }
.compact-course-heading {
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:8px;
  margin:7px 0 8px;
}
.compact-course-heading h3 { min-width:0; margin:0; }
.compact-course-card .compact-course-title-row h3 {
  flex:1 1 auto;
  min-width:0;
  margin:0;
  font-size:16px;
  line-height:1.25;
}
.compact-course-meta { display:flex; align-items:baseline; gap:8px; }
.compact-course-meta strong { color:var(--focus-ink); font-size:18px; }
.compact-course-meta span { color:var(--focus-muted); font-size:11px; font-weight:800; }
.compact-course-card p { margin:8px 0 9px; color:var(--focus-muted); font-size:12px; line-height:1.5; }
.compact-course-details {
  margin:0 0 8px;
  color:var(--focus-ink);
  font-size:11px;
}
.compact-course-details summary {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  padding:7px 0;
  color:var(--focus-blue);
  font-weight:900;
  cursor:pointer;
  list-style:none;
}
.compact-course-details summary::-webkit-details-marker { display:none; }
.compact-course-details summary::after {
  content:"+";
  flex:0 0 auto;
  font-size:17px;
  line-height:1;
  transition:transform .2s ease;
}
.compact-course-details[open] summary::after { transform:rotate(45deg); }
.compact-course-details-lead {
  margin:4px 0 10px !important;
  color:var(--focus-ink) !important;
  font-size:11px !important;
  font-weight:900;
  line-height:1.5 !important;
}
.compact-course-details ul {
  margin:3px 0 0;
  padding:0;
  display:grid;
  gap:8px;
  list-style:none;
}
.compact-course-details li {
  position:relative;
  display:grid;
  gap:1px;
  padding:0 0 0 18px;
}
.compact-course-details li::before {
  content:"✓";
  position:absolute;
  top:0;
  left:0;
  color:var(--focus-blue);
  font-size:11px;
  font-weight:1000;
}
.compact-course-details strong { color:var(--focus-ink); font-size:11px; }
.compact-course-details span { color:var(--focus-muted); font-size:10.5px; line-height:1.45; }
.compact-course-card > a { min-height:36px; display:flex; align-items:center; justify-content:center; margin-top:4px; padding:7px 10px; color:#fff; background:var(--focus-blue); border-radius:7px; font-size:12px; font-weight:900; text-align:center; text-decoration:none; }
.compact-course-card > a:hover { background:var(--focus-blue-dark); }
.compact-course-material-row { margin:7px 0 0; text-align:center; }
.compact-course-card .compact-course-material { display:inline; padding:0; color:var(--focus-blue); background:transparent; border-radius:0; font-size:11px; font-weight:800; line-height:1.5; text-decoration:underline; text-underline-offset:3px; }
.compact-course-card .compact-course-material:hover { color:var(--focus-blue-dark); background:transparent; }
.salon-section {
  position:relative;
  overflow:hidden;
  background:linear-gradient(145deg,#f4f1ff 0%,#fff 48%,#eef2ff 100%);
  border-top:1px solid rgba(83,103,217,.14);
  border-bottom:1px solid rgba(83,103,217,.14);
}
.salon-section::before {
  content:"";
  position:absolute;
  width:420px;
  aspect-ratio:1;
  left:-250px;
  top:130px;
  border-radius:50%;
  background:rgba(122,103,216,.08);
}
.salon-intro {
  position:relative;
  z-index:1;
  max-width:980px;
  margin:0 auto 24px;
  display:grid;
  grid-template-columns:minmax(0,1.08fr) minmax(300px,.92fr);
  grid-template-areas:
    "copy values"
    "facts facts";
  gap:34px;
  align-items:center;
  padding:30px;
  border:1px solid rgba(83,103,217,.20);
  border-radius:22px;
  background:linear-gradient(135deg,rgba(255,255,255,.97),rgba(245,248,255,.93));
  box-shadow:0 18px 54px rgba(38,54,112,.08);
}
.salon-intro-copy { grid-area:copy; }
.salon-intro-kicker {
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:7px 11px;
  color:var(--focus-blue);
  background:#edf5ff;
  border:1px solid rgba(7,95,200,.16);
  border-radius:999px;
  font:900 11px/1.2 Inter,"Noto Sans JP",sans-serif;
  letter-spacing:.04em;
}
.salon-intro-kicker i {
  width:8px;
  height:8px;
  border-radius:50%;
  background:#e2394f;
  box-shadow:0 0 0 5px rgba(226,57,79,.10);
}
.salon-intro h2 {
  margin:15px 0 0;
  color:var(--focus-ink);
  font-size:clamp(34px,4vw,52px);
  line-height:1.08;
  letter-spacing:-.055em;
}
.salon-intro-tagline {
  margin:13px 0 0;
  color:var(--focus-blue);
  font-size:clamp(18px,2vw,24px);
  line-height:1.4;
  font-weight:900;
  letter-spacing:-.025em;
}
.salon-value-list {
  grid-area:values;
  display:grid;
  gap:0;
  align-self:stretch;
  border-top:1px solid rgba(83,103,217,.16);
  border-bottom:1px solid rgba(83,103,217,.16);
}
.salon-value {
  display:grid;
  grid-template-columns:34px minmax(0,1fr);
  gap:12px;
  align-items:center;
  padding:13px 2px;
  border:0;
  border-radius:0;
  background:transparent;
}
.salon-value + .salon-value { border-top:1px solid rgba(83,103,217,.14); }
.salon-value > b {
  display:block;
  width:auto;
  height:auto;
  color:var(--focus-blue);
  background:transparent;
  border-radius:0;
  font:900 18px/1 Inter,sans-serif;
  letter-spacing:-.04em;
}
.salon-value small {
  display:block;
  margin-bottom:3px;
  color:var(--focus-blue);
  font:900 9px/1.2 Inter,sans-serif;
  letter-spacing:.11em;
}
.salon-value strong {
  display:block;
  color:var(--focus-ink);
  font-size:14px;
  line-height:1.35;
}
.salon-facts {
  grid-area:facts;
  width:100%;
  max-width:none;
  margin:-8px 0 0;
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:0;
  border-top:1px solid rgba(83,103,217,.18);
}
.salon-fact {
  padding:17px 18px 0;
  border:0;
  border-radius:0;
  background:transparent;
  text-align:left;
}
.salon-fact + .salon-fact { border-left:1px solid rgba(83,103,217,.14); }
.salon-fact small { display:block; color:var(--focus-muted); font-size:10px; font-weight:900; letter-spacing:.1em; }
.salon-fact strong { display:block; margin-top:5px; color:var(--focus-ink); font-size:15px; }
.salon-live-guide {
  position:relative;
  z-index:1;
  max-width:980px;
  margin:0 auto 34px;
  display:grid;
  grid-template-columns:minmax(280px,.86fr) minmax(0,1.14fr);
  gap:28px;
  align-items:center;
  padding:28px;
  border:1px solid rgba(83,103,217,.20);
  border-radius:20px;
  background:rgba(255,255,255,.90);
  box-shadow:0 18px 44px rgba(42,53,105,.09);
}
.salon-live-figure { margin:0; }
.salon-live-figure img {
  display:block;
  width:100%;
  height:auto;
  border-radius:16px;
  background:#eef3ff;
}
.salon-live-figure figcaption {
  margin-top:8px;
  color:var(--focus-muted);
  font-size:10px;
  line-height:1.5;
  text-align:center;
}
.salon-live-guide-copy { min-width:0; }
.salon-live-badge {
  display:inline-flex;
  align-items:center;
  gap:7px;
  margin-bottom:10px;
  color:var(--focus-blue);
  font:900 10px/1.2 Inter,sans-serif;
  letter-spacing:.11em;
}
.salon-live-badge i {
  width:8px;
  height:8px;
  border-radius:50%;
  background:#e2394f;
  box-shadow:0 0 0 5px rgba(226,57,79,.10);
}
.salon-live-guide h3 { margin:0; color:var(--focus-ink); font-size:clamp(20px,2vw,27px); line-height:1.35; }
.salon-live-guide-copy > p { margin:10px 0 0; color:var(--focus-muted); font-size:13px; line-height:1.75; }
.salon-live-benefits { display:flex; flex-wrap:wrap; gap:7px 14px; margin:12px 0 0; padding:0; list-style:none; }
.salon-live-benefits li { color:var(--focus-ink); font-size:11px; font-weight:850; }
.salon-live-benefits li::before { content:"✓"; margin-right:5px; color:var(--focus-blue); font-weight:950; }
.salon-live-steps { margin:18px 0 0; padding:0; display:grid; gap:9px; list-style:none; }
.salon-live-steps li {
  display:grid;
  grid-template-columns:38px minmax(0,1fr);
  gap:10px;
  align-items:start;
  padding:11px 12px;
  border:1px solid rgba(83,103,217,.13);
  border-radius:12px;
  background:#f8faff;
}
.salon-live-steps b {
  display:grid;
  place-items:center;
  width:38px;
  height:38px;
  color:#fff;
  background:var(--focus-blue);
  border-radius:11px;
  font:900 11px/1 Inter,sans-serif;
}
.salon-live-steps span { color:var(--focus-muted); font-size:11.5px; line-height:1.55; }
.salon-live-steps strong { display:block; margin:1px 0 2px; color:var(--focus-ink); font-size:13px; }
.salon-live-guide-foot { margin-top:13px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.salon-live-guide-foot span { color:var(--focus-ink); font-size:11px; font-weight:850; }
.salon-live-guide-foot a { color:var(--focus-blue); font-size:11px; font-weight:850; text-underline-offset:3px; }
.salon-note { max-width:880px; margin:20px auto 0; color:var(--focus-muted); font-size:12px; line-height:1.8; text-align:center; }
.salon-timeline-wrap {
  max-width:1180px !important;
  margin:0 auto !important;
  padding:0 48px 4px;
  overflow:visible;
}
.salon-timeline {
  display:grid !important;
  grid-auto-flow:column;
  grid-auto-columns:calc((100% - 36px)/3) !important;
  gap:18px !important;
  overflow-x:auto;
  scroll-snap-type:x mandatory;
  scroll-behavior:smooth;
  scrollbar-width:none;
  overscroll-behavior-inline:contain;
  -webkit-overflow-scrolling:touch;
  padding:8px 2px 20px;
}
.salon-timeline::-webkit-scrollbar { display:none; }
.salon-timeline-card,
.salon-timeline-card:first-child {
  grid-column:auto;
  min-height:338px;
  scroll-snap-align:start;
  scroll-snap-stop:always;
  padding:18px;
  overflow:hidden;
  border:1px solid var(--focus-line);
  border-radius:16px;
  background:#fff;
  box-shadow:0 12px 30px rgba(10,40,80,.07);
  opacity:1;
  transform:none;
  transition:opacity .24s ease,transform .24s ease,box-shadow .24s ease,border-color .24s ease;
}
.salon-timeline-card.is-active {
  border-color:rgba(83,103,217,.44);
  box-shadow:0 18px 42px rgba(63,79,171,.13);
  opacity:1;
  transform:none;
}
.salon-timeline-card-head { display:flex; align-items:center; justify-content:space-between; gap:14px; }
.salon-timeline-card-head span { color:var(--focus-ink); font-size:12px; font-weight:950; letter-spacing:.08em; }
.salon-timeline-card-head small { margin-left:auto; }
.salon-timeline-card .compact-course-visual { height:126px; }
.salon-timeline-card .compact-course-meta strong { font-size:25px; }
.salon-timeline-card .compact-course-meta span { padding:3px 8px; border-radius:999px; background:#eef7ff; color:var(--focus-blue); }
.salon-timeline-nav { display:flex; align-items:center; justify-content:center; gap:12px; min-height:26px; margin:2px auto 0; }
.salon-timeline-dots { display:flex; align-items:center; gap:7px; }
.salon-timeline-dots button { width:9px; height:9px; padding:0; border:0; border-radius:999px; background:#c7d7e8; cursor:pointer; transition:width .2s ease,background .2s ease; }
.salon-timeline-dots button[aria-current="step"] { width:26px; background:var(--focus-blue); }
.salon-timeline-status { min-width:34px; color:var(--focus-muted); font-size:11px; font-weight:850; }
.salon-timeline-wrap .pf-arrow { top:45%; }
.course-quick-actions { max-width:1400px; margin:12px auto 0; display:flex; align-items:center; justify-content:flex-end; gap:14px; }
.compact-diagnose { padding:0; color:var(--focus-blue); background:transparent; border:0; font-size:12px; font-weight:900; text-decoration:underline; text-underline-offset:3px; cursor:pointer; }
.course-quick-actions a { color:var(--focus-muted); font-size:12px; font-weight:800; }
.path-grid { max-width:1320px; margin:auto; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:24px; }
.path-card-new { display:flex; flex-direction:column; min-height:360px; padding:30px; border:1.5px solid var(--focus-line); border-radius:14px; background:#fff; text-decoration:none; color:inherit; transition:transform .2s,border-color .2s,box-shadow .2s; }
.path-card-new:hover { transform:translateY(-5px); border-color:var(--focus-blue); box-shadow:0 20px 50px rgba(10,40,80,.12); }
.path-card-visual { display:block; width:100%; aspect-ratio:4/3; margin:0 0 24px; border:1px solid rgba(7,95,200,.14); border-radius:10px; background:#fffaf0; object-fit:cover; }
.path-index { color:var(--focus-blue); font-size:34px; font-weight:900; letter-spacing:-.04em; }
.path-card-new h3 { margin:16px 0 10px; font-size:26px; }
.path-card-new p { margin:0; color:var(--focus-muted); line-height:1.75; }
.path-card-new ul { margin:22px 0 0; padding:0; list-style:none; display:grid; gap:10px; color:#24344a; font-size:14px; font-weight:700; }
.path-card-new li::before { content:"✓"; color:var(--focus-blue); margin-right:8px; }
.path-card-new span:last-child { margin-top:auto; padding-top:24px; color:var(--focus-blue); font-weight:900; }
.focus-proof-grid { max-width:1320px; margin:auto; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:24px; }
.focus-proof { overflow:hidden; border:1px solid var(--focus-line); border-radius:12px; background:#fff; }
.focus-proof img { width:100%; aspect-ratio:16/9; object-fit:cover; display:block; border-bottom:1px solid var(--focus-line); }
.focus-proof div { padding:22px; }
.focus-proof small { color:var(--focus-blue); font-weight:900; }
.focus-proof h3 { margin:7px 0 8px; font-size:22px; }
.focus-proof p { margin:0; color:var(--focus-muted); line-height:1.65; font-size:14px; }
.focus-split { max-width:1120px; margin:auto; display:grid; grid-template-columns:340px 1fr; gap:54px; align-items:center; }
.focus-split img { width:100%; border-radius:14px; object-fit:cover; aspect-ratio:4/3; }
.focus-split .speaker-painting { aspect-ratio:1/1; object-position:center; background:#fffaf0; box-shadow:0 18px 46px rgba(10,40,80,.10); }
.focus-split h2 { margin:0 0 18px; font-size:clamp(30px,3vw,46px); line-height:1.25; }
.focus-split p { color:var(--focus-muted); font-size:16px; line-height:1.9; }
.focus-flow { max-width:1100px; margin:auto; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:22px; }
.focus-step { position:relative; padding:14px 14px 24px; overflow:hidden; border:1px solid var(--focus-line); border-radius:14px; background:#fff; box-shadow:0 12px 30px rgba(10,40,80,.06); }
.focus-step-visual { display:block; width:100%; margin-bottom:18px; aspect-ratio:4/3; object-fit:cover; border-radius:9px; background:#f2f7fb; }
.focus-step b { color:var(--focus-blue); font-size:28px; }
.focus-step h3 { margin:8px 10px; font-size:21px; }
.focus-step b,.focus-step p { margin-left:10px; margin-right:10px; }
.focus-step p { margin-top:0; margin-bottom:0; color:var(--focus-muted); line-height:1.7; font-size:14px; }
.focus-faq { max-width:940px; margin:auto; }
.focus-faq details { border-bottom:1px solid var(--focus-line); padding:20px 0; }
.focus-faq summary { cursor:pointer; font-weight:850; font-size:16px; }
.focus-faq p { margin:12px 0 0; color:var(--focus-muted); line-height:1.8; }
.focus-contact { margin:0; padding:56px max(18px,calc((100vw - 1400px)/2)); background:var(--focus-blue); color:#fff; }
.focus-contact-inner { max-width:1100px; margin:auto; display:flex; align-items:center; justify-content:space-between; gap:36px; }
.focus-contact h2 { margin:0; font-size:clamp(28px,3vw,44px); }
.focus-contact p { margin:10px 0 0; color:rgba(255,255,255,.9); }
.focus-contact .focus-btn { background:#fff; color:var(--focus-blue); border-color:#fff; white-space:nowrap; }
.focus-resources { max-width:1100px; margin:30px auto 0; padding-top:24px; border-top:1px solid var(--focus-line); display:flex; gap:20px; flex-wrap:wrap; justify-content:center; }
.focus-resources a { color:var(--focus-muted); font-size:13px; font-weight:750; }
.focus-block[id] { scroll-margin-top:88px; }
.focus-section-lead { max-width:820px; margin:-12px auto 30px; color:var(--focus-muted); font-size:15px; line-height:1.85; text-align:center; }
.focus-content-shell { max-width:1400px; margin:0 auto; }
.focus-content-actions { display:flex; flex-wrap:wrap; justify-content:center; gap:12px; margin:28px auto 0; }
.focus-content-actions .focus-btn { min-height:48px; padding:0 22px; font-size:14px; }
.focus-block .pf-carousel-wrap,
.focus-block .lecture-grid { max-width:1400px; margin-left:auto; margin-right:auto; }
.focus-block .pf-card,
.focus-block .lecture-card,
.focus-block .blog-card { background:#fff !important; border:0 !important; box-shadow:0 9px 24px rgba(10,40,80,.065) !important; }
.focus-block .pf-card:hover,
.focus-block .lecture-card:hover,
.focus-block .blog-card:hover { border-color:transparent !important; box-shadow:0 16px 34px rgba(10,40,80,.11) !important; }
.focus-block .lecture-title { color:var(--focus-ink) !important; }
.focus-block .lecture-summary,
.focus-block .lecture-date,
.focus-block .pf-sum,
.focus-block .pf-host,
.focus-block .blog-card p { color:var(--focus-muted) !important; }
.focus-blog-carousel { max-width:1400px; margin:0 auto; }
.sticky-cta { background:#fff !important; color:var(--focus-ink) !important; border-color:var(--focus-line) !important; }
/* Standardized footer rhythm, 2026-07-22 */
footer.site-footer {
  margin-top:0;
  padding:var(--focus-footer-y) var(--focus-shell-x) calc(16px + env(safe-area-inset-bottom));
}
.footer-grid {
  width:100%;
  grid-template-columns:minmax(0,1.6fr) minmax(0,1fr) minmax(0,1.2fr);
  gap:var(--focus-footer-gap);
  margin-bottom:var(--focus-footer-gap);
}
.footer-grid > * { min-width:0; }
.footer-nap a { overflow-wrap:anywhere; color:var(--focus-blue-dark); }
@media (max-width: 900px) {
  .header-member-login {
    min-height: 36px;
    margin-left: auto;
    padding: 0 10px;
    font-size: 12px;
  }
  .mobile-toggle { flex: 0 0 auto; }
  .focus-hero { min-height:0; }
  .focus-hero::after { width:760px; right:-30%; bottom:-12%; }
  .focus-hero-shell { min-height:0; padding:54px 24px 62px; grid-template-columns:1fr; gap:42px; }
  .focus-hero-copy { width:100%; max-width:760px; padding:0; }
  .focus-title { font-size:clamp(42px,10.5vw,62px); }
  .outcome-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .path-grid,.focus-proof-grid { grid-template-columns:1fr; max-width:680px; }
  .focus-split { grid-template-columns:1fr; max-width:680px; }
  .focus-split img { max-width:360px; }
  .course-venue-common,.compact-course-grid,.course-quick-actions { max-width:680px; }
  .compact-course-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .compact-course-card { grid-column:span 1; }
  .salon-timeline-wrap { max-width:680px !important; }
  .salon-timeline { grid-auto-columns:76% !important; }
  .focus-hub-head { align-items:flex-start; flex-direction:column; }
  .focus-hub-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .footer-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .footer-brand { grid-column:1 / -1; }
  .footer-tagline { max-width:620px; }
}
@media (max-width: 760px) {
  .salon-intro {
    grid-template-columns:1fr;
    grid-template-areas:"copy" "values" "facts";
    gap:18px;
  }
}
@media (max-width: 680px) {
  :root {
    --focus-shell-x:14px;
    --focus-footer-y:36px;
    --focus-footer-gap:24px;
  }
  .container { padding:64px 0 0 !important; }
  .site-header-inner { min-height:64px; padding:8px 14px !important; gap:8px !important; }
  .wordmark { font-size:19px !important; }
  .focus-hero::before { mask-image:linear-gradient(180deg,#000 0%,transparent 90%); }
  .focus-hero {
    background:
      linear-gradient(180deg,rgba(249,250,255,.98) 0%,rgba(249,250,255,.94) 58%,rgba(249,250,255,.90) 100%),
      url('/img/hero-ai-consult-hikone.png') 64% center/cover no-repeat;
  }
  .focus-hero::after { width:520px; right:-55%; bottom:8%; opacity:.45; }
  .focus-hero-shell { padding:28px 14px 46px; gap:28px; }
  .focus-hero-copy { padding:0; }
  .hero-salon-launch { grid-template-columns:auto 1fr; gap:9px; margin-bottom:24px; border-radius:13px; }
  .hero-salon-launch > b { grid-column:2; margin-top:-2px; }
  .hero-salon-copy strong { font-size:13px; }
  .hero-salon-copy small { font-size:10px; }
  .focus-kicker { font-size:11px; }
  .focus-title { font-size:clamp(32px,9.7vw,44px); }
  .focus-title-line { white-space:normal; }
  .footer-grid { grid-template-columns:1fr; }
  .footer-brand { grid-column:auto; }
  .focus-title strong { white-space:normal; }
  .focus-actions { display:grid; grid-template-columns:1fr; }
  .hero-diagnose-cta { width:100%; }
  .hero-diagnose-cta .focus-btn { width:100%; }
  .focus-btn { width:100%; }
  .hero-text-link { width:max-content; justify-self:center; }
  .focus-trust { gap:8px 12px; margin-top:18px; font-size:14px; line-height:1.5; }
  .focus-outcomes,.focus-block,.focus-hub { padding:48px 14px; }
  .hero-advantage { grid-template-columns:clamp(108px,27vw,140px) minmax(0,1fr); grid-template-areas:"number copy" "pillars pillars"; gap:12px; margin-top:20px; padding:0; }
  .hero-advantage-number { display:block; }
  .hero-advantage-number strong { display:block; font-size:clamp(72px,18.5vw,90px); }
  .hero-advantage-number span { display:block; margin-bottom:7px; padding:0; font-size:12px; line-height:1.2; }
  .hero-advantage-copy small { gap:4px 6px; margin-bottom:5px; font-size:11px; line-height:1.3; }
  .hero-advantage-copy small strong { min-height:22px; padding:3px 7px; }
  .hero-advantage-copy p { display:block; font-size:clamp(18px,4.8vw,20px); line-height:1.35; }
  .hero-advantage-copy p > span { display:block; }
  .hero-advantage-equation { margin-bottom:2px; font-size:1.12em; }
  .hero-advantage-equation span { display:inline; }
  .hero-advantage-outcome { white-space:normal; }
  .hero-advantage-pillars { grid-column:1 / -1; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); padding:0; }
  .hero-advantage-pillars li { min-width:0; padding:0 2px; font-size:12px; line-height:1.45; text-align:center; }
  .hero-advantage-pillars li + li::before { left:-4px; }
  .focus-hub-grid { grid-template-columns:1fr; }
  .focus-hub-card { min-height:180px; }
  .outcome-grid { grid-template-columns:1fr; }
  .outcome-item { min-height:0; }
  .focus-flow { grid-template-columns:1fr; }
  .focus-step { padding:12px 12px 22px; }
  .focus-contact-inner { align-items:flex-start; flex-direction:column; }
  .focus-contact .focus-btn { width:100%; }
  .focus-section-lead { margin-top:-14px; font-size:14px; text-align:left; }
  .main-course { padding-top:40px !important; padding-bottom:42px !important; }
  .course-venue-common { grid-template-columns:72px minmax(0,1fr); gap:10px; margin-top:22px; padding:14px 0 0; }
  .course-venue-common h3 { font-size:14px; }
  .course-venue-common p { font-size:11px; }
  .course-venue-map { margin-top:4px; }
  .course-venue-map iframe { height:220px; }
  .compact-course-grid { grid-template-columns:1fr; gap:12px; }
  .compact-course-card { grid-column:auto; min-height:0; padding:17px; border:1px solid var(--focus-line); border-radius:14px; }
  .compact-course-visual { height:auto; }
  .compact-course-card h3 { font-size:18px; }
  .compact-course-title-row { gap:7px; }
  .compact-course-card .compact-course-title-row h3 { font-size:18px; }
  .compact-course-title-row .compact-course-badge { padding:4px 8px; font-size:9px; }
  .salon-intro {
    grid-template-columns:1fr;
    grid-template-areas:"copy" "values" "facts";
    gap:18px;
    margin-bottom:18px;
    padding:16px;
    border-radius:16px;
  }
  .salon-intro-kicker { padding:6px 9px; font-size:10px; }
  .salon-intro h2 { margin-top:10px; font-size:29px; }
  .salon-intro-tagline { margin-top:8px; font-size:17px; }
  .salon-value-list { gap:0; overflow:visible; border-width:1px 0; border-radius:0; background:transparent; }
  .salon-value { grid-template-columns:28px minmax(0,1fr); gap:8px; padding:10px 2px; border:0; border-radius:0; background:transparent; }
  .salon-value + .salon-value { border-top:1px solid rgba(83,103,217,.14); }
  .salon-value > b { width:auto; height:auto; border-radius:0; font-size:15px; }
  .salon-value small { display:inline; margin:0 6px 0 0; font-size:7.5px; letter-spacing:.06em; }
  .salon-value strong { display:inline; font-size:12.5px; line-height:1.3; }
  .salon-timeline-wrap { width:100%; padding:0; }
  .salon-timeline { grid-auto-columns:88% !important; gap:12px !important; padding:6px 1px 16px; }
  .salon-timeline-card,
  .salon-timeline-card:first-child { min-height:342px; padding:16px; border:1px solid var(--focus-line); border-radius:14px; }
  .salon-timeline-card .compact-course-visual { height:128px; }
  .salon-timeline-nav { justify-content:flex-start; flex-wrap:wrap; gap:9px; }
  .salon-facts { grid-template-columns:repeat(2,minmax(0,1fr)); gap:0; margin:0; }
  .salon-fact { padding:12px 10px 4px 2px; }
  .salon-fact + .salon-fact { border-left:0; }
  .salon-fact:nth-child(even) { padding-left:12px; border-left:1px solid rgba(83,103,217,.14); }
  .salon-fact:nth-child(n+3) { margin-top:10px; padding-top:12px; border-top:1px solid rgba(83,103,217,.14); }
  .salon-fact:nth-child(2) strong { font-size:12px; white-space:nowrap; }
  .salon-live-guide { grid-template-columns:1fr; gap:18px; padding:17px; border-radius:16px; }
  .salon-live-figure { width:min(100%,420px); margin:0 auto; }
  .salon-live-guide h3 { font-size:20px; }
  .salon-live-guide-copy > p { font-size:12px; }
  .salon-live-steps li { padding:10px; }
  .salon-live-guide-foot { align-items:flex-start; flex-direction:column; gap:6px; }
  .salon-note { text-align:left; }
  .course-quick-actions { align-items:flex-end; justify-content:space-between; }
}

/* ---- Compact, payment-gated AI salon panel, 2026-07-25 ---- */
.compact-course-checkout {
  width:100%;
  margin-top:auto;
}
.compact-course-checkout button {
  width:100%;
  min-height:var(--ai-size-tap,44px);
  padding:7px 10px;
  color:#fff;
  background:var(--focus-blue);
  border:0;
  border-radius:7px;
  font:900 12px/1.4 Inter,"Noto Sans JP",sans-serif;
  text-align:center;
  cursor:pointer;
}
.compact-course-checkout button:hover,
.compact-course-checkout button:focus-visible {
  background:var(--focus-blue-dark);
  outline:3px solid rgba(83,103,217,.18);
  outline-offset:2px;
}
.salon-section {
  padding:32px 18px !important;
  background:#f7f8fc;
}
.salon-section::before {
  display:none;
}
.salon-panel {
  position:relative;
  z-index:1;
  max-width:1040px;
  margin:0 auto;
  padding:20px 22px 18px;
  border:1px solid rgba(83,103,217,.16);
  border-radius:18px;
  background:#fff;
  box-shadow:0 12px 36px rgba(38,54,112,.07);
}
.salon-panel .salon-intro {
  max-width:none;
  margin:0;
  padding:0;
  grid-template-columns:minmax(0,1.15fr) minmax(320px,.85fr);
  grid-template-areas:"copy values";
  gap:18px;
  border:0;
  border-radius:0;
  background:transparent;
  box-shadow:none;
}
.salon-panel .salon-intro h2 {
  margin-top:10px;
  font-size:clamp(30px,3.2vw,40px);
}
.salon-panel .salon-intro-tagline {
  margin-top:8px;
  font-size:clamp(17px,1.8vw,21px);
}
.salon-panel .salon-value-list {
  display:grid;
  grid-template-columns:1fr;
  gap:0;
  align-self:center;
  border-width:1px 0;
  border-style:solid;
  border-color:rgba(83,103,217,.14);
}
.salon-panel .salon-value {
  grid-template-columns:28px minmax(0,1fr);
  gap:8px;
  padding:7px 0;
  border:0;
  border-radius:0;
  background:transparent;
}
.salon-panel .salon-value + .salon-value { border-top:1px solid rgba(83,103,217,.12); }
.salon-panel .salon-value > b { font-size:14px; }
.salon-panel .salon-value small {
  display:inline;
  margin:0 6px 0 0;
  font-size:9px;
}
.salon-panel .salon-value strong {
  display:inline;
  font-size:12.5px;
}
.salon-panel .salon-facts {
  width:100%;
  margin:12px 0 0;
  grid-template-columns:repeat(4,minmax(0,1fr));
  overflow:hidden;
  border-width:1px 0;
  border-style:solid;
  border-color:rgba(83,103,217,.15);
  border-radius:0;
  background:transparent;
}
.salon-panel .salon-fact {
  padding:7px 10px;
  text-align:center;
}
.salon-panel .salon-fact + .salon-fact { border-left:1px solid rgba(83,103,217,.13); }
.salon-panel .salon-fact small { font-size:9px; }
.salon-panel .salon-fact strong {
  margin-top:3px;
  font-size:13px;
  white-space:nowrap;
}
.salon-participation {
  margin-top:12px;
  display:grid;
  grid-template-columns:146px minmax(0,1fr);
  gap:14px;
  align-items:center;
  padding:11px 13px;
  border:1px solid rgba(83,103,217,.12);
  border-radius:12px;
  background:#fbfcff;
}
.salon-participation .salon-live-figure { margin:0; }
.salon-participation .salon-live-figure img {
  width:100%;
  aspect-ratio:4/3;
  object-fit:contain;
  border-radius:11px;
}
.salon-participation .salon-live-figure figcaption {
  margin-top:4px;
  font-size:9.5px;
}
.salon-participation .salon-live-badge {
  margin-bottom:5px;
  font-size:9.5px;
}
.salon-participation h3 {
  margin:0;
  color:var(--focus-ink);
  font-size:18px;
  line-height:1.35;
}
.salon-participation .salon-live-steps {
  margin:7px 0 0;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:5px;
}
.salon-participation .salon-live-steps li {
  grid-template-columns:26px minmax(0,1fr);
  gap:6px;
  align-items:center;
  min-width:0;
  padding:5px 6px;
  border:0;
  border-left:2px solid rgba(83,103,217,.22);
  border-radius:0;
  background:transparent;
}
.salon-participation .salon-live-steps b {
  width:26px;
  height:26px;
  border-radius:8px;
  font-size:10px;
}
.salon-participation .salon-live-steps strong {
  margin:0;
  font-size:11px;
  line-height:1.25;
}
.salon-participation .salon-live-steps small {
  display:block;
  margin-top:2px;
  color:var(--focus-muted);
  font-size:9.5px;
  line-height:1.25;
}
.salon-participation .salon-live-guide-foot {
  margin-top:8px;
  gap:8px;
}
.salon-participation .salon-live-guide-foot span,
.salon-participation .salon-live-guide-foot a {
  font-size:10px;
}
.salon-session-head {
  margin-top:11px;
  display:flex;
  align-items:baseline;
  gap:9px;
}
.salon-session-head small {
  color:var(--focus-blue);
  font:900 9.5px/1 Inter,sans-serif;
  letter-spacing:.11em;
}
.salon-session-head h3 {
  margin:0;
  color:var(--focus-ink);
  font-size:15px;
}
.salon-run-strip {
  margin-top:5px;
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:0;
  border-width:1px 0;
  border-style:solid;
  border-color:rgba(83,103,217,.14);
}
.salon-run-cell {
  min-width:0;
  padding:7px 8px;
  border:0;
  border-radius:0;
  background:transparent;
}
.salon-run-cell + .salon-run-cell { border-left:1px solid rgba(83,103,217,.13); }
.salon-run-cell time {
  display:block;
  color:var(--focus-blue);
  font:900 13px/1 Inter,sans-serif;
}
.salon-run-cell small {
  display:block;
  margin-top:4px;
  color:var(--focus-muted);
  font:900 9px/1 Inter,sans-serif;
  letter-spacing:.08em;
}
.salon-run-cell strong {
  display:block;
  margin-top:4px;
  color:var(--focus-ink);
  font-size:11px;
  line-height:1.25;
}
.salon-register-row {
  margin-top:11px;
  padding-top:10px;
  display:grid;
  grid-template-columns:minmax(0,1fr) 260px;
  gap:16px;
  align-items:center;
  border-top:1px solid rgba(83,103,217,.15);
}
.salon-register-row--solo {
  grid-template-columns:1fr;
}
.salon-register-row--solo .salon-register-form {
  max-width:560px;
  margin-inline:auto;
}
.salon-register-row .salon-note {
  max-width:none;
  margin:0;
  font-size:11px;
  line-height:1.65;
  text-align:left;
}
.salon-register-row .salon-note strong {
  display:block;
  color:var(--focus-ink);
  font-size:12px;
}
.salon-register-form {
  width:100%;
  text-align:center;
}
.salon-register-form .focus-btn {
  width:100%;
  min-height:42px;
  border:0;
  cursor:pointer;
}
.salon-register-form small {
  display:block;
  margin-top:6px;
  color:var(--focus-muted);
  font-size:9.5px;
}
.course-menu-unified {
  max-width:1400px;
  margin:0 auto;
}
.course-menu-unified > .salon-section--integrated {
  max-width:none;
  margin:14px auto 0;
  padding:0 !important;
  overflow:visible;
  border:0;
  background:transparent;
}
.salon-section--integrated .salon-panel {
  max-width:none;
  border-color:rgba(83,103,217,.28);
  box-shadow:0 18px 44px rgba(38,54,112,.10);
}
#seven-day-courses .salon-panel {
  padding:16px 18px;
}
.salon-card-category {
  display:block;
  color:var(--focus-blue);
  font:900 9px/1 Inter,sans-serif;
  letter-spacing:.12em;
}
.salon-card-meta {
  margin-top:10px;
}
.salon-card-meta strong {
  font-size:18px;
}
.salon-card-checkout {
  max-width:420px;
  margin:12px auto 0;
}
.salon-simple-note {
  margin:12px 0 7px;
  color:var(--focus-muted);
  font-size:9.5px;
  text-align:center;
}
.salon-material-row {
  margin:5px 0 0;
  text-align:center;
}
.salon-material-link {
  color:var(--focus-blue);
  font-size:11px;
  font-weight:900;
  line-height:1.5;
  text-decoration:underline;
  text-underline-offset:3px;
}
.salon-material-link:hover { color:var(--focus-blue-dark); }
.salon-all-details--complete {
  margin-top:10px;
}
.salon-details-complete {
  padding:4px 0 6px;
}
.salon-detail-title {
  margin:8px 0 0;
  color:var(--focus-ink);
  font-size:22px;
  line-height:1.25;
}
.salon-benefits-title {
  margin:12px 0 0;
  color:var(--focus-ink);
  font-size:12px;
  font-weight:900;
}
.salon-eyebrow-row {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom:12px;
}
.salon-eyebrow-row > small {
  color:var(--focus-blue);
  font:900 10px/1 Inter,sans-serif;
  letter-spacing:.12em;
}
.salon-eyebrow-row .compact-course-badge { margin:0; }
.salon-card-eyebrow { margin-bottom:12px; }
.salon-panel .salon-intro.salon-intro--fused {
  grid-template-columns:minmax(200px,.62fr) minmax(300px,1fr) minmax(250px,.72fr);
  grid-template-areas:"media copy values";
  align-items:stretch;
}
.salon-main-visual {
  grid-area:media;
  min-width:0;
  margin:0;
  overflow:hidden;
  border:1px solid rgba(83,103,217,.14);
  border-radius:12px;
  background:#eef1ff;
}
.salon-main-visual img {
  width:100%;
  height:100%;
  min-height:210px;
  display:block;
  object-fit:cover;
}
.salon-main-visual figcaption {
  position:absolute;
  width:1px;
  height:1px;
  padding:0;
  overflow:hidden;
  clip:rect(0,0,0,0);
  white-space:nowrap;
  border:0;
}
.salon-intro-description {
  margin:9px 0 0;
  color:var(--focus-muted);
  font-size:12px;
  line-height:1.6;
}
.salon-details-complete > ul {
  margin:0;
  padding:12px 0 14px;
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:10px 18px;
  list-style:none;
}
.salon-benefit {
  position:relative;
  min-width:0;
  display:grid;
  gap:2px;
  padding-left:20px;
}
.salon-benefit::before {
  content:"✓";
  position:absolute;
  left:0;
  top:0;
  color:var(--focus-blue);
  font-size:12px;
  font-weight:1000;
}
.salon-benefit strong { color:var(--focus-ink); font-size:12px; }
.salon-benefit span { color:var(--focus-muted); font-size:11px; line-height:1.55; }
@media (max-width:1100px) {
  .course-menu-unified { max-width:900px; }
  .compact-course-grid {
    max-width:none;
    grid-template-columns:repeat(2,minmax(0,1fr));
    align-items:start;
    gap:12px;
  }
  .compact-course-card {
    grid-column:auto;
    min-height:0;
  }
}
@media (max-width:1000px) {
  .salon-panel .salon-intro.salon-intro--fused {
    grid-template-columns:180px minmax(0,1fr);
    grid-template-areas:"media copy" "values values";
  }
  .salon-panel .salon-intro--fused .salon-value-list {
    grid-template-columns:repeat(3,minmax(0,1fr));
  }
  .salon-panel .salon-intro--fused .salon-value + .salon-value {
    border-top:0;
    border-left:1px solid rgba(83,103,217,.13);
  }
}
@media (min-width:721px) and (max-width:1000px) {
  .salon-panel .salon-intro--fused .salon-value {
    grid-template-columns:24px minmax(0,1fr);
    gap:6px;
    padding:5px 8px;
  }
  .salon-panel .salon-intro--fused .salon-value > b {
    font-size:13px;
  }
  .salon-panel .salon-intro--fused .salon-value > div {
    display:grid;
    min-width:0;
    gap:1px;
  }
  .salon-panel .salon-intro--fused .salon-value small {
    display:block;
    margin:0;
    font-size:8px;
    line-height:1;
    white-space:nowrap;
  }
  .salon-panel .salon-intro--fused .salon-value strong {
    display:block;
    font-size:11px;
    line-height:1.2;
    white-space:nowrap;
  }
}
@media (max-width:720px) {
  .course-menu-unified {
    margin:0;
  }
  .compact-course-grid {
    grid-template-columns:1fr;
    gap:10px;
  }
  .salon-section {
    padding:22px 10px !important;
  }
  .salon-panel {
    padding:12px;
    border-radius:14px;
  }
  .salon-simple-note {
    font-size:9px;
    line-height:1.45;
    text-align:center;
  }
  .salon-material-row { text-align:center; }
  .salon-panel .salon-intro {
    grid-template-columns:1fr;
    grid-template-areas:"copy" "values";
    gap:9px;
  }
  .salon-panel .salon-intro.salon-intro--fused {
    grid-template-columns:1fr;
    grid-template-areas:"media" "copy" "values";
  }
  .salon-main-visual img {
    height:auto;
    min-height:0;
    aspect-ratio:16/9;
  }
  .salon-panel .salon-intro-kicker {
    padding:5px 8px;
    font-size:10px;
  }
  .salon-panel .salon-intro h2 {
    margin-top:8px;
    font-size:25px;
  }
  .salon-panel .salon-intro-tagline {
    margin-top:6px;
    font-size:15px;
  }
  .salon-panel .salon-value-list {
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:0;
    border-width:1px 0;
  }
  .salon-panel .salon-value {
    display:block;
    min-width:0;
    padding:5px 2px;
    border:0;
    border-radius:0;
    background:transparent;
    text-align:center;
  }
  .salon-panel .salon-value + .salon-value {
    border-top:0;
    border-left:1px solid rgba(83,103,217,.13);
  }
  .salon-panel .salon-value > b {
    font-size:11px;
  }
  .salon-panel .salon-value small {
    display:block;
    margin:2px 0 1px;
    overflow:visible;
    font-size:7.5px;
    line-height:1;
    text-overflow:clip;
    white-space:normal;
  }
  .salon-panel .salon-value strong {
    display:block;
    font-size:9.5px;
    line-height:1.25;
  }
  .salon-panel .salon-facts {
    grid-template-columns:repeat(4,minmax(0,1fr));
    margin-top:8px;
  }
  .salon-panel .salon-fact {
    padding:6px 1px;
  }
  .salon-panel .salon-fact + .salon-fact {
    border-left:1px solid rgba(83,103,217,.13);
  }
  .salon-panel .salon-fact:nth-child(n+3) {
    margin-top:0;
    border-top:0;
  }
  .salon-panel .salon-fact small {
    font-size:9px;
  }
  .salon-panel .salon-fact strong {
    font-size:11px;
    white-space:normal;
  }
  .salon-participation {
    grid-template-columns:88px minmax(0,1fr);
    gap:8px;
    margin-top:9px;
    padding:8px;
    border-radius:12px;
  }
  .salon-participation .salon-live-figure figcaption {
    display:block;
    font-size:9px;
    line-height:1.35;
  }
  .salon-participation .salon-live-badge {
    font-size:9px;
  }
  .salon-participation h3 {
    font-size:15px;
  }
  .salon-participation .salon-live-steps {
    grid-template-columns:1fr;
    gap:0;
    margin-top:6px;
  }
  .salon-participation .salon-live-steps li {
    grid-template-columns:20px minmax(0,1fr);
    gap:6px;
    padding:3px 0;
    border-width:0 0 1px;
    border-style:solid;
    border-color:rgba(83,103,217,.12);
    background:transparent;
  }
  .salon-participation .salon-live-steps li:last-child { border-bottom:0; }
  .salon-participation .salon-live-steps b {
    width:20px;
    height:20px;
    font-size:8px;
  }
  .salon-participation .salon-live-steps strong {
    font-size:11px;
  }
  .salon-participation .salon-live-steps small {
    font-size:9.5px;
  }
  .salon-participation .salon-live-guide-foot {
    align-items:flex-start;
    flex-direction:column;
    gap:3px;
  }
  .salon-participation .salon-live-guide-foot span,
  .salon-participation .salon-live-guide-foot a {
    font-size:10px;
  }
  .salon-session-head {
    margin-top:9px;
  }
  .salon-run-strip {
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:0;
  }
  .salon-run-cell {
    padding:6px 3px;
  }
  .salon-run-cell time {
    font-size:11px;
  }
  .salon-run-cell strong {
    font-size:10px;
  }
  .salon-register-row {
    grid-template-columns:1fr;
    gap:8px;
    margin-top:9px;
    padding-top:9px;
  }
  .salon-register-form .focus-btn {
    min-height:44px;
  }
  .salon-details-complete > ul { grid-template-columns:1fr; }
  .salon-benefit strong { font-size:11.5px; }
  .salon-benefit span { font-size:10.5px; }
}
@media (max-width:340px) {
  .hero-advantage-pillars li { padding:0; font-size:11px; }
  .salon-run-strip { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .salon-run-cell:nth-child(odd) { border-left:0; }
  .salon-run-cell:nth-child(n+3) { border-top:1px solid rgba(83,103,217,.13); }
}

/* ---- Conventional public mobile drawer, 2026-07-19 ---- */
@media (max-width: 900px) {
  body.mobile-menu-open { overflow: hidden !important; }
  .header-member-login { display: none !important; }
  .mobile-toggle {
    width: auto !important;
    min-width: 94px !important;
    height: 44px !important;
    padding: 0 12px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    border: 1px solid rgba(10,23,40,.22) !important;
    border-radius: 8px !important;
    background: #fff !important;
    color: var(--focus-ink) !important;
    box-shadow: 0 6px 16px rgba(10,23,40,.08) !important;
  }
  .mobile-toggle:hover,
  .mobile-toggle:focus-visible,
  .mobile-toggle[aria-expanded="true"] {
    background: #f1f7ff !important;
    color: var(--focus-blue) !important;
    border-color: rgba(7,95,200,.36) !important;
    outline: none !important;
  }
  .mobile-toggle > svg { display: none !important; }
  .mobile-toggle-icon {
    width: 22px;
    height: 18px;
    display: grid;
    align-content: space-between;
  }
  .mobile-toggle-icon span {
    width: 22px;
    height: 2px;
    display: block;
    border-radius: 999px;
    background: currentColor;
    transition: transform .2s ease, opacity .2s ease;
    transform-origin: center;
  }
  .mobile-toggle[aria-expanded="true"] .mobile-toggle-icon span:nth-child(1) { transform: translateY(8px) rotate(45deg); }
  .mobile-toggle[aria-expanded="true"] .mobile-toggle-icon span:nth-child(2) { opacity: 0; }
  .mobile-toggle[aria-expanded="true"] .mobile-toggle-icon span:nth-child(3) { transform: translateY(-8px) rotate(-45deg); }
  .mobile-toggle-text { font-size: 13px; font-weight: 900; line-height: 1; }
  .mobile-nav {
    position: fixed !important;
    inset: 74px 0 0 !important;
    max-height: none !important;
    padding: 0 !important;
    display: block !important;
    overflow: hidden !important;
    overscroll-behavior: contain;
    visibility: hidden;
    opacity: 0;
    pointer-events: none;
    background: rgba(10,23,40,.38) !important;
    border-top: 1px solid rgba(10,23,40,.12) !important;
    box-shadow: none !important;
    transition: opacity .24s ease, visibility 0s linear .32s;
  }
  .mobile-nav.open {
    visibility: visible;
    opacity: 1;
    pointer-events: auto;
    transition: opacity .24s ease;
  }
  .mobile-nav-panel--public {
    width: min(88vw, 380px) !important;
    height: 100%;
    min-height: 100%;
    margin: 0 0 0 auto !important;
    padding: 0 18px calc(28px + env(safe-area-inset-bottom)) !important;
    display: block !important;
    overflow-y: auto;
    overscroll-behavior: contain;
    background: #fff !important;
    color: var(--focus-ink) !important;
    box-shadow: -22px 0 52px rgba(10,23,40,.20) !important;
    transform: translateX(100%);
    transition: transform .32s cubic-bezier(.22,1,.36,1);
  }
  .mobile-nav.open .mobile-nav-panel--public {
    transform: translateX(0);
  }
  .mobile-public-links { display: grid; }
  .mobile-nav-panel--public .mobile-public-links a {
    min-height: 50px;
    display: flex !important;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    padding: 12px 4px !important;
    border: 0 !important;
    border-bottom: 1px solid rgba(10,23,40,.10) !important;
    border-radius: 0 !important;
    background: #fff !important;
    color: var(--focus-ink) !important;
    box-shadow: none !important;
    text-align: left !important;
    text-decoration: none !important;
    font-size: 15px !important;
    font-weight: 800 !important;
  }
  .mobile-nav-panel--public .mobile-public-links a:hover,
  .mobile-nav-panel--public .mobile-public-links a:focus-visible {
    padding-left: 10px !important;
    background: #f6f9fd !important;
    color: var(--focus-blue) !important;
    outline: none !important;
  }
  .mobile-nav-panel--public .mobile-public-link--cta { color: var(--focus-blue) !important; }
  .mobile-link-arrow { flex: 0 0 auto; color: #718096; font-size: 22px; font-weight: 500; line-height: 1; }
  .mobile-nav-admin {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 2px solid rgba(10,23,40,.13);
  }
  .mobile-nav-panel--public .mobile-nav-admin .mobile-nav-label {
    display: block;
    padding: 0 2px 8px !important;
    color: #66758a !important;
    font-size: 10px !important;
    font-weight: 900 !important;
    letter-spacing: .12em !important;
    text-align: left !important;
  }
  .mobile-nav-panel--public .mobile-admin-link {
    min-height: 60px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 14px !important;
    padding: 10px 14px !important;
    border: 1px solid rgba(10,23,40,.16) !important;
    border-radius: 8px !important;
    background: #f7f9fc !important;
    color: var(--focus-ink) !important;
    box-shadow: none !important;
    text-align: left !important;
    text-decoration: none !important;
  }
  .mobile-admin-link-copy { display: grid; gap: 2px; }
  .mobile-admin-link-copy strong { font-size: 14px; line-height: 1.2; }
  .mobile-admin-link-copy small { display: block !important; color: #66758a; font-size: 11px; font-weight: 700; line-height: 1.3; }
}
@media (max-width: 680px) {
  .mobile-nav { inset: 64px 0 0 !important; }
}
@media (max-width: 900px) and (prefers-reduced-motion: reduce) {
  .mobile-nav,
  .mobile-nav-panel--public {
    transition: none !important;
  }
}
@media (min-width: 901px) {
  .mobile-nav,
  .mobile-nav.open {
    display: none !important;
  }
}

/* ---- Clear Sky Rose palette, selected 2026-08-03 ----
   Color and surface changes only. Layout, type sizes, copy, and imagery stay unchanged. */
header.site-header,
header.site-header.scrolled,
header.site-header:hover {
  border-bottom: 1px solid rgba(79,111,216,.10) !important;
  box-shadow: 0 8px 24px rgba(39,60,104,.06) !important;
}
.site-nav .nav-cta,
.focus-btn.primary,
.compact-course-card > a,
.compact-course-checkout button,
.salon-register-form .focus-btn,
.focus-contact {
  background: var(--focus-blue) !important;
  background-image: none !important;
}
.site-nav .nav-cta:hover,
.site-nav .nav-cta:focus-visible,
.compact-course-card > a:hover,
.compact-course-checkout button:hover,
.compact-course-checkout button:focus-visible {
  background: var(--focus-blue-dark) !important;
}
.hero-advantage-copy small strong,
.site-nav .menu-drop a:hover,
.site-nav .menu-drop a:focus-visible,
.mobile-toggle:hover,
.mobile-toggle:focus-visible,
.mobile-toggle[aria-expanded="true"] {
  background: var(--focus-lavender) !important;
}
.compact-course-badge,
.salon-intro-kicker {
  background: var(--focus-rose-soft) !important;
  border-color: rgba(232,142,160,.34) !important;
}
.compact-course-badge i,
.salon-intro-kicker i,
.salon-live-badge i {
  background: var(--focus-rose) !important;
  box-shadow: 0 0 0 4px rgba(232,142,160,.13) !important;
}
.compact-course-card,
.salon-panel,
.salon-live-guide,
.salon-timeline-card,
.path-card-new,
.focus-proof,
.salon-participation {
  border-color: var(--focus-line) !important;
  box-shadow: 0 8px 24px rgba(39,60,104,.08) !important;
}
.compact-course-card:hover,
.path-card-new:hover,
.focus-hub-card:hover,
.salon-timeline-card.is-active {
  border-color: rgba(79,111,216,.38) !important;
  box-shadow: 0 14px 34px rgba(79,111,216,.13) !important;
}
.salon-section,
.focus-block.soft {
  background-color: var(--focus-surface) !important;
}
.salon-participation,
.salon-live-steps li {
  background: #f8fbff !important;
}
.focus-hero .focus-title strong::after {
  background: #cbd4fa !important;
}
/* Mobile conversion dock: show two clear booking choices after the hero. */
.sticky-cta {
  position: fixed !important;
  right: 0 !important;
  bottom: 0 !important;
  left: 0 !important;
  z-index: 90 !important;
  display: none !important;
  align-items: stretch !important;
  gap: 8px !important;
  width: 100% !important;
  max-width: none !important;
  margin: 0 !important;
  padding: 8px 12px calc(8px + env(safe-area-inset-bottom)) !important;
  border: 1px solid var(--focus-line) !important;
  border-radius: 16px 16px 0 0 !important;
  background: rgba(255,255,255,.98) !important;
  box-shadow: 0 -10px 28px rgba(7,20,38,.12) !important;
  transform: translateY(140%);
  opacity: 0;
  pointer-events: none;
  transition: transform .24s ease, opacity .24s ease;
}
.sticky-cta.is-visible {
  transform: translateY(0);
  opacity: 1;
  pointer-events: auto;
}
.sticky-cta-btn {
  display: flex !important;
  flex: 1 1 0 !important;
  min-width: 0 !important;
  min-height: 50px !important;
  align-items: center !important;
  justify-content: center !important;
  flex-direction: column !important;
  gap: 2px !important;
  padding: 8px 6px !important;
  border: 1px solid rgba(79,111,216,.32) !important;
  border-radius: 10px !important;
  background: #f6f8ff !important;
  color: var(--focus-blue-dark) !important;
  box-shadow: none !important;
  font-size: 12px !important;
  font-weight: 900 !important;
  line-height: 1.2 !important;
  text-align: center !important;
  text-decoration: none !important;
  white-space: nowrap !important;
}
.sticky-cta-btn small {
  color: inherit !important;
  font-size: 10px !important;
  font-weight: 750 !important;
  line-height: 1.2 !important;
}
.sticky-cta-btn--agent {
  border-color: var(--focus-blue) !important;
  background: var(--focus-blue) !important;
  color: #fff !important;
}
.sticky-cta-btn:hover,
.sticky-cta-btn:focus-visible {
  transform: translateY(-1px);
  filter: brightness(.97);
  outline: 3px solid rgba(79,111,216,.25) !important;
  outline-offset: 2px;
}
@media (max-width: 760px) {
  .sticky-cta { display: flex !important; }
  body { padding-bottom: calc(76px + env(safe-area-inset-bottom)); }
}
@media (min-width: 761px) {
  .sticky-cta { display: none !important; }
}
.focus-btn:focus-visible,
.compact-course-checkout button:focus-visible,
.mobile-toggle:focus-visible,
a:focus-visible,
button:focus-visible {
  outline-color: rgba(79,111,216,.28) !important;
}
.offer-panel {
  width:min(1180px,calc(100% - 48px));
  margin:18px auto;
  overflow:hidden;
  border:1px solid rgba(79,111,216,.18);
  border-radius:20px;
  background:#fff;
  box-shadow:0 16px 38px rgba(32,55,100,.08);
}
.offer-card { border-color:rgba(79,111,216,.18); }
.offer-role-row {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin:0 0 11px;
}
.offer-role-copy { display:flex; min-width:0; align-items:center; gap:8px; }
.offer-role-badge {
  display:inline-flex;
  min-height:25px;
  align-items:center;
  justify-content:center;
  padding:4px 10px;
  color:#fff;
  border-radius:999px;
  background:var(--focus-blue);
  font-size:10px;
  font-weight:950;
  letter-spacing:.08em;
  line-height:1;
}
.offer-role-note {
  color:var(--focus-blue-dark);
  font-size:10px;
  font-weight:900;
  letter-spacing:.08em;
  line-height:1.35;
}
.offer-audience {
  flex:0 0 auto;
  display:inline-flex;
  align-items:baseline;
  gap:6px;
  padding:5px 9px;
  color:var(--focus-blue-dark);
  border:1px solid rgba(79,111,216,.2);
  border-radius:9px;
  background:#f2f5ff;
}
.offer-audience-label { font-size:9px; font-weight:800; }
.offer-audience strong { color:var(--focus-blue-dark); font-size:14px; line-height:1; }
.offer-action {
  display:inline-flex;
  min-height:46px;
  align-items:center;
  justify-content:center;
  padding:11px 16px;
  color:#fff;
  border:1px solid var(--focus-blue);
  border-radius:11px;
  background:var(--focus-blue);
  box-shadow:0 8px 20px rgba(43,72,177,.18);
  font-size:13px;
  font-weight:900;
  line-height:1.35;
  text-align:center;
  text-decoration:none;
}
.offer-action:hover,
.offer-action:focus-visible { color:#fff; background:var(--focus-blue-dark); border-color:var(--focus-blue-dark); }
.offer-action--secondary { color:var(--focus-blue-dark); background:#fff; box-shadow:none; }
.offer-action--secondary:hover,
.offer-action--secondary:focus-visible { color:var(--focus-blue-dark); background:#edf3ff; }
.compact-course-card > .compact-course-action,
.compact-course-checkout > .compact-course-action {
  width:100%;
  min-height:46px;
  margin-top:4px;
  padding:11px 16px;
  border-radius:11px;
  font-size:13px;
}
@media (max-width:760px) {
  .offer-panel { width:calc(100% - 28px); margin:14px auto; border-radius:16px; }
  .offer-role-row { align-items:flex-start; }
}
@media (max-width:360px) {
  .compact-course-heading { flex-wrap:nowrap; gap:5px; }
  .compact-course-heading h3 {
    flex:1 1 auto;
    white-space:nowrap;
    font-size:16px;
    letter-spacing:-.04em;
  }
  .compact-course-heading .offer-audience { gap:4px; padding:4px 6px; }
  .compact-course-heading .offer-audience-label { font-size:8px; }
  .compact-course-heading .offer-audience strong { font-size:12px; }
}
.readiness-guide {
  padding: 0;
  background: linear-gradient(135deg, #f5f9ff 0%, #fff 62%, #f4fbfa 100%);
  border-top: 1px solid rgba(79,111,216,.14);
  border-bottom: 1px solid rgba(79,111,216,.14);
}
.readiness-guide > .offer-panel { padding:30px 32px; }
.readiness-guide__inner {
  display: grid;
  grid-template-columns: minmax(340px, 1.08fr) minmax(280px, .9fr) minmax(290px, .84fr);
  gap: 22px clamp(18px, 2vw, 30px);
  max-width: 100%;
  margin: 0 auto;
  align-items: center;
}
.readiness-guide__inner > * { min-width:0; }
.readiness-guide__eyebrow {
  display: block;
  margin: 0 0 4px;
  color: var(--focus-blue);
  font: 900 12px/1.35 Inter, sans-serif;
  letter-spacing: .12em;
}
.readiness-guide__title {
  margin: 0;
  color: var(--focus-blue);
  font-size: clamp(31px, 3vw, 40px);
  font-weight: 950;
  letter-spacing: -.06em;
  line-height: 1.16;
}
.readiness-guide__summary {
  max-width: 470px;
  margin: 7px 0 0;
  color: #30415b;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.55;
}
.readiness-guide__prompt {
  margin: 9px 0 0;
  color: var(--focus-ink);
  font-size: 14px;
  font-weight: 900;
  line-height: 1.45;
}
.readiness-guide__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 5px 12px;
  margin: 9px 0 0;
  color: #53627a;
  font-size: 11px;
  font-weight: 800;
}
.readiness-guide__questions {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.readiness-guide__questions li {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  min-width: 0;
  padding: 7px 10px;
  color: #30415b;
  border: 1px solid rgba(79,111,216,.15);
  border-radius: 10px;
  background: rgba(255,255,255,.82);
  font-size: 12px;
  font-weight: 800;
  line-height: 1.35;
}
.readiness-guide__questions li span {
  display: inline-grid;
  width: 22px;
  height: 22px;
  place-items: center;
  color: #fff;
  border-radius: 50%;
  background: var(--focus-blue);
  font: 900 12px/1 Inter, sans-serif;
}
.readiness-guide__questions li > div { min-width:0; }
.readiness-guide__questions li > div strong {
  display: block;
  color: var(--focus-ink);
  font-size: 12px;
  font-weight: 900;
}
.readiness-guide__questions li > div small {
  display:block;
  margin-top:1px;
  color:#53627a;
  font-size:10px;
  font-weight:700;
  line-height:1.35;
}
.readiness-guide__actions {
  display:grid;
  min-width:0;
  gap:8px;
}
.readiness-guide__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 52px;
  padding: 13px 18px;
  color: #fff;
  border: 2px solid var(--focus-blue);
  border-radius: 12px;
  background: var(--focus-blue);
  box-shadow: 0 8px 18px rgba(43,72,177,.22);
  font-size: 15px;
  font-weight: 900;
  line-height: 1.2;
  text-align:center;
  text-decoration: none;
  transition: transform .18s ease, background .18s ease, box-shadow .18s ease;
}
.readiness-guide__cta b { font-size: 20px; line-height: 1; }
.readiness-guide__cta:hover,
.readiness-guide__cta:focus-visible {
  color: #fff;
  background: #243a9b;
  border-color: #243a9b;
  box-shadow: 0 11px 22px rgba(43,72,177,.29);
  transform: translateY(-1px);
}
.readiness-guide__cta--secondary {
  color:var(--focus-blue-dark);
  background:#fff;
  border-color:rgba(79,111,216,.45);
  box-shadow:none;
}
.readiness-guide__cta--secondary:hover,
.readiness-guide__cta--secondary:focus-visible {
  color:var(--focus-blue-dark);
  background:#edf3ff;
  border-color:var(--focus-blue);
  box-shadow:none;
}
@media (min-width:761px) and (max-width:1050px) {
  .readiness-guide__inner { grid-template-columns:minmax(0,1fr) minmax(280px,.9fr); }
  .readiness-guide__actions { grid-column:1 / -1; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }
}
@media (max-width: 760px) {
  .readiness-guide { padding: 0; }
  .readiness-guide > .offer-panel { padding:24px 18px; }
  .readiness-guide__inner { grid-template-columns: minmax(0, 1fr); gap: 16px; }
  .readiness-guide__title { font-size: clamp(31px, 9vw, 39px); }
  .readiness-guide__summary { margin-top: 6px; font-size: 15px; }
  .readiness-guide__prompt { font-size: 13px; }
  .readiness-guide__questions li { font-size: 12px; }
  .readiness-guide__cta { width: 100%; }
}
.skip-link {
  position: fixed;
  inset: 12px auto auto 12px;
  z-index: 9999;
  padding: 10px 14px;
  border-radius: var(--ai-radius-control, 8px);
  background: var(--focus-ink);
  color: #fff !important;
  font-weight: 800;
  text-decoration: none;
  transform: translateY(-180%);
  transition: transform var(--ai-duration-fast, 140ms) ease;
}
.skip-link:focus { transform: translateY(0); }
:where(a, button, input, textarea, select, summary):focus-visible {
  outline: 3px solid var(--ai-color-focus, #263d91) !important;
  outline-offset: 3px !important;
}
@media (prefers-reduced-motion: reduce) {
  .skip-link { transition: none; }
}
"""

FOCUSED_PORTAL_CSS += r"""
/* ---- AIアプリサイト: 相談から仕組み化へ進む公開導線, 2026-08-20 ---- */
.home-app-site-guide { position:relative; overflow:hidden; border-top:1px solid #d6e5f1; border-bottom:1px solid #d6e5f1; background:linear-gradient(135deg,#eef7ff 0%,#fbfdff 52%,#edfbf7 100%); }
.home-app-site-guide::after { position:absolute; right:-120px; bottom:-180px; width:420px; height:420px; border-radius:50%; background:rgba(23,103,190,.09); content:""; }
.home-app-site-guide > .offer-panel { position:relative; z-index:1; }
.home-app-site-guide .readiness-guide__title { color:#142d4c; font-size:clamp(31px,2.4vw,36px); letter-spacing:-.05em; }
.home-app-site-title-line { display:block; white-space:nowrap; }
.home-app-site-guide .readiness-guide__summary { color:#526a83; font-size:14px; line-height:1.65; }
.home-app-site-price { margin:9px 0 0; }
.home-app-site-price small { display:block; color:#087972; font-size:10px; font-weight:900; letter-spacing:.08em; }
.home-app-site-price strong { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 8px; margin-top:3px; color:#132d4d; font-size:14px; line-height:1.4; }
.home-app-site-price strong b { color:#1767be; font-size:21px; }
.home-app-site-price > span { display:block; margin-top:2px; color:#5d7390; font-size:11px; font-weight:800; }
.home-app-site-capabilities li { position:relative; min-height:44px; }
.home-app-site-capabilities li > span { position:relative; z-index:1; pointer-events:none; }
.home-app-site-card { position:absolute; inset:0; display:flex; min-width:0; min-height:44px; width:100%; padding:10px 12px 10px 42px; box-sizing:border-box; align-items:center; justify-content:space-between; gap:8px; color:#17304f; text-decoration:none; }
.home-app-site-card strong { min-width:0; font-size:12px; line-height:1.35; }
.home-app-site-card b { flex:0 0 auto; color:#1767be; font-size:14px; transition:transform .18s ease; }
.home-app-site-card:hover,
.home-app-site-card:focus-visible { color:#114f93; }
.home-app-site-card:hover b,
.home-app-site-card:focus-visible b { transform:translateX(2px); }
@media (min-width:901px) and (max-width:1210px) {
  .site-nav { gap:2px !important; }
  .site-nav .nav-link { padding-inline:7px !important; font-size:11px !important; }
}
@media (max-width:760px) {
  .focus-title-line { font-size:clamp(28px,9vw,44px); white-space:nowrap; }
  .focus-title-line strong { white-space:nowrap; }
  .home-app-site-capabilities { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .home-app-site-capabilities li { min-height:52px; }
  .home-app-site-capabilities li:last-child { grid-column:1 / -1; }
  .home-app-site-card { min-height:52px; padding:8px 8px 8px 34px; }
}
@media (max-width:360px) {
  .home-app-site-guide .readiness-guide__title { font-size:clamp(26px,8.5vw,31px); }
  .home-app-site-title-line { white-space:nowrap; }
}
"""


def _render_header_focused() -> str:
    desktop_navigation = render_desktop_navigation()
    mobile_navigation = render_mobile_navigation()
    return (
        "<header class='site-header' id='site-header'><div class='site-header-inner'>"
        "<a class='site-logo' href='/' aria-label='AI相談 トップへ'>"
        "<span class='wordmark'><span class='word-ai'>AI相談</span></span></a>"
        f"<nav class='site-nav' aria-label='メインナビ'>{desktop_navigation}</nav>"
        "<button class='mobile-toggle' id='mobile-toggle' type='button' aria-label='メニューを開く' aria-controls='mobile-nav' aria-expanded='false'>"
        "<span class='mobile-toggle-icon' aria-hidden='true'><span></span><span></span><span></span></span>"
        "<span class='mobile-toggle-text'>メニュー</span></button>"
        "</div><div class='mobile-nav' id='mobile-nav' aria-hidden='true'><div class='mobile-nav-panel mobile-nav-panel--public'>"
        f"{mobile_navigation}"
        "</div></div></header>"
    )


def _render_hero_focused() -> str:
    return (
        "<section class='focus-hero' id='top' data-interactive-hero>"
        "<div class='hero-orb hero-orb-one' aria-hidden='true'></div><div class='hero-orb hero-orb-two' aria-hidden='true'></div>"
        "<div class='focus-hero-shell'>"
        "<div class='focus-hero-copy'>"
        "<p class='focus-kicker'>彦根・滋賀の中小事業者向け</p>"
        "<h1 class='focus-title'><span class='focus-title-first'>AI導入120分で</span><br><span class='focus-title-line'><strong>やりたいことが動き出す</strong></span></h1>"
        "<aside class='hero-advantage' id='advantage' aria-labelledby='hero-advantage-title'>"
        "<div class='hero-advantage-number' role='img' aria-label='AI利用率 6パーセント'><span>AI利用率</span><strong>6%</strong></div>"
        "<div class='hero-advantage-copy'><small><strong>まだまだこれから！</strong><span>始めるなら今。</span></small><p id='hero-advantage-title'><span class='hero-advantage-equation'><strong>AI</strong><span>×</span><strong>経験</strong></span><span class='hero-advantage-outcome'>こんなことできたらがすぐ叶う</span></p></div>"
        "<ul class='hero-advantage-pillars' aria-label='AI活用を成果に変える3原則'><li><b>01</b>試しに作る</li><li><b>02</b>素早く修正</li><li><b>03</b>仕組み化する</li></ul>"
        "</aside>"
        "<p class='focus-lead'>告知・事務・集客に追われる方へ。AIが気になるけれど、何から始めるか迷う方へ。3つの質問で、いまの仕事に合う次の一歩を提案します。</p>"
        "<div class='focus-actions'>"
        "<div class='hero-diagnose-cta'><span class='hero-diagnose-eyebrow'>何から始めるか、1分で見える。</span>"
        "<a class='focus-btn primary hero-diagnose-button diagnose-open' href='#packages'>迷ったら60秒診断をはじめる →</a>"
        "<small>3問で完了。結果を見てから、予約するか決められます。</small></div>"
        f"<a class='focus-btn secondary' href='{AI_AGENT_COURSE_URL}' target='_blank' rel='noopener'>AIエージェント講習を見る</a>"
        "<a class='hero-text-link' href='/lectures/index.html'>受講資料 <span aria-hidden='true'>→</span></a></div>"
        "<ul class='focus-trust'><li>AI初心者OK</li><li>対面・オンライン対応</li><li>仕事を持ち込める</li></ul></div>"
        "</div>"
        "</section>"
    )


def _render_ai_app_site_home_guide() -> str:
    cards = (
        ("AI見積もり", "/ai-estimate/"),
        ("AI問い合わせ", "/ai-inquiry/"),
        ("AI予約受付", "/ai-reservation/"),
        ("AIシフト", "/ai-shift/"),
        ("AIブログ", "/ai-blog/"),
    )
    cards_html = "".join(
        "<li><span aria-hidden='true'>?</span><a class='home-app-site-card' href='{}' aria-label='{}の詳細を見る'>"
        "<strong>{}</strong><b aria-hidden='true'>→</b></a></li>".format(
            href, title, title
        )
        for title, href in cards
    )
    return (
        "<section class='readiness-guide readiness-guide--compact home-app-site-guide' id='ai-app-site' aria-labelledby='home-app-site-title'>"
        "<div class='offer-panel home-app-site-shell'><div class='readiness-guide__inner'>"
        "<div class='readiness-guide__intro'><div class='offer-role-row'><div class='offer-role-copy'>"
        "<span class='offer-role-badge'>代行</span><span class='offer-role-note'>AIアプリサイト</span></div></div>"
        "<h2 id='home-app-site-title' class='readiness-guide__title' aria-label='AIアプリサイト制作'>"
        "<span class='home-app-site-title-line'>AIアプリサイト制作</span></h2>"
        "<p class='readiness-guide__summary'>情報を載せるだけのサイトではなく、見積もり・問い合わせ・予約受付などのAIアプリを、すぐ使える形でサイト内に組み込みます。別アプリを増やさず、新規制作・リニューアル・移行まで対応。まずこちらで土台を作り、その後は講習を通じて社内で保守・改善・バージョンアップすることも、必要な部分だけこちらへ任せることも自由に選べます。</p>"
        "<div class='home-app-site-price'><small>制作を任せたい方へ</small><strong>AIアプリサイト制作 <b>99,000円〜</b></strong><span>ホームページ＋AI機能1つ</span></div></div>"
        f"<ul class='readiness-guide__questions home-app-site-capabilities' aria-label='サイトに組み込めるAIアプリ'>{cards_html}</ul>"
        "<div class='readiness-guide__actions'>"
        f"<a class='readiness-guide__cta offer-action' href='{DIAGNOSIS_FREE_CONSULT_BOOK_URL}' target='_blank' rel='noopener' aria-label='AIアプリサイト制作を無料相談する'>"
        "<span>AIアプリサイト制作を無料相談する</span><b aria-hidden='true'>→</b></a>"
        "<a class='readiness-guide__cta readiness-guide__cta--secondary offer-action offer-action--secondary' href='/ai-app-site/'>"
        "<span>制作内容・料金を見る</span><b aria-hidden='true'>→</b></a></div>"
        "</div></div></section>"
    )


def _render_readiness_guide() -> str:
    return (
        "<section class='readiness-guide readiness-guide--compact' aria-labelledby='readiness-guide-title'><div class='offer-panel'><div class='readiness-guide__inner'>"
        "<div class='readiness-guide__intro'><div class='offer-role-row'><div class='offer-role-copy'>"
        "<span class='offer-role-badge'>診断</span><span class='offer-role-note'>10問・約3分</span></div></div>"
        "<h2 id='readiness-guide-title' class='readiness-guide__title'>あなたのAI実力診断</h2>"
        "<p class='readiness-guide__summary'>10問・約3分で、いまの実践力と次に整える一歩がわかります。結果から、少数・個別・組織の受講方法も選べます。</p>"
        "<p class='readiness-guide__prompt'>AIを使っているつもりで、仕事は変わりましたか？</p>"
        "<p class='readiness-guide__meta'><span>100点・5段階</span><span>5つの基準</span><span>次の90日</span></p></div>"
        "<ul class='readiness-guide__questions' aria-label='AI活用の3つの疑問'>"
        "<li><span aria-hidden='true'>?</span><strong>コピペで止まっていないか</strong></li>"
        "<li><span aria-hidden='true'>?</span><strong>任せた仕事を確かめられるか</strong></li>"
        "<li><span aria-hidden='true'>?</span><strong>うまくいった方法を次にも残せるか</strong></li>"
        "</ul>"
        "<div class='readiness-guide__actions'><a class='readiness-guide__cta' href='/ai-agent-readiness/' aria-label='あなたのAI実力診断をはじめる。10問・約3分'>"
        "<span>あなたのAI実力診断をはじめる</span><b aria-hidden='true'>→</b></a></div>"
        "</div></div></section>"
    )


def _render_seo_llmo_guide() -> str:
    return (
        "<section class='readiness-guide readiness-guide--compact seo-llmo-guide' aria-labelledby='seo-llmo-guide-title'><div class='offer-panel'><div class='readiness-guide__inner'>"
        "<div class='readiness-guide__intro'><div class='offer-role-row'><div class='offer-role-copy'>"
        "<span class='offer-role-badge'>診断</span><span class='offer-role-note'>URLを入れて約1分</span></div></div>"
        "<h2 id='seo-llmo-guide-title' class='readiness-guide__title'>あなたのサイト診断</h2>"
        "<p class='readiness-guide__summary'>あなたのサイトは、検索とAIに正しく伝わっていますか？ 公開ページを100点・4領域で確認し、優先して直すことを整理します。</p></div>"
        "<ul class='readiness-guide__questions' aria-label='あなたのサイト診断でわかること'>"
        "<li><span aria-hidden='true'>?</span><div><strong>見つける土台</strong><small>クロール・索引</small></div></li>"
        "<li><span aria-hidden='true'>?</span><div><strong>信頼と主体</strong><small>誰のサイトか</small></div></li>"
        "<li><span aria-hidden='true'>?</span><div><strong>次の行動</strong><small>相談・申込導線</small></div></li>"
        "</ul>"
        "<div class='readiness-guide__actions'><a class='readiness-guide__cta' href='/seo-llmo-diagnosis/' aria-label='あなたのサイト診断をはじめる。URLを入れて約1分'>"
        "<span>あなたのサイト診断をはじめる</span><b aria-hidden='true'>→</b></a></div>"
        "</div></div></section>"
    )


def _render_focused_blog_content() -> str:
    posts = _load_recent_blog_posts(limit=6)
    if not posts:
        return "<p class='focus-section-lead'>ブログ記事は準備中です。</p>"
    cards = [_render_blog_card(post) for post in posts]
    return (
        "<div class='pf-carousel-wrap blog-carousel-wrap focus-blog-carousel'>"
        "<button type='button' class='pf-arrow pf-prev' aria-label='前へ' data-dir='-1'>‹</button>"
        "<div class='pf-carousel blog-carousel' id='blog-carousel'>"
        + "".join(cards)
        + "</div>"
        "<button type='button' class='pf-arrow pf-next' aria-label='次へ' data-dir='1'>›</button>"
        "</div>"
    )


def _render_focused_main() -> str:
    parts = [
        "<section class='focus-block main-course' id='packages'><div class='focus-section-head'><small>COURSES</small><h2>講習・相談コース</h2></div>",
        "<p class='focus-section-lead'><strong>制作を任せたい方は、上の「AIアプリサイト制作」へ。学ぶなら、受講人数で選べます。</strong><br>少数で基本を学ぶ、個別で自作する、組織で自作・改善・運用まで身につける。目的に合うコースへ進めます。</p>",
        "<div class='course-menu-unified' id='course-voices' role='region' aria-label='講習・相談の全4メニュー'>",
        _render_compact_course_cards(),
        _render_salon_menu(),
        "</div>",
        "<aside class='course-venue-common' aria-label='講習・相談コース共通の開催場所'>",
        "<img src='/img/gubboru-cafe-ai-course-painting.webp' alt='講習・相談の対面会場 グッぼるカフェの店内' loading='lazy' decoding='async'>",
        "<div><small>COMMON VENUE</small><h3>開催場所：グッぼるカフェ（彦根）</h3><p>対面は普段のPCと課題を持ち寄って実施します。オンライン受講・相談にも対応します。</p></div>",
        "<div class='course-venue-map'><iframe src='https://www.google.com/maps?q=%E3%82%B0%E3%83%83%E3%81%BC%E3%82%8B%E3%82%AB%E3%83%95%E3%82%A7%20%E6%BB%8B%E8%B3%80%E7%9C%8C%E5%BD%A6%E6%A0%B9%E5%B8%82%E5%B2%A1%E7%94%BA12&amp;output=embed' title='グッぼるカフェ周辺のGoogleマップ' loading='lazy' referrerpolicy='no-referrer-when-downgrade' allowfullscreen></iframe></div>",
        "<p class='course-venue-map-link'><a href='https://www.google.com/maps/search/?api=1&amp;query=%E3%82%B0%E3%83%83%E3%81%BC%E3%82%8B%E3%82%AB%E3%83%95%E3%82%A7%20%E6%BB%8B%E8%B3%80%E7%9C%8C%E5%BD%A6%E6%A0%B9%E5%B8%82%E5%B2%A1%E7%94%BA12' target='_blank' rel='noopener'>Googleマップで開く →</a></p></aside>",
        "<div class='course-quick-actions'><a href='#lectures'>受講資料から選ぶ →</a></div></section>",
        "<section class='focus-block soft' id='lectures'><div class='focus-section-head'><small>LEARNING MATERIALS</small><h2>受講資料</h2></div>",
        "<p class='focus-section-lead'>公開中の受講資料をすべて表示しています。迷ったら「AIが初めて」から順に選べます。</p>",
        _render_lectures_section(),
        "<div class='focus-content-actions'><a class='focus-btn secondary' href='/lectures/index.html'>受講資料を一覧で見る</a></div></section>",
        "<section class='focus-block' id='blog'><div class='focus-section-head'><small>PRACTICAL BLOG</small><h2>ブログ</h2></div>",
        "<p class='focus-section-lead'>AIエージェント活用と業務改善で試したことを、成功だけでなく失敗と修正も含めて残しています。</p>",
        _render_focused_blog_content(),
        "<div class='focus-content-actions'><a class='focus-btn secondary' href='/blog/index.html'>ブログを一覧で読む</a></div></section>",
        "<section class='focus-block soft' id='speaker'><div class='focus-split'><img class='speaker-painting' src='/img/speaker-portrait-gubboru-cafe-20260719.webp' alt='グッぼるカフェで少人数のAI講習を行うAI相談講師 由井辰美の絵画調ポートレート' loading='lazy' decoding='async'>",
        "<div><small class='outcome-num'>INSTRUCTOR</small><h2>9つの事業でAIエージェントを使う講師</h2><p>理想論ではなく、告知、予約、事務、サイト運営で実際に任せている仕事を題材にします。成果物の確認と、次も続けられる手順づくりまで一緒に進めます。</p><a class='focus-btn secondary' href='#contact'>彦根で相談する</a></div></div></section>",
        "<section class='focus-block' id='all-works'><div class='focus-section-head'><small>AI WORKS</small><h2>実績サイト</h2></div>",
        "<p class='focus-section-lead'>講習で扱う考え方を、地域交流、福祉、店舗、EC、予約、業務システムで実際に使った支援例です。</p><div class='focus-content-shell'>",
        _render_works_section(),
        "</div><div class='focus-content-actions'><a class='focus-btn secondary' href='#contact'>似た課題を相談する</a></div></section>",
        "<section class='focus-block soft' id='flow'><div class='focus-section-head'><small>HOW IT WORKS</small><h2>講習から、仕事で使うまで</h2></div>",
        "<div class='focus-flow'>",
        "<article class='focus-step'><img class='focus-step-visual' src='/img/flow-step-bring-20260719.webp' alt='仕事の資料とパソコンを講習へ持ち込むイメージ' loading='lazy' decoding='async'><b>01</b><h3>持ち込む</h3><p>止まっている仕事や、繰り返している作業を題材にします。<br><strong>WindowsまたはMacのパソコンを必ずお持ちください。</strong></p></article>",
        "<article class='focus-step'><img class='focus-step-visual' src='/img/flow-step-build-20260719.webp' alt='講師と受講者がパソコンを見ながら一緒に作業するイメージ' loading='lazy' decoding='async'><b>02</b><h3>一緒に動かす</h3><p>実際の仕事でAIエージェントを動かし、依頼、確認、修正までその場で実践します。</p></article>",
        "<article class='focus-step'><img class='focus-step-visual' src='/img/flow-step-save-20260719.webp' alt='確認済みの手順を資料として保存するイメージ' loading='lazy' decoding='async'><b>03</b><h3>手順に残す</h3><p>成果物と次回の進め方を保存し、自分の仕事へ戻します。受講後もLINEで質問できます。</p></article></div></section>",
        "<section class='focus-block' id='faq'><div class='focus-section-head'><small>FAQ</small><h2>よくある質問</h2></div><div class='focus-faq'>",
        "<details><summary>AIエージェント講習では何を作りますか？</summary><p>告知文、資料、調査メモ、集計、業務ツール、サイト改善など、実際の仕事から1つ選び、使える成果物と次回手順まで作ります。</p></details>",
        "<details><summary>AIがまったく初めてでも大丈夫ですか？</summary><p>大丈夫です。専門用語ではなく、普段の仕事と困りごとから始めます。</p></details>",
        "<details><summary>受講にパソコンは必要ですか？</summary><p>はい。WindowsまたはMacのパソコンを必ずお持ちください。直したい資料やページもあれば、あわせてお持ちください。</p></details>",
        "<details><summary>オンラインでも受講できますか？</summary><p>対面・オンラインの両方に対応しています。彦根市内は訪問も相談できます。</p></details>",
        "<details><summary>AIオンラインサロンでは、何がわかりますか？</summary><p>AIオンラインサロンは近日開始で、現在は仮運用中です。登録中の方にはテスト運用へご協力いただいています。月額2,200円（税込）で、Square決済は毎月自動更新し、決済確認後にLINE参加案内を表示します。</p></details></div></section>",
        "<section class='focus-contact' id='contact'><div class='focus-contact-inner'><div><h2>AIエージェントに任せたい仕事を聞かせてください。</h2><p>講習前に、今の仕事に合う題材と進め方を一緒に整理できます。</p></div>",
        f"<a class='focus-btn' href='{AI_APP_SELFBUILD_BOOK_URL}' target='_blank' rel='noopener'>AI自作講習を予約する（120分・11,000円）</a></div></section>",
    ]
    return "".join(parts)


def render_portal(businesses: list[dict], recent_lectures: list[dict]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    title = SITE_BROWSER_TITLE
    desc = "AI相談は、彦根・滋賀でAIアプリサイト制作とAI自作講習を提供しています。制作を任せたい方には99,000円から相談・制作・公開まで対応し、自分で作りたい方には個別講習でAIへの依頼、確認、修正、公開まで支援します。AIオンラインサロンは近日開始・現在仮運用中です。"

    parts: list[str] = []
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>" + FAVICON_HEAD_HTML)
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append("<meta name='theme-color' content='#F8FBFF'>")
    # 案A: 和文明朝の大見出し + monospace ラベル用に Google Fonts を読み込む
    parts.append("<link rel='preconnect' href='https://fonts.googleapis.com'>")
    parts.append("<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>")
    parts.append("<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;700;900&family=JetBrains+Mono:wght@500;700&display=swap'>")
    parts.append("<link rel='stylesheet' href='/design-system/tokens.css?v=20260815'>")
    parts.append(f"<title>{html.escape(title)}</title>")
    parts.append(f"<meta name='description' content='{html.escape(desc, quote=True)}'>")
    parts.append(f"<link rel='canonical' href='{html.escape(SITE_URL + '/', quote=True)}'>")
    parts.append(_build_ogp(title, desc, SITE_URL + "/"))
    parts.append(f"<script type='application/ld+json'>{_build_jsonld_website()}</script>")
    parts.append(f"<style>{PORTAL_CSS}{BLOG_TEASER_CSS}{FOCUSED_PORTAL_CSS}</style>")
    parts.append("</head><body><a class='skip-link' href='#main-content'>本文へ移動</a>")

    parts.append(_render_header_focused())

    parts.append("<div class='container'><main id='main-content'>")
    parts.append(_render_hero_focused())
    parts.append(_render_ai_app_site_home_guide())
    parts.append(_render_readiness_guide())
    parts.append(_render_seo_llmo_guide())

    parts.append(_render_focused_main())
    parts.append("</main>")

    parts.append(_render_footer(today))
    parts.append("</div>")
    parts.append(_render_sticky_cta())
    parts.append(_render_diagnose_modal())
    parts.append(HEADER_JS)
    parts.append("</body></html>")
    return "".join(parts)

    # Legacy sections remain below as reusable source assets, but are intentionally
    # outside the focused homepage composition.

    parts.append(_render_hero())
    parts.append(_render_ai_course_video_feature())

    # 1. 入口を一括化: 選び方、必要性、講習と資料をまとめて見せる
    parts.append("<section class='block block-tight merged-section' id='start'>")
    parts.append("<p class='section-heading fade-up'>START / AI CONSULT</p>")
    parts.append("<h2 class='section-title fade-up d1'>悩みから、AI相談の入口を選ぶ</h2>")
    parts.append("<p class='section-sub fade-up d2'>時間がない、告知が苦手、AIが分からない、事務作業が重い。最初の3択から入り、数字、講習、資料まで同じ流れで確認できます。</p>")
    parts.append(_render_path_selector())
    parts.append(_render_choice_lens())
    parts.append("<div class='section-cluster' id='why-now'>")
    parts.append("<div class='section-mini-head'><p>WHY NOW</p><h3>数字で見る、AI講習の必要性</h3><span>現場の作業に落とし、確認し、復習できるかで差が出ます。</span></div>")
    parts.append(_render_ai_impact_board())
    parts.append("</div>")
    parts.append("<div class='section-cluster' id='lesson-bridge'>")
    parts.append("<div class='section-mini-head'><p>AI LESSON / MATERIAL</p><h3>AI講習と資料を、迷わず選ぶ</h3><span>講習前に選び、講習後に復習し、仕事に転用する導線です。</span></div>")
    parts.append(_render_lesson_bridge())
    parts.append("</div>")
    parts.append("</section>")

    # 2. 受講プラン — メインCTA
    parts.append("<section class='block' id='packages'>")
    parts.append("<p class='section-heading fade-up'>AI LESSON COCKPIT</p>")
    parts.append("<h2 class='section-title packages-title fade-up d1'>複数のAI講習を、一画面で選ぶ</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI無料相談、個別相談、AIエージェント講習、伴走支援を、目的と到達点で比較できます。</p>")
    parts.append(_render_courses_packages())
    parts.append("</section>")

    # 3. 制作、実績、進め方、改善ループを一括化
    parts.append("<section class='block web-showcase-block merged-section' id='web-showcase'>")
    parts.append("<p class='section-heading fade-up'>MAKE / OPERATE</p>")
    parts.append("<h2 class='section-title fade-up d1'>制作、実績、改善までを一つの流れにする</h2>")
    parts.append("<p class='section-sub fade-up d2'>店舗LP、企業サイト、EC、講習資料、管理画面、SNS改善、実績、相談後の進め方を、提案書のようにまとめて見られる構成にしました。</p>")
    parts.append(_render_web_showcase())
    parts.append("<div class='section-cluster' id='works'>")
    parts.append("<div class='section-mini-head'><p>WORKS</p><h3>公開実績</h3><span>AI相談、制作、管理画面、地域事業の実例を横に並べます。</span></div>")
    parts.append(_render_works_section())
    parts.append("</div>")
    parts.append("<div class='section-cluster' id='business-compass'>")
    parts.append("<div class='section-mini-head'><p>BUSINESS COMPASS</p><h3>全事業を、悩みから選べる入口にする</h3><span>誰に向けて、何の悩みを解決し、どの行動へ進めばよいかを整理します。</span></div>")
    parts.append(_render_business_compass())
    parts.append("</div>")
    parts.append("<div class='section-cluster' id='flow'>")
    parts.append("<div class='section-mini-head'><p>FLOW</p><h3>相談から資料化・集客まで</h3><span>一度聞いて終わりではなく、資料センターと集客導線に変換します。</span></div>")
    parts.append(_render_flow())
    parts.append("</div>")
    parts.append("<div class='section-cluster' id='growth'>")
    parts.append("<div class='section-mini-head'><p>DAILY DESIGN LOOP</p><h3>競合とSNS反響で、講習導線を育てる</h3><span>入口とFAQを毎朝チューニングし、検索とSNSの反応を次の改善に戻します。</span></div>")
    parts.append(_render_growth_plan_section())
    parts.append("</div>")
    parts.append("</section>")

    parts.append(_render_blog_teaser())

    # 4. 資料、講師、声を一括化
    parts.append("<section class='block merged-section' id='lectures'>")
    parts.append("<p class='section-heading fade-up'>MATERIALS / SPEAKER</p>")
    parts.append("<h2 class='section-title fade-up d1'>受講前後に見返せる資料と、教える人</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI業務活用、SNS、LLMO、Codex、Claude Code、画像生成、AIコーディングを資料として残し、誰がどう教えるかまで同じ場所で確認できます。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_lectures_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-primary' href='#packages'>受講プランへ戻る →</a><a class='btn btn-secondary' href='/lectures/index.html'>📚 受講資料の一覧を見る →</a></div>")
    parts.append("<div class='section-cluster' id='speaker'>")
    parts.append("<div class='section-mini-head'><p>SPEAKER</p><h3>講師紹介</h3><span>AI活用、講習、地域コミュニティ運営、複数事業の実践者です。</span></div>")
    parts.append(_render_speaker_section())
    parts.append("</div>")

    voices_html = _render_voices()
    if voices_html:
        parts.append("<div class='section-cluster' id='voices'>")
        parts.append("<div class='section-mini-head'><p>VOICES</p><h3>受講した方の声</h3><span>あなたと同じ「AIは苦手」だった方が、何をできるようになったか。</span></div>")
        if VOICES_ARE_SAMPLE:
            parts.append("<p class='voices-sample-note fade-up d2'>※ 掲載イメージです（実際の受講者の声に差し替え予定）。</p>")
        parts.append(voices_html)
        parts.append("</div>")
    parts.append("</section>")

    # 5. FAQ（疑問解消）
    parts.append("<section class='block' id='faq'>")
    parts.append("<p class='section-heading'>FAQ</p>")
    parts.append("<h2 class='section-title'>AI相談のよくある質問</h2>")
    parts.append(_render_faq())
    parts.append("</section>")

    # 6. お問い合わせ（予約）
    parts.append("<section class='block' id='contact'>")
    parts.append("<p class='section-heading fade-up'>CONTACT</p>")
    parts.append("<h2 class='section-title fade-up d1'>AI無料相談で、今の課題を整理する</h2>")
    parts.append("<p class='section-sub fade-up d2'>講習に参加するか、伴走で進めるか。初回は無料で入口を整理します。日程を選んで、今の課題をそのまま持ってきてください。</p>")
    parts.append(_render_contact_form())
    parts.append("</section>")

    parts.append(_render_footer(today))
    parts.append("</div>")
    parts.append(_render_sticky_cta())
    parts.append(_render_diagnose_modal())
    parts.append(HEADER_JS)
    parts.append("</body></html>")
    return "".join(parts)


def main(dry_run: bool = False) -> int:
    businesses = _load_businesses()
    if not businesses:
        print("[!] config/businesses.yaml が読み込めません。スキップ。")
        return 1

    # agents_status を最新に更新（読み取り元が無いときは既存ファイルを温存）
    try:
        import importlib.util as _ilu
        _agents_script = ROOT / "scripts" / "build_agents_status.py"
        if _agents_script.exists():
            _spec = _ilu.spec_from_file_location("build_agents_status", _agents_script)
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _mod.main()
    except Exception as e:
        print(f"  agents_status 生成スキップ: {e}")

    recent_lectures = _load_recent_lectures(limit=3)
    # AIアプリサイト自作講習・相談 120分は受講資料カードとして残すが、最新資料を先頭にする
    pmap_card = {
        "title": "AIアプリサイト自作講習・相談 120分",
        "icon": "🧭",
        "date": "2026-06-06",
        "summary": "作りたいAIアプリサイトを題材に、相談、実装、変更確認、修正、安全な公開までを段階的に進める個別講習。",
        "image": "/img/course-path-coding.webp",
        "image_alt": "AIが変更したコードを人が確認し、AIアプリサイトを自作して公開する講習・相談",
        "href": "/programming-map.html",
    }
    recent_lectures = list(recent_lectures) + [pmap_card]

    html_text = render_portal(businesses, recent_lectures)

    if dry_run:
        print(html_text)
        return 0

    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / "index.html").write_text(html_text, encoding="utf-8")
    print(f"[+] portal index.html → {DIST / 'index.html'}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="dist に書かず標準出力")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
