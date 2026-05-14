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


PORTAL_CSS = """
:root {
  --bg-base: #f8fafc;
  --bg-white: #ffffff;
  --text: #0f172a;        /* slate-950 */
  --text-soft: #334155;   /* slate-700 */
  --muted: #64748b;       /* slate-500 */
  --line: #e2e8f0;        /* slate-200 */
  --primary: #2563eb;     /* blue-600 */
  --primary-soft: #3b82f6;/* blue-500 */
  --primary-bg: #eff6ff;  /* blue-50 */
  --emerald: #10b981;     /* emerald-500 */
  --amber: #f59e0b;
  --pink: #ec4899;
  --glass-bg: rgba(255,255,255,0.72);
  --glass-border: rgba(255,255,255,0.72);
  --shadow-card: 0 12px 40px rgba(15,23,42,0.08);
  --shadow-card-hover: 0 24px 60px rgba(15,23,42,0.14);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
  background:
    radial-gradient(900px 500px at 12% -6%, rgba(37,99,235,.10), transparent 60%),
    radial-gradient(700px 500px at 88% 8%, rgba(236,72,153,.07), transparent 60%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
}
::selection { background: var(--primary); color: #fff; }

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
  background: rgba(255,255,255,0.92);
  box-shadow: 0 1px 0 rgba(15,23,42,0.05), 0 10px 30px rgba(15,23,42,0.04);
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
.site-logo .dot { width: 8px; height: 8px; border-radius: 999px; background: var(--primary); display: inline-block; }
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
  background: rgba(255,255,255,0.96); border: 1px solid var(--line);
  border-radius: 16px; box-shadow: 0 18px 48px rgba(15,23,42,0.12);
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
  background: var(--text); color: #fff;
  font-size: 13px; font-weight: 700;
  text-decoration: none; transition: background .2s, transform .2s;
}
.site-nav .login-btn:hover { background: var(--primary); transform: translateY(-1px); }

.mobile-toggle {
  display: none; padding: 8px; border-radius: 999px;
  background: rgba(255,255,255,0.8); border: 1px solid var(--line);
  cursor: pointer;
}
.mobile-nav {
  display: none; padding: 16px 24px 24px;
  background: rgba(255,255,255,0.98); backdrop-filter: blur(18px);
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
  background: var(--text); color: #fff; text-align: center;
  font-size: 14px; font-weight: 700; text-decoration: none;
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
.hero-text { text-align: left; }
@media (max-width: 900px) { .hero { grid-template-columns: 1fr; gap: 28px; }
  .hero-text { text-align: center; }
}
.hero .eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 16px; border-radius: 999px;
  background: var(--primary-bg); color: var(--primary);
  font-size: 12px; font-weight: 700; letter-spacing: .04em;
  border: 1px solid rgba(37,99,235,.18);
}
.hero h1 {
  margin: 20px 0 16px; font-size: clamp(32px, 5.2vw, 60px);
  font-weight: 800; letter-spacing: -.025em; color: var(--text); line-height: 1.15;
}
.hero h1 .accent {
  background: linear-gradient(110deg, #2563eb 0%, #8b5cf6 50%, #ec4899 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  white-space: nowrap;
}
.hero h1 .underline {
  position: relative; white-space: nowrap;
}
.hero h1 .underline::after {
  content:''; position: absolute; left: 0; right: 0; bottom: -2px; height: 6px;
  background: linear-gradient(90deg, rgba(37,99,235,.18), rgba(236,72,153,.18));
  border-radius: 999px; z-index: -1;
}
.hero .lead {
  max-width: 520px; margin: 0 0 28px;
  font-size: clamp(15px, 1.6vw, 17px); color: var(--text-soft); line-height: 1.85;
}
@media (max-width: 900px) { .hero .lead { margin: 0 auto 28px; } }
.hero-actions {
  display: flex; flex-wrap: wrap; gap: 12px;
}
@media (max-width: 900px) { .hero-actions { justify-content: center; } }

/* hero visual (右側ビジュアル) */
.hero-visual {
  position: relative; aspect-ratio: 4/5; max-width: 460px; justify-self: end;
  border-radius: 28px; overflow: hidden; isolation: isolate;
  box-shadow: 0 30px 80px rgba(15,23,42,.18);
  transform: rotate(.5deg);
  transition: transform .6s cubic-bezier(.22,1,.36,1);
}
@media (max-width: 900px) { .hero-visual { justify-self: center; max-width: 380px; transform: rotate(0); } }
.hero-visual:hover { transform: rotate(0); }
.hero-visual img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 1.2s ease; }
.hero-visual:hover img { transform: scale(1.04); }
.hero-visual::after {
  content:''; position: absolute; inset: 0;
  background: linear-gradient(160deg, rgba(37,99,235,.05) 0%, rgba(236,72,153,.10) 100%);
  pointer-events: none;
}
.hero-blob {
  position: absolute; width: 260px; height: 260px; border-radius: 50%;
  filter: blur(60px); opacity: .55; z-index: -1; pointer-events: none;
}
.hero-blob.b1 { background: #3b82f6; top: -40px; right: -40px; }
.hero-blob.b2 { background: #ec4899; bottom: -40px; left: 30%; width: 200px; height: 200px; }

/* floating badge over hero image */
.hero-badge {
  position: absolute; padding: 10px 16px; border-radius: 16px;
  background: rgba(255,255,255,.96); backdrop-filter: blur(12px);
  border: 1px solid var(--line);
  box-shadow: 0 14px 36px rgba(15,23,42,.16);
  font-size: 12.5px; font-weight: 700; color: var(--text);
  display: inline-flex; align-items: center; gap: 8px;
  animation: float 5s ease-in-out infinite;
}
.hero-badge.b-top { top: 24px; left: -28px; }
.hero-badge.b-bot { bottom: 22px; right: -28px; animation-delay: -2.5s; }
.hero-badge .b-icon { font-size: 18px; }
@media (max-width: 900px) {
  .hero-badge.b-top { left: 8px; }
  .hero-badge.b-bot { right: 8px; }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 13px 28px; border-radius: 999px;
  font-size: 14.5px; font-weight: 700; text-decoration: none;
  transition: transform .2s, box-shadow .2s, background .2s;
  cursor: pointer; border: none;
}
.btn-primary { background: var(--primary); color: #fff; box-shadow: 0 8px 24px rgba(37,99,235,.30); }
.btn-primary:hover { background: #1d4fd6; transform: translateY(-2px); box-shadow: 0 12px 30px rgba(37,99,235,.40); }
.btn-secondary { background: #fff; color: var(--text); border: 1px solid var(--line); box-shadow: 0 4px 12px rgba(15,23,42,.05); }
.btn-secondary:hover { background: var(--bg-base); transform: translateY(-2px); }
.btn-ghost { background: transparent; color: var(--text-soft); padding: 9px 16px; }
.btn-ghost:hover { color: var(--primary); }

/* ---- stats strip ---- */
.stats-strip {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  margin: 24px 0 56px;
}
@media (max-width: 720px) { .stats-strip { grid-template-columns: repeat(2, 1fr); } }
.stat {
  text-align: center; padding: 22px 18px; border-radius: 18px;
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
}
.stat .num {
  font-size: clamp(26px, 3.4vw, 38px); font-weight: 800; color: var(--primary);
  line-height: 1.1; letter-spacing: -.02em;
}
.stat .label { font-size: 12.5px; color: var(--muted); margin-top: 6px; font-weight: 600; }

/* ---- section frame ---- */
section.block { padding: 56px 0; scroll-margin-top: 96px; }
section.block + section.block { border-top: 1px dashed var(--line); }
.section-title {
  font-size: clamp(22px, 3vw, 32px); font-weight: 800; letter-spacing: -.01em;
  color: var(--text); text-align: center; margin: 0 0 12px;
}
.section-sub {
  text-align: center; color: var(--muted);
  font-size: 13.5px; max-width: 640px; margin: 0 auto 36px;
}
.section-heading {
  font-size: 11px; font-weight: 800; letter-spacing: .14em;
  text-transform: uppercase; color: var(--primary);
  margin: 0 0 16px; text-align: center;
}

/* ---- services grid ---- */
.services-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
}
@media (max-width: 900px) { .services-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .services-grid { grid-template-columns: 1fr; } }
.service-card {
  position: relative; overflow: hidden;
  border-radius: 22px;
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  transition: transform .35s cubic-bezier(.22,1,.36,1), box-shadow .35s, border-color .25s;
  display: flex; flex-direction: column;
}
.service-card:hover { transform: translateY(-6px) rotate(-.3deg); box-shadow: var(--shadow-card-hover); border-color: rgba(37,99,235,.30); }
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
  width: 56px; height: 56px; border-radius: 16px;
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
  border-radius: 20px;
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
  background: radial-gradient(420px 160px at 0% 0%, var(--card-glow, rgba(37,99,235,.12)) 0%, transparent 60%);
  opacity: 0; transition: opacity .35s; pointer-events: none;
}
.biz-card:hover::before { opacity: 1; }
.biz-card:hover {
  transform: translateY(-6px) rotate(.3deg);
  border-color: var(--card-border, rgba(37,99,235,.45));
  box-shadow: var(--shadow-card-hover);
}
.biz-card.no-link { cursor: default; opacity: .65; }
.biz-card.no-link:hover { transform: none; box-shadow: var(--shadow-card); border-color: var(--line); }
.biz-card.self-card { border-color: rgba(37,99,235,.5); background: var(--primary-bg); }
.biz-card-icon { font-size: 28px; line-height: 1; margin-bottom: 2px; }
.biz-card-name { font-size: 16.5px; font-weight: 800; color: var(--text); line-height: 1.3; }
.biz-card-tagline { font-size: 12px; color: var(--muted); letter-spacing: .02em; font-weight: 600; }
.biz-card-desc { font-size: 13px; color: var(--text-soft); line-height: 1.65; flex: 1; }
.biz-card-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
.biz-badge {
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  font-size: 10.5px; font-weight: 700; letter-spacing: .04em;
}
.biz-badge.live { background: rgba(16,185,129,.12); color: #047857; border: 1px solid rgba(16,185,129,.25); }
.biz-badge.coming-soon { background: rgba(245,158,11,.15); color: #b45309; border: 1px solid rgba(245,158,11,.30); }
.biz-badge.empty { background: rgba(100,116,139,.10); color: var(--muted); border: 1px solid rgba(100,116,139,.20); }
.biz-badge.self { background: rgba(37,99,235,.15); color: var(--primary); border: 1px solid rgba(37,99,235,.35); }
.biz-arrow { font-size: 14px; color: var(--muted); transition: color .2s, transform .2s; }
.biz-card:not(.no-link):hover .biz-arrow { color: var(--primary); transform: translateX(3px); }

/* ---- gallery (事例ギャラリー) ---- */
.gallery-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
}
@media (max-width: 900px) { .gallery-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .gallery-grid { grid-template-columns: 1fr; } }
.gallery-item {
  position: relative; border-radius: 18px; overflow: hidden;
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
  display: inline-block; padding: 3px 10px; border-radius: 999px;
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

/* ---- flow steps ---- */
.flow-list {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  counter-reset: step;
}
@media (max-width: 900px) { .flow-list { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .flow-list { grid-template-columns: 1fr; } }
.flow-step {
  padding: 24px 22px; border-radius: 18px;
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  position: relative;
}
.flow-step::before {
  counter-increment: step;
  content: "0" counter(step);
  position: absolute; top: 14px; right: 18px;
  font-size: 26px; font-weight: 800; color: rgba(37,99,235,.18);
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
  padding: 20px; border-radius: 16px;
  background: var(--bg-white); border: 1px solid var(--line);
  text-decoration: none; color: inherit;
  box-shadow: var(--shadow-card);
  transition: transform .2s, border-color .2s, box-shadow .2s;
}
.lecture-card:hover { transform: translateY(-3px); border-color: rgba(37,99,235,.40); box-shadow: var(--shadow-card-hover); }
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

/* ---- profile section ---- */
.profile-block {
  display: grid; grid-template-columns: minmax(0, 1fr) 220px; gap: 32px;
  align-items: center;
  padding: 32px; border-radius: 24px;
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
}

/* ---- FAQ ---- */
.faq-list { max-width: 760px; margin: 0 auto; }
.faq-item {
  border: 1px solid var(--line); border-radius: 14px;
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
  padding: 48px 32px; border-radius: 24px;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
  color: #fff; text-align: center;
}
.contact-block h2 { font-size: clamp(22px, 3vw, 30px); font-weight: 800; margin: 0 0 10px; color: #fff; }
.contact-block p { font-size: 14px; opacity: .85; margin: 0 0 24px; }
.contact-mail {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 32px; border-radius: 999px;
  background: #fff; color: var(--primary);
  font-size: 14.5px; font-weight: 800; text-decoration: none;
  box-shadow: 0 8px 24px rgba(0,0,0,.18);
  transition: transform .2s, box-shadow .2s;
}
.contact-mail:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(0,0,0,.24); }

/* ---- watch link bar ---- */
.watch-link-bar {
  margin-top: 32px; padding: 16px 22px;
  border-radius: 16px;
  background: var(--bg-white); border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
}
.watch-link-bar p { font-size: 13px; color: var(--text-soft); margin: 0; }
.watch-link-bar a { font-size: 13px; font-weight: 700; color: var(--primary); text-decoration: none; white-space: nowrap; }
.watch-link-bar a:hover { text-decoration: underline; }

/* ---- footer ---- */
footer.site-footer {
  margin-top: 48px; padding: 32px 0 12px;
  color: var(--muted); font-size: 12px; text-align: center;
  border-top: 1px solid var(--line);
}
"""


