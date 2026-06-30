"""
outputs/top10.json を読み取り、静的 HTML サイトを生成する。
- ジャンルでグループ化
- 各グループ内に小タブ (全部 / 記事 / 動画) でメディア絞り込み
- 全カードにサムネイル
- クリックを localStorage + Gist へ送信（好み学習用）
"""
from __future__ import annotations
import html
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

SITE_URL = os.environ.get("AIHUB_SITE_URL", os.environ.get("AIWATCH_SITE_URL", "https://ai-hub-jp.vercel.app")).rstrip("/")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
TOP10_JSON = ROOT / "outputs" / "top10.json"
ARCHIVE_DIR = ROOT / "outputs" / "archive"
GENRES_YAML = ROOT / "config" / "genres.yaml"
SUPPORT_SNS_YAML = ROOT / "config" / "support_sns.yaml"
TOP_BUTTONS_YAML = ROOT / "config" / "top_buttons.yaml"
DIST = ROOT / "site" / "dist"
STATIC = ROOT / "site" / "static"

SNS_META = [
    ("youtube",         "🎥", "YouTube"),
    ("x",               "🐦", "X (Twitter)"),
    ("instagram_feed",  "📷", "Instagram Feed"),
    ("instagram_reel",  "🎬", "Instagram Reel"),
    ("instagram_story", "⭕", "Instagram Story"),
    ("threads",         "🧵", "Threads"),
    ("facebook",        "📘", "Facebook"),
]

URL_RE = re.compile(r"https?://\S+")


def clean_summary(s: str) -> str:
    s = URL_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip(" 　、。,")
    return s


def load_genres() -> list[dict]:
    if not GENRES_YAML.exists():
        return []
    data = yaml.safe_load(GENRES_YAML.read_text(encoding="utf-8"))
    return data.get("genres", [])


DEFAULT_TOP_BUTTONS = [
    {"id": "home",            "group": "メイン",       "label": "ホーム",             "icon": "🏠", "href": "index.html",            "kind": "link",   "enabled": True},
    {"id": "speaker",         "group": "講師",         "label": "講師紹介",           "icon": "🎤", "href": "speaker.html",          "kind": "link",   "enabled": True},
    {"id": "profile",         "group": "講師",         "label": "人物メモ",           "icon": "📜", "href": "speaker.html",          "kind": "link",   "enabled": False},
    {"id": "portfolio",       "group": "資料",         "label": "運営メモ",           "icon": "🧭", "href": "index.html#flow",       "kind": "link",   "enabled": False},
    {"id": "lectures",        "group": "教材資料",     "label": "受講資料",           "icon": "📝", "href": "lectures/index.html",   "kind": "link",   "enabled": True},
    # AIコーディング講習は lectures index の中にリンクとして掲載するためトップナビからは外す
    {"id": "archive",         "group": "アーカイブ",   "label": "過去ログ",           "icon": "📚", "href": "archive.html",          "kind": "link",   "enabled": True},
    {"id": "run",             "group": "操作",         "label": "巡回実行",           "icon": "🔄", "href": "",                      "kind": "action", "action_id": "run", "enabled": True},
]


def load_top_buttons() -> list[dict]:
    if not TOP_BUTTONS_YAML.exists():
        return DEFAULT_TOP_BUTTONS
    try:
        data = yaml.safe_load(TOP_BUTTONS_YAML.read_text(encoding="utf-8")) or {}
        items = data.get("top_buttons") or []
        if not items:
            return DEFAULT_TOP_BUTTONS
        return items
    except Exception:
        return DEFAULT_TOP_BUTTONS


def _resolve_nav_href(href: str, path_prefix: str) -> str:
    """ルート相対 href にページから見たプレフィックスを当てる。

    - 絶対パス (/admin) や URL (http...) はそのまま
    - 空 href は空のまま
    - その他は path_prefix を前置（path_prefix は "./" / "../" 想定）
    """
    if not href:
        return ""
    if href.startswith(("http://", "https://", "/", "#", "mailto:")):
        return href
    return f"{path_prefix.rstrip('/')}/{href}"


def render_top_nav(*, path_prefix: str = "./", current_id: str | None = None,
                   include_run: bool = True) -> str:
    """全ページ共通のトップナビを config/top_buttons.yaml から生成。

    path_prefix: 呼び出しページから見た dist ルートへのプレフィックス。
                 dist/ 直下のページは "./"、dist/lectures/* のような子ページは "../"。
    current_id:  現在ページの id。一致するボタンはハイライト表示し、リンクではなく強調表示にする。
    include_run: 巡回実行ボタンを出すかどうか（index トップだけ True、サブページは False）。
    """
    buttons = load_top_buttons()

    # group ごとに分配（出現順を保つ）
    grouped: list[tuple[str, list[dict]]] = []
    by_group: dict[str, list[dict]] = {}
    for b in buttons:
        if not b.get("enabled", True):
            continue
        if b.get("kind") == "action" and (b.get("action_id") or b.get("id")) == "run" and not include_run:
            continue
        g = str(b.get("group") or "その他")
        if g not in by_group:
            by_group[g] = []
            grouped.append((g, by_group[g]))
        by_group[g].append(b)

    # トップポータルの fixed ヘッダーと同じ構造にして全ページの UI を統一する。
    # ロゴ + 真ん中ナビ + 右側「管理ログイン」CTA の 3 ブロック。
    home_href = _resolve_nav_href("index.html", path_prefix)
    admin_href = "/admin"  # 常にルート相対
    safe_home = html.escape(home_href, quote=True) if home_href else "/"

    parts: list[str] = [
        "<header class='site-header scrolled' aria-label='サイトヘッダー'>"
        "<div class='site-header-inner'>"
        f"<a class='site-logo' href='{safe_home}'>"
        "<span class='brand-mark' aria-hidden='true'><span class='brand-a'>AI</span><span class='brand-ha'>相</span></span>"
        "<span class='wordmark'><span class='word-ai'>AI相談</span><span class='word-hub'>彦根</span><span class='word-en'>AI CONSULT</span></span>"
        "<span class='site-logo-by'>滋賀・彦根</span>"
        "</a>"
        "<nav class='site-nav top-nav' aria-label='サイトナビ'>"
    ]
    # TOP(_render_header) と同じく、固定メニューは主要導線だけにする。
    # 詳細な章移動は各ページ内の目次レールへ分離し、ヘッダーを1段に保つ。
    pmap_cls = " nav-current" if current_id == "pmap" else ""
    parts.append(f"<a class='nav-link nav-essential' href='{safe_home}'>ホーム</a>")
    parts.append("<a class='nav-link nav-essential' href='/#packages'>受講プラン</a>")
    parts.append("<a class='nav-link nav-essential' href='/#lectures'>資料</a>")
    parts.append("<a class='nav-link nav-essential' href='/#flow'>流れ</a>")
    parts.append(f"<a class='nav-link' href='{admin_href}' style='color:var(--muted);'>🔐 管理</a>")
    parts.append("</nav>")
    parts.append(
        "<a class='nav-cta' href='/#contact'>個別相談</a>"
        "</div>"
        "</header>"
    )
    parts.append(
        "<button class='mobile-toggle generated-mobile-toggle' id='mobile-toggle' aria-label='メニュー' aria-controls='mobile-nav' aria-expanded='false'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none' aria-hidden='true'><path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg>"
        "</button>"
        "<div class='mobile-nav generated-mobile-nav' id='mobile-nav'>"
        "<div class='mobile-nav-panel'>"
        "<div class='mobile-nav-primary'>"
        "<a class='login-btn-mobile' href='/#contact'>個別相談</a>"
        "<a class='mobile-main-link' href='/#packages'>受講プラン</a>"
        "</div>"
        "<span class='mobile-nav-label'>ホーム</span>"
        "<div class='mobile-link-grid'>"
        "<a href='/'>ホーム</a>"
        f"<a class='{'is-current' if current_id == 'pmap' else ''}' href='/programming-map.html'>AIコーディング</a>"
        "<a href='/#lectures'>資料</a>"
        "<a href='/#speaker'>講師紹介</a>"
        "<a href='/#faq'>FAQ</a>"
        "<a href='/blog/index.html'>ブログ</a>"
        "<a href='/watch/index.html'>AI Watch</a>"
        "<a class='mobile-admin-link' href='/admin'>管理画面</a>"
        "</div>"
        "</div>"
        "</div>"
        "<script>(function(){"
        "var b=document.getElementById('mobile-toggle'),n=document.getElementById('mobile-nav');"
        "if(!b||!n)return;"
        "function close(){n.classList.remove('open');b.setAttribute('aria-expanded','false');}"
        "b.addEventListener('click',function(e){e.stopPropagation();var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});"
        "n.querySelectorAll('a').forEach(function(a){a.addEventListener('click',close);});"
        "document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});"
        "})();</script>"
    )
    return "".join(parts)


def load_support_sns() -> dict:
    if not SUPPORT_SNS_YAML.exists():
        return {k: [] for k, _, _ in SNS_META}
    data = yaml.safe_load(SUPPORT_SNS_YAML.read_text(encoding="utf-8")) or {}
    sns = data.get("support_sns") or {}
    return {k: sns.get(k, []) or [] for k, _, _ in SNS_META}


SUPPORT_SNS_LATEST_JSON = ROOT / "outputs" / "support_sns" / "latest.json"


def _hash_str(s: str) -> str:
    import hashlib
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:16]


