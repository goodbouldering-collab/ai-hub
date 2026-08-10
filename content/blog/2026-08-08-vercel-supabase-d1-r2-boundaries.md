---
title: "サイト公開から本格稼働させるには、データをどこに置くのが正解？──Sites・GitHub＋Vercel＋Supabaseの選び方"
date: 2026-08-10
authorship_note: "※この記事は、運営者が自ら考えた内容を、AIを使って読みやすく整えた記事です。"
role: ブログ / AI活用・Webシステム設計
gen_by: 由井辰美 / AI相談
summary: 仮LPや小さな社内ツールならSites、継続開発や複数PCならGitHub＋Vercel、顧客情報・会計・書類・権限を扱うならGitHub＋Vercel＋Supabase。データ量だけでなく、共有・復旧・バックアップの必要性で選ぶ実務的な基準を整理します。
image: /img/blog-sites-runtime-data-decision-hero-20260810.png
hero_image: true
image_alt: Sites、GitHubとVercel、Supabaseを役割別に選ぶための3つの経路を描いた図解
image_caption: データ量より、共有・復旧・権限・バックアップの必要性で置き場所を決めます。
audience: AIでサイトや業務ツールを作りたい地域事業者、学校・福祉の現場責任者、個人事業主、小規模チーム
duration: 8分
goal: サイトを公開する段階と本格稼働させる段階を分け、データの置き場所と復旧手順を自分で判断できるようになる
---

「イベントの案内ページは作れた。でも、申込者や書類を扱い始めたら、どこに置けばよいのだろう」

「PCが壊れたとき、別のPCや別のCodexで続きを作れる状態になっているだろうか」

AIでサイトを作る速度が上がるほど、次に大切になるのがデータの置き場所です。ここで見るべきなのは、データの容量だけではありません。**将来、クローン・共有・復旧・バックアップが必要になるか**です。

結論から言うと、私は次のように分けます。

<div class="publishing-table-scroll" tabindex="0" aria-label="用途別に向く構成を示す一覧。横にスクロールできます。">
  <table>
    <thead><tr><th>用途</th><th>向く構成</th><th>判断理由</th></tr></thead>
    <tbody>
      <tr><td>仮LP、イベント告知、企画の試作</td><td>Sites</td><td>早く形にして、限られた相手へ共有しやすい</td></tr>
      <tr><td>社内の小さな検索・チェック表・集計画面</td><td>Sites</td><td>データが少なく、ChatGPT利用者だけで閉じるなら扱いやすい</td></tr>
      <tr><td>他PCや他Codexで開発を続ける可能性がある</td><td>GitHub＋Vercel</td><td>コードをクローンし、同じ環境を再現しやすい</td></tr>
      <tr><td>顧客情報、売上、在庫、PDF、会員情報を扱う</td><td>GitHub＋Vercel＋Supabase</td><td>認証、DB、Storage、権限、復元を分けて管理できる</td></tr>
      <tr><td>決済や本番業務を扱う</td><td>GitHub＋Vercel＋Supabase</td><td>Sitesへ無理に寄せず、専門サービスとも安全に連携しやすい</td></tr>
    </tbody>
  </table>
</div>

<figure>
  <img src="/img/blog-sites-runtime-data-decision-hero-20260810.png" alt="Sites、GitHubとVercel、Supabaseを役割別に選ぶための3つの経路を描いた図解" loading="eager" decoding="async">
  <figcaption>「何GBあるか」ではなく、「止まったときに何を戻せる必要があるか」から考えます。</figcaption>
</figure>

## 最初の判断軸は「容量」ではなく、共有・復旧・バックアップ

<figure>
  <img src="/img/blog-sites-runtime-decision-criteria-20260810.png" alt="共有、クローン、復旧、バックアップの4つを基準にデータの置き場所を選ぶ図解" loading="lazy" decoding="async">
  <figcaption>同じ小さなデータでも、誰が使い、止まると何が困るかで必要な構成は変わります。</figcaption>
</figure>

正解は、すべてを一つのサービスに寄せることではありません。まずは、次の3段階で考えると判断しやすくなります。

- **早く見せたいだけ**なら、Sitesで仮サイトや匿名データの試作をつくる。
- **続けて直したい**なら、GitHubにコードと手順を残し、Vercelで公開する。
- **人の情報や日々の業務を預かる**なら、Supabaseの認証・DB・Storageを加え、権限と復元まで設計する。

たとえば、画像1枚とイベント名だけの案内は、容量が大きくなくても「誰が更新するか」「消えたらどこから戻すか」を決めておく必要があります。反対に、数十MBのAccessファイルでも、顧客・会計・在庫・書類・印刷を支えるなら、容量ではなく業務の重さで考えるべきです。

