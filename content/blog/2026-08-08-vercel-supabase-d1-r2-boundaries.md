---
title: "ウェブサイト公開から本格稼働へ：AIで作ったWebサービスの5つの置き場所"
date: 2026-08-08
authorship_note: "この記事は、AIを整理・編集の補助として使い、運営者が内容を確認・編集しています。"
role: ブログ / AI活用・Webシステム設計
gen_by: 由井辰美 / AI相談
summary: AIで作ったWebサービスを公開後に本格稼働させるとき、公開画面、軽量データ、ファイル、認証・権限、既存の業務サービスをどこに置くかを解説します。データベースの置き場所を、データ量ではなく権限の複雑さと業務上の責任から判断し、小さく安全に運用を広げる順番を、地域事業者や小規模チーム向けに整理します。
image: /img/blog-sites-d1-r2-supabase-hero-20260808.png
hero_image: true
image_alt: 公開サイト、軽量データ、安全な会員データ、外部サービスを分けてつなぐモジュール型のWebシステム
image_caption: 速く作るために一つへ集めるのではなく、役割ごとに小さく分けてつなぐ設計です。
audience: AIでサイトや業務ツールを作りたい地域事業者、学校・福祉の現場責任者、個人事業主、小規模チーム
duration: 9分
goal: Webサービスを公開後に本格稼働させるため、公開情報、軽量データ、ファイル、認証・権限、外部業務サービスの5つを分け、次に残す基盤と試せる基盤を判断できるようになる
---

「AIで作ったウェブサイトを公開できた。次は、お知らせ、画像、会員情報、予約をどこに置けばよいだろうか」

「最初は一人で管理できても、スタッフや利用者が増えた後に壊れない形にしたい」

AIでサイトや業務ツールを作れるようになると、公開までは以前より速くなりました。けれど公開はゴールではなく、運用の始まりです。どのデータをどこへ置くかを最初に分けないと、後から認証、権限、費用、引継ぎが絡み合います。

ここでいう本格稼働は、最初から大きなシステムを作ることではありません。公開画面、軽い情報、ファイル、人と権限、現実の業務を混ぜず、必要な場所だけを強くすることです。

> **AIで何でも作れる時代だからこそ、何でも一つに入れない。**

公開情報は小さく。ログインと重要な会員・業務データは強く。決済や予約など、現実の業務を動かす情報は、すでに使っている専門サービスを正本として残す。この分け方なら、運用費を見直しながら、修正も速くできます。

<figure>
  <img src="/img/blog-sites-d1-r2-supabase-hero-20260808.png" alt="公開サイト、軽量データ、安全な会員データ、外部サービスを分けてつなぐモジュール型のWebシステム" loading="eager" decoding="async">
  <figcaption>「全部を移すか」ではなく、「何をどこまで移すか」を決めることが出発点です。</figcaption>
</figure>

## 本格稼働の出発点は、データと機能を5つに分けること

<figure>
  <img src="/img/blog-sites-d1-r2-supabase-system-layers-20260808.png" alt="公開ページ、軽量データ、ファイル、認証、外部業務サービスの5つを分けた構成図" loading="lazy" decoding="async">
  <figcaption>技術名から始めず、実際に扱うものを5つに分けると判断しやすくなります。</figcaption>
</figure>

本格稼働へ進むときに大切なのは、どのサービスを採用するかより先に、何を預けるかを分けることです。たとえば、地域の講座やイベントを案内するサイトでも、実際には次の5つが混ざっています。