def load_support_sns_items() -> list[dict]:
    """outputs/support_sns/latest.json を読み、各アカウントの最新1件を Top10 と同じ形に整える。"""
    if not SUPPORT_SNS_LATEST_JSON.exists():
        return []
    try:
        data = json.loads(SUPPORT_SNS_LATEST_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []

    from urllib.parse import unquote
    result: list[dict] = []
    platforms = data.get("platforms", {})
    for plat_key, icon, label in SNS_META:
        entries = platforms.get(plat_key, [])
        for entry in entries:
            items = entry.get("items") or []
            if not items:
                continue
            latest = items[0]
            acc = entry.get("account", {})
            url = latest.get("url", "")
            title = latest.get("title", "") or f"{acc.get('name','')} - 最新"
            display_handle = unquote(acc.get("handle") or acc.get("name", ""))
            source_name = f"{icon} {display_handle}"
            result.append({
                "hash": _hash_str(f"sns:{plat_key}:{url}"),
                "title": title,
                "orig_title": title,
                "summary": f"{label}の最新投稿",
                "url": url,
                "source": source_name,
                "category": "サポートSNS",
                "genre": "support_sns",
                "score": 0,
                "thumbnail": latest.get("thumbnail", ""),
                "published": latest.get("published", ""),
            })
    return result


def render_support_sns_section(sns: dict) -> str:
    total = sum(len(sns.get(k, [])) for k, _, _ in SNS_META)
    if total == 0:
        return (
            "<section class='support-sns'>"
            "<h2>📡 サポートSNS</h2>"
            "<p class='empty'>まだ登録がありません。管理画面 (http://localhost:4001/) から追加できます。</p>"
            "</section>"
        )
    parts = ["<section class='support-sns'><h2>📡 サポートSNS</h2><div class='sns-grid'>"]
    for key, icon, label in SNS_META:
        items = sns.get(key, [])
        if not items:
            continue
        parts.append(
            f"<div class='sns-card'><div class='sns-head'>{icon} {label} "
            f"<span class='sns-count'>{len(items)}</span></div><ul class='sns-list'>"
        )
        for it in items:
            name = html.escape(it.get("name", ""))
            handle = html.escape(it.get("handle", ""))
            url = it.get("url", "")
            note = html.escape(it.get("note", ""))
            handle_html = f" <span class='sns-handle'>{handle}</span>" if handle else ""
            note_html = f"<div class='sns-note'>{note}</div>" if note else ""
            if url:
                safe_url = html.escape(url, quote=True)
                parts.append(
                    f"<li><a href='{safe_url}' target='_blank' rel='noopener'>{name}</a>"
                    f"{handle_html}{note_html}</li>"
                )
            else:
                parts.append(f"<li><span>{name}</span>{handle_html}{note_html}</li>")
        parts.append("</ul></div>")
    parts.append("</div></section>")
    return "".join(parts)


def is_video(item: dict) -> bool:
    url = item.get("url", "")
    return "youtube.com/watch" in url or "youtu.be/" in url


# 全ページ共通の favicon (HEAD に注入)
# SVGを正本にし、Apple/iPhone向けはPNGの apple-touch-icon を明示する
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

# top_buttons の中で `localhost_only: true` のリンクは
# サーバ生成HTMLでは display:none で出力 → 本スクリプトが localhost 系ホストのときだけ
# display を inline に戻す。本番 (GitHub Pages) では訪問者に一切見えない。
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


# スクロールで要素をふわっと出す共通 JS（HTML構造は変えず、対象セレクタへ
# .reveal を付与して IntersectionObserver で監視）。reduced-motion は即表示。
REVEAL_JS = """<script>
(function(){
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var sel = '.tr-card, .pf-card, .profile-stat, .profile-tech-card, .sns-card, article, .content-toc, .tr-section, .profile-tl-item, .profile-app-card, .profile-biz-card';
  var els = Array.prototype.slice.call(document.querySelectorAll(sel));
  if (!els.length || !('IntersectionObserver' in window)) return;
  els.forEach(function(el, i){ el.classList.add('reveal'); el.style.transitionDelay = Math.min(i * 40, 240) + 'ms'; });
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  els.forEach(function(el){ io.observe(el); });
})();
</script>"""

CSS = """
:root {
  --bg-base:#f8fafc;
  --bg-white:#ffffff;
  --text:#0f172a;
  --text-soft:#334155;
  --muted:#64748b;
  --line:#e2e8f0;
  --primary:#2563eb;
  --primary-soft:#3b82f6;
  --primary-bg:#eff6ff;
  --emerald:#10b981;
  --amber:#f59e0b;
  --pink:#ec4899;
  /* accent1/2/3 はトップ(PORTAL_CSS)に合わせ primary 系へ寄せる。
     既存セレクタの参照を壊さないよう変数自体は残し、値だけ単色トーンに統一。 */
  --accent1:#2563eb;
  --accent2:#2563eb;
  --accent3:#2563eb;
  --glass-bg:rgba(255,255,255,0.72);
  --glass-border:#e2e8f0;
  --glass-hover:rgba(255,255,255,0.92);
  --shadow-card: 0 12px 40px rgba(15,23,42,0.08);
  --shadow-card-hover: 0 24px 60px rgba(15,23,42,0.14);
}
* { box-sizing: border-box; }
html, body { margin:0; padding:0; }
html { scroll-behavior:smooth; }
body {
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans","Noto Sans JP",sans-serif;
  color:var(--text);
  line-height:1.7;
  min-height:100vh;
  background:
    radial-gradient(900px 500px at 12% -6%, rgba(45,203,161,.10), transparent 60%),
    radial-gradient(700px 500px at 88% 8%, rgba(45,203,161,.07), transparent 60%),
    linear-gradient(180deg, var(--bg-white) 0%, var(--bg-base) 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
}
::selection { background: var(--primary); color: #fff; }

/* glassmorphism helpers（コンテンツ系ページ・PORTAL_CSS と同質） */
.tr-card, .pf-card, .content-toc, .profile-stat, .profile-tech-card,
.sns-card, article {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(var(--glass-blur, 20px)) saturate(140%);
  -webkit-backdrop-filter: blur(var(--glass-blur, 20px)) saturate(140%);
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card), inset 0 1px 0 var(--glass-hi, transparent);
}
.reveal { opacity: 0; transform: translateY(18px); transition: opacity .7s cubic-bezier(.22,1,.36,1), transform .7s cubic-bezier(.22,1,.36,1); }
.reveal.is-in { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .reveal { opacity: 1 !important; transform: none !important; transition: none; } }
.container { position:relative; z-index:1; max-width: 1200px; margin: 0 auto; padding: 96px 24px 80px; }

header { margin-bottom:32px; }
header h1 {
  margin:0 0 8px;
  font-size:clamp(28px, 4.5vw, 42px);
  font-weight:800; letter-spacing:-.015em;
  color: var(--text);
}
header h1 .grad {
  color: var(--primary);
}
header .sub { margin:0; color:var(--muted); font-size:13px; letter-spacing:.04em; }

/* ---- 共通トップヘッダー（fixed・N デザイン風 white/blur）---- */
html { scroll-padding-top: 96px; }
[id] { scroll-margin-top: 96px; }
/* トップ(PORTAL_CSS)と同一定義。生成ページは <header class='site-header scrolled'>
   を静的付与しているため scrolled 側に実体スタイルを置けば JS 不要でトップと一致する。 */
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
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
}
.site-logo {
  font-size: 18px; font-weight: 800; letter-spacing: -.01em;
  color: var(--text); text-decoration: none;
  display: inline-flex; align-items: center; gap: 8px;
}
.site-logo .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--grad); box-shadow: 0 0 12px rgba(139,160,255,.6); display: inline-block; }
.brand-mark {
  width: 44px; height: 36px; border-radius: 8px;
  display: inline-flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #FFFFFF 0%, #E8F8F5 52%, #F2F9E8 100%);
  border: 1px solid rgba(15,143,114,.22);
  box-shadow: 0 10px 24px rgba(15,143,114,.13), inset 0 1px 0 rgba(255,255,255,.95);
  color: #0F172A; font-family: var(--mono, monospace); font-weight: 900; line-height: 1;
}
.brand-mark .brand-a { font-size: 14px; letter-spacing: 0; color: var(--primary); }
.brand-mark .brand-ha { font-size: 16px; margin-left: -2px; color: var(--emerald); transform: translateY(1px); }
.wordmark { display: inline-flex; align-items: baseline; gap: 3px; font-weight: 900; letter-spacing: 0; }
.wordmark .word-ai { font-family: var(--mono, monospace); color: var(--primary); letter-spacing: 0; }
.wordmark .word-hub { color: var(--text); font-weight: 900; }
.wordmark .word-en { margin-left: 8px; color: var(--muted); font-family: var(--mono, monospace); font-size: 11px; font-weight: 700; letter-spacing: .08em; }
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
.nav-cta {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 16px; border-radius: 8px;
  background: var(--grad); color: #fff; font-size: 13px; font-weight: 800; text-decoration: none;
  box-shadow: 0 6px 22px rgba(40,84,197,.22), inset 0 1px 0 rgba(255,255,255,.25);
  white-space: nowrap;
}
.site-header .login-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 18px; border-radius: 999px;
  background: var(--glass-bg); color: var(--text);
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  font-size: 13px; font-weight: 600; text-decoration: none;
  transition: border-color .2s, transform .2s, box-shadow .2s;
  white-space: nowrap;
}
.site-header .login-btn:hover { border-color: var(--line-strong); transform: translateY(-1px); box-shadow: 0 0 24px rgba(110,139,255,.22); }
@media (max-width: 720px) {
  .site-header-inner { padding: 10px 14px; gap: 8px; }
  .site-logo { font-size: 16px; }
  .wordmark .word-en, .site-logo-by { display: none; }
  .site-header .login-btn { padding: 7px 14px; font-size: 12px; }
}

/* ---- 共通トップナビ（ヘッダー内のリンク群） ---- */
nav.top-nav {
  flex: 1 1 auto;
  display:flex; flex-wrap:wrap; align-items:center;
  gap:6px;
  margin: 0;
  background: transparent;
  border:none;
  border-radius:0;
  box-shadow: none;
  justify-content:center;
}
nav.top-nav .nav-btn {
  display:inline-flex; align-items:center; gap:4px;
  padding:7px 14px; border-radius:999px;
  background:transparent; border:1px solid transparent;
  color:var(--text-soft); text-decoration:none;
  font:inherit; font-size:12.5px; font-weight:600; line-height:1.3;
  cursor:pointer; white-space:nowrap;
  transition: background .2s ease, color .2s ease, border-color .2s ease;
}
nav.top-nav .nav-btn:hover:not(:disabled) {
  background: var(--primary-bg);
  color: var(--primary);
  border-color: var(--glass-border);
}
nav.top-nav .nav-current {
  background: var(--grad);
  border-color: transparent;
  color:#fff; font-weight:700;
  box-shadow: 0 6px 22px rgba(110,139,255,.40), inset 0 1px 0 rgba(255,255,255,.22);
  cursor:default;
}
nav.top-nav .run-btn {
  background: var(--grad); color:#fff;
  border:1px solid transparent;
  font-weight:600; box-shadow: 0 6px 22px rgba(110,139,255,.40), inset 0 1px 0 rgba(255,255,255,.22);
}
nav.top-nav .run-btn:hover:not(:disabled) {
  filter: brightness(1.08); transform: translateY(-1px);
  box-shadow: 0 14px 44px rgba(139,160,255,.55), inset 0 1px 0 rgba(255,255,255,.30);
}
nav.top-nav .run-btn:disabled { opacity:.6; cursor:not-allowed; }
/* TOP(.site-nav) と同じく、狭幅ではヘッダー内リンク群を隠してロゴ+CTAだけ残す。
   下層ページはハンバーガーを持たないため、リンクは隠してヘッダー高を一定に保つ。 */
@media (max-width: 900px) {
  nav.top-nav { display: none; }
  .site-logo { white-space: nowrap; }
}
@media (max-width: 640px) {
  html { scroll-padding-top: 78px; }
  [id] { scroll-margin-top: 78px; }
}
.run-status { margin-left:10px; font-size:12px; color:var(--muted); }
.run-status.ok { color:#047857; }
.run-status.err { color:#b91c1c; }

/* ---- compact glass command header override for generated pages ---- */
html { scroll-padding-top: 78px; }
[id] { scroll-margin-top: 78px; }
header.site-header,
header.site-header.scrolled {
  min-height: 62px;
  background: linear-gradient(135deg, rgba(255,255,255,.92), rgba(247,252,253,.84));
  border-bottom: 1px solid rgba(7,20,38,.13);
  box-shadow: 0 10px 34px rgba(7,20,38,.08), inset 0 1px 0 rgba(255,255,255,.92);
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
}
.site-header-inner {
  min-height: 62px;
  padding: 8px 20px;
  gap: 12px;
}
.brand-mark {
  width: 40px;
  height: 34px;
}
nav.top-nav {
  flex-wrap: nowrap;
  justify-content: flex-end;
  gap: 6px;
}
nav.top-nav .nav-link {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  padding: 0 10px;
  border-radius: 8px;
  border: 1px solid transparent;
  color: #223148;
  text-decoration: none;
  font-size: 12.5px;
  font-weight: 850;
  white-space: nowrap;
}
nav.top-nav .nav-link:hover,
nav.top-nav .nav-link:focus-visible {
  color: #075e67;
  background: rgba(14,165,198,.10);
  border-color: rgba(14,165,198,.24);
  outline: none;
}
nav.top-nav .nav-current {
  color: #075e67;
  background: rgba(14,165,198,.12);
  border-color: rgba(14,165,198,.26);
  box-shadow: none;
}
.nav-cta {
  min-height: 38px;
  padding: 0 14px;
  background: linear-gradient(135deg, #F26655, #D99A20);
  box-shadow: 0 12px 28px rgba(242,102,85,.20), inset 0 1px 0 rgba(255,255,255,.28);
}
.mobile-toggle {
  display: none;
  width: 42px;
  height: 42px;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(18,32,51,.20);
  border-radius: 8px;
  background: #fff;
  color: #122033;
  box-shadow: 0 8px 18px rgba(18,32,51,.10);
  cursor: pointer;
}
.generated-mobile-toggle {
  position: fixed;
  top: 10px;
  right: max(14px, env(safe-area-inset-right));
  z-index: 72;
}
.mobile-toggle svg { display: block; }
.mobile-toggle svg path { stroke: currentColor; }
.mobile-nav {
  display: none;
  position: fixed;
  top: 62px;
  left: 0;
  right: 0;
  z-index: 70;
  max-height: calc(100dvh - 62px);
  padding: 12px max(16px, env(safe-area-inset-left)) calc(18px + env(safe-area-inset-bottom)) max(16px, env(safe-area-inset-right));
  overflow-y: auto;
  overscroll-behavior: contain;
  background: #fff;
  color: #122033;
  border-top: 1px solid rgba(18,32,51,.14);
  box-shadow: 0 18px 34px rgba(18,32,51,.14);
}
.mobile-nav.open { display: block; }
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 10px;
  border: 1px solid rgba(18,32,51,.12);
  border-radius: 8px;
  background: rgba(255,255,255,.94);
  color: #122033;
  text-align: center;
  text-decoration: none;
  line-height: 1.35;
  font-size: 13px;
  font-weight: 850;
}
.mobile-nav .login-btn-mobile {
  background: linear-gradient(135deg, #F26655, #D99A20);
  color: #fff;
  border-color: transparent;
}
.mobile-nav .mobile-main-link,
.mobile-nav a[href="/programming-map.html"] {
  background: rgba(14,165,198,.10);
  color: #075E67;
}
.mobile-nav .mobile-admin-link {
  grid-column: 1 / -1;
  background: rgba(7,20,38,.05);
}
.mobile-nav .mobile-nav-label {
  padding: 2px 2px 0;
  color: #5D6C80;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .14em;
  line-height: 1.2;
  text-transform: uppercase;
}
@media (max-width: 900px) {
  html { scroll-padding-top: 68px; }
  [id] { scroll-margin-top: 68px; }
  .site-header-inner {
    min-height: 60px;
    padding: 8px 14px;
  }
  nav.top-nav,
  .nav-cta {
    display: none;
  }
  .site-logo {
    max-width: calc(100% - 58px);
    overflow: hidden;
  }
  .mobile-toggle {
    display: inline-flex;
  }
  .mobile-nav {
    top: 60px;
    max-height: calc(100dvh - 60px);
  }
}
.run-status.running { color:#b45309; }

.genre-tabs {
  display:flex; flex-wrap:wrap; gap:8px;
  margin:24px 0 28px; padding:10px;
  background:var(--bg-white); border:1px solid var(--line);
  border-radius:16px;
  box-shadow: var(--shadow-card);
}
.genre-tab {
  font: inherit;
  padding:8px 14px; border-radius:999px;
  background:transparent; border:1px solid transparent;
  color:var(--muted); cursor:pointer; font-size:13px; font-weight:600;
  transition: all .2s ease;
  display:inline-flex; align-items:center; gap:6px;
}
.genre-tab:hover { color:var(--primary); background:var(--primary-bg); }
.genre-tab.active {
  background: var(--primary);
  color:#fff; border-color: var(--primary);
  box-shadow: 0 6px 16px rgba(37,99,235,.30);
}

.group { margin-top:36px; }
.group-head {
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:14px; padding:14px 20px;
  background: var(--primary-bg);
  border:1px solid rgba(37,99,235,.15);
  border-radius:16px;
  box-shadow: var(--shadow-card);
}
.group-label {
  font-size:17px; font-weight:800;
  color: var(--text);
}
.group-count {
  font-size:11px; color:var(--muted);
  padding:4px 10px; border-radius:999px;
  background:#fff; border:1px solid var(--line);
}

.sub-tabs {
  display:flex; gap:6px; margin:0 0 12px 4px;
}
.sub-tab {
  font: inherit;
  padding:4px 12px; border-radius:999px;
  background:transparent; border:1px solid var(--line);
  color:var(--muted); cursor:pointer; font-size:11px; font-weight:600;
  transition: all .2s ease;
}
.sub-tab:hover { color:var(--primary); background:var(--primary-bg); }
.sub-tab.active {
  background: var(--primary); color:#fff;
  border-color: var(--primary);
}

article {
  position:relative;
  display:flex; gap:16px;
  background:var(--bg-white); border:1px solid var(--line);
  border-radius:18px; padding:16px;
  margin-bottom:12px;
  box-shadow: var(--shadow-card);
  transition: transform .3s ease, box-shadow .3s ease, border-color .25s ease;
  cursor:pointer;
  text-decoration:none; color:inherit;
  overflow:hidden;
}
article:hover {
  transform: translateY(-4px);
  border-color: rgba(37,99,235,.30);
  box-shadow: var(--shadow-card-hover);
}
.thumb {
  flex-shrink:0;
  width:160px; height:100px;
  border-radius:12px;
  background:#f1f5f9 center/cover;
  border:1px solid var(--line);
  position:relative;
  overflow:hidden;
}
.thumb.placeholder {
  display:flex; align-items:center; justify-content:center;
  font-size:32px; opacity:.55;
  background: var(--primary-bg);
}
.thumb .play {
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-size:32px; color:#fff;
  text-shadow: 0 2px 12px rgba(0,0,0,.5);
}
.body {
  flex:1; min-width:0;
  display:flex; flex-direction:column; gap:6px;
}
.meta {
  display:flex; align-items:center; gap:8px;
  font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em;
}
.meta .rank {
  padding:2px 8px; border-radius:6px;
  background: var(--primary);
  color:#fff; font-weight:800;
}
.meta .score { opacity:.7; }
article h3 {
  margin:0; font-size:15.5px; font-weight:700;
  line-height:1.5; color:var(--text);
}
article p {
  margin:0; font-size:13px; color:var(--text-soft);
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
  overflow:hidden;
}
.src {
  font-size:10px; color:var(--muted);
  display:flex; align-items:center; gap:6px;
}

.empty {
  color:var(--muted); font-size:14px;
  padding:40px 20px; text-align:center;
  background:var(--bg-white); border:1px solid var(--line);
  border-radius:16px;
  box-shadow: var(--shadow-card);
}

footer {
  margin-top:64px; padding-top:24px;
  color:var(--muted); font-size:12px; text-align:center;
  border-top: 1px solid var(--line);
}

.support-sns { margin-top: 48px; }
.support-sns > h2 {
  font-size: 18px; font-weight: 800; margin-bottom: 14px;
  color: var(--text);
}
.support-sns .empty {
  color:var(--muted); font-size:13px;
  padding:20px; text-align:center;
  background:var(--bg-white); border:1px solid var(--line);
  border-radius:14px;
  box-shadow: var(--shadow-card);
}
.sns-grid {
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap:14px;
}
.sns-card {
  background:var(--bg-white); border:1px solid var(--line);
  border-radius:14px; padding:14px 16px;
  box-shadow: var(--shadow-card);
}
.sns-head {
  font-size:13px; font-weight:700; color:var(--text);
  margin-bottom:8px; display:flex; align-items:center; gap:8px;
}
.sns-count {
  font-size:10px; color:var(--muted);
  padding:2px 8px; border-radius:999px;
  background:#f1f5f9; border:1px solid var(--line);
}
.sns-list { list-style:none; margin:0; padding:0; }
.sns-list li {
  padding:6px 0; border-top:1px solid var(--line);
  font-size:12px; color:var(--text);
}
.sns-list li:first-child { border-top:none; }
.sns-list a { color:var(--primary); text-decoration:none; font-weight:600; }
.sns-list a:hover { text-decoration:underline; }
.sns-handle { color:var(--muted); font-size:11px; margin-left:4px; }
.sns-note { color:var(--muted); font-size:10px; margin-top:2px; }

/* ---- ボタン体系（トップ PORTAL_CSS から移植・同一定義） ---- */
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

@media (max-width: 640px) {
  .container { padding: 80px 14px 60px; }
  article { flex-direction:column; }
  .thumb { width:100%; height:180px; }
}
"""


def render_index(payload: dict, genres: list[dict], is_live: bool = True) -> str:
    date = payload.get("date", "")
    items = list(payload.get("items", []))

    sns_items = load_support_sns_items()
    items.extend(sns_items)
    total = len(items)

    for it in items:
        it["_is_video"] = is_video(it)
        it["_summary_clean"] = clean_summary(it.get("summary", "")) or ""

    genre_order = [g["key"] for g in genres] + ["support_sns"]
    genre_label = {g["key"]: f"{g.get('icon','')} {g['label']}" for g in genres}
    genre_label["support_sns"] = "📡 サポートSNS"

    genre_counts: dict[str, int] = {}
    for it in items:
        genre_counts[it["genre"]] = genre_counts.get(it["genre"], 0) + 1

    parts: list[str] = []
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>" + FAVICON_HEAD_HTML)
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append(f"<title>AI Watch Top{total} / {date} | AI相談</title>")
    desc = f"AI情報とSNSアルゴリズム動向を毎朝要約・ランキング。{date} のTop{total}を掲載。"
    parts.append(f"<meta name='description' content='{html.escape(desc, quote=True)}'>")
    parts.append(f"<link rel='canonical' href='{html.escape(SITE_URL + '/watch/index.html', quote=True)}'>")
    parts.append(_build_ogp("AI相談 AI Watch", desc, SITE_URL + "/watch/index.html", kind="website"))
    ld = _build_jsonld("website", {}, "AI相談 AI Watch", SITE_URL + "/watch/index.html")
    if ld:
        parts.append(f"<script type='application/ld+json'>{ld}</script>")
    parts.append(f"<style>{MASTER_CSS}</style></head><body><div class='container'>")
    parts.append(ADMIN_BUTTON_HTML)
    parts.append(render_top_nav(path_prefix="../", current_id="home" if is_live else "archive", include_run=is_live))
    parts.append("<header>")
    parts.append("<h1>AI相談</h1>")
    parts.append(f"<p class='sub'>{date} ・ 今日の注目Top{total} ・ クリックで好みを学習</p>")
    parts.append("</header>")

    if not items:
        parts.append("<p class='empty'>今日の記事はありません。</p>")
        parts.append(render_support_sns_section(load_support_sns()))
        parts.append("<footer>AI相談</footer></div></body></html>")
        return "".join(parts)

    parts.append("<div class='genre-tabs'>")
    parts.append(f"<button class='genre-tab active' data-genre='all'>🌐 すべて ({total})</button>")
    for key in genre_order:
        c = genre_counts.get(key, 0)
        if c == 0:
            continue
        parts.append(f"<button class='genre-tab' data-genre='{html.escape(key)}'>{html.escape(genre_label.get(key, key))} ({c})</button>")
    parts.append("</div>")

    rank_map = {it["hash"]: i + 1 for i, it in enumerate(items)}

    for key in genre_order:
        g_items = [it for it in items if it["genre"] == key]
        if not g_items:
            continue
        label = genre_label.get(key, key)
        has_article = any(not it["_is_video"] for it in g_items)
        has_video = any(it["_is_video"] for it in g_items)

        parts.append(f"<section class='group' data-genre='{html.escape(key)}'>")
        parts.append("<div class='group-head'>")
        parts.append(f"<span class='group-label'>{html.escape(label)}</span>")
        parts.append(f"<span class='group-count'>{len(g_items)}件</span>")
        parts.append("</div>")

        if has_article and has_video:
            parts.append("<div class='sub-tabs'>")
            parts.append("<button class='sub-tab active' data-sub='all'>すべて</button>")
            parts.append("<button class='sub-tab' data-sub='article'>📄 記事</button>")
            parts.append("<button class='sub-tab' data-sub='video'>📺 動画</button>")
            parts.append("</div>")

        for it in g_items:
            rank = rank_map[it["hash"]]
            sub_kind = "video" if it["_is_video"] else "article"
            title = html.escape(it["title"])
            summary = html.escape(it["_summary_clean"]) or "<span style='color:#777'>（要約なし）</span>"
            url = html.escape(it["url"])
            source = html.escape(it["source"])
            score = it.get("score", 0)
            thumb = html.escape(it.get("thumbnail", ""))
            hash_ = html.escape(it["hash"])
            genre_key = html.escape(it["genre"])

            if thumb:
                thumb_html = f"<div class='thumb' style='background-image:url(\"{thumb}\")'>" + ("<div class='play'>▶</div>" if it["_is_video"] else "") + "</div>"
            else:
                thumb_html = "<div class='thumb placeholder'>📄</div>" if not it["_is_video"] else "<div class='thumb placeholder'>📺</div>"

            parts.append(
                f"<article data-sub='{sub_kind}' data-hash='{hash_}' "
                f"data-genre='{genre_key}' data-source='{source}' "
                f"onclick=\"trackClick(this, '{url}')\">"
            )
            parts.append(thumb_html)
            parts.append("<div class='body'>")
            parts.append("<div class='meta'>")
            parts.append(f"<span class='rank'>#{rank}</span>")
            parts.append(f"<span class='score'>score {score:.0f}</span>")
            parts.append(f"<span>{source}</span>")
            parts.append("</div>")
            parts.append(f"<h3>{title}</h3>")
            parts.append(f"<p>{summary}</p>")
            parts.append("</div>")
            parts.append("</article>")

        parts.append("</section>")

    parts.append(render_support_sns_section(load_support_sns()))
    parts.append("<footer>AI相談 / Generated by Claude</footer>")
    parts.append("</div>")

    parts.append("""<script>
const LS_KEY = 'ai_intel_clicks_v1';
const GIST_ENDPOINT = window.AI_INTEL_GIST_ENDPOINT || '';

function loadClicks() {
  try { return JSON.parse(localStorage.getItem(LS_KEY)) || []; }
  catch(e) { return []; }
}
function saveClicks(arr) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(arr.slice(-500))); }
  catch(e) {}
}

function trackClick(el, url) {
  const rec = {
    hash: el.dataset.hash,
    genre: el.dataset.genre,
    source: el.dataset.source,
    ts: new Date().toISOString(),
  };
  const all = loadClicks();
  all.push(rec);
  saveClicks(all);

  if (GIST_ENDPOINT) {
    try {
      navigator.sendBeacon(GIST_ENDPOINT, JSON.stringify(rec));
    } catch(e) {}
  }
  window.open(url, '_blank', 'noopener');
}

(function(){
  const gtabs = document.querySelectorAll('.genre-tab');
  const groups = document.querySelectorAll('.group');
  gtabs.forEach(t => t.addEventListener('click', () => {
    gtabs.forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    const g = t.dataset.genre;
    groups.forEach(sec => {
      sec.style.display = (g === 'all' || sec.dataset.genre === g) ? '' : 'none';
    });
  }));

  document.querySelectorAll('.group').forEach(sec => {
    const subs = sec.querySelectorAll('.sub-tab');
    const cards = sec.querySelectorAll('article');
    subs.forEach(t => t.addEventListener('click', (e) => {
      e.stopPropagation();
      subs.forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      const s = t.dataset.sub;
      cards.forEach(c => {
        c.style.display = (s === 'all' || c.dataset.sub === s) ? '' : 'none';
      });
    }));
  });
})();

(function(){
  const btn = document.getElementById('run-btn');
  const status = document.getElementById('run-status');
  if (!btn) return;

  function setStatus(text, cls) {
    status.textContent = text;
    status.className = 'run-status' + (cls ? ' ' + cls : '');
  }

  async function poll() {
    try {
      const r = await fetch('/api/run/status');
      const s = await r.json();
      if (s.running) {
        setStatus('巡回中...', 'running');
        btn.disabled = true;
        setTimeout(poll, 3000);
      } else {
        btn.disabled = false;
        if (s.last_status === 'ok') {
          setStatus('完了 — 3秒後にリロード', 'ok');
          setTimeout(() => location.reload(), 3000);
        } else if (s.last_status === 'error') {
          setStatus('エラー（コンソール確認）', 'err');
          console.error(s.last_log);
        }
      }
    } catch(e) {
      setStatus('通信エラー（サーバー起動中？）', 'err');
      btn.disabled = false;
    }
  }

  btn.addEventListener('click', async () => {
    if (!confirm('巡回を開始しますか？（数分かかることがあります）')) return;
    btn.disabled = true;
    setStatus('開始中...', 'running');
    try {
      const r = await fetch('/api/run', { method: 'POST' });
      const j = await r.json();
      if (!j.ok) { setStatus(j.message || '開始失敗', 'err'); btn.disabled = false; return; }
      poll();
    } catch(e) {
      setStatus('通信エラー（FastAPI経由で開いていますか？）', 'err');
      btn.disabled = false;
    }
  });

  // 起動時に一度だけ状態確認（実行中ならポーリング再開）
  fetch('/api/run/status').then(r => r.json()).then(s => {
    if (s.running) { btn.disabled = true; setStatus('巡回中...', 'running'); poll(); }
  }).catch(() => {});
})();
</script>""")
    parts.append("</body></html>")
    return "".join(parts)


def render_archive(dates: list[str]) -> str:
    parts: list[str] = []
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>" + FAVICON_HEAD_HTML)
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append("<title>AI相談 — AI Watch 過去ログ</title>")
    parts.append(f"<style>{MASTER_CSS}</style></head><body><div class='container'>")
    parts.append(ADMIN_BUTTON_HTML)
    parts.append(render_top_nav(path_prefix="../", current_id="archive", include_run=False))
    parts.append("<header>")
    parts.append("<h1>過去ログ</h1>")
    parts.append(f"<p class='sub'>アーカイブ {len(dates)}件</p>")
    parts.append("</header>")
    if dates:
        parts.append("<ul style='list-style:none;padding:0;margin:0'>")
        for d in dates:
            parts.append(
                f"<li style='margin-bottom:10px;background:var(--glass-bg);"
                f"border:1px solid var(--glass-border);border-radius:14px;"
                f"backdrop-filter:blur(14px)'>"
                f"<a href='./{d}.html' style='display:block;padding:16px 20px;"
                f"color:var(--text);text-decoration:none'>{d}</a></li>"
            )
        parts.append("</ul>")
    else:
        parts.append("<p class='empty'>アーカイブはまだありません。</p>")
    parts.append("<footer>AI相談</footer></div></body></html>")
    return "".join(parts)


CONTENT_DIR = ROOT / "content"
SPEAKER_MD = CONTENT_DIR / "speaker.md"
LECTURES_DIR = CONTENT_DIR / "lectures"
PORTFOLIO_YAML = ROOT / "config" / "portfolio.yaml"
PROFILE_YAML = ROOT / "config" / "profile.yaml"
TEACHING_YAML = ROOT / "config" / "teaching_resources.yaml"
BLOG_DIR = ROOT / "content" / "blog"

CONTENT_CSS = """
.content-wrap {
  background: var(--bg-white);
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 32px clamp(20px, 4vw, 44px);
  box-shadow: var(--shadow-card);
  color: var(--text);
  line-height: 1.85;
}
.content-wrap h1,
.content-wrap h2,
.content-wrap h3 {
  color: var(--text);
  font-weight: 800;
  line-height: 1.35;
  margin: 1.6em 0 .5em;
}
.content-wrap h1 {
  font-size: clamp(24px, 4vw, 34px); letter-spacing: -.015em;
  color: var(--text);
}
.content-wrap h2 {
  font-size: 20px;
  padding: 10px 16px;
  border-radius: 14px;
  background: var(--primary-bg);
  border: 1px solid rgba(37,99,235,.15);
}
.content-wrap h3 { font-size: 15px; color: var(--primary); letter-spacing: .02em; }
.content-wrap p { margin: .6em 0; color: var(--text-soft); font-size: 14.5px; }
.content-wrap ul,
.content-wrap ol { margin: .4em 0 1em 1.3em; padding: 0; color: var(--text-soft); font-size: 14.5px; }
.content-wrap li { margin: .2em 0; }
.content-wrap a { color: var(--primary); text-decoration: none; border-bottom: 1px dashed rgba(37,99,235,.35); transition: color .2s; font-weight: 600; }
.content-wrap a:hover { color: var(--primary); border-bottom-color: rgba(37,99,235,.55); }
.content-wrap blockquote {
  margin: 1em 0;
  padding: 12px 18px;
  border-left: 4px solid var(--primary);
  background: #f8fafc;
  border-radius: 0 12px 12px 0;
  color: var(--text-soft);
  font-size: 13.5px;
}
.content-wrap code {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  background: var(--primary-bg);
  padding: 1px 6px;
  border-radius: 6px;
  font-size: .9em;
  color: var(--primary);
}
.content-wrap strong { color: var(--text); font-weight: 700; }
.content-wrap img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 16px;
  border: 1px solid var(--line);
  box-shadow: 0 16px 44px rgba(15,23,42,.10);
  margin: 22px 0;
}
.content-wrap figure {
  margin: 26px 0;
}
.content-wrap figure img {
  margin: 0;
}
.content-wrap figcaption {
  color: var(--muted);
  font-size: 12.5px;
  line-height: 1.7;
  margin-top: 8px;
}
.speaker-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  align-items: center;
  margin-bottom: 4px;
  font-size: 13px;
  color: var(--muted);
}
.speaker-meta .role {
  padding: 3px 12px;
  border-radius: 999px;
  background: var(--primary);
  color: #fff;
  font-weight: 700;
  font-size: 11.5px;
}
.content-toc {
  background: #f8fafc;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px 20px;
  margin: 0 0 22px;
}
.content-toc .toc-label {
  font-size: 12px;
  color: var(--primary);
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.content-toc ol {
  margin: 0;
  padding-left: 1.3em;
  columns: 2;
  column-gap: 28px;
  font-size: 13.5px;
}
.content-toc ol li { margin: 2px 0; break-inside: avoid; }
.content-toc a {
  color: var(--text-soft);
  text-decoration: none;
  border-bottom: 1px dashed transparent;
  font-weight: 600;
}
.content-toc a:hover { color: var(--primary); border-bottom-color: rgba(37,99,235,.40); }
@media (max-width: 640px) {
  .content-toc ol { columns: 1; }
}
.content-wrap h2[id],
.content-wrap h3[id] { scroll-margin-top: 20px; }
.back-to-top {
  position: fixed;
  right: 18px;
  bottom: 22px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-weight: 800;
  font-size: 20px;
  display: none;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(37,99,235,.30);
  cursor: pointer;
  border: none;
  z-index: 50;
}
.back-to-top.show { display: flex; }

/* ---- Portfolio ---- */
.pf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 8px;
}
.pf-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 14px 16px 12px;
  transition: transform .15s, border-color .15s, box-shadow .15s;
  text-decoration: none;
  color: inherit;
  min-height: 150px;
}
.pf-card:hover {
  transform: translateY(-2px);
  border-color: rgba(37,99,235,.40);
  box-shadow: var(--shadow-card-hover);
}
.pf-card .pf-title {
  font-weight: 800;
  font-size: 15px;
  color: var(--text);
}
.pf-card .pf-host {
  font-size: 11.5px;
  color: var(--muted);
  margin-top: 2px;
  word-break: break-all;
}
.pf-card .pf-sum {
  font-size: 13px;
  color: var(--text-soft);
  line-height: 1.55;
  margin: 8px 0 10px;
  flex: 1;
}
.pf-card .pf-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 11px;
}
.pf-card .pf-chip {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(37,99,235,.10);
  color: #1d4fd6;
  border: 1px solid rgba(37,99,235,.20);
}
.pf-card .pf-chip.cat {
  background: rgba(37,99,235,.10);
  color: #1d4fd6;
  border-color: rgba(37,99,235,.20);
}
.pf-card .pf-chip.retired { background: rgba(120,120,120,.2); color: var(--muted); }
.pf-card .pf-chip.dev { background: rgba(250,204,21,.15); color: #b45309; border-color: rgba(250,204,21,.35); }
.pf-section-title {
  font-size: 13px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--accent1);
  margin: 22px 0 4px;
  font-weight: 700;
}
.pf-note {
  font-size: 12px;
  color: var(--muted);
  margin-top: 18px;
  padding: 10px 14px;
  border-left: 3px solid var(--accent2);
  background: #f8fafc;
  border-radius: 0 10px 10px 0;
}

/* ---- Teaching resources directory (config/teaching_resources.yaml) ---- */
.tr-intro {
  font-size: 13.5px;
  color: var(--muted);
  margin: 4px 0 22px;
  padding: 10px 14px;
  border-left: 3px solid var(--accent2);
  background: #f8fafc;
  border-radius: 0 10px 10px 0;
}
.tr-section { margin: 22px 0 18px; }
.tr-section-head {
  display: flex; align-items: center; gap: 10px;
  margin: 0 0 4px;
  padding: 10px 16px !important;
}
.tr-section-icon { font-size: 20px; }
.tr-section-name { flex: 1; }
.tr-section-count {
  font-size: 11px; font-weight: 600;
  color: var(--muted);
  padding: 3px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  border: 1px solid var(--glass-border);
}
.tr-section-desc {
  margin: 6px 4px 12px !important;
  color: var(--muted);
  font-size: 12.5px !important;
}
.tr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}
.tr-card {
  display: flex; flex-direction: column; gap: 6px;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  text-decoration: none !important;
  color: inherit !important;
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
  border-bottom: 1px solid var(--glass-border) !important;
  min-height: 112px;
}
.tr-card:hover {
  transform: translateY(-3px);
  border-color: rgba(37,99,235,.40) !important;
  box-shadow: var(--shadow-card-hover);
}
.tr-card .tr-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.4;
}
.tr-card .tr-date {
  font-size: 11.5px;
  color: var(--muted);
  letter-spacing: .03em;
}
.tr-card .tr-sum {
  font-size: 13px;
  color: var(--text-soft);
  line-height: 1.6;
  flex: 1;
}
.tr-card .tr-meta {
  display: flex; gap: 6px; flex-wrap: wrap;
  margin-top: 4px;
}
.tr-chip {
  font-size: 10.5px; font-weight: 700;
  padding: 2px 9px; border-radius: 999px;
  letter-spacing: .04em;
}
.tr-chip.ext {
  background: rgba(37,99,235,.12);
  color: #1d4fd6;
  border: 1px solid rgba(37,99,235,.25);
}
.tr-home {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(260px, .65fr);
  gap: 20px;
  align-items: stretch;
  margin: 0 0 26px;
  padding: clamp(20px, 4vw, 32px);
  border: 1px solid rgba(37,99,235,.16);
  border-radius: 18px;
  background:
    radial-gradient(circle at 96% 12%, rgba(15,139,141,.13), transparent 30%),
    linear-gradient(135deg, #f8fbff 0%, #fff 48%, #f0fdf4 100%);
  box-shadow: 0 18px 50px rgba(15,23,42,.08);
}
.tr-home h2 {
  margin: 0 0 10px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  font-size: clamp(26px, 4vw, 42px);
  line-height: 1.2;
}
.tr-home p {
  margin: 0;
  color: var(--text-soft);
  font-size: 14.5px;
  line-height: 1.85;
}
.tr-home-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}
.tr-home-actions a {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 8px 13px;
  border-radius: 999px;
  border: 1px solid rgba(37,99,235,.24);
  background: #fff;
  color: var(--primary) !important;
  font-size: 12.5px;
  font-weight: 800;
  text-decoration: none !important;
}
.tr-home-panel {
  display: grid;
  gap: 10px;
}
.tr-home-stat {
  padding: 14px 15px;
  border-radius: 14px;
  background: rgba(255,255,255,.82);
  border: 1px solid var(--glass-border);
}
.tr-home-stat b {
  display: block;
  color: var(--text);
  font-size: 22px;
  line-height: 1.1;
}
.tr-home-stat span {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
}
.tr-format-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 18px 0 26px;
}
.tr-format {
  min-height: 92px;
  padding: 13px 14px;
  border-radius: 14px;
  border: 1px solid var(--glass-border);
  background: #fff;
}
.tr-format b {
  display: block;
  color: var(--text);
  font-size: 13.5px;
  line-height: 1.4;
}
.tr-format span {
  display: block;
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.55;
}
.tr-card .tr-meta {
  row-gap: 7px;
}
.tr-chip.format {
  background: #f8fafc;
  color: var(--text-soft);
  border: 1px solid var(--glass-border);
}
.tr-chip.format.on {
  background: rgba(37,99,235,.10);
  color: #1d4fd6;
  border-color: rgba(37,99,235,.20);
}
.tr-featured {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  margin: 0 0 22px;
  padding: 16px 18px;
  border-radius: 16px;
  border: 1px solid rgba(15,139,141,.22);
  background: linear-gradient(135deg, rgba(15,139,141,.08), rgba(37,99,235,.08));
  text-decoration: none !important;
  color: inherit !important;
}
.tr-featured b {
  display: block;
  color: var(--text);
  font-size: 16px;
  line-height: 1.45;
}
.tr-featured span {
  display: block;
  color: var(--muted);
  font-size: 12.5px;
  line-height: 1.65;
  margin-top: 3px;
}
.tr-featured .arrow {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #fff;
  color: var(--primary);
  border: 1px solid rgba(37,99,235,.2);
  font-weight: 900;
}
.lecture-shell {
  margin: 0 0 22px;
  padding: 18px;
  border: 1px solid rgba(37,99,235,.16);
  border-radius: 16px;
  background:
    radial-gradient(circle at 100% 0%, rgba(15,139,141,.10), transparent 28%),
    linear-gradient(135deg, #f8fbff 0%, #fff 55%, #f6fef9 100%);
}
.lecture-shell-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: start;
}
.lecture-shell-title {
  font-size: 18px;
  font-weight: 900;
  color: var(--text);
  line-height: 1.4;
}
.lecture-shell-desc {
  margin: 5px 0 0 !important;
  color: var(--text-soft) !important;
  font-size: 13.5px !important;
  line-height: 1.7 !important;
}
.lecture-shell-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}
.lecture-home-link {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 12px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid rgba(37,99,235,.22) !important;
  color: var(--primary) !important;
  font-size: 12px;
  font-weight: 800;
  text-decoration: none !important;
}
.lecture-format-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 14px;
}
.lecture-format-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 9px;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  background: #fff;
  color: var(--text-soft);
  font-size: 11.5px;
  font-weight: 800;
  line-height: 1.2;
}
.lecture-format-chip small {
  color: inherit;
  opacity: .72;
  font-size: 10px;
  font-weight: 800;
}
.lecture-format-chip.on {
  background: rgba(37,99,235,.10);
  border-color: rgba(37,99,235,.22);
  color: #1d4fd6;
}
.lecture-format-chip.missing {
  color: var(--muted);
  background: rgba(148,163,184,.10);
}
.lecture-jump {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}
.lecture-jump a {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 7px 11px;
  border-radius: 10px;
  border: 1px solid var(--glass-border) !important;
  background: rgba(255,255,255,.82);
  color: var(--text-soft) !important;
  font-size: 12px;
  font-weight: 800;
  text-decoration: none !important;
}
.lecture-jump a:hover {
  color: var(--primary) !important;
  border-color: rgba(37,99,235,.30) !important;
}
.lecture-outline-preview {
  margin: 14px 0 0;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255,255,255,.78);
  border: 1px solid var(--glass-border);
}
.lecture-outline-preview b {
  display: block;
  color: var(--text);
  font-size: 12.5px;
  margin-bottom: 6px;
}
.lecture-outline-preview ol {
  columns: 2;
  column-gap: 22px;
  margin: 0 0 0 1.2em !important;
  font-size: 12.5px !important;
}
.lecture-outline-preview li {
  break-inside: avoid;
}
.content-toc {
  scroll-margin-top: 92px;
}
@media (max-width: 760px) {
  .tr-home,
  .lecture-shell-head,
  .tr-featured {
    grid-template-columns: 1fr;
  }
  .tr-format-grid {
    grid-template-columns: 1fr;
  }
  .lecture-outline-preview ol {
    columns: 1;
  }
}

/* ---- Profile page (config/profile.yaml) ---- */
.profile-tagline {
  font-size: 15px;
  color: var(--muted);
  margin: -4px 0 22px;
  line-height: 1.6;
}
.profile-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin: 18px 0 28px;
}
.profile-stat {
  text-align: center;
  padding: 18px 12px;
  background: var(--bg-white);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow-card);
  transition: transform .2s ease, border-color .2s ease;
}
.profile-stat:hover {
  transform: translateY(-2px);
  border-color: rgba(37,99,235,.30);
}
.profile-stat .num {
  display: block;
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 4px;
}
.profile-stat .lbl {
  font-size: 12px;
  color: var(--muted);
  letter-spacing: .03em;
}

.profile-intro {
  font-size: 15px;
  line-height: 1.85;
  color: var(--text-soft);
  margin-bottom: 8px;
}

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
  background: #fff;
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  transition: border-color .2s ease, transform .2s ease;
}
.profile-tl-item:hover {
  border-color: rgba(37,99,235,.30);
  transform: translateX(2px);
}
.profile-tl-item::before {
  content: '';
  position: absolute;
  left: -36px;
  top: 22px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--primary);
  border: 3px solid #fff;
  box-shadow: 0 0 0 3px rgba(37,99,235,.20);
}
.profile-tl-year {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent1);
  letter-spacing: .03em;
  margin-bottom: 4px;
}
.profile-tl-role {
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 8px;
  line-height: 1.4;
}
.profile-tl-desc {
  font-size: 14px;
  color: var(--text-soft);
  line-height: 1.75;
  margin-bottom: 10px;
}
.profile-tl-desc strong { color: var(--primary); }
.profile-tl-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.profile-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(37,99,235,.12);
  border: 1px solid rgba(37,99,235,.25);
  color: #1d4fd6;
  font-size: 11.5px;
  font-weight: 600;
}

.profile-tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 16px 0 8px;
}
.profile-tech-card {
  padding: 18px 20px;
  background: #fff;
  border: 1px solid var(--glass-border);
  border-radius: 14px;
}
.profile-tech-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--glass-border);
}
.profile-tech-head .icon { font-size: 22px; }
.profile-tech-head .ttl {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
}
.profile-tech-head .period {
  font-size: 11px;
  color: var(--muted);
  margin-left: auto;
}
.profile-tech-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.profile-tech-list li {
  position: relative;
  padding: 6px 0 6px 16px;
  font-size: 13.5px;
  color: var(--text-soft);
  border-bottom: 1px dashed var(--line);
}
.profile-tech-list li:last-child { border-bottom: none; }
.profile-tech-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--accent1);
  font-weight: 700;
}

.profile-apps-grid,
.profile-biz-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin: 16px 0 8px;
}
.profile-app-card,
.profile-biz-card {
  display: flex;
  flex-direction: column;
  padding: 18px 20px;
  background: #fff;
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
  text-decoration: none;
  color: inherit;
}
.profile-app-card:hover,
.profile-biz-card:hover {
  transform: translateY(-3px);
  border-color: rgba(37,99,235,.40);
  box-shadow: var(--shadow-card-hover);
}
.profile-app-cat {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--primary);
  margin-bottom: 4px;
}
.profile-app-title,
.profile-biz-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 8px;
  line-height: 1.4;
}
.profile-biz-title { display: flex; align-items: center; gap: 8px; }
.profile-biz-title .ic { font-size: 22px; }
.profile-app-desc,
.profile-biz-desc {
  font-size: 13.5px;
  color: var(--text-soft);
  line-height: 1.65;
  margin-bottom: 12px;
  flex: 1;
}
.profile-app-go {
  align-self: flex-start;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--accent1);
  border-bottom: 1px dashed rgba(37,99,235,.40);
}
.profile-app-card:hover .profile-app-go { color: var(--primary); border-bottom-color: rgba(37,99,235,.6); }
.profile-biz-metrics {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12.5px;
  border-top: 1px solid var(--glass-border);
  padding-top: 10px;
}
.profile-biz-metrics .row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}
.profile-biz-metrics .lbl { color: var(--muted); }
.profile-biz-metrics .val { color: var(--text); font-weight: 700; }

.profile-source {
  margin-top: 24px;
  padding: 12px 16px;
  font-size: 12px;
  color: var(--muted);
  background: #f8fafc;
  border: 1px dashed var(--glass-border);
  border-radius: 12px;
}
.profile-source code { font-size: 11.5px; }

.profile-footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 16px 0 4px;
}
.profile-footer-links a {
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--glass-border);
  color: var(--text);
  text-decoration: none;
  transition: background .2s ease, border-color .2s ease;
}
.profile-footer-links a:hover {
  background: rgba(37,99,235,.12);
  border-color: rgba(37,99,235,.4);
}

@media (max-width: 640px) {
  .profile-stats { grid-template-columns: repeat(2, 1fr); }
  .profile-stat .num { font-size: 22px; }
  .profile-timeline { padding-left: 22px; }
  .profile-tl-item::before { left: -30px; }
}
"""


def _redirect_html(a, t):
    d = "https://ai-hub-jp.vercel.app/#" + a
    return ("<!doctype html><html lang='ja'><head><meta charset='utf-8'>"
        "<title>" + t + " | AI相談</title>"
        "<link rel='canonical' href='" + d + "'>"
        "<meta http-equiv='refresh' content='0; url=" + d + "'>"
        "<meta name='robots' content='noindex,follow'>"
        "<script>location.replace(" + repr(d) + ");</script>"
        "</head><body><p>このページは "
        "<a href='" + d + "'>トップの" + t + "</a> に統合されました。</p>"
        "</body></html>")


def _portal_css() -> str:
    """build_portal.py の PORTAL_CSS を唯一の正本として取り込む。
    取得失敗時は空文字（既存 CSS のみで従来動作にフォールバック）。"""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import build_portal  # noqa: WPS433
        return build_portal.PORTAL_CSS
    except Exception as e:
        print(f"[!] PORTAL_CSS 取り込み失敗（既存CSSで継続）: {e}")
        return ""


# 全ページ共通のマスタCSS。build_site 固有 CSS を土台に、PORTAL_CSS を
# 後置して後勝ちにすることで、共通セレクタ(body/.container/.site-header 等)を
# トップ(LP)と完全一致させる。watch/lectures 固有の .thumb/.genre-tabs 等は
# PORTAL に無いため前置の CSS 側で生き残る（破綻しない）。
MASTER_CSS = CSS + _portal_css()
MASTER_CONTENT_CSS = CSS + CONTENT_CSS + _portal_css()


def _load_markdown():
    import importlib
    return importlib.import_module("markdown")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}, text
    fm_raw = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    try:
        meta = yaml.safe_load(fm_raw) or {}
    except Exception:
        meta = {}
    return (meta if isinstance(meta, dict) else {}), body


