---
title: "Chat・Work・Codexはどう使い分ける？使用量をムダにしない超簡単ガイド"
date: 2026-07-31
role: ブログ / ChatGPT・Codex初心者向け
gen_by: 由井辰美 / AI相談
summary: Chatは相談、Workは完成資料、Codexはファイルやコードの実作業。3つの役割と、Luna・Terra・Solをムダなく選ぶ方法を簡単に説明します。
image: /img/blog-codex-usage-hero-20260731.jpg
image_alt: Chat・Work・Codexの3つの使い道と、作業に合わせたモデル選びを表すイラスト
audience: ChatGPTとCodexの使い分けや使用量が気になる地域事業者、講座受講者、AI初心者
duration: 3分
goal: 相談はChat、成果物はWork、開発はCodexと判断し、軽いモデルから使い始められる
---

<style>
.codex-usage-guide{--cu-blue:#5367d9;--cu-indigo:#3f46a8;--cu-coral:#ef7c68;--cu-ink:#172033;--cu-soft:#526071;--cu-line:#dfe3f4;color:var(--cu-ink)}
.codex-usage-guide *{box-sizing:border-box}
.codex-usage-guide p,.codex-usage-guide li{line-height:1.85}
.codex-usage-guide h2{margin-top:2.8rem}
.codex-usage-guide .guide-figure{width:min(100%,1100px);margin:1rem auto 2rem}
.codex-usage-guide .guide-figure img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border:1px solid var(--cu-line);border-radius:18px;background:#f8f8ff;box-shadow:0 14px 36px rgba(34,44,94,.12)}
.codex-usage-guide .guide-figure figcaption{margin:.7rem auto 0;color:var(--cu-soft);font-size:.9rem;line-height:1.65;text-align:center}
.codex-usage-guide .guide-hero{margin-top:0}
.codex-usage-guide .answer{margin:1.4rem 0 2rem;padding:1.2rem 1.35rem;border-left:6px solid var(--cu-blue);border-radius:10px;background:#f0f2ff}
.codex-usage-guide .answer strong{display:block;margin-bottom:.35rem;color:var(--cu-indigo);font-size:1.18rem}
.codex-usage-guide .simple-table{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.codex-usage-guide table{min-width:620px}
.codex-usage-guide .rule-box{margin:1.2rem 0 1.8rem;padding:1.15rem 1.3rem;border:1px solid rgba(83,103,217,.28);border-radius:14px;background:#fafaff}
.codex-usage-guide .rule-box p:first-child{margin-top:0}
.codex-usage-guide .rule-box p:last-child{margin-bottom:0}
.codex-usage-guide .cta{margin:2.4rem 0 1rem;padding:1.4rem;border-radius:16px;background:#172d57;color:#fff}
.codex-usage-guide .cta strong{display:block;margin-bottom:.45rem;font-size:1.12rem}
.codex-usage-guide .cta p{color:#e7ecff}
.codex-usage-guide .cta a{display:inline-block;margin-top:.3rem;padding:.75rem 1rem;border-radius:999px;background:#fff;color:#263e92;font-weight:800;text-decoration:none}
.codex-usage-guide .note{color:var(--cu-soft);font-size:.9rem}
@media(max-width:640px){.codex-usage-guide .guide-figure img{border-radius:12px}.codex-usage-guide .answer,.codex-usage-guide .rule-box,.codex-usage-guide .cta{padding:1rem}}
</style>

<div class="codex-usage-guide" markdown="1">

<figure class="guide-figure guide-hero">
  <img src="/img/blog-codex-usage-hero-20260731.jpg" alt="Chat・Work・Codexの3つの使い道と、作業の重さに合わせた選択を表すイラスト" loading="eager" decoding="async">
  <figcaption>先に「相談したいのか、実際に作業してほしいのか」を決めると、選ぶ画面とモデルが分かります。</figcaption>
</figure>

「Chat、Work、Codexのどれを使えばいいの？」「使用量をムダにしたくない」と迷う方へ。

覚えることは、たくさんありません。

<div class="answer">
<strong>結論：相談はChat、完成資料はWork、ファイルやコードの実作業はCodexです。</strong>
モデルは軽いものから始めて、難しい時だけ上げます。
</div>

## Chatは相談、WorkとCodexは実作業に使う

<figure class="guide-figure">
  <img src="/img/blog-codex-usage-chat-work-codex-20260731.jpg" alt="Chatで相談し、Workで資料を作り、Codexでコードやファイルを編集する3つの役割" loading="lazy" decoding="async">
  <figcaption>3つの画面は、優劣ではなく役割で使い分けます。</figcaption>
</figure>

まずは、これだけで十分です。

<div class="simple-table" markdown="1">

| やりたいこと | 使う画面 |
|---|---|
| 質問、相談、文章の清書、方針決め | **Chat** |
| 調査して、Word・Excel・スライドなどを完成させる | **Work** |
| ファイル編集、コード、テスト、Git、サイト公開 | **Codex** |

</div>

[OpenAIの公式説明](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)でも、Chatは日常的な会話、Workは長い複合作業と完成品づくり、Codexは開発作業向けと整理されています。

大事なのは、**WorkとCodexは同じエージェント使用枠を共有する**ことです。使用量を節約する目的だけでCodexからWorkへ移っても、基本的な使用構造は変わりません。

## モデルはLunaから始め、必要な時だけTerra・Solへ上げる

<figure class="guide-figure">
  <img src="/img/blog-codex-usage-model-steps-20260731.jpg" alt="軽い作業から難しい作業へ、3段階でモデルを上げるイラスト" loading="lazy" decoding="async">
  <figcaption>小さな作業に大きなモデルを常用せず、必要な時だけ一段上げます。</figcaption>
</figure>

実務では、次の順番で考えると簡単です。

<div class="simple-table" markdown="1">

| モデル | 使う目安 |
|---|---|
| **Luna** | 短い修正、検索、1ファイルの軽い作業 |
| **Terra** | 通常のサイト修正、資料整理、複数ファイルの作業 |
| **Sol** | 難しい設計、大規模修正、複雑な調査や判断 |

</div>

これはAI相談での実務上の目安です。公式のクレジット単価ではLunaが最も軽く、Terra、Solの順に高くなります。料金表は更新されるため、倍率を覚えるより、[最新のCodex公式レート表](https://help.openai.com/en/articles/20001106-codex-rate-card)を見るのが確実です。

<div class="rule-box">
<p><strong>おすすめは「Lunaで開始 → 足りなければTerra → 難所だけSol」です。</strong></p>
<p>最初から毎回Solにする必要はありません。</p>
</div>

## 長い出力と長い会話を減らすと使用量を抑えられる

<figure class="guide-figure">
  <img src="/img/blog-codex-usage-focus-output-20260731.jpg" alt="大量の会話や資料を減らし、必要なフォルダと短い報告に整理するイラスト" loading="lazy" decoding="async">
  <figcaption>読ませる量と書かせる量を絞ると、作業も確認も軽くなります。</figcaption>
</figure>

Codexの使用量は、最後の返事だけで決まりません。読んだ会話、ファイル、ツールの結果、作った文章やコードも影響します。

特に効果があるのは、次の4つです。

1. 相談と方針決めはChatで済ませる
2. Codexには対象フォルダやファイルを指定する
3. 「最後に変更点だけ短く報告」と伝える
4. 目的が変わったら新しいスレッドに分ける

公式レート表でも、出力トークンは入力より高く設定されています。長い報告を毎回求めるより、**必要な修正と確認結果だけ**に絞る方が効率的です。

Ultraなど強い推論やFastモードも、必要な場面だけにします。公式情報では、Ultraは追加エージェントが動く場合があり、Fastは対応モデルでクレジット消費率が高くなると案内されています。

## 迷ったら「Chatで整理、Codexで実行、Usageで確認」

<figure class="guide-figure">
  <img src="/img/blog-codex-usage-workflow-20260731.jpg" alt="Chatで相談し、Codexで実行し、本番を確認してUsageを見る4段階の流れ" loading="lazy" decoding="async">
  <figcaption>相談、実行、確認、使用量チェックを分けると、AIを続けて使いやすくなります。</figcaption>
</figure>

毎日の流れは、これで十分です。

1. **Chat**で「何をするか」を決める
2. **Codex**のLunaかTerraで実作業を始める
3. 難しい部分だけSolへ上げる
4. 終わったら **Codex Settings → Usage** で実際の使用量を見る

WordやExcelなど、コードを触らず完成品を作りたい時は、2をWorkに置き換えます。ただしWorkもCodexと共通のエージェント枠です。

料金や上限はプランと時期で変わります。推測ではなく、自分のUsage画面に出る残量と履歴を最終判断にしてください。

<div class="cta">
<strong>AIを「何となく使う」から「仕事に合わせて使い分ける」へ。</strong>
<p>AI相談では、地域事業者、学校、福祉施設、個人事業主の方に、実際の画面を見ながら無理なく続く使い方を一緒に整理しています。</p>
<a href="/#contact">AI相談へ相談する</a>
</div>

### 参考にした公式情報

- [OpenAI：ChatGPT WorkとCodexの使い分け](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)
- [OpenAI：Codexの公式レート表](https://help.openai.com/en/articles/20001106-codex-rate-card)
- [OpenAI：ChatGPTのクレジットと共通利用枠](https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-free-go-plus-pro-sora)
- [OpenAI：ChatGPTプランでのCodex利用](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)

<p class="note">※画面名、モデル、料金、利用上限は変わることがあります。この記事は2026年7月31日時点のOpenAI公式情報を基準にしています。</p>

</div>
