---
title: "今日のAIニュースと新機能活用術"
date: "2026-08-21"
date_modified: "2026-08-26"
content_series: codex-update-log
source_period: "August 24–28, 2026"
source_fingerprint: "2af26099642a03264bdf4e2653631421305573d4e92be0ff43d492c0b381d6b6"
source_release_tag: "rust-v0.149.1"
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
<!-- source-fingerprint: 2af26099642a03264bdf4e2653631421305573d4e92be0ff43d492c0b381d6b6 -->
<section class="codex-update-guide" aria-labelledby="codex-update-guide-title">
<div class="codex-update-guide__header">
<p class="codex-update-guide__eyebrow">今日のAIニュースを読んだら</p>
<h2 id="codex-update-guide-title" class="codex-update-guide__title">今日のCodex新機能と活用術</h2>
<p class="codex-update-guide__lead">ログインが必要なサイトで調べものをしたい時や、メールやレビューが届いた瞬間に次の作業を始めたい時へ。機能名から入り、困りごと、使い方、確認点の順で読めるようにしました。</p>
<p class="codex-update-guide__date"><time datetime="2026-08-28">公式情報の確認期間：August 24–28, 2026</time></p>
</div>
</section>

### 今回の要点

- Chromeに加え、Edge、Brave、Opera、Vivaldiでも開いているページを使えます。
- Webサイトが用意した操作機能や、クラウドブラウザのログインを仕事へつなげられます。
- Gmail、Slack、GitHubの対応イベントを合図に、予定した作業を始められます。

## 1. `Use your browser`｜普段のブラウザから頼む { .codex-feature-title }

たとえば、地域のお店の管理ページをEdgeで確認していて、内容をチェックリストにしたい時は、デスクトップアプリのChatGPT WorkまたはCodexへ開いているタブを渡します。ログイン済みのページをそのまま使い、別のブラウザへ移し直さず作業を頼めます。

Chrome、Edge、Brave、Opera、Vivaldiが対象です。Operaはブラウザ操作に対応しますが、サイドチャットはありません。利用可否は展開状況とワークスペース設定で異なります。

[公式情報](https://learn.chatgpt.com/docs/chrome-extension)

## 2. `Site tools (WebMCP)`｜サイトの操作を使う { .codex-feature-title }

たとえば、学校の共有文書で直したい場所を探し、担当者へコメントを残す時は、デスクトップアプリ内のブラウザでサイトが提供する操作を使います。文章を目で追って探し直さず、対象箇所の検索やコメント追加を頼めます。

デスクトップアプリを更新し、GPT-5.6 SolまたはGPT-5.6 Terraを使います。GPT-5.6 Luna、Enterprise、Eduでは利用できません。

[公式情報](https://learn.chatgpt.com/docs/webmcp)

## 3. `Web sign-in`｜クラウド作業へ安全にログインする { .codex-feature-title }

たとえば、外出先から予約サイトの情報を確認する必要が出た時は、ChatGPT Workのログイン要求に従い、チャット欄ではなく専用のログイン画面へ認証情報を入力します。手元のブラウザプロファイルをクラウドへ接続せず、必要なサイトの作業を続けられます。

対象プランのWeb、iOS、Androidで利用できます。EnterpriseとEduでは使えず、利用可否は展開状況とワークスペース設定で異なります。

[公式情報](https://learn.chatgpt.com/docs/browser?surface=web#web-sign-in-to-a-website)

## 4. `Event-triggered tasks`｜レビューを合図に動かす { .codex-feature-title }

たとえば、地域団体のサイト修正でGitHubのプルリクエストに指摘が届いた時は、レビュー内容の要約と修正案の準備を自動で始められます。決まった時刻を待たず、Gmail、Slack、GitHubの対応イベントをきっかけに作業を動かせます。

対象プランのChatGPT Webとモバイルで利用できます。先に対応アプリを接続し、要求されるアクセスを承認します。管理ワークスペースでは管理者が利用可否を設定できます。

[公式情報](https://learn.chatgpt.com/docs/changelog#codex-2026-08-25-event-triggers)

Codex CLIの最新安定版は`rust-v0.149.1`です。今回の公式リリース本文は、0.149.0からの差分リンクのみを案内しています。

[Codex CLI 0.149.1公式リリース](https://github.com/openai/codex/releases/tag/rust-v0.149.1)

## 公式情報

- [ChatGPT & Codex公式変更履歴](https://learn.chatgpt.com/docs/changelog)
- [仕事を変える主な新機能](https://learn.chatgpt.com/docs/whats-new)
<!-- CODEX_UPDATE_CURRENT:END -->

## 過去のアップデート要約

<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->
<!-- source-fingerprint: b3cc9f4347cd95104d81f462b4aacfaf044a35d70d523e8df6b6814f0a993774 -->
### 2026年8月25日｜共有と作業管理

読み取り専用共有、複数作業の一覧、作業中の追加依頼、接続診断が加わり、共同確認とトラブル相談がしやすくなりました。

<!-- source-fingerprint: seed-cli-0.148.0 -->
### 2026年8月18日｜CLI 0.148.0

会話のMarkdown出力、作業の分岐、保管と復元に対応。長い作業を再利用しやすくなりました。

<!-- source-fingerprint: seed-cli-0.147.0 -->
### 2026年8月7日｜CLI 0.147.0

Agent Pluginsの導入、会話の整理、CursorやClaudeからの取り込みが使いやすくなりました。
<!-- CODEX_UPDATE_ARCHIVE:END -->
