---
title: "ChatGPT Sites・クラウドフレア・Vercel比較｜サイト公開の極意はGitHubを残す"
date: 2026-07-25
date_modified: 2026-08-28
authorship_note: "※内容は運営者が考え、AIで整えています。"
role: ブログ / AI初心者・地域事業者・個人事業主向け
gen_by: 由井 辰美 / AI相談
summary: ChatGPT Sites、Cloudflare、Vercelを2026年の最新仕様で比較。Cloudflare ProとWorkers Paidの違い、Pagesの現在地、料金・DB・独自ドメイン、GitHubを残す安全な移行まで、サイト公開の極意を実務目線で解説します。
image: /img/blog-sites-cloudflare-vercel-hero-20260828.webp
hero_image: true
image_alt: ChatGPT Sites、Cloudflare、Vercelの3つの公開先と、共通の原本になるGitHubを比較するイメージ
image_caption: 公開先は目的で選び、GitHubは原本と戻り道として残す。これがサービスの変化に振り回されない公開設計です。
---

「Cloudflare Proに上げれば、サイト公開もWorkersも全部有料版になる？」

「Cloudflare Pagesは終わって、今はWorkersへ移さないといけない？」

「AIで作るならChatGPT Sites、仕事ならVercel、と単純に決めてよい？」

2026年のサイト公開が分かりにくいのは、**作る道具、公開する場所、ドメインを守るサービス、コードを保管する場所**が、一つの画面にまとまり始めたからです。特にCloudflareは、同じ会社の中にDNS、CDN、WAF、Workers、D1、R2などがあり、プラン名だけを見ると役割を混同しやすくなっています。

先に結論を言います。

> **最短で形にして共有するならChatGPT Sites。既存サイトの防御・高速化はCloudflare Pro。静的サイトやAPIをCloudflare上で動かすならWorkers Static Assets。GitHub中心にWebアプリを継続開発するならVercelが選びやすいです。**

そして、どれを選んでもサイト公開の極意は同じです。**GitHubを原本として残し、コード、データ、ドメインを同じ日に動かさないこと**です。

この記事は2026年8月28日時点の公式情報を基に、AI初心者、地域事業者、学校・福祉施設、個人事業主が実際に選べるところまで整理します。

## 結論：公開先は「作る・守る・動かす・戻す」の4役で選ぶ

<figure>
  <img src="/img/blog-sites-cloudflare-vercel-section-1-compare-20260828.webp" alt="ChatGPT Sites、Cloudflare、Vercelの得意分野を4つの役割で比較したイメージ" loading="eager" decoding="async">
  <figcaption>サービス名から選ぶのではなく、誰が作り、何を守り、どこで動かし、どう戻すかを先に決めます。</figcaption>
</figure>

まず、3サービスとGitHubの役割を一行で分けます。

| 役割 | 第一候補 | 何を任せるか |
|---|---|---|
| AIと相談して早く作る | ChatGPT Sites | 作成、修正、保存したバージョンの確認、公開 |
| ドメインを守り速くする | Cloudflare Pro | DNS、CDN、WAF、キャッシュ、画像最適化 |
| Cloudflare上でサイトや処理を動かす | Workers Static Assets / Workers | HTML・画像の配信、API、認証、D1・R2との接続 |
| Git中心にアプリを育てる | Vercel | Git連携のビルド、Preview、本番、Functions |
| 原本と変更履歴を残す | GitHub | コード、文章、画像、レビュー、復旧、引継ぎ |

ここで大切なのは、**Cloudflare ProとCloudflare Workersは、同じCloudflareでも別の役割**だということです。Cloudflare Proは主に「ドメインの前に立って、既存サイトを守り、速くするプラン」です。Workersは「コードや静的ファイルをCloudflare上で動かす開発基盤」です。

