---
title: "Codexアップデート｜新機能とすぐ使える使い方【常時更新】"
date: "2026-08-21"
date_modified: "2026-08-21"
content_series: codex-update-log
source_period: "August 17–21, 2026"
source_fingerprint: "b3cc9f4347cd95104d81f462b4aacfaf044a35d70d523e8df6b6814f0a993774"
source_release_tag: "rust-v0.149.0"
image: "/img/blog-codex-update-log-hero-20260821.webp"
image_alt: "Codexの更新を仕事へつなぐ知的な観測装置と三つの機能モジュール"
hero_image: true
authorship_note: "※内容は運営者が考え、AIで整えています。"
summary: "Codexアップデートから、多くの人に役立つ新機能と使い方だけを選んで追記する常時更新ページです。"
audience: "Codexを仕事、教育、地域活動、制作に使う人"
problem: "更新内容を読んでも、何が便利になり、どう使うのか分かりにくい"
action: "使えそうな機能を1つ試す"
---

<!-- CODEX_UPDATE_CURRENT:BEGIN -->
<!-- source-fingerprint: b3cc9f4347cd95104d81f462b4aacfaf044a35d70d523e8df6b6814f0a993774 -->
Codexアップデートで、作業の「共有・並行・追加指示」が一気に実用的になりました。

**公式情報の確認期間：August 17–21, 2026**

### 今回の要点

- 作業内容を読み取り専用リンクで共有できます。
- 複数の仕事を一覧で管理し、進行中でも追加指示を送れます。
- 困った時は診断結果をまとめ、原因を伝えやすくなりました。

## 1. 作業内容をリンクで共有

ローカルCodexの作業を、読み取り専用のスナップショットとして共有できます。

**使い方：** macOS版ChatGPTで対象スレッドを開き、「Share」または`/share`を選びます。

**利用例：** サイト修正の内容を、公開前に担当者へ確認してもらう。

全Codexプランが対象です。共有前に、機密情報や個人情報が残っていないか確認してください。

[公式情報](https://learn.chatgpt.com/docs/use-chatgpt#share-a-read-only-snapshot-of-a-codex-thread)

## 2. 複数の作業を一覧で管理

`codex agents`で、タスクの検索・開始・再開・名前変更・停止ができます。

**使い方：** ターミナルで`codex agents`を実行し、一覧から続けたい作業を選びます。

**利用例：** サイト修正、講座資料、SNS原稿を並行し、止まった作業だけを再開する。

Codex CLI 0.149.0以降で使えます。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## 3. 動いている作業へ追加指示

`codex queue`で、既存のローカルまたはリモートの作業へ後から指示を送れます。

**使い方：** 進行中の作業へ追加指示を送りたい時に`codex queue`を使います。

**利用例：** 「iPhone幅と横スクロールも確認して」と途中で加える。

Codex CLI 0.149.0以降で使えます。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## 4. 不具合の原因を診断

`codex doctor`で、設定、認証、ネットワーク、端末の状態をまとめて確認できます。

**使い方：** 接続や起動で困った時に`codex doctor`を実行し、表示された診断結果を確認します。

**利用例：** 学校や施設のネットワークで接続できないとき、原因を絞って管理者へ伝える。

Codex CLI 0.149.0以降で使えます。診断結果を共有する前に、秘密情報がないか確認してください。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## その他の更新

- GitLab連携がベータ公開され、IssueやマージリクエストからCodexへ作業を頼めます。
- ピン留めしたスレッドがデスクトップ版とiOS版で同期されます。
- macOS版ではApple Messagesを検索し、返信案の作成や送信ができます。初期設定では送信前に内容と宛先の承認が必要です。

## 公式情報

- [ChatGPT & Codex公式変更履歴](https://learn.chatgpt.com/docs/changelog)
- [仕事を変える主な新機能](https://learn.chatgpt.com/docs/whats-new)
<!-- CODEX_UPDATE_CURRENT:END -->

## 過去のアップデート要約

<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->
<!-- source-fingerprint: seed-cli-0.148.0 -->
### 2026年8月18日｜CLI 0.148.0

会話のMarkdown出力、作業の分岐、保管と復元に対応。長い作業を再利用しやすくなりました。

<!-- source-fingerprint: seed-cli-0.147.0 -->
### 2026年8月7日｜CLI 0.147.0

Agent Pluginsの導入、会話の整理、CursorやClaudeからの取り込みが使いやすくなりました。
<!-- CODEX_UPDATE_ARCHIVE:END -->
