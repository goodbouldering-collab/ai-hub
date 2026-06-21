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
from datetime import datetime
from pathlib import Path

import yaml

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
BUSINESSES_YAML = ROOT / "config" / "businesses.yaml"
PROFILE_YAML = ROOT / "config" / "profile.yaml"
PORTFOLIO_YAML = ROOT / "config" / "portfolio.yaml"
SPEAKER_MD = ROOT / "content" / "speaker.md"
DIST = ROOT / "site" / "dist"
LECTURES_DIR = ROOT / "content" / "lectures"
BLOG_DIR = ROOT / "content" / "blog"

SITE_URL = os.environ.get("AIHUB_SITE_URL", os.environ.get("AIWATCH_SITE_URL", "https://ai-hub-jp.vercel.app")).rstrip("/")

OWNER_NAME = "由井 辰美"
OWNER_EMAIL = "goodbouldering@gmail.com"
SITE_BRAND = "AIスペシャリスト 彦根"
SITE_LEGACY_NAME = "AI相談。彦根 / AIハブ"
OWNER_SUBTITLE = "彦根・滋賀のAI導入定着スペシャリスト"
OWNER_TAGLINE = "経験をAI導入に翻訳し、相談から実装・社内定着まで伴走する"
AI_CODING_BOOK_URL = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
MONTHLY_SUPPORT_CHECKOUT_URL = "/api/stripe/monthly-support"


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
    "<link rel='icon' type='image/svg+xml' href='/favicon.svg'>"
    "<link rel='icon' type='image/png' sizes='32x32' href='/favicon-32x32.png'>"
    "<link rel='icon' type='image/png' sizes='16x16' href='/favicon-16x16.png'>"
    "<link rel='shortcut icon' href='/favicon.ico'>"
    "<link rel='apple-touch-icon' sizes='180x180' href='/apple-touch-icon.png'>"
    "<link rel='manifest' href='/site.webmanifest'>"
    "<link rel='mask-icon' href='/favicon.svg' color='#0EA5E9'>"
    "<meta name='theme-color' content='#F7FBFF'>"
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


def _build_jsonld_website() -> str:
    """TOP の構造化データを @graph で一括出力。
    LocalBusiness(地域シグナル) / Person(異色の権威) / WebSite / Service×6(価格付き Offer) /
    FAQPage(一次情報) / BreadcrumbList を相互参照させ、SEO・LLMO 両面の引用源にする。"""
    org_id = SITE_URL + "/#business"
    person_id = SITE_URL + "/#yui"
    web_id = SITE_URL + "/#website"

    local_business = {
        "@type": ["ProfessionalService", "LocalBusiness"],
        "@id": org_id,
        "name": SITE_BRAND,
        "alternateName": [SITE_LEGACY_NAME, "AI相談。彦根", "AI Hub Hikone", "AI講習 彦根", "彦根 AIスペシャリスト"],
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
            "streetAddress": "岡町12番地",
            "addressCountry": "JP",
        },
        "description": "滋賀県彦根市を拠点に、中小事業者・地域団体・個人事業者向けのAIスペシャリスト相談、生成AI講習、Codex実践会、Claude Code併用、画像生成、AIコーディング講習、受講資料公開、実例紹介、Web/業務システム制作、補助金を使ったAI導入支援を行う。エンジニア経験、コンサル経験、9事業運営の実務経験をもとに、相談から講習、実装、公開、社内定着まで伴走する。",
        "knowsAbout": [
            "AIスペシャリスト", "AI相談", "生成AI講習", "ChatGPT", "Claude Code", "Codex", "画像生成", "AIコーディング講習",
            "LLMO（AI検索最適化）", "SEO", "MEO", "YouTube SEO", "Reels導線",
            "業務自動化", "AI導入補助金", "デジタル化補助金", "中小企業DX",
        ],
        "slogan": OWNER_TAGLINE,
    }

    person = {
        "@type": "Person",
        "@id": person_id,
        "name": OWNER_NAME,
        "jobTitle": "AIスペシャリスト / AI講師 / Web経営コンサルタント / 複数事業オーナー",
        "email": OWNER_EMAIL,
        "url": SITE_URL + "/speaker.html",
        "image": SITE_URL + "/img/speaker-portrait-v2.webp",
        "worksFor": {"@id": org_id},
        "knowsAbout": ["生成AI", "クライミング", "店舗経営", "マーケティング", "補助金活用"],
        "description": "クライミング歴30年。ボルダリングカフェ「グッぼる」をはじめ9事業を経営しながら、滋賀・彦根の中小事業者にAI相談、生成AI講習、Codex実践会、SNS/LLMO導線づくりを教える。経営者であり、コードを書き、業務導入を設計するAIスペシャリストであることが強み。",
    }

    website = {
        "@type": "WebSite",
        "@id": web_id,
        "name": SITE_BRAND,
        "url": SITE_URL,
        "inLanguage": "ja",
        "publisher": {"@id": org_id},
        "description": "滋賀・彦根の中小事業者向けAIスペシャリスト相談、AI導入支援、講習募集、受講資料、実例、講師紹介、AI/SNS/LLMO情報の資料センター。",
    }

    codex_prep_title = "Codex準備会 60分"
    codex_practice_title = "Codex実践会 120分"
    ai_coding_title = "AIコーディング講習 120分"
    free_consult_title = "AI無料相談 とりあえず30分"
    consult_title = "AI個別相談 しっかり60分"
    support_title = "AI伴走支援 いっしょに導入"

    # 受講プランを Service + Offer として構造化（_render_packages の items と整合）
    plans = [
        (codex_prep_title, "Codex準備会 導入と習得の流れに沿って、ChatGPTログイン、作業フォルダ選定、秘密情報を入れない権限設計、最初の依頼、差分確認、ブラウザ表示確認、独立レビュー、AGENTS.md、公式アップデート確認先までを60分で整える準備講習。", "2200", "2200", "Course"),
        (codex_practice_title, "Codex実践会で持ち込み課題を進め、Claude Codeとの使い分け、ページ、資料、コード、画像生成プロンプト、動画台本などの成果物を120分で作る実践講習。", "5500", "5500", "Course"),
        (ai_coding_title, "Codex導入、Claude Code併用、画像生成、AI時代の本物のエンジニア像、レベルマップ、プログラミング基礎、設計、データ、運用、セキュリティを1本で学ぶAIコーディング講習。AIの成果物を判断し、説明し、仕事に入れるための作業設計と確認の型を120分で身につける。", "11000", "11000", "Course"),
        (free_consult_title, "来店またはオンラインで、AI導入の入口を30分で整理する無料相談。講習や伴走の前に、今の課題と次の一手を確認する。", "0", "0", "BusinessCoaching"),
        (consult_title, "AIの使い方、役割分担、指示書、確認体制、運用導線を60分で整理する個別相談。", "5500", "5500", "BusinessCoaching"),
        (support_title, "HP公開から事務自動化・経理・マーケまで6ヶ月で一気に定着。技術的な難所は講師が代行・支援。滋賀・彦根の補助金で負担1/3以下に。", "100000", "100000", "Service"),
    ]
    services = []
    for name, desc, lo, hi, stype in plans:
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
        service = {
            "@type": "Service",
            "serviceType": stype,
            "name": name,
            "description": desc,
            "provider": {"@id": org_id},
            "areaServed": {"@type": "AdministrativeArea", "name": "滋賀県"},
            "offers": offer,
        }
        if name == ai_coding_title:
            offer["url"] = AI_CODING_BOOK_URL
            service["url"] = AI_CODING_BOOK_URL
        if name == support_title:
            offer["url"] = SITE_URL + MONTHLY_SUPPORT_CHECKOUT_URL
            service["url"] = SITE_URL + MONTHLY_SUPPORT_CHECKOUT_URL
        services.append(service)

    faq = {
        "@type": "FAQPage",
        "@id": SITE_URL + "/#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in FAQ_QA
        ],
    }

    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "受講プラン", "item": SITE_URL + "/#packages"},
            {"@type": "ListItem", "position": 3, "name": "講師紹介", "item": SITE_URL + "/#speaker"},
            {"@type": "ListItem", "position": 4, "name": "受講資料", "item": SITE_URL + "/#lectures"},
            {"@type": "ListItem", "position": 5, "name": "FAQ", "item": SITE_URL + "/#faq"},
        ],
    }

    graph = {"@context": "https://schema.org", "@graph": [local_business, person, website, *services, faq, breadcrumb]}
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
    for f in sorted(LECTURES_DIR.glob("*.md"), reverse=True)[:limit]:
        raw = f.read_text(encoding="utf-8")
        meta: dict = {}
        if raw.startswith("---"):
            try:
                end = raw.index("\n---", 3)
                fm = raw[3:end].strip()
                meta = yaml.safe_load(fm) or {}
            except Exception:
                pass
        items.append({
            "slug": f.stem,
            "title": str(meta.get("title") or f.stem),
            "date": str(meta.get("date") or ""),
            "summary": str(meta.get("summary") or ""),
        })
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
        return data.get("portfolio") or []
    except Exception as e:
        print(f"[!] portfolio.yaml load error: {e}")
        return []


