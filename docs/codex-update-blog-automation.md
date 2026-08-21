# Codexアップデート記事の自動更新

固定記事 `content/blog/codex-update-log.md` を、OpenAI公式の週次「What's new」に合わせて更新する仕組みです。記事URLと公開日は変えず、実際に内容が変わった日だけ `date_modified` を更新します。

## 自動実行

- Workflow: `.github/workflows/codex-update-log.yml`
- 実行時刻: 毎日 JST 07:40
- 取得元: `https://learn.chatgpt.com/docs/whats-new.md` とOpenAI公式GitHubの最新安定版リリース
- 編集モデル: `CODEX_BLOG_EDITOR_MODEL`。未指定時は低コストのHaikuを使用
- 必要なSecret: 既存の `ANTHROPIC_API_KEY`

公式週次ブロックと最新安定版CLIリリースを合わせたSHA-256が前回と同じ場合は、AI APIを呼ばず終了します。新しい期間やCLI安定版が出た時だけ、一般の仕事・教育・地域活動・制作に役立つ機能を最大4件に整理します。追加コマンドは専用カードで強調し、利用例は「こんな時・操作・確認できること」の3段ストーリーにします。複数週止まっていた場合は、未処理の週を古い順に処理します。

## 記事の更新範囲

- `CODEX_UPDATE_CURRENT` 内: 最新のフック、要点、機能、追加コマンド、使い方、3段ストーリー
- `CODEX_UPDATE_ARCHIVE` 内: 直前の内容を1〜2文で要約して先頭へ追加
- frontmatter: `date_modified`、`source_period`、`source_fingerprint`、`source_release_tag`だけ更新

固定slug、初回公開日、シリーズ名、ヒーロー画像は変更しません。画像は `site/static/img/blog-codex-update-log-hero-20260821.webp` を継続利用します。

## 安全策

- HTTPSのOpenAI公式ドキュメントとOpenAI公式GitHubリリースだけを取得
- 転送先、Content-Type、1MB上限を検証
- AIが返したURLは、取得した公式本文に実在するものだけ許可
- 追加コマンドは、選択した根拠原文に同じ文字列がある場合だけ表示
- 利用ストーリーは「困りごと・具体的な操作・公式に確認できること」を必須にし、架空の成果や時短率を作らない
- 保存済み期間より古い公式データへの巻き戻しを拒否
- AIの自由文にMarkdownリンク、HTMLコメント、記事制御マーカーを許可しない
- 根拠URLと原文を個別検証できない「その他の更新」は自動生成しない
- 週次期間とCLI安定版の巻き戻しを拒否し、年をまたぐ週次期間にも対応
- マーカー欠落、解析失敗、API失敗時は元記事を変更しない
- 一時ファイルを検証後、原子的に置換
- Workflowがcommitするのは固定記事だけ。画像や生成済みHTMLは自動commitしない
- mainへpush後、Vercel本番に同じfingerprintが出るまで確認

## 手動確認

```powershell
python scripts/update_codex_update_log.py
python -m unittest tests.test_codex_update_log_updater tests.test_codex_update_production_verifier tests.test_blog_freshness
$env:AIWATCH_PORTFOLIO_NO_FETCH = "1"
python site/build_site.py
```

GitHub Actionsの「Update Codex evergreen blog」から手動実行もできます。