<div class="publishing-table-scroll" tabindex="0" aria-label="扱うものを5つに分ける一覧。横にスクロールできます。">
  <table>
    <thead><tr><th>分けるもの</th><th>具体例</th><th>まず考える置き場所</th></tr></thead>
    <tbody>
      <tr><td>画面</td><td>サイト、ブログ、管理画面</td><td>Sites / Vercel / Workers</td></tr>
      <tr><td>小さな情報</td><td>お知らせ、FAQ、イベント一覧、表示設定</td><td>D1 などサイト単位のDB</td></tr>
      <tr><td>ファイル</td><td>写真、PDF、動画、音声</td><td>R2 などファイル保管先</td></tr>
      <tr><td>人と権限</td><td>Googleログイン、会員、スタッフ、閲覧範囲</td><td>Supabase Auth + Postgres + RLS</td></tr>
      <tr><td>現実の業務</td><td>決済、予約、注文、配送、解錠</td><td>Square、EC、予約、IoTなどの専門サービス</td></tr>
    </tbody>
  </table>
</div>

D1は、イベント名・開催日・定員のような、表形式の小さな情報を扱う場所です。R2は画像、PDF、動画など、ファイル本体の保管場所です。

たとえば、イベント情報なら、D1には「タイトル・日時・定員・画像のパス」を持たせ、画像そのものはR2のようなファイル保管先へ置く、という分け方になります。

ここで大切なのは、D1とR2を「安いから使う箱」として決めないことです。公開に近い情報を、サイトごとに小さく独立させるための箱として使います。

## データベースは、データ量ではなく権限の複雑さで決める

<figure>
  <img src="/img/blog-sites-d1-r2-supabase-access-boundary-20260808.png" alt="公開コンテンツと安全な会員データの間に認証と権限の門を置いたイメージ" loading="lazy" decoding="async">
  <figcaption>ログインがあるだけでD1を避ける必要はありません。ただし、誰がどの行を見られるかが複雑なら、RLSを持つPostgresを残します。</figcaption>
</figure>

データベースの置き場所は、容量の小ささだけで決めません。誰が何を見たり変えたりできるかを、どこで守るかが判断の中心です。Supabase Authは「この人は誰か」を確認する仕組みです。さらにSupabase PostgresのRLS（行レベルセキュリティ）は、「その人が、このデータのどこまで見たり変えたりできるか」をデータベース側で守れます。

たとえば、スタッフ、支店、役割、会員区分が絡み、利用者ごとに見える予約・顧客・売上情報が違う場合です。こうしたデータをD1へ移すと、Supabaseで使っていたRLSが自動で引き継がれるわけではありません。アプリ側でトークン確認と行ごとの権限判定を実装し、テストし続ける必要があります。

そのため判断軸は、次のようになります。

<div class="publishing-table-scroll" tabindex="0" aria-label="データ別の推奨構成一覧。横にスクロールできます。">
  <table>
    <thead><tr><th>データの例</th><th>推奨する考え方</th></tr></thead>
    <tbody>
      <tr><td>公開FAQ、イベント、ブログ一覧、表示設定</td><td>D1など、サイトごとの軽量DBを検討</td></tr>
      <tr><td>会員プロフィール、スタッフ所属、支店権限、受講進捗</td><td>Supabase Auth + Postgres + RLSを基本に残す</td></tr>
      <tr><td>写真、PDF、公開動画</td><td>R2などのファイル保管先を使う</td></tr>
      <tr><td>カード情報、注文、予約枠、配送、解錠</td><td>専門サービスを正本にする。必要な連携だけを作る</td></tr>
    </tbody>
  </table>
</div>

「小さいデータだからD1」ではありません。

> **権限モデルが単純ならD1を検討し、利用者や権限の関係が複雑ならSupabase PostgresとRLSを残す。**

この基準なら、後でスタッフが増えても、顧客情報が混ざっても、守るべき境界が曖昧になりません。Supabaseの公式ドキュメントでも、ブラウザから到達できるテーブルではRLSを有効にし、Authと組み合わせて行単位の権限を設計することが案内されています。

## 公開・軽量処理と、複雑な業務を分けて運用する

<figure>
  <img src="/img/blog-sites-d1-r2-supabase-hosting-choice-20260808.png" alt="軽い公開サイトと複雑な業務システムが異なるクラウド経路を選ぶイメージ" loading="lazy" decoding="async">
  <figcaption>公開ページと複雑なバックエンドは、同じ場所に置く必要がありません。</figcaption>
