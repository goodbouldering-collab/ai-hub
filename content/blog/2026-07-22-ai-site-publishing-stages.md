---
title: "AIで作ったサイトはどこにアップする？初心者向け「とりあえず公開・仮稼働・本番稼働」の違い"
date: 2026-07-22
role: ブログ / AI初心者・地域事業者・個人事業主向け
gen_by: 由井 辰美 / AI相談
summary: AIで作ったページをCodex Sites、Vercel＋Supabase、Cloudflareのどこへ公開すべきかを、性能・使いやすさ・将来性と「とりあえず公開・仮稼働・本番稼働」の違いからやさしく整理します。
image: /img/blog-ai-site-publishing-hero-20260722.png
hero_image: true
image_alt: AIで作ったサイトの公開先としてCodex Sites、VercelとSupabase、Cloudflareを比較するスライド
image_caption: 最初から完璧な基盤を選ぶ必要はありません。目的と扱うデータに合わせて、公開先を段階的に選びます。
---

AIでWebページを作れるようになると、次に出てくるのが「これは、どこにアップすればいいの？」という不安です。

ページを作るところまではAIが手伝ってくれても、公開先にはいくつも名前が出てきます。Codex Sites、Vercel、Supabase、Cloudflare。知らない言葉が並ぶと、公開する前に止まりたくなるのは普通です。

でも、最初から全部を理解する必要はありません。大切なのは、**いま作っているものが「見せるページ」なのか、「試しに使ってもらう仕組み」なのか、「お客様の情報を預かる本番サービス」なのか**を分けることです。

まずは約49秒の動画で、結論をつかんでください。

<figure class="publishing-video">
  <video controls playsinline preload="metadata" poster="/img/blog-ai-site-publishing-hero-20260722.png">
    <source src="/videos/ai-site-publishing-guide-20260722.mp4" type="video/mp4">
    お使いのブラウザでは動画を再生できません。
  </video>
  <figcaption>7枚の要点版スライドを動画にしました。音を出さなくても内容を追えます。</figcaption>
</figure>

<div class="publishing-downloads" aria-label="比較資料のダウンロード">
  <a href="/downloads/ai-site-publishing-guide-7slides-20260722.pptx" download>7枚の要点版スライドをダウンロード</a>
  <a href="/downloads/ai-site-publishing-guide-20slides-20260722.pptx" download>20枚の詳細版スライドをダウンロード</a>
</div>

先に結論を言うと、AI相談では次の選び方をおすすめします。

- **すぐ見せたいページや試作品**：Codex Sites
- **予約・会員・業務アプリなどの本番運用**：Vercel＋Supabase
- **大量アクセス、動画・画像配信、世界規模の高速化が必要**：Cloudflare

これは優劣ではなく、役割の違いです。初心者ほど「一生使える唯一の正解」を探すより、段階に合った道具を選ぶほうが安全に前へ進めます。

## なぜ公開先を選ぶ必要があるのか

<figure>
  <img src="/img/blog-ai-site-publishing-section-1-why-20260722.png" alt="公開先によって安全性、費用、直しやすさが変わることを示す図" loading="eager" decoding="async">
  <figcaption>公開先は単なる置き場所ではありません。誰に見せるか、何を預かるか、止まったとき誰が直すかまで決めます。</figcaption>
</figure>

サイトは、インターネット上にファイルを置けば終わりではありません。公開後には、少なくとも次のことが起きます。

- 誰でも見られるURLができる
- 間違いを見つけたら修正する
- 画像や動画を配信する
- 問い合わせや予約の情報を受け取る
- 利用者が増えたら性能や費用を見直す
- トラブル時に元へ戻す

公開先によって、これらのやりやすさが変わります。特に大切なのは、**「公開できた」と「安心して続けられる」は別**だということです。

たとえば、講演会の案内ページなら、公開後に集める情報がなく、短期間だけ見られれば十分かもしれません。一方で、福祉施設の利用者情報、学校の名簿、会員のログイン情報、予約や決済を扱うなら、間違った人にデータを見せない権限設定、バックアップ、障害時の復旧手順が必要です。

公開前に難しい技術用語を覚える代わりに、次の5問へ答えてみてください。

1. 誰に見せますか。自分だけ、関係者だけ、誰でも、のどれですか。
2. 個人情報、予約、決済、会員データを扱いますか。
3. 1日止まると、誰がどれくらい困りますか。
4. 毎月いくらまでなら無理なく続けられますか。
5. 半年後に別のサービスへ移す必要が出ても、データを取り出せますか。

