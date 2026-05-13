"""
エージェント運用状況の集約スクリプト。
outputs/agents_status.json を生成し、build_portal.py がトップに静的描画する。

入力:
  - consul/.claude/agents/*.md  → 社内エージェント定義 (役割と最新更新)
  - content/consul-work/*.md    → 各エージェントの最新成果物 (consul/work から日次同期)
  - agents_system/INDEX.md      → CMA で動かしているアプリの一覧 (ローカル側のため CI では空配列扱い)

出力:
  outputs/agents_status.json {
    "generated_at": "2026-05-14T10:00:00Z",
    "consul_agents": [{ "name", "role_summary", "last_work_date", "last_work_title", "last_work_path" }, ...],
    "recent_works":  [{ "date", "title", "path", "category" }, ...],   # 最新 8 件
    "cma_apps":      [{ "name", "status", "last_run" }, ...]            # ベストエフォート
  }

引数なし。CI でも手元でも実行できる。読み取り元が見つからない場合は空配列で書き出す。
"""
from __future__ import annotations
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONSUL_AGENTS_DIR = ROOT / "content" / "consul-work" / ".." / ".." / "content" / "consul-work"
# consul/.claude/agents/ は ai-hub リポには無いので、agent 名だけハードコードしておく
AGENT_NAMES = [
    ("secretary", "受付・振り分け（CEO 窓口）"),
    ("advisor",   "助言・経営観点レビュー"),
    ("cfo",       "数字・採算・キャッシュフロー"),
    ("designer",  "UI / ビジュアル制作"),
    ("developer", "実装・コード作成"),
    ("mailer",    "顧客メール・LINE 文面"),
    ("marketer",  "集客・SNS 戦略"),
    ("pm",        "進行管理・スケジュール調整"),
    ("scheduler", "予約・カレンダー調整"),
    ("writer",    "記事・コピー執筆"),
]

WORK_DIR = ROOT / "content" / "consul-work"
INDEX_MD = ROOT.parent / "agents_system" / "INDEX.md"
OUT_FILE = ROOT / "outputs" / "agents_status.json"


DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def _read_title(md_path: Path) -> str:
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return md_path.stem
    # frontmatter スキップ
    if text.startswith("---"):
        m = re.search(r"\n---\s*\n", text)
        if m:
            text = text[m.end():]
    # 最初の # 見出し
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return md_path.stem


def _collect_recent_works(limit: int = 8) -> list[dict]:
    if not WORK_DIR.exists():
        return []
    items: list[dict] = []
    for md in WORK_DIR.glob("*.md"):
        m = DATE_RE.match(md.stem)
        if not m:
            continue
        date = m.group(1)
        # YYYY-MM-DD-<biz>-<topic>.md → category=2つ目のセグメント
        parts = md.stem.split("-")
        category = parts[3] if len(parts) >= 4 else ""
        items.append({
            "date": date,
            "title": _read_title(md),
            "path": f"/admin/docs?file={md.name}",
            "category": category,
            "filename": md.name,
        })
    items.sort(key=lambda x: (x["date"], x["filename"]), reverse=True)
    return items[:limit]


def _collect_consul_agents() -> list[dict]:
    """各エージェントが最後に何を書いたかを consul/work のファイル名から推定する。
    ファイル命名は YYYY-MM-DD-<事業>-<内容>.md でエージェント名が直接入らないため、
    現状は agent ごとの「役割サマリ」と「過去 30 日に同じカテゴリ語が含まれる成果物」の
    軽い結びつけのみ。詳細な紐付けは将来 frontmatter で実装する。
    """
    works = _collect_recent_works(limit=200)
    out: list[dict] = []
    for name, role in AGENT_NAMES:
        # name と category が一致する成果物（ヒューリスティック）
        matched = next((w for w in works if name in w["filename"].lower()), None)
        out.append({
            "name": name,
            "role_summary": role,
            "last_work_date": matched["date"] if matched else None,
            "last_work_title": matched["title"] if matched else None,
            "last_work_path": matched["path"] if matched else None,
        })
    return out


def _collect_cma_apps() -> list[dict]:
    if not INDEX_MD.exists():
        return []
    out: list[dict] = []
    try:
        text = INDEX_MD.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    # | # | アプリ名 | 実行日 | ポート | 種別 | 状態 | レポート |
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        # ヘッダ / 区切り / 空行をスキップ
        if len(cols) < 6:
            continue
        if cols[0] in ("#", "") or cols[0].startswith("--") or cols[0].startswith(":-"):
            continue
        if not cols[0].isdigit():
            continue
        out.append({
            "name": cols[1],
            "last_run": cols[2],
            "kind": cols[4],
            "status": cols[5],
        })
    return out[:10]


def main() -> int:
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "consul_agents": _collect_consul_agents(),
        "recent_works": _collect_recent_works(limit=8),
        "cma_apps": _collect_cma_apps(),
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[+] agents_status → {OUT_FILE} ({len(payload['recent_works'])} works, {len(payload['cma_apps'])} cma apps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