CloudflareでDNSだけを管理し、公開先をVercelにすることはできます。ただし、CloudflareのリバースプロキシをVercelの前段へ重ねる構成は、二重キャッシュ、遅延、Vercel側のセキュリティ判定低下につながるため、Vercel公式は推奨していません。Vercelを使う時はCloudflareのDNSレコードを「DNSのみ」にするか、両社の制約を理解したうえで設計します。

ChatGPT Sitesは、会話からサイト作成・修正・公開までの距離が短いのが強みです。現在はパブリックベータで、対象プランごとの上限があります。発行された各デプロイURLは本番URLとして扱われるため、変更は先にバージョン保存とプレビューで確認してから公開します。

Vercelは、GitHubのブランチやPull Requestと確認用URLが自然につながります。Next.jsを使う予約、会員、管理画面など、何年も改善するWebアプリで特に分かりやすい選択です。

迷ったら、次の順で決めます。

1. **告知ページを今日出したい** → ChatGPT Sitesから検討
2. **既存サイトの攻撃対策や表示速度を強めたい** → Cloudflare Proを検討
3. **静的サイトやAPIを低コストで公開したい** → Workers Static Assetsを検討
4. **GitHub中心に業務アプリを継続開発したい** → Vercelを検討
5. **予約・決済・個人情報がある** → 公開先より先に認証、DB、バックアップを設計

## Cloudflare ProとWorkers Paidは別契約。料金と役割を二層に分ける

<figure>
  <img src="/img/blog-sites-vs-vercel-section-3-assets-20260725.webp" alt="Cloudflare ProとWorkers Paidの料金、データ、運用範囲を二層に分けたイメージ" loading="lazy" decoding="async">
  <figcaption>Proはドメイン側の防御・高速化、Workers Paidはアカウント側の実行・データ機能。請求も上限も別に考えます。</figcaption>
</figure>

Cloudflareで最も誤解しやすいのがここです。

| 比較 | Cloudflare Pro | Workers Paid |
|---|---|---|
| 主な役割 | ドメインのセキュリティ、配信、高速化 | Workerコード、Pages Functions、KV、Durable Objectsなどの利用枠 |
| 課金単位 | **ドメインごと** | **アカウント単位** |
| 2026年8月時点の入口 | 年払いで月20ドル相当、月払いは25ドル | 最低月5ドル＋超過利用分 |
| 代表的な強化 | Managed WAF、20個のWAFカスタムルール、キャッシュ制御、Polish、Mirage | 動的リクエスト、CPU時間、関連する開発者向け製品の利用枠 |
| 含まれないもの | Workers Paid、D1・R2等の従量分、Argo等の追加サービス | ProのWAF・画像最適化・ドメイン別機能 |
| 無料版との関係 | FreeのDNS・CDN・DDoS対策を、事業サイト向けに強化 | Workers Freeの上限を、アカウント全体で有料枠へ拡張 |

Cloudflareのドメイン向けプランは、登録したドメイン単位で請求されます。たとえば `example.jp` と `example.com` を両方Proにすると2件分です。一方、`shop.example.jp` のようなサブドメインは、別の請求ドメインとして数えられません。

Workers Paidはそれとは**別契約**で、Cloudflare公式もFree・Pro・Businessなどのドメイン向けプランとは別だと明記しています。Proへ上げてもWorkers Paidにはならず、Workers Paidへ上げてもProのWAF機能は付きません。

たとえば3つの独立ドメインを年払いのProへ上げ、同じアカウントでWorkers Paidも使うなら、入口は月額換算でおおむね次の構造です。

- Pro：20ドル相当 × 3ドメイン ＝ 60ドル相当
- Workers Paid：アカウント全体で最低5ドル
- 合計：最低65ドル相当＋Workers、D1、R2、Argoなどの超過・追加利用分

これは「Cloudflareが高い」という話ではありません。**守るドメイン数と、動かす処理量を分けて見積もる**ための考え方です。請求書では、一つのアクセスがProゾーン、Workers、R2、Argoなど複数製品に触れ、それぞれ別の課金軸になる場合があります。

