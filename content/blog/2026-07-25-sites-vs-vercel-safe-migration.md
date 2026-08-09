---
title: "ChatGPT SitesとVercel、どちらを選ぶ？GitHubを残す安全な移行ガイド"
date: 2026-07-25
authorship_note: "この記事は、運営者が独自に考え、思考したものを、AIを使って読みやすくしました。"
role: ブログ / AI初心者・地域事業者・個人事業主向け
gen_by: 由井 辰美 / AI相談
summary: ChatGPT SitesとVercelの違いを、料金、GitHub、データベース、引継ぎ、独自ドメインからやさしく比較。Sitesだけで使う手順と、GitHubを原本に残す手順を分けて説明します。
image: /img/blog-sites-vs-vercel-hero-20260725.webp
hero_image: true
image_alt: ChatGPT SitesとVercelの公開方法を比べ、GitHubを残した安全な移行経路を選ぶイメージ
image_caption: GitHubを安全網として残せば、公開先を変えても、記録・確認・公開の基本手順を続けられます。
---

「いまはVercelを使っているけれど、ChatGPT Sitesへ移せば管理が楽になるのでは？」

「GitHubを使わなくてよくなるなら、料金も手間も減る？」

「でも、ほかの人への引継ぎや、同じサイトのクローンで困らない？」

Sitesを知ると、こうした疑問が出てきます。難しそうに見えますが、先に結論を言うと、次のように考えれば大丈夫です。

> **Sitesは、AIと相談しながら素早く作って公開するのが得意です。Vercelは、GitHubやデータベースと組み合わせ、本番のWebアプリを細かく管理するのが得意です。**

そして、SitesではGitHubの操作を省くことも、GitHubを正式な原本として残すこともできます。同じなのは「記録して、確認してから公開する」という考え方です。実際に押すボタンや手順は同じではありません。

## Sitesは公開を簡単にし、Vercelは運用を細かく管理できる

<figure>
  <img src="/img/blog-sites-vs-vercel-section-1-compare-20260725.webp" alt="AIとの対話からすぐ公開するSitesと、GitHubやデータベースを細かく管理するVercelを比べたイメージ" loading="eager" decoding="async">
  <figcaption>どちらが上かではなく、簡単に始めたいのか、細かく管理したいのかで選びます。</figcaption>
</figure>

ChatGPT Sitesは、ChatGPTのWebやデスクトップアプリから、サイトや軽いWebアプリを作成、修正、保存、公開できる仕組みです。別の公開サービスを用意しなくても、AIへ変更を頼み、そのまま公開へ進めます。

Vercelは、GitHubなどに保存したコードを受け取り、自動でWebサイトやWebアプリを公開するサービスです。変更前の確認用URL、本番URL、環境変数、実行ログなどを細かく管理できます。

身近な言葉にすると、次の違いです。

| 比べること | ChatGPT Sites | Vercel |
|---|---|---|
| 得意なこと | AIと相談して、早く形にする | 本番サイトを細かく管理する |
| 公開方法 | ChatGPTから保存・公開 | Gitの更新や管理画面から公開 |
| 公開前の確認 | バージョンを保存して確認 | ブランチやPull RequestごとのPreview |
| GitHub | なくても始められる。残すこともできる | 連携すると自動公開しやすい |
| データ保存 | D1、R2などSites対応の保存機能 | 外部DBを接続。Supabase連携が充実 |
| 向く用途 | 案内ページ、試作品、軽い社内ツール | 予約、会員、業務管理、継続運用するアプリ |

Sitesは現在パブリックベータです。有料プラン内で利用できますが、プラン別の上限があり、上限や対応機能は変わる可能性があります。

VercelはHobbyが月額0ドル、Proが月額20ドルからです。ただし、Vercel自身もHobbyを個人・非商用向け、Proを仕事や事業向けと案内しています。料金だけでなく、何を公開するかで判断する必要があります。