_SECTION_HEADING_RE = re.compile(
    r"<h2(?P<h2_attrs>[^>]*)>(?P<h2_content>.*?)</h2>"
    r"|<div(?P<div_attrs>[^>]*(?:data-lecture-section|class=[\"'][^\"']*\bcc-h\b[^\"']*[\"'])[^>]*)>(?P<div_content>.*?)</div>",
    re.I | re.S,
)
_HTML_ID_ATTR_RE = re.compile(r"\sid=(['\"])(.*?)\1", re.I | re.S)
_SLUG_NON_ALNUM = re.compile(r"[^0-9A-Za-z぀-ヿ一-鿿\-]+")

LECTURE_FORMATS = [
    ("toc", "目次"),
    ("video", "動画"),
    ("narration", "ナレーション"),
    ("slides", "スライド"),
    ("pdf", "PDF"),
    ("check", "チェック"),
]


def _plain_text_from_html(markup: str) -> str:
    text = re.sub(r"<style[\s\S]*?</style>", " ", markup, flags=re.I)
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def _heading_match_parts(m: re.Match) -> tuple[str, str, str]:
    if m.group("h2_content") is not None:
        return "h2", m.group("h2_attrs") or "", m.group("h2_content") or ""
    return "div", m.group("div_attrs") or "", m.group("div_content") or ""


