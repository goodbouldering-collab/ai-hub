---
title: "サイト公開は、ChatGPT Sites、クラウドフレア、Vercel、どれがいい？完全比較とGitHubとの関係"
date: 2026-07-25
date_modified: 2026-08-28
authorship_note: "※内容は運営者が考え、AIで整えています。"
role: ブログ / AI初心者・地域事業者・個人事業主向け
gen_by: 由井 辰美 / AI相談
summary: ChatGPT Sites、Cloudflare、Vercelを、作りやすさ、料金、確認URL、データ、独自ドメイン、GitHubとの関係で比較。地域事業者が安全に選び、移行する手順まで解説します。
image: /img/blog-sites-cloudflare-vercel-hero-20260828.webp
hero_image: true
image_alt: ChatGPT Sites、Cloudflare、Vercelの3つの公開先と、共通の原本になるGitHubを比較するイメージ
image_caption: 公開先は目的で選び、GitHubは原本と戻り道として残すと、安全に試して切り替えられます。
---

「AIで作った案内ページを、難しい設定なしですぐ公開したい」

「Cloudflareは速いと聞くけれど、Vercelと何が違う？」

「公開先を変えたら、GitHubはもう要らない？」

サイト公開で迷う原因は、3つのサービスを同じ種類のものとして比べてしまうことです。先に結論を言うと、得意分野は次のように違います。

> **AIと相談しながら最短で公開するならChatGPT Sites。静的サイトやAPIを世界中へ効率よく配信するならCloudflare。GitHubと連携してWebアプリを継続開発するならVercelが選びやすいです。**

そして、どれを選んでもGitHubは残せます。GitHubは公開先ではなく、サイトのコード、変更履歴、引継ぎに使う「原本」です。

## 結論：早さはSites、配信基盤はCloudflare、Webアプリ運用はVercelが選びやすい

<figure>
  <img src="/img/blog-sites-cloudflare-vercel-section-1-compare-20260828.webp" alt="ChatGPT Sites、Cloudflare、Vercelの得意分野を3つに分けて比較したイメージ" loading="eager" decoding="async">
  <figcaption>優劣ではなく、誰が更新し、何を動かし、止まったときにどこまで困るかで選びます。</figcaption>
</figure>

まずは全体像です。

| 比べること | ChatGPT Sites | Cloudflare | Vercel |
|---|---|---|---|
| いちばんの強み | AIとの対話から作成・修正・公開まで進めやすい | 世界各地のネットワークで静的ファイルや処理を配信しやすい | Git連携、確認用URL、Webアプリ運用がまとまっている |
| 向く人 | コードやサーバー設定を減らしたい人 | 配信速度、通信量、セキュリティを重視する人 | GitHubを使い、継続的に開発・改善する人 |
| 向く用途 | 講座・イベント案内、試作品、軽い社内ツール | コーポレートサイト、ブログ、LP、軽量API | Next.js、予約、会員、管理画面、業務アプリ |
| 公開前の確認 | バージョンを保存して確認してから公開 | Git連携のPreviewや非本番バージョン | ブランチ・Pull RequestごとのPreview |
| GitHub | なくても始められる。原本として残すこともできる | GitHub/GitLabから自動ビルド・公開できる | GitHub/GitLab/Bitbucketから自動公開できる |
| 注意点 | パブリックベータ。対応外の構成や扱えないデータがある | Workers、Pages、DNSなど選択肢が多く、最初の設計が必要 | 商用利用、実行量、チーム人数で費用を確認する |

ChatGPT Sitesは、ChatGPTでサイトを作り、修正し、そのまま公開できる仕組みです。別のホスティング管理画面を往復しにくいのが魅力です。ただし現在はパブリックベータで、公開すると発行されたURLは本番扱いになります。確認段階では、先にバージョンを保存して内容を見る運用が安全です。

Cloudflareで新しく静的サイトを始める場合、公式は**Workers Static Assets**を案内しています。従来のCloudflare Pagesも継続利用できますが、新機能への投資はWorkers側が中心です。HTMLや画像だけのサイトから、APIや認証を含む処理まで段階的に広げやすいのが特徴です。

