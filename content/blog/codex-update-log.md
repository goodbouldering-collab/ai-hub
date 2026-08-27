---
title: "今日のAIニュースと更新情報"
date: "2026-08-21"
date_modified: "2026-08-27"
content_series: codex-update-log
source_period: "August 24–28, 2026"
source_fingerprint: "560b6e910da6a867d526e0e1477012087225232d3120df1246de90bdbd56a748"
source_release_tag: "rust-v0.150.0"
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
<!-- source-fingerprint: 560b6e910da6a867d526e0e1477012087225232d3120df1246de90bdbd56a748 -->
<section class="codex-update-guide" aria-labelledby="codex-update-guide-title">
<div class="codex-update-guide__header">
<p class="codex-update-guide__eyebrow">今日のAIニュースを読んだら</p>
<h2 id="codex-update-guide-title" class="codex-update-guide__title">今日のCodex新機能と活用術</h2>
<p class="codex-update-guide__lead">複数のCodex作業をつないで進めたい時や、長い回答から必要な部分だけ持ち帰りたい時へ。ターミナルでの作業整理と共有がしやすくなりました。</p>
<p class="codex-update-guide__date"><time datetime="2026-08-28">公式情報の確認期間：August 24–28, 2026</time></p>
</div>
</section>

### 今回の要点

- 別のCodex作業を参照し、ターミナルから作成やメッセージ送信ができます。
- 回答全体、コード、引用のどれをコピーするか選べます。
- 作業名とリンク表示が整い、あとから見返しやすくなりました。

<section class="codex-feature-card update-card" data-update-kind="codex" data-update-index="1" aria-labelledby="codex-feature-1-title">
<header class="update-card__header">
<span class="update-card__rank" aria-hidden="true">1</span>
<div class="update-card__heading">
<p class="update-card__eyebrow">CODEX</p>
<h2 id="codex-feature-1-title" class="codex-feature-title"><span class="visually-hidden">1. </span>別の作業とつなぐ</h2>
</div></header>
<div class="update-card__body">
<p class="update-card__summary">たとえば、地域イベントの告知ページと申込フォームを別々のCodex作業で進める時は、別の作業を参照して内容を確認し、必要なメッセージを送れます。担当を分けたまま前提をつなげられます。</p>
<p class="update-card__context">Codex CLI 0.150.0で追加されました。ターミナルから別のCodex作業を参照、作成、確認、メッセージ送信できます。</p>
<p class="update-card__source"><a href="https://github.com/openai/codex/releases/tag/rust-v0.150.0" target="_blank" rel="noopener">公式情報</a></p>
</div></section>

<section class="codex-feature-card update-card" data-update-kind="codex" data-update-index="2" aria-labelledby="codex-feature-2-title">
<header class="update-card__header">
<span class="update-card__rank" aria-hidden="true">2</span>
<div class="update-card__heading">
<p class="update-card__eyebrow">CODEX</p>
<h2 id="codex-feature-2-title" class="codex-feature-title"><span class="visually-hidden">2. </span>必要な部分だけコピーする<span class="codex-feature-command"><code>/copy</code></span></h2>
</div></header>
<div class="update-card__body">
<p class="update-card__summary">たとえば、AI講座の資料づくりで長い回答からコード例だけを共有したい時は、コピー対象の一覧からコードブロックを選びます。回答全体を貼り直さず、必要な部分だけ渡せます。</p>
<p class="update-card__context">Codex CLI 0.150.0で追加されました。回答全体、個別のコードブロック、引用から対象を選べます。</p>
<p class="update-card__source"><a href="https://github.com/openai/codex/releases/tag/rust-v0.150.0" target="_blank" rel="noopener">公式情報</a></p>
</div></section>

<section class="codex-feature-card update-card" data-update-kind="codex" data-update-index="3" aria-labelledby="codex-feature-3-title">
<header class="update-card__header">
<span class="update-card__rank" aria-hidden="true">3</span>
<div class="update-card__heading">
<p class="update-card__eyebrow">CODEX</p>
<h2 id="codex-feature-3-title" class="codex-feature-title"><span class="visually-hidden">3. </span>作業名を整える<span class="codex-feature-command"><code>/rename</code></span></h2>
</div></header>
<div class="update-card__body">
<p class="update-card__summary">たとえば、複数の学校向け資料を並行して直し、後でどの作業か分からなくなった時は、会話内容から出る名前の候補を確認して編集します。作業一覧を探しやすい名前に整えられます。</p>
<p class="update-card__context">Codex CLI 0.150.0で、名前のない作業への自動タイトルと、会話に基づく編集可能なタイトル候補が追加されました。</p>
<p class="update-card__source"><a href="https://github.com/openai/codex/releases/tag/rust-v0.150.0" target="_blank" rel="noopener">公式情報</a></p>
</div></section>

<section class="codex-feature-card update-card" data-update-kind="codex" data-update-index="4" aria-labelledby="codex-feature-4-title">
<header class="update-card__header">
<span class="update-card__rank" aria-hidden="true">4</span>
<div class="update-card__heading">
<p class="update-card__eyebrow">CODEX</p>
<h2 id="codex-feature-4-title" class="codex-feature-title"><span class="visually-hidden">4. </span>リンク先をすぐ開く</h2>
</div></header>
<div class="update-card__body">
<p class="update-card__summary">たとえば、調査結果に並んだ公式資料を順番に確認したい時は、対応するターミナルで表示されたリンク名を選びます。長いURLをコピーしてブラウザへ貼り直す手間を減らせます。</p>
<p class="update-card__context">Codex CLI 0.150.0で追加されました。対応するターミナルではリンク名をクリックでき、それ以外ではURLが表示されます。</p>
<p class="update-card__source"><a href="https://github.com/openai/codex/releases/tag/rust-v0.150.0" target="_blank" rel="noopener">公式情報</a></p>
</div></section>

Codex CLIの最新安定版は`rust-v0.150.0`です。

[Codex CLI 0.150.0公式リリース](https://github.com/openai/codex/releases/tag/rust-v0.150.0)

## 公式情報

- [ChatGPT & Codex公式変更履歴](https://learn.chatgpt.com/docs/changelog)
- [仕事を変える主な新機能](https://learn.chatgpt.com/docs/whats-new)
<!-- CODEX_UPDATE_CURRENT:END -->

## 過去のアップデート要約

<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->
<!-- source-fingerprint: 2af26099642a03264bdf4e2653631421305573d4e92be0ff43d492c0b381d6b6 -->
### 2026年8月26日｜ブラウザ連携とイベント起動

複数ブラウザ、WebMCP、クラウドブラウザのログイン、Gmail・Slack・GitHubのイベントを合図にした作業開始が紹介されました。

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