def _existing_html_id(attrs: str) -> str:
    match = _HTML_ID_ATTR_RE.search(attrs)
    return html.unescape(match.group(2).strip()) if match else ""


def _collect_h2_toc(body_html: str) -> list[tuple[str, str]]:
    toc: list[tuple[str, str]] = []
    for i, m in enumerate(_SECTION_HEADING_RE.finditer(body_html)):
        _tag, attrs, content = _heading_match_parts(m)
        text = _plain_text_from_html(content)
        if not text:
            continue
        slug = _existing_html_id(attrs) or f"h-{i + 1}"
        toc.append((slug, text))
    return toc


def _lecture_feature_flags(body_html: str, toc: list[tuple[str, str]]) -> dict[str, bool]:
    text = _plain_text_from_html(body_html)
    text_l = text.lower()
    markup_l = body_html.lower()
    return {
        "body": bool(text),
        "toc": len(toc) >= 3,
        "video": "<video" in markup_l or "youtube.com" in markup_l or "youtu.be" in markup_l,
        "narration": any(k in text for k in ("ナレーション", "台本", "収録用")),
        "slides": "codex-slide-deck" in markup_l or "/slides/" in markup_l or "スライド" in text,
        "pdf": ".pdf" in markup_l,
        "check": any(k in text for k in ("チェックリスト", "アップロード前チェック", "宿題", "進行メモ", "確認リスト")),
        "sources": any(k in text for k in ("公式確認", "出典", "参考リンク", "事実確認")),
    }