def _render_header() -> str:
    """N デザイン風 fixed ヘッダー。スクロールで white/90 + blur に切替。"""
    return (
        "<header class='site-header' id='site-header'>"
        "<div class='site-header-inner'>"
        "<a class='site-logo' href='/'><span class='dot'></span>AIハブ <span style='color:var(--muted);font-weight:600;font-size:13px;margin-left:6px;'>by 由井辰美</span></a>"
        "<nav class='site-nav' aria-label='メインナビ'>"
        "<a class='nav-link' href='#services'>サービス</a>"
        "<a class='nav-link' href='#works'>実績</a>"
        "<a class='nav-link' href='#flow'>ご依頼の流れ</a>"
        "<a class='nav-link' href='#profile'>プロフィール</a>"
        "<a class='nav-link' href='#faq'>FAQ</a>"
        "<div class='menu-wrap'>"
        "<button class='menu-toggle' id='menu-toggle' aria-haspopup='menu' aria-expanded='false'>メニュー"
        "<svg class='chev' width='14' height='14' viewBox='0 0 20 20' fill='none' aria-hidden='true'><path d='M5 8l5 5 5-5' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        "</button>"
        "<div class='menu-drop' id='menu-drop' role='menu'>"
        "<a href='/lectures/index.html'>📝 講習資料</a>"
        "<a href='/watch/index.html'>📡 AI Watch（毎朝ダイジェスト）</a>"
        "<a href='/portfolio.html'>🏆 実績ページ</a>"
        "<a href='/speaker.html'>🎤 講師紹介</a>"
        "<a href='/profile.html'>📜 経歴</a>"
        "</div>"
        "</div>"
        "<a class='login-btn' href='/admin'>🔐 管理ログイン</a>"
        "</nav>"
        "<button class='mobile-toggle' id='mobile-toggle' aria-label='メニュー'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'><path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg>"
        "</button>"
        "</div>"
        "<div class='mobile-nav' id='mobile-nav'>"
        "<a href='#services'>サービス</a>"
        "<a href='#works'>実績</a>"
        "<a href='#flow'>ご依頼の流れ</a>"
        "<a href='#profile'>プロフィール</a>"
        "<a href='#faq'>FAQ</a>"
        "<a href='/lectures/index.html'>講習資料</a>"
        "<a href='/watch/index.html'>AI Watch</a>"
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
        "<span class='eyebrow'>🧗 滋賀 × 9事業オーナー Web経営コンサル</span>"
        "<h1>数字で語れる<br><span class='accent'>Webコンサル</span>を、<span class='underline'>滋賀</span>から。</h1>"
        "<p class='lead'>"
        "現役オーナーとして9事業を回し、Next.js / Supabase / Cloudflare で自社サイトを構築。"
        "「集客が止まった」「人がいない」「補助金を活かしたい」中小企業の経営課題を、"
        "Web と AI で具体的に動かします。"
        "</p>"
        "<div class='hero-actions'>"
        f"<a class='btn btn-primary' href='mailto:{html.escape(OWNER_EMAIL)}'>無料相談する →</a>"
        "<a class='btn btn-secondary' href='#works'>実績を見る</a>"
        "<a class='btn btn-ghost' href='/admin'>🔐 管理ログイン</a>"
        "</div>"
        "</div>"
        "<div class='hero-visual fade-up d2'>"
        f"<img src='{HERO_IMG}' alt='オーナーとチームが数字を見ながら戦略を立てている様子' loading='eager' fetchpriority='high' decoding='async'>"
        "<div class='hero-badge b-top'><span class='b-icon'>📈</span>毎月レビュー伴走</div>"
        "<div class='hero-badge b-bot'><span class='b-icon'>🚀</span>最短 2 週間で公開</div>"
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
        ("育成就労（2027 移行）支援はどんな内容？",
         "技能実習から育成就労への移行に必要な 30 項目チェックリストを動的ダッシュボード化し、法令確定状況を反映しながら社内体制を整える伴走型支援です。"),
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


def _render_profile() -> str:
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
        "<div class='profile-avatar'>🧗</div>"
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
    parts.append(_render_stats())

    # 事例ギャラリー（営業ヒット率を上げる視覚パンチ）
    parts.append("<section class='block' id='gallery'>")
    parts.append("<p class='section-heading fade-up'>WORK GALLERY</p>")
    parts.append("<h2 class='section-title fade-up d1'>つくれるもの・任せられること</h2>")
    parts.append("<p class='section-sub fade-up d2'>LP・EC・LINE Bot・社内 RAG。「企画 → 制作 → 運用」をぜんぶ自社で。</p>")
    parts.append(_render_gallery())
    parts.append("</section>")


    # サービス
    parts.append("<section class='block' id='services'>")
    parts.append("<p class='section-heading fade-up'>SERVICES</p>")
    parts.append("<h2 class='section-title fade-up d1'>提供できる 6 つのこと</h2>")
    parts.append("<p class='section-sub fade-up d2'>「コンサルだけする人」ではなく、9事業のオーナーとして毎日サイトと業務を回している実装者だからこそ提案できる内容です。</p>")
    parts.append(_render_services())
    parts.append("</section>")

    # 実績（事業ポートフォリオ + クライアント案件をまとめて表示）
    parts.append("<section class='block' id='works'>")
    parts.append("<p class='section-heading fade-up'>WORKS</p>")
    parts.append("<h2 class='section-title fade-up d1'>事業ポートフォリオ</h2>")
    parts.append("<p class='section-sub fade-up d2'>運営・制作・運用しているサイト。すべてを自分で構築・運用しています。</p>")
    parts.append("<div class='biz-grid'>")
    for i, biz in enumerate(businesses):
        # 各カードを fade-up + ディレイで段階的に出す
        parts.append(_render_biz_card(biz, fade_class=f"fade-up d{(i % 6) + 1}"))
    parts.append("</div>")
    parts.append("</section>")

    # ご依頼の流れ
    parts.append("<section class='block' id='flow'>")
    parts.append("<p class='section-heading'>FLOW</p>")
    parts.append("<h2 class='section-title'>ご依頼の流れ</h2>")
    parts.append("<p class='section-sub'>ご相談から公開・運用まで、最短 2 週間で動き始めます。</p>")
    parts.append(_render_flow())
    parts.append("</section>")

    # プロフィール
    parts.append("<section class='block' id='profile'>")
    parts.append("<p class='section-heading'>PROFILE</p>")
    parts.append("<h2 class='section-title'>プロフィール</h2>")
    parts.append(_render_profile())
    parts.append("</section>")

    # 最新の講習資料（あれば）
    if recent_lectures:
        parts.append("<section class='block' id='news'>")
        parts.append("<p class='section-heading'>NEWS</p>")
        parts.append("<h2 class='section-title'>最新の講習資料</h2>")
        parts.append("<div class='lecture-grid'>")
        for lec in recent_lectures:
            parts.append(_render_lecture_card(lec))
        parts.append("</div>")
        parts.append("<div style='text-align:center;'><a class='see-all' href='/lectures/index.html'>すべての講習資料を見る →</a></div>")
        parts.append("</section>")

    # FAQ
    parts.append("<section class='block' id='faq'>")
    parts.append("<p class='section-heading'>FAQ</p>")
    parts.append("<h2 class='section-title'>よくある質問</h2>")
    parts.append(_render_faq())
    parts.append("</section>")

    # AI Watch ハイライト
    parts.append(
        "<div class='watch-link-bar'>"
        "<p>📡 AI / SNS の毎朝ダイジェストを Watch ページで配信中</p>"
        "<a href='/watch/index.html'>AI Watch を見る →</a>"
        "</div>"
    )

    # お問い合わせ
    parts.append("<section class='block' id='contact'>")
    parts.append(
        "<div class='contact-block'>"
        "<h2>まずは 30 分、無料でご相談</h2>"
        "<p>事業の状況・課題・予算感をヒアリングして、最適なアウトプット案をご提案します。</p>"
        f"<a class='contact-mail' href='mailto:{html.escape(OWNER_EMAIL)}'>✉ {html.escape(OWNER_EMAIL)} に相談する</a>"
        "</div>"
    )
    parts.append("</section>")

    parts.append(f"<footer class='site-footer'>© {today[:4]} 由井辰美 / AIハブ — Web経営コンサル · 滋賀</footer>")
    parts.append("</div>")
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