> **迷ったら、「来月、別のPC・別の人・別のAI開発環境で同じ状態を再現する必要があるか」を先に問います。**

「ある」と答えるなら、コードと手順をGitHubへ置く段階です。さらに、顧客や会員ごとに見える情報が違う、書類を保管する、履歴を戻す必要があるなら、Supabaseまで含めて設計します。

## Sitesは、限定公開の試作・デモに向く

<figure>
  <img src="/img/blog-sites-runtime-safe-pilot-20260810.png" alt="匿名データだけを使った小さな試作サイトを、限られた利用者に見せる様子を表した図解" loading="lazy" decoding="async">
  <figcaption>試作の範囲を小さく切れば、現場で確かめるまでの時間を短くできます。</figcaption>
</figure>

ChatGPT Sitesは、プロンプトからWebサイトや小さなアプリを作り、ホストして共有できる仕組みです。永続データにはD1、ファイルにはR2を使う構成も選べます。ChatGPTでのサインインを使い、ワークスペース内の人だけに見せる設計もできます。

ただし、ここは大事です。OpenAI公式ドキュメントでは、**SitesのデプロイURLはすべて本番デプロイ**とされています。保存したバージョンをレビュー候補として残すことはできますが、URLを発行するなら「本番として見られてよい内容か」を確認する必要があります。一般的な本格ステージング環境と同じ感覚で、外部に出す場所ではありません。

また、Sitesはパブリックベータで、利用可否や上限はプラン・地域・ワークスペース設定で変わります。一部のフレームワーク、プライベートネットワーク、DB、バックグラウンドサービス、ホスティング形態には対応しない場合があります。データレジデンシーにも対応していません。決済を動かす用途や、機微な個人情報を扱う基幹業務を寄せる場所にはしません。

Sitesで安全に小さく試すなら、たとえば次の範囲です。

- 匿名データだけを使う受付画面の試作
- スタッフ向けマニュアル・FAQ
- 顧客情報を持たない小さな集計ダッシュボード
- 講座や地域イベントの仮LP、申込前の案内ページ

この小さな試作が「顧客データを持つ」「複数人で改修する」「PC移設や復旧が必要になる」段階に達したら、GitHub＋Vercelへ移す。それで十分です。

## GitHub＋Vercelは、複数PCでも開発を続けるための土台

<figure>
  <img src="/img/blog-sites-runtime-continuity-backup-20260810.png" alt="ノートPC、GitHubのコード保管、Vercelの公開、Supabaseのデータと書類保管を分けた復旧の図解" loading="lazy" decoding="async">
  <figcaption>コード、公開、データ、秘密情報は役割が違うため、復旧方法も分けて持ちます。</figcaption>
</figure>

GitHubは、コードと変更履歴を残す場所です。リポジトリをクローンすれば、別のPCにコードと履歴を取り出せます。VercelをGitHubとつなげておけば、ブランチごとのプレビューと、本番ブランチへの反映を分けて公開できます。

この組み合わせは、次のような場面で効きます。

- 自宅PCと事務所PCの両方で続きを作りたい
- Codex、Claude Code、Cursorなど、複数の開発環境で引き継ぎたい
- 修正前の状態に戻したい
- 家族、スタッフ、外部の開発者と安全に共有したい

ただし、GitHubをクローンできても、業務データそのものが戻るわけではありません。PC故障への備えは、構成に関係なく次の4つを分けます。

```text
GitHub            コード・README・DBマイグレーション
Vercel            Web公開設定
Supabase          DB・認証・書類Storage・バックアップ
安全な保管先       .env・秘密鍵・復旧手順
```

GitHubへ入れるのは、コードと設定のひな型だけです。顧客DB、Accessファイル、CSV移行データ、PDF、`.env`、秘密鍵はGitHubに入れません。復旧手順のREADMEには「どの順番で環境変数を入れ、DBを復元し、公開を確認するか」を書き、秘密そのものは安全な保管先に分けます。

## 顧客・会計・書類を扱うなら、Supabaseを加えて復元まで運用する

<figure>
  <img src="/img/blog-sites-runtime-core-system-20260810.png" alt="顧客情報、会計、在庫、PDF、会員情報を権限付きのデータベースと書類保管へ分けた図解" loading="lazy" decoding="async">
  <figcaption>本格稼働では、保存先だけでなく、誰が見て、誰が戻せるかを決めます。</figcaption>
</figure>

顧客情報、売上、在庫、会員情報、PDFなどを扱い始めたら、GitHub＋VercelにSupabaseを加えます。ここで重要なのは「Supabaseを入れれば安全」ではありません。認証、テーブルごとのRLS（行レベルセキュリティ）、Storageのアクセス方針、管理者権限、バックアップと復元確認を、業務に合わせて決めることです。

