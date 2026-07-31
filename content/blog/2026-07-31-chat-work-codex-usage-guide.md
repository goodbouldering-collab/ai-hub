---
title: "朝8時45分、告知はまだ白紙。Codex「1回5〜45クレジット」をムダにしないAIの使い分け"
date: 2026-07-31
role: ブログ / AI活用・Codex使用量
gen_by: 由井辰美 / AI相談
summary: 昼までに地域交流会の告知を完成させたい架空の物語から、Codexの使用量を数字で解説。同じ10万入力＋1万出力でもLuna 4、Terra 10、Sol 20クレジットになる理由と、Chat・Work・Codexの使い分けを紹介します。
image: /img/blog-codex-story-hero-20260731.jpg
image_alt: 朝の事務所で締切時計を見ながらChat・Work・Codexの使い分けを考える地域事業者
audience: AIを仕事に使いたいが、Codexの使用量やモデル選びに不安がある地域事業者、学校・福祉施設の担当者、個人事業主
duration: 6分
goal: 数字と仕事の重さを見ながら、Chatで整理し、Luna・Terraから実作業を始め、難所だけSolを選べる
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
.codex-usage-guide .case-note{margin:1rem 0 1.5rem;padding:.9rem 1rem;border-radius:10px;background:#fff7e7;color:#594618;font-size:.92rem}
.codex-usage-guide .metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.85rem;margin:1.5rem 0 2rem}
.codex-usage-guide .metric{padding:1rem;border:1px solid var(--cu-line);border-radius:15px;background:#fff;box-shadow:0 8px 24px rgba(38,62,146,.08)}
.codex-usage-guide .metric b{display:block;color:var(--cu-indigo);font-size:1.75rem;line-height:1.2}
.codex-usage-guide .metric span{display:block;margin-top:.35rem;color:var(--cu-soft);font-size:.86rem;line-height:1.55}
.codex-usage-guide .bars{margin:1.4rem 0 2rem;padding:1.2rem;border-radius:16px;background:#f7f8ff}
.codex-usage-guide .bar-row{display:grid;grid-template-columns:72px 1fr 70px;gap:.75rem;align-items:center;margin:.8rem 0}
.codex-usage-guide .bar-track{height:18px;overflow:hidden;border-radius:999px;background:#e6e9f7}
.codex-usage-guide .bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--cu-blue),var(--cu-coral))}
.codex-usage-guide .timeline{margin:1.5rem 0 2rem;border-left:4px solid var(--cu-blue)}
.codex-usage-guide .timeline-item{position:relative;margin-left:1rem;padding:.2rem 0 1.25rem 1rem}
.codex-usage-guide .timeline-item:before{position:absolute;left:-1.45rem;top:.42rem;width:.75rem;height:.75rem;border:3px solid #fff;border-radius:50%;background:var(--cu-coral);box-shadow:0 0 0 2px var(--cu-coral);content:""}
.codex-usage-guide .timeline-item strong{display:block;color:var(--cu-indigo)}
.codex-usage-guide .number-box{margin:1.4rem 0 1.8rem;padding:1.25rem 1.35rem;border:1px solid rgba(83,103,217,.3);border-radius:16px;background:#fafaff}
.codex-usage-guide .number-box .big{display:block;color:var(--cu-indigo);font-size:1.55rem;font-weight:900}
.codex-usage-guide .checklist{padding:1.2rem 1.3rem;border-radius:16px;background:#edf8f5}
.codex-usage-guide .checklist li{margin:.35rem 0}
@media(max-width:760px){.codex-usage-guide .metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.codex-usage-guide .guide-figure img{border-radius:12px}.codex-usage-guide .answer,.codex-usage-guide .rule-box,.codex-usage-guide .number-box,.codex-usage-guide .cta{padding:1rem}.codex-usage-guide .bar-row{grid-template-columns:58px 1fr 54px;gap:.55rem}}
</style>

<div class="codex-usage-guide" markdown="1">

<figure class="guide-figure guide-hero">
  <img src="/img/blog-codex-story-hero-20260731.jpg" alt="朝の事務所で締切時計を見ながらChat・Work・Codexの使い分けを考える地域事業者" loading="eager" decoding="async">
  <figcaption>「強いモデルを選べば早く終わる」とは限りません。仕事を分ける順番が、使用量と完成までの時間を変えます。</figcaption>
</figure>

朝8時45分。地域交流会の告知は、まだ白紙です。

正午までに文章を作り、画像を選び、Webサイトへ載せなければいけません。焦った担当者の佐藤さんは、こう考えました。

**「一番強いSolに、全部まとめて頼めば安心だろう」**

過去資料をたくさん渡し、「詳しく調べて、考え方も全部説明して、長い報告書にしてください」と指示しました。立派な回答は返ってきましたが、告知に使うには長すぎます。結局、短く直す作業が残りました。

<div class="case-note">
※佐藤さんは、地域事業者によくある悩みを伝えるための架空の人物です。以下のクレジット数は実測事例ではなく、2026年7月31日時点のOpenAI公式レートを使った比較計算です。
</div>

<div class="answer">
<strong>結論：問題はSolではなく、「相談・実作業・難しい判断」を最初から一つにしたことでした。</strong>
Chatで目的を決め、LunaかTerraで作り、難所だけSolへ渡す。それだけで、仕事も使用量も見通しやすくなります。
</div>

<div class="metric-grid">
  <div class="metric"><b>5〜45</b><span>GPT-5.5の典型的なCodexタスク1件の公式目安。上限と下限で9倍差。</span></div>
  <div class="metric"><b>6倍</b><span>GPT-5.6系では、出力1トークンの単価は入力1トークンの6倍。</span></div>
  <div class="metric"><b>1/10</b><span>キャッシュ済み入力の単価は、通常入力の10分の1。</span></div>
  <div class="metric"><b>5倍</b><span>同じトークン量なら、SolはLunaの5倍。TerraはLunaの2.5倍。</span></div>
</div>

## 朝8時45分、「一番強いSolなら安心」が遠回りの始まりだった

<figure class="guide-figure">
  <img src="/img/blog-codex-story-0845-20260731.jpg" alt="締切が迫る朝の事務所で、大量の資料と長いAI回答を前に困る地域事業者" loading="lazy" decoding="async">
  <figcaption>欲しかったのはA4一枚の告知。でも指示は「全部読んで、全部説明して」になっていました。</figcaption>
</figure>

佐藤さんが欲しかったのは、難しい経営分析ではありません。

- 初めて見る人にも分かる見出し
- 日時と場所
- 参加するメリット
- 申込みボタン

必要なのは、この4つです。

ところが「念のため」と資料を増やし、「途中の考え方も詳しく」と出力を増やしました。Codexの使用量は、画面に最後に出た文章だけでは決まりません。読み込んだ会話やファイル、ツールの結果、生成した文章やコードも影響します。

[OpenAIの公式案内](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)も、使用量は仕事の大きさ・複雑さ・モデル・実行場所で変わり、大きなコードベースや長時間の作業、長いセッションほど多くなると説明しています。

ここで大切なのは「高性能モデルを使わない」ことではありません。**作業に必要な強さを見極めること**です。

## 同じ10万入力＋1万出力でも、Luna 4・Terra 10・Sol 20クレジットになる

<figure class="guide-figure">
  <img src="/img/blog-codex-story-numbers-20260731.jpg" alt="同じ仕事量でもLuna、Terra、Solで必要なエネルギーが段階的に増える様子" loading="lazy" decoding="async">
  <figcaption>同じトークン量でも、選ぶモデルだけで計算上は4・10・20クレジットに分かれます。</figcaption>
</figure>

[Codex公式レート表](https://help.openai.com/en/articles/20001106-codex-rate-card)は、100万トークン当たりのクレジットを次のように示しています。

<div class="simple-table" markdown="1">

| モデル | 入力100万 | キャッシュ済み入力100万 | 出力100万 | Luna比 |
|---|---:|---:|---:|---:|
| **Luna** | 25 | 2.5 | 150 | 1倍 |
| **Terra** | 62.5 | 6.25 | 375 | 2.5倍 |
| **Sol** | 125 | 12.5 | 750 | 5倍 |

</div>

比較しやすいように、佐藤さんの仮想タスクを「入力10万トークン＋出力1万トークン」とします。

<div class="simple-table" markdown="1">

| モデル | 入力分 | 出力分 | 合計 |
|---|---:|---:|---:|
| **Luna** | 25×0.1＝2.5 | 150×0.01＝1.5 | **4クレジット** |
| **Terra** | 62.5×0.1＝6.25 | 375×0.01＝3.75 | **10クレジット** |
| **Sol** | 125×0.1＝12.5 | 750×0.01＝7.5 | **20クレジット** |

</div>

<div class="bars" aria-label="同じトークン量でのモデル別クレジット比較">
  <div class="bar-row"><strong>Luna</strong><div class="bar-track"><div class="bar-fill" style="width:20%"></div></div><b>4</b></div>
  <div class="bar-row"><strong>Terra</strong><div class="bar-track"><div class="bar-fill" style="width:50%"></div></div><b>10</b></div>
  <div class="bar-row"><strong>Sol</strong><div class="bar-track"><div class="bar-fill" style="width:100%"></div></div><b>20</b></div>
</div>

同じトークン量という前提なら、LunaはSolより80％少ない計算です。ただし、モデルを変えれば回答品質や必要なやり直し回数も変わります。**「すべてLunaが正解」ではなく、「軽い仕事を最初からSolへ渡さない」ための比較**です。

OpenAIは、GPT-5.5の典型的なCodexタスクを**5〜45クレジット**と案内しています。たった1件でも9倍の幅があるのは、依頼の長さ、読み込む量、推論、出力量が毎回違うからです。

## 問題はSolではなく順番だった。Chat→Luna→Terra→Solで仕事を軽くする

<figure class="guide-figure">
  <img src="/img/blog-codex-story-workflow-20260731.jpg" alt="朝の相談から告知公開までをChat、Luna、Terra、Solへ段階的に渡す仕事の流れ" loading="lazy" decoding="async">
  <figcaption>最初から全部を一つのモデルへ渡さず、相談・制作・検証・難所に分けます。</figcaption>
</figure>

佐藤さんは、仕事を次の順番へ変えました。

<div class="timeline">
  <div class="timeline-item"><strong>8:45　Chatで3つだけ決める</strong>誰に来てほしいか、何に困っているか、読後に何をしてほしいかを整理します。</div>
  <div class="timeline-item"><strong>9:00　Lunaで1ファイルを作る</strong>見出しと本文を短く作り、対象ファイルだけ直します。検索や軽い修正もここです。</div>
  <div class="timeline-item"><strong>10:00　Terraで複数の整合性を確認する</strong>記事、画像、申込み導線、スマホ表示など、数ファイルにまたがる通常作業を任せます。</div>
  <div class="timeline-item"><strong>難所が出た時だけSolへ上げる</strong>複雑な設計、矛盾した資料の統合、難しい判断だけを切り出します。</div>
</div>

Word、Excel、スライドなどの完成品を作りたいならWorkが便利です。ただし、[OpenAIはWorkがCodexと同じ使用構造](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)であり、対応プランではCodex、Work、ChatGPT for Excelなどが同じエージェント利用枠・クレジットプールを使うと説明しています。

つまり、**CodexからWorkへ移るだけでは節約になりません。** 画面を変える前に、仕事の範囲を小さくする方が先です。

## 出力を5分の1にすると計算上20→14。正午までに終える最後の工夫

<figure class="guide-figure">
  <img src="/img/blog-codex-story-finish-20260731.jpg" alt="長いAI回答を短い完成稿へ絞り込み、正午前に地域交流会の告知を公開する地域事業者" loading="lazy" decoding="async">
  <figcaption>長い説明を集めるより、必要な完成物と確認結果へ絞る方が、公開までの距離は短くなります。</figcaption>
</figure>

GPT-5.6の3モデルは、出力トークンの単価が入力トークンの**6倍**です。

先ほどのSolの例で、入力10万はそのまま、出力だけを1万から2千トークンへ減らすと、

<div class="number-box">
  <span class="big">20クレジット → 14クレジット</span>
  <p>入力12.5＋出力7.5＝20<br>入力12.5＋出力1.5＝14</p>
  <p><strong>出力を5分の1にすると、この前提では合計が30％減ります。</strong></p>
</div>

Lunaでも同じ条件なら、4クレジットから2.8クレジットになります。長い報告が必要な仕事もありますが、告知作成のような仕事なら「最後に変更点と確認結果だけ、5行で報告」と頼めます。

また、公式単価ではキャッシュ済み入力が通常入力の**10分の1**です。ただし、実際にどの入力がキャッシュされるかはタスクごとに異なります。キャッシュを当てにして長い資料を何度も渡すより、必要な資料だけを指定する方が確実です。

物語の佐藤さんが正午までにやったことは、次の4つだけです。

<div class="checklist" markdown="1">

1. 「地域交流会に初参加する人向け」と読者を一人に絞る
2. 告知ページと画像だけを作業対象にする
3. 最終報告を「変更点・確認結果・URL」に絞る
4. 終了後に **Codex Settings → Usage** で実際の消費を見る

</div>

強いAIを我慢するのではありません。**軽い仕事に軽い道具を使い、難しいところへ力を残す。** それが、AIを一度の花火で終わらせず、毎日の仕事で続ける方法です。

### よくある質問

**Q. 最初からTerraを使ってもよいですか？**

はい。複数ファイルやWeb調査を含む通常作業なら、Terraは能力と使用量のバランスを取りやすい選択です。

**Q. Solは使わない方がよいですか？**

いいえ。複雑な設計や大規模修正、複数資料の矛盾整理ではSolが役立ちます。難所だけ切り出すのがポイントです。

**Q. 実際に何クレジット使ったかは、どこで見ますか？**

**Codex Settings → Usage Dashboard** で残量と最近の使用量を確認できます。記事中の計算は比較例であり、最終判断は自分のUsage画面です。

<div class="cta">
<strong>「自分の仕事なら、Chat・Work・Codexをどう分ければいい？」を一緒に整理します。</strong>
<p>AI相談では、彦根の地域事業者、学校、福祉施設、個人事業主の方に、実際の仕事を見ながら、無理なく続けられるAI活用の順番を作ります。</p>
<a href="/#contact">AI相談へ相談する</a>
</div>

### 参考にした公式情報

- [OpenAI：Codexの公式レート表](https://help.openai.com/en/articles/20001106-codex-rate-card)
- [OpenAI：ChatGPT WorkとCodexの使い分け](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)
- [OpenAI：ChatGPTプランでのCodex利用](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [OpenAI：ChatGPTの共通利用枠とUsage Dashboard](https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-free-go-plus-pro)

<p class="note">※画面名、モデル、料金、利用上限は変わることがあります。この記事は2026年7月31日時点のOpenAI公式情報を基準にしています。数値例はレート表からの計算であり、実際のタスク消費を保証するものではありません。</p>

</div>