### Cloudflare Proへ上げる意味

Proが向くのは、次のようなサイトです。

- 売上や申込みにつながる公式サイトで、Freeより細かいWAF・キャッシュ制御が必要
- WordPressなどの既存サーバーを残しながら、防御と表示を強めたい
- 画像が多く、PolishやMirageによる最適化を使いたい
- 自動攻撃、認証情報の悪用、一般的なWeb攻撃への対策を強めたい
- 障害時にコミュニティだけでなく、メールの技術サポートへ問い合わせたい

Cloudflare自身はProを「事業上の最重要ではないプロ向けサイト」のプランと位置づけています。Proには稼働率SLAがなく、技術サポートはケース・メールです。サイト停止がそのまま受注停止になる、チャットサポートや稼働率SLAが必要、といった場合はBusiness以上も比較します。「Pro」という名前だけで、基幹サイトに十分だと判断しないことが大切です。

逆に、会社案内の静的ページを公開するだけなら、最初からProが必須とは限りません。Cloudflare FreeとWorkers Static Assetsでも始められます。アクセス、攻撃、更新頻度、担当者の技術力を見て上げる方が無駄がありません。

### 3つの現実的な組み合わせ

| 構成 | 向く場面 |
|---|---|
| 既存サーバー＋Cloudflare Pro | WordPressや既存Webサービスを残し、防御・キャッシュだけ強化する |
| Cloudflare Free＋Workers Free | 小規模な静的サイト、LP、試作品を低コストで始める |
| Cloudflare Pro＋Workers Paid | 重要な独自ドメインを守りつつ、API・認証・D1・R2を本格運用する |

Cloudflare Proは「ホスティング全部入り」ではなく、**既存または新規のサイトに付ける防御・配信の上位層**と理解すると、迷いが減ります。

## 2026年の新規サイトはWorkers Static Assets中心。Pagesは急いで捨てない

<figure>
  <img src="/img/blog-sites-vs-vercel-section-2-workflow-corrected-20260725.webp" alt="GitHubからCloudflare Workers Static Assetsへ、確認後に公開する流れ" loading="lazy" decoding="async">
  <figcaption>新規はWorkers Static Assetsを軸にしやすくなりました。既存Pagesは、必要が生じた時に公式手順で移します。</figcaption>
</figure>

Cloudflareには、名前が似た3つの仕組みがあります。

| 名前 | 2026年の位置づけ | 判断 |
|---|---|---|
| Workers Static Assets | 静的ファイルとWorkerコードを一つの単位で配備する現在の中心 | 新規サイトの第一候補 |
| Cloudflare Pages | Git連携で静的サイトやPages Functionsを公開する既存サービス | 動いているなら急いで移行不要 |
| Workers Sites | KVを使う旧製品 | **非推奨**。新規では使わない |

つまり、**Cloudflare Pagesが廃止されたという意味ではありません。非推奨なのは旧製品のWorkers Sitesです。** CloudflareはPagesからWorkersへの公式移行ガイドを用意していますが、既存Pagesを今すぐ止めるよう求めているわけではありません。

新規でWorkers Static Assetsを選びやすい理由は、HTML、CSS、画像などの静的ファイルと、APIや認証のWorkerコードを同じプロジェクトで扱えるからです。最初は会社案内だけで始め、後から問い合わせAPIや会員機能を足す、といった成長に対応しやすくなっています。

### 無料なのは「静的ファイルへのリクエスト」

CloudflareはStatic Assetsへのリクエストを無料・無制限と案内しています。ただし、すべての処理が無制限になるわけではありません。