def _load_all_lectures() -> list[dict]:
    """受講資料を全件（新しい順）。LP の受講資料セクション用。"""
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
        items.append({
            "slug": f.stem,
            "title": str(meta.get("title") or f.stem),
            "date": str(meta.get("date") or ""),
            "summary": str(meta.get("summary") or ""),
        })
    return items


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
html, body { margin: 0; padding: 0; overflow-x: hidden; }
html { scroll-behavior: smooth; }
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
/* ヘッダー右端の主CTA: 無料相談（グラデ・最も目立たせる） */
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
.diagnose-head { font-size: 18px; font-weight: 800; color: var(--text); margin-bottom: 16px; }
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
.lecture-card {
  display: flex; flex-direction: column; gap: 6px;
  padding: 20px; border-radius: var(--radius-sm);
  background: var(--bg-white); border: 1px solid var(--line);
  text-decoration: none; color: inherit;
  box-shadow: var(--shadow-card);
  transition: transform .2s, border-color .2s, box-shadow .2s;
}
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
/* 主導線: 無料相談の予約カード（大きく・グラデで最優先） */
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

/* ---- 制作実績カード（LP #portfolio。build_site CONTENT_CSS から移植・PORTALトークン化）---- */
.pf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 8px;
}
/* 制作実績の横スライド（カルーセル） */
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
  display: block; margin: -14px -16px 12px; /* カード内パディングを打ち消して全幅バナーに */
  border-radius: var(--radius-sm) var(--radius-sm) 0 0; overflow: hidden;
  aspect-ratio: 32 / 15; background: var(--bg-elev);
}
.pf-card .pf-thumb svg, .pf-card .pf-thumb img { display: block; width: 100%; height: 100%; object-fit: cover; }
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