def _teaching_item_features(item: dict) -> dict[str, bool]:
    explicit = item.get("features")
    base = {"body": False, "sources": False}
    for key, _label in LECTURE_FORMATS:
        base[key] = False
    if isinstance(explicit, dict):
        flags = dict(base)
        for key in flags:
            flags[key] = bool(explicit.get(key, False))
        return flags
    href = str(item.get("href", ""))
    href_l = href.lower()
    text = " ".join(str(item.get(k, "")) for k in ("title", "summary", "href")).lower()
    inferred_body = bool(href_l and href_l.endswith(".html") and not href_l.startswith("slides/"))
    return {
        "body": inferred_body,
        "toc": bool(item.get("toc")),
        "video": any(k in text for k in ("動画", "video", ".webm", "youtube", "youtu.be")),
        "narration": any(k in text for k in ("ナレーション", "台本", "script")),
        "slides": any(k in text for k in ("スライド", "slides/", "slide", "marp")),
        "pdf": ".pdf" in text or "pdf" in text,
        "check": any(k in text for k in ("チェック", "宿題", "演習")),
        "sources": any(k in text for k in ("出典", "参考", "公式")),
    }


def _find_toc_anchor(toc: list[tuple[str, str]], *keywords: str) -> str:
    for slug, text in toc:
        if any(k in text for k in keywords):
            return f"#{slug}"
    return ""


def _render_feature_chips(flags: dict[str, bool], *, show_missing: bool = False, css_prefix: str = "lecture") -> str:
    parts: list[str] = []
    for key, label in LECTURE_FORMATS:
        active = bool(flags.get(key))
        if not active and not show_missing:
            continue
        if css_prefix == "lecture":
            cls = "lecture-format-chip on" if active else "lecture-format-chip missing"
            state = "あり" if active else "整備待ち"
            parts.append(f"<span class='{cls}'>{html.escape(label)}<small>{state}</small></span>")
        else:
            cls = "tr-chip format on" if active else "tr-chip format"
            parts.append(f"<span class='{cls}'>{html.escape(label)}</span>")
    return "".join(parts)


def _render_lecture_overview(title: str, meta: dict, body_html: str, toc: list[tuple[str, str]]) -> str:
    flags = _lecture_feature_flags(body_html, toc)
    desc = str(meta.get("summary") or "")
    parts: list[str] = []
    parts.append("<section class='lecture-shell' aria-label='この資料の入口'>")
    parts.append("<div class='lecture-shell-head'>")
    parts.append("<div>")
    parts.append("<div class='lecture-shell-title'>この資料の入口</div>")
    if desc:
        parts.append(f"<p class='lecture-shell-desc'>{html.escape(desc)}</p>")
    else:
        parts.append(f"<p class='lecture-shell-desc'>{html.escape(title)} の目次・本文・関連形式をまとめています。</p>")
    parts.append("</div>")
    parts.append("<div class='lecture-shell-actions'>")
    parts.append("<a class='lecture-home-link' href='../#packages'>受講プラン</a>")
    parts.append("<a class='lecture-home-link' href='./index.html'>受講資料ホーム</a>")
    parts.append("</div>")
    parts.append("</div>")
    parts.append("<div class='lecture-format-strip'>")
    parts.append("<span class='lecture-format-chip on'>本文<small>あり</small></span>")
    parts.append(_render_feature_chips(flags, show_missing=False, css_prefix="lecture"))
    parts.append("</div>")

    jumps: list[tuple[str, str]] = [("受講資料ホーム", "./index.html"), ("受講プラン", "../#packages")]
    if flags.get("toc"):
        jumps.append(("目次", "#lecture-toc"))
    video_anchor = _find_toc_anchor(toc, "動画", "動画版")
    if flags.get("video") and video_anchor:
        jumps.append(("動画へ", video_anchor))
    narration_anchor = _find_toc_anchor(toc, "ナレーション", "台本", "収録")
    if flags.get("narration") and narration_anchor:
        jumps.append(("台本へ", narration_anchor))
    slide_anchor = _find_toc_anchor(toc, "スライド", "スライド版", "第I部", "第II部")
    if flags.get("slides") and slide_anchor:
        jumps.append(("スライドへ", slide_anchor))
    check_anchor = _find_toc_anchor(toc, "チェック", "宿題", "進行メモ")
    if flags.get("check") and check_anchor:
        jumps.append(("確認へ", check_anchor))
    source_anchor = _find_toc_anchor(toc, "出典", "参考", "確認先", "アップデート")
    if flags.get("sources") and source_anchor:
        jumps.append(("出典へ", source_anchor))
    parts.append("<div class='lecture-jump'>")
    for label, href in jumps:
        parts.append(f"<a href='{html.escape(href, quote=True)}'>{html.escape(label)}</a>")
    parts.append("</div>")

    preview_toc = [(slug, text) for slug, text in toc if text != title][:6]
    if preview_toc:
        parts.append("<div class='lecture-outline-preview'><b>この資料の流れ</b><ol>")
        for _slug, text in preview_toc:
            parts.append(f"<li>{html.escape(text)}</li>")
        parts.append("</ol></div>")
    parts.append("</section>")
    return "".join(parts)


