"""
AIハブ エントリーポイント。

使い方:
    python run.py                  # 過去24h の新着を収集・要約・NLM直貼り版を出力
    python run.py --hours 72        # 鮮度フィルタを変更
    python run.py --no-summary      # Claude API をスキップ (原文抜粋のまま)
    python run.py --full            # 全件統合版(--hours 無視)も併せて出力
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from dotenv import load_dotenv

from core.collector import collect_all
from core.differ import ArticleStore
from core.summarizer import summarize_all
from core.exporter import export_diff_report, export_full_source, export_nlm_paste, export_top10_json
from core.thumbnails import resolve_thumbnails
from core.ranker import rank_articles


ROOT = Path(__file__).parent
CONFIG = ROOT / "config" / "sources.yaml"
DB = ROOT / "data" / "history.db"
OUT_NLM = ROOT / "outputs" / "notebooklm"
OUT_FULL = ROOT / "outputs" / "full"
OUT_TOP10 = ROOT / "outputs" / "top10.json"
THUMB_CACHE = ROOT / "data" / "thumb_cache.json"
PREFS = ROOT / "data" / "preferences.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=24, help="何時間以内の記事に絞るか (デフォルト24)")
    parser.add_argument("--full", action="store_true", help="--hours に関係なく全件統合版も出力")
    parser.add_argument("--no-summary", action="store_true", help="Claude API での要約をスキップ")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env", override=False)
    load_dotenv(ROOT.parent.parent / ".env", override=False)
    load_dotenv(ROOT.parent.parent / "agents_system" / ".env", override=False)

    print("=" * 60)
    print(f" AIハブ 開始 (直近 {args.hours}h)")
    print("=" * 60)

    print("\n[1/4] ソース取得")
    articles = collect_all(CONFIG, max_age_hours=args.hours)
    print(f"  直近{args.hours}h以内: {len(articles)}件")

    if not articles:
        print("該当記事ゼロ。終了。")
        return 0

    print("\n[2/4] 差分検出 (SQLite)")
    store = ArticleStore(DB)
    try:
        new_items, existing_items = store.upsert(articles)
    finally:
        store.close()
    print(f"  新着: {len(new_items)}件 / 継続: {len(existing_items)}件")

    print("\n[3/4] 要約 (Claude API)")
    if args.no_summary:
        print("  スキップ (--no-summary)")
        summary_map = {}
    else:
        summary_map = summarize_all(articles)

    print("\n[4a/6] サムネ取得")
    thumb_map = resolve_thumbnails(articles, THUMB_CACHE)
    print(f"  サムネあり: {len(thumb_map)}/{len(articles)}件")

    print("\n[4b/6] ランキング (Top10選定)")
    top_articles, summary_map = rank_articles(articles, summary_map, PREFS)
    print(f"  Top{len(top_articles)}件を選定")
    for i, a in enumerate(top_articles, 1):
        info = summary_map.get(a.hash, {})
        print(f"  {i:2d}. [{info.get('final_score', 0):.0f}] {info.get('title_ja') or a.title[:50]}")

    print("\n[5/6] 出力")
    export_nlm_paste(articles, summary_map, OUT_NLM)
    export_diff_report(new_items, existing_items, summary_map, OUT_NLM)
    export_top10_json(top_articles, summary_map, thumb_map, OUT_TOP10)

    if args.full:
        print("\n[extra] 全件統合版 (--full)")
        all_articles = collect_all(CONFIG, max_age_hours=None)
        full_summary = summarize_all(all_articles) if not args.no_summary else {}
        export_full_source(all_articles, full_summary, OUT_FULL)

    print("\n[6/6] 静的サイト生成")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_site", ROOT / "site" / "build_site.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    except Exception as e:
        print(f"  サイト生成スキップ: {e}")

    print("\n完了。")
    print(f"NotebookLM直貼り用: {OUT_NLM / 'nlm_latest.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
