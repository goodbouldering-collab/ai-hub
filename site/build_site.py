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
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
TOP10_JSON = ROOT / "outputs" / "top10.json"
ARCHIVE_DIR = ROOT / "outputs" / "archive"
GENRES_YAML = ROOT / "config" / "genres.yaml"
SUPPORT_SNS_YAML = ROOT / "config" / "support_sns.yaml"
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


CSS = """
:root {
  --text:#f2f4fb;
  --muted:#aab1c5;
  --glass-bg:rgba(255,255,255,0.06);
  --glass-border:rgba(255,255,255,0.14);
  --glass-hover:rgba(255,255,255,0.10);
  --accent1:#7aa2ff;
  --accent2:#c77dff;
  --accent3:#ff7ab6;
}
* { box-sizing: border-box; }
html, body { margin:0; padding:0; }
body {
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans","Noto Sans JP",sans-serif;
  color:var(--text);
  line-height:1.7;
  min-height:100vh;
  background:
    radial-gradient(1200px 800px at 15% -10%, rgba(122,162,255,.35), transparent 60%),
    radial-gradient(900px 700px at 85% 10%, rgba(199,125,255,.28), transparent 60%),
    radial-gradient(1000px 800px at 50% 110%, rgba(255,122,182,.22), transparent 60%),
    linear-gradient(180deg, #0a0d1a 0%, #0d1126 50%, #0a0d1a 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
}
.container { position:relative; z-index:1; max-width: 920px; margin: 0 auto; padding: 48px 20px 80px; }

header { margin-bottom:32px; }
header h1 {
  margin:0 0 8px;
  font-size:clamp(28px, 5vw, 42px);
  font-weight:800;
  background: linear-gradient(100deg, var(--accent1) 0%, var(--accent2) 45%, var(--accent3) 100%);
  -webkit-background-clip:text;
  background-clip:text;
  color:transparent;
  filter: drop-shadow(0 2px 20px rgba(122,162,255,.25));
  background-size: 200% 100%;
  animation: shimmer 6s ease-in-out infinite;
}
@keyframes shimmer {
  0%,100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
header .sub { margin:0; color:var(--muted); font-size:13px; letter-spacing:.04em; }

nav { margin-top:16px; display:flex; gap:10px; flex-wrap:wrap; }
nav a {
  padding:8px 16px; border-radius:999px;
  background:var(--glass-bg); border:1px solid var(--glass-border);
  backdrop-filter: blur(14px) saturate(160%);
  color:var(--text); text-decoration:none; font-size:13px;
  transition: all .25s ease;
}
nav a:hover { background:var(--glass-hover); transform: translateY(-1px); }
.run-btn {
  font: inherit;
  padding:8px 16px; border-radius:999px;
  background: linear-gradient(135deg, rgba(122,162,255,.35), rgba(199,125,255,.35));
  border:1px solid rgba(255,255,255,.22);
  color:var(--text); cursor:pointer; font-size:13px; font-weight:700;
  backdrop-filter: blur(14px) saturate(160%);
  transition: all .25s ease;
}
.run-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(122,162,255,.55), rgba(199,125,255,.55));
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(122,162,255,.25);
}
.run-btn:disabled { opacity:.6; cursor:not-allowed; }
.run-status { margin-left:10px; font-size:12px; color:var(--muted); }
.run-status.ok { color:#7eeba3; }
.run-status.err { color:#ff7a90; }
.run-status.running { color:#ffd36b; }

.genre-tabs {
  display:flex; flex-wrap:wrap; gap:8px;
  margin:24px 0 28px; padding:10px;
  background:var(--glass-bg); border:1px solid var(--glass-border);
  border-radius:16px;
  backdrop-filter: blur(16px) saturate(160%);
}
.genre-tab {
  font: inherit;
  padding:8px 14px; border-radius:999px;
  background:transparent; border:1px solid transparent;
  color:var(--muted); cursor:pointer; font-size:13px; font-weight:600;
  transition: all .25s ease;
  display:inline-flex; align-items:center; gap:6px;
}
.genre-tab:hover { color:var(--text); background:rgba(255,255,255,.05); }
.genre-tab.active {
  background: linear-gradient(135deg, rgba(122,162,255,.3), rgba(199,125,255,.3));
  color:var(--text); border-color: rgba(255,255,255,.2);
  box-shadow: 0 4px 16px rgba(122,162,255,.25);
}

.group { margin-top:36px; }
.group-head {
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom:14px; padding:14px 20px;
  background: linear-gradient(135deg, rgba(122,162,255,.12), rgba(199,125,255,.08));
  border:1px solid var(--glass-border); border-radius:16px;
  backdrop-filter: blur(16px);
}
.group-label {
  font-size:17px; font-weight:800;
  background: linear-gradient(100deg, var(--accent1), var(--accent2));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.group-count {
  font-size:11px; color:var(--muted);
  padding:4px 10px; border-radius:999px;
  background:rgba(255,255,255,.06); border:1px solid var(--glass-border);
}

.sub-tabs {
  display:flex; gap:6px; margin:0 0 12px 4px;
}
.sub-tab {
  font: inherit;
  padding:4px 12px; border-radius:999px;
  background:transparent; border:1px solid rgba(255,255,255,.12);
  color:var(--muted); cursor:pointer; font-size:11px; font-weight:600;
  transition: all .2s ease;
}
.sub-tab:hover { color:var(--text); }
.sub-tab.active {
  background: rgba(122,162,255,.2); color:var(--text);
  border-color: rgba(122,162,255,.4);
}

article {
  position:relative;
  display:flex; gap:16px;
  background:var(--glass-bg); border:1px solid var(--glass-border);
  border-radius:18px; padding:16px;
  margin-bottom:12px;
  backdrop-filter: blur(18px) saturate(160%);
  box-shadow: 0 8px 32px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.08);
  transition: transform .3s ease, background .3s ease, box-shadow .3s ease;
  cursor:pointer;
  text-decoration:none; color:inherit;
  overflow:hidden;
}
article:hover {
  transform: translateY(-3px);
  background:var(--glass-hover);
  box-shadow: 0 16px 48px rgba(122,162,255,.18);
}
.thumb {
  flex-shrink:0;
  width:140px; height:88px;
  border-radius:12px;
  background:rgba(255,255,255,.04) center/cover;
  border:1px solid var(--glass-border);
  position:relative;
  overflow:hidden;
}
.thumb.placeholder {
  display:flex; align-items:center; justify-content:center;
  font-size:28px; opacity:.4;
  background: linear-gradient(135deg, rgba(122,162,255,.15), rgba(199,125,255,.15));
}
.thumb .play {
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-size:32px; color:#fff;
  text-shadow: 0 2px 12px rgba(0,0,0,.6);
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
  background: linear-gradient(135deg, var(--accent1), var(--accent2));
  color:#fff; font-weight:800;
}
.meta .score { opacity:.7; }
article h3 {
  margin:0; font-size:15px; font-weight:700;
  line-height:1.5; color:var(--text);
}
article p {
  margin:0; font-size:12.5px; color:#c5cbdd;
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
  background:var(--glass-bg); border:1px solid var(--glass-border);
  border-radius:16px;
}

footer {
  margin-top:64px; padding-top:20px;
  color:var(--muted); font-size:11px; text-align:center;
  letter-spacing:.1em; text-transform:uppercase; opacity:.6;
}

.support-sns { margin-top: 48px; }
.support-sns > h2 {
  font-size: 18px; font-weight: 800; margin-bottom: 14px;
  background: linear-gradient(100deg, var(--accent1), var(--accent3));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.support-sns .empty {
  color:var(--muted); font-size:13px;
  padding:20px; text-align:center;
  background:var(--glass-bg); border:1px solid var(--glass-border);
  border-radius:14px;
}
.sns-grid {
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap:14px;
}
.sns-card {
  background:var(--glass-bg); border:1px solid var(--glass-border);
  border-radius:14px; padding:14px 16px;
  backdrop-filter: blur(14px);
}
.sns-head {
  font-size:13px; font-weight:700; color:var(--text);
  margin-bottom:8px; display:flex; align-items:center; gap:8px;
}
.sns-count {
  font-size:10px; color:var(--muted);
  padding:2px 8px; border-radius:999px;
  background:rgba(255,255,255,.06); border:1px solid var(--glass-border);
}
.sns-list { list-style:none; margin:0; padding:0; }
.sns-list li {
  padding:6px 0; border-top:1px solid rgba(255,255,255,.06);
  font-size:12px; color:var(--text);
}
.sns-list li:first-child { border-top:none; }
.sns-list a { color:var(--accent1); text-decoration:none; }
.sns-list a:hover { text-decoration:underline; }
.sns-handle { color:var(--muted); font-size:11px; margin-left:4px; }
.sns-note { color:var(--muted); font-size:10px; margin-top:2px; }

@media (max-width: 640px) {
  .container { padding: 32px 14px 60px; }
  article { flex-direction:column; }
  .thumb { width:100%; height:180px; }
}
"""