def _build_jsonld(kind: str, meta: dict, title: str, page_url: str) -> str:
    """BlogPosting / Person / WebSite の JSON-LD を生成。"""
    if kind == "lecture":
        doc = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "datePublished": str(meta.get("date") or datetime.now().strftime("%Y-%m-%d")),
            "mainEntityOfPage": { "@type": "WebPage", "@id": page_url },
            "author": { "@type": "Person", "name": "由井 辰美" },
            "publisher": {
                "@type": "Organization",
                "name": "AI相談",
                "url": SITE_URL,
            },
            "description": str(meta.get("summary") or title),
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": ["h1", ".content-wrap p:first-of-type"],
            },
        }
        return json.dumps(doc, ensure_ascii=False)
    if kind == "speaker":
        avatar_url = str(meta.get("avatar_url") or "/img/speaker.webp")
        avatar_image = avatar_url if avatar_url.startswith(("http://", "https://")) else SITE_URL + avatar_url
        doc = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": title,
            "jobTitle": str(meta.get("role") or "AI講師"),
            "url": page_url,
            "image": avatar_image,
            "sameAs": [str(meta.get("profile_url"))] if meta.get("profile_url") else [],
        }
        return json.dumps(doc, ensure_ascii=False)
    if kind == "website":
        doc = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "AI相談",
            "url": SITE_URL,
            "description": "AI情報とSNSアルゴリズム動向を毎朝要約して届ける静的サイト",
        }
        return json.dumps(doc, ensure_ascii=False)
    return ""


def _build_ogp(title: str, description: str, page_url: str, kind: str = "article") -> str:
    desc = description or title
    return "".join([
        f"<meta property='og:title' content='{html.escape(title, quote=True)}'>",
        f"<meta property='og:description' content='{html.escape(desc, quote=True)}'>",
        f"<meta property='og:url' content='{html.escape(page_url, quote=True)}'>",
        f"<meta property='og:type' content='{html.escape(kind, quote=True)}'>",
        "<meta property='og:site_name' content='AI相談'>",
        "<meta name='twitter:card' content='summary'>",
    ])


def _inject_heading_ids(body_html: str) -> tuple[str, list[tuple[str, str]]]:
    """講習で章見出しとして使う h2 / .cc-h に id を付与し、(id, text) のリストを返す。"""
    toc: list[tuple[str, str]] = []
    used: set[str] = set()

    def repl(m: re.Match) -> str:
        tag, attrs, content = _heading_match_parts(m)
        text = _plain_text_from_html(content)
        if not text:
            return m.group(0)
        existing_id = _existing_html_id(attrs)
        # slug 作成(日本語も通す)
        slug = existing_id or _SLUG_NON_ALNUM.sub("-", text).strip("-").lower()
        if not slug:
            slug = f"h-{len(toc) + 1}"
        base = slug
        i = 2
        while slug in used:
            slug = f"{base}-{i}"
            i += 1
        used.add(slug)
        toc.append((slug, text))
        if existing_id:
            return m.group(0)
        return f"<{tag}{attrs} id='{html.escape(slug, quote=True)}'>{content}</{tag}>"

    new_html = _SECTION_HEADING_RE.sub(repl, body_html)
    return new_html, toc


def render_content_page(title: str, meta: dict, body_html: str, nav_html: str, page_path: str = "", kind: str = "") -> str:
    body_html, toc = _inject_heading_ids(body_html)
    page_url = f"{SITE_URL}/{page_path.lstrip('/')}" if page_path else SITE_URL
    parts: list[str] = []
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>" + FAVICON_HEAD_HTML)
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append(f"<title>{html.escape(title)} | AI相談</title>")
    desc = str(meta.get("summary") or "")
    if desc:
        parts.append(f"<meta name='description' content='{html.escape(desc, quote=True)}'>")
    parts.append(f"<link rel='canonical' href='{html.escape(page_url, quote=True)}'>")
    parts.append(_build_ogp(title, desc, page_url, "article" if kind in ("lecture", "speaker", "blog") else "website"))
    if kind:
        jsonld_kind = "website" if kind == "portfolio" else kind
        ld = _build_jsonld(jsonld_kind, meta, title, page_url)
        if ld:
            parts.append(f"<script type='application/ld+json'>{ld}</script>")
    parts.append(f"<style>{MASTER_CONTENT_CSS}</style></head><body><div class='container'>")
    parts.append(ADMIN_BUTTON_HTML)
    parts.append(nav_html)
    parts.append("<header>")
    parts.append(f"<h1>{html.escape(title)}</h1>")
    sub_bits: list[str] = []
    if meta.get("role"):
        sub_bits.append(f"<span class='role'>{html.escape(str(meta['role']))}</span>")
    if meta.get("date"):
        sub_bits.append(f"<span>📅 {html.escape(str(meta['date']))}</span>")
    if meta.get("gen_by"):
        sub_bits.append(f"<span>{html.escape(str(meta['gen_by']))}</span>")
    if meta.get("profile_url"):
        url = html.escape(str(meta["profile_url"]), quote=True)
        sub_bits.append(f"<a href='{url}' target='_blank' rel='noopener'>プロフィール</a>")
    if sub_bits:
        parts.append("<div class='speaker-meta'>" + "".join(sub_bits) + "</div>")
    parts.append("</header>")
    parts.append("<div class='content-wrap'>")
    if kind == "lecture":
        parts.append(_render_lecture_overview(title, meta, body_html, toc))
    # TOC: h2 が 3 個以上あれば出す
    if len(toc) >= 3:
        toc_id = " id='lecture-toc'" if kind == "lecture" else ""
        parts.append(f"<div class='content-toc'{toc_id}><div class='toc-label'>🗂 目次</div><ol>")
        for slug, text in toc:
            parts.append(f"<li><a href='#{slug}'>{html.escape(text)}</a></li>")
        parts.append("</ol></div>")
    parts.append(body_html)
    parts.append("</div>")
    parts.append("<footer>AI相談 / Generated by Claude</footer>")
    parts.append("<button class='back-to-top' id='backTop' aria-label='トップへ戻る'>↑</button>")
    parts.append("<script>(function(){var b=document.getElementById('backTop');if(!b)return;window.addEventListener('scroll',function(){b.classList.toggle('show',window.scrollY>400);});b.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});})();</script>")
    parts.append(REVEAL_JS)
    parts.append("</div></body></html>")
    return "".join(parts)


def build_speaker_page() -> bool:
    if not SPEAKER_MD.exists():
        return False
    md = _load_markdown()
    raw = SPEAKER_MD.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)
    body_html = md.markdown(body, extensions=["extra", "sane_lists"])
    avatar_url = str(meta.get("avatar_url") or "").strip()
    if avatar_url:
        speaker_name = html.escape(str(meta.get("name") or "由井 辰美"))
        speaker_role = html.escape(str(meta.get("role") or "AI講師"))
        avatar = html.escape(avatar_url, quote=True)
        body_html = (
            "<div class='speaker-page-visual'>"
            "<div class='speaker-page-copy'>"
            f"<p class='speaker-page-role'>{speaker_role}</p>"
            "<p>講師本人の写真を、AI講習・制作・運用をまとめて扱うAI相談の顔として掲載しています。</p>"
            "</div>"
            "<div class='speaker-art speaker-art-animated'>"
            f"<img src='{avatar}' alt='{speaker_name} の講師写真' loading='eager' decoding='async'>"
            "</div>"
            "</div>"
        ) + body_html
    title = "講師紹介"
    nav = render_top_nav(path_prefix="./", current_id="speaker", include_run=False)
    html_text = render_content_page(title, meta, body_html, nav, page_path="speaker.html", kind="speaker")
    (DIST / "speaker.html").write_text(html_text, encoding="utf-8")
    return True


def _is_external_url(href: str) -> bool:
    return href.startswith(("http://", "https://", "//"))


def _resolve_lecture_href(href: str) -> str:
    """teaching_resources.yaml の href を lectures/index.html から見たパスに解決。

    - 絶対URL → そのまま
    - "./..." / "../..." → そのまま
    - "xxx.html"（ルート相対表記）→ "../xxx.html" として dist ルートへ戻す
    """
    if not href:
        return ""
    if _is_external_url(href) or href.startswith(("./", "../", "/")):
        return href
    return f"../{href}"


def _load_teaching_sections(lecture_md_items: list[dict]) -> list[dict]:
    """config/teaching_resources.yaml を読み、source: lectures-md は自動展開して返す。

    YAML が無ければ「受講資料」セクションだけを返す簡易フォールバック。
    """
    if TEACHING_YAML.exists():
        try:
            data = yaml.safe_load(TEACHING_YAML.read_text(encoding="utf-8")) or {}
            sections = data.get("sections") or []
            resolved: list[dict] = []
            for sec in sections:
                if sec.get("source") == "lectures-md":
                    sec_copy = {k: v for k, v in sec.items() if k != "source"}
                    # YAML 側に追加 items があれば結合（lectures-md + 手動アイテム）
                    extra_items = sec.get("items") or []
                    sec_copy["items"] = list(lecture_md_items) + extra_items
                    resolved.append(sec_copy)
                else:
                    resolved.append(sec)
            return resolved
        except Exception as e:
            print(f"[!] teaching_resources.yaml parse error: {e}")
    if lecture_md_items:
        return [{"name": "受講資料", "icon": "📝", "items": lecture_md_items}]
    return []


def _flatten_teaching_items(sections: list[dict]) -> list[dict]:
    items: list[dict] = []
    for sec in sections:
        for item in sec.get("items") or []:
            if isinstance(item, dict):
                items.append(item)
    return items


def _teaching_section_id(section: dict) -> str:
    sec_id = re.sub(r"[^a-zA-Z0-9一-鿿぀-ヿ]+", "-", str(section.get("name", ""))).strip("-").lower()
    return sec_id or "section"


def _render_teaching_home(sections: list[dict]) -> str:
    items = _flatten_teaching_items(sections)
    primary_items = [item for item in (sections[0].get("items") if sections else []) or [] if isinstance(item, dict)]
    feature_counts: dict[str, int] = {key: 0 for key, _label in LECTURE_FORMATS}
    for item in items:
        flags = _teaching_item_features(item)
        for key, _label in LECTURE_FORMATS:
            if flags.get(key):
                feature_counts[key] += 1

    featured = next((it for it in items if it.get("featured")), None)
    if not featured:
        featured = next((it for it in items if "Codex実践" in str(it.get("title", ""))), items[0] if items else {})
    featured_href = _resolve_lecture_href(str(featured.get("href", ""))) if featured else ""
    first_section_id = _teaching_section_id(sections[0]) if sections else ""
    parts: list[str] = []
    parts.append("<section class='tr-home' aria-label='受講資料ホーム'>")
    parts.append("<div>")
    parts.append("<h2>受講資料ホーム</h2>")
    parts.append(
        "<p>「Codex実践会 120分 構築と応用」の形式を基準に、各資料を目次、本文、動画、"
        "ナレーション、スライド、PDF、チェックの観点で探せるようにまとめた入口です。"
        "受講前は内容確認、受講中は投影資料、受講後は本文とチェック項目へ進めます。</p>"
    )
    parts.append("<div class='tr-home-actions'>")
    parts.append("<a href='../#packages'>受講プランを見る</a>")
    if featured_href:
        parts.append(f"<a href='{html.escape(featured_href, quote=True)}'>Codex実践会から見る</a>")
    if first_section_id:
        parts.append(f"<a href='#sec-{html.escape(first_section_id, quote=True)}'>全資料を見る</a>")
    parts.append("</div>")
    parts.append("</div>")
    parts.append("<div class='tr-home-panel'>")
    parts.append(f"<div class='tr-home-stat'><b>{len(primary_items)}</b><span>受講資料本体</span></div>")
    parts.append(f"<div class='tr-home-stat'><b>{max(len(items) - len(primary_items), 0)}</b><span>補助・投影資料</span></div>")
    parts.append(f"<div class='tr-home-stat'><b>{feature_counts.get('video', 0)}</b><span>動画付き</span></div>")
    parts.append("</div></section>")

    if featured:
        title = html.escape(str(featured.get("title", "")))
        summary = html.escape(str(featured.get("summary", "")))
        parts.append(f"<a class='tr-featured' href='{html.escape(featured_href, quote=True)}'>")
        parts.append("<div>")
        parts.append(f"<b>基準フォーマット: {title}</b>")
        if summary:
            parts.append(f"<span>{summary}</span>")
        parts.append("</div><span class='arrow'>→</span></a>")

    parts.append("<div class='tr-format-grid' aria-label='共通フォーマット'>")
    format_notes = [
        ("目次", "最初に流れを確認し、必要な章へ移動する。"),
        ("動画・ナレーション", "講師の説明順で見せる資料や収録台本を確認する。"),
        ("スライド式説明", "投影、画面共有、短時間説明に使う。"),
        ("本文", "復習、引用、手順確認のための読み物として使う。"),
        ("PDF・配布物", "印刷、配布、別ページ資料がある場合に使う。"),
        ("チェック", "宿題、運用確認、公開前レビューに使う。"),
    ]
    for label, note in format_notes:
        parts.append(f"<div class='tr-format'><b>{html.escape(label)}</b><span>{html.escape(note)}</span></div>")
    parts.append("</div>")
    return "".join(parts)


