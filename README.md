# AIハブ — AI Hub

「自分のAIをひとつに集める場所」をテーマにした個人ポートフォリオ兼マイページ。
作品（アプリ集）・講師紹介・講習資料を見せる**フロント面**と、AI/SNS関連情報をRSSから自動収集・要約してNotebookLMに流し込む**バックエンドのパイプライン**を1つのサイトに同居させている。

## 特徴

- **ポートフォリオ統合**: 作品カードは [config/portfolio.yaml](config/portfolio.yaml) に1ブロック追加するだけ
- **ソース追加は設定1つ**: `config/sources.yaml` に URL を書き足すだけで RSS 収集対象が増える
- **差分検出**: SQLite(`data/history.db`) で過去取得を全保存し、前回以降の新着を自動でハイライト
- **NotebookLM 対応**: `outputs/notebooklm/latest.md` と `outputs/full/*.txt` をそのまま NotebookLM に放り込める
- **定期実行**: GitHub Actions (`.github/workflows/daily.yml`) で毎朝 JST 07:00 自動実行
- **拡張容易**: `core/collector.py` の `DISPATCH` に関数を追加すれば X API / スクレイピング等の新タイプに対応可能

## セットアップ

```bash
cd ai-hub
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
python site/build_site.py     # 静的サイトだけ再ビルド (speaker.html / lectures/ 含む)
```

## 管理画面（ローカル専用）

GitHub Pages は静的ホスティングなので、`/admin` はローカル起動時のみ利用できる。

```bash
uvicorn admin.server:app --host 127.0.0.1 --port 3010 --reload
# → http://localhost:3010/admin
```

管理画面から巡回を走らせた場合は `site/dist/` も再ビルドされるが、Pages への反映は `git push` が必要。

## 講師紹介・講習資料の編集

- 講師紹介ページ: [content/speaker.md](content/speaker.md) を編集して `python site/build_site.py`
- 講習資料を追加: `content/lectures/YYYY-MM-slug.md` を作成
- 公開URL: `https://goodbouldering-collab.github.io/ai-hub/speaker.html`

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