.site-nav a.nav-link[href="/programming-map.html"] {
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

  .mobile-nav a[href="/programming-map.html"] {
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
.mobile-nav a[href="/programming-map.html"] {
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


BLOG_TEASER_CSS = """
.specialist-grid {
  display: grid;
  grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
  gap: clamp(14px, 2vw, 22px);
  align-items: stretch;
}
.specialist-lead-card,
.specialist-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255,255,255,.92);
  box-shadow: var(--shadow-card);
}
.specialist-lead-card {
  padding: clamp(18px, 3vw, 28px);
  background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(238,249,247,.90));
}
.specialist-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(14,165,198,.10);
  color: var(--primary);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .04em;
}
.specialist-lead-card h3 {
  margin: 14px 0 12px;
  color: var(--text);
  font-size: clamp(24px, 3vw, 38px);
  line-height: 1.22;
  letter-spacing: 0;
}
.specialist-lead-card p,
.specialist-card p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.9;
}
.specialist-source {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;
}
.specialist-source a {
  color: var(--primary);
  font-weight: 800;
}
.specialist-card-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.specialist-card {
  min-height: 100%;
  padding: 18px;
}
.specialist-card b {
  display: block;
  color: var(--text);
  font-size: 17px;
  margin-bottom: 8px;
}
.specialist-card small {
  display: inline-flex;
  margin-bottom: 10px;
  color: var(--primary);
  font-weight: 900;
  letter-spacing: .04em;
}
.blog-section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.blog-section-head .section-title,
.blog-section-head .section-sub {
  text-align: left;
  margin-left: 0;
  margin-right: 0;
}
.blog-section-head .section-sub {
  max-width: 680px;
}
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
  color: var(--text);
  text-decoration: none;
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
@media (max-width: 820px) {
  .specialist-grid,
  .specialist-card-list,
  .blog-section-head {
    grid-template-columns: 1fr;
    display: grid;
  }
  .blog-feature {
    grid-template-columns: 1fr;
  }
  .blog-list {
    grid-template-columns: 1fr;
  }
}
"""


def _render_header() -> str:
    """N デザイン風 fixed ヘッダー。スクロールで white/90 + blur に切替。"""
    return (
        "<header class='site-header' id='site-header'>"
        "<div class='site-header-inner'>"
        "<a class='site-logo' href='/' aria-label='AIスペシャリスト 彦根 トップへ'>"
        "<span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>専</span></span>"
        "<span class='wordmark'><span class='word-ai'>AIスペシャリスト</span><span class='word-hub'>彦根</span><span class='word-en'>HIKONE AI SPECIALIST</span></span>"
        "<span class='site-logo-by'>彦根・滋賀のAI導入支援</span>"
        "</a>"
        "<nav class='site-nav' aria-label='メインナビ'>"
        "<a class='nav-link nav-essential' href='#specialist'>専門性</a>"
        "<a class='nav-link nav-essential' href='#blog'>ブログ</a>"
        "<a class='nav-link nav-essential' href='#packages'>講習/伴走</a>"
        "<div class='menu-wrap'>"
        "<button class='menu-toggle' id='menu-toggle' aria-haspopup='menu' aria-expanded='false'>見る"
        "<svg class='chev' width='14' height='14' viewBox='0 0 20 20' fill='none' aria-hidden='true'><path d='M5 8l5 5 5-5' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        "</button>"
        "<div class='menu-drop' id='menu-drop' role='menu'>"
        "<span class='menu-drop-label'>学ぶ・確認する</span>"
        "<a href='#lectures'>受講資料</a>"
        "<a href='/programming-map.html'>AIコーディング</a>"
        "<a href='/blog/index.html'>ブログ一覧</a>"
        "<span class='menu-drop-label'>実績・制作</span>"
        "<a href='#works'>実例サイト</a>"
        "<a href='#web-showcase'>HP制作メニュー</a>"
        "<a href='/portfolio.html'>実績詳細</a>"
        "<span class='menu-drop-label'>確認</span>"
        "<a href='#faq'>FAQ</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='/admin'>🔐 管理画面</a>"
        "</div>"
        "</div>"
        "<a class='nav-cta' href='#contact'>無料相談</a>"
        "</nav>"
        "<button class='mobile-toggle' id='mobile-toggle' aria-label='メニュー' aria-controls='mobile-nav' aria-expanded='false'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'><path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg>"
        "</button>"
        "</div>"
        "<div class='mobile-nav' id='mobile-nav'>"
        "<div class='mobile-nav-panel'>"
        "<div class='mobile-nav-primary'>"
        "<a class='login-btn-mobile' href='#contact'>無料相談</a>"
        "<a class='mobile-main-link' href='#specialist'>AIスペシャリストとは</a>"
        "</div>"
        "<span class='mobile-nav-label'>講習</span>"
        "<div class='mobile-link-grid'>"
        "<a href='#packages'>講習/伴走</a>"
        "<a href='/programming-map.html'>AIコーディング</a>"
        "<a href='#lectures'>受講資料</a>"
        "<a href='#blog'>ブログ</a>"
        "</div>"
        "<span class='mobile-nav-label'>制作・運用</span>"
        "<div class='mobile-link-grid'>"
        "<a href='#web-showcase'>HP制作</a>"
        "<a href='#works'>実例サイト</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='#faq'>FAQ</a>"
        "</div>"
        "<a class='mobile-admin-link' href='/admin'>🔐 管理画面</a>"
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

  if (mobileToggle && mobileNav) {
    mobileToggle.addEventListener('click', function(){
      var open = mobileNav.classList.toggle('open');
      mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    mobileNav.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){
        mobileNav.classList.remove('open');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
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

  // ---- AIレベル診断 (4段階: 初級/中級/実装/上級。ヒーロー第1問から起動)
  (function(){
    var modal = document.getElementById('diagnoseModal');
    if (!modal) return;
    var body = modal.querySelector('.diagnose-body');

    // 各設問の選択肢にレベルスコアを持たせ、合計で初級/中級/上級を判定
    var QUESTIONS = [
      { q: 'Codex の理解度はどの段階ですか？', a: [
        { label: 'インストールから確認したい', lv: 'beginner' },
        { label: '基本は触れるので成果物を作りたい', lv: 'intermediate' },
        { label: 'コードの基礎から公開まで学びたい', lv: 'implementation' },
        { label: 'エージェント組織まで作りたい', lv: 'advanced' },
      ]},
      { q: '当日いちばん進めたいことは？', a: [
        { label: 'PCとモバイルの準備を整えたい', lv: 'beginner' },
        { label: 'ページや資料などを完成させたい', lv: 'intermediate' },
        { label: 'AIの成果物を読んで直せるようにしたい', lv: 'implementation' },
        { label: 'AIの役割分担と運用設計を作りたい', lv: 'advanced' },
      ]},
      { q: 'どのスパンで取り組みたい？', a: [
        { label: 'まず60分2,200円で準備したい', lv: 'beginner' },
        { label: '120分5,500円で成果物を作りたい', lv: 'intermediate' },
        { label: '120分11,000円で体系的に実装を学びたい', lv: 'implementation' },
        { label: '相談から伴走まで設計したい', lv: 'advanced' },
      ]},
    ];
    var RESULT = {
      beginner: {
        badge: 'Codex準備会', title: 'インストールからモバイルまで整える',
        name: 'Codex準備会 60分',
        desc: 'インストール、ログイン、作業フォルダ、最初の依頼、差分確認、モバイル確認までを2,200円で整えます。',
        level_id: 'beginner'
      },
      intermediate: {
        badge: 'Codex実践会', title: '成果物をその場で作る',
        name: 'Codex実践会 120分',
        desc: 'ページ、資料、コード、動画台本など、持ち込み課題を成果物として形にする少人数講習です。',
        level_id: 'intermediate'
      },
      implementation: {
        badge: 'AIコーディング講習', title: '基礎から公開前チェックまで学ぶ',
        name: 'AIコーディング講習 120分',
        desc: 'Codex導入、Claude Code併用、画像生成、AI時代の本物のエンジニア像、レベルマップ、設計・データ・運用・セキュリティ、差分確認までを体系的に学ぶ講習です。',
        level_id: 'implementation'
      },
      advanced: {
        badge: '相談', title: '個別相談で整理する',
        name: 'AI個別相談 しっかり60分',
        desc: 'AIの使い方、指示書、確認体制、運用導線を60分でしっかり整理します。',
        level_id: 'advanced'
      }
    };
    var ORDER = ['beginner','intermediate','implementation','advanced'];

    var step = 0, scores = { beginner:0, intermediate:0, implementation:0, advanced:0 };

    function render(){
      if (step < QUESTIONS.length) {
        var Q = QUESTIONS[step];
        var h = '<div class="diag-progress">STEP ' + (step+1) + ' / ' + QUESTIONS.length + '</div>';
        h += '<h3 class="diag-q">' + Q.q + '</h3><div class="diag-opts">';
        Q.a.forEach(function(opt){ h += '<button class="diag-opt" data-lv="' + opt.lv + '">' + opt.label + '</button>'; });
        h += '</div>';
        body.innerHTML = h;
      } else {
        // 同点は「より高いレベル」を優先（ORDER後方優先）
        var best = ORDER[0], bestScore = -1;
        ORDER.forEach(function(k){ if (scores[k] >= bestScore) { bestScore = scores[k]; best = k; } });
        var r = RESULT[best];
        body.innerHTML =
          '<div class="diag-result">' +
          '<div class="diag-result-badge">あなたは ' + r.badge + ' タイプ</div>' +
          '<div class="diag-result-lv">' + r.title + '</div>' +
          '<h3 class="diag-result-name">' + r.name + '</h3>' +
          '<p class="diag-result-desc">' + r.desc + '</p>' +
          '<a class="btn btn-primary" href="#packages" data-close-diag data-focus-level="' + r.level_id + '">この講座を見る →</a>' +
          '<a class="btn btn-secondary" href="mailto:goodbouldering@gmail.com" data-close-diag>無料で相談する</a>' +
          '<button class="diag-restart" type="button">もう一度診断する</button>' +
          '</div>';
      }
    }
    // start(preLv): ヒーロー第1問で選んだレベルを1問目の回答として引き継ぐ
    function open(preLv){
      step = 0; scores = { beginner:0, intermediate:0, implementation:0, advanced:0 };
      if (preLv && scores.hasOwnProperty(preLv)) { scores[preLv]++; step = 1; }
      render(); modal.classList.add('open');
    }
    function close(){ modal.classList.remove('open'); }

    // PACKAGES の該当レベルをハイライト
    function focusLevel(lv){
      var grid = document.querySelector('.packages-grid');
      if (!grid) return;
      grid.classList.add('pkg-filter-active');
      grid.querySelectorAll('.pkg-card').forEach(function(c){
        var levels = (c.getAttribute('data-level') || '').split(/\\s+/);
        c.classList.toggle('pkg-match', levels.indexOf(lv) !== -1);
      });
    }

    // 起動口: PACKAGESの診断ボタン + ヒーロー第1問
    document.addEventListener('click', function(e){
      var dOpen = e.target.closest('.diagnose-open');
      if (dOpen) { open(dOpen.getAttribute('data-prelevel') || null); return; }
    });
    modal.addEventListener('click', function(e){
      if (e.target === modal || e.target.closest('.diagnose-close')) { close(); return; }
      var focusBtn = e.target.closest('[data-focus-level]');
      if (focusBtn) { focusLevel(focusBtn.getAttribute('data-focus-level')); close(); return; }
      if (e.target.closest('[data-close-diag]')) { close(); return; }
      var opt = e.target.closest('.diag-opt');
      if (opt) { scores[opt.getAttribute('data-lv')]++; step++; render(); return; }
      if (e.target.closest('.diag-restart')) { open(); }
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
    bar.style.transform = 'translateY(140%)';
    function update(){
      var y = window.scrollY || document.documentElement.scrollTop;
      var show = y > 520;
      if (contact){
        var r = contact.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) show = false; // 問い合わせ表示中は隠す
      }
      bar.style.transform = show ? 'translateY(0)' : 'translateY(140%)';
    }
    window.addEventListener('scroll', update, { passive: true });
    update();
  })();

  // 制作実績カルーセルの左右矢印
  (function(){
    var track = document.getElementById('works-carousel');
    if (!track) return;
    document.querySelectorAll('.pf-arrow').forEach(function(btn){
      btn.addEventListener('click', function(){
        var dir = parseInt(btn.getAttribute('data-dir'), 10) || 1;
        track.scrollBy({ left: dir * Math.round(track.clientWidth * 0.8), behavior: 'smooth' });
      });
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
"""


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


def _render_hero() -> str:
    atlas_items = [
        {
            "index": "01",
            "title": "AI導入相談",
            "sub": "経験を業務に翻訳",
            "desc": "課題を聞き、AIをどこに入れ、誰が使い、どう続けるかを30分で整理します。",
            "cta": "相談日程を見る",
            "href": "#contact",
            "x": "42%",
            "y": "35%",
        },
        {
            "index": "02",
            "title": "講習会",
            "sub": "現場で使える型を学ぶ",
            "desc": "Codex、Claude Code、画像生成、AIコーディングを、仕事の成果物に結びつけます。",
            "cta": "講習プランを見る",
            "href": "#packages",
            "x": "64%",
            "y": "24%",
        },
        {
            "index": "03",
            "title": "実践ブログ",
            "sub": "経験を記事で確認",
            "desc": "AI導入、業務システム、Codex、RAG、AI時代のエンジニア像を実例で読めます。",
            "cta": "ブログを見る",
            "href": "#blog",
            "x": "71%",
            "y": "52%",
        },
        {
            "index": "04",
            "title": "実例サイト",
            "sub": "運営中の制作物",
            "desc": "実際に構築・運用しているサイトを教材として見せながら進めます。",
            "cta": "実例を見る",
            "href": "#works",
            "x": "50%",
            "y": "68%",
        },
        {
            "index": "05",
            "title": "社内定着",
            "sub": "相談で終わらせない",
            "desc": "講習後の資料化、予約導線、ブログ、SNS、業務システムまで接続します。",
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
    first_item = atlas_items[0]
    return (
        "<section class='hero hero-atlas' id='top' data-hero-atlas>"
        "<div class='hero-bg-layer' aria-hidden='true'>"
        "<img src='img/hero-codex-claude-imagegen-20260616.png' alt='' decoding='async' fetchpriority='high'>"
        "</div>"
        "<div class='hero-text fade-up'>"
        "<span class='eyebrow'>彦根・滋賀のAIスペシャリスト / AI導入・講習・社内定着支援</span>"
        "<h1 class='hero-brand'>"
        "<span class='fusion-logo-large'><span class='ai'>AIスペシャリスト</span><span class='hub'>彦根</span></span>"
        "<span class='hero-title-sub'><strong>経験をAI導入に変える。</strong><br>相談から実装・社内定着まで伴走。</span>"
        "<span class='visually-hidden'>｜彦根 AIスペシャリスト、滋賀 AI導入相談、生成AI講習、Codex講習、Claude Code併用、ChatGPT講座、画像生成講習、AI導入支援、補助金申請サポート、LLMO対策、YouTube SEO、SNS集客</span>"
        "</h1>"
        "<p class='sub-catch'>"
        "<strong>AIスペシャリストの価値は、ツール名を知っていることだけではありません。<br>現場経験をもとに、AIをどこへ入れ、どう続けるかを設計できることです。</strong>"
        "</p>"
        "<p class='lead'>"
        "エンジニアとして作れること、コンサルタントとして整理できること、9事業を回す経営者として続けられること。その経験を使って、AI導入、講習、業務改善、Web集客、資料化まで一気通貫で支援します。"
        "</p>"
        "<div class='hero-actions'>"
        "<a class='btn btn-primary btn-lg' href='#contact'>無料30分相談を予約</a>"
        "<a class='btn btn-secondary btn-lg' href='#blog'>実践ブログを読む</a>"
        "</div>"
        "<div class='hero-route-bento' aria-label='最初に選ぶ4つの入口'>"
        "<a class='hero-route-card route-consult' href='#contact'><small>01 / FREE</small><b>無料相談</b><span>AI導入の入口を整理</span></a>"
        "<a class='hero-route-card route-plan' href='#packages'><small>02 / PLAN</small><b>講習/伴走</b><span>学ぶか任せるかを選ぶ</span></a>"
        "<a class='hero-route-card route-code' href='#blog'><small>03 / BLOG</small><b>実践ブログ</b><span>経験と実績を読む</span></a>"
        "<a class='hero-route-card route-material' href='#lectures'><small>04 / MATERIAL</small><b>受講資料</b><span>先に読んで判断する</span></a>"
        "</div>"
        "<div class='hero-proof-grid' aria-label='AI講習会の特徴'>"
        "<div class='hero-proof'><span class='proof-icon'>01</span><span><b>Engineer</b><span>AIの出力を読み、直し、公開まで見られる</span></span></div>"
        "<div class='hero-proof'><span class='proof-icon'>02</span><span><b>Consultant</b><span>業務課題を分解し、社内手順に落とす</span></span></div>"
        "<div class='hero-proof'><span class='proof-icon'>03</span><span><b>Owner</b><span>9事業の現場で使い続ける視点がある</span></span></div>"
        "</div>"
        "</div>"
        "<div class='hero-photo-card hero-atlas-panel fade-up d2' aria-label='AIハブのサービス地図'>"
        "<div class='atlas-pathlines' aria-hidden='true'></div>"
        f"{''.join(atlas_buttons)}"
        "<div class='atlas-live-card' aria-live='polite'>"
        f"<span class='atlas-live-kicker'>Service {html.escape(first_item['index'])}</span>"
        f"<b class='atlas-live-title'>{html.escape(first_item['title'])}</b>"
        f"<p class='atlas-live-desc'>{html.escape(first_item['desc'])}</p>"
        f"<a class='atlas-live-cta' href='{html.escape(first_item['href'], quote=True)}'>{html.escape(first_item['cta'])}</a>"
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
            "copy": "相談、講習、制作へ迷わず進める",
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
        "暗いAIサイトではなく、触ってわかる明るい入口に変えて、相談、講習、HP制作、SNS集客へ迷わず進めます。</p>"
        "<div class='boost-actions'>"
        "<a class='boost-action primary' href='#contact'>30分相談へ進む</a>"
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
            "primary": "トップ、事業紹介、実績、採用、問い合わせ",
            "secondary": "写真整理、文章作成、公開後の更新しやすさ",
            "cta": "企業サイトを相談する",
            "href": "#contact",
            "chips": ["会社案内", "実績", "採用", "代表紹介", "FAQ"],
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


def _render_specialist_value() -> str:
    """AIスペシャリスト訴求の核。動画の要点を営業導線へ翻訳する。"""
    cards = [
        (
            "01 / Engineer",
            "AIの出力を判断できる",
            "コード、画面、文章、画像、データのどこが使えるかを読み、必要なら自分で直して公開前確認まで進めます。",
        ),
        (
            "02 / Consultant",
            "業務に入れる順番を設計できる",
            "何をAIに任せ、どこを人が確認し、誰が毎日使うのか。現場の言葉に直して手順へ落とします。",
        ),
        (
            "03 / Operator",
            "自分の事業で使い続けている",
            "9事業のWeb、SNS、資料、予約、管理画面を自分で動かすため、机上のAI論ではなく運用の詰まりを話せます。",
        ),
        (
            "04 / Teacher",
            "講習後に戻れる資料を残す",
            "講習、受講資料、実践ブログ、予約導線をつなげ、聞いて終わりではなく社内に残る形へ変えます。",
        ),
    ]
    card_html = "".join(
        "<article class='specialist-card fade-up d2'>"
        f"<small>{html.escape(kicker)}</small>"
        f"<b>{html.escape(title)}</b>"
        f"<p>{html.escape(body)}</p>"
        "</article>"
        for kicker, title, body in cards
    )
    return (
        "<section class='block block-tight' id='specialist'>"
        "<p class='section-heading fade-up'>AI SPECIALIST</p>"
        "<h2 class='section-title fade-up d1'>AIスペシャリストとは、経験をAI導入に翻訳できる人</h2>"
        "<div class='specialist-grid'>"
        "<div class='specialist-lead-card fade-up d1'>"
        "<span class='specialist-kicker'>動画から読み取った本質</span>"
        "<h3>非エンジニアでもAI時代の仕事は作れる。差がつくのは、これまでの経験をAIに渡せるかです。</h3>"
        "<p>AIスペシャリストの仕事は、ツールの説明だけではありません。現場経験をもとに課題を言語化し、AIに任せる範囲、人が判断する範囲、社内で続ける手順まで設計する仕事です。由井辰美は、エンジニア、コンサルタント、複数事業オーナーの経験を重ねているため、AI導入から定着までを一続きで見られます。</p>"
        "<div class='specialist-source'>参考動画: <a href='https://youtu.be/99EQoP7q3pA' target='_blank' rel='noopener'>「非エンジニアが荒稼ぎするAI時代の新しいお仕事」</a>。字幕本文は取得できなかったため、公開タイトルと依頼内容の要点を営業ページ向けに再構成しています。</div>"
        "</div>"
        f"<div class='specialist-card-list'>{card_html}</div>"
        "</div>"
        "</section>"
    )


def _render_path_selector() -> str:
    cards = [
        (
            "AI導入を相談したい",
            "今の課題を30分で整理して、講習で学ぶか、伴走で定着させるかを決める入口です。",
            "相談を予約する",
            "#contact",
            "30分 / 無料",
        ),
        (
            "講習会を比べたい",
            "Codex準備、Codex実践、AIコーディング、個別相談、伴走支援の違いを先に見たい方向け。",
            "講習/伴走を見る",
            "#packages",
            "料金と到達点を確認",
        ),
        (
            "実績ブログを読みたい",
            "AIスペシャリストとして何を考え、何を作っているか。Codex、RAG、業務システムの記事で確認できます。",
            "ブログを読む",
            "#blog",
            "複数記事を掲載",
        ),
        (
            "受講資料を先に見たい",
            "受講資料やAIコーディング講習を見て、雰囲気を確かめてから受講プランへ戻れます。",
            "受講資料を見る",
            "#lectures",
            "公開資料あり",
        ),
    ]
    parts = ["<div class='path-grid'>"]
    for title, desc, cta, href, meta in cards:
        parts.append(
            "<a class='path-card fade-up' href='{href}'>"
            "<span class='path-kicker'>FIRST STEP</span>"
            f"<strong>{html.escape(title)}</strong>"
            f"<p>{html.escape(desc)}</p>"
            f"<span class='path-meta'>{html.escape(meta)}</span>"
            f"<span class='path-cta'>{html.escape(cta)} →</span>"
            "</a>".format(href=html.escape(href, quote=True))
        )
    parts.append("</div>")
    return "".join(parts)


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
    codex_prep_title = "Codex準備会 60分"
    codex_practice_title = "Codex実践会 120分"
    ai_coding_title = "AIコーディング講習 120分"
    seminar_url = "https://goodbouldering.com/?pid=188553378"
    free_consult_title = "AI無料相談 とりあえず30分"
    free_consult_url = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
    consult_title = "AI個別相談 しっかり60分"
    support_title = "AI伴走支援 いっしょに導入"
    items = [
        {
            "icon": "◧",
            "cat": "無料相談",
            "level": "入口",
            "level_id": "beginner",
            "title": free_consult_title,
            "price": "無料",
            "duration": "30分",
            "subsidy": False,
            "desc": "来店またはオンラインで、講習・AI導入・補助金の入口を30分で整理します。",
            "content": [
                "今の課題とAIで試したいことを聞き取り",
                "講習、個別相談、伴走支援の入口を切り分け",
                "補助金、交流会、次回予約の導線を確認",
            ],
            "fit": ["まず話を聞きたい", "講習か伴走か迷う", "来店またはオンラインで相談したい"],
            "url": free_consult_url,
            "cta": "無料相談を予約する",
            "material_url": "#lectures",
            "material_cta": "受講資料で選び方を見る",
        },
        {
            "icon": "?",
            "cat": "相談",
            "level": "上級",
            "level_id": "advanced",
            "title": consult_title,
            "price": "5,500円",
            "duration": "60分",
            "subsidy": False,
            "desc": "仕事や課題を聞き、AIの使い方、指示書、確認体制、運用導線を60分で整理します。",
            "content": [
                "LLMO/SEO/MEO、アプリ作成、業務改善の相談テーマを整理",
                "指示文、確認手順、ファイル整理、AIの役割分担を設計",
                "相談後すぐ試す次の一手と、継続用テンプレを残す",
            ],
            "fit": ["自分の仕事でAIをどう使うか整理したい", "指示文やチェック体制を整えたい", "成果物づくりを継続運用に変えたい"],
            "url": "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP",
            "cta": "AI個別相談を予約する",
            "material_url": "#lectures",
            "material_cta": "受講資料を見て相談内容を整理",
        },
        {
            "icon": "◇",
            "cat": "伴走",
            "level": "上級",
            "level_id": "advanced",
            "title": support_title,
            "price": "月額 100,000円（税込）× 6ヶ月",
            "duration": "初回相談予約",
            "subsidy": True,
            "desc": "HP公開、事務自動化、AI導入、デザイン内製化、経理、マーケを6ヶ月で定着させます。",
            "content": [
                "AIホームページ、書類作成、営業効率化を設計",
                "経理・バックオフィス自動化、専用AIツール作成を支援",
                "補助金用のカリキュラム案、見積、導入計画まで並走",
            ],
            "fit": ["社内にAI運用を定着させたい", "複数業務をまとめて仕組み化したい", "補助金前提で導入計画を組みたい"],
            "url": MONTHLY_SUPPORT_CHECKOUT_URL,
            "cta": "Stripeで月額支払いを始める",
            "material_url": "#lectures",
            "material_cta": "受講資料で導入の流れを見る",
            "variant": "wide",
        },
        {
            "icon": "⌘",
            "cat": "Codex講習",
            "level": "準備",
            "level_id": "beginner",
            "title": codex_prep_title,
            "price": "2,200円",
            "duration": "60分 / 少人数",
            "subsidy": False,
            "desc": "Codexを安全に使い始めるため、ログイン、作業フォルダ、最初の依頼、確認手順を60分で揃えます。",
            "content": [
                "ChatGPTログイン、Codex起動、PC/モバイルの表示を確認",
                "作業フォルダ、権限、秘密情報を入れないルールを設定",
                "最初の依頼文、差分、ブラウザ表示、独立レビューを練習",
            ],
            "fit": ["開いた後に何を頼むか迷っている", "権限や秘密情報の扱いを安全にしたい", "小さな成果物を作って実践へ進みたい"],
            "req_title": "持ち帰れる形",
            "requirements": [
                "AGENTS.md、公式アップデート確認先、説明→候補→編集前確認の依頼テンプレ",
                "差分、リンク、画像、文字サイズを見て採用判断する確認手順",
            ],
            "verify": "到達点は小さな成果物を1つ作り、差分を読める状態です。申込時に「Codex準備会」を選択してください。",
            "url": seminar_url,
            "cta": "Codexメニューで準備会を選ぶ",
            "material_url": "/lectures/2026-06-codex-app-onboarding.html",
            "material_cta": "Codex準備会の受講資料を見る",
            "variant": "featured",
        },
        {
            "icon": "▣",
            "cat": "Codex講習",
            "level": "実践",
            "level_id": "intermediate",
            "title": codex_practice_title,
            "price": "5,500円",
            "duration": "120分 / 少人数",
            "subsidy": True,
            "desc": "持ち込み課題をCodexで分解し、Claude Codeとの使い分け、ページ、資料、コード、画像生成プロンプト、動画台本、運用マニュアルを成果物にします。",
            "content": [
                "作りたいもの、直したいページ、既存資料を要件に分解",
                "ページ、資料、コード、画像生成プロンプト、動画台本、運用マニュアルを制作",
                "修正指示、差分、表示確認、次回使えるテンプレ化まで実施",
            ],
            "fit": ["持ち込み課題を成果物にしたい", "講習中に公開物や資料、画像を作りたい", "CodexとClaude Codeの使い方を実務で定着させたい"],
            "req_title": "当日の進め方",
            "requirements": [
                "要件整理、依頼文、差分確認、修正指示を一緒に実行",
                "完成物を確認し、画像生成やレビューも含めて次回使える作業テンプレとして保存",
            ],
            "verify": "申込リンクは準備会と同じです。申込時に「Codex実践会」をオプション選択してください。",
            "url": seminar_url,
            "cta": "Codexメニューで実践会を選ぶ",
            "material_url": "/lectures/2026-06-codex-app-practice.html",
            "material_cta": "Codex実践会の受講資料を見る",
            "variant": "featured",
        },
        {
            "icon": "▧",
            "cat": "AIコーディング講習",
            "level": "実装",
            "level_id": "implementation",
            "title": ai_coding_title,
            "price": "11,000円",
            "duration": "120分 / 少人数",
            "subsidy": False,
            "desc": "Codex導入、Claude Code併用、画像生成、AI時代の本物のエンジニア像、レベルマップ、プログラミング基礎、設計・データ・運用・セキュリティ、実装、公開までを1本で学ぶ総合講習です。",
            "content": [
                "AIが作ったものを、目的・設計・データ・運用・セキュリティの観点で説明する",
                "HTML/CSS/JS/API/DB/GitをAIの成果物を読むための専門用語として学ぶ",
                "依頼文、差分、ブラウザ確認、独立レビュー、画像生成、本番確認を実行する",
            ],
            "fit": ["AIの成果物を判断して直せるようになりたい", "LP、資料、画像、フォーム、業務画面を作りたい", "Codex実践会より体系的に学びたい"],
            "req_title": "このプランで使う受講資料",
            "requirements": [
                "AIコーディング講習ページをもとに、Codex、Claude Code、画像生成、本物のエンジニア像、専門用語、実装、確認、公開を通しで学ぶ",
                "受講後は小さな制作物を作り、説明できない変更を公開前に止める判断まで練習する",
            ],
            "verify": "予約サイトでは「【AIコーディング講習 120分】AI時代の専門技術を伝授」を選んでください。",
            "url": AI_CODING_BOOK_URL,
            "cta": "AIコーディング講習を予約する",
            "material_url": "/programming-map.html",
            "material_cta": "AIコーディング講習の受講資料を見る",
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
        "<div class='packages-cta-row fade-up d4'>"
        "<button type='button' class='btn btn-diagnose diagnose-open'>"
        "60秒診断｜準備・実践・実装・個別相談のどれ？"
        "</button>"
        "<span class='packages-cta-hint'>3つの質問に答えるだけ。いまの状態に合う入口をその場で提案します。</span>"
        "</div>"
    )
    parts.append(
        "<p class='packages-note fade-up d4'>"
        "<strong>Codex講習:</strong> レベルは経験年数ではなく理解度で分けます。準備会はログイン、フォルダ選択、最初の依頼、差分確認、独立レビュー、公式更新確認まで60分2,200円、実践会はClaude Codeとの使い分けや画像生成も含めた成果物作成まで120分5,500円です。"
        "Codexの申込リンクは1つに統一し、申込時に「準備会」または「実践会」をオプション選択します。各カードから関連する受講資料へ進めます。"
        "<br><strong>AIコーディング講習:</strong> Codex導入、Claude Code併用、画像生成、AI時代の本物のエンジニア像、レベルマップ、設計・データ・運用・セキュリティ、実装、公開までを120分11,000円で扱う総合講習です。専用のSquare予約メニューから申し込めます。"
        "<br><strong>相談:</strong> AI個別相談は、AIの使い方、指示書、確認体制、運用導線を60分で整理します。"
        "<br><strong>月額支払い:</strong> AI伴走支援の月額決済はStripe Checkoutで受け付け、申込後に初回範囲と日程を確認します。"
        "<br><strong>補助金:</strong> 講習と伴走支援は、滋賀県・彦根市のデジタル化/AI導入系補助金と組み合わせて相談できます。"
        "</p>"
    )
    return "".join(parts)


def _render_footer(today: str) -> str:
    """リッチフッター: 屋号+一言 / ナビ / NAP(ローカルSEOの住所明示) / CTA。"""
    year = today[:4]
    return (
        "<footer class='site-footer'>"
        "<div class='footer-grid'>"
        "<div class='footer-brand'>"
        "<div class='footer-logo'><span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>専</span></span><span class='wordmark'><span class='word-ai'>AIスペシャリスト</span><span class='word-hub'>彦根</span><span class='word-en'>HIKONE AI SPECIALIST</span></span></div>"
        "<p class='footer-tagline'>滋賀・彦根の中小事業者向けに、AI導入相談・生成AI講習・Codex準備会/実践会・AIコーディング講習・受講資料・Web集客支援を行う"
        "資料センター型の相談サイト。9事業を実際に回しながら、現場に居着くAIを一緒に作ります。</p>"
        "<a class='footer-cta' href='#contact'>📩 無料で30分相談する</a>"
        "</div>"
        "<nav class='footer-nav' aria-label='フッターナビ'>"
        "<span class='footer-nav-head'>メニュー</span>"
        "<a href='#packages'>受講プラン</a>"
        "<a href='#works'>制作実績</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='#lectures'>受講資料</a>"
        "<a href='#faq'>よくある質問</a>"
        "</nav>"
        "<div class='footer-nap'>"
        "<span class='footer-nav-head'>運営</span>"
        "<p>AIスペシャリスト 彦根（AI相談。彦根 / クライミングコンサル）</p>"
        "<p>代表 由井 辰美</p>"
        "<p>〒522-0043<br>滋賀県彦根市岡町12番地</p>"
        f"<p><a href='mailto:{OWNER_EMAIL}'>{OWNER_EMAIL}</a></p>"
        "<p class='footer-area'>対応: 彦根・湖東・滋賀県全域 / 出張・オンライン全国</p>"
        "</div>"
        "</div>"
        f"<div class='footer-copy'>© {year} 由井 辰美 / AIスペシャリスト — 滋賀・彦根のAI導入相談・受講資料</div>"
        "</footer>"
    )


def _render_sticky_cta() -> str:
    """モバイルで常時追従する無料相談バー（スクロール中もCVできる）。"""
    return (
        "<div class='sticky-cta' id='sticky-cta' aria-hidden='false'>"
        "<div class='sticky-cta-text'><strong>AI導入相談は30分無料</strong><span>講習・実装・社内定着まで整理</span></div>"
        "<a class='sticky-cta-btn' href='#contact'>30分相談する</a>"
        "</div>"
    )


def _render_diagnose_modal() -> str:
    return (
        "<div class='diagnose-modal' id='diagnoseModal' role='dialog' aria-modal='true' aria-label='コース診断'>"
        "<div class='diagnose-box'>"
        "<button type='button' class='diagnose-close' aria-label='閉じる'>&times;</button>"
        "<div class='diagnose-head'>🔍 60秒コース診断</div>"
        "<div class='diagnose-body'></div>"
        "</div>"
        "</div>"
    )


def _render_explore() -> str:
    """メニュー集約: 実績 / 受講資料 をカードで（詳細は各ページへ）。
    ※ SNSポータル(AI Watch /watch/)は管理ページ(/admin)へ移行したため公開側には出さない。"""
    cards = [
        ("📂", "制作実績・事業ポートフォリオ",
         "運営事業・制作したサイト・生成した提案LP。すべて自分で構築・運用した実物。",
         "/portfolio.html", "実績を見る"),
        ("📚", "受講資料",
         "AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）の講習で使う資料。AIコーディング講習も。",
         "/lectures/index.html", "資料を見る"),
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


GUBBLE_LINE_URL = "https://lin.ee/14YxIC6"
# 無料相談の予約導線（Square・個別相談60分のサービスID）。全CTAの最終到達先をここに一本化。
CONSULT_BOOK_URL = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"


def _render_contact_form() -> str:
    """申込導線は「無料30分相談の予約(Square)」に一本化。相談はZoomまたはLINEで実施。"""
    return (
        # 主導線: 日程を選ぶだけで予約完了
        f"<a class='contact-primary fade-up' href='{CONSULT_BOOK_URL}' target='_blank' rel='noopener'>"
        "<span class='cp-ico'>📅</span>"
        "<span class='cp-body'>"
        "<span class='cp-title'>AIスペシャリストの無料30分相談を予約する</span>"
        "<span class='cp-desc'>カレンダーから空いている日時を選ぶだけ。2〜3分で予約できます（料金はかかりません）。彦根での対面、Zoom、LINE相談から選べます。</span>"
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
        ("① まず相談（無料）", "彦根・湖東の仕事で困っていること、SNSで伸ばしたいこと、AIで試したいことを30分で整理します。"),
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
        ("制作会社・SEO会社", "制作やSEOは強いが、本人がAIを使えるようになる講習導線が薄い", "実績・講習・資料・予約を同じページに置き、内製化と外注の境目を選べる構造にする"),
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


# FAQ は本文表示と FAQPage 構造化データの両方で使う（一次情報＝LLMO引用源）。
# 地域・お悩み・補助金の検索意図を素の質問形で網羅する。
FAQ_QA = [
    ("彦根・滋賀でAIスペシャリストに相談できますか？",
     "はい。滋賀県彦根市を拠点に、彦根・湖東・東近江を中心とした対面のAI導入相談・AI講習・個別相談を行っています。京都・大阪・名古屋までは出張可、リモートなら全国対応します。"),
    ("AIスペシャリストには何を頼めますか？",
     "AIツールの使い方だけでなく、業務整理、AIに任せる範囲の設計、社内手順化、Web/予約/ブログ/SNSへの展開、公開前確認、定着まで相談できます。エンジニア経験とコンサル経験を合わせて、実装と運用の両方を見ます。"),
    ("Codex準備会とCodex実践会はどう違いますか？",
     "レベルは理解度で分けます。Codex準備会は60分2,200円で、ログイン、作業フォルダ選択、秘密情報を入れない権限設計、最初の小さな依頼、差分確認、ブラウザ表示確認、独立レビュー、AGENTS.md、公式アップデート確認先までを整えます。Codex実践会は120分5,500円で、Claude Codeとの使い分け、ページ、資料、コード、画像生成プロンプト、動画台本、運用マニュアルなどの成果物作成まで進めます。AIコーディング講習は120分11,000円で、Codex導入、Claude Code併用、画像生成、本物のエンジニア像、レベルマップ、専門用語、設計・データ・運用・セキュリティ、実装ループ、公開前確認までを体系的に扱います。"),
    ("AIコーディング講習では何を学びますか？",
     "Codexを、相談、実装、確認、公開を一緒に進める作業者として使うための総合講習です。Claude Codeとの役割分担、画像生成の依頼と採用判断、AI時代の本物のエンジニア像、AIオペレーターからアーキテクトまでのレベルマップ、目的理解、設計、データ、運用、セキュリティを扱います。専門用語は省かず、HTML/CSS/JavaScript/API/DB/Git、認証、認可、Cloudflare、DNS、CDN、WAF、SQLインジェクション、負荷試験などを、AIの成果物を判断する地図として学びます。依頼文、差分確認、ブラウザ表示、独立レビュー、本番URL確認までを120分で通します。料金は11,000円で、専用のSquare予約メニューから申し込めます。"),
    ("受講資料はあとから見返せますか？",
     "はい。受講で使った資料、プロンプト、実例、動画、スライドは資料センターとして整理し、あとから復習できるようにします。受講前に内容を確認したい方も、受講資料ページから雰囲気を見られます。"),
    ("Reels や YouTube の集客にも使えますか？",
     "使えます。1つの講習テーマから、Reels/Shorts用の短い台本、YouTubeタイトル・説明欄・チャプター、サイト内の動画専用ページ、FAQ、ブログ要約まで展開する流れを作ります。"),
    ("LLMO やAI検索に強いサイトにできますか？",
     "できます。地域名、講師の一次経験、料金、対応範囲、実例、FAQ、構造化データを整理し、AIが回答に引用しやすい形で公開します。大量の自動生成ではなく、講習と実例に基づく一次情報を重視します。"),
    ("料金はどれくらいですか？",
     "AI無料相談 とりあえず30分は無料、Codex準備会60分は2,200円、Codex実践会120分は5,500円、AIコーディング講習120分は11,000円、AI個別相談 しっかり60分は5,500円です。AI伴走支援 いっしょに導入は月額10万円×6ヶ月が目安で、月額決済はStripe Checkoutで行います。LP制作は1本18〜30万円が目安。多くは補助金併用を前提に組みます。"),
    ("補助金は使えますか？滋賀の事業者でも対象ですか？",
     "講習・伴走パックは「デジタル化・AI導入補助金」や滋賀県・彦根市の補助金の対象になります。補助率は小規模事業者で最大4/5、実質負担が1/3以下になるケースが多いです。申請からツール選定・実装・定着まで一気通貫で支援します。"),
    ("パソコンやスマホが苦手ですが、大丈夫ですか？",
     "大丈夫です。スマホで文字が打てれば始められます。専門用語は使わず、画面を一緒に見ながら進めます。「こんなことも聞いていいの？」というレベルから歓迎します。"),
    ("AIを仕事で使いたいのですが、何から始めれば？",
     "毎日やっている作業で「これ、同じような文章を毎回書いてるな」と思うものを1つ思い浮かべてください。問い合わせの返信・見積の文面・日報など、決まり文句の多い仕事から始めると、最初の30分でAIが役に立つのを実感できます。むずかしいことは後でOKです。"),
    ("特定の人しかできない仕事が多くて困っています。効きますか？",
     "そこが得意分野です。「あの人がいないと回らない」作業をAIと手順書に置き換え、誰でもできる形にします。たとえば請求書づくりが月8時間→1時間に減った例があります。"),
    ("出張やオンラインだけの依頼も可能ですか？",
     "可能です。滋賀県外への出張AI研修、オンライン完結の伴走、単発の講演・登壇いずれも対応します。まずは無料の30分相談でご要望をお聞かせください。"),
]


# 受講者の声。形式: {"quote": 一言, "who": "彦根市・建設業・50代", "before_after": "見積作成 月4時間→30分"}
# ★VOICES_ARE_SAMPLE = True の間は「掲載イメージ（実際の声に差し替え予定）」と明示し、虚偽表示を避ける。
#   CEO が実際の受講者から許諾を得た声に差し替えたら VOICES_ARE_SAMPLE = False にする（注記が消える）。
VOICES_ARE_SAMPLE = True
VOICES: list[dict] = [
    {
        "quote": "パソコンも苦手な自分が、見積書をAIに作ってもらえるようになりました。何より「これならできる」と思えたのが大きい。",
        "who": "彦根市・建設業・50代",
        "before_after": "見積作成 1件40分 → 10分",
    },
    {
        "quote": "毎日の問い合わせ返信が苦痛でしたが、AIが下書きしてくれるので、確認して送るだけ。夜に持ち帰る仕事が減りました。",
        "who": "東近江市・小売業・40代",
        "before_after": "問い合わせ対応 1日2時間 → 30分",
    },
    {
        "quote": "「AIなんて大企業のもの」と思っていました。対面でその場で一緒に作ってもらえたので、置いていかれずに済みました。",
        "who": "彦根市・サービス業・60代",
        "before_after": "AI利用ゼロ → 毎日活用",
    },
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
    """講師紹介+経歴の統合要約セクション。
    speaker.md の役職とプロフィール冒頭 + profile.yaml の stats を一体で表示し、
    詳細は「もっと詳しく」ボタンで speaker.html / profile.html へ誘導する。"""
    sp = _load_speaker()
    prof = _load_profile()
    name = html.escape(sp.get("name") or OWNER_NAME)
    role = html.escape(sp.get("role") or "")
    import re as _re
    intro_raw = sp.get("intro") or ""
    intro = html.escape(intro_raw)
    # **強調** を <strong> に変換（Markdown は要約段階で残ってしまうため）
    intro = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", intro)
    role_html = f"<p style='font-weight:700;color:var(--primary);margin:0 0 16px;'>{role}</p>" if role else ""
    intro_html = f"<p style='line-height:1.9;'>{intro}</p>" if intro else ""

    parts = [
        "<div class='profile-block' style='display:block;'>"
        "<div class='speaker-intro-grid'>"
        "<div>"
        f"<h3>{name}</h3>"
        f"{role_html}"
        f"{intro_html}"
        "<p style='font-weight:700;color:var(--text);margin-top:16px;'>「現場で使えるAIを、実例で教える。」</p>"
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

    stats = (prof.get("stats") or []) if prof else []
    if stats:
        parts.append("<div class='stats-strip' style='margin:32px 0 8px;'>")
        for st in stats[:4]:
            num = html.escape(str(st.get("number") or ""))
            lbl = html.escape(str(st.get("label") or ""))
            parts.append(
                f"<div class='stat'><div class='num'>{num}</div>"
                f"<div class='label'>{lbl}</div></div>"
            )
        parts.append("</div>")

    parts.append(
        "<div style='display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-top:24px;'>"
        "<a class='btn btn-primary' href='/speaker.html'>🎤 詳しい経歴を見る</a>"
        "</div>"
        "</div>"
    )
    return "".join(parts)

def _render_portfolio_section() -> str:
    """L3 制作実績セクション。portfolio.yaml の全件をカードグリッドで。
    詳細は portfolio.html へ誘導。"""
    items = _load_portfolio()
    if not items:
        return ""
    parts: list[str] = ["<div class='pf-grid'>"]
    for it in items:
        name = html.escape(str(it.get("name") or ""))
        url = html.escape(str(it.get("url") or ""), quote=True)
        summary = html.escape(str(it.get("summary") or ""))
        category = html.escape(str(it.get("category") or ""))
        status = str(it.get("status") or "")
        tech = it.get("tech") or []
        since = html.escape(str(it.get("since") or ""))
        status_label = {"live": "公開中", "dev": "開発中", "retired": "終了"}.get(status, "")
        status_cls = {"live": "", "dev": " dev", "retired": " retired"}.get(status, "")
        chips = ""
        if category:
            chips += f"<span class='pf-chip cat'>{category}</span>"
        for tg in (tech if isinstance(tech, list) else [])[:3]:
            chips += f"<span class='pf-chip'>{html.escape(str(tg))}</span>"
        if status_label:
            chips += f"<span class='pf-chip{status_cls}'>{status_label}</span>"
        host = url.replace("https://", "").replace("http://", "").rstrip("/")
        is_link = bool(it.get("url"))
        tag = "a" if is_link else "div"
        href = f" href='{url}' target='_blank' rel='noopener'" if is_link else ""
        since_html = f"<span class='pf-host'>since {since}</span>" if since else ""
        parts.append(
            f"<{tag} class='pf-card'{href}>"
            f"<div class='pf-title'>{name}</div>"
            f"<div class='pf-host'>{html.escape(host)}</div>"
            f"<div class='pf-sum'>{summary}</div>"
            f"<div class='pf-meta'>{chips}</div>"
            f"{since_html}"
            f"</{tag}>"
        )
    parts.append("</div>")
    return "".join(parts)


# カテゴリ別サムネ: 実画面のスクショではなく、ブランドカラーのSVGモチーフで体裁を統一する。
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


def _works_thumb_svg(category: str, name: str) -> str:
    icon, c1, c2 = _WORKS_THUMB.get(category, _WORKS_THUMB_DEFAULT)
    # gradient id を name から安全に生成（重複しても描画は問題ないが一応ユニーク化）
    gid = "g" + str(abs(hash((category, name))) % 100000)
    return (
        f"<span class='pf-thumb' aria-hidden='true'>"
        f"<svg viewBox='0 0 320 150' preserveAspectRatio='xMidYMid slice' xmlns='http://www.w3.org/2000/svg'>"
        f"<defs><linearGradient id='{gid}' x1='0' y1='0' x2='1' y2='1'>"
        f"<stop offset='0' stop-color='{c1}'/><stop offset='1' stop-color='{c2}'/></linearGradient></defs>"
        f"<rect width='320' height='150' fill='url(#{gid})'/>"
        # 軽い光のドット（装飾）
        f"<circle cx='270' cy='30' r='46' fill='#fff' opacity='0.10'/>"
        f"<circle cx='40' cy='128' r='34' fill='#fff' opacity='0.08'/>"
        f"<text x='160' y='95' font-size='54' text-anchor='middle'>{icon}</text>"
        f"</svg></span>"
    )


def _render_works_section() -> str:
    """制作実績セクション（TOP内サマリ）。portfolio.yaml から live のみを抜き、
    各カードは公開サイト本体へ直リンク。ページ遷移を減らすため一覧をインライン掲載。"""
    items = [p for p in _load_portfolio() if str(p.get("status") or "live") != "retired"]
    if not items:
        return ""
    # 横スライド（カルーセル）。左右の矢印 + scroll-snap で見やすく。
    parts = [
        "<div class='pf-carousel-wrap'>"
        "<button type='button' class='pf-arrow pf-prev' aria-label='前へ' data-dir='-1'>‹</button>"
        "<div class='pf-carousel' id='works-carousel'>"
    ]
    for p in items:
        name = html.escape(str(p.get("name") or p.get("slug") or ""))
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
        href = html.escape(url, quote=True) if url else "/portfolio.html"
        target = " target='_blank' rel='noopener'" if url else ""
        thumb_url = str(p.get("thumbnail") or "").strip()
        if thumb_url:
            thumb = (f"<span class='pf-thumb' aria-hidden='true'>"
                     f"<img src='{html.escape(thumb_url, quote=True)}' alt='' loading='lazy' decoding='async'></span>")
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
    """受講資料セクション。最新の受講資料を先頭にし、AIコーディング講習 120分は独立資料として残す。"""
    pmap_card = {
        "title": "AIコーディング講習 120分",
        "icon": "🧭",
        "date": "2026-06-06",
        "summary": "Codex導入、Claude Code併用、画像生成、AI時代の本物のエンジニア像、レベルマップ、設計・データ・運用・セキュリティ、実装、公開までを段階的に学ぶ講習LP。",
        "href": "/programming-map.html",
    }
    lecs = list(_load_all_lectures()) + [pmap_card]
    parts: list[str] = []
    parts.append("<div class='lecture-grid'>")
    for lec in lecs:
        parts.append(_render_lecture_card(lec))
    parts.append("</div>")
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
            "summary": summary,
            "image": str(meta.get("image") or "").strip() or _first_markdown_image(body),
            "href": f"/blog/{f.stem}.html",
        })
        if len(items) >= limit:
            break
    return items


def _render_blog_card(post: dict, *, extra_class: str = "") -> str:
    title = html.escape(str(post.get("title") or "ブログ記事"))
    href = html.escape(str(post.get("href") or "/blog/index.html"), quote=True)
    date = html.escape(str(post.get("date") or ""))
    summary = html.escape(str(post.get("summary") or ""))
    image = str(post.get("image") or "").strip()
    cls = "blog-card" + (f" {extra_class}" if extra_class else "")
    media = ""
    if image:
        safe_image = html.escape(image, quote=True)
        media = f"<div class='blog-card-media'><img src='{safe_image}' alt='' loading='lazy' decoding='async'></div>"
    return (
        f"<a class='{cls}' href='{href}'>"
        f"{media}"
        "<div class='blog-card-body'>"
        f"<div class='blog-card-meta'><span>{date or 'BLOG'}</span></div>"
        f"<h3>{title}</h3>"
        + (f"<p>{summary}</p>" if summary else "")
        + "<span class='blog-card-more'>読む</span>"
        "</div>"
        "</a>"
    )


def _render_blog_teaser() -> str:
    posts = _load_recent_blog_posts(limit=6)
    if not posts:
        return ""
    featured = posts[0]
    feature_title = html.escape(str(featured.get("title") or "AIスペシャリストの実践記事"))
    feature_summary = html.escape(str(featured.get("summary") or "AI導入、講習、制作、業務改善の実践記録。"))
    feature_href = html.escape(str(featured.get("href") or "/blog/index.html"), quote=True)
    feature_date = html.escape(str(featured.get("date") or "BLOG"))
    feature_image = html.escape(str(featured.get("image") or "/img/hero-codex-claude-imagegen-20260616.png"), quote=True)
    cards = [_render_blog_card(post, extra_class="fade-up d2") for post in posts[1:]]
    return (
        "<section class='block' id='blog'>"
        "<div class='blog-section-head'>"
        "<div>"
        "<p class='section-heading fade-up'>BLOG / PROOF</p>"
        "<h2 class='section-title fade-up d1'>AIスペシャリストの実践ブログ</h2>"
        "<p class='section-sub fade-up d2'>講習で話す内容、実際に作っている業務システム、AI時代のエンジニア像を記事で確認できます。営業前の信頼材料として、トップ上部に複数掲載しています。</p>"
        "</div>"
        "<a class='btn btn-secondary fade-up d2' href='/blog/index.html'>すべての記事を見る</a>"
        "</div>"
        f"<a class='blog-feature fade-up d2' href='{feature_href}'>"
        "<div class='blog-feature-copy'>"
        f"<div class='blog-feature-meta'><span>{feature_date}</span><span>FEATURED</span></div>"
        f"<h3>{feature_title}</h3>"
        f"<p>{feature_summary}</p>"
        "<span class='blog-card-more'>特集記事を読む</span>"
        "</div>"
        f"<div class='blog-feature-visual'><img src='{feature_image}' alt='' loading='lazy' decoding='async'></div>"
        "</a>"
        "<div class='blog-list'>"
        + "".join(cards) +
        "</div>"
        "</section>"
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
    icon_html = f"<span class='lecture-icon'>{icon}</span>" if icon else ""
    date_html = f"<div class='lecture-date'>📅 {date}</div>" if date else ""
    summary_html = f"<div class='lecture-summary'>{summary}</div>" if summary else ""
    return (
        f"<a class='lecture-card' href='{href}'>"
        f"<div class='lecture-title'>{icon_html}{title}</div>"
        f"{date_html}{summary_html}</a>"
    )


def render_portal(businesses: list[dict], recent_lectures: list[dict]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    title = "AIスペシャリスト 彦根｜滋賀のAI導入相談・生成AI講習・実装支援"
    desc = "彦根・滋賀でAIを学びたい企業・個人へ。エンジニア経験とコンサル経験を持つAIスペシャリストが、生成AI講習、Codex、Claude Code、画像生成、業務改善、ホームページ制作、社内定着まで伴走します。"

    parts: list[str] = []
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>" + FAVICON_HEAD_HTML)
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append("<meta name='theme-color' content='#F7F8FC'>")
    # 案A: 和文明朝の大見出し + monospace ラベル用に Google Fonts を読み込む
    parts.append("<link rel='preconnect' href='https://fonts.googleapis.com'>")
    parts.append("<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>")
    parts.append("<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;700;900&family=JetBrains+Mono:wght@500;700&display=swap'>")
    parts.append(f"<title>{html.escape(title)}</title>")
    parts.append(f"<meta name='description' content='{html.escape(desc, quote=True)}'>")
    parts.append(f"<link rel='canonical' href='{html.escape(SITE_URL + '/', quote=True)}'>")
    parts.append(_build_ogp(title, desc, SITE_URL + "/"))
    parts.append(f"<script type='application/ld+json'>{_build_jsonld_website()}</script>")
    parts.append(f"<style>{PORTAL_CSS}{BLOG_TEASER_CSS}</style>")
    parts.append("</head><body>")

    parts.append(_render_header())

    parts.append("<div class='container'>")
    parts.append(ADMIN_BUTTON_HTML)

    parts.append(_render_hero())

    # 1. AIスペシャリストの定義と専門性
    parts.append(_render_specialist_value())

    # 2. ブログを信頼材料として上部に出す
    parts.append(_render_blog_teaser())

    # 3. 最初の選び方
    parts.append("<section class='block block-tight' id='start'>")
    parts.append("<p class='section-heading fade-up'>START HERE</p>")
    parts.append("<h2 class='section-title fade-up d1'>最初の一歩を、4つに絞る</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI導入を相談する、講習会を選ぶ、実践ブログで確かめる、受講資料を先に読む。初回訪問で迷わないよう、営業の入口を上部に集約しました。</p>")
    parts.append(_render_path_selector())
    parts.append("</section>")

    # 4. 受講プラン — メインCTA
    parts.append("<section class='block' id='packages'>")
    parts.append("<p class='section-heading fade-up'>AI LESSON / SUPPORT</p>")
    parts.append("<h2 class='section-title packages-title fade-up d1'>AI導入・講習・実装支援のプラン</h2>")
    parts.append("<p class='section-sub fade-up d2'>無料相談、個別相談、伴走支援、Codex準備会、Codex実践会、AIコーディング講習を、目的と到達点で選べるように整理しています。学びたい方も、社内に定着させたい企業も、各プランから関連資料を確認して予約できます。</p>")
    parts.append(_render_courses_packages())
    parts.append("</section>")

    # 5. ホームページ制作ショールーム
    parts.append("<section class='block web-showcase-block' id='web-showcase'>")
    parts.append("<p class='section-heading fade-up'>WEB / SYSTEM</p>")
    parts.append("<h2 class='section-title fade-up d1'>AIを入れるホームページと業務システムも作る</h2>")
    parts.append("<p class='section-sub fade-up d2'>店舗LP、企業サイト、EC、講習資料、管理画面、SNS改善まで。AIスペシャリストとして、相談だけでなく実装できることを用途別に提示します。</p>")
    parts.append(_render_web_showcase())
    parts.append("</section>")

    # 6. 制作実績（TOP内にサマリを掲載・各カードは公開サイト本体へ直リンク）
    parts.append("<section class='block' id='works'>")
    parts.append("<p class='section-heading fade-up'>WORKS</p>")
    parts.append("<h2 class='section-title fade-up d1'>AI導入に使える実例サイト</h2>")
    parts.append("<p class='section-sub fade-up d2'>説明だけではなく、講師が実際に構築・運用しているサイトや業務システムを教材として使います。経験があるから、AIに任せる部分と人が見る部分を具体化できます。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_works_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-secondary' href='/portfolio.html'>📂 実績の詳細・技術スタックを見る →</a></div>")
    parts.append("</section>")

    # 7. ご依頼の流れ
    parts.append("<section class='block' id='flow'>")
    parts.append("<p class='section-heading'>FLOW</p>")
    parts.append("<h2 class='section-title'>相談から実装・社内定着まで</h2>")
    parts.append("<p class='section-sub'>一度聞いて終わりではなく、受講内容を資料センター、ブログ、予約導線、業務システムに変換します。</p>")
    parts.append(_render_flow())
    parts.append("</section>")

    # 8. 受講資料（TOP内にサマリを掲載）
    parts.append("<section class='block' id='lectures'>")
    parts.append("<p class='section-heading fade-up'>MATERIALS</p>")
    parts.append("<h2 class='section-title fade-up d1'>予約前に読める受講資料</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）・Codex実践会・Claude Code併用・画像生成・AIコーディングを、受講後も見返せる形で整理しています。資料を読んだら、上の講習/伴走プランへ戻って予約できます。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_lectures_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-primary' href='#packages'>受講プランへ戻る →</a><a class='btn btn-secondary' href='/lectures/index.html'>📚 受講資料の一覧を見る →</a></div>")
    parts.append("</section>")

    # 9. 講師紹介（誰が教えるか）
    parts.append("<section class='block' id='speaker'>")
    parts.append("<p class='section-heading fade-up'>SPEAKER</p>")
    parts.append("<h2 class='section-title fade-up d1'>AIスペシャリストとしての経歴</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI活用の啓発・講習・地域コミュニティ運営・複数事業のマーケ支援を行う実践者。エンジニアとコンサルタントの両方の視点で支援します。</p>")
    parts.append(_render_speaker_section())
    parts.append("</section>")

    # 6b. 受講者の声（信頼の証拠・実データがある時だけ表示）
    voices_html = _render_voices()
    if voices_html:
        parts.append("<section class='block' id='voices'>")
        parts.append("<p class='section-heading fade-up'>VOICES</p>")
        parts.append("<h2 class='section-title fade-up d1'>受講した方の声</h2>")
        parts.append("<p class='section-sub fade-up d2'>あなたと同じ「AIは苦手」だった方が、何をできるようになったか。</p>")
        if VOICES_ARE_SAMPLE:
            parts.append("<p class='voices-sample-note fade-up d2'>※ 掲載イメージです（実際の受講者の声に差し替え予定）。</p>")
        parts.append(voices_html)
        parts.append("</section>")

    # 10. FAQ（疑問解消）
    parts.append("<section class='block' id='faq'>")
    parts.append("<p class='section-heading'>FAQ</p>")
    parts.append("<h2 class='section-title'>AIスペシャリスト相談のよくある質問</h2>")
    parts.append(_render_faq())
    parts.append("</section>")

    # 11. 競合比較と集客施策
    parts.append("<section class='block' id='growth'>")
    parts.append("<p class='section-heading fade-up'>DAILY DESIGN LOOP</p>")
    parts.append("<h2 class='section-title fade-up d1'>検索・SNS反響で、AI相談ページを育てる</h2>")
    parts.append("<p class='section-sub fade-up d2'>公的DX相談・パソコン教室・大手AI研修・制作会社と比較し、さらにYouTube/Shorts/SNSの反応を見て、入口、FAQ、ブログ導線をチューニングします。</p>")
    parts.append(_render_growth_plan_section())
    parts.append("</section>")

    # 12. お問い合わせ（予約）
    parts.append("<section class='block' id='contact'>")
    parts.append("<p class='section-heading fade-up'>CONTACT</p>")
    parts.append("<h2 class='section-title fade-up d1'>彦根でAIを学びたい、業務を改善したい方へ</h2>")
    parts.append("<p class='section-sub fade-up d2'>企業も個人も、まずは無料30分相談から。講習に参加するか、AI個別相談で整理するか、伴走で社内定着まで進めるかを一緒に決めましょう。</p>")
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
    # AIコーディング講習 120分は受講資料カードとして残すが、最新資料を先頭にする
    pmap_card = {
        "title": "AIコーディング講習 120分",
        "icon": "🧭",
        "date": "2026-06-06",
        "summary": "Codex導入、Claude Code併用、画像生成、AI時代の本物のエンジニア像、レベルマップ、設計・データ・運用・セキュリティ、実装、公開までを段階的に学ぶ講習LP。",
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