</figure>

公開基盤を一本化するか、すべてを移すか、の二択にする必要はありません。

公開ページ、キャンペーン、ブログ、イベント一覧、個人情報を保存しない小型ツールなら、ChatGPT SitesやCloudflare Workersを試す候補になります。AIと相談しながら更新しやすく、サイトごとの軽量データを小さく保てるからです。

一方で、次のような処理は、VercelまたはCloudflare Workersのような明確な実行基盤と、Supabaseの認証・DBを残して考える方が安全です。

- StripeやSquareのWebhookを受け、契約・支払い状態を更新する
- 予約枠、在庫、注文、配送など、二重登録や競合が困る処理を行う
- 会員、スタッフ、支店、役割をまたぐ権限を管理する
- 長めのAPI処理、定期実行、外部SaaS連携を安定して運用する

ChatGPT Sitesは、軽量なWeb体験を素早く作り、プレビュー後に公開できる有力な選択肢です。ただし、2026年8月時点ではパブリックベータで、利用上限はアカウント全体にかかり、一部のフレームワーク、バックグラウンド処理、外部DB、ホスティング形態は対象外になりえます。また、Sites本体、D1/R2のデータやファイル保管を含め、データレジデンシーには対応していません。

したがって、個人情報、顧客情報、決済情報を何でもSites内のD1/R2へ移す前提にはしません。

もう一つ大事なのは、**ChatGPT Sitesで使うD1/R2と、自分のCloudflareアカウントで直接使うD1/R2は、同じ費用体系・運用条件だと決めつけない**ことです。Cloudflareを直接使う場合は、Workers・D1・R2の利用量と上限をCloudflare側で管理します。Sitesを使う場合は、まずSites画面に出るプラン別の上限と対応機能を確認します。

## 本格稼働へ進むために、6段階で小さく試す

<figure>
  <img src="/img/blog-sites-d1-r2-supabase-migration-ladder-20260808.png" alt="公開サイトから認証、重要データ、専門サービスへ段階的に進む移行の道筋" loading="lazy" decoding="async">
  <figcaption>必要な場所だけ一段ずつ足す方が、費用も確認範囲も小さくできます。</figcaption>
</figure>

ウェブサイトを公開した後は、最初から一番大きな構成にしません。次の6段階で考えると、現場で判断しやすくなります。

<div class="publishing-table-scroll" tabindex="0" aria-label="6段階の構成一覧。横にスクロールできます。">
  <table>
    <thead><tr><th>段階</th><th>構成</th><th>向くもの</th></tr></thead>
    <tbody>
      <tr><td>L0</td><td>静的ホスティング</td><td>会社案内、講座LP、作品紹介</td></tr>
      <tr><td>L1</td><td>静的ホスティング + 軽量DB/ファイル保管</td><td>お知らせ、イベント、FAQ、公開資料</td></tr>
      <tr><td>L2</td><td>L1 + Supabase Auth</td><td>ログインで見せ分ける資料や小型ツール</td></tr>
      <tr><td>L3</td><td>L2 + Supabase Postgres/RLS</td><td>会員、スタッフ、権限、進捗、個人ごとの記録</td></tr>
      <tr><td>L4</td><td>Vercel / Workers + Supabase</td><td>Webhook、外部API、予約、複雑な業務処理</td></tr>
      <tr><td>L5</td><td>専門SaaSを正本にする</td><td>決済、EC、POS、予約、配送、IoT</td></tr>
    </tbody>
  </table>
</div>

L1で十分なサイトなら、L4まで持ち上げない方が、修正も引継ぎも楽になります。逆にL4やL5が必要な仕組みは、無理にD1だけへ寄せない方が安全です。

最初の実証候補は、止まっても顧客や決済に影響しない公開サイトです。既存のVercel版を残したまま、次の順番で比べます。

1. 公開ページを1つだけ複製し、PCとスマホで見た目を確認する
2. お知らせやイベント一覧だけを軽量DBへ移し、更新のしやすさを確かめる
3. GitHubの原本、バックアップ、元の公開先を残す
4. 利用量、更新時間、障害時の戻し方を数週間記録する
5. 問題がなければ、次の小さなサイトへ同じ型を広げる