VercelはGitの変更と公開を結びつけるのが得意です。Pull Requestごとに確認用URLができ、mainなど本番ブランチへ反映すると本番公開へ進めます。Next.jsを使うサイトや、画面とAPIを一緒に改善する業務アプリでは分かりやすい選択です。

## GitHubは3つの公開先に共通して残せる「原本」と「戻り道」

<figure>
  <img src="/img/blog-sites-vs-vercel-section-2-workflow-corrected-20260725.webp" alt="GitHubを原本として残し、確認後に公開先へ反映する安全な流れ" loading="lazy" decoding="async">
  <figcaption>GitHubを残す目的は公開そのものではなく、変更履歴、復旧、引継ぎを失わないことです。</figcaption>
</figure>

GitHubと公開サービスの役割を分けると、判断が楽になります。

| 役割 | 主に担当するもの |
|---|---|
| GitHub | コード、文章、画像の参照元、変更履歴、レビュー、引継ぎ |
| ChatGPT Sites | AIとの対話による作成・修正とSites上での公開 |
| Cloudflare | 静的ファイル、Worker処理、DNS、CDN、セキュリティ |
| Vercel | Git連携のビルド、Preview、本番デプロイ、Functions |

ChatGPT Sitesだけでも小さなサイトは始められます。しかし、別のAI開発ツールでも直したい、制作会社へ引き継ぎたい、顧客ごとに複製したい、過去の版へ確実に戻したいなら、GitHubを原本として残す方が安全です。

CloudflareとVercelはGitHub連携が明確です。GitHubへ更新を送ると、自動でビルドと公開を行えます。ChatGPT Sitesでもローカルプロジェクトから扱う場合は、公開するプロジェクト版をGitのコミットと関連付けて管理できます。

ただし、**GitHubへコードを置いただけでは、サイト全体のバックアップにはなりません。** 次のものは別に保存・復旧確認が必要です。

- 顧客、予約、注文などのデータベース
- 利用者がアップロードした画像やPDF
- APIキー、パスワード、環境変数
- 独自ドメインのDNS設定
- 決済、メール、外部サービス側の設定

「GitHubがあるから安心」ではなく、「コードはGitHub、データはDBのバックアップ、秘密情報は安全な保管先」と役割を分けます。

## 料金・確認URL・DB・独自ドメインまで比べると違いが見える

<figure>
  <img src="/img/blog-sites-vs-vercel-section-3-assets-20260725.webp" alt="料金、データベース、引継ぎ、クローンまで含めてサイト公開先を比較するイメージ" loading="lazy" decoding="async">
  <figcaption>月額料金だけでなく、更新、データ、復旧、引継ぎに必要な時間まで含めて比べます。</figcaption>
</figure>

2026年8月28日時点の公式情報を、実務で迷いやすい項目に絞ると次のようになります。料金や上限は変わるため、契約前には必ず公式ページで再確認してください。

| 比べること | ChatGPT Sites | Cloudflare | Vercel |
|---|---|---|---|
| 入口の料金 | 対象のChatGPTプラン内。プラン単位の利用上限あり | Workers Freeあり。Paidは月5ドルから | Hobbyは0ドル。Proは月20ドルからで追加利用料あり |
| 商用利用 | 公開内容と利用規約、プラン上限を確認 | Free/Paidの上限と用途を確認 | Hobbyは個人・非商用向け。仕事はProを基本に検討 |
| 静的ファイル | Sitesとして配信 | Static Assetsは無料・無制限として案内 | プランの転送量や上限を確認 |
| 公開前確認 | 保存したバージョンを確認 | Preview URLまたは非本番バージョン | Pull RequestごとのPreview URL |
| サーバー処理 | Sites対応範囲内 | Workersでエッジ処理 | Functionsでサーバー処理 |
| データ保存 | D1、R2などSites対応機能 | D1、R2、KV、Durable Objectsなど | 外部DBやMarketplace連携を利用 |
| 独自ドメイン | 対応環境で既存ドメインを接続 | DNSと配信を一体管理しやすい | 既存ドメインを接続できる |
| 得意なフレームワーク | 対応範囲に制約あり | 静的サイトと対応Worker構成 | Next.jsを中心に多くの構成へ対応 |

