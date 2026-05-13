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


AGENTS_STATUS_JSON = ROOT / "outputs" / "agents_status.json"


def _load_agents_status() -> dict:
    if not AGENTS_STATUS_JSON.exists():
        return {}
    try:
        return json.loads(AGENTS_STATUS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


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
  --text: #f2f4fb;
  --muted: #aab1c5;
  --glass-bg: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.14);
  --glass-hover: rgba(255,255,255,0.10);
  --accent1: #7aa2ff;
  --accent2: #c77dff;
  --accent3: #ff7ab6;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
  background:
    radial-gradient(1200px 800px at 15% -10%, rgba(122,162,255,.35), transparent 60%),
    radial-gradient(900px 700px at 85% 10%, rgba(199,125,255,.28), transparent 60%),
    radial-gradient(1000px 800px at 50% 110%, rgba(255,122,182,.22), transparent 60%),
    linear-gradient(180deg, #0a0d1a 0%, #0d1126 50%, #0a0d1a 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
}

/* ---- layout ---- */
.container {
  position: relative;
  z-index: 1;
  max-width: 960px;
  margin: 0 auto;
  padding: 0 20px 80px;
}

/* ---- sticky nav (親 CLAUDE.md の position:sticky 教訓準拠) ---- */
/* body 直下の .container 内の先頭に置く。親が height 制限されると消えるため注意 */
html { scroll-padding-top: 72px; }
[id] { scroll-margin-top: 72px; }
nav.top-nav {
  position: sticky;
  top: 8px;
  z-index: 100;
  margin: 0 0 18px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: rgba(13,17,38,0.72);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
  box-shadow: 0 6px 20px rgba(0,0,0,.25);
}
nav.top-nav .nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text);
  text-decoration: none;
  font: inherit;
  font-size: 11.5px;
  font-weight: 600;
  line-height: 1.3;
  cursor: pointer;
  white-space: nowrap;
  transition: background .2s ease, transform .2s ease, border-color .2s ease;
}
nav.top-nav .nav-btn:hover {
  background: var(--glass-hover);
  border-color: rgba(122,162,255,.4);
  transform: translateY(-1px);
}
nav.top-nav .nav-current {
  background: linear-gradient(135deg, rgba(122,162,255,.55), rgba(199,125,255,.4));
  border-color: rgba(255,255,255,.32);
  color: #fff;
  font-weight: 800;
  box-shadow: 0 3px 10px rgba(122,162,255,.25), inset 0 1px 0 rgba(255,255,255,.12);
  cursor: default;
}
@media (max-width: 640px) {
  html { scroll-padding-top: 64px; }
  [id] { scroll-margin-top: 64px; }
  nav.top-nav { padding: 5px 8px; gap: 5px; top: 6px; }
  nav.top-nav .nav-btn { padding: 4px 9px; font-size: 11px; }
}

/* ---- hero ---- */
.hero {
  padding: 60px 0 48px;
  text-align: center;
}
.hero-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56px;
  background: linear-gradient(135deg, rgba(122,162,255,.25), rgba(199,125,255,.25));
  border: 2px solid var(--glass-border);
  box-shadow: 0 8px 32px rgba(0,0,0,.4), 0 0 60px rgba(122,162,255,.15);
}
.hero h1 {
  margin: 0 0 6px;
  font-size: clamp(28px, 5vw, 44px);
  font-weight: 800;
  background: linear-gradient(100deg, var(--accent1) 0%, var(--accent2) 45%, var(--accent3) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 2px 20px rgba(122,162,255,.25));
}
.hero .subtitle {
  font-size: 14px;
  color: var(--muted);
  letter-spacing: .04em;
  margin: 0 0 12px;
}
.hero .tagline {
  font-family: 'Noto Serif JP', serif;
  font-weight: 700;
  font-size: 18px;
  color: var(--accent, #4D7FFF);
  letter-spacing: .02em;
  margin: 0 0 24px;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 8px;
}
.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  border-radius: 999px;
  font: inherit;
  font-size: 13.5px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: transform .2s ease, box-shadow .2s ease;
}
.hero-btn.primary {
  background: linear-gradient(135deg, var(--accent1), var(--accent2));
  color: #0b1020;
  border: none;
  box-shadow: 0 6px 20px rgba(122,162,255,.35);
}
.hero-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(122,162,255,.45);
}
.hero-btn.secondary {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text);
}
.hero-btn.secondary:hover {
  background: var(--glass-hover);
  transform: translateY(-2px);
}