## Sitesでは操作が変わるが、記録・確認・公開の考え方は同じ

<figure>
  <img src="/img/blog-sites-vs-vercel-section-2-workflow-corrected-20260725.webp" alt="Sitesだけで運用する手順と、GitHubを原本に残して運用する手順を上下に分けた比較図" loading="lazy" decoding="async">
  <figcaption>SitesだけならWorktree・Commit・Pull Requestは日常操作に出ません。GitHubを原本に残す場合は、これまでの手順を続けられます。</figcaption>
</figure>

ここは、いちばん誤解しやすいところです。

最初に見ていただいた「Worktree → Commit → Pull Request → Deploy」は、GitとGitHubを使う開発の流れです。**Sitesだけで作成・修正する場合に、この4つを毎回自分で操作するわけではありません。**

変わらないのは操作名ではなく、次の考え方です。

1. **変更を分ける**
   Sitesだけなら、AIへ一つずつ修正を頼みます。GitHubを使うならWorktreeで作業を分けます。

2. **変更を記録する**
   Sitesだけなら保存バージョン、GitHubを使うならCommitで記録します。

3. **公開前に確認する**
   Sitesだけなら保存したバージョン、GitHubを使うならPull RequestやPreviewで確認します。

4. **本番へ公開する**
   確認後にSitesへ公開します。Vercelを使う場合は、mainへの反映後にVercelが自動公開します。

実際の流れは、次のように分かれます。

| 運用方法 | 日常の流れ | Worktree・Commit・Pull Request |
|---|---|---|
| Sitesだけで運用 | AIに変更を依頼 → バージョンを保存 → 内容を確認 → Sitesへ公開 | 自分で毎回操作する必要はない |
| GitHubを原本に残してSitesへ公開 | Worktree → Commit → Pull Request → Sites用バージョンを保存 → 公開 | これまでどおり使える |
| GitHubからVercelへ公開 | Worktree → Commit → Pull Request → mainへ反映 → Vercelが自動公開 | これまでどおり使う |

CodexがローカルのプロジェクトからSitesへ公開するときは、裏側で検証済みソースをGitのCommitと結びつけて保存します。ただし、これは**利用者が毎回GitHubのPull Request画面を操作する**という意味ではありません。

なお、Sitesでは公開して発行されたURLはすべて本番公開です。確認だけしたいときは、すぐ公開せず、先にバージョンを保存して確認します。

Worktree、Commit、Pull Requestの違いは、別記事の[Codexで安全に直して公開する：Worktree・Git・PRの役割](/blog/2026-07-24-codex-worktree-git-deploy-guide.html)でも図解しています。

## 料金だけでなく、データベース・引継ぎ・クローンまで比べて決める

<figure>
  <img src="/img/blog-sites-vs-vercel-section-3-assets-20260725.webp" alt="料金、データベース、引継ぎ、クローンの4項目を並べて公開先を判断するイメージ" loading="lazy" decoding="async">
  <figcaption>毎月の料金だけで決めず、データと開発資産を将来も取り出せるかまで確認します。</figcaption>
</figure>

Sitesへ移れば、Vercel Proの料金を減らせる可能性はあります。ただし、「Sitesなら追加料金なしで無制限」とは限りません。現在はベータ期間中で、ChatGPTのプランごとにSites全体の利用上限があります。

特に業務システムでは、次の4点を一緒に見ます。

### データベース

Sitesには、表のようなデータを保存するD1と、画像やファイルを保存するR2があります。

Vercel自体は本格的なデータベースではありません。Supabaseなどを接続して使います。SupabaseはPostgreSQL、ログイン認証、ファイル保存、利用者ごとの閲覧制限などをまとめて扱えます。VercelとSupabaseには、環境変数やPreview用ブランチを連携する仕組みがあります。

### 引継ぎとクローン

GitHubに正式なソースを残しておけば、別のパソコンや別の開発者がリポジトリをクローンできます。過去の変更履歴も含めて取得できるため、他社向けの複製や担当者変更が楽になります。