def render_index(payload: dict, genres: list[dict]) -> str:
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
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>")
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append(f"<title>AI-watch Top{total} / {date}</title>")
    parts.append(f"<style>{CSS}</style></head><body><div class='container'>")
    parts.append("<header>")
    parts.append("<h1>AI-watch</h1>")
    parts.append(f"<p class='sub'>{date} ・ 今日の注目Top{total} ・ クリックで好みを学習</p>")
    parts.append(
        "<nav>"
        "<a href='./archive.html'>📚 過去ログ</a> "
        "<a href='./programming-map.html'>📘 プログラミングマップ</a> "
        "<a href='/admin'>⚙️ 管理画面</a> "
        "<button type='button' id='run-btn' class='run-btn'>🔄 巡回実行</button>"
        "<span id='run-status' class='run-status'></span>"
        "</nav>"
    )
    parts.append("</header>")

    if not items:
        parts.append("<p class='empty'>今日の記事はありません。</p>")
        parts.append(render_support_sns_section(load_support_sns()))
        parts.append("<footer>AI-watch</footer></div></body></html>")
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
    parts.append("<footer>AI-watch / Generated by Claude</footer>")
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
    parts.append("<!doctype html><html lang='ja'><head><meta charset='utf-8'>")
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append("<title>AI-watch — 過去ログ</title>")
    parts.append(f"<style>{CSS}</style></head><body><div class='container'>")
    parts.append("<header>")
    parts.append("<h1>過去ログ</h1>")
    parts.append(f"<p class='sub'>アーカイブ {len(dates)}件</p>")
    parts.append("<nav><a href='./index.html'>📰 最新に戻る</a> <a href='./programming-map.html'>📘 プログラミングマップ</a> <a href='/admin'>⚙️ 管理画面</a></nav>")
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
    parts.append("<footer>AI-watch</footer></div></body></html>")
    return "".join(parts)


def copy_static() -> None:
    if not STATIC.exists():
        return
    for src in STATIC.rglob("*"):
        if src.is_dir():
            continue
        dst = DIST / src.relative_to(STATIC)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    copy_static()

    genres = load_genres()

    if not TOP10_JSON.exists():
        print(f"[!] {TOP10_JSON} が見つかりません。run.py を先に実行してください。")
        (DIST / "index.html").write_text(
            render_index({"date": datetime.now().strftime("%Y-%m-%d"), "items": []}, genres),
            encoding="utf-8",
        )
        (DIST / "archive.html").write_text(render_archive([]), encoding="utf-8")
        (DIST / ".nojekyll").write_text("", encoding="utf-8")
        return 0

    payload = json.loads(TOP10_JSON.read_text(encoding="utf-8"))
    (DIST / "index.html").write_text(render_index(payload, genres), encoding="utf-8")

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
        (DIST / f"{d}.html").write_text(render_index(arc_payload, genres), encoding="utf-8")

    (DIST / "archive.html").write_text(render_archive(dates), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    print(f"[+] site built: {DIST} ({len(dates)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