この答えが軽ければ「とりあえず公開」で十分です。答えが重くなるほど、仮稼働、本番稼働へ進む準備が必要です。

## 「とりあえず公開・仮稼働・本番稼働」は何が違うのか

<figure>
  <img src="/img/blog-ai-site-publishing-section-2-stages-20260722.png" alt="とりあえず公開、仮稼働、本番稼働の3段階を示す図" loading="lazy" decoding="async">
  <figcaption>段階が上がるほど、実データ、利用者への責任、監視と復旧の準備が増えます。</figcaption>
</figure>

「本番」という言葉はサービスごとに使い方が違うため、初心者には特に分かりにくい言葉です。ここでは、地域の事業者や講座受講者が判断しやすいよう、業務上の意味で3段階に分けます。

| 段階 | 目的 | 扱う情報 | 公開期間・相手 | 必要な準備 |
|---|---|---|---|---|
| とりあえず公開 | アイデアや見た目を見せる | 公開してよい文章・画像だけ | 短期、少人数または一般公開 | 内容確認、削除・修正方法 |
| 仮稼働 | 実際に使えるか試す | ダミーデータ、または限定した低リスク情報 | 期限を決めた限定利用 | 利用ルール、測定項目、終了・移行条件 |
| 本番稼働 | 日常の業務やサービスを支える | 顧客、会員、予約、決済などの実データ | 継続利用 | 認証、権限、バックアップ、監視、復旧、担当者 |

Codex Sitesの公式説明では、Sitesが発行する公開URLは製品上「production deployment」と呼ばれます。ただし、これは**URLが一般利用できる状態になった**という意味です。AI相談でいう「業務上の本番稼働」は、実際のお客様や職員が使い、データを預かり、止まったときにも対応できる状態を指します。

この2つを混同しなければ、焦る必要はありません。Sitesで公開した試作品を見てもらい、反応が良ければVercel＋Supabaseへ育てる、という進め方で大丈夫です。

仮稼働では、始める前に終了条件も決めます。たとえば「2週間、5人に使ってもらい、3人以上がもう一度使ったら本番化を検討する」のようにします。試す目的が決まっていれば、機能を足し続けて終わらない試作品になるのを防げます。

本番稼働では、画面の完成度だけでなく、次の裏側が重要になります。

- ログインした人ごとに見られる情報を分ける
- 個人情報や秘密鍵を画面や公開ファイルへ置かない
- データを定期的にバックアップする
- エラーや利用量を確認する
- 更新前に別URLで確認し、問題があれば元へ戻す
- 担当者がいなくても復旧手順を追えるようにする

AIを習い始めた人が、これを一人で最初から完璧にする必要はありません。**重要な情報を扱う段階で、詳しい人と一緒に確認する**ことも立派な設計です。

## Codex Sites・Vercel＋Supabase・Cloudflareのどれを選ぶか

<figure>
  <img src="/img/blog-ai-site-publishing-section-3-compare-20260722.png" alt="Codex Sites、VercelとSupabase、Cloudflareの使いやすさ、将来性、費用感を比較した図" loading="lazy" decoding="async">
  <figcaption>性能だけで決めず、作る速さ、データ管理、運用のしやすさを一緒に比べます。</figcaption>
</figure>

### Codex Sites：まず形にして見せるのが得意

Codex Sitesは、ChatGPT上でサイトを作成、保存、公開、管理できる仕組みです。別のデプロイ作業を組まずに、プロンプトや対応した既存プロジェクトから公開体験へ進めます。現在はパブリックベータで、利用できる機能や上限はプラン、地域、ワークスペース設定によって変わります。

向いているのは、講座の説明ページ、イベント案内、提案用デモ、学習中の作品、期間限定の試作品です。D1による構造化データ、R2によるファイル保存にも対応するため、単なる1枚ページより先まで作れます。

一方で、運用管理はChatGPTのWebまたはデスクトップアプリが中心で、単独のCLIやIDE管理画面はありません。パブリックベータ中は上限や仕様が変わる可能性もあります。だから「使えない」のではなく、**まず試す場所として非常に便利で、止められない業務へ入れるときは改めて運用要件を確認する**のがよい選び方です。