| 項目 | Workers Free | Workers Paid |
|---|---|---|
| 静的ファイルへのリクエスト | 無料・無制限 | 無料・無制限 |
| Workerの動的リクエスト | 1日10万件 | リクエスト上限なし。含有枠超過は従量 |
| CPU時間 | 1リクエスト10ms | 1リクエスト最大5分 |
| Workerサイズ | 3MB | 10MB |
| 静的ファイル数／バージョン | 2万件 | 10万件 |
| 静的ファイル1件 | 最大25MiB | 最大25MiB |

静的ファイルより先に必ずWorkerを実行する設定にすると、静的ページへのアクセスもWorker側の上限・課金へ入る場合があります。「静的だから無料」とだけ覚えず、**どのURLがWorkerを通るか**を確認します。

また、リクエスト本文の上限はWorkersプランではなくドメイン向けプランにも左右され、FreeとProは100MBです。大きな動画や資料をWorker経由で受け取るより、R2へ直接アップロードする設計を検討します。

### D1とR2は便利だが、コードとは別に復旧を考える

| データ機能 | 無料枠・入口の目安 | 運用で確認すること |
|---|---|---|
| D1 | Freeは1日500万行読み取り、10万行書き込み、合計5GB。1DBは500MBまで | Paidは1DB 10GB。Time TravelはFree 7日、Paid 30日。別保管も準備 |
| R2 | Standardは月10GBまで無料。超過ストレージは1GB月0.015ドル。R2から外への通信料は無料 | 保存量だけでなくClass A・B操作も課金対象。削除・世代管理を決める |

D1のTime Travelは強力ですが、保持期間を超えた削除やアカウント事故まで救う万能バックアップではありません。重要データは定期エクスポートや別ストレージへの退避も用意します。

### Git連携とPreviewにも注意点がある

Workers BuildsはGitHubまたはGitLabと連携し、本番ブランチの更新を自動公開できます。非本番ブランチのビルドを有効にすれば、Pull Requestで確認URLも使えます。

ただし、WorkersのPreview URLは有効時に**公開URL**です。顧客名、児童・生徒の情報、福祉相談、未公開価格などを置くなら、Cloudflare Accessで保護するか、匿名のテストデータだけを使います。

費用対策では、2026年7月から対象の従量課金アカウントへ10ドルの既定予算アラートが順次設定されています。ただし予算アラートは通知だけで、利用停止や上限固定ではありません。前日分を日次処理するため遅れて届く場合があり、ProやWorkers Paidなどの定額料金も判定に含まれません。

安全な運用は次の3点です。

1. アカウント全体の予算アラートを、自分で必要額へ設定する
2. Workers、D1、R2など製品別の利用通知も設定する
3. 月1回、請求画面と実際のアクセス・保存量を担当者が確認する

## ChatGPT Sites・Cloudflare・Vercelを地域事業の現場で選ぶ

<figure>
  <img src="/img/blog-sites-vs-vercel-section-5-pilot-20260725.webp" alt="地域の講座、店舗サイト、業務アプリを小さく試して公開先を選ぶイメージ" loading="lazy" decoding="async">
  <figcaption>最善のサービスは用途で変わります。止まっても困らない小さなページで、作成・更新・復旧を一度通します。</figcaption>
</figure>

3サービスを、地域事業で本当に困る項目に絞って比べます。

