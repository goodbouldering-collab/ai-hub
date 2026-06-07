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
OWNER_SUBTITLE = "クライミング歴30年・9事業を回す滋賀の Web 経営コンサル"
OWNER_TAGLINE = "異端OK、数字根拠で経営を変える"


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


OG_IMAGE_URL = SITE_URL + "/img/hero-ai-hub-studio.png"


def _build_ogp(title: str, description: str, page_url: str, *, image: str | None = None) -> str:
    img = image or OG_IMAGE_URL
    return "".join([
        f"<meta property='og:title' content='{html.escape(title, quote=True)}'>",
        f"<meta property='og:description' content='{html.escape(description, quote=True)}'>",
        f"<meta property='og:url' content='{html.escape(page_url, quote=True)}'>",
        "<meta property='og:type' content='website'>",
        "<meta property='og:site_name' content='AIハブ'>",
        "<meta property='og:locale' content='ja_JP'>",
        f"<meta property='og:image' content='{html.escape(img, quote=True)}'>",
        "<meta property='og:image:width' content='1200'>",
        "<meta property='og:image:height' content='630'>",
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
        "name": "AIハブ（クライミングコンサル）",
        "alternateName": "AIハブ",
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
        "description": "滋賀県彦根市を拠点に、中小事業者向けのAI業務活用講習・Web経営コンサル・LP/業務システム制作・補助金支援を行う。9事業を実際に回す現役オーナーが、補助金申請からAIの現場定着まで一気通貫で伴走する。",
        "knowsAbout": [
            "生成AI業務活用", "ChatGPT", "Claude Code", "LLMO（AI検索最適化）",
            "SEO", "MEO", "業務自動化", "AI導入補助金", "デジタル化補助金", "中小企業DX",
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
        "image": SITE_URL + "/img/speaker.webp",
        "worksFor": {"@id": org_id},
        "knowsAbout": ["生成AI", "クライミング", "店舗経営", "マーケティング", "補助金活用"],
        "description": "クライミング歴30年。ボルダリングカフェ「グッぼる」をはじめ9事業を経営しながら、滋賀の中小事業者にAI活用を教える。経営者でありコードを書く実装者でもある二重性が強み。",
    }

    website = {
        "@type": "WebSite",
        "@id": web_id,
        "name": "AIハブ",
        "url": SITE_URL,
        "inLanguage": "ja",
        "publisher": {"@id": org_id},
        "description": "滋賀・彦根の中小事業者向けAI講習とWeb経営コンサルのポータル。",
    }

    seminar_title = "【講習】ClaudeCode Codex準備/実践 ※AI無料相談/ AI個別相談/AI伴走支援 ※上位0.6%実践講座 ※講師はエンジニア歴30年 ※HP 通販 SEO SNS ※補助金対応"
    free_consult_title = "【AI無料相談】まずは30分の導入相談"
    consult_title = "【AI個別相談】しっかり60分最適AI導入"
    support_title = "【AI伴走支援パック】いっしょに実務導入 ※初回相談予約"

    # 受講プランを Service + Offer として構造化（_render_packages の items と整合）
    plans = [
        (seminar_title, "Claude Code または Codex の環境が整い、自分で1つ以上動くものを作った人向けの月例少人数セミナー。持ち込み課題をその場で進める。", "5500", "5500", "Course"),
        (seminar_title, "実践会の前に、環境構築・ログイン・最初の成果物作成までを整える少人数の準備講座。", "5500", "5500", "Course"),
        (free_consult_title, "来店またはオンラインで、AI導入の入口を30分で整理する無料相談。講習や伴走の前に、今の課題と次の一手を確認する。", "0", "0", "BusinessCoaching"),
        (consult_title, "経営者・専門職・初心者なんでも相談。AI活用、Claude Code / Codex導入、補助金申請まで現役オーナーがその場で解決。", "4400", "4400", "BusinessCoaching"),
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
   明るいベースに、AIらしいシアン/ブルーと発見感のあるライムを混ぜる。 */
:root {
  /* ===== デフォルト=ライト（初心者に「難しそう」を与えない）。dark は data-theme=dark で。 ===== */
  /* --- 共有トークン（テーマ非依存） --- */
  --cyan: #06A7D8;
  --blue: #2357E5;
  --sage: #86D1AF;
  --emerald: #12A88A;
  --amber: #F5C542;
  --coral: #FF6B5B;
  --glass-blur: 18px;
  --radius: 8px;
  --radius-sm: 8px;
  --serif: "Inter", -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
  --mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
  --bg-base: #F4F7FB;
  --bg-white: #FBFCFF;
  --bg-elev: #FFFFFF;
  --text: #101827;
  --text-soft: #3A475D;
  --muted: #687489;
  --line: rgba(16,24,39,0.12);
  --line-strong: rgba(16,24,39,0.24);
  --primary: #2357E5;
  --primary-soft: #06A7D8;
  --violet: #6C5CE7;
  --primary-bg: rgba(35,87,229,0.08);
  --grad: linear-gradient(120deg, #2357E5 0%, #06A7D8 52%, #9BE43A 100%);
  --grad-soft: linear-gradient(120deg, rgba(35,87,229,.11), rgba(6,167,216,.11), rgba(155,228,58,.12));
  --glass-bg: rgba(255,255,255,0.66);
  --glass-border: rgba(16,24,39,0.13);
  --glass-hi: rgba(255,255,255,0.88);
  --shadow-card: 0 1px 2px rgba(16,24,39,0.04), 0 16px 38px rgba(16,24,39,0.08);
  --shadow-card-hover: 0 6px 16px rgba(16,24,39,0.08), 0 24px 58px rgba(35,87,229,0.13), 0 0 0 1px rgba(6,167,216,0.18);
  --glow: 0 18px 58px rgba(35,87,229,0.16);
  --grad-glow-a: rgba(35,87,229,.11);
  --grad-glow-b: rgba(6,167,216,.11);
  --grad-glow-c: rgba(155,228,58,.09);
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
    linear-gradient(120deg, rgba(35,87,229,.05) 0%, transparent 34%),
    linear-gradient(180deg, var(--bg-white) 0%, #F4F7FB 45%, #EDF5F8 100%);
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
    linear-gradient(90deg, rgba(21,32,50,.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(21,32,50,.025) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,.44), transparent 58%);
}
::selection { background: rgba(40,84,197,.22); color: var(--text); }

/* ---- glassmorphism helpers (再利用) ----
   カード/ヘッダー/ドロップに共通で当てる「ガラス質感」。
   半透明背景 + backdrop blur + 1px光彩ボーダー + 上端の内側ハイライト。 */
.biz-card, .service-card, .pkg-card, .faq-item, .stat,
.menu-drop, .diagnose-box, .hero-quiz {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(var(--glass-blur)) saturate(118%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(118%);
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
  transition: background .3s, box-shadow .3s, backdrop-filter .3s;
}
header.site-header.scrolled {
  background: var(--glass-bg);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}
.site-header-inner {
  max-width: 1280px; margin: 0 auto;
  padding: 14px 24px;
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
  width: 34px; height: 34px; border-radius: 10px;
  display: inline-flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #EEF5FF 0%, #FFFFFF 52%, #F0F4E8 100%);
  border: 1px solid rgba(40,84,197,.20);
  box-shadow: 0 10px 24px rgba(40,84,197,.14), inset 0 1px 0 rgba(255,255,255,.9);
  color: #0F172A; font-family: var(--mono); font-weight: 900; line-height: 1;
}
.brand-mark .brand-a { font-size: 16px; letter-spacing: 0; color: var(--primary); }
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
.site-logo-by { color: var(--muted); font-weight: 600; font-size: 12px; margin-left: 4px; }
@media (max-width: 720px) {
  .wordmark .word-en, .site-logo-by { display: none; }
}
.site-nav { display: flex; align-items: center; gap: 22px; }
.site-nav a.nav-link {
  font-size: 13.5px; font-weight: 600; color: var(--text-soft);
  text-decoration: none; transition: color .2s;
}
.site-nav a.nav-link:hover { color: var(--primary); }
.site-nav .menu-wrap { position: relative; }
.site-nav .menu-toggle {
  display: inline-flex; align-items: center; gap: 4px;
  background: transparent; border: none; cursor: pointer;
  font: inherit; font-size: 13.5px; font-weight: 600; color: var(--text-soft);
  padding: 0;
}
.site-nav .menu-toggle:hover { color: var(--primary); }
.site-nav .menu-toggle .chev { transition: transform .2s; }
.site-nav .menu-toggle[aria-expanded="true"] .chev { transform: rotate(180deg); }
.site-nav .menu-drop {
  position: absolute; right: 0; top: calc(100% + 10px);
  min-width: 220px; padding: 8px;
  background: var(--glass-bg); border: 1px solid var(--line);
  border-radius: var(--radius-sm); box-shadow: var(--shadow-card);
  backdrop-filter: blur(18px);
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
  padding: 10px 20px; border-radius: 999px;
  background: var(--grad); color: #fff;
  font-size: 13.5px; font-weight: 700;
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
  padding: 54px 0 66px;
  display: grid; grid-template-columns: minmax(0, .95fr) minmax(420px, 1.05fr); gap: 52px; align-items: center;
  position: relative;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 8px calc(50% - 50vw) 0;
  z-index: -1;
  background:
    linear-gradient(120deg, rgba(255,255,255,.90) 0%, rgba(236,246,255,.84) 48%, rgba(239,255,245,.82) 100%);
  border-top: 1px solid rgba(21,32,50,.06);
  border-bottom: 1px solid rgba(21,32,50,.07);
}
.hero-text { text-align: left; min-width: 0; max-width: 100%; }
@media (max-width: 900px) { .hero { grid-template-columns: 1fr; gap: 28px; }
  .hero-text { text-align: center; }
}
.hero .eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 16px; border-radius: 999px;
  background: rgba(255,255,255,.78); color: var(--primary);
  font-family: var(--mono); font-size: 11.5px; font-weight: 600; letter-spacing: .06em;
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 24px rgba(21,32,50,.06);
  max-width: 100%;
}
@media (max-width: 560px) {
  .hero .eyebrow {
    display: flex; text-align: left; line-height: 1.5;
    padding: 8px 12px; font-size: 10.5px;
  }
}
.hero h1 {
  margin: 20px 0 14px; font-size: clamp(42px, 6.2vw, 76px);
  font-family: var(--serif); font-weight: 900; letter-spacing: 0;
  color: var(--text); line-height: 1.12;
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
  font-family: var(--mono); color: rgba(14,165,233,.45);
  font-size: .62em; margin: 0 .08em; transform: translateY(-.08em);
}
.hero-title-sub {
  display: block; margin-top: 8px;
  font-size: clamp(22px, 2.7vw, 34px);
  line-height: 1.28; color: var(--text-soft); letter-spacing: 0;
}
.hero-title-sub strong {
  color: var(--primary);
  background: transparent;
}
.hero .sub-catch {
  max-width: 560px; margin: 0 0 18px;
  font-size: clamp(15px, 1.7vw, 18px); font-weight: 700; color: var(--text); line-height: 1.7;
}
.hero .sub-catch strong { color: var(--primary); }
@media (max-width: 900px) { .hero .sub-catch { margin: 0 auto 18px; } }
.hero .lead {
  max-width: 560px; margin: 0 0 28px;
  font-size: clamp(14px, 1.5vw, 16px); color: var(--text-soft); line-height: 1.85;
}
.hero .lead strong { color: var(--text); font-weight: 700; }
@media (max-width: 900px) { .hero .lead { margin: 0 auto 28px; } }
.hero-actions {
  display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px;
}
@media (max-width: 900px) { .hero-actions { justify-content: center; } }
.btn-lg { padding: 16px 32px; font-size: 16px; }
/* 主CTAを脈動させて視線を集める（控えめ・reduced-motionで停止） */
.hero-actions .btn-primary { animation: cta-pulse 2.6s ease-in-out infinite; }
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
  width: min(100%, 580px);
  aspect-ratio: 5 / 4;
  padding: 10px;
  border-radius: var(--radius);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow: 0 24px 68px rgba(16,24,39,.16), inset 0 1px 0 var(--glass-hi);
  backdrop-filter: blur(var(--glass-blur)) saturate(126%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(126%);
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
  inset: 10px;
  border-radius: 6px;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(255,255,255,.02) 0%, rgba(11,16,32,.16) 100%),
    linear-gradient(120deg, rgba(35,87,229,.10), rgba(6,167,216,.08), transparent 62%);
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
  background: rgba(255,255,255,.88);
  border: 1px solid rgba(255,255,255,.72);
  box-shadow: 0 14px 32px rgba(21,32,50,.14);
  color: var(--text);
  font-size: 12.5px;
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
  background: rgba(11,16,32,.72);
  border: 1px solid rgba(255,255,255,.18);
  color: #fff;
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 18px 42px rgba(11,16,32,.22);
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
  background: rgba(255,255,255,.78);
  color: var(--text);
  text-decoration: none;
  box-shadow: 0 12px 30px rgba(16,24,39,.14);
  backdrop-filter: blur(14px) saturate(130%);
  -webkit-backdrop-filter: blur(14px) saturate(130%);
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
/* アニメ調ヒーローSVG */
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
  padding: 13px 28px; border-radius: 999px;
  font-size: 14.5px; font-weight: 600; text-decoration: none;
  transition: transform .2s, box-shadow .2s, background .2s, filter .2s;
  cursor: pointer; border: none; letter-spacing: 0;
}
.btn-primary {
  background: var(--grad); color: #fff;
  box-shadow: 0 8px 28px rgba(40,84,197,.26), inset 0 1px 0 rgba(255,255,255,.25);
}
.btn-primary:hover { transform: translateY(-2px); filter: brightness(1.08); box-shadow: 0 14px 38px rgba(15,143,114,.23), inset 0 1px 0 rgba(255,255,255,.30); }
.btn-secondary {
  background: var(--glass-bg); color: var(--text);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 var(--glass-hi);
}
.btn-secondary:hover { border-color: var(--line-strong); transform: translateY(-2px); box-shadow: 0 14px 30px rgba(21,32,50,.10); }
.btn-ghost { background: transparent; color: var(--text-soft); padding: 9px 16px; }
.btn-ghost:hover { color: var(--primary); }

/* ---- stats strip ---- */
.stats-strip {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  margin: 24px 0 56px;
}
@media (max-width: 720px) { .stats-strip { grid-template-columns: repeat(2, 1fr); } }
.stat {
  text-align: center; padding: 22px 18px; border-radius: var(--radius-sm);
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
}
.stat .num {
  font-size: clamp(26px, 3.4vw, 38px); font-weight: 800;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent;
  line-height: 1.1; letter-spacing: 0;
}
.stat .label { font-size: 12.5px; color: var(--muted); margin-top: 6px; font-weight: 600; }
.stat .stat-sub { font-size: 10.5px; color: var(--muted); margin-top: 3px; font-style: italic; opacity: .8; }

/* ---- section frame ---- */
section.block { padding: 72px 0; scroll-margin-top: 96px; }
section.block + section.block { border-top: 1px solid var(--line); }
.section-title {
  font-family: var(--serif);
  font-size: clamp(28px, 4vw, 46px); font-weight: 700; letter-spacing: 0;
  color: var(--text); text-align: center; margin: 0 0 14px; line-height: 1.15;
  overflow-wrap: anywhere;
}
.section-sub {
  text-align: center; color: var(--text-soft);
  font-size: 14.5px; max-width: 640px; margin: 0 auto 48px; line-height: 1.8;
}
.section-heading {
  font-family: var(--mono);
  font-size: 11px; font-weight: 700; letter-spacing: .18em;
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

/* ---- packages (Claude Code / Codex 講習プラン) ---- */
.packages-stage {
  display: grid;
  grid-template-columns: minmax(280px, .94fr) minmax(0, 1.06fr);
  gap: 18px;
  align-items: stretch;
  margin: -22px 0 20px;
}
.package-visual,
.package-stage-copy {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius);
  border: 1px solid var(--glass-border);
  background:
    linear-gradient(140deg, rgba(255,255,255,.78), rgba(255,255,255,.44)),
    linear-gradient(120deg, rgba(43,167,200,.12), rgba(245,249,255,.7) 42%, rgba(122,165,138,.15));
  backdrop-filter: blur(22px) saturate(128%);
  -webkit-backdrop-filter: blur(22px) saturate(128%);
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,.82);
}
.package-visual {
  min-height: 340px;
  display: grid;
  place-items: center;
  padding: 26px;
  isolation: isolate;
}
.package-visual::before,
.package-visual::after {
  content: "";
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
  filter: blur(2px);
}
.package-visual::before {
  width: 220px; height: 220px; left: -88px; top: -74px;
  background: rgba(43,167,200,.18);
}
.package-visual::after {
  width: 190px; height: 190px; right: -64px; bottom: -60px;
  background: rgba(217,133,43,.14);
}
.package-line-art {
  position: relative;
  z-index: 1;
  width: min(100%, 430px);
  aspect-ratio: 1.12;
}
.package-line-art svg { width: 100%; height: 100%; display: block; overflow: visible; }
.line-orbit { transform-origin: 200px 180px; animation: lineOrbit 18s linear infinite; }
.line-orbit.slow { animation-duration: 28s; animation-direction: reverse; }
.line-pulse { transform-origin: center; animation: linePulse 3.2s ease-in-out infinite; }
.line-dash { stroke-dasharray: 7 12; animation: lineDash 12s linear infinite; }
.line-bubble { animation: bubbleFloat 7s ease-in-out infinite; }
.line-bubble.b2 { animation-delay: -2.1s; }
.line-bubble.b3 { animation-delay: -4.2s; }
.package-visual-label {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 18px;
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--text-soft);
}
.package-visual-label span {
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid rgba(40,84,197,.14);
  background: rgba(255,255,255,.54);
}
@keyframes lineOrbit { to { transform: rotate(360deg); } }
@keyframes linePulse { 0%,100% { transform: scale(1); opacity: .82; } 50% { transform: scale(1.08); opacity: 1; } }
@keyframes lineDash { to { stroke-dashoffset: -180; } }
@keyframes bubbleFloat { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
.package-stage-copy {
  padding: clamp(24px, 3vw, 34px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}
.package-stage-kicker {
  margin: 0 0 10px;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .14em;
  color: var(--primary);
}
.package-stage-copy h3 {
  margin: 0 0 12px;
  font-size: clamp(24px, 3vw, 36px);
  line-height: 1.24;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}
.package-stage-copy p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.85;
  font-size: 14.5px;
}
.package-track-tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}
.track-pill {
  border-radius: var(--radius-sm);
  border: 1px solid rgba(40,84,197,.14);
  background: rgba(255,255,255,.52);
  padding: 13px 14px;
}
.track-pill b { display: block; color: var(--text); font-size: 13.5px; line-height: 1.35; }
.track-pill span { display: block; color: var(--muted); font-size: 12px; line-height: 1.55; margin-top: 3px; }
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
    linear-gradient(145deg, rgba(255,255,255,.72), rgba(255,255,255,.44)),
    var(--glass-bg) !important;
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,.76);
  transition: transform .25s cubic-bezier(.22,1,.36,1), box-shadow .25s, border-color .2s;
  position: relative;
  overflow: hidden;
}
.pkg-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(180px 140px at 16% 0%, rgba(43,167,200,.14), transparent 72%),
    radial-gradient(180px 150px at 100% 20%, rgba(217,133,43,.10), transparent 70%);
  opacity: .86;
}
.pkg-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,.85);
  border-color: rgba(40,84,197,.24);
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
  border: 1px solid rgba(40,84,197,.14);
  padding: 4px 10px;
  border-radius: 999px;
}
.pkg-no {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 900;
  color: rgba(40,84,197,.34);
}
.pkg-head { display: flex; align-items: flex-start; gap: 10px; }
.pkg-icon {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,.62);
  border: 1px solid rgba(40,84,197,.12);
  font-size: 18px;
  line-height: 1;
}
.pkg-title { font-size: 17px; font-weight: 900; color: var(--text); line-height: 1.38; margin: 0; flex: 1; letter-spacing: 0; min-width: 0; overflow-wrap: anywhere; }
.pkg-featured .pkg-title { font-size: clamp(22px, 2.6vw, 30px); line-height: 1.22; }
.pkg-meta { font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pkg-level {
  font-family: var(--mono); font-size: 10.5px; font-weight: 800; letter-spacing: .06em;
  padding: 3px 10px; border: 1px solid var(--glass-border); color: var(--primary);
  background: var(--primary-bg); border-radius: 999px;
}
.pkg-price {
  font-size: 20px; font-weight: 900;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent;
}
.pkg-subsidy {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 800; color: #047857;
  background: rgba(209,250,229,.74); padding: 4px 10px; border-radius: 999px;
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
  .packages-stage { grid-template-columns: 1fr; }
  .package-visual { min-height: 300px; }
  .pkg-card, .pkg-featured, .pkg-wide { grid-column: span 6; }
}
@media (max-width: 680px) {
  .packages-stage { margin-top: -12px; }
  .package-track-tabs { grid-template-columns: 1fr; }
  .packages-grid { grid-template-columns: 1fr; }
  .pkg-card, .pkg-featured, .pkg-wide { grid-column: auto; }
  .package-visual { min-height: 260px; padding: 18px; }
  .pkg-featured .pkg-title { font-size: 22px; }
  #packages .section-title { font-size: 28px; line-height: 1.2; }
  #packages .section-title .title-line { display: block; }
}


/* ---- theme toggle ---- */
.theme-toggle {
  width: 38px; height: 38px; border-radius: var(--radius-sm);
  border: 1px solid var(--line); background: var(--bg-white);
  font-size: 16px; cursor: pointer; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
  transition: transform .15s ease, border-color .15s ease, background .3s ease;
}
.theme-toggle:hover { transform: translateY(-1px) rotate(-12deg); border-color: var(--primary); }
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
  display: grid; grid-template-columns: 1fr 360px; gap: 36px; align-items: stretch;
}
@media (max-width: 720px) {
  .speaker-intro-grid { grid-template-columns: 1fr; gap: 24px; text-align: center; }
  .speaker-intro-grid .profile-avatar { margin: 0 auto; }
}
/* 講師アートビジュアル（実画像 or CSSプレースホルダ） */
.speaker-art {
  position: relative; overflow: hidden;
  border: 1px solid var(--line); border-radius: var(--radius-sm);
  min-height: 320px; aspect-ratio: 4/5; align-self: stretch;
  background: var(--bg-base);
}
.speaker-art img { width: 100%; height: 100%; object-fit: cover; object-position: center 30%; display: block; }
.speaker-art-animated {
  isolation: isolate;
  transform: translateZ(0);
  box-shadow: 0 18px 48px rgba(15,23,42,.16);
  animation: speakerFloat 7s ease-in-out infinite;
}
.speaker-art-animated img {
  transform-origin: 52% 34%;
  filter: saturate(1.08) contrast(1.03);
  animation: speakerKenburns 12s ease-in-out infinite alternate;
}
.speaker-art-animated::before {
  content: "";
  position: absolute; inset: 0; z-index: 1; pointer-events: none;
  background:
    radial-gradient(220px 180px at 76% 18%, rgba(96,165,250,.34), transparent 62%),
    radial-gradient(220px 190px at 18% 82%, rgba(45,212,191,.22), transparent 66%),
    linear-gradient(115deg, transparent 0%, rgba(255,255,255,.34) 46%, transparent 58%);
  mix-blend-mode: screen;
  opacity: .72;
  transform: translateX(-42%);
  animation: speakerLightSweep 5.6s ease-in-out infinite;
}
.speaker-art-animated::after {
  content: "";
  position: absolute; inset: 0; z-index: 2; pointer-events: none;
  border-radius: inherit;
  background-image:
    linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px);
  background-size: 34px 34px;
  opacity: .42;
  -webkit-mask-image: linear-gradient(180deg, rgba(0,0,0,.92), rgba(0,0,0,.34) 74%, transparent);
  mask-image: linear-gradient(180deg, rgba(0,0,0,.92), rgba(0,0,0,.34) 74%, transparent);
  animation: speakerGridDrift 11s linear infinite;
}
.speaker-art-orbit {
  position: absolute; inset: 16px; z-index: 3; pointer-events: none;
  border: 1px solid rgba(255,255,255,.34); border-radius: calc(var(--radius-sm) - 2px);
  box-shadow: inset 0 0 38px rgba(96,165,250,.14);
}
.speaker-art-chip {
  position: absolute; z-index: 4; pointer-events: none;
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 10px; border-radius: 999px;
  background: rgba(255,255,255,.88); color: #17202a;
  border: 1px solid rgba(255,255,255,.70);
  box-shadow: 0 12px 32px rgba(15,23,42,.18);
  font-size: 11px; font-weight: 800; letter-spacing: .06em;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.speaker-art-chip.ai { top: 20px; left: 18px; color: var(--primary); animation: speakerChipFloat 4.8s ease-in-out infinite; }
.speaker-art-chip.live { right: 18px; bottom: 20px; color: #0f8b8d; animation: speakerChipFloat 5.4s ease-in-out infinite reverse; }
.speaker-art-spark {
  position: absolute; z-index: 3; width: 8px; height: 8px; border-radius: 50%;
  background: #fff; box-shadow: 0 0 18px rgba(255,255,255,.9), 0 0 30px rgba(96,165,250,.6);
  pointer-events: none; opacity: .9;
}
.speaker-art-spark.s1 { top: 18%; right: 24%; animation: speakerSpark 3.2s ease-in-out infinite; }
.speaker-art-spark.s2 { top: 48%; left: 13%; animation: speakerSpark 4.1s ease-in-out infinite .5s; }
.speaker-art-spark.s3 { bottom: 24%; right: 16%; animation: speakerSpark 3.8s ease-in-out infinite 1.1s; }
@keyframes speakerFloat {
  0%, 100% { transform: translateY(0) rotate(.001deg); }
  50% { transform: translateY(-8px) rotate(.001deg); }
}
@keyframes speakerKenburns {
  0% { transform: scale(1.015) translate3d(0,0,0); }
  100% { transform: scale(1.075) translate3d(-1.8%, -1.2%, 0); }
}
@keyframes speakerLightSweep {
  0%, 18% { transform: translateX(-58%); opacity: .30; }
  48% { transform: translateX(32%); opacity: .82; }
  100% { transform: translateX(58%); opacity: .24; }
}
@keyframes speakerGridDrift {
  from { background-position: 0 0, 0 0; }
  to { background-position: 34px 68px, 68px 34px; }
}
@keyframes speakerChipFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-7px); }
}
@keyframes speakerSpark {
  0%, 100% { transform: scale(.72); opacity: .28; }
  42% { transform: scale(1.25); opacity: .95; }
  70% { transform: scale(.92); opacity: .58; }
}
@media (prefers-reduced-motion: reduce) {
  .speaker-art-animated,
  .speaker-art-animated img,
  .speaker-art-animated::before,
  .speaker-art-animated::after,
  .speaker-art-chip,
  .speaker-art-spark {
    animation: none !important;
  }
}
@media (max-width: 720px) {
  .speaker-art { max-width: 320px; margin: 0 auto; }
  .speaker-art-chip.live { top: 20px; right: 18px; bottom: auto; }
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
        "<a class='site-logo' href='/' aria-label='AIハブ トップへ'>"
        "<span class='brand-mark' aria-hidden='true'><span class='brand-a'>A</span><span class='brand-ha'>ハ</span></span>"
        "<span class='wordmark'><span class='word-ai'>AI</span><span class='word-hub'>ハブ</span><span class='word-en'>AI HUB</span></span>"
        "<span class='site-logo-by'>by 由井辰美</span>"
        "</a>"
        "<nav class='site-nav' aria-label='メインナビ'>"
        "<a class='nav-link' href='#packages'>受講プラン</a>"
        "<a class='nav-link' href='#works'>制作実績</a>"
        "<a class='nav-link' href='#speaker'>講師紹介</a>"
        "<a class='nav-link' href='#faq'>FAQ</a>"
        "<div class='menu-wrap'>"
        "<button class='menu-toggle' id='menu-toggle' aria-haspopup='menu' aria-expanded='false'>その他"
        "<svg class='chev' width='14' height='14' viewBox='0 0 20 20' fill='none' aria-hidden='true'><path d='M5 8l5 5 5-5' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        "</button>"
        "<div class='menu-drop' id='menu-drop' role='menu'>"
        "<a href='#flow'>🛠 ご依頼の流れ</a>"
        "<a href='#lectures'>📚 講習資料</a>"
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
        "<a href='#works'>制作実績</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='#flow'>ご依頼の流れ</a>"
        "<a href='#lectures'>講習資料</a>"
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
      { q: 'Claude Code / Codex はどこまで触れていますか？', a: [
        { label: 'これから環境を整えたい', lv: 'beginner' },
        { label: '3日以上触って、少し作った', lv: 'intermediate' },
        { label: '業務やサイト制作で使い始めている', lv: 'advanced' },
      ]},
      { q: '当日いちばん進めたいことは？', a: [
        { label: 'ログインや最初の依頼を整えたい', lv: 'beginner' },
        { label: '持ち込み課題をその場で進めたい', lv: 'intermediate' },
        { label: '自社業務の仕組みまで作りたい', lv: 'advanced' },
      ]},
      { q: 'どのスパンで取り組みたい？', a: [
        { label: 'まず90分で準備したい', lv: 'beginner' },
        { label: '月1回・120分で継続したい', lv: 'intermediate' },
        { label: '半日〜6ヶ月で本格導入したい', lv: 'advanced' },
      ]},
    ];
    var RESULT = {
      beginner: {
        badge: '準備', title: '実践会の前に環境を整える',
        name: '【講習】ClaudeCode Codex準備/実践 ※AI無料相談/ AI個別相談/AI伴走支援 ※上位0.6%実践講座 ※講師はエンジニア歴30年 ※HP 通販 SEO SNS ※補助金対応',
        desc: 'ログイン、作業フォルダ、最初の依頼、差分確認までを整えます。実践会で置いていかれない状態を作ります。',
        level_id: 'beginner'
      },
      intermediate: {
        badge: '実践', title: '持ち込み課題を深く進める',
        name: '【講習】ClaudeCode Codex準備/実践 ※AI無料相談/ AI個別相談/AI伴走支援 ※上位0.6%実践講座 ※講師はエンジニア歴30年 ※HP 通販 SEO SNS ※補助金対応',
        desc: '3日以上の利用経験、1つ以上の成果物、基本コマンドへの抵抗がない方に向く月例少人数会です。',
        level_id: 'intermediate'
      },
      advanced: {
        badge: '実装', title: '業務に組み込む',
        name: '【AI伴走支援パック】いっしょに実務導入 ※初回相談予約',
        desc: '自社業務の自動化、社内手順化、補助金前提の導入まで進めたい方向けです。',
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
        c.classList.toggle('pkg-match', c.getAttribute('data-level') === lv);
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

# アニメ調ヒーローSVG（designer設計仕様 2026-05-27 を実装）。
# 7レイヤー: 背景グラデ→glowリング→データストリーム→書類スタック(✓)→
# 人物(IT苦手だが前向きな経営者の安堵の笑み)→データ粒子→ラベルバッジ。
# フラットカラー+統一アウトライン(#F0F4FF)でアニメ感。ロボット要素は出さない。
HERO_SVG = """
<svg class="hero-svg" viewBox="0 0 460 575" role="img"
  aria-label="アニメ調イラスト: 彦根の経営者がAIの光と一緒に山積みの業務を片付けて軽くなっていく様子"
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
    <!-- 目（やや大きめ・アニメ感）-->
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
        "<span class='eyebrow'>彦根・滋賀｜AIコーディングと業務AIを学ぶ入口</span>"
        "<h1 class='hero-brand'>"
        "<span class='fusion-logo-large'><span class='ai'>AI</span><span class='pipe'>|</span><span class='hub'>ハブ</span></span>"
        "<span class='hero-title-sub'><strong>AIに作らせ、自分で確認する力</strong>を、ひとつの入口に。</span>"
        "<span class='visually-hidden'>｜滋賀・彦根の中小事業者向けAI講習・AI導入支援・補助金申請サポート</span>"
        "</h1>"
        "<p class='sub-catch'>"
        "<strong>AIコーディングは、まだ早期層の実務スキル。講習、相談、制作実績、AI情報を整理して、次にやることをすぐ選べるトップへ。</strong>"
        "</p>"
        "<p class='lead'>"
        "上位0.6%級という言い方が出るほど、AIコーディングはまだ少数派です。"
        "だからこそ、コード暗記よりも、依頼文、差分確認、ブラウザ確認、公開前レビューを早く身につける価値があります。"
        "</p>"
        "<div class='hero-actions'>"
        "<a class='btn btn-primary btn-lg' href='#contact'>無料で30分相談する</a>"
        "<button type='button' class='btn btn-secondary btn-lg diagnose-open' data-prelevel='beginner'>30秒でAIレベル診断</button>"
        "</div>"
        "<ul class='hero-trust'>"
        "<li>相談は<strong>無料</strong></li>"
        "<li>補助金<strong>申請まで支援</strong></li>"
        "<li><strong>9事業</strong>を回す現役オーナー</li>"
        "</ul>"
        "<div class='hero-entry-strip' aria-label='AIハブの主要入口'>"
        "<a class='entry-chip' href='#packages'><b>相談・講習</b><span>Codexと実務AIを学ぶ</span></a>"
        "<a class='entry-chip' href='#works'><b>制作実績</b><span>作れるものを見る</span></a>"
        "<a class='entry-chip' href='#lectures'><b>講習資料</b><span>教材で学ぶ</span></a>"
        "<a class='entry-chip' href='/watch/index.html'><b>AI情報</b><span>最新要約を見る</span></a>"
        "</div>"
        "</div>"
        "<div class='hero-photo-card fade-up d2' aria-label='AIハブの相談イメージ'>"
        "<img src='/img/hero-ai-hub-studio.png' alt='AI相談と制作、講習資料を一緒に整理するAIハブのイメージ' decoding='async' fetchpriority='high'>"
        "<span class='hero-photo-note'><i aria-hidden='true'></i>相談・制作・講習を一つに</span>"
        "<div class='hero-photo-map' aria-hidden='true'>"
        "<svg viewBox='0 0 280 170' fill='none' xmlns='http://www.w3.org/2000/svg'>"
        "<rect x='12' y='14' width='76' height='44' rx='8' stroke='#8bdcff' stroke-width='2'/>"
        "<rect x='102' y='14' width='76' height='44' rx='8' stroke='#c8ff5f' stroke-width='2'/>"
        "<rect x='192' y='14' width='76' height='44' rx='8' stroke='#ffb3a8' stroke-width='2'/>"
        "<path class='route-line' d='M88 36H102M178 36H192' stroke='#fff' stroke-width='2'/>"
        "<text x='31' y='40' fill='#fff' font-size='12'>相談</text>"
        "<text x='121' y='40' fill='#fff' font-size='12'>実装</text>"
        "<text x='211' y='40' fill='#fff' font-size='12'>確認</text>"
        "<path class='route-line' d='M50 58C50 112 230 112 230 58' stroke='#8bdcff' stroke-width='2'/>"
        "<circle cx='50' cy='120' r='20' stroke='#c8ff5f' stroke-width='2'/>"
        "<circle cx='140' cy='134' r='23' stroke='#8bdcff' stroke-width='2'/>"
        "<circle cx='230' cy='120' r='20' stroke='#ffb3a8' stroke-width='2'/>"
        "<path d='M70 120H117M163 134H210' stroke='#fff' stroke-opacity='.72' stroke-width='2'/>"
        "<text x='39' y='124' fill='#fff' font-size='10'>Git</text>"
        "<text x='121' y='138' fill='#fff' font-size='10'>Browser</text>"
        "<text x='214' y='124' fill='#fff' font-size='10'>Deploy</text>"
        "</svg>"
        "</div>"
        "<div class='hero-mini-routes' aria-label='AIハブの主要入口'>"
        "<a href='#contact'><b>相談する</b><small>課題を整理</small></a>"
        "<a href='#packages'><b>学ぶ</b><small>講習プラン</small></a>"
        "<a href='#works'><b>作る</b><small>実績を見る</small></a>"
        "<a href='/watch/index.html'><b>追う</b><small>AI情報</small></a>"
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
    """Claude Code / Codex 実践会を中心にした講習プラン。"""
    seminar_title = "【講習】ClaudeCode Codex準備/実践 ※AI無料相談/ AI個別相談/AI伴走支援 ※上位0.6%実践講座 ※講師はエンジニア歴30年 ※HP 通販 SEO SNS ※補助金対応"
    seminar_url = "https://goodbouldering.com/?pid=188553378"
    free_consult_title = "【AI無料相談】まずは30分の導入相談"
    free_consult_url = "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
    consult_title = "【AI個別相談】しっかり60分最適AI導入"
    support_title = "【AI伴走支援パック】いっしょに実務導入 ※初回相談予約"
    items = [
        {
            "icon": "⌘",
            "cat": "月例・実践編",
            "level": "実践者向け",
            "level_id": "intermediate",
            "title": seminar_title,
            "price": "5,500円",
            "duration": "120分 / 月1回 / 定員8名",
            "subsidy": True,
            "desc": "Claude Code と Codex を使って、自分の課題をその場で進める少人数セミナー。環境構築だけで終わらせず、差分・画面・成果物まで見ながら進めます。",
            "fit": ["自分のPCで Claude Code / Codex が動く", "作りたいもの・直したい課題を持ち込む", "参加者同士の質を保ちながら深く進める"],
            "req_title": "参加条件",
            "requirements": [
                "Claude Code または Codex を3日以上使ったことがある",
                "自分で1つ以上「動くもの」を作った経験がある",
                "cd / ls / git など基本コマンドに抵抗がない",
                "申込時に当日扱いたい課題を一言で書ける",
            ],
            "verify": "申込時に「作ったもの」「環境構築済みか」「持ち込み課題」を確認します。条件に満たない方は準備会を案内します。",
            "url": seminar_url,
            "cta": "実践会の詳細を見る",
            "variant": "featured",
        },
        {
            "icon": "↗",
            "cat": "入門・準備編",
            "level": "準備中",
            "level_id": "beginner",
            "title": seminar_title,
            "price": "5,500円",
            "duration": "90分 / 少人数",
            "subsidy": False,
            "desc": "実践会に来る前の入口。ログイン、作業フォルダ、最初の依頼、差分確認までを整え、当日トラブルで時間が溶けない状態にします。",
            "fit": ["インストールやログインが不安", "Codex / Claude Code の違いを整理したい", "まず1つ小さな成果物を作りたい"],
            "url": seminar_url,
            "cta": "準備会の詳細を見る",
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
            "cat": "相談・振り分け",
            "level": "初級",
            "level_id": "beginner",
            "title": consult_title,
            "price": "4,400円",
            "duration": "60分",
            "subsidy": False,
            "desc": "実務をこなす経営者が、ビジネスに最適なAI活用を最短でアドバイス。Claude Code / Codex 導入、補助金、業務改善まで対応します。",
            "fit": ["実践会か準備会か迷う", "仕事への使いどころを決めたい", "補助金や導入順序も相談したい"],
            "url": "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP",
            "cta": "個別相談を予約する",
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
    parts = [
        "<div class='packages-stage fade-up d1'>"
        "<div class='package-visual' aria-hidden='true'>"
        "<div class='package-line-art'>"
        "<svg viewBox='0 0 400 360' xmlns='http://www.w3.org/2000/svg'>"
        "<defs>"
        "<linearGradient id='pkgLineGrad' x1='0' y1='0' x2='1' y2='1'>"
        "<stop offset='0' stop-color='#2854C5'/><stop offset='.52' stop-color='#2BA7C8'/><stop offset='1' stop-color='#0F8F72'/>"
        "</linearGradient>"
        "<filter id='pkgGlow' x='-40%' y='-40%' width='180%' height='180%'><feGaussianBlur stdDeviation='7'/></filter>"
        "</defs>"
        "<circle class='line-bubble' cx='78' cy='88' r='20' fill='rgba(43,167,200,.15)'/>"
        "<circle class='line-bubble b2' cx='320' cy='94' r='26' fill='rgba(217,133,43,.13)'/>"
        "<circle class='line-bubble b3' cx='330' cy='274' r='18' fill='rgba(15,143,114,.13)'/>"
        "<g fill='none' stroke='url(#pkgLineGrad)' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'>"
        "<circle class='line-orbit slow' cx='200' cy='180' r='132' opacity='.36'/>"
        "<circle class='line-orbit' cx='200' cy='180' r='96' opacity='.5'/>"
        "<path class='line-dash' d='M74 220 C118 136 174 102 244 120 C306 136 338 190 314 246 C286 314 180 316 124 270' opacity='.72'/>"
        "<path d='M124 230 L176 178 L226 210 L280 142' opacity='.88'/>"
        "</g>"
        "<g fill='rgba(255,255,255,.84)' stroke='url(#pkgLineGrad)' stroke-width='2.4'>"
        "<circle class='line-pulse' cx='124' cy='230' r='20'/><circle class='line-pulse' cx='176' cy='178' r='24'/><circle class='line-pulse' cx='226' cy='210' r='20'/><circle class='line-pulse' cx='280' cy='142' r='26'/>"
        "</g>"
        "<g fill='url(#pkgLineGrad)' filter='url(#pkgGlow)' opacity='.42'>"
        "<circle cx='200' cy='180' r='54'/>"
        "</g>"
        "<g fill='#152032' font-family='Inter, Noto Sans JP, sans-serif' text-anchor='middle' font-weight='800'>"
        "<text x='200' y='174' font-size='18'>Claude Code</text>"
        "<text x='200' y='199' font-size='18'>Codex Lab</text>"
        "</g>"
        "</svg>"
        "</div>"
        "<div class='package-visual-label'><span>環境構築済み</span><span>成果物あり</span><span>課題持ち込み</span></div>"
        "</div>"
        "<div class='package-stage-copy'>"
        "<p class='package-stage-kicker'>HIKONE MONTHLY LAB</p>"
        "<h3>入口は広く、実践会は深く。<br>彦根で Claude Code / Codex を定期開催。</h3>"
        "<p>実践会は、当日のインストール対応で終わらないよう参加条件を明確にします。まだ不安な方には準備会を用意し、実践会の質と集客の入口を両方守ります。</p>"
        "<div class='package-track-tabs'>"
        "<div class='track-pill'><b>準備会</b><span>環境構築・最初の成果物まで</span></div>"
        "<div class='track-pill'><b>実践会</b><span>3日以上利用 + 成果物 + 課題持ち込み</span></div>"
        "</div>"
        "</div>"
        "</div>"
        "<div class='packages-grid'>"
    ]
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
            f"<div class='pkg-topline'><span class='pkg-cat'>{html.escape(it['cat'])}</span><span class='pkg-no'>{i + 1:02d}</span></div>"
            f"<div class='pkg-head'>"
            f"<span class='pkg-icon' aria-hidden='true'>{html.escape(it['icon'])}</span>"
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
        "60秒診断｜準備会・実践会・伴走のどれ？"
        "</button>"
        "<span class='packages-cta-hint'>3つの質問に答えるだけ。いまの状態に合う入口をその場で提案します。</span>"
        "</div>"
    )
    parts.append(
        "<p class='packages-note fade-up d4'>"
        "<strong>実践会の品質方針:</strong> 「3日以上使った」だけではなく、環境構築済み・成果物あり・持ち込み課題ありを基準にします。"
        "まだ条件に満たない方は準備会へ案内し、入口を閉じずに実践会の密度を守ります。"
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
        "<div class='footer-logo'><span class='brand-mark' aria-hidden='true'><span class='brand-a'>A</span><span class='brand-ha'>ハ</span></span><span class='wordmark'><span class='word-ai'>AI</span><span class='word-hub'>ハブ</span><span class='word-en'>AI HUB</span></span></div>"
        "<p class='footer-tagline'>滋賀・彦根の中小事業者向けに、AI講習・Web経営コンサル・補助金支援を行う"
        "「実装する経営者」。9事業を実際に回しながら、現場に居着くAIを一緒に作ります。</p>"
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
        "<p>AIハブ（クライミングコンサル）</p>"
        "<p>代表 由井 辰美</p>"
        "<p>〒522-0043<br>滋賀県彦根市岡町12番地</p>"
        f"<p><a href='mailto:{OWNER_EMAIL}'>{OWNER_EMAIL}</a></p>"
        "<p class='footer-area'>対応: 彦根・湖東・滋賀県全域 / 出張・オンライン全国</p>"
        "</div>"
        "</div>"
        f"<div class='footer-copy'>© {year} 由井 辰美 / AIハブ — 滋賀・彦根のAI講習 & Web経営コンサル</div>"
        "</footer>"
    )


def _render_sticky_cta() -> str:
    """モバイルで常時追従する無料相談バー（スクロール中もCVできる）。"""
    return (
        "<div class='sticky-cta' id='sticky-cta' aria-hidden='false'>"
        "<div class='sticky-cta-text'><strong>相談は無料</strong><span>補助金で実質1/3以下</span></div>"
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
        "<span class='cp-title'>無料の30分相談を予約する</span>"
        "<span class='cp-desc'>カレンダーから空いている日時を選ぶだけ。2〜3分で予約できます（料金はかかりません）。相談は Zoom か LINE で行います。</span>"
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
        ("① まず相談（無料）", "メールかLINEで「困っていること」を教えてください。30分で、AIで何ができそうかを一緒に整理します。"),
        ("② やることを決める", "あなたの仕事の中で「まずこれをAIに任せよう」という1つを決め、費用と進め方をお見せします。"),
        ("③ 一緒に作る", "むずかしい設定は講師が代わりにやります。あなたは「使えるようになる」ことに集中。その日から動く形で持ち帰り。"),
        ("④ 続けてサポート", "始めたあとも毎月いっしょに振り返り。うまくいかない所は何度でも聞けます。"),
    ]
    parts = ["<div class='flow-list'>"]
    for title, body in steps:
        parts.append(
            f"<div class='flow-step'><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>"
        )
    parts.append("</div>")
    return "".join(parts)


# FAQ は本文表示と FAQPage 構造化データの両方で使う（一次情報＝LLMO引用源）。
# 地域・お悩み・補助金の検索意図を素の質問形で網羅する。
FAQ_QA = [
    ("彦根・滋賀でAIの講習や相談はできますか？",
     "はい。滋賀県彦根市を拠点に、彦根・湖東・東近江を中心とした対面のAI講習・個別相談を行っています。京都・大阪・名古屋までは出張可、リモートなら全国対応します。"),
    ("Claude Code / Codex 実践会の参加条件はありますか？",
     "あります。実践会は、Claude Code または Codex を3日以上使ったことがあり、自分で1つ以上動くものを作った経験があり、cd・ls・git など基本コマンドに抵抗がない方を対象にします。申込時に、環境構築済みか、作ったもの、当日扱いたい課題を確認します。条件に満たない方は準備会を案内します。"),
    ("料金はどれくらいですか？",
     "【AI無料相談】まずは30分の導入相談は無料、【AI個別相談】しっかり60分最適AI導入は4,400円、【講習】ClaudeCode Codex準備/実践は5,500円から。【AI伴走支援パック】いっしょに実務導入は月額10万円×6ヶ月が目安です。LP制作は1本18〜30万円が目安。多くは補助金併用を前提に組みます。"),
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
            f"<img src='{html.escape(sp.get('avatar_url') or '', quote=True)}' alt='{name} のビジュアル' "
            f"loading='lazy' decoding='async'>"
            "<span class='speaker-art-orbit' aria-hidden='true'></span>"
            "<span class='speaker-art-chip ai' aria-hidden='true'>AI GUIDE</span>"
            "<span class='speaker-art-chip live' aria-hidden='true'>LIVE LESSON</span>"
            "<span class='speaker-art-spark s1' aria-hidden='true'></span>"
            "<span class='speaker-art-spark s2' aria-hidden='true'></span>"
            "<span class='speaker-art-spark s3' aria-hidden='true'></span>"
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
    title = f"{OWNER_NAME} — 滋賀のWeb経営コンサル | AIハブ"
    desc = "9事業を回す現役オーナーによる Web 経営コンサル。LP / 業務システム / AI 活用 / 補助金支援を、数字根拠で動かす伴走型サービス。"

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

    # 1. 受講プラン（Claude Code / Codex 実践会を中心に再編）— メインCTA
    parts.append("<section class='block' id='packages'>")
    parts.append("<p class='section-heading fade-up'>HIKONE AI LAB</p>")
    parts.append("<h2 class='section-title fade-up d1'><span class='title-line'>彦根 Claude Code</span> <span class='title-line'>/ Codex</span> <span class='title-line'>講習プラン</span></h2>")
    parts.append("<p class='section-sub fade-up d2'>"
                 "<span class='lv-flow'><span class='lv-flow-step'>準備会 環境を整える</span><span class='lv-flow-arr'>→</span>"
                 "<span class='lv-flow-step'>実践会 作って深める</span><span class='lv-flow-arr'>→</span>"
                 "<span class='lv-flow-step'>伴走 業務に入れる</span></span><br>"
                 "実践会は参加条件を設け、初心者は準備会へ案内します。場の質を守りながら、入口は閉じません。</p>")
    parts.append(_render_courses_packages())
    parts.append("</section>")

    # 2. ご依頼の流れ
    parts.append("<section class='block' id='flow'>")
    parts.append("<p class='section-heading'>FLOW</p>")
    parts.append("<h2 class='section-title'>ご依頼の流れ</h2>")
    parts.append("<p class='section-sub'>ご相談から公開・運用まで、最短 2 週間で動き始めます。</p>")
    parts.append(_render_flow())
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

    # 4. FAQ（疑問解消）
    parts.append("<section class='block' id='faq'>")
    parts.append("<p class='section-heading'>FAQ</p>")
    parts.append("<h2 class='section-title'>よくある質問</h2>")
    parts.append(_render_faq())
    parts.append("</section>")

    # 4b. 制作実績（TOP内にサマリを掲載・各カードは公開サイト本体へ直リンク）
    parts.append("<section class='block' id='works'>")
    parts.append("<p class='section-heading fade-up'>WORKS</p>")
    parts.append("<h2 class='section-title fade-up d1'>制作実績・運営サイト</h2>")
    parts.append("<p class='section-sub fade-up d2'>すべて自分で構築・運用している実物。カードから各サイトへ直接どうぞ。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_works_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-secondary' href='/portfolio.html'>📂 実績の詳細・技術スタックを見る →</a></div>")
    parts.append("</section>")

    # 4c. 講習資料（TOP内にサマリを掲載）
    parts.append("<section class='block' id='lectures'>")
    parts.append("<p class='section-heading fade-up'>MATERIALS</p>")
    parts.append("<h2 class='section-title fade-up d1'>講習資料</h2>")
    parts.append("<p class='section-sub fade-up d2'>AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）に加え、CodexとAIコーディングを仕事で使うための実装講習を整理しています。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_lectures_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-secondary' href='/lectures/index.html'>📚 講習資料の一覧を見る →</a></div>")
    parts.append("</section>")

    # 5. お問い合わせ（Resend 送信フォーム）
    parts.append("<section class='block' id='contact'>")
    parts.append("<p class='section-heading fade-up'>CONTACT</p>")
    parts.append("<h2 class='section-title fade-up d1'>まずは 30 分、無料でご相談</h2>")
    parts.append("<p class='section-sub fade-up d2'>「何から始めればいいか」を一緒に整理します。日程を選んで予約するだけ。相談は Zoom か LINE で、お気軽にどうぞ。</p>")
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
