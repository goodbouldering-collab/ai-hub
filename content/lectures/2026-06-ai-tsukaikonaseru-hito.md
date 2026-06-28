---
title: "AIを使いこなせる人と使いこなせない人の違い｜仕事で差がつく5つの実践"
date: 2026-06-16
role: "SEOブログ / AI活用"
gen_by: "由井 辰美 / AIハブ"
summary: "AIを使いこなせる人と使いこなせない人の違いを、仕事の言語化、材料の渡し方、修正指示、検証、業務導入の観点で解説。ChatGPT、Codex、Claude Code、画像生成を仕事に入れる具体的な手順とセルフチェック付き。"
---

<style>
.content{--ink:#102033;--soft:#405166;--muted:#6b7280;--line:#d8e2ee;--blue:#2563eb;--green:#15803d;--red:#b42318;--amber:#b7791f;--bg:#ffffff;--wash:#f6f9fc;}
.content *{box-sizing:border-box;}
.ai-use-hero{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:center;margin:4px 0 26px;padding:22px;border:1px solid var(--line);border-radius:8px;background:linear-gradient(135deg,#f8fbff 0%,#ffffff 48%,#f2fbf6 100%);}
.ai-use-hero p{font-size:16px;line-height:1.9;color:var(--soft);margin:0 0 12px;}
.ai-use-hero strong{color:var(--ink);}
.ai-use-hero img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:7px;border:1px solid rgba(16,32,51,.12);display:block;}
.ai-use-note{border-left:5px solid var(--blue);background:#f8fbff;border-radius:8px;padding:16px 18px;margin:18px 0 26px;color:var(--soft);line-height:1.9;}
.ai-use-note b{color:var(--ink);}
.ai-use-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:18px 0 28px;}
.ai-use-card{border:1px solid var(--line);border-radius:8px;background:#fff;padding:18px;}
.ai-use-card h3{font-size:20px;line-height:1.4;margin:0 0 10px;color:var(--ink);}
.ai-use-card p,.ai-use-card li{font-size:14.5px;line-height:1.85;color:var(--soft);}
.ai-use-card ul{margin:8px 0 0;padding-left:1.15em;}
.ai-use-card.bad{border-top:5px solid var(--red);}
.ai-use-card.good{border-top:5px solid var(--green);}
.ai-use-badge{display:inline-flex;align-items:center;font-size:12px;font-weight:800;letter-spacing:.04em;color:#fff;border-radius:999px;padding:4px 10px;margin-bottom:8px;background:var(--blue);}
.ai-use-card.bad .ai-use-badge{background:var(--red);}
.ai-use-card.good .ai-use-badge{background:var(--green);}
.ai-use-table{width:100%;border-collapse:collapse;margin:16px 0 28px;border:1px solid var(--line);border-radius:8px;overflow:hidden;font-size:14px;background:#fff;}
.ai-use-table th{background:#172033;color:#fff;text-align:left;padding:12px 14px;}
.ai-use-table td{border-top:1px solid var(--line);padding:12px 14px;vertical-align:top;line-height:1.75;color:var(--soft);}
.ai-use-table td:first-child{font-weight:800;color:var(--ink);white-space:nowrap;}
.ai-use-evidence{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0 28px;}
.ai-use-metric{border:1px solid var(--line);border-radius:8px;background:#fff;padding:16px;border-top:5px solid var(--blue);}
.ai-use-metric b{display:block;font-size:28px;line-height:1.1;color:var(--ink);margin-bottom:8px;}
.ai-use-metric span{display:block;font-size:13.5px;line-height:1.7;color:var(--soft);}
.ai-use-metric small{display:block;margin-top:8px;color:var(--muted);font-size:12px;line-height:1.55;}
.ai-use-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:16px 0 28px;counter-reset:flow;}
.ai-use-step{position:relative;border:1px solid var(--line);border-top:5px solid var(--blue);border-radius:8px;background:#fff;padding:14px;min-height:136px;}
.ai-use-step:before{counter-increment:flow;content:counter(flow);display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--blue);color:#fff;font-weight:900;margin-bottom:10px;}
.ai-use-step b{display:block;font-size:16px;margin-bottom:5px;color:var(--ink);}
.ai-use-step span{display:block;font-size:13.5px;line-height:1.65;color:var(--soft);}
.ai-use-example{background:#101827;color:#e5edf7;border-radius:8px;padding:18px 20px;margin:14px 0 28px;line-height:1.8;font-size:14px;white-space:pre-wrap;}
.ai-use-check{list-style:none;margin:16px 0 28px;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;}
.ai-use-check li{border:1px solid var(--line);border-radius:8px;padding:12px 13px 12px 38px;position:relative;background:#fff;color:var(--soft);line-height:1.65;font-size:14px;}
.ai-use-check li:before{content:"";position:absolute;left:13px;top:16px;width:14px;height:14px;border:2px solid var(--blue);border-radius:3px;background:#f8fbff;}
.ai-use-cta{background:linear-gradient(135deg,#172033,#2458d4);color:#fff;border-radius:8px;padding:22px;margin:24px 0 30px;}
.ai-use-cta h2,.ai-use-cta h3{color:#fff;margin-top:0;}
.ai-use-cta p{color:rgba(255,255,255,.92);line-height:1.85;}
.ai-use-cta a{display:inline-flex;align-items:center;justify-content:center;margin:6px 8px 0 0;padding:10px 14px;border-radius:7px;background:#fff;color:#172033;text-decoration:none;font-weight:800;}
.ai-use-roadmap{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:14px 0 28px;}
.ai-use-roadmap .ai-use-card{border-top:5px solid var(--amber);}
.ai-use-faq details{border:1px solid var(--line);border-radius:8px;background:#fff;padding:14px 16px;margin:10px 0;}
.ai-use-faq summary{cursor:pointer;font-weight:800;color:var(--ink);}
.ai-use-faq p{color:var(--soft);line-height:1.8;margin:10px 0 0;}
.ai-use-sources{font-size:13px;color:var(--muted);line-height:1.75;}
@media(max-width:900px){.ai-use-hero,.ai-use-grid,.ai-use-evidence,.ai-use-flow,.ai-use-check,.ai-use-roadmap{grid-template-columns:1fr}.ai-use-table td:first-child{white-space:normal}.ai-use-hero{padding:18px}.ai-use-flow{gap:12px}}
</style>

<div class="ai-use-hero">
<div>
<p><strong>結論から言うと、AIを使いこなせる人は「プロンプトが上手い人」ではありません。</strong></p>
<p>成果が出る人は、自分の仕事を分解して、AIに渡せる形まで具体化できる人です。逆に成果が出ない人は、「AIで何かしたい」と言いながら、何を変えたいのか、どの数字を見れば成功なのか、誰の課題を解くのかが曖昧なままです。</p>
<p>AIは目的を作る道具ではありません。目的を達成するために、調査、文章、画像、コード、資料、改善案を高速に出す道具です。</p>
</div>
<img src="../img/hero-codex-claude-imagegen-20260616.png" alt="Codex、Claude Code、画像生成を使ってAI活用を仕事に取り入れるイメージ" loading="eager" decoding="async">
</div>

<div class="ai-use-note">
<b>この記事の対象:</b> ChatGPTや生成AIを仕事で使いたいが、何から始めればいいかわからない個人事業主、中小企業、店舗運営者、広報・事務・制作担当者。滋賀・彦根でAI相談やAI講習を検討している方にも向けて書いています。
</div>

## AIを使いこなせる人と使いこなせない人の違い

<div class="ai-use-grid" role="img" aria-label="AIを使いこなせない人と使いこなせる人の違いを比較した図解">
<div class="ai-use-card bad">
<span class="ai-use-badge">使いこなせない人</span>
<h3>AIに「何かいい感じに」と頼む</h3>
<ul>
<li>売上を増やしたい、集客したい、効率化したい、で止まる</li>
<li>材料を渡さず、AIの一般論だけを受け取る</li>
<li>1回目の回答を見て「使えない」と判断する</li>
<li>事実確認、数字確認、権利確認をしない</li>
<li>出た文章を仕事の流れに戻せない</li>
</ul>
</div>
<div class="ai-use-card good">
<span class="ai-use-badge">使いこなせる人</span>
<h3>AIに「この結果に近づけて」と頼む</h3>
<ul>
<li>月商100万円を150万円にしたい、問い合わせを20件から40件にしたい、と数字で話す</li>
<li>商品情報、顧客像、過去投稿、写真、表、URL、コードを渡す</li>
<li>回答を見て、短く、具体的に、別案で、と修正する</li>
<li>人間が確認する箇所を決めている</li>
<li>SNS投稿、見積、LP、FAQ、業務手順に組み込む</li>
</ul>
</div>
</div>

「AIで何ができますか」と聞くより、「この作業を何分短縮できますか」「このページの問い合わせ率を上げるには何を直しますか」と聞くほうが、AIは力を発揮します。

例えば、次のように変えるだけで回答の質は大きく変わります。

<table class="ai-use-table">
<thead><tr><th>曖昧な依頼</th><th>成果につながる依頼</th></tr></thead>
<tbody>
<tr><td>売上を増やしたい</td><td>月商100万円のECで、リピート購入を増やして150万円に近づけたい。商品ページ、同梱チラシ、LINE配信の改善案を出して。</td></tr>
<tr><td>集客したい</td><td>整体院の問い合わせを月20件から40件にしたい。Google検索、Instagram、既存客紹介の3つに分けて施策を出して。</td></tr>
<tr><td>業務効率化したい</td><td>見積作成に毎回30分かかっている。入力項目を整理して、5分で作れるテンプレと確認チェックリストを作って。</td></tr>
<tr><td>ホームページを作りたい</td><td>彦根の小規模店舗向けに、スマホで予約まで進める1ページLPを作りたい。写真、料金、よくある質問、CTAを入れて。</td></tr>
</tbody>
</table>

## 2026年のAI活用は「試す」だけでは足りない

生成AIはすでに珍しい道具ではありません。McKinseyの2025年調査では、回答者の88%が少なくとも1つの業務機能でAIを定期利用していると報告しています。一方で、全社的なスケールまで進んでいる企業は約3分の1にとどまり、AIが企業全体のEBITに影響していると答えた割合も39%でした。

つまり、AIを触っている人は多い。しかし、仕事の成果に変えられている人はまだ少ない。

差が出る理由は、ツールの知識だけではありません。McKinseyは、AIで高い成果を出す組織ほど、既存業務をそのままAI化するのではなく、ワークフロー自体を作り直していると示しています。個人でも同じです。ChatGPT、Codex、Claude Code、Cursor、画像生成ツールを入れても、仕事の流れが曖昧なままでは成果は出ません。

AI時代の価値は「作れること」から「何を、なぜ、どの順番で作るか」に移っています。

## 調査で見えた「AIで成果が出る条件」

今回の記事では、検索意図だけでなく、Microsoft、McKinsey、RAND、BCG、Stack Overflow、GitHub Copilot、METRなどの公開調査も確認しました。数字を見ると、AI活用は「使うか、使わないか」だけでは語れません。

<div class="ai-use-evidence" role="img" aria-label="AI活用に関する主要調査データの要約">
<div class="ai-use-metric"><b>75%</b><span>Microsoft / LinkedIn 2024では、知識労働者の75%が仕事でAIを使っていると報告。</span><small>ただしベンダー調査なので、導入実感の参考として扱う。</small></div>
<div class="ai-use-metric"><b>13.8%</b><span>顧客サポート5,172人の研究では、AI支援により1時間あたりの解決件数が約13.8%増加。</span><small>効果が大きかったのは経験の浅い層。全職種にそのまま一般化しない。</small></div>
<div class="ai-use-metric"><b>19%</b><span>METRの2025年実験では、熟練OSS開発者がAIを使った場合、完了時間が19%増えた。</span><small>大規模な既存コード、熟練者、当時のツール条件での結果。</small></div>
</div>

BCGのコンサルタント実験では、AIが得意な範囲のタスクでは完了数、速度、品質が上がる一方、AIの能力外のタスクでは正答率が落ちました。GitHub Copilotの実験では、限定されたJavaScript実装タスクで作業が速くなった一方、Stack Overflowの2025年調査では、多くの開発者がAIツールを使いながらも、出力精度への不信を持っています。

ここから言えることは一つです。AIを使いこなせる人は、AIに丸投げしていません。AIが得意な作業を選び、出力を検証し、何度も修正し、最後に仕事の流れへ戻しています。

RANDの調査でも、AI/MLプロジェクトの失敗要因として、解くべき問題の誤解、データ不足、技術先行、インフラ不足、AIに不向きな課題設定が挙げられています。これは大企業だけの話ではありません。小さな店舗や個人事業でも、「何をAIに任せるか」が曖昧なままでは、時間だけが過ぎます。

## AIを使いこなす人の5つの実践

### 1. 目的を数字で言う

「もっと良くしたい」ではAIも人間も動けません。

最初に書くべきなのは、理想論ではなく現在地と到達点です。

<div class="ai-use-example">悪い例:
Instagramを伸ばしたいです。いい投稿を考えてください。

良い例:
現在フォロワー1,200人、月の問い合わせは8件です。
3か月で問い合わせを月15件にしたいです。
ターゲットは彦根周辺の30代女性で、肩こり・腰痛に悩む人です。
投稿テーマを10本、保存されやすい構成で出してください。</div>

AIは「目的地」と「制約」があるほど、実務に近い答えを出します。

### 2. 材料を渡す

AIが出す一般論に不満がある場合、多くは材料不足です。

商品名、価格、客層、過去の反応、競合URL、写真、既存文章、FAQ、Excel、コード、社内ルール。こうした材料が入るほど、回答は自分の仕事に近づきます。

ホームページ改善なら、ページURL、現状の悩み、問い合わせ導線、料金、強み、写真の有無を渡す。SNS投稿なら、過去投稿、反応が良かった投稿、売りたい商品、今月のイベントを渡す。コード修正なら、該当ファイル、エラー文、再現手順、期待する動作を渡す。

AI活用が上手い人は、AIに魔法を期待しているのではなく、判断に必要な材料を渡しています。

### 3. 出力形式を決める

AIに「考えて」と頼むと、長い文章が返ってきます。仕事に使うなら、最初から形式を指定します。

<div class="ai-use-flow" role="img" aria-label="AIへの依頼を目的、材料、条件、出力形式、修正の5項目に分けたフロー図">
<div class="ai-use-step"><b>目的</b><span>何を達成したいか。売上、問い合わせ、時間短縮、公開日など。</span></div>
<div class="ai-use-step"><b>材料</b><span>文章、写真、URL、表、コード、過去データ、顧客像。</span></div>
<div class="ai-use-step"><b>条件</b><span>誰向け、文字数、口調、禁止事項、使う媒体。</span></div>
<div class="ai-use-step"><b>形式</b><span>表、箇条書き、HTML、SNS投稿、チェックリスト。</span></div>
<div class="ai-use-step"><b>修正</b><span>短く、具体例追加、初心者向け、別案、根拠追加。</span></div>
</div>

この5項目を埋めるだけで、AIの回答は「読んで終わり」から「そのまま使える下書き」に近づきます。

### 4. 1回で終わらせず、直す

AIを使いこなせない人は、1回目の回答を完成品として見ます。使いこなせる人は、1回目をたたき台として扱います。

修正指示は難しくありません。

<div class="ai-use-example">この回答は抽象的です。彦根の小規模店舗向けに、明日できる行動だけに絞ってください。

文章が長いです。Instagramのカルーセル10枚に分けてください。

専門用語が多いです。AI初心者でもわかる言葉にしてください。

根拠が弱いです。確認すべき数字、見るべき画面、判断基準を追加してください。</div>

AIは「一発で正解を出す機械」ではなく、「修正しながら形にする相手」です。ここを理解すると、AI活用の成功率は一気に上がります。

### 5. 検証とリスク管理を入れる

AIの回答には、誤り、古い情報、著作権や個人情報のリスクが混ざることがあります。デジタル庁の生成AIリスク対策ガイドブックでも、利用形態やユースケースごとにリスクと留意点が変わることが示されています。

仕事で使うなら、次の3つは人間が確認します。

- 数字、日付、法律、料金、商品仕様などの事実
- 顧客情報、個人情報、社外秘を入れていないか
- 公開してよい表現か、誤解を招かないか

AIを使いこなす人は、AIを信用しすぎません。任せる部分と、人間が確認する部分を分けています。

## ChatGPT、Codex、Claude Code、画像生成はどう使い分けるか

AI活用はChatGPTだけではありません。今は文章、画像、コード、資料、業務手順を分けて使うほうが成果につながります。

<table class="ai-use-table">
<thead><tr><th>用途</th><th>向いている使い方</th></tr></thead>
<tbody>
<tr><td>ChatGPT</td><td>アイデア整理、文章作成、FAQ、営業メール、議事録、SNS投稿、企画の壁打ち。</td></tr>
<tr><td>画像生成</td><td>ブログのアイキャッチ、LPのビジュアル案、SNS投稿素材、チラシの方向性確認。</td></tr>
<tr><td>Codex</td><td>ホームページ改善、コード修正、テスト追加、複数ファイルをまたぐ実装、レビュー。OpenAIはCodexを「AIで構築し出荷するためのコーディングエージェント」と説明しています。</td></tr>
<tr><td>Claude Code</td><td>既存コードの読み解き、設計相談、長い文章や仕様の整理、別視点でのレビュー。</td></tr>
<tr><td>Cursor</td><td>エディタ内でのコード生成、既存プロジェクトの小さな修正、自然言語での実装補助。</td></tr>
</tbody>
</table>

ただし、道具を増やすだけでは成果は出ません。大事なのは「どの作業を、どのAIに、どの材料で任せるか」を決めることです。

## AIを使いこなせる人のセルフチェック

<ul class="ai-use-check">
<li>AIに頼む前に「何を達成したいか」を1文で言える</li>
<li>参考資料、URL、写真、既存文章、表、コードなどの材料を渡している</li>
<li>誰向け、文字数、口調、出力形式を指定している</li>
<li>1回目の回答を完成品扱いせず、追加修正を出している</li>
<li>事実確認が必要な部分をAI任せにしていない</li>
<li>個人情報、顧客情報、社外秘を不用意に入れていない</li>
<li>SNS投稿、チラシ文、議事録、Excel整理など小さい業務で試している</li>
<li>うまくいった指示文をテンプレとして保存している</li>
<li>画像生成やコード生成も、目的と修正指示で改善できると理解している</li>
<li>自分で悩み続ける前に、相談・講習・伴走支援を使う判断ができる</li>
</ul>

半分以上チェックが入れば、AI活用の入口には立てています。3個以下なら、プロンプト集を集めるより先に、自分の仕事を整理するところから始めたほうが早いです。

## 今日から使えるAI依頼テンプレ

コピーして、あなたの仕事に合わせて書き換えてください。

<div class="ai-use-example">あなたは私の業務改善パートナーです。

目的:
今の課題は「【ここに課題】」です。
現在は「【現在の数字・状態】」で、目標は「【目標の数字・状態】」です。

材料:
以下の情報をもとに考えてください。
・商品/サービス: 【内容】
・対象者: 【誰向け】
・現状の悩み: 【悩み】
・使える素材: 【写真、URL、文章、表、コードなど】

条件:
・初心者にもわかる表現にする
・明日からできる行動に分ける
・必要なら確認すべき数字も書く
・事実確認が必要な箇所は「要確認」と明記する

出力形式:
1. まず結論
2. 優先順位つきの改善案
3. すぐ使える文章またはチェックリスト
4. 次にAIへ追加で頼むべき指示</div>

このテンプレの狙いは、AIに「答え」を求めることではありません。自分の仕事の目的、材料、条件を整理し、次の行動に変えることです。

## AIを学ぶ前に決めるべきこと

AIを学ぶ前に、次の問いに答えてください。

- 売上を上げたいのか
- 問い合わせを増やしたいのか
- 作業時間を減らしたいのか
- ホームページやSNSを改善したいのか
- 新しいサービスを作りたいのか
- 自分でコードや画像生成まで触れるようになりたいのか

ここが明確になるほど、AIは強力になります。逆にここが曖昧だと、どれだけ高性能なAIを使っても、一般論の回答しか返ってきません。

## AIを仕事に入れる3ステップ

<div class="ai-use-roadmap" role="img" aria-label="AI相談からAI講習、CodexやClaude Codeを使った実装改善支援までの流れ">
<div class="ai-use-card"><span class="ai-use-badge">Step 1</span><h3>相談する</h3><p>自分の仕事のどこにAIを使えるかを整理します。最初はツール選びより、課題の分解が先です。</p></div>
<div class="ai-use-card"><span class="ai-use-badge">Step 2</span><h3>学ぶ</h3><p>ChatGPT、画像生成、Codex、Claude Codeを実際に触り、仕事の題材で練習します。</p></div>
<div class="ai-use-card"><span class="ai-use-badge">Step 3</span><h3>実装する</h3><p>ホームページ、SNS投稿、業務資料、コード修正まで、試して終わりではなく仕事に組み込みます。</p></div>
</div>

<div class="ai-use-cta">
<h2>AIを「知っている」で止めず、仕事に入れる</h2>
<p>何から始めればいいかわからない方は個別相談へ。自分で使えるようになりたい方はAI講習へ。サイト、SNS、業務改善、Codex / Claude Codeまで進めたい方は実装・改善支援をご相談ください。</p>
<a href="/#contact">無料でAI活用を相談する</a>
<a href="/#packages">AI講習の内容を見る</a>
<a href="/#lectures">受講資料を見る</a>
</div>

## よくある質問

<div class="ai-use-faq">
<details><summary>AIを使いこなせる人の一番の特徴は何ですか？</summary><p>自分の仕事を具体的に説明できることです。目的、材料、条件、出力形式、確認方法を言語化できる人ほど、AIから実務に使える回答を引き出せます。</p></details>
<details><summary>プロンプトが上手ければAIを使いこなせますか？</summary><p>プロンプトは大事ですが、それだけでは足りません。成果につながるのは、何を達成したいか、どの数字を見るか、どの業務に戻すかまで決める力です。</p></details>
<details><summary>AIを使いこなせない原因は何ですか？</summary><p>多くの場合、目的が曖昧、材料不足、修正指示不足、検証不足のどれかです。「AIで何かしたい」ではなく「この作業をこの状態にしたい」と言えるようにすると改善します。</p></details>
<details><summary>仕事でAIを使うなら何から始めればいいですか？</summary><p>議事録、メール、SNS投稿、FAQ、見積テンプレ、既存文章の改善など、小さく失敗しても困らない業務から始めるのがおすすめです。</p></details>
<details><summary>AIを使うときの注意点はありますか？</summary><p>事実確認、個人情報、顧客情報、社外秘、著作権、公開表現の確認が必要です。AIの回答をそのまま公開せず、人間が確認する工程を入れてください。</p></details>
</div>

## 参考にした主な情報

この記事は、2026年6月16日時点で公開されている検索結果、公式ドキュメント、調査レポート、実験論文を確認し、AIハブのAI相談・講習・実装支援の現場で使いやすい形に再構成しました。AI関連の数字は調査対象やタスク条件で結果が変わるため、本文では「全員が必ず同じ成果を得る」という表現は避けています。

<div class="ai-use-sources">
<ul>
<li><a href="https://www.microsoft.com/en-us/worklab/work-trend-index/ai-at-work-is-here-now-comes-the-hard-part" target="_blank" rel="noopener">Microsoft / LinkedIn: 2024 Work Trend Index Annual Report</a></li>
<li><a href="https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai" target="_blank" rel="noopener">McKinsey: The state of AI in 2025: Agents, innovation, and transformation</a></li>
<li><a href="https://www.rand.org/pubs/research_reports/RRA2680-1.html" target="_blank" rel="noopener">RAND: The Root Causes of Failure for Artificial Intelligence Projects and How They Can Succeed</a></li>
<li><a href="https://arxiv.org/abs/2304.11771" target="_blank" rel="noopener">Generative AI at Work: 顧客サポート現場での生産性研究</a></li>
<li><a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573321" target="_blank" rel="noopener">BCG / Harvard / MIT: Navigating the Jagged Technological Frontier</a></li>
<li><a href="https://arxiv.org/abs/2302.06590" target="_blank" rel="noopener">GitHub Copilot実験: The Impact of AI on Developer Productivity</a></li>
<li><a href="https://arxiv.org/abs/2507.09089" target="_blank" rel="noopener">METR: Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity</a></li>
<li><a href="https://survey.stackoverflow.co/2025/ai" target="_blank" rel="noopener">Stack Overflow Developer Survey 2025: AI</a></li>
<li><a href="https://developers.google.com/search/docs/fundamentals/creating-helpful-content" target="_blank" rel="noopener">Google Search Central: Creating helpful, reliable, people-first content</a></li>
<li><a href="https://www.digital.go.jp/resources/generalitve-ai-guidebook" target="_blank" rel="noopener">デジタル庁: テキスト生成AI利活用におけるリスクへの対策ガイドブック</a></li>
<li><a href="https://www.meti.go.jp/shingikai/mono_info_service/ai_shakai_jisso/20240419_report.html" target="_blank" rel="noopener">経済産業省: AI事業者ガイドライン</a></li>
<li><a href="https://openai.com/codex/" target="_blank" rel="noopener">OpenAI: Codex</a></li>
</ul>
</div>
