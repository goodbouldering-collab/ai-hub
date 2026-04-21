# CLAUDE.md — AI-watch

AI 情報と SNS アルゴリズム動向を自動収集・要約・可視化するパイプライン。
RSS を中心に複数ソースから記事を集め、差分検出 → Claude API で要約 → NotebookLM 用 Markdown/TXT + 静的サイトを出力する。

## リポジトリ名の正規化

- プロジェクト名: **AI-watch**（かつての「AI情報収集」「cclimb-intel」「ai-info」から統一）
- GitHub: `goodbouldering-collab/ai-watch`
- Render service: `ai-watch`（静的サイト、Singapore、`main` push で自動デプロイ）
- GitHub Pages: `https://goodbouldering-collab.github.io/ai-watch/`
- Supabase: 既存の共有プロジェクト `zrawhzwtppmlxyhngnju` の `public.ai_watch_*` 相乗り

新規で文言を書くときは「AI-watch」に揃える。過去ログ（`outputs/notebooklm/*`）は改名しない（NotebookLM 側で参照中のため）。

## ディレクトリ

| パス | 役割 |
|---|---|
| `run.py` | エントリーポイント。収集→要約→出力→サイト生成まで一気通貫 |
| `core/` | 収集・差分・要約・ランキング・サムネ・書き出し |
| `config/sources.yaml` | 収集対象 RSS。追加するだけで増やせる |
| `config/genres.yaml` | ジャンル（AI業務活用 / SNSアルゴリズム 等）の定義 |
| `config/support_sns.yaml` | サポートSNSアカウントリスト |
| `site/build_site.py` | `outputs/top10.json` から静的 HTML を生成 |
| `site/dist/` | 生成物（GitHub Pages / Render が公開） |
| `outputs/notebooklm/` | NotebookLM 用 Markdown/TXT（日次） |
| `outputs/full/` | 週次フル版 TXT |
| `data/history.db` | SQLite の既取得ログ（差分検出の土台） |
| `admin/server.py` | FastAPI 管理画面（ローカル 4001） |
| `scripts/migrate_sqlite_to_supabase.py` | SQLite → Supabase へのマイグレーション |
| `content/speaker.md` | 講師紹介（由井辰美）の編集ソース。ビルドで `speaker.html` になる |
| `content/lectures/*.md` | 講習資料の編集ソース。ビルドで `lectures/<slug>.html` になる |
| `content/assets/` | 画像・PDF。`./assets/xxx` で参照 |

## デプロイ構成

- **GitHub Actions `daily.yml`**: JST 07:00 に `run.py` を実行し、`outputs/` と `data/history.db` を main に commit back
- **GitHub Actions `pages.yml`**: `main` への push で `site/build_site.py` を叩いて GitHub Pages に配布
- **Render (`render.yaml`)**: `main` push で `pip install` → `build_site.py` → `site/dist/` を静的配信
- **Supabase**: `ai_watch_articles` テーブルに差分保存（`SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` が env にあれば書き込む）

## コマンド

```bash
python run.py                 # 日次ダイジェスト (直近24h の diff モード)
python run.py --full          # 週次フル版も生成
python run.py --no-summary    # Claude API をスキップ
python site/build_site.py     # サイトだけ再ビルド
uvicorn admin.server:app --port 4001 --reload   # 管理画面
```

## 守るべきルール

- ソース追加は `config/sources.yaml` に 1 ブロック足すだけ。コードは触らない
- RSS 以外（X API・スクレイピング等）を増やすときは `core/collector.py` の `DISPATCH` に関数を追加する
- 日付入りの出力ファイルは上書きしない（NotebookLM 側がソースとして保持しているため）
- `data/history.db` は commit back される前提。`.gitignore` で除外しない
- 文字化け防止: グッぼる本店など EUC-JP ソースを HTML で取り込む場合は親 `CLAUDE.md` のルールに従って `iconv` 変換層を挟む

## 管理画面について

`admin/server.py` は FastAPI ベースの**ローカル専用**管理 UI。
GitHub Pages / Render (static) は静的ホスティングなので、公開ナビから `/admin` リンクは外してある。
ローカルで触るときは `uvicorn admin.server:app --port 4001 --reload` を起動して `http://localhost:4001/admin` にアクセスする。
運用（記事収集の実行）は基本 GitHub Actions 任せで、管理画面は手元確認用。