ChatGPT Sitesでは、表のようなデータにD1、画像やファイルにR2を使えます。一方で、外部データベース、バックグラウンド処理、特定のフレームワークなど、対応しない構成があります。また現時点では、医療上の保護情報、カード情報、金融取引を扱う用途には使えません。予約、決済、重要な個人情報を含むシステムは、案内ページと本体を分けて考える必要があります。

Cloudflareは、静的ファイルを低コストで配りたいときに強みがあります。必要になればWorkersで処理を追加し、D1やR2を組み合わせられます。ただし、CPU時間、動的リクエスト、保存量などはプラン上限や従量料金の対象です。

Vercelは、コード更新からPreview、本番公開までの流れを整えやすい反面、商用サイトではProを前提に費用を見ます。Supabaseなどの外部データベース、認証、ストレージと組み合わせる場合は、Vercelだけでなく接続先の料金と復旧方法も確認します。

## 地域事業者はサイトの役割と「止まった時の影響」で選ぶ

<figure>
  <img src="/img/blog-sites-vs-vercel-section-5-pilot-20260725.webp" alt="止まっても困らない小さなページから新しい公開先を試すイメージ" loading="lazy" decoding="async">
  <figcaption>最初から全体を移さず、影響の小さい1ページで更新と復旧を試します。</figcaption>
</figure>

一般論より、現場の役割で決める方が失敗しません。

| 現場の目的 | 第一候補 | 理由 |
|---|---|---|
| 講演会、地域交流会、AI講座の告知をすぐ出す | ChatGPT Sites | 会話しながら文章と見た目を整え、公開まで進めやすい |
| 店舗や団体の静的な公式サイトを軽く運営する | Cloudflare | 静的配信、独自ドメイン、セキュリティをまとめやすい |
| 予約、会員、管理画面を継続改善する | Vercel＋外部DB | GitHub、Preview、API、ログを一つの開発フローにしやすい |
| 在庫、受注、決済、個人情報を扱う | 要件ごとに設計 | 公開先だけでなく、認証、DB、監査、バックアップが必要 |
| 他社や次の担当者へ渡す | GitHubを残す | コードと履歴を再現・レビュー・複製しやすい |

たとえば講座の募集ページなら、ChatGPT Sitesで早く試し、申込は既存フォームへつなぐ方法があります。小さな地域団体の公式サイトなら、Cloudflareで静的に配信し、更新はGitHubから行う形が堅実です。予約や会員機能を何年も改善するなら、Vercelと外部DBを使い、Pull Requestごとに確認する方が運用しやすくなります。

AI相談のサイトは、現在GitHubを原本にしてVercelで公開しています。Codex、Claude Code、Cursorなど複数のAI開発ツールから同じソースを扱え、変更履歴と本番を分けられるためです。これはVercelが常に最善という意味ではなく、継続開発する現在の用途に合っているという判断です。

## 安全な移行はGitHubと現行サイトを残し、1ページから試す

<figure>
  <img src="/img/blog-sites-vs-vercel-section-4-domain-20260725.webp" alt="現行サイトとGitHubを残し、独自ドメインの接続先を段階的に切り替えるイメージ" loading="lazy" decoding="async">
  <figcaption>公開先の変更とドメイン移管を分ければ、問題が起きても元へ戻しやすくなります。</figcaption>
</figure>

移行では「新しいサービスへ全部移す」より、「戻れる状態のまま小さく試す」ことを優先します。

1. **現状を一覧にする**
   ページ、API、フォーム、Cron、DB、画像、環境変数、DNS、メール設定を分けて記録します。

2. **GitHubと復旧用コピーを残す**
   コードはGitHubへ保存し、DBとストレージはそれぞれエクスポートやバックアップを確認します。

3. **止まっても困らない1ページを選ぶ**
   講座案内や会社紹介など、個人情報と決済を扱わないページから試します。

4. **仮URLとスマホで確認する**
   文字、画像、リンク、フォーム、表示速度、横はみ出しをPCとスマホで確認します。

5. **更新と復旧を一度実演する**
   文章を直して再公開し、前の版へ戻せるか、別の担当者がGitHubから再現できるか試します。

6. **独自ドメインは接続先だけ変える**
   ドメイン管理会社の移管は後回しにし、Web用のAやCNAMEを変更します。メール用のMX、SPF、DKIM、DMARCは消しません。

