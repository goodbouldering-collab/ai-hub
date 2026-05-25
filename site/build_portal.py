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
    "<link rel='mask-icon' href='/favicon.svg' color='#7aa2ff'>"
    "<meta name='theme-color' content='#0d1126'>"
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


def _build_ogp(title: str, description: str, page_url: str) -> str:
    return "".join([
        f"<meta property='og:title' content='{html.escape(title, quote=True)}'>",
        f"<meta property='og:description' content='{html.escape(description, quote=True)}'>",
        f"<meta property='og:url' content='{html.escape(page_url, quote=True)}'>",
        "<meta property='og:type' content='website'>",
        "<meta property='og:site_name' content='AIハブ'>",
        "<meta name='twitter:card' content='summary'>",
    ])


def _build_jsonld_website() -> str:
    doc = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "AIハブ",
        "url": SITE_URL,
        "description": f"{OWNER_NAME}のCEOポータル。9事業への入口・講習資料・AI情報を集約。",
    }
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": OWNER_NAME,
        "jobTitle": "AI講師 / 複数事業オーナー",
        "email": OWNER_EMAIL,
        "url": SITE_URL,
    }
    return json.dumps([doc, person], ensure_ascii=False)


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
/* ===== Obsidian Solid (案A: ダーク高級ミニマル + ブルータリズム) =====
   デフォルトをオブシディアン・ダークに。アクセントはシアン #6E8BFF 単色。
   data-theme="light" で明るいバリアントに切替可能（トグルは維持）。 */