この順番なら、コスト削減だけでなく、AIへ「どこを直してほしいか」を小さく伝えられます。確認範囲が狭くなるので、修正、引継ぎ、改善の速度も上がります。

### よくある質問

**Q. 認証だけを使い、別のDBに会員データを置いてもよいですか？**

できますが、会員ごと・スタッフごとに行単位の閲覧権限が必要なら、Supabase PostgresとRLSを残す方が実装と監査が単純です。D1側へ移すなら、サーバー側でJWT確認と権限判定を設計・検証する責任が増えます。

**Q. 公開基盤を変えれば、すぐ無料になりますか？**

必ずしもそうではありません。ChatGPT Sitesはベータのプラン別上限、CloudflareはWorkers・D1・R2の利用量、Supabaseは認証・DB・ストレージの利用量を、それぞれ確認する必要があります。費用だけでなく、障害時に戻せるか、誰が運用するかまで比べます。

**Q. 決済や予約まで同じ基盤へ移すべきですか？**

おすすめしません。すでにSquare、EC、予約サービスなどが正本として動いているなら、その正本を置き換えず、案内・申込導線・表示・必要な連携だけを作る方が安全です。

<div class="publishing-cta">
  <strong>ウェブサイトを公開した後こそ、「どのサービスを使うか」より先に、「何をどこに置くか」を整理します。</strong>
  <p>AI相談では、公開情報、会員・権限、ファイル、決済・予約、既存SaaSを分け、本格稼働へ進む構成と移行順序を一緒に設計します。</p>
  <p><a href="/#contact">AI相談へ相談する</a> ・ <a href="/blog/index.html">AI相談のブログ一覧を読む</a></p>
</div>

### 参考にした公式情報

- [OpenAI：ChatGPT Sitesの作成・管理と対応範囲](https://help.openai.com/en/articles/20001339-creating-and-managing-chatgpt-sites)
- [OpenAI：ChatGPTのデータレジデンシーとSitesの対象外範囲](https://help.openai.com/en/articles/9903489-data-residency-and-inference-residency-for-chatgpt)
- [Supabase：Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase：Auth](https://supabase.com/docs/guides/auth)
- [Cloudflare：D1の料金](https://developers.cloudflare.com/d1/platform/pricing/)
- [Cloudflare：D1の上限](https://developers.cloudflare.com/d1/platform/limits/)
- [Cloudflare：R2の料金](https://developers.cloudflare.com/r2/pricing/)
- [Vercel：料金プラン](https://vercel.com/pricing)

<p class="publishing-note">※機能、上限、料金、対応範囲は2026年8月8日時点で公式情報を確認しています。移行の実行前に、対象サイトの個人情報・決済・権限・現在の契約条件を個別に確認してください。</p>

<style>
html,body{max-width:100%;overflow-x:hidden}
main>header h1{overflow-wrap:anywhere}
.content-wrap table{display:block;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.content-wrap pre{max-width:100%;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word}
.publishing-table-scroll{max-width:100%;margin:22px 0;overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid rgba(7,95,200,.14);border-radius:12px;background:#fff}
.publishing-table-scroll table{display:table;min-width:680px;max-width:none;margin:0}
.publishing-cta{margin:34px 0 18px;padding:24px;border:1px solid rgba(7,95,200,.22);border-radius:14px;background:#f3f8ff}
.publishing-cta strong{display:block;color:#0b3b76;font-size:1.08rem;line-height:1.7}
.publishing-cta p{margin:10px 0 0}
.publishing-cta a{font-weight:800}
.publishing-note{margin-top:22px;color:#5f6f82;font-size:.9rem}
@media(max-width:640px){.publishing-table-scroll{margin:18px 0}.publishing-table-scroll table{min-width:640px;font-size:.92rem}.publishing-cta{padding:18px}}
</style>
