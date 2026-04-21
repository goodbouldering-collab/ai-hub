# AI-watch

AI情報とSNSアルゴリズム動向を自動収集・整理するパイプライン。
RSS を中心に複数ソースから記事を集め、差分検出 → Claude API で要約 → NotebookLM 用 Markdown/TXT を出力する。

## 特徴

- **ソース追加は設定ファイル1つ**: `config/sources.yaml` に URL を書き足すだけ
- **差分検出**: SQLite(`data/history.db`) で過去取得を全保存し、前回以降の新着を自動でハイライト
- **NotebookLM 対応**: `outputs/notebooklm/latest.md` と `outputs/full/*.txt` をそのまま NotebookLM に放り込める
- **定期実行**: GitHub Actions (`.github/workflows/daily.yml`) で毎朝 JST 07:00 自動実行
- **拡張容易**: `core/collector.py` の `DISPATCH` に関数を追加すれば X API / スクレイピング等の新タイプに対応可能

## セットアップ

```bash
cd AI-watch
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

# .env に API キー (プロジェクトルートの .env を自動で読みます)
# ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 手動実行

```bash
python run.py                 # 日次ダイジェスト (diff モード)
python run.py --full          # 統合版 (NotebookLM 丸ごと投入用) も生成
python run.py --no-summary    # Claude API を使わずタイトル＋原文抜粋だけ
```

## 出力ファイル

| パス | 用途 |
|---|---|
| `outputs/notebooklm/latest.md` | 常に最新の日次ダイジェスト (上書き) |
| `outputs/notebooklm/YYYY-MM-DD.md` | 日付別アーカイブ |
| `outputs/full/YYYY-MM-DD_full.txt` | 全ソース統合版 (NotebookLM ソース投入用) |
| `data/history.db` | 過去取得全ログ (SQLite) |

## ソースを追加する

`config/sources.yaml` を編集。

```yaml
  - name: 新しいソース名
    type: rss                 # 現時点では rss のみ対応
    url: https://example.com/feed.xml
    category: カテゴリ名        # 出力で自動グルーピング
    enabled: true
```

RSS 以外(X API, スクレイピング等)を追加したくなったら `core/collector.py` の `DISPATCH` に関数を足す。

## GitHub Actions で定期実行

1. このディレクトリを GitHub リポジトリに push
2. リポジトリの `Settings → Secrets and variables → Actions` で `ANTHROPIC_API_KEY` を登録
3. `.github/workflows/daily.yml` が毎朝 JST 07:00 に自動実行し、生成物を `outputs/` に commit back する

## NotebookLM への取り込み方

1. `outputs/full/YYYY-MM-DD_full.txt` を NotebookLM の「ソースを追加」にアップロード
2. 日次の差分だけ追いたい場合は `outputs/notebooklm/latest.md` を追加
3. 古いソースは NotebookLM 側で手動削除
