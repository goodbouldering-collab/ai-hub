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

SITE_URL = os.environ.get("AIHUB_SITE_URL", os.environ.get("AIWATCH_SITE_URL", "https://ai-hub-jp.vercel.app")).rstrip("/")

OWNER_NAME = "由井 辰美"
OWNER_EMAIL = "goodbouldering@gmail.com"
SITE_BRAND = "AI相談 彦根"
SITE_LEGACY_NAME = "AIハブ"
OWNER_SUBTITLE = "クライミング歴30年・9事業を回す滋賀のAI講師"
OWNER_TAGLINE = "AIを聞いて終わりにせず、講習・実例・資料で仕事に入れる"


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
    "<link rel='alternate icon' type='image/svg+xml' href='/favicon.svg'>"
    "<link rel='apple-touch-icon' href='/apple-touch-icon.svg'>"
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


OG_IMAGE_URL = SITE_URL + "/img/hero-ai-consult-hikone.png"


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
    LocalBusiness(地域シグナル) / Person(異色の権威) / WebSite / Service×4(価格付き Offer) /
    FAQPage(一次情報) / BreadcrumbList を相互参照させ、SEO・LLMO 両面の引用源にする。"""
    org_id = SITE_URL + "/#business"
    person_id = SITE_URL + "/#yui"
    web_id = SITE_URL + "/#website"

    local_business = {
        "@type": ["ProfessionalService", "LocalBusiness"],
        "@id": org_id,
        "name": SITE_BRAND,
        "alternateName": [SITE_LEGACY_NAME, "AI Hub Hikone", "AI講習 彦根"],
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
        "description": "滋賀県彦根市を拠点に、中小事業者・地域団体・個人事業者向けのAI相談、生成AI講習、Codex実践講習、講習資料公開、実例紹介、Web/業務システム制作、補助金を使ったAI導入支援を行う。9事業を実際に回す現役オーナーが、相談から講習、実装、公開、運用定着まで伴走する。",
        "knowsAbout": [
            "AI相談", "生成AI講習", "ChatGPT", "Claude Code", "Codex",
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
        "image": SITE_URL + "/img/speaker-portrait.webp",
        "worksFor": {"@id": org_id},
        "knowsAbout": ["生成AI", "クライミング", "店舗経営", "マーケティング", "補助金活用"],
        "description": "クライミング歴30年。ボルダリングカフェ「グッぼる」をはじめ9事業を経営しながら、滋賀・彦根の中小事業者にAI相談、生成AI講習、Codex実践、SNS/LLMO導線づくりを教える。経営者でありコードを書く実装者でもある二重性が強み。",
    }

    website = {
        "@type": "WebSite",
        "@id": web_id,
        "name": SITE_BRAND,
        "url": SITE_URL,
        "inLanguage": "ja",
        "publisher": {"@id": org_id},
        "description": "滋賀・彦根の中小事業者向けAI相談、講習募集、講習資料、実例、講師紹介、AI/SNS/LLMO情報の資料センター。",
    }

    codex_prep_title = "Codex準備 90分"
    codex_practice_title = "Codex実践 120分"
    free_consult_title = "AI無料相談 とりあえず30分"
    consult_title = "エージェント組織構築相談"
    support_title = "AI伴走支援 いっしょに導入"

    # 受講プランを Service + Offer として構造化（_render_packages の items と整合）
    plans = [
        (codex_prep_title, "Codex準備 導入と習得の流れに沿って、ChatGPTログイン、作業フォルダ選定、最初の小さな依頼、差分確認、独立レビュー、AGENTS.md、公式アップデート確認先までを90分で整える無料の準備講習。", "0", "0", "Course"),
        (codex_practice_title, "Codexで持ち込み課題を進め、ページ、資料、コード、動画台本などの成果物を120分で作る実践講習。", "5500", "5500", "Course"),
        (free_consult_title, "来店またはオンラインで、AI導入の入口を30分で整理する無料相談。講習や伴走の前に、今の課題と次の一手を確認する。", "0", "0", "BusinessCoaching"),
        (consult_title, "社内や事業内で動くAIエージェントの役割分担、権限、手順、チェック体制を設計し、エージェント組織として回す相談。", "4400", "4400", "BusinessCoaching"),
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
        services.append({
            "@type": "Service",
            "serviceType": stype,
            "name": name,
            "description": desc,
            "provider": {"@id": org_id},
            "areaServed": {"@type": "AdministrativeArea", "name": "滋賀県"},
            "offers": offer,
        })

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
            {"@type": "ListItem", "position": 3, "name": "制作実績", "item": SITE_URL + "/#works"},
            {"@type": "ListItem", "position": 4, "name": "講師紹介", "item": SITE_URL + "/#speaker"},
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
    return {
        "name": str(meta.get("name") or OWNER_NAME),
        "role": str(meta.get("role") or ""),
        "intro": intro,
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
    """講習資料を全件（新しい順）。LP の講習資料セクション用。"""
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
  background: rgba(255,255,255,.92);
  border-bottom: 1px solid rgba(7,26,58,.10);
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  transition: background .3s, box-shadow .3s, backdrop-filter .3s;
}
header.site-header.scrolled {
  background: rgba(255,255,255,.96);
  box-shadow: 0 12px 34px rgba(7,26,58,.08);
}
.site-header-inner {
  max-width: 1280px; margin: 0 auto;
  padding: 12px 24px;
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
  background: linear-gradient(135deg, #FFFFFF 0%, #EAF8FF 58%, #EAFBF7 100%);
  border: 1px solid rgba(0,95,158,.18);
  box-shadow: 0 10px 24px rgba(0,95,158,.12), inset 0 1px 0 rgba(255,255,255,.95);
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
.site-logo-by { color: var(--muted); font-weight: 600; font-size: 12px; margin-left: 4px; white-space: nowrap; }
@media (max-width: 720px) {
  .wordmark .word-en, .site-logo-by { display: none; }
}
.site-nav { display: flex; align-items: center; gap: 12px; }
.site-nav a.nav-link {
  font-size: 12.5px; font-weight: 800; color: var(--text-soft);
  text-decoration: none; transition: color .2s;
}
.site-nav a.nav-link:hover { color: var(--primary); }
.site-nav .menu-wrap { position: relative; }
.site-nav .menu-toggle {
  display: inline-flex; align-items: center; gap: 4px;
  background: transparent; border: none; cursor: pointer;
  font: inherit; font-size: 13px; font-weight: 800; color: var(--text-soft);
  padding: 0;
}
.site-nav .menu-toggle:hover { color: var(--primary); }
.site-nav .menu-toggle .chev { transition: transform .2s; }
.site-nav .menu-toggle[aria-expanded="true"] .chev { transform: rotate(180deg); }
.site-nav .menu-drop {
  position: absolute; right: 0; top: calc(100% + 10px);
  min-width: 220px; padding: 8px;
  background: rgba(255,255,255,.94); border: 1px solid var(--line);
  border-radius: var(--radius-sm); box-shadow: var(--shadow-card);
  backdrop-filter: blur(18px) saturate(140%);
  display: none;
}
.site-nav .menu-drop.open { display: block; }
.site-nav .menu-drop a {
  display: block; padding: 9px 14px; border-radius: 10px;
  font-size: 13px; font-weight: 600; color: var(--text-soft);
  text-decoration: none;
}
.site-nav .menu-drop a:hover { background: var(--primary-bg); color: var(--primary); }
/* ドロップ内で管理ログインを区切って格下げ表示 */
.site-nav .menu-drop a.menu-drop-sep {
  margin-top: 6px; padding-top: 12px; border-top: 1px solid var(--line);
  font-size: 12px; color: var(--muted);
}
/* ヘッダー右端の主CTA: 無料相談（グラデ・最も目立たせる） */
.site-nav .nav-cta {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border-radius: var(--radius-sm);
  background: var(--grad); color: #fff;
  font-size: 13px; font-weight: 800;
  text-decoration: none;
  box-shadow: 0 6px 22px rgba(40,84,197,.24), inset 0 1px 0 rgba(255,255,255,.25);
  transition: transform .2s, box-shadow .2s, filter .2s;
}
.site-nav .nav-cta:hover { transform: translateY(-1px); filter: brightness(1.08); box-shadow: 0 12px 36px rgba(15,143,114,.22), inset 0 1px 0 rgba(255,255,255,.30); }
/* モバイル: 管理ログインは控えめなテキストリンクに格下げ */
.mobile-nav .mobile-admin-link {
  display: block; padding: 10px 4px; margin-top: 4px;
  font-size: 12.5px; color: var(--muted); text-decoration: none;
  border-bottom: none;
}

.mobile-toggle {
  display: none; padding: 8px; border-radius: var(--radius-sm);
  background: var(--glass-bg); border: 1px solid var(--line);
  cursor: pointer;
}
.mobile-nav {
  display: none; padding: 16px 24px 24px;
  background: var(--bg-white); backdrop-filter: blur(18px);
  border-top: 1px solid var(--line);
}
.mobile-nav.open { display: block; }
.mobile-nav a {
  display: block; padding: 12px 4px; font-size: 15px; font-weight: 600;
  color: var(--text); text-decoration: none; border-bottom: 1px solid var(--line);
}
.mobile-nav a:last-child { border-bottom: none; }
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
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}
/* 診断結果で該当レベル以外を減光（.pkg-filter-active 時のみ） */
.packages-grid.pkg-filter-active .pkg-card { opacity: .34; transition: opacity .35s ease; }
.packages-grid.pkg-filter-active .pkg-card.pkg-match { opacity: 1; outline: 2px solid var(--primary); outline-offset: 2px; }
.pkg-card {
  grid-column: span 3;
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
.pkg-featured,
.pkg-wide { grid-column: span 6; }
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
.pkg-fit,
.pkg-req {
  display: grid;
  gap: 6px;
  margin: 2px 0 0;
  padding: 0;
  list-style: none;
}
.pkg-fit li,
.pkg-req li {
  position: relative;
  padding-left: 18px;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text);
}
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
.packages-note {
  margin-top: 22px; padding: 16px 20px;
  background: var(--grad-soft); border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  font-size: 13px; line-height: 1.75; color: var(--text);
}
@media (max-width: 1060px) {
  .pkg-card, .pkg-featured, .pkg-wide { grid-column: span 6; }
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
.section-more { display: flex; justify-content: center; margin-top: 28px; }
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


def _render_header() -> str:
    """N デザイン風 fixed ヘッダー。スクロールで white/90 + blur に切替。"""
    return (
        "<header class='site-header' id='site-header'>"
        "<div class='site-header-inner'>"
        "<a class='site-logo' href='/' aria-label='AI相談 彦根 トップへ'>"
        "<span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>相</span></span>"
        "<span class='wordmark'><span class='word-ai'>AI相談</span><span class='word-hub'>彦根</span><span class='word-en'>AI CONSULT</span></span>"
        "<span class='site-logo-by'>講師 由井辰美</span>"
        "</a>"
        "<nav class='site-nav' aria-label='メインナビ'>"
        "<a class='nav-link' href='#packages'>受講プラン</a>"
        "<a class='nav-link' href='#usecases'>実例</a>"
        "<a class='nav-link' href='#growth'>集客施策</a>"
        "<a class='nav-link' href='#works'>制作実績</a>"
        "<a class='nav-link' href='#lectures'>講習資料</a>"
        "<a class='nav-link' href='#speaker'>講師紹介</a>"
        "<a class='nav-link' href='/watch/index.html'>AI Watch</a>"
        "<div class='menu-wrap'>"
        "<button class='menu-toggle' id='menu-toggle' aria-haspopup='menu' aria-expanded='false'>その他"
        "<svg class='chev' width='14' height='14' viewBox='0 0 20 20' fill='none' aria-hidden='true'><path d='M5 8l5 5 5-5' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        "</button>"
        "<div class='menu-drop' id='menu-drop' role='menu'>"
        "<a href='#flow'>🛠 ご依頼の流れ</a>"
        "<a href='#faq'>FAQ</a>"
        "<a href='/portfolio.html'>📂 実績の詳細</a>"
        "<a class='menu-drop-sep' href='/admin'>🔐 管理ログイン</a>"
        "</div>"
        "</div>"
        "<button type='button' class='theme-toggle' aria-label='ダークモードに切替'>🌙</button>"
        "<a class='nav-cta' href='#contact'>📩 無料相談</a>"
        "</nav>"
        "<button type='button' class='theme-toggle theme-toggle-mobile' aria-label='ダークモードに切替'>🌙</button>"
        "<button class='mobile-toggle' id='mobile-toggle' aria-label='メニュー'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'><path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg>"
        "</button>"
        "</div>"
        "<div class='mobile-nav' id='mobile-nav'>"
        "<a href='#packages'>受講プラン</a>"
        "<a href='#usecases'>実例</a>"
        "<a href='#growth'>集客施策</a>"
        "<a href='#works'>制作実績</a>"
        "<a href='#lectures'>講習資料</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='/watch/index.html'>AI Watch</a>"
        "<a href='#flow'>ご依頼の流れ</a>"
        "<a href='#faq'>FAQ</a>"
        "<a class='login-btn-mobile' href='#contact'>📩 無料で30分相談する</a>"
        "<a class='mobile-admin-link' href='/admin'>🔐 管理ログイン</a>"
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
      mobileNav.classList.toggle('open');
    });
    mobileNav.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){ mobileNav.classList.remove('open'); });
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

  // ---- テーマ切替 (デフォルトはライト。dark で暗いバリアント=data-theme属性で付与)
  (function(){
    var KEY = 'aihub-theme';
    var root = document.documentElement;
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch(e) {}
    // 保存があればそれ、無ければデフォルト light(=data-theme属性なし)
    var mode = saved === 'dark' ? 'dark' : 'light';
    function apply(m){
      if (m === 'dark') root.setAttribute('data-theme', 'dark');
      else root.removeAttribute('data-theme');
      var btns = document.querySelectorAll('.theme-toggle');
      btns.forEach(function(b){ b.textContent = (m === 'dark') ? '☀️' : '🌙'; b.setAttribute('aria-label', m === 'dark' ? 'ライトモードに切替' : 'ダークモードに切替'); });
    }
    apply(mode);
    document.addEventListener('click', function(e){
      var t = e.target.closest && e.target.closest('.theme-toggle');
      if (!t) return;
      mode = (root.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
      apply(mode);
      try { localStorage.setItem(KEY, mode); } catch(e) {}
    });
  })();

  // ---- AIレベル診断 (3段階: 初級/中級/上級。ヒーロー第1問から起動)
  (function(){
    var modal = document.getElementById('diagnoseModal');
    if (!modal) return;
    var body = modal.querySelector('.diagnose-body');

    // 各設問の選択肢にレベルスコアを持たせ、合計で初級/中級/上級を判定
    var QUESTIONS = [
      { q: 'Codex の理解度はどの段階ですか？', a: [
        { label: 'インストールから確認したい', lv: 'beginner' },
        { label: '基本は触れるので成果物を作りたい', lv: 'intermediate' },
        { label: 'エージェント組織まで作りたい', lv: 'advanced' },
      ]},
      { q: '当日いちばん進めたいことは？', a: [
        { label: 'PCとモバイルの準備を整えたい', lv: 'beginner' },
        { label: 'ページや資料などを完成させたい', lv: 'intermediate' },
        { label: 'AIの役割分担と運用設計を作りたい', lv: 'advanced' },
      ]},
      { q: 'どのスパンで取り組みたい？', a: [
        { label: 'まず90分無料で準備したい', lv: 'beginner' },
        { label: '120分で成果物を作りたい', lv: 'intermediate' },
        { label: '相談から伴走まで設計したい', lv: 'advanced' },
      ]},
    ];
    var RESULT = {
      beginner: {
        badge: 'Codex準備', title: 'インストールからモバイルまで整える',
        name: 'Codex準備 90分',
        desc: 'インストール、ログイン、作業フォルダ、最初の依頼、差分確認、モバイル確認までを無料で整えます。',
        level_id: 'beginner'
      },
      intermediate: {
        badge: 'Codex実践', title: '成果物をその場で作る',
        name: 'Codex実践 120分',
        desc: 'ページ、資料、コード、動画台本など、持ち込み課題を成果物として形にする少人数講習です。',
        level_id: 'intermediate'
      },
      advanced: {
        badge: '相談', title: 'エージェント組織を設計する',
        name: 'エージェント組織構築相談',
        desc: 'AIエージェントの役割分担、チェック体制、指示書、運用導線を事業内に組み込む方向けです。',
        level_id: 'advanced'
      }
    };
    var ORDER = ['beginner','intermediate','advanced'];

    var step = 0, scores = { beginner:0, intermediate:0, advanced:0 };

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
      step = 0; scores = { beginner:0, intermediate:0, advanced:0 };
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
    return (
        "<section class='hero' id='top'>"
        "<div class='hero-text fade-up'>"
        "<span class='eyebrow'>HIKONE AI CONSULTATION / LESSON / RESOURCE CENTER</span>"
        "<h1 class='hero-brand'>"
        "<span class='fusion-logo-large'><span class='ai'>AI相談</span><span class='pipe'>|</span><span class='hub'>彦根</span></span>"
        "<span class='hero-title-sub'><strong>聞く、試す、作る。</strong>講習資料まで残るAI相談。</span>"
        "<span class='visually-hidden'>｜彦根 AI相談、滋賀 生成AI講習、Codex講習、ChatGPT講座、AI導入支援、補助金申請サポート、LLMO対策、YouTube SEO、Reels集客</span>"
        "</h1>"
        "<p class='sub-catch'>"
        "<strong>彦根・湖東の事業者と個人向けに、AI相談、少人数講習、実例、講習資料をひとつの入口にまとめました。</strong>"
        "</p>"
        "<p class='lead'>"
        "ただ便利ツールを紹介して終わりではなく、あなたの仕事の文章、写真、SNS、YouTube、資料、予約導線、Webページまで一緒に触って、講習後も見返せる形で残します。"
        "</p>"
        "<div class='hero-actions'>"
        "<a class='btn btn-primary btn-lg' href='#contact'>無料30分相談を予約</a>"
        "<a class='btn btn-secondary btn-lg' href='#packages'>講習プランを見る</a>"
        "</div>"
        "<ul class='hero-trust'>"
        "<li>彦根で<strong>対面相談可</strong></li>"
        "<li>資料は<strong>あとで見返せる</strong></li>"
        "<li><strong>9事業</strong>を回す講師が実例で説明</li>"
        "</ul>"
        "<div class='hero-entry-strip' aria-label='AI相談 彦根の主要入口'>"
        "<a class='entry-chip' href='#packages'><b>相談・講習</b><span>初心者から実装まで</span></a>"
        "<a class='entry-chip' href='#usecases'><b>実例</b><span>仕事でどう使うか</span></a>"
        "<a class='entry-chip' href='#lectures'><b>資料センター</b><span>教材・動画・スライド</span></a>"
        "<a class='entry-chip' href='#growth'><b>集客施策</b><span>Reels / YouTube / LLMO</span></a>"
        "</div>"
        "</div>"
        "<div class='hero-photo-card fade-up d2' aria-label='AI相談 彦根の講習イメージ'>"
        "<img src='/img/hero-ai-consult-hikone.png' alt='彦根の明るい教室でAI相談と少人数講習を進めるイメージ' decoding='async' fetchpriority='high'>"
        "<span class='hero-photo-note'><i aria-hidden='true'></i>彦根でAIを一緒に触る</span>"
        "<div class='hero-photo-map' aria-hidden='true'>"
        "<svg viewBox='0 0 280 170' fill='none' xmlns='http://www.w3.org/2000/svg'>"
        "<rect x='12' y='14' width='76' height='44' rx='8' stroke='#8bdcff' stroke-width='2'/>"
        "<rect x='102' y='14' width='76' height='44' rx='8' stroke='#c8ff5f' stroke-width='2'/>"
        "<rect x='192' y='14' width='76' height='44' rx='8' stroke='#ffb3a8' stroke-width='2'/>"
        "<path class='route-line' d='M88 36H102M178 36H192' stroke='#fff' stroke-width='2'/>"
        "<text x='31' y='40' fill='#fff' font-size='12'>相談</text>"
        "<text x='121' y='40' fill='#fff' font-size='12'>講習</text>"
        "<text x='211' y='40' fill='#fff' font-size='12'>資料</text>"
        "<path class='route-line' d='M50 58C50 112 230 112 230 58' stroke='#8bdcff' stroke-width='2'/>"
        "<circle cx='50' cy='120' r='20' stroke='#c8ff5f' stroke-width='2'/>"
        "<circle cx='140' cy='134' r='23' stroke='#8bdcff' stroke-width='2'/>"
        "<circle cx='230' cy='120' r='20' stroke='#ffb3a8' stroke-width='2'/>"
        "<path d='M70 120H117M163 134H210' stroke='#fff' stroke-opacity='.72' stroke-width='2'/>"
        "<text x='36' y='124' fill='#fff' font-size='10'>SNS</text>"
        "<text x='122' y='138' fill='#fff' font-size='10'>LLMO</text>"
        "<text x='212' y='124' fill='#fff' font-size='10'>動画</text>"
        "</svg>"
        "</div>"
        "<div class='hero-mini-routes' aria-label='AI相談 彦根の主要入口'>"
        "<a href='#contact'><b>相談する</b><small>課題を整理</small></a>"
        "<a href='#packages'><b>学ぶ</b><small>講習プラン</small></a>"
        "<a href='#lectures'><b>残す</b><small>資料で復習</small></a>"
        "<a href='#growth'><b>集客</b><small>SEO/動画</small></a>"
        "</div>"
        "</div>"
        "</section>"
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
    codex_prep_title = "Codex準備 90分"
    codex_practice_title = "Codex実践 120分"
    seminar_url = "https://goodbouldering.com/?pid=188553378"
    free_consult_title = "AI無料相談 とりあえず30分"
    free_consult_url = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
    consult_title = "エージェント組織構築相談"
    support_title = "AI伴走支援 いっしょに導入"
    items = [
        {
            "icon": "⌘",
            "cat": "Codexオプション",
            "level": "準備",
            "level_id": "beginner",
            "title": codex_prep_title,
            "price": "無料",
            "duration": "90分 / 少人数",
            "subsidy": False,
            "desc": "講習ページ「Codex準備 導入と習得」の順番に沿って、開く、プロジェクトを選ぶ、小さく頼む、差分を見て採用する、公開前に独立レビューするところまでを90分で整えます。",
            "fit": ["Codexを開いたが、何から頼めばよいか分からない", "フォルダ選択・権限・秘密情報の扱いを安全にしたい", "PC/モバイル両方で、最初の成果物と確認手順を残したい"],
            "req_title": "90分で整えること",
            "requirements": [
                "ChatGPTログイン、Codex起動、プロジェクト/フォルダ選択",
                "秘密情報を避ける作業フォルダと権限の決め方",
                "最初の依頼テンプレ: 説明して、候補を出して、編集前に確認",
                "差分、ブラウザ表示、リンク・画像・文字サイズの確認",
                "AGENTS.md、独立レビュー、公式アップデート確認先の初期セット",
            ],
            "verify": "到達点は「Codexを入れた」ではなく、小さな成果物を1つ作り、差分を読んで、次に実践120分へ進める状態です。申込時に「Codex準備」を選択してください。",
            "url": seminar_url,
            "cta": "Codexメニューで準備を選ぶ",
            "variant": "featured",
        },
        {
            "icon": "▣",
            "cat": "Codexオプション",
            "level": "実践",
            "level_id": "intermediate",
            "title": codex_practice_title,
            "price": "5,500円",
            "duration": "120分 / 少人数",
            "subsidy": True,
            "desc": "Codexでページ、資料、コード、動画台本、運用マニュアルなどの成果物を作る実践講習です。理解度に合わせて、完成までの手順を一緒に進めます。",
            "fit": ["持ち込み課題を成果物にしたい", "講習中に公開物や資料を作りたい", "Codexの使い方を実務で定着させたい"],
            "req_title": "実践で扱うこと",
            "requirements": [
                "作りたい成果物、直したいページ、資料の持ち込み",
                "要件整理、依頼文、差分確認、修正指示",
                "完成物の確認と次に使えるテンプレ化",
            ],
            "verify": "Codexの申込リンクは準備と同じです。申込時に「Codex実践」をオプション選択してください。",
            "url": seminar_url,
            "cta": "Codexメニューで実践を選ぶ",
            "variant": "featured",
        },
        {
            "icon": "◧",
            "cat": "無料相談",
            "level": "入口",
            "level_id": "beginner",
            "title": free_consult_title,
            "price": "無料",
            "duration": "30分",
            "subsidy": False,
            "desc": "来店相談とオンライン相談を選べる30分の入口相談。講習・AI導入・補助金のどこから始めるかを短時間で整理します。",
            "fit": ["まず話を聞きたい", "講習か伴走か迷う", "来店またはオンラインで相談したい"],
            "url": free_consult_url,
            "cta": "無料相談を予約する",
        },
        {
            "icon": "?",
            "cat": "相談",
            "level": "上級",
            "level_id": "advanced",
            "title": consult_title,
            "price": "4,400円",
            "duration": "60分",
            "subsidy": False,
            "desc": "AIエージェントを1人の便利ツールではなく、役割を持った組織として設計する相談です。企画、調査、制作、確認、投稿、改善の担当と指示書を整理します。",
            "fit": ["社内や事業内でAIの役割分担を作りたい", "複数エージェントの指示書やチェック体制を整えたい", "成果物づくりを継続運用に変えたい"],
            "url": "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP",
            "cta": "組織構築相談を予約する",
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
            "desc": "HP公開から事務自動化まで、技術的な難所は講師が代行・支援。AI導入・デザイン内製化・経理・マーケティングを6ヶ月で定着させます。",
            "fit": ["社内にAI運用を定着させたい", "複数業務をまとめて仕組み化したい", "補助金前提で導入計画を組みたい"],
            "url": "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/V57YTNICA2KV2TN7ENARAVQE",
            "cta": "導入相談を予約する",
            "variant": "wide",
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
            f"{fit_html}"
            f"{req_html}"
            f"<a class='pkg-cta' href='{html.escape(it['url'], quote=True)}'{target_attr}>{html.escape(it['cta'])} →</a>"
            f"</div>"
            f"</div>"
        )
    parts.append("</div>")
    parts.append(
        "<div class='packages-cta-row fade-up d4'>"
        "<button type='button' class='btn btn-diagnose diagnose-open'>"
        "60秒診断｜準備・実践・組織構築のどれ？"
        "</button>"
        "<span class='packages-cta-hint'>3つの質問に答えるだけ。いまの状態に合う入口をその場で提案します。</span>"
        "</div>"
    )
    parts.append(
        "<p class='packages-note fade-up d4'>"
        "<strong>Codex講習:</strong> レベルは経験年数ではなく理解度で分けます。準備はログイン、フォルダ選択、最初の依頼、差分確認、独立レビュー、公式更新確認まで90分無料、実践は成果物作成まで120分5,500円です。"
        "Codexの申込リンクは1つに統一し、申込時に「準備」または「実践」をオプション選択します。"
        "<br><strong>相談:</strong> 相談メニューは、AIエージェントの役割分担、指示書、確認体制を組むエージェント組織構築に寄せています。"
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
        "<div class='footer-logo'><span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>相</span></span><span class='wordmark'><span class='word-ai'>AI相談</span><span class='word-hub'>彦根</span><span class='word-en'>AI CONSULT</span></span></div>"
        "<p class='footer-tagline'>滋賀・彦根の中小事業者向けに、AI相談・生成AI講習・Codex準備/実践・講習資料・Web集客支援を行う"
        "資料センター型の相談サイト。9事業を実際に回しながら、現場に居着くAIを一緒に作ります。</p>"
        "<a class='footer-cta' href='#contact'>📩 無料で30分相談する</a>"
        "</div>"
        "<nav class='footer-nav' aria-label='フッターナビ'>"
        "<span class='footer-nav-head'>メニュー</span>"
        "<a href='#packages'>受講プラン</a>"
        "<a href='#works'>制作実績</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='#lectures'>講習資料</a>"
        "<a href='#faq'>よくある質問</a>"
        "</nav>"
        "<div class='footer-nap'>"
        "<span class='footer-nav-head'>運営</span>"
        "<p>AI相談 彦根（AIハブ / クライミングコンサル）</p>"
        "<p>代表 由井 辰美</p>"
        "<p>〒522-0043<br>滋賀県彦根市岡町12番地</p>"
        f"<p><a href='mailto:{OWNER_EMAIL}'>{OWNER_EMAIL}</a></p>"
        "<p class='footer-area'>対応: 彦根・湖東・滋賀県全域 / 出張・オンライン全国</p>"
        "</div>"
        "</div>"
        f"<div class='footer-copy'>© {year} 由井 辰美 / AI相談 彦根 — 滋賀・彦根のAI相談・講習資料センター</div>"
        "</footer>"
    )


def _render_sticky_cta() -> str:
    """モバイルで常時追従する無料相談バー（スクロール中もCVできる）。"""
    return (
        "<div class='sticky-cta' id='sticky-cta' aria-hidden='false'>"
        "<div class='sticky-cta-text'><strong>彦根のAI相談は無料</strong><span>講習・資料・集客まで整理</span></div>"
        "<a class='sticky-cta-btn' href='#contact'>📩 30分相談する</a>"
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
    """メニュー集約: 実績 / 講習資料 をカードで（詳細は各ページへ）。
    ※ SNSポータル(AI Watch /watch/)は管理ページ(/admin)へ移行したため公開側には出さない。"""
    cards = [
        ("📂", "制作実績・事業ポートフォリオ",
         "運営事業・制作したサイト・生成した提案LP。すべて自分で構築・運用した実物。",
         "/portfolio.html", "実績を見る"),
        ("📚", "講習資料",
         "AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）の講習で使う資料。AIコーディング実装講習も。",
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
        "<span class='cp-title'>AI相談 彦根の無料30分相談を予約する</span>"
        "<span class='cp-desc'>カレンダーから空いている日時を選ぶだけ。2〜3分で予約できます（料金はかかりません）。相談は対面・Zoom・LINEから選べます。</span>"
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
        ("② 講習で一緒に触る", "ChatGPT / Codex / NotebookLM / 画像生成などを、画面を見ながら実際の仕事に当てはめます。"),
        ("③ 資料として残す", "講習で使った手順、プロンプト、動画、実例を資料センターに残し、あとから復習できるようにします。"),
        ("④ 集客へつなげる", "Reels、YouTube、ブログ、Googleビジネスプロフィール、LLMO向けFAQへ展開し、検索とAI回答に残します。"),
    ]
    parts = ["<div class='flow-list'>"]
    for title, body in steps:
        parts.append(
            f"<div class='flow-step'><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_usecases_section() -> str:
    """講習で扱う実例。相談者が自分ごと化しやすい業務別メニューにする。"""
    items = [
        ("文章", "問い合わせ返信・見積文・募集文", "いつも似た文章を書く仕事を、AIの下書きと確認フローに変える。"),
        ("写真", "商品写真・講習告知・サムネ", "生成/編集した写真を、サイト・Instagram・YouTubeサムネに展開する。"),
        ("資料", "講習資料・議事録・マニュアル", "NotebookLMやCodexで、資料を質問できる状態にして属人化を減らす。"),
        ("集客", "Reels・YouTube・SEO/LLMO", "1本の実例から、ショート動画、説明ページ、FAQ、構造化データへ分解する。"),
        ("実装", "Webページ・予約・申込導線", "相談から申込までのページ、フォーム、Square予約、Vercel公開まで見る。"),
        ("補助金", "AI導入計画・見積・実績報告", "補助金前提で、導入目的、費用、講習、成果物の説明を整える。"),
    ]
    parts = ["<div class='usecase-grid'>"]
    for label, title, body in items:
        parts.append(
            "<article class='usecase-card fade-up'>"
            f"<span class='usecase-label'>{html.escape(label)}</span>"
            f"<h3>{html.escape(title)}</h3>"
            f"<p>{html.escape(body)}</p>"
            "</article>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_growth_plan_section() -> str:
    """競合比較から逆算した、今後の集客施策。"""
    rows = [
        ("公的DX相談・商工支援", "信頼は強いが、実際の画面操作・成果物・復習資料が見えにくい", "講習ごとに教材、プロンプト、実例、予約導線を公開して「相談後に何が残るか」を見せる"),
        ("一般パソコン教室", "初心者対応は強いが、地域事業の売上導線やAI検索までは弱くなりやすい", "彦根の事業例、SNS投稿、YouTube説明欄、Googleビジネスプロフィールまで講習内で扱う"),
        ("大手AI/DX研修", "体系化は強いが、地元でその場の実務に合わせる柔軟性が弱い", "少人数・持ち込み課題・即日公開確認で、地元の具体課題を成果物にする"),
        ("制作会社・SEO会社", "公開後のサイト制作は強いが、本人がAIを使えるようになる導線が薄い", "制作実績と講習を同じページで見せ、内製化と外注の境目を相談で決める"),
    ]
    actions = [
        ("Reels / Shorts", "講習1テーマを15〜45秒に分解し、タイトル先頭に「彦根 AI相談」「ChatGPT講習」を入れる。"),
        ("YouTube", "各動画に専用ページを作り、タイトル・説明・チャプター・字幕・講習資料リンクをセット化する。"),
        ("LLMO", "FAQを質問文で増やし、講師の一次経験、価格、対応地域、実例、補助金の根拠を構造化データに入れる。"),
        ("MEO", "Googleビジネスプロフィールへ写真・講習風景・受講後の声・最新投稿を継続追加する。"),
    ]
    parts = ["<div class='growth-layout'>"]
    parts.append("<div class='growth-panel fade-up'><h3>競合との比較</h3><div class='growth-table'>")
    for competitor, gap, move in rows:
        parts.append(
            "<div class='growth-row'>"
            f"<strong>{html.escape(competitor)}</strong>"
            f"<span>{html.escape(gap)}</span>"
            f"<em>{html.escape(move)}</em>"
            "</div>"
        )
    parts.append("</div></div>")
    parts.append("<div class='growth-panel growth-actions fade-up d2'><h3>今後90日の施策</h3>")
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
    ("彦根・滋賀でAIの講習や相談はできますか？",
     "はい。滋賀県彦根市を拠点に、彦根・湖東・東近江を中心とした対面のAI講習・個別相談を行っています。京都・大阪・名古屋までは出張可、リモートなら全国対応します。"),
    ("Codex準備とCodex実践はどう違いますか？",
     "レベルは理解度で分けます。Codex準備は90分無料で、ログイン、作業フォルダ選択、最初の小さな依頼、差分確認、ブラウザ表示確認、独立レビュー、AGENTS.md、公式アップデート確認先までを整えます。Codex実践は120分5,500円で、ページ、資料、コード、動画台本などの成果物作成まで進めます。申込リンクは1つで、申込時に準備か実践をオプション選択します。"),
    ("講習資料はあとから見返せますか？",
     "はい。講習で使った資料、プロンプト、実例、動画、スライドは資料センターとして整理し、あとから復習できるようにします。受講前に内容を確認したい方も、講習資料ページから雰囲気を見られます。"),
    ("Reels や YouTube の集客にも使えますか？",
     "使えます。1つの講習テーマから、Reels/Shorts用の短い台本、YouTubeタイトル・説明欄・チャプター、サイト内の動画専用ページ、FAQ、ブログ要約まで展開する流れを作ります。"),
    ("LLMO やAI検索に強いサイトにできますか？",
     "できます。地域名、講師の一次経験、料金、対応範囲、実例、FAQ、構造化データを整理し、AIが回答に引用しやすい形で公開します。大量の自動生成ではなく、講習と実例に基づく一次情報を重視します。"),
    ("料金はどれくらいですか？",
     "AI無料相談 とりあえず30分は無料、Codex準備90分は無料、Codex実践120分は5,500円、エージェント組織構築相談60分は4,400円です。AI伴走支援 いっしょに導入は月額10万円×6ヶ月が目安です。LP制作は1本18〜30万円が目安。多くは補助金併用を前提に組みます。"),
    ("補助金は使えますか？滋賀の事業者でも対象ですか？",
     "講習・伴走パックは「デジタル化・AI導入補助金」や滋賀県・彦根市の補助金の対象になります。補助率は小規模事業者で最大4/5、実質負担が1/3以下になるケースが多いです。申請からツール選定・実装・定着まで一気通貫で支援します。"),
    ("パソコンやスマホが苦手ですが、大丈夫ですか？",
     "大丈夫です。スマホで文字が打てれば始められます。専門用語は使わず、画面を一緒に見ながら進めます。「こんなことも聞いていいの？」というレベルから歓迎します。"),
    ("AI を仕事で使いたいのですが、何から始めれば？",
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
        "<p style='font-weight:700;color:var(--text);margin-top:16px;'>「異端OK、数字根拠で経営を変える」</p>"
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
        "<a class='btn btn-primary' href='/speaker.html'>🎤 講師紹介履歴をもっと詳しく</a>"
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
    """講習資料セクション。最新の講習資料を先頭にし、AIコーディング実装講習は独立資料として残す。"""
    pmap_card = {
        "title": "AIコーディング実装講習",
        "icon": "🧭",
        "date": "2026-06-06",
        "summary": "Codex導入、プログラミング基礎、実装、公開、公式アップデート、AI応用制作までを、線画とタブUIで段階的に学ぶ講習LP。",
        "href": "/programming-map.html",
    }
    lecs = list(_load_all_lectures()) + [pmap_card]
    parts: list[str] = []
    parts.append("<div class='lecture-grid'>")
    for lec in lecs:
        parts.append(_render_lecture_card(lec))
    parts.append("</div>")
    return "".join(parts)


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
    title = f"AI相談 彦根 — 生成AI講習・Codex講習・資料センター | {OWNER_NAME}"
    desc = "彦根・滋賀の中小事業者向けAI相談サイト。生成AI講習、Codex準備/実践、講習資料、実例、講師紹介、Reels/YouTube/LLMO集客施策まで、9事業を回す講師が伴走。"

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
    parts.append(f"<style>{PORTAL_CSS}</style>")
    parts.append("</head><body>")

    parts.append(_render_header())

    parts.append("<div class='container'>")
    parts.append(ADMIN_BUTTON_HTML)

    parts.append(_render_hero())

    # 1. 受講プラン — メインCTA
    parts.append("<section class='block' id='packages'>")
    parts.append("<p class='section-heading fade-up'>AI LESSON</p>")
    parts.append("<h2 class='section-title packages-title fade-up d1'>AI相談・講習プラン</h2>")
    parts.append("<p class='section-sub fade-up d2'>レベルは理解度で分けます。Codexは準備90分無料と実践120分5,500円に分け、同じ申込リンク内でオプション選択。相談はエージェント組織構築に寄せています。</p>")
    parts.append(_render_courses_packages())
    parts.append("</section>")

    # 2. ご依頼の流れ
    parts.append("<section class='block' id='flow'>")
    parts.append("<p class='section-heading'>FLOW</p>")
    parts.append("<h2 class='section-title'>相談から資料化・集客まで</h2>")
    parts.append("<p class='section-sub'>一度聞いて終わりではなく、講習内容を資料センターと集客導線に変換します。</p>")
    parts.append(_render_flow())
    parts.append("</section>")

    # 2b. 講習で扱う実例
    parts.append("<section class='block' id='usecases'>")
    parts.append("<p class='section-heading fade-up'>USE CASES</p>")
    parts.append("<h2 class='section-title fade-up d1'>講習で扱う実例</h2>")
    parts.append("<p class='section-sub fade-up d2'>AIの説明だけではなく、実際の文章・写真・資料・SNS・Web導線をその場で触ります。</p>")
    parts.append(_render_usecases_section())
    parts.append("</section>")

    # 3. 講師紹介（誰が教えるか）
    parts.append("<section class='block' id='speaker'>")
    parts.append("<p class='section-heading fade-up'>SPEAKER</p>")
    parts.append("<h2 class='section-title fade-up d1'>講師紹介</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI 活用の啓発・講習・地域コミュニティ運営・複数事業のマーケ支援を行う実践者。</p>")
    parts.append(_render_speaker_section())
    parts.append("</section>")

    # 3b. 受講者の声（信頼の証拠・実データがある時だけ表示）
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

    # 4. 競合比較と集客施策
    parts.append("<section class='block' id='growth'>")
    parts.append("<p class='section-heading fade-up'>GROWTH PLAN</p>")
    parts.append("<h2 class='section-title fade-up d1'>競合比較から作る集客施策</h2>")
    parts.append("<p class='section-sub fade-up d2'>公的DX相談・パソコン教室・大手AI研修・制作会社と比較し、AI相談 彦根が勝てる導線を講習ページ内に組み込みます。</p>")
    parts.append(_render_growth_plan_section())
    parts.append("</section>")

    # 5. FAQ（疑問解消）
    parts.append("<section class='block' id='faq'>")
    parts.append("<p class='section-heading'>FAQ</p>")
    parts.append("<h2 class='section-title'>AI相談 彦根のよくある質問</h2>")
    parts.append(_render_faq())
    parts.append("</section>")

    # 6. 制作実績（TOP内にサマリを掲載・各カードは公開サイト本体へ直リンク）
    parts.append("<section class='block' id='works'>")
    parts.append("<p class='section-heading fade-up'>WORKS</p>")
    parts.append("<h2 class='section-title fade-up d1'>講習で見せられる実例・運営サイト</h2>")
    parts.append("<p class='section-sub fade-up d2'>説明だけではなく、講師が実際に構築・運用しているサイトや業務システムを教材として使います。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_works_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-secondary' href='/portfolio.html'>📂 実績の詳細・技術スタックを見る →</a></div>")
    parts.append("</section>")

    # 7. 講習資料（TOP内にサマリを掲載）
    parts.append("<section class='block' id='lectures'>")
    parts.append("<p class='section-heading fade-up'>MATERIALS</p>")
    parts.append("<h2 class='section-title fade-up d1'>講習資料センター</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）・Codex実践・AIコーディングを、講習後も見返せる形で整理しています。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_lectures_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-secondary' href='/lectures/index.html'>📚 講習資料の一覧を見る →</a></div>")
    parts.append("</section>")

    # 8. お問い合わせ（予約）
    parts.append("<section class='block' id='contact'>")
    parts.append("<p class='section-heading fade-up'>CONTACT</p>")
    parts.append("<h2 class='section-title fade-up d1'>彦根のAI相談、まずは30分無料</h2>")
    parts.append("<p class='section-sub fade-up d2'>講習に参加するか、エージェント組織構築を相談するか、伴走で進めるか。日程を選んで、今の課題をそのまま持ってきてください。</p>")
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
    # AIコーディング実装講習は講習資料カードとして残すが、最新資料を先頭にする
    pmap_card = {
        "title": "AIコーディング実装講習",
        "icon": "🧭",
        "date": "2026-06-06",
        "summary": "Codex導入、プログラミング基礎、実装、公開、公式アップデート、AI応用制作までを、線画とタブUIで段階的に学ぶ講習LP。",
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