### Vercel＋Supabase：本番Webアプリの基本形にしやすい

Vercelは、Web画面とサーバー側の処理を公開し、Gitの更新からプレビューと本番を分けやすいサービスです。Supabaseは、Postgresデータベース、ログイン認証、ファイル保存などをまとめて提供します。

この組み合わせは、予約、会員ページ、業務管理、相談記録、学習記録、地域サービスの受付など、**画面とデータを一緒に育てる本番Webアプリ**に向いています。SupabaseではRow Level Security（RLS）を使い、利用者ごとにデータの閲覧・更新範囲を制限できます。VercelではLocal、Preview、Productionを分け、変更を別URLで確かめてから本番へ進められます。

ただし、接続しただけで自動的に安全になるわけではありません。RLSの設計、秘密情報の管理、バックアップ対象の確認が必要です。無料枠から試せますが、本番運用では利用量、停止条件、バックアップ保持期間を見て有料プランを検討します。価格や上限は変わるため、公開前に公式ページで確認してください。

### Cloudflare：大量配信とEdge処理で力を発揮する

Cloudflare Workersは、世界各地に近い場所で処理を動かしやすく、Pages Functions、D1、R2などと組み合わせられます。画像・動画・大きなファイルを多く配る場合は、R2がインターネットへのデータ転送量に対するエグレス料金を取らない点も強みです。

向いているのは、大量アクセスへの対応、世界向けの低遅延API、キャッシュ、セキュリティ対策、動画・画像配信、既存サービスの前段での高速処理です。性能と将来性は高い一方、Vercel＋Supabaseのような「認証とPostgresを一式で始める」体験とは設計思想が違います。D1はSQLite互換で、SupabaseのPostgresと同じものではありません。

そのため、初心者が最初の予約アプリを作るならCloudflareを全部の土台にするより、Vercel＋Supabaseを基本にし、**アクセス量や配信コストという具体的な問題が見えてからCloudflareを加える**ほうが分かりやすい場合が多いです。

### 3つを簡単に比較

| 比較点 | Codex Sites | Vercel＋Supabase | Cloudflare |
|---|---|---|---|
| 公開までの速さ | とても速い | 速いが初期設定あり | 構成により設定が増える |
| 初心者の使いやすさ | 最も始めやすい | 学びながら本番へ育てやすい | 基盤設計の知識が必要 |
| データ・ログイン | 対応可能。要件を明示 | Auth＋Postgres＋RLSが強い | 組み合わせを設計する |
| 性能 | 試作・一般的なサイトに十分 | 一般的なWebアプリに強い | Edge・大量配信に強い |
| 将来性 | 学習・試作・内部ツールで有望 | 本番サービスを長く育てやすい | 世界規模・高トラフィックで有望 |
| おすすめの役割 | 実験室 | 本店 | 専門設備 |

## 迷ったら、小さく公開して必要になったら本番へ進む

<figure>
  <img src="/img/blog-ai-site-publishing-section-4-choice-20260722.png" alt="仮公開はCodex Sites、本番業務はVercelとSupabase、大量配信はCloudflareを選ぶ結論図" loading="lazy" decoding="async">
  <figcaption>AI相談の基本提案は、Sitesを実験室、Vercel＋Supabaseを本店、Cloudflareを専門設備として使い分けることです。</figcaption>
</figure>

これからAIを習う人にとって、一番危険なのは「間違ったサービスを選ぶこと」より、怖くなって何も公開せず、誰の反応も得られないことです。

次の4歩なら、無理なく進められます。

1. 個人情報を入れない1ページをCodex Sitesで公開する
2. 見てもらう相手、公開期限、確認したいことを1つ決める
3. 予約・会員・継続データが必要になったらVercel＋Supabaseへ育てる
4. 実測で速度や配信費用の問題が出たらCloudflareを加える

たとえば地域交流会なら、最初は日時、場所、目的、問い合わせ先だけをSitesで見せます。参加申込が増え、名簿管理や自動返信が必要になったら、Vercel＋Supabaseで受付システムへ進めます。写真や動画を大量に届ける必要が出たら、Cloudflare R2などを検討します。

学校や福祉施設では、公開ページに個人情報を置かないことを最優先にします。職員だけの内部ツールは、誰がログインできるか、退職・異動時にどう権限を外すか、記録をどれくらい残すかまで決めます。

