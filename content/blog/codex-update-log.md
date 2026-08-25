---
title: "今日のAIニュースと新機能活用術"
date: "2026-08-21"
date_modified: "2026-08-25"
content_series: codex-update-log
source_period: "August 17–21, 2026"
source_fingerprint: "b3cc9f4347cd95104d81f462b4aacfaf044a35d70d523e8df6b6814f0a993774"
source_release_tag: "rust-v0.149.0"
image: "/img/blog-codex-update-log-hero-20260822.png"
image_alt: "毎日のAIニュース10件とCodexの変化だけを選び出す和紙のカードと光のプリズム"
hero_image: true
authorship_note: "※内容は運営者が考え、AIで整えています。"
summary: "AIニュース10件とCodexの新機能を、仕事で使う場面からわかりやすく読む常時更新ページです。"
audience: "AIを仕事、学び、制作に役立てたい人"
problem: "更新内容を読んでも、何が便利になり、どう使うのか分かりにくい"
action: "使えそうな機能を1つ試す"
---

<!-- CODEX_UPDATE_CURRENT:BEGIN -->
<!-- source-fingerprint: b3cc9f4347cd95104d81f462b4aacfaf044a35d70d523e8df6b6814f0a993774 -->
<section class="codex-update-guide" aria-labelledby="codex-update-guide-title">
<div class="codex-update-guide__header">
<p class="codex-update-guide__eyebrow">今日のAIニュースを読んだら</p>
<h2 id="codex-update-guide-title" class="codex-update-guide__title">今日のCodex新機能と活用術</h2>
<p class="codex-update-guide__lead">新機能の名前だけでは、仕事がどう変わるのか想像しにくいものです。たとえば、作業の途中で「スマホ表示も確認して」と頼みたい時や、変更の経緯を相手に見せたい時から読めるようにしました。</p>
<p class="codex-update-guide__date"><time datetime="2026-08-21">公式情報の確認期間：August 17–21, 2026</time></p>
</div>
</section>

### 今回の要点

- 作業の経緯を、読み取り専用リンクで相手に見せられます。
- いくつもの仕事を一覧で管理し、途中でも追加のお願いを送れます。
- 困った時は診断結果をまとめ、相談しやすい情報にできます。

## 1. 途中経過を、相手と一緒に確認する｜`/share`

お店のページ修正を公開前に担当者へ見せたい時は、macOS版ChatGPTで対象の会話を開き、「Share」または`/share`を選びます。パソコンやプロジェクトの権限を渡さず、頼んだ内容と変更の流れを読み取り専用リンクで確認してもらえます。

全Codexプランが対象です。共有後の会話は自動反映されません。共有前には、機密情報や個人情報が残っていないかを確認してください。

[公式情報](https://learn.chatgpt.com/docs/use-chatgpt#share-a-read-only-snapshot-of-a-codex-thread)

## 2. いくつもの仕事を、迷わず開き直す｜`codex agents`

イベント案内、講座資料、SNS投稿などの仕事が増えて続きを探しにくい時は、ターミナルで`codex agents`を実行します。仕事の一覧から検索して続きを開き、不要な仕事は名前変更や停止ができます。

Codex CLI 0.149.0以降で使えます。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## 3. 頼み忘れを、作業中に追加する｜`codex queue`

サイトの公開確認中にiPhone幅の確認を頼み忘れた時は、`codex queue`で進行中の会話へ追加のお願いを送ります。最初からやり直さず、動いている仕事へ確認項目を足せます。

Codex CLI 0.149.0以降で使えます。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## 4. 困った時に、状況を伝えやすくする｜`codex doctor`

共有のパソコンでCodexにつながらない時は、ターミナルで`codex doctor --summary`を実行します。設定やネットワークの状態がまとまって表示されるので、その内容を詳しい人へ見せれば、どこを確認すればよいか伝えやすくなります。

Codex CLI 0.149.0以降で使えます。診断結果を共有する前に、秘密情報がないか確認してください。

[公式情報](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## そのほかの更新

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
