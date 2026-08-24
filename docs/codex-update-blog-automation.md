# Codexアップデート記事の自動更新

固定記事 `content/blog/codex-update-log.md` に、毎日のAIニュース10件と、OpenAI公式の変更時だけ更新するCodex解説をまとめる仕組みです。記事URLと初回公開日は変えません。

## 3本のフック

| フック | 時刻 | 更新条件 | 記事で変わる場所 |
|---|---:|---|---|
| GitHubニュース収集 | 毎日 JST 07:00 | 直近48時間の公開RSSを収集 | AI Watchの収集データ |
| GitHub Codex公式監視 | 毎日 JST 07:40 | 公式週次情報または安定版CLIのfingerprintが変わった時だけ | Codex解説、`date_modified`、過去要約 |
| Codex日次編集 | 毎日 JST 08:10 | 有効なニュース10件がそろった時。Codex本文は公式差分がある時だけ | 記事上部の「今日のAIニュース10」と、必要時だけCodex解説 |

GitHub Actionsの共通concurrency group `ai-hub-content-publish` で2本のActionを直列化します。Codex日次編集はアプリのローカル定期タスク `AI相談 毎朝AIニュース10・Codex更新監視`（ID: `ai-ai-10-codex`）です。いずれも外部サービスから通知を受けるイベントWebhookではなく、公式情報を定期確認するポーリング方式です。ローカル定期タスクはPCとCodexアプリが動作している時に実行されます。

## 毎日のAIニュース10

- 主更新: Codexアプリのローカル定期タスク（毎日 JST 08:10）
- 予備収集: `.github/workflows/daily.yml`（毎日 JST 07:00、外部AI APIを呼ばず公開RSSだけを保存）
- 取得範囲: 直近48時間（休日などでも10件を確保しやすくするため）
- 取得元: OpenAI Codex公式安定版リリース、主要AI企業・技術メディア、日本語AI媒体（alpha・beta・rc版は除外）
- 選定: 新規性・影響・具体性に、日本との関係、Codexとの関係、情報元の偏り防止を加点
- 表現: 各ニュースを「わかりやすく」「たとえば」の2文で説明
- 公開データ: `content/daily-ai-news.json`

要約失敗、URL不正、重複などを除外し、次点候補から補います。有効な10件がそろわなければファイルを置換せず、前回の正常版を本番に残します。AIが実測の検索数やSNS反応を取得しているわけではないため、「日本で流行中」とは断定せず、日本の学校・仕事・暮らしとの関係が強い順として扱います。

## Codex公式監視

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

固定slug、初回公開日、シリーズ名、ヒーロー画像は自動更新では変更しません。画像は `site/static/img/blog-codex-update-log-hero-20260822.png` を利用します。

## 安全策

- HTTPSのOpenAI公式ドキュメントとOpenAI公式GitHubリリースだけを取得
- 転送先、Content-Type、1MB上限を検証
- AIが返したURLは、取得した公式本文に実在するものだけ許可
- 追加コマンドは、選択した根拠原文のインラインコードと完全一致する場合だけ表示
- 利用ストーリーの「確認できること」は自由生成せず、検証済みコマンドまたは公式掲載の事実から定型生成
- 使い方やストーリー本文に現れる全コマンドを、検証済みコマンド一覧と完全一致で照合
- 保存済み期間より古い公式データへの巻き戻しを拒否
- AIの自由文にMarkdownリンク、HTMLコメント、記事制御マーカーを許可しない
- 根拠URLと原文を個別検証できない「その他の更新」は自動生成しない
- 週次期間とCLI安定版の巻き戻しを拒否し、年をまたぐ週次期間にも対応
- マーカー欠落、解析失敗、API失敗時は元記事を変更しない
- 一時ファイルを検証後、原子的に置換
- Workflowがcommitするのは固定記事だけ。画像や生成済みHTMLは自動commitしない
- mainへpush後、Vercel本番に同じfingerprintが出るまで確認
- 日次ニュースは10件すべてを検証してから原子的に置換し、途中結果を公開しない
- 1情報元は原則2件までにし、特定メディアだけで上位を埋めない

## 手動確認

```powershell
python scripts/update_codex_update_log.py
python -m unittest tests.test_codex_update_log_updater tests.test_codex_update_production_verifier tests.test_blog_freshness
$env:AIWATCH_PORTFOLIO_NO_FETCH = "1"
python site/build_site.py
```

GitHub Actionsの「Update Codex evergreen blog」から手動実行もできます。