:root {
  /* ===== Linear 型: 暗背景 × 青→紫グラデ発光 ===== */
  --bg-base: #0B0D14;        /* 深い夜空ネイビー */
  --bg-white: #11131D;       /* 1段明るいパネル */
  --bg-elev: #161925;        /* さらに上のカード面 */
  --text: #F4F6FB;
  --text-soft: #A6AEC4;
  --muted: #6B7488;
  --line: rgba(255,255,255,0.08);   /* 極薄の境界線（硬い枠を排除） */
  --line-strong: rgba(255,255,255,0.14);
  --primary: #6E8BFF;        /* インディゴ・ブルー */
  --primary-soft: #8AA0FF;
  --violet: #9B7BFF;         /* バイオレット */
  --primary-bg: rgba(110,139,255,0.10);   /* アクセントの淡い面 */
  /* グラデーション（Linear のシグネチャ：青→紫） */
  --grad: linear-gradient(120deg, #6E8BFF 0%, #9B7BFF 55%, #C77DFF 100%);
  --grad-soft: linear-gradient(120deg, rgba(110,139,255,.16), rgba(199,125,255,.14));
  --emerald: #5BE0B0;
  --amber: #F4C667;
  --pink: #C77DFF;
  --glass-bg: rgba(20,23,34,0.62);          /* ガラス面 */
  --glass-border: rgba(255,255,255,0.10);   /* 微細な光彩ボーダー */
  --glass-hi: rgba(255,255,255,0.06);       /* 内側ハイライト(上端の光) */
  --glass-blur: 22px;                        /* backdrop blur 基準値 */
  --shadow-card: 0 10px 40px rgba(0,0,0,0.30);
  --shadow-card-hover: 0 24px 70px rgba(0,0,0,0.45), 0 0 0 1px rgba(139,160,255,0.22);
  --glow: 0 0 60px rgba(110,139,255,0.35);   /* 柔らかい発光 */
  --radius: 20px;                            /* カード角丸（やわらかく） */
  --radius-sm: 14px;
  --serif: "Inter", -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;  /* 見出しもサンセリフ化 */
  --mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
}
:root[data-theme="light"] {
  --bg-base: #F7F8FC;
  --bg-white: #FFFFFF;
  --bg-elev: #FFFFFF;
  --text: #0B0D14;
  --text-soft: #404A63;
  --muted: #6B7488;
  --line: rgba(11,13,20,0.08);
  --line-strong: rgba(11,13,20,0.14);
  --primary: #5468FF;
  --primary-soft: #6E8BFF;
  --violet: #8B5CF6;
  --primary-bg: rgba(84,104,255,0.08);
  --grad: linear-gradient(120deg, #5468FF 0%, #8B5CF6 55%, #C77DFF 100%);
  --grad-soft: linear-gradient(120deg, rgba(84,104,255,.10), rgba(199,125,255,.08));
  --glass-bg: rgba(255,255,255,0.70);
  --glass-border: rgba(11,13,20,0.08);
  --glass-hi: rgba(255,255,255,0.65);
  --shadow-card: 0 10px 40px rgba(15,23,42,0.08);
  --shadow-card-hover: 0 24px 70px rgba(15,23,42,0.16), 0 0 0 1px rgba(84,104,255,0.20);
  --glow: 0 0 50px rgba(84,104,255,0.20);
}
:root { color-scheme: dark; }
:root[data-theme="light"] { color-scheme: light; }
html, body, .hero, .biz-card, .service-card, .pkg-card, .faq-item, .stat,
.site-header, .menu-drop, .mobile-nav, .diagnose-box {
  transition: background-color .3s ease, color .3s ease, border-color .3s ease;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; overflow-x: hidden; }
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
  background:
    radial-gradient(1100px 600px at 8% -8%, rgba(110,139,255,.20), transparent 58%),
    radial-gradient(900px 600px at 92% 4%, rgba(199,125,255,.14), transparent 56%),
    radial-gradient(700px 500px at 50% 110%, rgba(155,123,255,.10), transparent 60%),
    linear-gradient(180deg, var(--bg-white) 0%, var(--bg-base) 60%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
  letter-spacing: -0.005em;
}
::selection { background: rgba(139,160,255,.35); color: var(--text); }

/* ---- glassmorphism helpers (再利用) ----
   カード/ヘッダー/ドロップに共通で当てる「ガラス質感」。
   半透明背景 + backdrop blur + 1px光彩ボーダー + 上端の内側ハイライト。 */
.biz-card, .service-card, .pkg-card, .faq-item, .stat,
.menu-drop, .diagnose-box, .hero-quiz {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(var(--glass-blur)) saturate(140%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(140%);
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card), inset 0 1px 0 var(--glass-hi);
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
  font-size: 18px; font-weight: 800; letter-spacing: -.01em;
  color: var(--text); text-decoration: none;
  display: inline-flex; align-items: center; gap: 8px;
}
.site-logo .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--grad); box-shadow: 0 0 12px rgba(139,160,255,.6); display: inline-block; }
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
.site-nav .login-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 18px; border-radius: 999px;
  background: var(--glass-bg); color: var(--text);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  font-size: 13px; font-weight: 600;
  text-decoration: none; transition: border-color .2s, transform .2s, box-shadow .2s;
}
.site-nav .login-btn:hover { border-color: var(--line-strong); transform: translateY(-1px); box-shadow: 0 0 24px rgba(110,139,255,.22); }

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
  padding: 32px 0 64px;
  display: grid; grid-template-columns: 1.05fr 1fr; gap: 48px; align-items: center;
  position: relative;
}
.hero-text { text-align: left; min-width: 0; max-width: 100%; }
@media (max-width: 900px) { .hero { grid-template-columns: 1fr; gap: 28px; }
  .hero-text { text-align: center; }
}
.hero .eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 16px; border-radius: 999px;
  background: var(--primary-bg); color: var(--primary-soft);
  font-family: var(--mono); font-size: 11.5px; font-weight: 600; letter-spacing: .06em;
  border: 1px solid var(--glass-border);
  box-shadow: inset 0 0 0 1px rgba(139,160,255,.10), 0 0 24px rgba(110,139,255,.12);
  max-width: 100%;
}
@media (max-width: 560px) {
  .hero .eyebrow {
    display: flex; text-align: left; line-height: 1.5;
    padding: 8px 12px; font-size: 10.5px;
  }
}
.hero h1 {
  margin: 22px 0 18px; font-size: clamp(38px, 7vw, 78px);
  font-family: var(--serif); font-weight: 800; letter-spacing: -.03em;
  color: var(--text); line-height: 1.08;
  overflow-wrap: anywhere; word-break: normal;
}
.hero h1 .accent {
  background: var(--grad);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero h1 .underline {
  position: relative;
}
.hero h1 .underline::after {
  content:''; position: absolute; left: 0; right: 0; bottom: 2px; height: 8px;
  background: var(--grad); opacity: .35;
  border-radius: 999px; z-index: -1; filter: blur(2px);
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
  display: flex; flex-wrap: wrap; gap: 12px;
}
@media (max-width: 900px) { .hero-actions { justify-content: center; } }

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
.hq-opt:hover { border-color: var(--primary); transform: translateY(-2px); background: var(--primary-bg); box-shadow: 0 0 24px rgba(110,139,255,.18); }
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
.hero-visual:hover { transform: translateY(-4px); }
.hero-visual img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 1.2s ease; }
.hero-visual:hover img { transform: scale(1.04); }
.hero-visual::after {
  content:''; position: absolute; inset: 0;
  background:
    linear-gradient(160deg, rgba(110,139,255,.10) 0%, rgba(199,125,255,.12) 50%, transparent 70%),
    linear-gradient(0deg, rgba(11,13,20,.40) 0%, rgba(11,13,20,0) 42%);
  pointer-events: none;
}
.hero-blob {
  position: absolute; width: 260px; height: 260px; border-radius: 50%;
  filter: blur(60px); opacity: .55; z-index: -1; pointer-events: none;
}
.hero-blob.b1 { background: #6E8BFF; top: -40px; right: -40px; }
.hero-blob.b2 { background: #9B7BFF; bottom: -40px; left: 30%; width: 200px; height: 200px; }
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
  cursor: pointer; border: none; letter-spacing: -.01em;
}
.btn-primary {
  background: var(--grad); color: #fff;
  box-shadow: 0 8px 30px rgba(110,139,255,.40), inset 0 1px 0 rgba(255,255,255,.25);
}
.btn-primary:hover { transform: translateY(-2px); filter: brightness(1.08); box-shadow: 0 14px 44px rgba(139,160,255,.55), inset 0 1px 0 rgba(255,255,255,.30); }
.btn-secondary {
  background: var(--glass-bg); color: var(--text);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 var(--glass-hi);
}
.btn-secondary:hover { border-color: var(--line-strong); transform: translateY(-2px); box-shadow: 0 0 30px rgba(110,139,255,.18); }
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
  line-height: 1.1; letter-spacing: -.02em;
}
.stat .label { font-size: 12.5px; color: var(--muted); margin-top: 6px; font-weight: 600; }