Sitesを使う場合も、元のローカルプロジェクトをGitHubへ残せます。

大切なのは、**Sitesを使うかではなく、GitHubを原本として残すか**です。クローンや引継ぎの可能性があるなら、GitHubは残す方が安全です。

### 安全性とERP

Sitesは軽いWebアプリや社内ツールも作れますが、現在はベータです。OpenAIは、一部のフレームワーク、外部データベース、バックグラウンド処理などが対応しない場合があると案内しています。

また、現時点のSitesでは、カード情報や医療上の保護情報を扱うこと、金融取引を実行する仕組みは禁止されています。データを特定地域に保存するデータレジデンシーにも対応していません。

そのため、案内ページや試作品はSitesで試しやすい一方、在庫、受注、決済、重要な個人情報を扱うERPは、いきなり全面移行せず、機能ごとに確認する必要があります。

### 速度と稼働保証

通常の案内ページでは、どちらも十分な速さを期待できます。ただし、本当に必要なのは、同じページと同じ利用条件で測ることです。

VercelはEnterpriseで99.99%のSLAを案内しています。Sitesには、現時点で同じ形の専用SLAが公開されていません。止まると業務へ大きな影響が出る場合は、契約上の保証、監視、復旧方法まで比べます。

## 独自ドメインは移管せず、DNSの接続先変更から試すのが安全

<figure>
  <img src="/img/blog-sites-vs-vercel-section-4-domain-20260725.webp" alt="同じ独自ドメインの行き先だけをVercelからSitesへ切り替えるイメージ" loading="lazy" decoding="async">
  <figcaption>住所である独自ドメインを手放さず、案内先だけをVercelからSitesへ変えます。</figcaption>
</figure>

独自ドメインは、インターネット上の住所です。VercelやSitesは、その住所から案内される建物のようなものです。

Sitesへ移るために、ドメインの管理会社まで同時に変える必要はありません。

```text
移行前
独自ドメイン → Vercel

試験移行後
同じ独自ドメイン → Sites
```

OpenAIの公式案内では、Sitesはドメインを販売・登録しません。すでに持っているドメインを追加し、指定されたDNSレコードをドメイン管理会社で設定します。

DNSは「この住所へ来た人を、どのサービスへ案内するか」という設定です。

安全に切り替える順番は、次のとおりです。

1. Sitesの仮URLで表示と動作を完成させる
2. 現在のDNS設定を記録する
3. Webサイトに関係するAやCNAMEだけを変更する
4. 独自ドメインでSites版が開くことを確認する
5. 問題があれば、保存したVercel用設定へ戻す

メールに使うMX、SPF、DKIM、DMARCなどは、Webサイトだけを移すときに削除しません。ここを消すと、独自ドメインのメールへ影響する可能性があります。

Vercelで購入したドメインも、Sitesへ接続するだけなら、すぐに別会社へ移管する必要はありません。Vercelをドメイン管理にも使わなくなると決めてから、別の管理会社への移管を検討できます。

つまり、**サイト移行とドメイン移管は別の作業**です。同時に行わない方が、問題が起きたときに原因を見つけやすくなります。

## GitHubとVercelを残したまま、小さなサイトでSitesを試す

<figure>
  <img src="/img/blog-sites-vs-vercel-section-5-pilot-20260725.webp" alt="小さな案内ページからSitesを試し、確認後に必要な機能だけ段階的に移すイメージ" loading="lazy" decoding="async">
  <figcaption>最初から全部を動かさず、止まっても困らない小さなページで使い勝手を確かめます。</figcaption>
</figure>

Sitesが自分の仕事に合うかは、説明を読むだけでは決められません。小さく試すのが一番確実です。

最初の候補には、次のようなページが向いています。

- 講習会や地域交流会の案内
- 商品やサービスの説明ページ
- 個人情報を保存しない簡単な診断
- 社内で見る軽い資料ページ
- 新しい業務アプリの画面だけを見せる試作品