個人事業主や若い挑戦者は、最初の公開でお金をかけすぎる必要はありません。ただし、予約や決済を受け始めたら「無料だから」だけで選ばず、売上機会、復旧時間、顧客への責任を含めて判断します。

### よくある質問

**Q. 公開URLができたら、本番稼働ですか？**

技術上は「本番URL」と呼ばれることがありますが、業務上の本番稼働とは限りません。実際のお客様や実データを預かるなら、認証、権限、バックアップ、監視、復旧手順まで確認して初めて本番と考えます。

**Q. 無料で始めても大丈夫ですか？**

公開内容だけの小さな試作なら、無料枠から始めて構いません。ただし、利用上限を超えたときに停止する条件や、バックアップの有無はサービスごとに違います。本番へ移る前に現在の公式料金と上限を確認してください。

**Q. プログラミングができなくても公開できますか？**

最初の案内ページや試作品は、AIとSitesを使えばコードを書かずに近い感覚で進められます。個人情報、予約、決済を扱う段階では、AIに任せきらず、設計と確認ができる人の支援を受けると安心です。

**Q. 最初からVercel＋Supabaseにしたほうが二度手間になりませんか？**

要件が明確で、継続運用することが決まっているなら最初から選ぶ価値があります。まだ誰が使うか分からない段階では、Sitesで言葉と流れを確かめることで、作り直す範囲を小さくできます。試作は無駄ではなく、間違った本番を作らないための確認です。

<div class="publishing-cta">
  <strong>AI相談では「作る」だけでなく、どこまで公開してよいか、本番へ進む準備ができているかまで一緒に整理します。</strong>
  <p>地域事業者、学校、福祉施設、個人事業主の方が、今ある資料や止まっている業務を持ち込み、小さな公開から安全な運用へ進める形にします。</p>
  <p><a href="/#contact">AI相談へ相談する</a> ・ <a href="/programming-map.html">AIコーディング講習を見る</a></p>
</div>

### 参考にした公式情報

- [OpenAI: Sites](https://learn.chatgpt.com/docs/sites)
- [Vercel: Deployments](https://vercel.com/docs/deployments/overview)
- [Vercel: Pricing](https://vercel.com/docs/pricing)
- [Supabase: Documentation](https://supabase.com/docs)
- [Supabase: Database and Row Level Security](https://supabase.com/docs/guides/database/overview)
- [Supabase: Pricing](https://supabase.com/pricing)
- [Cloudflare Workers: Pricing](https://developers.cloudflare.com/workers/platform/pricing/)
- [Cloudflare D1: Pricing](https://developers.cloudflare.com/d1/platform/pricing/)
- [Cloudflare R2: Pricing](https://developers.cloudflare.com/r2/pricing/)

<p class="publishing-note">※機能、利用上限、料金は2026年7月22日時点の公式情報を確認しています。公開前には各サービスの最新情報を再確認してください。</p>

<style>
html,body{max-width:100%;overflow-x:hidden;}
main>header h1{overflow-wrap:anywhere;}
.content-wrap table{display:block;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;}
.publishing-video{margin:26px 0 14px;}
.publishing-video video{display:block;width:100%;max-width:100%;aspect-ratio:16/9;background:#061225;border-radius:16px;box-shadow:0 18px 40px rgba(6,18,37,.18);}
.publishing-video figcaption{margin-top:10px;text-align:center;color:#526277;font-size:.92rem;}
.publishing-downloads{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:18px 0 30px;}
.publishing-downloads a{display:flex;align-items:center;justify-content:center;min-height:52px;padding:12px 16px;border-radius:12px;background:#075fc8;color:#fff;text-align:center;font-weight:800;text-decoration:none;}
.publishing-downloads a:last-child{background:#0b3b76;}
.publishing-downloads a:hover{filter:brightness(1.08);}
.publishing-cta{margin:34px 0 18px;padding:24px;border:1px solid rgba(7,95,200,.22);border-radius:14px;background:#f3f8ff;}
.publishing-cta strong{display:block;color:#0b3b76;font-size:1.08rem;line-height:1.7;}
.publishing-cta p{margin:10px 0 0;}
.publishing-cta a{font-weight:800;}
.publishing-note{margin-top:22px;color:#5f6f82;font-size:.9rem;}
@media (max-width:640px){.publishing-downloads{grid-template-columns:1fr}.publishing-video video{border-radius:10px}.publishing-cta{padding:18px}}
</style>