/* ---- section heading ---- */
.section-heading {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--accent1);
  margin: 48px 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-heading::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--glass-border);
}

/* ---- business card grid ---- */
.biz-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}
.biz-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px 16px;
  border-radius: 18px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  text-decoration: none;
  color: inherit;
  backdrop-filter: blur(18px) saturate(160%);
  box-shadow: 0 6px 24px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.07);
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
  position: relative;
  overflow: hidden;
}
.biz-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 18px;
  opacity: 0;
  transition: opacity .25s ease;
}
.biz-card:hover::before { opacity: 1; }
.biz-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(0,0,0,.35);
}
.biz-card.no-link {
  cursor: default;
  opacity: .65;
}
.biz-card.no-link:hover {
  transform: none;
  box-shadow: 0 6px 24px rgba(0,0,0,.22);
}
.biz-card.self-card {
  border-color: rgba(122,162,255,.45);
  background: rgba(122,162,255,.08);
}
.biz-card-icon {
  font-size: 28px;
  line-height: 1;
  margin-bottom: 2px;
}
.biz-card-name {
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.3;
}
.biz-card-tagline {
  font-size: 11.5px;
  color: var(--muted);
  letter-spacing: .02em;
}
.biz-card-desc {
  font-size: 12.5px;
  color: #c5cbdd;
  line-height: 1.6;
  flex: 1;
}
.biz-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}
.biz-badge {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .04em;
}
.biz-badge.live {
  background: rgba(100,220,160,.18);
  color: #7eeba3;
  border: 1px solid rgba(100,220,160,.3);
}
.biz-badge.coming-soon {
  background: rgba(255,210,80,.18);
  color: #fde68a;
  border: 1px solid rgba(255,210,80,.3);
}
.biz-badge.empty {
  background: rgba(150,150,160,.12);
  color: var(--muted);
  border: 1px solid rgba(150,150,160,.2);
}
.biz-badge.self {
  background: rgba(122,162,255,.25);
  color: var(--accent1);
  border: 1px solid rgba(122,162,255,.4);
}
.biz-arrow {
  font-size: 14px;
  color: var(--muted);
  transition: color .2s ease, transform .2s ease;
}
.biz-card:not(.no-link):hover .biz-arrow {
  color: var(--accent1);
  transform: translateX(3px);
}

/* ---- lecture preview cards ---- */
.lecture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}
.lecture-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  text-decoration: none;
  color: inherit;
  backdrop-filter: blur(14px);
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.lecture-card:hover {
  transform: translateY(-3px);
  border-color: rgba(122,162,255,.4);
  box-shadow: 0 10px 26px rgba(8,12,30,.45);
}
.lecture-title {
  font-size: 14px;
  font-weight: 700;
  background: linear-gradient(100deg, var(--accent1), var(--accent3));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  line-height: 1.4;
}
.lecture-date {
  font-size: 11px;
  color: var(--muted);
}
.lecture-summary {
  font-size: 12.5px;
  color: #d3d8ea;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.see-all {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--accent1);
  text-decoration: none;
  margin-top: 12px;
  transition: color .2s ease;
}
.see-all:hover { color: var(--accent3); }

/* ---- contact ---- */
.contact-block {
  margin-top: 48px;
  padding: 28px 32px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(122,162,255,.10), rgba(199,125,255,.08));
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(18px);
  text-align: center;
}
.contact-block h2 {
  font-size: 18px;
  font-weight: 800;
  margin: 0 0 8px;
  background: linear-gradient(100deg, var(--accent1), var(--accent2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.contact-block p {
  font-size: 13.5px;
  color: var(--muted);
  margin: 0 0 18px;
}
.contact-mail {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent1), var(--accent2));
  color: #0b1020;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 6px 20px rgba(122,162,255,.35);
  transition: transform .2s ease, box-shadow .2s ease;
}
.contact-mail:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(122,162,255,.45);
}