def _render_teaching_index(sections: list[dict]) -> str:
    """セクション付きのカード式ディレクトリを描画。"""
    parts: list[str] = []
    parts.append(_render_teaching_home(sections))
    parts.append(
        "<p class='tr-intro'>まず受講資料本体を開き、必要に応じて投影用スライドや補助資料へ進む。"
        "内容を確認したら受講プランへ戻り、準備会・実践会・個別相談のどれで進めるかを選べます。</p>"
    )
    rendered_any = False
    for sec in sections:
        items = sec.get("items") or []
        if not items:
            continue
        rendered_any = True
        name = html.escape(str(sec.get("name", "")))
        icon = html.escape(str(sec.get("icon", "")))
        desc = html.escape(str(sec.get("description", "")))
        sec_id = _teaching_section_id(sec)
        parts.append(f"<section class='tr-section' id='sec-{sec_id}'>")
        parts.append(
            f"<h2 class='tr-section-head'><span class='tr-section-icon'>{icon}</span>"
            f"<span class='tr-section-name'>{name}</span>"
            f"<span class='tr-section-count'>{len(items)} 件</span></h2>"
        )
        if desc:
            parts.append(f"<p class='tr-section-desc'>{desc}</p>")
        parts.append("<div class='tr-grid'>")
        for it in items:
            title = html.escape(str(it.get("title", "")))
            iicon = html.escape(str(it.get("icon", "")))
            href_raw = str(it.get("href", ""))
            summary = html.escape(str(it.get("summary", "")))
            date = html.escape(str(it.get("date", "")))
            ext = _is_external_url(href_raw)
            href = _resolve_lecture_href(href_raw)
            attrs = f" target='_blank' rel='noopener'" if ext else ""
            safe_href = html.escape(href, quote=True)
            chip = "<span class='tr-chip ext'>外部</span>" if ext else ""
            features = _teaching_item_features(it)
            parts.append(f"<a class='tr-card' href='{safe_href}'{attrs}>")
            parts.append(
                f"<div class='tr-title'>{(iicon + ' ') if iicon else ''}{title}</div>"
            )
            if date:
                parts.append(f"<div class='tr-date'>📅 {date}</div>")
            if summary:
                parts.append(f"<div class='tr-sum'>{summary}</div>")
            meta_bits = [chip] if chip else []
            if features.get("body"):
                meta_bits.append("<span class='tr-chip format on'>本文</span>")
            meta_bits.append(_render_feature_chips(features, show_missing=False, css_prefix="tr"))
            if meta_bits:
                parts.append(f"<div class='tr-meta'>{''.join(meta_bits)}</div>")
            parts.append("</a>")
        parts.append("</div></section>")
    if not rendered_any:
        parts.append("<p class='empty'>まだ資料が登録されていません。</p>")
    return "".join(parts)


def build_lectures() -> int:
    """content/lectures/*.md を個別ページに変換しつつ、
    config/teaching_resources.yaml を元にセクション付きインデックスを生成する。"""
    if not LECTURES_DIR.exists():
        return 0
    md = _load_markdown()
    out_dir = DIST / "lectures"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    lecture_md_items: list[dict] = []
    for f in sorted(LECTURES_DIR.glob("*.md"), reverse=True):
        raw = f.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)
        body_html = md.markdown(body, extensions=["extra", "sane_lists"])
        title = meta.get("title") or f.stem
        toc_for_item = _collect_h2_toc(body_html)
        features = _lecture_feature_flags(body_html, toc_for_item)
        nav = render_top_nav(path_prefix="../", current_id="lectures", include_run=False)
        (out_dir / f"{f.stem}.html").write_text(
            render_content_page(title, meta, body_html, nav, page_path=f"lectures/{f.stem}.html", kind="lecture"),
            encoding="utf-8",
        )
        lecture_md_items.append({
            "id": f.stem,
            "title": title,
            "icon": "📝",
            "href": f"./{f.stem}.html",
            "summary": str(meta.get("summary", "")),
            "date": str(meta.get("date", "")),
            "features": features,
            "featured": f.stem == "2026-06-codex-app-practice",
        })
        count += 1

    assets_src = LECTURES_DIR / "assets"
    assets_dst = out_dir / "assets"
    if assets_src.exists():
        assets_dst.mkdir(parents=True, exist_ok=True)
        for src in assets_src.rglob("*"):
            if src.is_dir():
                continue
            rel = src.relative_to(assets_src)
            dst = assets_dst / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    sections = _load_teaching_sections(lecture_md_items)
    if sections:
        body_html = _render_teaching_index(sections)
        nav = render_top_nav(path_prefix="../", current_id="lectures", include_run=False)
        (out_dir / "index.html").write_text(
            render_content_page("受講資料 ディレクトリ", {"summary": "AI相談の受講資料・補助教材・外部リソースのディレクトリ"}, body_html, nav, page_path="lectures/index.html"),
            encoding="utf-8",
        )
    return count


def build_blog() -> int:
    """Build public blog markdown pages from content/blog/*.md."""
    if not BLOG_DIR.exists():
        return 0
    md = _load_markdown()
    out_dir = DIST / "blog"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    items: list[dict] = []
    for f in sorted(BLOG_DIR.glob("*.md"), reverse=True):
        raw = f.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)
        body_html = md.markdown(body, extensions=["extra", "sane_lists", "attr_list"])
        title = str(meta.get("title") or f.stem)
        nav = render_top_nav(path_prefix="../", current_id="blog", include_run=False)
        (out_dir / f"{f.stem}.html").write_text(
            render_content_page(title, meta, body_html, nav, page_path=f"blog/{f.stem}.html", kind="blog"),
            encoding="utf-8",
        )
        items.append({
            "slug": f.stem,
            "title": title,
            "date": str(meta.get("date") or ""),
            "summary": str(meta.get("summary") or ""),
            "image": str(meta.get("image") or ""),
        })
        count += 1

    if items:
        parts = [
            "<div class='tr-section'>",
            "<p>AIハブのブログです。講習・制作・AI活用の現場から、実際に使える視点を残していきます。</p>",
            "<div class='tr-grid'>",
        ]
        for item in items:
            safe_href = html.escape(f"./{item['slug']}.html", quote=True)
            safe_title = html.escape(item["title"])
            safe_date = html.escape(item["date"])
            safe_summary = html.escape(item["summary"])
            parts.append(f"<a class='tr-card' href='{safe_href}'>")
            parts.append(f"<div class='tr-title'>{safe_title}</div>")
            if safe_date:
                parts.append(f"<div class='tr-date'>{safe_date}</div>")
            if safe_summary:
                parts.append(f"<div class='tr-sum'>{safe_summary}</div>")
            parts.append("</a>")
        parts.append("</div></div>")
        nav = render_top_nav(path_prefix="../", current_id="blog", include_run=False)
        (out_dir / "index.html").write_text(
            render_content_page(
                "ブログ",
                {"summary": "AIハブのブログ一覧。Codex、Claude Code、生成AI活用、AIコーディングの実践記録。"},
                "".join(parts),
                nav,
                page_path="blog/index.html",
                kind="blog",
            ),
            encoding="utf-8",
        )
    return count


_OGP_TITLE_RE = re.compile(r"<meta[^>]+property=['\"]og:title['\"][^>]+content=['\"]([^'\"]+)['\"]", re.I)
_OGP_DESC_RE = re.compile(r"<meta[^>]+property=['\"]og:description['\"][^>]+content=['\"]([^'\"]+)['\"]", re.I)
_TITLE_RE = re.compile(r"<title[^>]*>([^<]+)</title>", re.I)
_DESC_RE = re.compile(r"<meta[^>]+name=['\"]description['\"][^>]+content=['\"]([^'\"]+)['\"]", re.I)


def _fetch_meta(url: str, timeout: float = 3.0) -> dict:
    """URL から og:title/og:description/<title>/meta[description] を拾う。失敗時は空 dict。"""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 ai-hub-portfolio-bot/1.0",
            "Accept": "text/html,application/xhtml+xml",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(200_000)  # 先頭 200KB で十分
            charset = resp.headers.get_content_charset() or "utf-8"
        try:
            text = raw.decode(charset, errors="replace")
        except LookupError:
            text = raw.decode("utf-8", errors="replace")
        meta = {}
        m = _OGP_TITLE_RE.search(text)
        if m: meta["title"] = m.group(1).strip()
        m = _OGP_DESC_RE.search(text)
        if m: meta["desc"] = m.group(1).strip()
        if "title" not in meta:
            m = _TITLE_RE.search(text)
            if m: meta["title"] = m.group(1).strip()
        if "desc" not in meta:
            m = _DESC_RE.search(text)
            if m: meta["desc"] = m.group(1).strip()
        return meta
    except Exception:
        return {}


def _host_of(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).hostname or url
    except Exception:
        return url


def build_portfolio_page() -> bool:
    """Retired public portfolio route. Delete stale output if it exists."""
    target = DIST / "portfolio.html"
    if target.exists():
        target.unlink()
    return False


_INLINE_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def _inline_md(text: str) -> str:
    """** で囲まれた強調だけを <strong> に変換（HTML エスケープ後）。改行は <br> に。"""
    escaped = html.escape(text.strip())
    escaped = _INLINE_BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    return escaped.replace("\n", "<br>")


def _build_profile_body() -> str:
    """Builds the retired internal profile fragment. Public callers no longer use it."""
    return ""
    if not PROFILE_YAML.exists():
        return ""
    try:
        data = yaml.safe_load(PROFILE_YAML.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"[!] profile.yaml load error: {e}")
        return ""

    meta = data.get("meta") or {}
    title = str(meta.get("title") or "由井 辰美")
    subtitle = str(meta.get("subtitle") or "")
    tagline = str(meta.get("tagline") or "")
    description = str(meta.get("description") or "")
    source_url = str(meta.get("source_url") or "")
    gen_by = str(meta.get("gen_by") or "")

    parts: list[str] = []

    # サブタイトル＋タグライン（h1 直下）
    if subtitle or tagline:
        parts.append("<p class='profile-tagline'>")
        if subtitle:
            parts.append(html.escape(subtitle))
        if subtitle and tagline:
            parts.append("<br>")
        if tagline:
            parts.append(f"<span style='color:var(--muted);font-size:13px'>{html.escape(tagline)}</span>")
        parts.append("</p>")

    # Retired metric block.
    stats = data.get("stats") or []
    if stats:
        parts.append("<h2 id='stats'>Profile metrics</h2>")
        parts.append("<div class='profile-stats'>")
        for st in stats:
            num = html.escape(str(st.get("number", "")))
            lbl = html.escape(str(st.get("label", "")))
            parts.append(
                f"<div class='profile-stat'><span class='num'>{num}</span><span class='lbl'>{lbl}</span></div>"
            )
        parts.append("</div>")

    # プロフィール概要
    intro = data.get("intro")
    if intro:
        parts.append("<h2 id='profile'>👤 プロフィール</h2>")
        parts.append(f"<p class='profile-intro'>{_inline_md(str(intro))}</p>")

    # キャリアタイムライン
    timeline = data.get("timeline") or []
    if timeline:
        parts.append("<h2 id='timeline'>🗓 キャリアタイムライン</h2>")
        parts.append("<div class='profile-timeline'>")
        for item in timeline:
            year = html.escape(str(item.get("year", "")))
            role = html.escape(str(item.get("role", "")))
            desc = _inline_md(str(item.get("description", "")))
            metrics = item.get("metrics") or []
            parts.append("<div class='profile-tl-item'>")
            if year:
                parts.append(f"<div class='profile-tl-year'>{year}</div>")
            if role:
                parts.append(f"<div class='profile-tl-role'>{role}</div>")
            if desc:
                parts.append(f"<div class='profile-tl-desc'>{desc}</div>")
            if metrics:
                parts.append("<div class='profile-tl-metrics'>")
                for m in metrics:
                    parts.append(f"<span class='profile-badge'>{html.escape(str(m))}</span>")
                parts.append("</div>")
            parts.append("</div>")
        parts.append("</div>")

    # 技術スタックの進化
    tech = data.get("tech_evolution") or []
    if tech:
        parts.append("<h2 id='tech'>⚙️ 技術スタックの進化</h2>")
        parts.append("<div class='profile-tech-grid'>")
        for t in tech:
            icon = html.escape(str(t.get("icon", "")))
            ttl = html.escape(str(t.get("title", "")))
            period = html.escape(str(t.get("period", "")))
            items = t.get("items") or []
            parts.append("<div class='profile-tech-card'>")
            parts.append(
                f"<div class='profile-tech-head'><span class='icon'>{icon}</span>"
                f"<span class='ttl'>{ttl}</span><span class='period'>{period}</span></div>"
            )
            parts.append("<ul class='profile-tech-list'>")
            for it in items:
                parts.append(f"<li>{html.escape(str(it))}</li>")
            parts.append("</ul></div>")
        parts.append("</div>")

    # 実用アプリケーション
    apps = data.get("apps") or []
    if apps:
        parts.append("<h2 id='apps'>🚀 実用アプリケーション</h2>")
        parts.append("<div class='profile-apps-grid'>")
        for a in apps:
            url = html.escape(str(a.get("url", "")), quote=True)
            ttl = html.escape(str(a.get("title", "")))
            cat = html.escape(str(a.get("category", "")))
            desc = _inline_md(str(a.get("description", "")))
            href_open = (
                f"<a class='profile-app-card' href='{url}' target='_blank' rel='noopener'>"
                if url else "<div class='profile-app-card'>"
            )
            href_close = "</a>" if url else "</div>"
            parts.append(href_open)
            if cat:
                parts.append(f"<div class='profile-app-cat'>{cat}</div>")
            parts.append(f"<div class='profile-app-title'>{ttl}</div>")
            if desc:
                parts.append(f"<div class='profile-app-desc'>{desc}</div>")
            if url:
                parts.append("<span class='profile-app-go'>アプリを見る →</span>")
            parts.append(href_close)
        parts.append("</div>")

    # 多角的事業展開
    business = data.get("business") or []
    if business:
        parts.append("<h2 id='business'>🏢 多角的事業展開</h2>")
        parts.append("<div class='profile-biz-grid'>")
        for b in business:
            icon = html.escape(str(b.get("icon", "")))
            ttl = html.escape(str(b.get("title", "")))
            desc = _inline_md(str(b.get("description", "")))
            metrics = b.get("metrics") or []
            parts.append("<div class='profile-biz-card'>")
            parts.append(
                f"<div class='profile-biz-title'><span class='ic'>{icon}</span>{ttl}</div>"
            )
            if desc:
                parts.append(f"<div class='profile-biz-desc'>{desc}</div>")
            if metrics:
                parts.append("<div class='profile-biz-metrics'>")
                for m in metrics:
                    lbl = html.escape(str(m.get("label", "")))
                    val = html.escape(str(m.get("value", "")))
                    parts.append(
                        f"<div class='row'><span class='lbl'>{lbl}</span><span class='val'>{val}</span></div>"
                    )
                parts.append("</div>")
            parts.append("</div>")
        parts.append("</div>")

    # フッターリンク
    footer_links = data.get("footer_links") or []
    if footer_links:
        parts.append("<h2 id='links'>🔗 関連リンク</h2>")
        parts.append("<div class='profile-footer-links'>")
        for fl in footer_links:
            url = html.escape(str(fl.get("url", "")), quote=True)
            lbl = html.escape(str(fl.get("label", "")))
            if url and lbl:
                parts.append(f"<a href='{url}' target='_blank' rel='noopener'>{lbl}</a>")
        parts.append("</div>")

    # 出典
    src_bits: list[str] = []
    if gen_by:
        src_bits.append(html.escape(gen_by))
    if source_url:
        src_bits.append(
            f"<a href='{html.escape(source_url, quote=True)}' target='_blank' rel='noopener'>"
            "オリジナルプロフィール（GenSpark）→</a>"
        )
    if src_bits:
        parts.append(
            "<div class='profile-source'>📎 出典: " + " ／ ".join(src_bits)
            + "<br><span style='font-size:11px'>編集は <code>config/profile.yaml</code> を直接修正して "
            "<code>python site/build_site.py</code> で再ビルド。</span></div>"
        )

    return "".join(parts)