/* ---- section frame ---- */
section.block { padding: 72px 0; scroll-margin-top: 96px; }
section.block + section.block { border-top: 1px solid var(--line); }
.section-title {
  font-family: var(--serif);
  font-size: clamp(28px, 4vw, 46px); font-weight: 800; letter-spacing: -.03em;
  color: var(--text); text-align: center; margin: 0 0 14px; line-height: 1.15;
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
.service-card:hover { transform: translateY(-6px) rotate(-.3deg); box-shadow: var(--shadow-card-hover); border-color: rgba(139,160,255,.30); }
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
.service-name { font-size: 17px; font-weight: 800; color: var(--text); margin-bottom: 8px; }
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
  background: radial-gradient(420px 160px at 0% 0%, var(--card-glow, rgba(139,160,255,.12)) 0%, transparent 60%);
  opacity: 0; transition: opacity .35s; pointer-events: none;
}
.biz-card:hover::before { opacity: 1; }
.biz-card:hover {
  transform: translateY(-6px) rotate(.3deg);
  border-color: var(--card-border, rgba(139,160,255,.45));
  box-shadow: var(--shadow-card-hover);
}
.biz-card.no-link { cursor: default; opacity: .65; }
.biz-card.no-link:hover { transform: none; box-shadow: var(--shadow-card); border-color: var(--line); }
.biz-card.self-card { border-color: rgba(139,160,255,.5); background: var(--primary-bg); }
.biz-card-icon { font-size: 28px; line-height: 1; margin-bottom: 2px; }
.biz-card-name { font-size: 16.5px; font-weight: 800; color: var(--text); line-height: 1.3; }
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
.biz-badge.self { background: rgba(139,160,255,.15); color: var(--primary); border: 1px solid rgba(139,160,255,.35); }
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