| 比べること | ChatGPT Sites | Cloudflare | Vercel |
|---|---|---|---|
| いちばんの強み | AIとの対話から公開までが短い | ドメイン防御、静的配信、エッジ処理、データ機能を組み合わせられる | Git、Preview、Webアプリ運用が一続き |
| 入口の料金 | Plus、Pro、対象ワークスペース等のプラン内。ベータ上限あり | Freeあり。Proはドメインごと月20ドル相当から。Workers Paidは別に最低5ドル | Hobbyは0ドル。Proは月20ドルで20ドル分の利用クレジットを含み、超過は従量 |
| 商用利用 | 公開内容、プラン、Sites規約を確認 | Free・Paidとも用途と各製品上限を確認 | Hobbyは個人・非商用向け。事業利用はProを基本に検討 |
| 公開前確認 | バージョン保存後に確認して公開 | GitブランチのBuild、Version Preview | ブランチ・Pull RequestごとのPreview |
| GitHub | 必須ではない。別途原本として残す | GitHub/GitLab連携 | GitHub/GitLab/Bitbucket/Azure DevOps連携 |
| 独自ドメイン | 対応するアカウント・環境で接続 | DNSから配信まで一体管理しやすい | 既存ドメインを接続 |
| サーバー処理 | Sitesが対応する軽量アプリの範囲 | Workers | Functions |
| データ | Sitesが対応するD1・R2等 | D1、R2、KV、Durable Objects等 | 外部DBやMarketplace連携が中心 |
| 注意点 | パブリックベータ、プラン・地域差、対応外構成、公開責任 | 製品と課金軸が多い。Preview公開、従量課金を確認 | 商用プラン、実行量、転送量、外部DBの費用も確認 |

ChatGPT Sitesは、公開ベータの対象アカウントで使え、利用上限はアカウント全体のSitesにかかります。独自ドメインは利用可能な環境で接続できますが、ドメイン自体を取得してくれるわけではありません。Enterpriseでは開始時点で独自ドメイン非対応など、プラン差があります。

また、Sitesにフォーム、ログイン、投稿機能を作れる場合でも、公開者には内容、個人情報、権利、アクセス範囲を確認する責任があります。学校・福祉・健康相談では、まず個人を特定しない案内や集計から始め、機微情報を試作品へ入れません。カード情報は自前で保持せず、Stripeなど適切な外部決済へ渡します。

VercelはHobbyが魅力的ですが、公式は個人・非商用向けとしています。店舗、講師業、受託制作、会員サービスなど事業利用では、Proの基本料金と超過利用を見積もります。Proは支出管理やハード上限を設定できるため、初期値のままにせず事業に合う通知・停止条件を決めます。

### 現場別のおすすめ

| 誰の、どんな悩みか | 最初の選択 | 次の行動 |
|---|---|---|
| 地域団体がイベント告知を今日出したい | ChatGPT Sites | 案内ページを作り、申込は既存フォームへつなぎ、スマホ確認後に公開 |
| 店舗の既存サイトで攻撃・表示速度が心配 | Cloudflare Pro | 対応可否を確認し、DNS・WAF・キャッシュを段階的に有効化 |
| 個人事業主が会社案内やブログを軽く持ちたい | Workers Static Assets | GitHubを原本にしてFreeから公開し、必要時にProやPaidを追加 |
| 予約・会員・管理画面を継続改善したい | Vercel Pro＋外部DB | Pull Requestごとの確認、権限、DBバックアップを運用にする |
| 学校・福祉施設が内部ツールを試したい | Sitesまたは保護したPreview | 匿名データで検証し、公開範囲・保管場所・責任者を先に決める |

AI相談のサイトは、GitHubを原本にしてVercelで公開しています。Codex、Claude Code、Cursorなど複数のAI開発ツールから同じソースを扱い、Pull RequestやPreviewを通して継続改善する現在の用途に合うためです。

一方、短期の講演会ページならChatGPT Sites、静的な地域サイトならWorkers Static Assets、既存の重要ドメインの防御強化ならCloudflare Proが合理的な場合があります。大切なのは「有名だから」ではなく、**誰の時間を減らし、どの失敗から戻りたいか**で選ぶことです。

## サイト公開の極意：GitHubを原本にし、コード・データ・ドメインを分けて移す

<figure>
  <img src="/img/blog-sites-vs-vercel-section-4-domain-20260725.webp" alt="現行サイトとGitHubを残し、コード、データ、独自ドメインを段階的に切り替えるイメージ" loading="lazy" decoding="async">
  <figcaption>一度に全部を変えなければ、問題の原因が分かり、元の公開先へ戻せます。</figcaption>
</figure>

