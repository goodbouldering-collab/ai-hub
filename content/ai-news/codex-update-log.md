---
title: "今日のAIニュース5とCodex"
date: "2026-08-21"
date_modified: "2026-09-19"
content_series: codex-update-log
source_period: "September 14–18, 2026"
source_fingerprint: "9af1427bd9891c47f1a24793480e2beb4579e25eaf84b6f5da587710bc40bf7d"
source_release_tag: "rust-v0.155.1"
image: "/img/blog-codex-update-log-hero-20260830.png"
image_alt: "巨大な水晶のAI脳を、10個の光るニュースホールドで登り、紙のヤギが見守る和紙の風景"
hero_image: false
show_toc: false
authorship_note: "※内容は運営者が考え、AIで整えています。"
summary: "AIニュース5件とCodexの新機能を、仕事で使う場面からわかりやすく読む常時更新ページです。"
audience: "AIを仕事、学び、制作に役立てたい人"
problem: "更新内容を読んでも、何が便利になり、どう使うのか分かりにくい"
action: "使えそうな機能を1つ試す"
---

<!-- CODEX_UPDATE_CURRENT:BEGIN -->
<!-- source-fingerprint: 9af1427bd9891c47f1a24793480e2beb4579e25eaf84b6f5da587710bc40bf7d -->
<section class="codex-update-guide" aria-labelledby="codex-update-guide-title">
<h2 id="codex-update-guide-title">Codex新機能と活用例</h2>
<p class="codex-update-guide__date">更新日：<time datetime="2026-09-19">2026年9月19日</time></p>
</section>


<section class="codex-feature-card update-card" data-update-kind="codex" data-update-index="1" aria-labelledby="codex-feature-1-title">
<header class="update-card__header">
<span class="update-card__rank" aria-hidden="true">1</span>
<div class="update-card__heading">
<p class="update-card__eyebrow">CODEX</p>
<h2 id="codex-feature-1-title" class="codex-feature-title"><span class="visually-hidden">1. </span>一部の接続先で依頼が拒否される不具合を修正</h2>
</div></header>
<div class="update-card__body">
<p class="update-card__summary">新しいローカルのターミナル会話では、推論の要約表示を初期状態で無効にし、非対応の接続先が依頼を拒否する問題を修正しました。たとえば、地域の申込ページや講座資料を作る依頼が、接続先の非対応機能で止まる場面です。個人情報を含まない短い依頼で動作を確認してから、元の作業へ戻ります。この機能の提供内容がOpenAI公式情報に掲載されていることを確認できます。</p>
<p class="update-card__context">Codex CLI 0.155.1の修正です。明示的に設定した推論の要約表示は尊重され、すべての接続エラーを直す修正ではありません。</p>
<p class="update-card__source"><a href="https://github.com/openai/codex/releases/tag/rust-v0.155.1" target="_blank" rel="noopener">公式情報</a></p>
</div></section>

<section class="codex-feature-card update-card" data-update-kind="codex" data-update-index="2" aria-labelledby="codex-feature-2-title">
<header class="update-card__header">
<span class="update-card__rank" aria-hidden="true">2</span>
<div class="update-card__heading">
<p class="update-card__eyebrow">CODEX</p>
<h2 id="codex-feature-2-title" class="codex-feature-title"><span class="visually-hidden">2. </span>古いモデル指定を確認する</h2>
</div></header>
<div class="update-card__body">
<p class="update-card__summary">GPT-5.5は10月14日にChatGPT・ChatGPT Work・Codexの全プランで提供終了予定です。たとえば、地域の告知や講座資料を作る定期処理に古いモデル指定が残っている場面です。対象設定を一覧にし、切替後の出力を確認します。この機能の提供内容がOpenAI公式情報に掲載されていることを確認できます。</p>
<p class="update-card__context">OpenAI APIは今回の提供終了の対象外です。利用者の設定をこの記事から変更するものではありません。</p>
<p class="update-card__source"><a href="https://learn.chatgpt.com/docs/changelog#codex-2026-09-14-gpt-55-retirement" target="_blank" rel="noopener">公式情報</a></p>
</div></section>

## 公式情報

- [ChatGPT & Codex公式変更履歴](https://learn.chatgpt.com/docs/changelog)
- [仕事を変える主な新機能](https://learn.chatgpt.com/docs/whats-new)
<!-- CODEX_UPDATE_CURRENT:END -->

## 過去のアップデート要約

<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->
<!-- source-fingerprint: 1423ac06585e7ab3c3b0a404bd8d6f56cf172c2d282f02e5b2e00dac9ef10842 -->
### 2026年9月18日確認：CLIの音声対話・進捗表示・常駐サーバー更新

CLI 0.155.0の対応ビルド限定の実験的音声対話、進捗と完了時刻の表示、常駐サーバーの更新を紹介しました。推論の要約表示の初期設定は0.155.1で変更されています。

<!-- source-fingerprint: f9ebce706bf64ec346fd745c6aad39fb04ddf7332c28950f8f7e6c47838a6aa1 -->
### 2026年9月16日確認：GPT-5.5提供終了の予告

10月14日のChatGPT・ChatGPT Work・Codexでの提供終了に備え、保存設定と定期処理のモデル指定を確認する案内を紹介しました。OpenAI APIは対象外で、この時点のCLI安定版は0.154.0でした。

<!-- source-fingerprint: 8469d2c77ed3c8114e6196a2b58087d285f9acec38d850e1ec4c4be003f977c1 -->
### 2026年9月7〜11日：小さな相談窓とWindowsの画面共有

PetsやMiniの操作窓からの相談と、WindowsのAppshotsによる最前面アプリ画面の共有が案内されました。アプリ更新が必要で、利用可否は提供状況と組織設定によります。

<!-- source-fingerprint: feac9c19be20f1dab5e8a6109c437bdbf97f3eb5b000706324603ef6b717bd9e -->
### 2026年9月6日確認：Astraの活用とCLI 0.153.4

Astraによる調査・文書・表計算などの成果物づくりと、アカウントや組織での利用条件を整理しました。CLI 0.153.4のモデル一覧表示修正も紹介しました。

<!-- source-fingerprint: 560b6e910da6a867d526e0e1477012087225232d3120df1246de90bdbd56a748 -->
### 2026年8月24〜28日：作業をつなぎ、回答を持ち帰る

CLI 0.150.0では別の作業の参照・作成・メッセージ送信、コピー対象の選択、作業名やリンク表示が改善されました。

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