7. **現行サービスを数週間残す**
   問題なく運用でき、復旧手順も確認してから、旧サービスの縮小や解約を判断します。

サイト移行とドメイン移管、データ移行を同日に行うと、問題の原因を特定しにくくなります。一つずつ変えれば、利用者への影響を小さくできます。

### よくある質問

**Q. Cloudflare PagesとWorkers、どちらを選びますか？**

新規プロジェクトなら、Cloudflareが推奨するWorkers Static Assetsを第一候補にします。既存のPagesプロジェクトを急いで移す必要はありません。今の構成、ビルド方法、将来追加する処理を見て判断します。

**Q. ChatGPT Sitesを使うならGitHubは不要ですか？**

小さな試作品ならGitHubなしでも始められます。引継ぎ、複製、複数のAI開発ツールでの編集、詳細な履歴が必要ならGitHubを原本として残します。

**Q. CloudflareとVercelは、どちらが速いですか？**

静的ページだけなら、どちらも十分速くできます。画像サイズ、キャッシュ、アクセス地域、サーバー処理で結果が変わるため、同じページを同じ条件で測らずに断定しません。

**Q. 料金が0円のサービスを選べばよいですか？**

料金だけでは決めません。更新にかかる時間、商用利用条件、障害時の復旧、データの取り出し、担当者への引継ぎまで含めます。毎月数ドルを減らして、復旧に何日もかかる状態は得ではありません。

**Q. 結局、迷ったらどれを選びますか？**

まずGitHubへ原本を残します。そのうえで、告知や試作品はSites、静的な公式サイトはCloudflare、継続開発するWebアプリはVercelを起点に比較します。重要データを扱う場合は、公開先より先に認証、DB、バックアップを決めます。

<div class="publishing-cta">
  <strong>公開先で迷ったら、サービス名ではなく「誰が更新し、何が止まると困るか」から整理します。</strong>
  <p>AI相談では、現在のサイト、GitHub、Cloudflare、Vercel、データベース、独自ドメインを確認し、残すものと小さく試すものを一緒に分けます。</p>
  <p><a href="/#contact">AI相談へ相談する</a> ・ <a href="/blog/2026-07-22-ai-site-publishing-stages.html">公開の3段階を先に読む</a></p>
</div>

### 参考にした公式情報

- [OpenAI：ChatGPT Sites公式ガイド](https://learn.chatgpt.com/docs/sites)
- [OpenAI：ChatGPT Sitesで社内アプリを作る](https://learn.chatgpt.com/use-cases/build-and-deploy-internal-apps)
- [Cloudflare：Workersのベストプラクティス](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
- [Cloudflare：Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [Cloudflare：Git連携のビルドとデプロイ](https://developers.cloudflare.com/workers/ci-cd/builds/)
- [Cloudflare：Workersの料金](https://developers.cloudflare.com/workers/platform/pricing/)
- [Vercel：Gitリポジトリからのデプロイ](https://vercel.com/docs/git)
- [Vercel：料金プラン](https://vercel.com/pricing)
- [GitHub：リポジトリのバックアップ](https://docs.github.com/en/repositories/archiving-a-github-repository/backing-up-a-repository)

<p class="publishing-note">※機能、上限、料金は2026年8月28日時点の公式情報を確認しています。実際の契約・移行前に、利用中プランと対象プロジェクトの最新条件を再確認してください。</p>

<style>
html,body{max-width:100%;overflow-x:hidden}
main>header h1{overflow-wrap:anywhere}
.content-wrap table{display:block;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.content-wrap pre{max-width:100%;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word}
.publishing-cta{margin:34px 0 18px;padding:24px;border:1px solid rgba(7,95,200,.22);border-radius:14px;background:#f3f8ff}
.publishing-cta strong{display:block;color:#0b3b76;font-size:1.08rem;line-height:1.7}
.publishing-cta p{margin:10px 0 0}
.publishing-cta a{font-weight:800}
.publishing-note{margin-top:22px;color:#5f6f82;font-size:.9rem}
@media(max-width:840px){
  .generated-mobile-nav.open{height:calc(100vh - 64px)!important;height:calc(100dvh - 64px)!important}
}
@media(max-width:640px){.publishing-cta{padding:18px}}
</style>