GitHubを残すのは、Vercelのためではありません。**公開先が変わっても、コードと変更履歴を持ち運べる状態にするため**です。

ただし、GitHubにコードがあってもサイト全体のバックアップにはなりません。

| 残すもの | 保存・確認先 |
|---|---|
| コード、文章、画像の原本 | GitHub＋外部にmirror cloneした復旧用コピー |
| 顧客、予約、投稿などのDB | D1、Supabase等の自動バックアップ＋定期エクスポート |
| 利用者が上げた画像・PDF | R2等のストレージ＋別保管 |
| APIキー、パスワード | GitHubへ入れず、環境変数・秘密情報管理 |
| DNS、メール設定 | A、AAAA、CNAME、MX、SPF、DKIM、DMARCを一覧化 |
| 課金と運用 | 契約プラン、予算通知、責任者、解約条件を記録 |

GitHub公式は、履歴を含む復旧用コピーに `git clone --mirror` を案内しています。GitHubそのものと同じアカウントだけに置かず、定期的に外部ストレージへ保管します。LFS、Issues、設定、Secrets、DBは別対象なので、何が戻るかを一度試します。

### 安全な移行の10手順

1. **現状を6層に分ける**
   画面、API・Cron、DB、ファイル、環境変数、DNS・メールを書き出します。

2. **GitHubの本番コミットを決める**
   「今の本番がどのコミットか」を記録し、戻す基準にします。

3. **DBとストレージを先にバックアップする**
   ダウンロードしただけで安心せず、別環境で読めるか確かめます。

4. **止まっても困らない1ページを選ぶ**
   講座案内、会社紹介、よくある質問など、決済や個人情報がないページから始めます。

5. **仮URLでPCとスマホを確認する**
   文字、画像、リンク、フォーム、404、横はみ出し、表示速度、コンソールエラーを見ます。

6. **Previewの公開範囲を確認する**
   URLを知れば見える状態なのか、ログインが必要なのかを別ブラウザで試します。

7. **更新とロールバックを実演する**
   1か所直して再公開し、直前の版へ戻すところまで担当者が行います。

8. **独自ドメインはWebの向き先だけ変える**
   ドメイン会社の移管は後回しにし、必要なA・AAAA・CNAMEだけ切り替えます。MX、SPF、DKIM、DMARCを不用意に消しません。

9. **現行サービスを数週間残す**
   新環境のアクセス、フォーム、メール、請求を確認してから、旧環境の縮小・解約を決めます。

10. **運用メモを1ページにまとめる**
    公開方法、復旧方法、月額、予算通知、担当者、公式URL、次の確認日をREADMEへ残します。

公開の極意を5つに縮めると、次の通りです。

1. **原本は一つ**：GitHubの本番ブランチを基準にする
2. **本番の前に確認**：保存版やPreviewを第三者の画面で見る
3. **一度に一層だけ変える**：コード、DB、DNSを同日移行しない
4. **移す前に戻し方を試す**：ロールバックできない移行は始めない
5. **料金にも責任者を置く**：通知は停止装置ではないと理解する

### よくある質問

**Q. Cloudflare Proはホスティングですか？**

Cloudflare Proは主に、ドメインの前段でDNS、CDN、WAF、キャッシュ、画像最適化を強化するプランです。元のサイトは別サーバーでもWorkersでも構いません。サイトをCloudflare上で動かす部分はWorkers Static AssetsやWorkersが担当します。

**Q. Workersを使うにはCloudflare Proが必要ですか？**

必要ありません。Freeのドメイン向けプランとWorkers Freeから始められます。重要ドメインの防御を強めるならPro、動的処理の上限を広げるならWorkers Paidを、それぞれ必要に応じて追加します。

**Q. Cloudflare Pagesは廃止ですか？**

いいえ。既存Pagesは利用でき、公式の移行ガイドもあります。新規はWorkers Static Assetsを第一候補にしやすい状況ですが、非推奨なのはPagesではなく旧製品のWorkers Sitesです。