SupabaseのPostgresは、Auth、Storage、Realtimeなどの土台です。公式ドキュメントでは、毎日のDBバックアップと、有料プランでのポイントインタイム復元が案内されています。一方で、Storageに置いたオブジェクトはDBバックアップには含まれません。書類や写真を預かるなら、Storage側の保管・バックアップ・復元確認も別に運用します。

この構成が向くのは、次のような仕事です。

- 会員ごと、スタッフごと、拠点ごとに見えるデータが違う
- 顧客の連絡先、申込履歴、受講記録、売上・在庫を扱う
- PDF、同意書、写真などの書類を権限付きで保管する
- 変更履歴や復元手順を残し、止まったときの対応を決めておきたい

特にStorageは、RLSポリシーを設計しない限りアップロードを許可しない仕組みです。公開バケット、スタッフだけの書類、会員本人だけが見られる書類を混ぜず、用途ごとに分けることが実務では大切です。

## Climbは、容量ではなく基幹業務の要件で選ぶ

<figure>
  <img src="/img/blog-sites-runtime-climb-core-boundary-20260810.png" alt="顧客、会計、在庫、書類、印刷を扱う基幹業務を、安全なデータ基盤へ置く考え方を表した図解" loading="lazy" decoding="async">
  <figcaption>基幹業務では、ファイルの大きさより、日々の入力・権限・復元・印刷が止まらないことが重要です。</figcaption>
</figure>

Climbでは、Access本体が約32MB、移行用データ全体が約246MBでした。容量だけを見ればSitesの候補に見えるかもしれません。しかし実際に扱うのは、顧客情報、会計、在庫、書類、権限、印刷です。選定理由は容量ではなく、業務要件です。

したがって、Climbの基幹は**GitHub＋Vercel＋Supabaseのまま**が適切です。コードと移行手順はGitHub、公開・画面はVercel、顧客データと権限付きの書類保管はSupabaseに分けます。決済、会計、予約など、すでに専門サービスが正本として動いている領域は、無理に置き換えず、必要な連携だけをつくります。

Sitesを使うなら、基幹の代わりではなく、次のような周辺の試作に限ります。

1. 匿名のサンプルデータだけを使った受付画面
2. スタッフ向けの手順書・FAQ
3. 顧客情報を持たない小さな集計画面
4. 講座や地域イベントの仮LP

その試作に顧客データ、複数人の改修、PC移設、復旧手順のどれかが加わったら、GitHub＋Vercelへ移します。さらに権限・書類・会員・業務データが加わったら、Supabaseを正本にして、バックアップから実際に戻せるかまで確認します。

### よくある質問

**Q. GitHubをクローンできれば、PC故障には備えられますか？**

コードと履歴には備えられます。しかし、DB、Storageの書類、Vercelの環境変数、`.env`、秘密鍵は別です。少なくとも年に一度ではなく、変更したタイミングごとに「別PCへクローンできるか」「DBを戻せるか」「書類を取り出せるか」を小さく確認します。

**Q. Sitesで永続データを使ってはいけませんか？**

いいえ。SitesではD1やR2を使う構成があります。ただし、デプロイURLは本番として扱われ、対応範囲や上限も変動します。匿名データの試作や限定公開の小さなツールに範囲を切り、重要データや本番業務を抱え込ませない、という使い分けが実務的です。

<div class="publishing-cta">
  <strong>「何をどこに置くか」を先に決めると、AIで作るサイトは速く、引き継ぎやすくなります。</strong>
  <p>AI相談では、公開ページ、顧客・会員データ、書類、決済・予約、復旧手順を分け、地域の事業者・学校・福祉の現場で続けられる構成を一緒に整理します。</p>
  <p><a href="/#contact">AI相談へ相談する</a> ・ <a href="/blog/index.html">AI相談のブログ一覧を読む</a></p>
</div>

### 参考にした公式情報

- [OpenAI：Sites](https://learn.chatgpt.com/docs/sites)
- [GitHub Docs：Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
- [Vercel：Deploying Git Repositories with Vercel](https://vercel.com/docs/git)
- [Supabase：Database overview](https://supabase.com/docs/guides/database/overview)
- [Supabase：Storage Access Control](https://supabase.com/docs/guides/storage/security/access-control)

<p class="publishing-note">※機能、上限、対応範囲は2026年8月10日時点で公式情報を確認しています。顧客情報・会計・決済・書類を扱う前には、対象業務の権限、契約条件、バックアップ、復元手順を個別に確認してください。</p>

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
