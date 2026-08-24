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

## 1. 途中経過を、相手と一緒に確認する

ローカルCodexの作業を、読み取り専用のスナップショットとして共有できます。完成した画面だけでなく、頼んだ内容と変更の流れも確認しやすくなります。

<aside class="codex-command-callout" aria-label="追加されたコマンド">
<span class="codex-command-callout__label">追加コマンド</span>
<div class="codex-command-callout__commands"><code>/share</code></div>
</aside>

**使い方：** macOS版ChatGPTで対象の会話を開き、「Share」または`/share`を選びます。

<div class="codex-use-story" role="group" aria-label="利用ストーリー">
<p class="codex-use-story__title">利用ストーリー｜たとえば</p>
<dl>
<dt>こんな時</dt><dd>お店のページ修正を頼んだ後、「何を変えたのか、公開前に見たい」と担当者から言われた。</dd>
<dt>操作</dt><dd>対象の会話で「Share」または<code>/share</code>を選び、共有する範囲を確認してリンクをコピーします。</dd>
<dt>確認できること</dt><dd>相手はリンクを見るだけで、パソコンやプロジェクトの権限を渡さずに、どこまで進んだかを確認できます。</dd>
</dl>
</div>

全Codexプランが対象です。共有後の会話は自動反映されません。共有前には、機密情報や個人情報が残っていないかを確認してください。

[公式情報](https://learn.chatgpt.com/docs/use-chatgpt#share-a-read-only-snapshot-of-a-codex-thread)

## 2. いくつもの仕事を、迷わず開き直す

`codex agents`で、タスクの検索・開始・オープン・名前変更・停止ができます。作業が増えても、前に頼んだ仕事を探し直す時間を減らせます。

<aside class="codex-command-callout" aria-label="追加されたコマンド">
<span class="codex-command-callout__label">追加コマンド</span>
<div class="codex-command-callout__commands"><code>codex agents</code></div>
</aside>

**使い方：** ターミナルで`codex agents`を実行し、対話型ダッシュボードを開きます。

<div class="codex-use-story" role="group" aria-label="利用ストーリー">
<p class="codex-use-story__title">利用ストーリー｜たとえば</p>
<dl>
<dt>こんな時</dt><dd>イベント案内、講座資料、SNS投稿の作業が増え、続きの仕事を探すだけで時間がかかる。</dd>
<dt>操作</dt><dd>ターミナルで<code>codex agents</code>を実行し、検索して続けたい仕事を開きます。不要な仕事は名前を変えるか停止します。</dd>
<dt>確認できること</dt><dd>対話型の一覧で、今どの仕事があるかを見渡し、次に開く仕事を選べます。</dd>
</dl>
</div>

Codex CLI 0.149.0以降で使えます。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## 3. 頼み忘れを、作業中に追加する

`codex queue`で、既存のローカルまたはリモートの作業へ後から指示を送れます。最初からやり直さず、気づいたことを追加できます。

<aside class="codex-command-callout" aria-label="追加されたコマンド">
<span class="codex-command-callout__label">追加コマンド</span>
<div class="codex-command-callout__commands"><code>codex queue</code></div>
</aside>

**使い方：** 進行中の作業へ追加指示を送りたい時に`codex queue`を使います。

<div class="codex-use-story" role="group" aria-label="利用ストーリー">
<p class="codex-use-story__title">利用ストーリー｜たとえば</p>
<dl>
<dt>こんな時</dt><dd>サイトの公開確認が進んでいる途中で、iPhone幅と横スクロールの確認を頼み忘れたことに気づく。</dd>
<dt>操作</dt><dd><code>codex queue</code>を使い、進行中の会話へ「iPhone幅と横スクロールも確認して」と追加メッセージを送ります。</dd>
<dt>確認できること</dt><dd>進んでいる仕事に、追加のお願いを届けられるため、確認漏れを減らせます。</dd>
</dl>
</div>

Codex CLI 0.149.0以降で使えます。

[公式情報](https://github.com/openai/codex/releases/tag/rust-v0.149.0)

## 4. 困った時に、状況を伝えやすくする

`codex doctor`で、設定、認証、ネットワーク、端末の状態をまとめて確認できます。「動かない」だけで終わらせず、何を確かめたかを伝えやすくなります。

<aside class="codex-command-callout" aria-label="追加されたコマンド">
<span class="codex-command-callout__label">追加コマンド</span>
<div class="codex-command-callout__commands"><code>codex doctor</code></div>
</aside>

**使い方：** 接続や起動で困った時に`codex doctor --summary`を実行し、診断結果の要約を確認します。

<div class="codex-use-story" role="group" aria-label="利用ストーリー">
<p class="codex-use-story__title">利用ストーリー｜たとえば</p>
<dl>
<dt>こんな時</dt><dd>共有のパソコンからCodexへ接続できず、詳しい人に何を伝えればよいか分からない。</dd>
<dt>操作</dt><dd>ターミナルで<code>codex doctor --summary</code>を実行し、表示された診断項目と件数を確認します。</dd>
<dt>確認できること</dt><dd>インストール、設定、認証、端末、ネットワークなどを一度に確認し、相談する時の手がかりにできます。</dd>
</dl>
</div>

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