**Q. ChatGPT Sitesを使うならGitHubは不要ですか？**

小さな試作品ならGitHubなしでも始められます。複数のAI開発ツールで直す、担当者へ渡す、公開先を変える、詳細な履歴から戻すなら、GitHubへ原本を残します。

**Q. CloudflareとVercelは、どちらが速いですか？**

静的ページだけなら、どちらも十分速くできます。画像、キャッシュ、利用地域、API、DBの場所で結果が変わるため、同じページを同じ条件で測らずに断定しません。運用の分かりやすさと復旧も含めて選びます。

**Q. 結局、迷ったらどれを選びますか？**

告知や試作品はChatGPT Sites、既存ドメインの防御強化はCloudflare Pro、Cloudflareで新規公開する静的サイト・APIはWorkers Static Assets、Git中心の継続的なWebアプリはVercelを起点にします。どの場合もGitHubを原本にし、重要データのバックアップを別に持ちます。

<div class="publishing-cta">
  <strong>公開先で迷ったら、「どの会社がよいか」より先に、作る・守る・動かす・戻すを分けます。</strong>
  <p>AI相談では、現在のサイト、GitHub、Cloudflareのプラン、Vercel、DB、独自ドメインを確認し、残すものと小さく試すものを一緒に整理します。</p>
  <p><a href="/#contact">AI相談へ相談する</a> ・ <a href="/blog/2026-07-22-ai-site-publishing-stages.html">公開の3段階を先に読む</a></p>
</div>

### 参考にした公式情報

- [OpenAI：ChatGPT Sitesの作成・管理・公開](https://help.openai.com/en/articles/20001339-creating-and-managing-chatgpt-sites)
- [OpenAI：ChatGPT Sites公開者の責任](https://help.openai.com/en/articles/20001337-understanding-responsibilities-for-your-chatgpt-sites)
- [Cloudflare：Proプランの機能](https://www.cloudflare.com/plans/pro/)
- [Cloudflare：Free・Pro・Businessの料金と機能](https://www.cloudflare.com/plans/)
- [Cloudflare：プラン別のサポート方法](https://developers.cloudflare.com/support/contacting-cloudflare-support/)
- [Cloudflare：ドメイン単位の請求方針](https://developers.cloudflare.com/billing/understand/billing-policy/)
- [Cloudflare：1リクエストで複数製品の料金が発生する仕組み](https://developers.cloudflare.com/billing/understand/how-charges-accrue/)
- [Cloudflare：Workersの料金](https://developers.cloudflare.com/workers/platform/pricing/)
- [Cloudflare：Workersの上限](https://developers.cloudflare.com/workers/platform/limits/)
- [Cloudflare：Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [Cloudflare：PagesからWorkersへの移行](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)
- [Cloudflare：D1の料金と上限](https://developers.cloudflare.com/d1/platform/pricing/)
- [Cloudflare：D1のデータベース上限](https://developers.cloudflare.com/d1/platform/limits/)
- [Cloudflare：R2の料金](https://developers.cloudflare.com/r2/pricing/)
- [Cloudflare：予算アラート](https://developers.cloudflare.com/billing/manage/budget-alerts/)
- [Vercel：Gitリポジトリからのデプロイ](https://vercel.com/docs/git)
- [Vercel：料金プラン](https://vercel.com/pricing)
- [Vercel：Cloudflare等の外部プロキシを前段に置く注意](https://vercel.com/kb/guide/cloudflare-with-vercel)
- [GitHub：リポジトリのバックアップ](https://docs.github.com/en/repositories/archiving-a-github-repository/backing-up-a-repository)

<p class="publishing-note">※機能、上限、料金は2026年8月28日時点の公式情報を確認しています。料金は米ドル表記で、税・為替・地域差・追加サービスは別です。実際の契約・移行前に、利用中アカウントの最新条件を再確認してください。</p>

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