/* ---- watch link ---- */
.watch-link-bar {
  margin-top: 32px;
  padding: 14px 20px;
  border-radius: 14px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.watch-link-bar p {
  font-size: 13px;
  color: var(--muted);
  margin: 0;
}
.watch-link-bar a {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent1);
  text-decoration: none;
  white-space: nowrap;
}
.watch-link-bar a:hover { color: var(--accent3); }

/* ---- footer ---- */
footer {
  margin-top: 64px;
  padding-top: 20px;
  color: var(--muted);
  font-size: 11px;
  text-align: center;
  letter-spacing: .1em;
  text-transform: uppercase;
  opacity: .6;
}

@media (max-width: 640px) {
  .container { padding: 0 14px 60px; }
  .hero { padding: 40px 0 32px; }
  .biz-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .biz-card { padding: 14px 14px 12px; }
  .biz-card-desc { display: none; }
  .contact-block { padding: 22px 18px; }
}
@media (max-width: 400px) {
  .biz-grid { grid-template-columns: 1fr; }
}

/* === エージェントセクション === */
.agents-block {
  margin: 0 0 36px 0;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 14px;
}
@media (max-width: 820px) {
  .agents-block { grid-template-columns: 1fr; }
}
.ai-chat-cta {
  grid-column: 1 / -1;
  display: flex; align-items: center; justify-content: space-between; gap: 14px;
  padding: 16px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(122,162,255,.22), rgba(199,125,255,.18));
  border: 1px solid rgba(255,255,255,.18);
  backdrop-filter: blur(10px);
}
.ai-chat-cta__head { display:flex; align-items:center; gap:12px; }
.ai-chat-cta__icon { font-size: 28px; }
.ai-chat-cta__head strong { display:block; font-size: 14.5px; font-weight: 800; }
.ai-chat-cta__head small { display:block; color: var(--muted); font-size: 11.5px; margin-top:2px; }
.ai-chat-cta__btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 18px; border-radius: 999px;
  background: rgba(255,255,255,.16); color: var(--text);
  font-size: 12.5px; font-weight: 700; text-decoration: none;
  border: 1px solid rgba(255,255,255,.25);
  white-space: nowrap;
  transition: background .2s;
}
.ai-chat-cta__btn:hover { background: rgba(255,255,255,.28); }
@media (max-width: 560px) {
  .ai-chat-cta { flex-direction: column; align-items: stretch; }
  .ai-chat-cta__btn { justify-content: center; }
}