試すときは、次の順番にします。

1. GitHubとVercelの現在版を残す
2. 個人情報や決済を扱わない1ページをSitesへ移す
3. PCとスマホで表示速度と操作を確認する
4. 修正、バージョン保存、元の版へ戻す手順を試す
5. 別のパソコンや開発者がGitHubから再現できるか確認する
6. 問題がなければ独自ドメインの接続先を切り替える
7. 数週間使ってから、Vercelの縮小を判断する

判断の目安は、次のとおりです。

| 目的 | 向きやすい選択 |
|---|---|
| AIで案内ページをすぐ作りたい | Sites |
| 一人で小さなツールを試したい | Sites |
| 予約、会員、在庫、受注を長く運用したい | Vercel＋Supabaseを基本に検討 |
| 他社へ引き継ぐ、顧客ごとに複製する | GitHubを必ず残す |
| 管理を減らしつつ、戻れるようにしたい | GitHub＋Sites、Vercelは移行中の予備 |

最終的に大切なのは、サービス名ではありません。

**現場で使えるか。続けられるか。困ったときに戻せるか。ほかの人へ渡せるか。**

この4つを確認できれば、Sitesの簡単さを使いながら、GitHubの安全性も残せます。

### よくある質問

**Q. Sitesへ移るならGitHubは不要ですか？**

プロンプトだけで作る小さなSiteなら、GitHubなしでも始められます。ただし、引継ぎ、クローン、詳細な変更履歴が必要なら、GitHubを原本として残す方が安全です。

**Q. SitesでもPull Requestは必要ですか？**

必須ではありません。一人で小さく直す場合は、Commit後にSitesで保存したバージョンを確認できます。複数人の確認や正式な承認が必要なら、GitHubのPull Requestを残します。

**Q. SitesからSupabaseを使えますか？**

外部サービスとの接続は、Sitesの実行環境と対象プロジェクトの構成によって確認が必要です。VercelとSupabaseの公式連携と同じ機能が、そのままSitesでも使えるとは限りません。Sitesでは、まずD1とR2が公式の保存方法として案内されています。

**Q. Sitesへ移ったら、すぐVercelを解約してよいですか？**

おすすめしません。API、Cron、環境変数、Supabase連携、独自ドメイン、メール設定、復旧手順を確認し、数週間の試験運用後に判断します。

<div class="publishing-cta">
  <strong>公開先で迷ったら、サービスを決める前に「何を預けるか」を整理します。</strong>
  <p>AI相談では、現在のサイト、GitHub、Vercel、Supabase、独自ドメインを確認し、残すものと小さく試すものを一緒に分けます。</p>
  <p><a href="/#contact">AI相談へ相談する</a> ・ <a href="/blog/2026-07-22-ai-site-publishing-stages.html">公開の3段階を先に読む</a></p>
</div>

### 参考にした公式情報

- [OpenAI：ChatGPT Sites公式ガイド](https://learn.chatgpt.com/docs/sites)
- [OpenAI：ChatGPT Sitesの作成と管理](https://help.openai.com/en/articles/20001339)
- [Vercel：Gitリポジトリからのデプロイ](https://vercel.com/docs/git)
- [Vercel：料金プラン](https://vercel.com/pricing)
- [Vercel：セキュリティ概要](https://vercel.com/docs/security)
- [Vercel：独自ドメイン設定](https://vercel.com/docs/domains/set-up-custom-domain)
- [Vercel：ドメイン移管](https://vercel.com/docs/domains/working-with-domains/transfer-your-domain)
- [Supabase：Vercelとのブランチ連携](https://supabase.com/docs/guides/deployment/branching/integrations)
- [GitHub：リポジトリのクローン](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

<p class="publishing-note">※機能、上限、料金は2026年7月25日時点の公式情報を確認しています。実際の移行前に、利用中プランと対象プロジェクトの最新条件を再確認してください。</p>

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