def build_profile_page() -> bool:
    """profile.html is retired so achievement-heavy profile content is not published."""
    target = DIST / "profile.html"
    if target.exists():
        target.unlink()
    return False


def copy_static() -> None:
    if not STATIC.exists():
        return
    for src in STATIC.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(STATIC)
        # admin/ ・ ops/ は静的配信せず管理ログイン付きの
        # api/admin/index.ts ・ api/ops/index.ts から返す（認証素通り防止）
        if rel.parts and rel.parts[0] in ("admin", "ops"):
            continue
        dst = DIST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    # static の programming-map.html だけ後処理: 独自ナビを共通ナビへ置換し、
    # 章立てはページ内目次バーに分離する
    pmap = DIST / "programming-map.html"
    if pmap.exists():
        _patch_programming_map_nav(pmap)


def _patch_programming_map_nav(pmap_file: Path) -> None:
    """programming-map.html の <nav class="top-nav">...</nav> ブロックを
    全ページ共通の render_top_nav() 出力で置換し、
    章立て (#part-1〜#sec-line) はページ内目次バーに分離する。"""
    import re as _re
    text = pmap_file.read_text(encoding="utf-8")
    # 共通ナビ HTML（pmap を current として）
    common_nav = render_top_nav(path_prefix="./", current_id="pmap", include_run=False)
    # ページ内目次バー（AIコーディング講習 専用 — sticky とは別）
    chapter_toc = (
        "<nav class='pm-chapter-toc' aria-label='ページ内目次'>"
        "<span class='pm-toc-label'>AI CODING</span>"
        "<a href='#top'>全体</a>"
        "<a href='#pm-real-pro'>00 本物のプロ</a>"
        "<a href='#pm-level-map'>01 レベル</a>"
        "<a href='#pm-pro-check'>02 説明力</a>"
        "<a href='#pm-modern-ai'>03 AI全体像</a>"
        "<a href='#part-1'>04 価値と入口</a>"
        "<a href='#part-2'>05 基礎</a>"
        "<a href='#part-3'>06 実装</a>"
        "<a href='#part-4'>07 公開</a>"
        "<a href='#sec-cms'>08 応用制作</a>"
        "<a href='#sec-ccode'>09 実務運用</a>"
        "<a href='#sec-line'>10 総合演習</a>"
        "</nav>"
    )
    # 共通トップヘッダー/ナビの CSS を、正本 CSS 定数からマーカーで切り出して注入する。
    # static の programming-map.html は <style> に header.site-header / nav.top-nav を
    # 持たないため、これを入れないと共通ナビのマークアップだけ付いて無スタイルになる
    # （= PORTAL_CSS 未定義クラス再発バグ。2026-05-19 修正）。
    # 文字列スライスで CSS 定数を参照するので、正本が変われば自動追従し二重管理にならない。
    _NAV_CSS_START = "/* ---- 共通トップヘッダー（fixed・N デザイン風 white/blur）---- */"
    _NAV_CSS_END = ".run-status.running { color:#b45309; }"
    _s = CSS.find(_NAV_CSS_START)
    _e = CSS.find(_NAV_CSS_END)
    if _s == -1 or _e == -1:
        # 正本側のマーカーが変わったら気付けるよう明示的に失敗させる
        raise RuntimeError(
            "programming-map nav CSS マーカーが CSS 定数内に見つからない"
            "（build_site.py の共通ヘッダー/ナビ CSS のコメントを変更した可能性）"
        )
    common_nav_css = CSS[_s : _e + len(_NAV_CSS_END)]
    # ページ内目次バーの CSS をまとめる
    chapter_css = (
        "<style id='pm-chapter-toc-css'>"
        # ---- 共通トップヘッダー/ナビ（index.html 等と同一・正本 CSS から抽出） ----
        + common_nav_css
        # ページ内目次バー（AIコーディング講習 専用：fixed top-nav の真下に1段で吸着）
        + "html{scroll-padding-top:118px;}"
        "[id]{scroll-margin-top:118px;}"
        ".pm-chapter-toc{position:sticky;top:66px;z-index:40;"
        "max-width:min(1160px,calc(100vw - 20px));"
        "display:flex;flex-wrap:nowrap;align-items:center;gap:6px;"
        "margin:0 auto 18px;padding:7px 10px;overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;"
        "background:rgba(255,255,255,.82);border:1px solid rgba(16,24,39,.12);"
        "border-radius:8px;backdrop-filter:blur(18px) saturate(160%);"
        "-webkit-backdrop-filter:blur(18px) saturate(160%);"
        "box-shadow:0 10px 28px rgba(16,24,39,.08),inset 0 1px 0 rgba(255,255,255,.82);}"
        ".pm-chapter-toc .pm-toc-label{font-size:10.5px;font-weight:800;letter-spacing:.14em;"
        "color:#2357e5;text-transform:uppercase;padding-right:4px;white-space:nowrap;}"
        ".pm-chapter-toc a{display:inline-flex;align-items:center;gap:3px;padding:5px 11px;"
        "flex:0 0 auto;border-radius:8px;background:rgba(255,255,255,.78);border:1px solid rgba(16,24,39,.12);"
        "color:#3a475d;text-decoration:none;font-size:11.5px;font-weight:700;line-height:1.3;"
        "white-space:nowrap;transition:all .2s;}"
        ".pm-chapter-toc a:hover{background:rgba(255,255,255,.95);color:#2357e5;"
        "border-color:rgba(6,167,216,.34);transform:translateY(-1px);}"
        "@media (max-width:640px){"
        "html{scroll-padding-top:108px;}[id]{scroll-margin-top:108px;}"
        ".pm-chapter-toc{padding:6px 8px;gap:5px;top:60px;max-width:calc(100vw - 12px);}"
        ".pm-chapter-toc a{padding:5px 10px;font-size:11px;}}"
        "</style>"
    )
    # 既存の <nav class="top-nav" aria-label="サイトナビゲーション">...</nav> を置換
    new_text, n = _re.subn(
        r'<nav class="top-nav" aria-label="サイトナビゲーション">.*?</nav>',
        common_nav + "\n" + chapter_toc,
        text,
        count=1,
        flags=_re.DOTALL,
    )
    if n == 0:
        return
    # CSS を </head> 直前に注入（既に注入済みなら何もしない）
    if "id='pm-chapter-toc-css'" not in new_text and "id=\"pm-chapter-toc-css\"" not in new_text:
        new_text = new_text.replace("</head>", chapter_css + "</head>", 1)
    pmap_file.write_text(new_text, encoding="utf-8")


def build_sitemap_and_robots() -> None:
    """DIST 内の index.html / speaker.html / programming-map.html / lectures/*.html / watch/*.html を
    集めて sitemap.xml と robots.txt を生成。"""
    urls: list[tuple[str, str, float]] = []  # (loc, lastmod, priority)
    today = datetime.now().strftime("%Y-%m-%d")

    def add(path_rel: str, priority: float) -> None:
        f = DIST / path_rel
        if not f.exists():
            return
        ts = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        urls.append((f"{SITE_URL}/{path_rel.replace(chr(92), '/')}", ts, priority))

    add("index.html", 1.0)
    add("speaker.html", 0.9)
    add("programming-map.html", 0.8)
    # lectures
    lec_idx = DIST / "lectures" / "index.html"
    if lec_idx.exists():
        add("lectures/index.html", 0.7)
    lec_dir = DIST / "lectures"
    if lec_dir.exists():
        for lp in sorted(lec_dir.glob("*.html")):
            if lp.name == "index.html":
                continue
            add(f"lectures/{lp.name}", 0.8)
    # blog
    blog_idx = DIST / "blog" / "index.html"
    if blog_idx.exists():
        add("blog/index.html", 0.7)
    blog_dir = DIST / "blog"
    if blog_dir.exists():
        for bp in sorted(blog_dir.glob("*.html")):
            if bp.name == "index.html":
                continue
            add(f"blog/{bp.name}", 0.8)
    # watch(SNSポータル) は管理ページ配下へ移行したため公開 sitemap には含めない。

    if not urls:
        return

    xml_lines = ["<?xml version='1.0' encoding='UTF-8'?>",
                 "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    for loc, lastmod, prio in urls:
        xml_lines.append(
            "  <url>"
            f"<loc>{html.escape(loc)}</loc>"
            f"<lastmod>{lastmod}</lastmod>"
            f"<priority>{prio:.1f}</priority>"
            "</url>"
        )
    xml_lines.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(xml_lines), encoding="utf-8")

    (DIST / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /api/\n"
        "Disallow: /ops\n"
        "Disallow: /watch/\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )




def build_slides() -> int:
    """Build Marp slides from content/slides/*.md -> site/dist/slides/<slug>.html.

    PDFs are pre-generated and committed to site/static/slides/; they are served
    automatically via copy_static() without any extra step here.

    Fail-safe: if npx / node is not available, print a WARNING and return 0 so
    that the existing build pipeline is never broken.
    """
    import subprocess  # noqa: PLC0415

    slides_dir = ROOT / "content" / "slides"
    out_dir = DIST / "slides"

    if not slides_dir.exists():
        return 0

    # Only process main slide decks, not script files (-script suffix)
    slide_files = [
        f for f in sorted(slides_dir.glob("climbing-history-*.md"))
        if "-script" not in f.stem
    ]
    if not slide_files:
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    built = 0

    # Windows resolves "npx" to npx.cmd which subprocess (no shell) does not
    # find by bare name; probe for an explicit executable name on Windows.
    import shutil as _shutil  # noqa: PLC0415
    npx_exe = _shutil.which("npx") or _shutil.which("npx.cmd") or "npx"

    for src in slide_files:
        dst = out_dir / (src.stem + ".html")
        cmd = [
            npx_exe, "--yes", "@marp-team/marp-cli",
            str(src),
            "--html",
            "--no-stdin",
            "--output", str(dst),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"[slides] Built: {dst.relative_to(ROOT)}")
                built += 1
            else:
                stderr = result.stderr.strip()
                print(f"[WARNING] Marp build failed for {src.name}: {stderr[:200]}")
        except FileNotFoundError:
            print("[WARNING] npx not found - skipping Marp slide build. Install Node.js to enable.")
            return 0
        except subprocess.TimeoutExpired:
            print(f"[WARNING] Marp build timed out for {src.name} - skipping.")
        except Exception as exc:  # noqa: BLE001
            print(f"[WARNING] Marp build error for {src.name}: {exc}")

    return built

def _build_portal() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_portal  # noqa: WPS433
    build_portal.main(dry_run=False)


def _reset_dist() -> None:
    """Reset dist while tolerating a Windows process holding the dist folder."""
    if not DIST.exists():
        DIST.mkdir(parents=True, exist_ok=True)
        return

    try:
        shutil.rmtree(DIST)
        DIST.mkdir(parents=True, exist_ok=True)
        return
    except PermissionError as exc:
        if os.name != "nt":
            raise
        print(f"[WARNING] dist root is locked; reusing folder after clearing contents: {exc}")

    for child in DIST.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    DIST.mkdir(parents=True, exist_ok=True)


def main() -> int:
    _reset_dist()

    copy_static()

    genres = load_genres()

    # AI Watch コンテンツは /watch/ サブディレクトリに出力する (Phase 1 移設)
    WATCH_DIR = DIST / "watch"
    WATCH_DIR.mkdir(parents=True, exist_ok=True)

    if not TOP10_JSON.exists():
        print(f"[!] {TOP10_JSON} が見つかりません。run.py を先に実行してください。")
        (WATCH_DIR / "index.html").write_text(
            render_index({"date": datetime.now().strftime("%Y-%m-%d"), "items": []}, genres),
            encoding="utf-8",
        )
        (WATCH_DIR / "archive.html").write_text(render_archive([]), encoding="utf-8")
        (DIST / ".nojekyll").write_text("", encoding="utf-8")
        build_speaker_page()
        build_lectures()
        build_blog()
        build_profile_page()
        build_slides()
        _build_portal()
        build_sitemap_and_robots()
        return 0

    payload = json.loads(TOP10_JSON.read_text(encoding="utf-8"))
    (WATCH_DIR / "index.html").write_text(render_index(payload, genres), encoding="utf-8")

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    date = payload.get("date", datetime.now().strftime("%Y-%m-%d"))
    archive_file = ARCHIVE_DIR / f"{date}.json"
    archive_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    dates: list[str] = []
    for f in sorted(ARCHIVE_DIR.glob("*.json"), reverse=True):
        d = f.stem
        dates.append(d)
        arc_payload = json.loads(f.read_text(encoding="utf-8"))
        (WATCH_DIR / f"{d}.html").write_text(render_index(arc_payload, genres, is_live=False), encoding="utf-8")

    (WATCH_DIR / "archive.html").write_text(render_archive(dates), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    speaker_built = build_speaker_page()
    lectures_built = build_lectures()
    blog_built = build_blog()
    slides_built = build_slides()
    profile_removed = build_profile_page()
    _build_portal()
    build_sitemap_and_robots()

    print(
        f"[+] site built: {DIST} ({len(dates)} archive pages in watch/"
        + (", speaker.html" if speaker_built else "")
        + (f", {lectures_built} lectures" if lectures_built else "")
        + (f", {blog_built} blog posts" if blog_built else "")
        + (f", {slides_built} slides" if slides_built else "")
        + (", profile.html removed" if profile_removed else "")
        + ", sitemap.xml, robots.txt)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