.agents-works, .agents-cma {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 14px;
  padding: 14px 16px;
}
.agents-works__title, .agents-cma__title {
  font-size: 11.5px; font-weight: 800; letter-spacing: .08em;
  color: var(--accent); margin-bottom: 8px; text-transform: uppercase;
}
.agents-works__list, .agents-cma__list {
  list-style: none; padding: 0; margin: 0;
}
.agents-works__list li { margin: 2px 0; }
.agents-works__list a {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; border-radius: 8px;
  color: var(--text); text-decoration: none; font-size: 12.5px;
}
.agents-works__list a:hover { background: rgba(122,162,255,.10); }
.aw-date { color: var(--muted); font-size: 11px; font-family: 'SFMono-Regular', monospace; flex: 0 0 auto; }
.aw-cat  { color: var(--accent); font-size: 10.5px; font-weight: 700; padding: 2px 7px; background: rgba(122,162,255,.14); border-radius: 999px; flex: 0 0 auto; }
.aw-title { flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.agents-cma__list li {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 0; font-size: 12px;
}
.ac-status { font-size: 12px; flex: 0 0 auto; }
.ac-name   { flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
.ac-date   { color: var(--muted); font-size: 10.5px; font-family: 'SFMono-Regular', monospace; flex: 0 0 auto; }

.agents-meta {
  grid-column: 1 / -1;
  color: var(--muted); font-size: 10.5px; text-align: right;
  margin: -4px 4px 0 0;
}
"""


def _render_nav() -> str:
    return (
        "<nav class='top-nav' aria-label='サイトナビ'>"
        "<span class='nav-btn nav-current'>🏠 ポータル</span>"
        "<a class='nav-btn' href='/lectures/index.html'>📝 講習資料</a>"
        "<a class='nav-btn' href='/speaker.html'>🎤 講師紹介</a>"
        "<a class='nav-btn' href='/profile.html'>📜 経歴</a>"
        "<a class='nav-btn' href='/portfolio.html'>🏆 実績</a>"
        "<a class='nav-btn' href='/watch/index.html'>📡 AI Watch</a>"
        "<a class='nav-btn' href='/admin'>🔐 管理</a>"
        "</nav>"
    )


def _render_hero() -> str:
    return (
        "<section class='hero' id='top'>"
        "<div class='hero-avatar'>🧗</div>"
        f"<h1>{html.escape(OWNER_NAME)}</h1>"
        f"<p class='subtitle'>{html.escape(OWNER_SUBTITLE)}</p>"
        f"<p class='tagline'>{html.escape(OWNER_TAGLINE)}</p>"
        "<div class='hero-actions'>"
        f"<a class='hero-btn primary' href='mailto:{html.escape(OWNER_EMAIL)}'>✉ お問い合わせ</a>"
        "<a class='hero-btn secondary' href='/speaker.html'>🎤 講師紹介を見る</a>"
        "</div>"
        "</section>"
    )


def _render_biz_card(biz: dict) -> str:
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

    inner = (
        f"<div class='biz-card-icon'>{icon}</div>"
        f"<div class='biz-card-name'>{name}</div>"
        f"<div class='biz-card-tagline'>{tagline}</div>"
        f"<div class='biz-card-desc'>{desc}</div>"
        f"<div class='biz-card-footer'>"
        f"{badge_html}"
        + (f"<span class='biz-arrow'>→</span>" if has_link else "")
        + "</div>"
    )

    style = (
        f"--card-border:{c_border};--card-glow:{c_glow};"
        "border-color:var(--card-border);"
    )
    hover_css = (
        f"border-color:{c_border};box-shadow:0 16px 40px rgba(0,0,0,.35),0 0 0 1px {c_border};"
    )

    if has_link:
        safe_url = html.escape(url, quote=True)
        return (
            f"<a class='biz-card{card_extra}' href='{safe_url}' target='_blank' rel='noopener' "
            f"style='{style}' "
            f"onmouseover=\"this.style.boxShadow='0 16px 40px rgba(0,0,0,.35),0 0 0 1px {c_border}'\" "
            f"onmouseout=\"this.style.boxShadow=''\">  "
            f"{inner}</a>"
        )
    return f"<div class='biz-card{card_extra}' style='{style}'>{inner}</div>"


def _render_lecture_card(lec: dict) -> str:
    slug = lec["slug"]
    title = html.escape(lec["title"])
    date = html.escape(lec["date"])
    summary = html.escape(lec["summary"])
    href = html.escape(f"/lectures/{slug}.html", quote=True)
    date_html = f"<div class='lecture-date'>📅 {date}</div>" if date else ""
    summary_html = f"<div class='lecture-summary'>{summary}</div>" if summary else ""
    return (
        f"<a class='lecture-card' href='{href}'>"
        f"<div class='lecture-title'>{title}</div>"
        f"{date_html}{summary_html}</a>"
    )


def _render_agents_section(status: dict) -> str:
    """エージェント運用状況の集約セクション。

    status が空または読めない場合は空文字を返してセクション自体を隠す（旧トップとの後方互換）。
    """
    if not status:
        return ""

    works = status.get("recent_works") or []
    cma = status.get("cma_apps") or []
    generated_at = status.get("generated_at") or ""

    parts: list[str] = []
    parts.append("<p class='section-heading'>エージェントの動き</p>")
    parts.append("<div class='agents-block'>")

    # AI チャット入口
    parts.append(
        "<div class='ai-chat-cta'>"
        "<div class='ai-chat-cta__head'>"
        "<span class='ai-chat-cta__icon'>🤖</span>"
        "<div>"
        "<strong>社内エージェントに質問する</strong>"
        "<small>9事業のドキュメントと最近の成果物を参照して答える AI チャット</small>"
        "</div>"
        "</div>"
        "<a class='ai-chat-cta__btn' href='/admin/chat'>チャットを開く →</a>"
        "</div>"
    )

    # 最近の成果物
    if works:
        parts.append("<div class='agents-works'>")
        parts.append("<div class='agents-works__title'>最近の成果物（consul/work）</div>")
        parts.append("<ul class='agents-works__list'>")
        for w in works[:8]:
            date = html.escape(w.get("date", ""))
            title = html.escape(w.get("title", "(untitled)"))
            cat = html.escape(w.get("category", ""))
            path = html.escape(w.get("path") or "/admin/docs", quote=True)
            parts.append(
                f"<li><a href='{path}'>"
                f"<span class='aw-date'>{date}</span>"
                f"<span class='aw-cat'>{cat}</span>"
                f"<span class='aw-title'>{title}</span>"
                f"</a></li>"
            )
        parts.append("</ul>")
        parts.append("</div>")

    # CMA 実行履歴
    if cma:
        parts.append("<div class='agents-cma'>")
        parts.append("<div class='agents-cma__title'>CMA（Managed Agents）実行履歴</div>")
        parts.append("<ul class='agents-cma__list'>")
        for c in cma[:7]:
            name = html.escape(c.get("name", ""))
            status_txt = html.escape(c.get("status", ""))
            last_run = html.escape(c.get("last_run", ""))
            parts.append(
                f"<li>"
                f"<span class='ac-status'>{status_txt}</span>"
                f"<span class='ac-name'>{name}</span>"
                f"<span class='ac-date'>{last_run}</span>"
                f"</li>"
            )
        parts.append("</ul>")
        parts.append("</div>")

    if generated_at:
        parts.append(f"<p class='agents-meta'>更新: {html.escape(generated_at)}</p>")

    parts.append("</div>")
    return "".join(parts)


def render_portal(businesses: list[dict], recent_lectures: list[dict], agents_status: dict | None = None) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    desc = f"{OWNER_NAME}（{OWNER_SUBTITLE}）のCEOポータル。9事業への入口・講習資料・AI情報を集約。"

    parts: list[str] = []
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>" + FAVICON_HEAD_HTML)
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append(f"<title>{html.escape(OWNER_NAME)} — CEOポータル | AIハブ</title>")
    parts.append(f"<meta name='description' content='{html.escape(desc, quote=True)}'>")
    parts.append(f"<link rel='canonical' href='{html.escape(SITE_URL + '/', quote=True)}'>")
    parts.append(_build_ogp(f"{OWNER_NAME} — CEOポータル", desc, SITE_URL + "/"))
    parts.append(f"<script type='application/ld+json'>{_build_jsonld_website()}</script>")
    parts.append(f"<style>{PORTAL_CSS}</style>")
    parts.append("</head><body>")
    parts.append("<div class='container'>")
    parts.append(ADMIN_BUTTON_HTML)

    parts.append(_render_nav())
    parts.append(_render_hero())

    parts.append(_render_agents_section(agents_status or {}))

    parts.append("<p class='section-heading'>事業ポートフォリオ</p>")
    parts.append("<div class='biz-grid'>")
    for biz in businesses:
        parts.append(_render_biz_card(biz))
    parts.append("</div>")

    if recent_lectures:
        parts.append("<p class='section-heading'>最新の講習資料</p>")
        parts.append("<div class='lecture-grid'>")
        for lec in recent_lectures:
            parts.append(_render_lecture_card(lec))
        parts.append("</div>")
        parts.append("<a class='see-all' href='/lectures/index.html'>すべての講習資料を見る →</a>")

    parts.append(
        "<div class='watch-link-bar'>"
        "<p>AI情報・SNSアルゴリズム動向の毎朝ダイジェスト（旧トップ）</p>"
        "<a href='/watch/index.html'>AI Watch を見る →</a>"
        "</div>"
    )

    parts.append(
        "<div class='contact-block'>"
        "<h2>お問い合わせ</h2>"
        "<p>講習・コンサル・事業連携のご相談はメールで</p>"
        f"<a class='contact-mail' href='mailto:{html.escape(OWNER_EMAIL)}'>"
        f"✉ {html.escape(OWNER_EMAIL)}</a>"
        "</div>"
    )

    parts.append(f"<footer>AIハブ / {today}</footer>")
    parts.append("</div></body></html>")
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
    agents_status = _load_agents_status()

    html_text = render_portal(businesses, recent_lectures, agents_status)

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