/* ---- packages (AI講習・相談・伴走パック) ---- */
.packages-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 12px;
}
@media (max-width: 1100px) { .packages-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .packages-grid { grid-template-columns: 1fr; } }
/* 診断結果で該当レベル以外を減光（.pkg-filter-active 時のみ） */
.packages-grid.pkg-filter-active .pkg-card { opacity: .38; transition: opacity .35s ease; }
.packages-grid.pkg-filter-active .pkg-card.pkg-match { opacity: 1; outline: 2px solid var(--primary); outline-offset: 2px; }
.pkg-card {
  background: var(--bg-elev);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  display: flex; flex-direction: column;
  box-shadow: var(--shadow-card);
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
  position: relative; overflow: hidden;
}
.pkg-card:hover {
  transform: translateY(-6px); box-shadow: var(--shadow-card-hover);
  border-color: rgba(139,160,255,.28);
}
.pkg-image {
  position: relative; aspect-ratio: 16/10; overflow: hidden;
}
.pkg-image img {
  width: 100%; height: 100%; object-fit: cover; display: block;
  transition: transform .6s cubic-bezier(.22,1,.36,1);
}
.pkg-card:hover .pkg-image img { transform: scale(1.07); }
.pkg-image::after {
  content:''; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(15,23,42,0) 40%, rgba(15,23,42,.28) 100%);
}
.pkg-image .pkg-cat {
  position: absolute; top: 12px; left: 12px; z-index: 1;
  box-shadow: 0 4px 12px rgba(0,0,0,.18);
}
.pkg-body {
  padding: 20px 22px 22px;
  display: flex; flex-direction: column; gap: 10px; flex: 1;
}
.pkg-head { display: flex; align-items: flex-start; gap: 10px; }
.pkg-icon { font-size: 26px; line-height: 1.1; }
.pkg-cat {
  font-size: 11px; font-weight: 700; letter-spacing: .08em;
  color: #b45309; background: #fef3c7;
  padding: 4px 10px; border-radius: var(--radius-sm);
}
.pkg-title { font-size: 16px; font-weight: 800; color: var(--text); line-height: 1.4; margin: 2px 0 0; flex: 1; }
.pkg-meta { font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pkg-level {
  font-family: var(--mono); font-size: 10.5px; font-weight: 700; letter-spacing: .06em;
  padding: 3px 10px; border: 1px solid var(--glass-border); color: var(--primary-soft);
  background: var(--primary-bg); border-radius: 999px;
}
.pkg-level[data-level="beginner"] { opacity: 1; }
.pkg-level[data-level="intermediate"] { opacity: 1; }
.pkg-level[data-level="advanced"] { opacity: 1; }
.pkg-price {
  font-size: 20px; font-weight: 900;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent;
}
.pkg-subsidy {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 700; color: #047857;
  background: #d1fae5; padding: 4px 10px; border-radius: 8px;
  width: fit-content;
}
.pkg-desc { font-size: 13px; line-height: 1.7; color: var(--text); flex: 1; margin: 4px 0; }
.pkg-cta {
  display: inline-flex; align-items: center; justify-content: center;
  margin-top: auto; padding: 12px 16px;
  background: var(--grad);
  color: #fff; font-weight: 600; font-size: 14px;
  text-decoration: none; border-radius: 999px;
  box-shadow: 0 6px 22px rgba(110,139,255,.32), inset 0 1px 0 rgba(255,255,255,.22);
  transition: opacity .15s ease, transform .15s ease;
}
.pkg-cta:hover { opacity: .92; transform: translateY(-1px); }
.packages-note {
  margin-top: 22px; padding: 16px 20px;
  background: var(--grad-soft); border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  font-size: 13px; line-height: 1.7; color: var(--text);
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

/* ---- カード/パネル面は変数化（デフォルト=obsidian dark） ---- */
.pkg-card, .service-card, .biz-card { background: var(--bg-elev); }
.pkg-cat { background: var(--primary-bg); color: var(--primary-soft); }
.pkg-subsidy { background: var(--primary-bg); color: var(--primary-soft); }

/* ---- diagnose modal ---- */
.btn-diagnose {
  background: var(--primary); color: #0B0D14;
  border: none; cursor: pointer; font-weight: 800; font-size: 15px;
  padding: 14px 26px; border-radius: var(--radius-sm);
  box-shadow: 0 10px 30px rgba(139,160,255,.32);
  transition: transform .15s ease, box-shadow .15s ease;
}
.btn-diagnose:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(139,160,255,.42); }
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
.diag-result-name { font-family: var(--serif); font-size: 26px; font-weight: 900; color: var(--text); margin: 6px 0; line-height: 1.3; }
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
  letter-spacing: -.02em;
}
.flow-step h3 { font-size: 15px; font-weight: 800; color: var(--text); margin: 0 0 8px; }
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
.lecture-card:hover { transform: translateY(-3px); border-color: rgba(139,160,255,.40); box-shadow: var(--shadow-card-hover); }
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
@media (max-width: 720px) { .speaker-art { max-width: 320px; margin: 0 auto; } }
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
.profile-block h3 { font-size: 22px; font-weight: 800; margin: 0 0 10px; color: var(--text); }
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
.contact-choices {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
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

/* ---- footer ---- */
footer.site-footer {
  margin-top: 48px; padding: 32px 0 12px;
  color: var(--muted); font-size: 12px; text-align: center;
  border-top: 1px solid var(--line);
}

/* ---- 制作実績カード（LP #portfolio。build_site CONTENT_CSS から移植・PORTALトークン化）---- */
.pf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 8px;
}
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
  border-color: rgba(139,160,255,.30);
  box-shadow: var(--shadow-card-hover);
}
.pf-card .pf-title { font-weight: 800; font-size: 15px; color: var(--text); }
.pf-card .pf-host { font-size: 11.5px; color: var(--muted); margin-top: 2px; word-break: break-all; }
.pf-card .pf-sum { font-size: 13px; color: var(--text-soft); line-height: 1.55; margin: 8px 0 10px; flex: 1; }
.pf-card .pf-meta { display: flex; flex-wrap: wrap; gap: 6px; font-size: 11px; }
.pf-card .pf-chip {
  padding: 2px 8px; border-radius: var(--radius-sm);
  background: rgba(139,160,255,.10); color: var(--primary);
  border: 1px solid rgba(139,160,255,.20);
}
.pf-card .pf-chip.cat { background: rgba(139,160,255,.10); color: var(--primary); border-color: rgba(139,160,255,.20); }
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
.profile-tl-item:hover { border-color: rgba(139,160,255,.30); transform: translateX(2px); }
.profile-tl-item::before {
  content: ''; position: absolute; left: -36px; top: 22px;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--primary); border: 3px solid #fff;
  box-shadow: 0 0 0 3px rgba(139,160,255,.20);
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
        "<a class='site-logo' href='/'><span class='dot'></span>AIハブ <span style='color:var(--muted);font-weight:600;font-size:13px;margin-left:6px;'>by 由井辰美</span></a>"
        "<nav class='site-nav' aria-label='メインナビ'>"
        "<a class='nav-link' href='#packages'>受講プラン</a>"
        "<a class='nav-link' href='#flow'>ご依頼の流れ</a>"
        "<a class='nav-link' href='#speaker'>講師紹介</a>"
        "<a class='nav-link' href='#faq'>FAQ</a>"
        "<div class='menu-wrap'>"
        "<button class='menu-toggle' id='menu-toggle' aria-haspopup='menu' aria-expanded='false'>その他"
        "<svg class='chev' width='14' height='14' viewBox='0 0 20 20' fill='none' aria-hidden='true'><path d='M5 8l5 5 5-5' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        "</button>"
        "<div class='menu-drop' id='menu-drop' role='menu'>"
        "<a href='#works'>📂 制作実績</a>"
        "<a href='#lectures'>📚 講習資料</a>"
        "<a href='#contact'>✉ お問い合わせ</a>"
        "</div>"
        "</div>"
        "<button type='button' class='theme-toggle' aria-label='ダークモードに切替'>🌙</button>"
        "<a class='login-btn' href='/admin'>🔐 管理ログイン</a>"
        "</nav>"
        "<button type='button' class='theme-toggle theme-toggle-mobile' aria-label='ダークモードに切替'>🌙</button>"
        "<button class='mobile-toggle' id='mobile-toggle' aria-label='メニュー'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'><path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg>"
        "</button>"
        "</div>"
        "<div class='mobile-nav' id='mobile-nav'>"
        "<a href='#packages'>受講プラン</a>"
        "<a href='#flow'>ご依頼の流れ</a>"
        "<a href='#speaker'>講師紹介</a>"
        "<a href='#faq'>FAQ</a>"
        "<a href='#contact'>お問い合わせ</a>"
        "<a href='#works'>制作実績</a>"
        "<a href='#lectures'>講習資料</a>"
        "<a class='login-btn-mobile' href='/admin'>🔐 管理ログイン</a>"
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

  // ---- テーマ切替 (デフォルトはオブシディアン dark。light で明るいバリアント)
  (function(){
    var KEY = 'aihub-theme';
    var root = document.documentElement;
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch(e) {}
    // 保存があればそれ、無ければデフォルト dark(=data-theme属性なし)
    var mode = saved === 'light' ? 'light' : 'dark';
    function apply(m){
      if (m === 'light') root.setAttribute('data-theme', 'light');
      else root.removeAttribute('data-theme');
      var btns = document.querySelectorAll('.theme-toggle');
      btns.forEach(function(b){ b.textContent = (m === 'dark') ? '☀️' : '🌙'; b.setAttribute('aria-label', m === 'dark' ? 'ライトモードに切替' : 'ダークモードに切替'); });
    }
    apply(mode);
    document.addEventListener('click', function(e){
      var t = e.target.closest && e.target.closest('.theme-toggle');
      if (!t) return;
      mode = (root.getAttribute('data-theme') === 'light') ? 'dark' : 'light';
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
      { q: 'いま、AIをどれくらい使っていますか？', a: [
        { label: 'ほぼ使っていない', lv: 'beginner' },
        { label: 'ChatGPTなどを自己流で時々', lv: 'intermediate' },
        { label: '一部業務で日常的に使えている', lv: 'advanced' },
      ]},
      { q: '一番かなえたいことは？', a: [
        { label: 'まず何ができるか知りたい', lv: 'beginner' },
        { label: '自分や社員のスキルを底上げしたい', lv: 'intermediate' },
        { label: '会社の業務を仕組み化・自動化したい', lv: 'advanced' },
      ]},
      { q: 'どのスパンで取り組みたい？', a: [
        { label: 'まず1回・短時間で', lv: 'beginner' },
        { label: '半日〜月1回で集中的に', lv: 'intermediate' },
        { label: '数ヶ月かけて本格的に', lv: 'advanced' },
      ]},
    ];
    var RESULT = {
      beginner: {
        badge: '初級', title: 'まずは「効く実感」から',
        name: 'AI個別相談 60分',
        desc: '何ができるかを30〜60分で具体化。あなたの業務に効くAI活用を最短でアドバイスします。',
        level_id: 'beginner'
      },
      intermediate: {
        badge: '中級', title: '「使える」を「仕組み」に',
        name: 'AI仕組み化ワークショップ 半日 / AI講習会',
        desc: '自己流から脱却し、1業務をその場で仕組み化。属人化を断ち切り明日から動くマニュアルごと持ち帰れます。',
        level_id: 'intermediate'
      },
      advanced: {
        badge: '上級', title: '組織のインフラにする',
        name: 'AI伴走パック 6回',
        desc: '6ヶ月で組織にAIを定着。導入・内製化・自動化まで伴走。滋賀・彦根の補助金で負担1/3以下に。',
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
    var sel = '.biz-card, .service-card, .pkg-card, .faq-item, .stat';
    var els = Array.prototype.slice.call(document.querySelectorAll(sel));
    if (!els.length || !('IntersectionObserver' in window)) return;
    els.forEach(function(el, i){ el.classList.add('reveal'); el.style.transitionDelay = Math.min(i * 40, 240) + 'ms'; });
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function(el){ io.observe(el); });
  })();
})();
</script>
"""


HERO_IMG = "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=1200&q=70"


def _render_hero() -> str:
    return (
        "<section class='hero' id='top'>"
        "<div class='hero-blob b1'></div>"
        "<div class='hero-blob b2'></div>"
        "<div class='hero-text fade-up'>"
        "<span class='eyebrow'>📍 彦根・滋賀・湖東｜現場リーダー限定ワークショップ</span>"
        "<h1>"
        "<span class='accent'>業務まるごと、</span><br>"
        "AIに任せる。"
        "</h1>"
        "<p class='sub-catch'>"
        "彦根の対面ワークショップで、"
        "<strong>集客・人手不足・業務の自動化</strong>の仕組みを、その場で完成。"
        "</p>"
        "<p class='lead'>"
        "ITの勉強はゼロ。社長の仕事は「どの業務を任せるか」を決めるだけ。"
        "<strong>週10時間の無駄</strong>を削る仕組みを、その日のうちに持ち帰れます。"
        "</p>"
        # ヒーロー起点の AIレベル診断（第1問を常時表示）
        "<div class='hero-quiz'>"
        "<div class='hq-label'><span class='hq-mono'>30秒 AI診断</span>いま、AIをどれくらい使っていますか？</div>"
        "<div class='hq-opts'>"
        "<button type='button' class='hq-opt diagnose-open' data-prelevel='beginner'>"
        "<span class='hq-lv'>初級</span>ほぼ使っていない</button>"
        "<button type='button' class='hq-opt diagnose-open' data-prelevel='intermediate'>"
        "<span class='hq-lv'>中級</span>自己流で時々使う</button>"
        "<button type='button' class='hq-opt diagnose-open' data-prelevel='advanced'>"
        "<span class='hq-lv'>上級</span>一部業務で日常的に</button>"
        "</div>"
        "<a class='hq-sub' href='/admin'>🔐 管理ログイン</a>"
        "</div>"
        "</div>"
        "<div class='hero-visual fade-up d2'>"
        f"<img src='{HERO_IMG}' alt='彦根・滋賀の現場リーダーがAI講師と対面で自社の業務仕組み化を設計している様子' loading='eager' fetchpriority='high' decoding='async'>"
        "<div class='hero-flow' aria-label='ワークショップの3ステップ'>"
        "<div class='hflow-step'>"
        "<span class='hflow-ico'>😵</span>"
        "<div class='hflow-txt'><b>現場の課題</b><small>人手不足・残業・属人化</small></div>"
        "</div>"
        "<div class='hflow-arrow'>→</div>"
        "<div class='hflow-step accent'>"
        "<span class='hflow-ico'>🧑‍🏫</span>"
        "<div class='hflow-txt'><b>対面ワークショップ</b><small>その場で一緒に設計</small></div>"
        "</div>"
        "<div class='hflow-arrow'>→</div>"
        "<div class='hflow-step done'>"
        "<span class='hflow-ico'>⚙️</span>"
        "<div class='hflow-txt'><b>仕組みが完成</b><small>週10時間を削減</small></div>"
        "</div>"
        "</div>"
        "</div>"
        "</section>"
    )


def _render_stats() -> str:
    items = [
        ("9", "", "同時運営事業"),
        ("30", "年", "クライミング歴"),
        ("100", "%", "Web 自社構築"),
        ("2027", "", "育成就労 移行支援"),
    ]
    parts = ["<div class='stats-strip'>"]
    for i, (num, suffix, label) in enumerate(items):
        cls = f"stat fade-up d{i+1}"
        suf_html = f"<span style='font-size:.6em'>{html.escape(suffix)}</span>" if suffix else ""
        parts.append(
            f"<div class='{cls}'><div class='num' data-count='{html.escape(num)}'>0{suf_html}</div><div class='label'>{html.escape(label)}</div></div>"
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
    """AI個別相談 / AI講習会 / AI伴走パック の3カード（minanowaから移管）"""
    items = [
        {
            "icon": "💬",
            "cat": "個別相談",
            "level": "初級",
            "level_id": "beginner",
            "title": "AI個別相談 60分",
            "price": "2,200円〜5,500円",
            "duration": "60分",
            "subsidy": False,
            "desc": "経営者・専門職・初心者なんでも相談。LLMO / SEO / MEO / Claude Code 活用 / バックオフィス効率化 / 補助金申請まで、現役オーナーがその場で「困った」を解決。",
            "url": "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP",
            "cta": "予約する（Square）",
            "img": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=800&q=70",
        },
        {
            "icon": "📚",
            "cat": "講習会",
            "level": "中級",
            "level_id": "intermediate",
            "title": "AI講習会 120分（月1回 / 定員8名）",
            "price": "5,500円",
            "duration": "120分",
            "subsidy": True,
            "desc": "彦根でAIや経営を学べる実践型講習。一般の講師が教えない「考え方とコツ」を中心に、参加者のレベルに合わせて内容を最適化。Claude Code / オフィス自動化 / 通販サイト構築まで。",
            "url": "https://goodbouldering.com/?pid=188553378",
            "cta": "詳細・お申込みはこちら",
            "img": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=800&q=70",
        },
        {
            "icon": "🛠️",
            "cat": "ワークショップ",
            "level": "中級",
            "level_id": "intermediate",
            "title": "AI仕組み化ワークショップ 半日",
            "price": "33,000円（税込・補助金対象）",
            "duration": "半日（4時間・対面）",
            "subsidy": True,
            "desc": "「使える」から「仕組みになる」へ。見積作成・問い合わせ対応・日報など現場の1業務をその場で自動化し、明日から動くマニュアルごと持ち帰る対面ワークショップ。属人化を断ち切る中級者の実装回。",
            "url": "mailto:goodbouldering@gmail.com?subject=AI仕組み化ワークショップ（半日）の相談",
            "cta": "開催を相談する",
            "img": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=70",
        },
        {
            "icon": "🚀",
            "cat": "伴走パック",
            "level": "上級",
            "level_id": "advanced",
            "title": "AI伴走パック 6回（補助金対象）",
            "price": "月額 100,000円（税込）× 6ヶ月",
            "duration": "6ヶ月（導入相談60分から開始）",
            "subsidy": True,
            "desc": "HP公開から事務自動化まで、技術的な難所は講師が代行・支援。AI導入・デザイン内製化・書類営業効率化・経理自動化・マーケティングを6ヶ月で一気に定着。滋賀・彦根の補助金で負担1/3以下に。",
            "url": "https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/V57YTNICA2KV2TN7ENARAVQE",
            "cta": "導入相談（無料・60分）",
            "img": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=800&q=70",
        },
    ]
    parts = ["<div class='packages-grid'>"]
    for i, it in enumerate(items):
        subsidy_badge = (
            "<span class='pkg-subsidy'>✓ 補助金対応</span>" if it["subsidy"] else ""
        )
        img_html = (
            f"<div class='pkg-image'>"
            f"<img src='{html.escape(it['img'], quote=True)}' alt='{html.escape(it['title'])}' loading='lazy' decoding='async'>"
            f"<span class='pkg-cat'>{html.escape(it['cat'])}</span>"
            f"</div>"
        ) if it.get("img") else ""
        lvl = it.get("level", "")
        lvl_id = it.get("level_id", "")
        level_badge = f"<span class='pkg-level' data-level='{html.escape(lvl_id)}'>{html.escape(lvl)}</span>" if lvl else ""
        # 外部URL(http)は別タブ、mailtoは同タブ
        is_ext = it["url"].startswith("http")
        target_attr = " target='_blank' rel='noopener'" if is_ext else ""
        parts.append(
            f"<div class='pkg-card fade-up d{(i % 3) + 1}' data-level='{html.escape(lvl_id)}'>"
            f"{img_html}"
            f"<div class='pkg-body'>"
            f"<div class='pkg-head'>"
            f"<span class='pkg-icon' aria-hidden='true'>{html.escape(it['icon'])}</span>"
            f"<h3 class='pkg-title'>{html.escape(it['title'])}</h3>"
            f"</div>"
            f"<div class='pkg-meta'>{level_badge}<span>⏱ {html.escape(it['duration'])}</span></div>"
            f"<div class='pkg-price'>{html.escape(it['price'])}</div>"
            f"{subsidy_badge}"
            f"<p class='pkg-desc'>{html.escape(it['desc'])}</p>"
            f"<a class='pkg-cta' href='{html.escape(it['url'], quote=True)}'{target_attr}>{html.escape(it['cta'])} →</a>"
            f"</div>"
            f"</div>"
        )
    parts.append("</div>")
    parts.append(
        "<div class='packages-cta-row fade-up d4'>"
        "<button type='button' class='btn btn-diagnose diagnose-open'>"
        "🔍 60秒診断｜あなたに合うプランは？"
        "</button>"
        "<span class='packages-cta-hint'>3つの質問に答えるだけ。最適なコースをその場でご提案します。</span>"
        "</div>"
    )
    parts.append(
        "<p class='packages-note fade-up d4'>"
        "🛡 <strong>滋賀県未来投資総合補助金</strong>（最大50万円・補助率2/3／一次：3/2〜3/31、二次：6/8〜7/17）と "
        "<strong>彦根市小規模事業者デジタル化推進補助金</strong>（最大20万円）に対応。申請サポートも個別相談で受け付けます。"
        "</p>"
    )
    return "".join(parts)


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
         "AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）の講習で使う資料。プログラミングマップも。",
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


def _render_contact_form() -> str:
    """問い合わせは「メール作成」と「LINE」の2導線（フォーム/サーバ送信なし）。"""
    mail_subject = "AI相談・講習のお問い合わせ"
    mail_body = (
        "下記にご記入のうえ送信してください。%0D%0A%0D%0A"
        "・お名前：%0D%0A"
        "・ご相談種別（AI個別相談 / 講習会・ワークショップ / 伴走パック / Web制作 / その他）：%0D%0A"
        "・ご相談内容（現状の課題・やりたいこと・ご予算感など）：%0D%0A"
    )
    mailto = (
        f"mailto:{html.escape(OWNER_EMAIL)}"
        f"?subject={html.escape(mail_subject, quote=True)}&body={mail_body}"
    )
    return (
        "<div class='contact-choices'>"
        f"<a class='contact-choice cc-mail fade-up' href='{mailto}'>"
        "<span class='cc-ico'>✉</span>"
        "<span class='cc-title'>メールで相談する</span>"
        "<span class='cc-desc'>記入項目入りのメールが立ち上がります。埋めて送信するだけ。2営業日以内にご返信します。</span>"
        "<span class='cc-cta'>メールを作成 →</span>"
        "</a>"
        f"<a class='contact-choice cc-line fade-up d2' href='{GUBBLE_LINE_URL}' target='_blank' rel='noopener'>"
        "<span class='cc-ico'>💬</span>"
        "<span class='cc-title'>LINEで相談する</span>"
        "<span class='cc-desc'>グッぼる公式LINEから、その場でメッセージ。気軽な質問・日程調整はこちらが早いです。</span>"
        "<span class='cc-cta'>LINEを開く →</span>"
        "</a>"
        "</div>"
        "<p class='contact-sub-note fade-up'>"
        "どちらか迷う方は、まず "
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
        ("ご相談", "メール／LINEで現状をヒアリング。事業内容・課題・予算感を 30 分でつかみます。"),
        ("提案・見積", "課題に対する具体的なアウトプット案（LP / 業務システム / 研修 等）と費用感を提示。"),
        ("制作・実装", "Next.js + Supabase + Vercel で構築。PR プレビューで毎日確認できる開発フロー。"),
        ("運用・伴走", "公開後も月次レビューで KPI を一緒に確認。必要な機能追加・運用代行も対応。"),
    ]
    parts = ["<div class='flow-list'>"]
    for title, body in steps:
        parts.append(
            f"<div class='flow-step'><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_faq() -> str:
    qa = [
        ("料金はどれくらいですか？",
         "LP 1本（簡易ヒアリング込み）で 18〜30万円が目安です。業務システム・EC 統合・社内RAG は内容により別途お見積もり。補助金併用を前提に組むことが多いです。"),
        ("対応エリアは？",
         "滋賀県を中心に、京都・大阪・名古屋まで対面 / 出張可。リモートだけでも全国対応します。"),
        ("自分は IT に弱いのですが、大丈夫ですか？",
         "9事業のオーナーをやっているので「経営者目線」で話します。LINE / メール / ZOOM どれでも、専門用語を避けて進めます。"),
        ("AI を会社で使いたいのですが、何から始めれば？",
         "まずは社内ドキュメントを 1 ヶ所にまとめ、RAG（社内 Q&A）から導入するのを推奨しています。AIハブ自体がそのリファレンス実装になっています。"),
    ]
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
            f"<div class='speaker-art'>"
            f"<img src='{html.escape(sp.get('avatar_url') or '', quote=True)}' alt='{name} のビジュアル' "
            f"loading='lazy' decoding='async'></div>"
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
        "<a class='btn btn-primary' href='/speaker.html'>🎤 講師紹介をもっと詳しく</a>"
        "<a class='btn btn-secondary' href='/profile.html'>📜 経歴をもっと詳しく</a>"
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


def _render_works_section() -> str:
    """制作実績セクション（TOP内サマリ）。portfolio.yaml から live のみを抜き、
    各カードは公開サイト本体へ直リンク。ページ遷移を減らすため一覧をインライン掲載。"""
    items = [p for p in _load_portfolio() if str(p.get("status") or "live") != "retired"]
    if not items:
        return ""
    parts = ["<div class='pf-grid'>"]
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
        parts.append(
            f"<a class='pf-card' href='{href}'{target}>"
            f"<div class='pf-title'>{name}</div>"
            + (f"<div class='pf-host'>{host}</div>" if host else "")
            + (f"<div class='pf-sum'>{summary}</div>" if summary else "")
            + (f"<div class='pf-meta'>{''.join(chips)}</div>" if chips else "")
            + "</a>"
        )
    parts.append("</div>")
    return "".join(parts)


def _render_lectures_section() -> str:
    """講習資料セクション。プログラミングマップを資料の1つとして配下に含める。"""
    pmap_card = {
        "title": "プログラミングマップ",
        "icon": "🗺️",
        "date": "2026-04-25",
        "summary": "プログラミング言語・用途・AI活用までの俯瞰図。何から学ぶか迷ったときの全体地図。",
        "href": "/programming-map.html",
    }
    lecs = [pmap_card] + list(_load_all_lectures())
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
    parts.append("<meta name='theme-color' content='#0A0F1C'>")
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

    # 1. 受講プラン（AI相談 / 講習会 / 伴走パック）— メインCTA
    parts.append("<section class='block' id='packages'>")
    parts.append("<p class='section-heading fade-up'>PACKAGES</p>")
    parts.append("<h2 class='section-title fade-up d1'>レベル別・AI受講プラン</h2>")
    parts.append("<p class='section-sub fade-up d2'>"
                 "<span class='lv-flow'><span class='lv-flow-step'>初級 まず実感</span><span class='lv-flow-arr'>→</span>"
                 "<span class='lv-flow-step'>中級 仕組み化</span><span class='lv-flow-arr'>→</span>"
                 "<span class='lv-flow-step'>上級 組織実装</span></span><br>"
                 "あなたの現在地から、次の一手を選べます。迷ったら上の30秒診断へ。</p>")
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
    parts.append("<p class='section-sub fade-up d2'>AI業務活用・SNSアルゴリズム・LLMO（AI検索最適化）の講習で使う資料。</p>")
    parts.append("<div class='fade-up d2'>")
    parts.append(_render_lectures_section())
    parts.append("</div>")
    parts.append("<div class='section-more fade-up d3'><a class='btn btn-secondary' href='/lectures/index.html'>📚 講習資料の一覧を見る →</a></div>")
    parts.append("</section>")

    # 5. お問い合わせ（Resend 送信フォーム）
    parts.append("<section class='block' id='contact'>")
    parts.append("<p class='section-heading fade-up'>CONTACT</p>")
    parts.append("<h2 class='section-title fade-up d1'>まずは 30 分、無料でご相談</h2>")
    parts.append("<p class='section-sub fade-up d2'>事業の状況・課題・予算感をヒアリングして、最適なアウトプット案をご提案します。メールまたはLINEから、お気軽にどうぞ。</p>")
    parts.append(_render_contact_form())
    parts.append("</section>")

    parts.append(f"<footer class='site-footer'>© {today[:4]} 由井辰美 / AIハブ — Web経営コンサル · 滋賀</footer>")
    parts.append("</div>")
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
    # プログラミングマップを講習資料カードとして先頭に常設
    pmap_card = {
        "title": "プログラミングマップ",
        "icon": "🗺️ ",
        "date": "2026-04-25",
        "summary": "プログラミング言語・用途・AI 活用までの俯瞰図。何から学ぶか迷ったときの全体地図。",
        "href": "/programming-map.html",
    }
    recent_lectures = [pmap_card] + list(recent_lectures)

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
