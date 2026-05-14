"""
エージェント運用状況の集約スクリプト。
outputs/agents_status.json を生成し、/admin が fetch して表示する。

「意味あるもの」を目指し、ファイル列挙ではなく実用シグナルを抽出する:

  - recent_works         直近 8 件 (タイトル + 日付 + 事業ラベル)
  - tasks_open           各 work ファイル内の TODO / FIXME / 「未対応」「ブロック」行 抜粋
  - per_business_recent  事業ごとの直近 7 日件数 (グッぼる / Notエステ / Nデザイン / ビジネス21 ...)
  - daily_histogram      日別件数（直近 14 日）
  - cma_apps             agents_system/INDEX.md の実行履歴
  - generated_at         UTC ISO

ファイル命名: content/consul-work/YYYY-MM-DD-<事業>-<内容>.md
"""
from __future__ import annotations
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK_DIR = ROOT / "content" / "consul-work"
INDEX_MD = ROOT.parent / "agents_system" / "INDEX.md"
OUT_FILE = ROOT / "outputs" / "agents_status.json"

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

# ファイル名の <事業> セグメントから日本語事業名に正規化
BIZ_LABELS = {
    "good": "グッぼる",
    "goodbouldering": "グッぼる",
    "karatto": "カラッと",
    "este": "Notエステ",
    "notesthe": "Notエステ",
    "notesute": "Notエステ",
    "n-design": "Nデザイン",
    "ndesign": "Nデザイン",
    "business-21": "ビジネス21",
    "business21": "ビジネス21",
    "minanowa": "みんなのWA",
    "trust": "トラスト",
    "fadie": "ファディー",
    "fadi": "ファディー",
    "ai-hub": "AIハブ",
    "aihub": "AIハブ",
}

TASK_KEYWORDS = re.compile(
    r"(TODO|FIXME|未対応|未解決|未着手|ブロック|要確認|要対応|保留|締切|期限)[:：\s]",
    re.IGNORECASE,
)


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        m = re.search(r"\n---\s*\n", text)
        if m:
            return text[m.end():]
    return text


def _title_of(text: str, fallback: str) -> str:
    body = _strip_frontmatter(text)
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def _business_label(filename: str) -> str:
    # YYYY-MM-DD-<biz>-<...>.md
    parts = filename.replace(".md", "").split("-")
    if len(parts) < 4:
        return ""
    # 4 番目以降を結合して順に hit するキーを探す（複合キー対応: business-21 / n-design / ai-hub）
    rest = "-".join(parts[3:]).lower()
    # 長いキーから順に評価
    for key in sorted(BIZ_LABELS.keys(), key=len, reverse=True):
        if rest.startswith(key):
            return BIZ_LABELS[key]
    # ヒットしなければ最初のセグメント
    return parts[3]


def _extract_tasks(text: str, limit: int = 3) -> list[str]:
    """TODO / FIXME / 未対応 などのキーワードを含む行を抜粋。
    短すぎる行は捨て、長すぎる行は 140 字で切る。"""
    out: list[str] = []
    for raw in _strip_frontmatter(text).splitlines():
        line = raw.strip()
        if len(line) < 8:
            continue
        if not TASK_KEYWORDS.search(line):
            continue
        # 先頭の Markdown 装飾を剥がす
        clean = re.sub(r"^[#*\->\s]+", "", line)
        if len(clean) > 140:
            clean = clean[:138] + "…"
        out.append(clean)
        if len(out) >= limit:
            break
    return out


def _today_utc() -> datetime:
    return datetime.now(timezone.utc)


def _collect() -> dict:
    works_files: list[tuple[str, str, Path]] = []  # (date, filename, path)
    if WORK_DIR.exists():
        for md in WORK_DIR.glob("*.md"):
            m = DATE_RE.match(md.stem)
            if m:
                works_files.append((m.group(1), md.name, md))
    works_files.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # recent_works (8 件) + open task 抽出
    recent_works: list[dict] = []
    tasks_open: list[dict] = []
    for date, name, path in works_files[:8]:
        text = _read_text(path)
        recent_works.append({
            "date": date,
            "filename": name,
            "title": _title_of(text, name),
            "business": _business_label(name),
            "path": f"/admin/docs?file={name}",
        })

    for date, name, path in works_files[:40]:  # 直近 40 件まで task 抽出
        text = _read_text(path)
        tasks = _extract_tasks(text, limit=3)
        for t in tasks:
            tasks_open.append({
                "date": date,
                "filename": name,
                "business": _business_label(name),
                "snippet": t,
                "path": f"/admin/docs?file={name}",
            })
    tasks_open = tasks_open[:20]  # トップ 20 件まで

    # 事業別 直近 7 日件数
    cutoff7 = (_today_utc() - timedelta(days=7)).date()
    per_business: dict[str, int] = {}
    for date, name, _ in works_files:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < cutoff7:
            break  # 既にソート済みなのでこれ以前は対象外
        biz = _business_label(name) or "(未分類)"
        per_business[biz] = per_business.get(biz, 0) + 1
    per_business_recent = sorted(
        ({"business": k, "count": v} for k, v in per_business.items()),
        key=lambda x: x["count"],
        reverse=True,
    )

    # 日別ヒストグラム（直近 14 日・件数 0 の日も埋める）
    daily: dict[str, int] = {}
    for date, _, _ in works_files:
        daily[date] = daily.get(date, 0) + 1
    histogram: list[dict] = []
    today = _today_utc().date()
    for i in range(13, -1, -1):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        histogram.append({"date": d, "count": daily.get(d, 0)})

    return {
        "generated_at": _today_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "recent_works": recent_works,
        "tasks_open": tasks_open,
        "per_business_recent": per_business_recent,
        "daily_histogram": histogram,
        "cma_apps": _collect_cma_apps(),
        "totals": {
            "consul_work_total": len(works_files),
            "recent_7d_total": sum(per_business.values()),
            "tasks_open_total": len(tasks_open),
        },
    }


def _collect_cma_apps() -> list[dict]:
    if not INDEX_MD.exists():
        return []
    out: list[dict] = []
    text = _read_text(INDEX_MD)
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 6 or not cols[0].isdigit():
            continue
        out.append({
            "name": cols[1],
            "last_run": cols[2],
            "kind": cols[4],
            "status": cols[5],
        })
    return out[:10]


def main() -> int:
    payload = _collect()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"[+] agents_status → {OUT_FILE} "
        f"(works={len(payload['recent_works'])}, tasks={len(payload['tasks_open'])}, "
        f"biz7d={len(payload['per_business_recent'])}, cma={len(payload['cma_apps'])})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
