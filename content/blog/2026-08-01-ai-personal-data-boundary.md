---
title: "「個人情報はAIに一切入力禁止」は正しい？ ChatGPT・Copilot・Codexを止めずに守る7つの境界線"
date: 2026-08-01
authorship_note: "この記事は、運営者が独自に考え、思考したものを、AIを使って読みやすくしました。"
role: ブログ / AI活用・情報セキュリティ
gen_by: 由井辰美 / AI相談
summary: 個人情報をAIへ入れた瞬間に一般公開や情報漏えいになるわけではありません。一方で、顧客DB、認証情報、本番環境をAIへ無条件に渡してよいわけでもありません。ChatGPT、Copilot、Codexを製品名で判断せず、データ、契約、保存、接続、権限の境界で安全に使い分ける方法を解説します。
image: /img/blog-ai-data-boundary-hero-20260801.webp
image_alt: 過剰な全面禁止と管理されたAI活用の間で、データの流れと権限を確認する職員
video: /video/blog-ai-data-boundary-20260802.mp4
video_poster: /img/blog-ai-data-boundary-video-cover-20260802.png
video_orientation: portrait
video_fullscreen_on_play: mobile
video_label: 個人情報をAIへ入力するときの7つの境界線を15秒で紹介する動画
video_caption: 15秒で要点を確認できます。個人情報は一律禁止ではなく、データ・契約・保存・接続・権限の境界で判断します（音声なし）。
audience: 生成AIの社内ルールを作る経営者・管理職、地域事業者、学校・福祉施設、大学生、個人事業主
duration: 12分
goal: AIへの入力を一律に怖がるのではなく、本当に止めるべきデータと権限を見分け、現場で使える1枚の利用ルールを作れるようになる
---

<style>
.ai-data-guide{--ad-blue:#285f78;--ad-navy:#173042;--ad-teal:#1e8c83;--ad-orange:#e4834a;--ad-red:#c84b4b;--ad-ink:#17232c;--ad-soft:#53646e;--ad-line:#d8e3e7;color:var(--ad-ink)}
.ai-data-guide *{box-sizing:border-box}
.ai-data-guide p,.ai-data-guide li{line-height:1.9}
.ai-data-guide h2{margin-top:3rem;line-height:1.45}
.ai-data-guide h3{margin-top:2.1rem}
.ai-data-guide .guide-figure{width:min(100%,1100px);margin:1rem auto 2rem}
.ai-data-guide .guide-figure img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border:1px solid var(--ad-line);border-radius:18px;background:#f4f8f9;box-shadow:0 14px 36px rgba(23,48,66,.12)}
.ai-data-guide .guide-figure figcaption{margin:.7rem auto 0;color:var(--ad-soft);font-size:.9rem;line-height:1.65;text-align:center}
.ai-data-guide .guide-hero{margin-top:0}
.ai-data-guide .story{margin:1.3rem 0 1.8rem;padding:1.2rem 1.35rem;border-left:6px solid var(--ad-orange);border-radius:12px;background:#fff8ef}
.ai-data-guide .answer{margin:1.4rem 0 2rem;padding:1.25rem 1.4rem;border-radius:15px;background:#eaf6f5}
.ai-data-guide .answer strong{display:block;margin-bottom:.45rem;color:var(--ad-navy);font-size:1.18rem}
.ai-data-guide .quick-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem;margin:1.4rem 0 2rem}
.ai-data-guide .quick-card{padding:1rem 1.1rem;border:1px solid var(--ad-line);border-radius:14px;background:#fff}
.ai-data-guide .quick-card b{display:block;margin-bottom:.35rem;color:var(--ad-blue)}
.ai-data-guide .quick-card.is-stop{border-top:5px solid var(--ad-red)}
.ai-data-guide .quick-card.is-go{border-top:5px solid var(--ad-teal)}
.ai-data-guide .simple-table{display:block;width:100%;margin:1.2rem 0 2rem;overflow-x:auto;-webkit-overflow-scrolling:touch}
.ai-data-guide table{min-width:740px}
.ai-data-guide th{white-space:nowrap}
.ai-data-guide .boundary-list{counter-reset:boundary;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.8rem;padding:0;list-style:none}
.ai-data-guide .boundary-list li{position:relative;padding:1rem 1rem 1rem 3.1rem;border:1px solid var(--ad-line);border-radius:13px;background:#fff}
.ai-data-guide .boundary-list li:before{counter-increment:boundary;content:counter(boundary);position:absolute;left:1rem;top:1rem;width:1.55rem;height:1.55rem;border-radius:50%;background:var(--ad-blue);color:#fff;font-weight:800;line-height:1.55rem;text-align:center}
.ai-data-guide .levels{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.7rem;margin:1.3rem 0 2rem}
.ai-data-guide .level{padding:1rem;border-radius:14px;color:#17232c}
.ai-data-guide .level b{display:block;margin-bottom:.4rem;font-size:1.08rem}
.ai-data-guide .green{background:#e5f6ec;border:1px solid #9bd4ae}.ai-data-guide .yellow{background:#fff7cf;border:1px solid #e7ce6c}.ai-data-guide .orange{background:#fff0e3;border:1px solid #e7ad79}.ai-data-guide .red{background:#fdeaea;border:1px solid #df9b9b}
.ai-data-guide .checklist{margin:1.3rem 0 2rem;padding:1.2rem 1.35rem;border-radius:15px;background:#f0f5f7}
.ai-data-guide .checklist li{margin:.35rem 0}
.ai-data-guide .warning{margin:1.3rem 0 1.8rem;padding:1.15rem 1.3rem;border:1px solid #ecc7c7;border-radius:14px;background:#fff4f4}
.ai-data-guide .cta{margin:2.5rem 0 1rem;padding:1.4rem;border-radius:16px;background:var(--ad-navy);color:#fff}
.ai-data-guide .cta p{color:#e6f0f4}.ai-data-guide .cta a{display:inline-block;margin-top:.35rem;padding:.75rem 1rem;border-radius:999px;background:#fff;color:var(--ad-navy);font-weight:800;text-decoration:none}
.ai-data-guide .note{color:var(--ad-soft);font-size:.9rem}
@media(max-width:800px){.ai-data-guide .levels{grid-template-columns:repeat(2,minmax(0,1fr))}.ai-data-guide .boundary-list{grid-template-columns:1fr}.ai-data-guide .guide-figure img{border-radius:12px}}
@media(max-width:540px){.ai-data-guide .quick-grid,.ai-data-guide .levels{grid-template-columns:1fr}.ai-data-guide .story,.ai-data-guide .answer,.ai-data-guide .checklist,.ai-data-guide .warning,.ai-data-guide .cta{padding:1rem}}
</style>

<div class="ai-data-guide" markdown="1">

<figure class="guide-figure guide-hero">
  <img src="/img/blog-ai-data-boundary-hero-20260801.webp" alt="過剰な全面禁止と管理されたAI活用の間で、データの流れと権限を確認する職員" loading="eager" decoding="async">
  <figcaption>安全は「AIだから禁止」「有名製品だから安全」では決まりません。データの種類、契約、保存、接続先、権限を一つずつ確認することで決まります。</figcaption>
</figure>

「お客様の名前が一文字でも入っていたら、AIは一切禁止です。ただし、Windowsに最初から入っているCopilotなら使って構いません」

ある地域企業の会議で、こんなルールが決まったとします。問い合わせ50件の傾向をまとめたい若手職員は、氏名を消して会社契約のAIへ渡すことも止められ、数時間かけて手作業を選びました。別の職員は締切に間に合わず、管理されていない個人アカウントを自宅で使いました。

その一方で、開発担当者は「会社公認のAIだから大丈夫」と、本番データベースの接続情報と書き込み権限をAIエージェントへ渡していました。

<div class="story">
※これは特定企業の実話ではなく、複数の相談で起こり得る問題を組み合わせた架空の場面です。大事なのは、氏名を除いた問い合わせ要約と、本番DBを自由に操作できるエージェントを、同じ「AI利用」として扱っている点です。
</div>

この記事の結論は、**個人情報をAIへ入力しただけで、直ちにインターネットへ一般公開されたり、必ず「情報漏えい」になったりするわけではない**、です。しかし、だから何を入れてもよい、という意味でもありません。入力は外部サービスへの送信になり得ます。利用目的、契約、学習利用、保存、接続先、操作権限によっては、法令・契約・社内規程違反や実際の漏えいにつながります。

<div class="answer">
<strong>本当に必要なのは、全面禁止ではなく「境界線」です。</strong>
AIの製品名ではなく、①何を、②どの契約の環境へ、③何の目的で、④どれだけ保存し、⑤どこへ接続し、⑥何を実行できる状態で渡すのかを確認します。
</div>

<div class="quick-grid">
  <div class="quick-card is-stop"><b>誤解1</b>AIへ入力した瞬間、世界中に公開される。</div>
  <div class="quick-card is-go"><b>実際</b>通常は一般公開ではない。ただし外部送信、保存、事業者側の利用は評価が必要。</div>
  <div class="quick-card is-stop"><b>誤解2</b>学習に使われなければ、保存も人の閲覧も一切ない。</div>
  <div class="quick-card is-go"><b>実際</b>学習、サービス保持、不正利用監視、監査ログは別々の条件。</div>
  <div class="quick-card is-stop"><b>誤解3</b>WindowsのCopilotなら無条件で会社利用に安全。</div>
  <div class="quick-card is-go"><b>実際</b>個人向けか、Entra IDで保護された会社向け環境かで条件が違う。</div>
  <div class="quick-card is-stop"><b>誤解4</b>AIが作ったコードで顧客情報をDB保存すると、必ずAI会社へ漏れる。</div>
  <div class="quick-card is-go"><b>実際</b>生成時と実行時は別。実行時の送信先、ログ、権限、脆弱性を調べる。</div>
</div>

## 「個人情報はAIに一切入力禁止」には正しい部分と過剰な部分がある

<figure class="guide-figure">
  <img src="/img/blog-ai-data-boundary-rule-20260801.webp" alt="全面禁止で止まる経路と、確認・承認を通して安全にAIを使う経路の比較" loading="lazy" decoding="async">
  <figcaption>守るべき対象を決めずに全員を止めると、危険な利用と有用な利用の違いが見えなくなります。</figcaption>
</figure>

一律禁止には、正しい出発点があります。無料の個人アカウントへ顧客名簿を貼り付けたり、認証情報をチャットへ書いたりしてよいはずがありません。医療・福祉・教育相談の記録、マイナンバー、決済情報、大量の顧客DB、未公開の契約や技術情報は、失敗したときの影響が大きいデータです。利用サービスと管理方法が決まっていない段階で止めるのは妥当です。

問題は、**「個人情報」という一語で、危険度の違う行為を全部同じにすること**です。

- 公開済みのイベント案内を読みやすくする
- 氏名と連絡先を除いた20件の問い合わせから傾向を出す
- 会社契約の環境で、権限を限定して社内文書を検索する
- 無料の個人アカウントへ顧客名簿を丸ごと貼る
- AIエージェントへ本番DBの管理者権限を渡す

これらは同じ「AIへの入力」ではありません。全て禁止にすると、最初の三つまで失います。一方で「会社公認のAIなら全部よい」とすると、最後の二つを見逃します。

日本の個人情報保護委員会も、生成AIへの個人データ入力を一律に「即漏えい」とは説明していません。事業者が本人同意なく個人データを入力する場合、提供者がそのデータを機械学習に利用しないことなどを十分確認するよう注意を促しています。つまり問われるのは、**利用目的と提供先での取扱い**です。[個人情報保護委員会の注意喚起](https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/)を、単なる「AI禁止のお知らせ」と読むのは正確ではありません。

また、禁止だけで業務上の必要が消えるわけではありません。2024年のMicrosoftの世界調査では、職場でAIを使う人の78%が自分で用意したAIツールを持ち込んでいると回答しました。2026年のGartner Japanも、単純な禁止・遮断より、利用の可視化、評価、承認、統制を勧めています。これらはベンダー調査であり、全面禁止が必ず事故を増やすという因果関係の証明ではありません。ただ、**見えない利用を管理するには「禁止」の一語では足りない**ことを示しています。[Microsoft Work Trend Index](https://www.microsoft.com/en-us/worklab/work-trend-index/ai-at-work-is-here-now-comes-the-hard-part)、[Gartner Japan](https://www.gartner.co.jp/ja/newsroom/press-releases/pr-20260618-aibs-shadow-ai)

## AIへの入力は直ちに一般公開や漏えいではなく、送信先と利用条件で評価が変わる

<figure class="guide-figure">
  <img src="/img/blog-ai-data-boundary-flow-20260801.webp" alt="データがAIへ届くまでに七つの確認ゲートを通る流れ" loading="lazy" decoding="async">
  <figcaption>「入力したか」だけでなく、送信の前後にある7つの境界を見ると判断が具体的になります。</figcaption>
</figure>

まず、似ている言葉を分けます。

- **一般公開**: 不特定多数が見られる状態にすること
- **外部送信**: 組織の端末や管理領域から外の事業者へデータを送ること
- **第三者提供・委託**: 個人情報保護法上の要件に沿って個別に判断する概念
- **漏えい等**: 本来アクセスできない相手に個人データが渡る、失われる、壊されるなどの事象

クラウドAIへの入力は通常、一般公開ボタンを押すことではありません。しかし外部送信になり得ます。契約や目的によっては、第三者提供か委託か、外国での取扱いはどうかという確認も必要です。そして設定ミス、誤共有、攻撃、障害があれば実際の漏えいへ進む可能性があります。

安全性は、次の7つの境界で見ます。

<ol class="boundary-list">
  <li><strong>目的と権限</strong><br>本人への説明や社内の利用目的の範囲か。入力する担当者に権限があるか。</li>
  <li><strong>データの質と量</strong><br>氏名だけか、病歴・相談内容・決済情報か。1件か、全顧客か。特定できない形に減らせるか。</li>
  <li><strong>アカウントと契約</strong><br>個人向け無料版か、会社が審査・契約・管理する環境か。委託条件やデータ処理契約はあるか。</li>
  <li><strong>学習と再利用</strong><br>入力がモデル訓練やサービス改善に使われるか。既定値とオプトアウトは何か。</li>
  <li><strong>保存と人のアクセス</strong><br>履歴、監視ログ、監査ログ、削除までの期間はどうか。管理者や委託先がアクセスし得るか。</li>
  <li><strong>接続先</strong><br>検索、プラグイン、MCP、クラウドストレージなど、別事業者へデータが渡る機能を使うか。</li>
  <li><strong>実行できる操作</strong><br>回答するだけか。メール送信、ファイル公開、DB更新、削除まで自動実行できるか。</li>
</ol>

たとえばOpenAIは、ChatGPT Business、Enterprise、Edu、APIの業務データを既定でモデル訓練に使わないと説明しています。しかし、これは「何も保存されない」「接続した外部サービスも同じ条件」「誤設定が起きない」という意味ではありません。APIには通常、不正利用監視のためのログ保持があり、適格な利用者向けにZero Data Retention等の別条件があります。コネクター先には、そのサービス独自の保持・権限・監査があります。[OpenAIの企業向けプライバシー説明](https://learn.chatgpt.com/docs/enterprise/work-admin-faq#how-does-chatgpt-work-support-enterprise-privacy-and-data-commitments)、[OpenAI APIのデータ管理](https://developers.openai.com/api/docs/guides/your-data)、[アプリとコネクターのデータフロー](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors#understand-data-flow-and-security)

Microsoftも同じです。WindowsのCopilotアプリには個人向け利用があります。一方、組織のEntra IDで利用するMicrosoft 365 Copilot Chatには、企業向けデータ保護があります。後者は基盤モデルの訓練にプロンプトや回答を使わない一方、監査やeDiscoveryのために記録が保持される場合があります。さらにSharePointやOneDriveの既存権限を尊重するため、もともとの過剰共有はAIにも見える範囲を広げます。**「Windowsに入っているから安全」ではなく、サインイン中のアカウント、契約、管理設定、既存権限を見る**のが正解です。[WindowsでのCopilot管理](https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot)、[Microsoft 365 Copilotのプライバシー](https://learn.microsoft.com/en-ca/copilot/privacy-and-protections)、[Microsoft 365 Copilotのセキュリティ](https://learn.microsoft.com/en-us/microsoft-365/copilot/security-microsoft-365-copilot)

なお、一般公開でなくても事故は起こります。OpenAIは2023年、障害により一部ユーザーのチャットタイトルなどが別ユーザーに表示された事例を公表しています。サービス提供者の対策は重要ですが、ゼロリスクではありません。入力を最小化する理由はここにもあります。[OpenAIの障害報告](https://openai.com/index/march-20-chatgpt-outage/)

## コード生成・自社DB保存・本番DB接続・顧客DB送信は別のリスクである

<figure class="guide-figure">
  <img src="/img/blog-ai-data-boundary-database-20260801.webp" alt="コード生成、自社DB保存、機密リポジトリ送信、本番DB接続の四つの経路" loading="lazy" decoding="async">
  <figcaption>コードを作る場面と、完成したシステムが動く場面を分けると、AI固有のリスクと通常のシステムリスクを整理できます。</figcaption>
</figure>

ここは、AIチャット以上に誤解されやすい部分です。

**AIにコードを書かせたこと**と、**完成したプログラムが顧客情報を処理すること**は別です。AIがダミーデータを使って予約システムのコードを書き、そのシステムが実行時に会社の承認済みDBへ顧客情報を保存するだけなら、顧客情報が自動的にAI提供者へ送られるわけではありません。問題は、生成コードに脆弱性がないか、不要なログを残していないか、外部APIや解析サービスへ送信していないか、DBのアクセス制御が正しいかです。これはAI固有の問題というより、通常のシステム開発でも必要な確認です。

一方、Codexのようなエージェントへ本番DBの接続情報を渡し、ネットワーク接続と読書き・削除権限まで与えると、危険度は急に上がります。誤った指示、悪意あるWebページやREADMEに仕込まれたプロンプトインジェクション、生成したコマンドの誤りによって、データの持ち出し・変更・削除が起こり得るからです。

<div class="simple-table" markdown="1">

| 場面 | AI提供者が実データを見るか | 主な危険 | 基本判断 |
|---|---|---|---|
| スキーマとダミーデータだけでコード生成 | 原則見ない。送ったスキーマ自体は見る | 機密構造の露出、脆弱な生成コード | **低〜中**。機密名を減らし、レビューとテスト |
| AI生成アプリが実行時に自社の承認済みDBへ保存 | AI機能へ別送信しない限り見ない | 認証不備、SQL注入、ログ、バックアップ、外部解析 | **通常のシステムリスク**。設計・実装・運用を監査 |
| `.env`、顧客ログ、DBダンプを含むリポジトリをクラウドAIへ送信 | 見る可能性が高い | 秘密鍵・個人データの外部送信、保持 | **高**。送らない。秘密を除去し鍵を失効・再発行 |
| AIエージェントが本番DBを直接読書き | 処理経路と設定次第 | 過剰取得、誤更新、削除、持ち出し | **高〜重大**。原則分離、読取専用、行・列制限、人の承認 |
| 顧客DB全体を外部AI APIへ送って分類 | 明確に見る | 大量外部送信、契約・目的・保持・国外処理 | **重大**。専用設計、法務・セキュリティ審査、最小化 |

</div>

OWASPは、AIエージェントの「過剰な代理権限」を主要リスクとして挙げ、必要な機能・権限・自律性を最小化し、影響の大きい操作は人が承認するよう勧めています。英国NCSCの安全なAI開発指針も、外部API、機密データ、最小権限、プロンプトインジェクションを設計段階から扱うよう求めています。[OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)、[NCSC Secure design](https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development/guidelines/secure-design)

Codexなどでは、作業フォルダだけ書き込み可、ネットワークは既定で遮断、範囲外操作は承認を求める、といったサンドボックスが防波堤になります。ただし、利用形態や設定で条件は変わります。**「ローカルで動かしたから安全」でも「クラウドだから危険」でもなく、モデルへ渡る文脈、ファイル範囲、ネットワーク、秘密情報、実行権限を確認**してください。

過去にはSamsungの従業員が機密ソースコード等をChatGPTへ入力したと報じられました。これは「別ユーザーがそのコードを検索できた」と確認された事件ではなく、許可されていない外部サービスへ機密を送ったこと自体が問題になった事例です。ここでも、一般公開と無断外部送信を混同しないことが重要です。[Bloomberg Lawの報道](https://news.bloomberglaw.com/tech-and-telecom-law/samsung-bans-staffs-ai-use-after-spotting-chatgpt-data-leak-2)

## 企業は全面禁止ではなく、データ分類と利用条件でAI活用を管理できる

<figure class="guide-figure">
  <img src="/img/blog-ai-data-boundary-controls-20260801.webp" alt="地域企業、学校、福祉施設の職員が資料を四色に分類する様子" loading="lazy" decoding="async">
  <figcaption>現場で続くルールは、法律用語の長文より「この色なら、どこまでできるか」を一目で判断できます。</figcaption>
</figure>

100ページの規程を最初に作る必要はありません。まずは次の4色をA4一枚にしてください。

<div class="levels">
  <div class="level green"><b>緑：公開情報</b>公開済みWeb、チラシ、商品説明。承認済みAIで利用可。著作権と正確性は確認。</div>
  <div class="level yellow"><b>黄：社内・非識別情報</b>社内手順、氏名等を除いた問い合わせ。必要最小限にし、会社契約の環境だけで利用。</div>
  <div class="level orange"><b>橙：顧客・機密</b>氏名、連絡先、契約、未公開情報。目的、契約、学習、保持、管理者、接続先を確認し、承認制。</div>
  <div class="level red"><b>赤：制限情報</b>医療福祉、マイナンバー、認証情報、秘密鍵、全顧客DB。一般チャット禁止。専用設計と法務・安全審査。</div>
</div>

「匿名化すれば大丈夫」と安易に考えるのも危険です。氏名を消しても、勤務先、希少な病気、日時、自由記述を組み合わせれば本人を推測できることがあります。仮名加工情報と匿名加工情報は法律上も同じではありません。まず、AIが答えるために不要な列・行・文章を削る**データ最小化**を行い、それでも必要な場合だけ承認済み環境を使います。[個人情報保護委員会のFAQ](https://www.ppc.go.jp/all_faq_index/faq1-q14-1/)

### 入力前90秒チェック

<div class="checklist" markdown="1">

1. これは公開・社内・顧客機密・制限情報のどれか
2. 氏名、連絡先、自由記述、不要な行や列を消せないか
3. 個人アカウントではなく、会社が承認・管理するアカウントか
4. 学習利用、保存期間、削除、管理者アクセスを確認したか
5. 検索、プラグイン、MCP、ストレージなど別の接続先はないか
6. AIは回答だけか、メール送信・公開・DB更新・削除までできるか
7. 失敗時に「誰が、何を、どこへ送ったか」を追えるか

</div>

### 会社が最初に整える6項目

1. **承認済みアカウント一覧**：製品名だけでなく、プラン、組織ID、管理者を記載
2. **四色データ分類**：具体例を自社業務の言葉で書く
3. **最小権限**：本番DB、メール、共有フォルダは読取専用から開始
4. **人の承認**：公開、送信、更新、削除、支払いは自動確定させない
5. **ログと削除**：誰が何を使ったか確認でき、不要データを消せる状態にする
6. **相談・事故窓口**：隠さず早く報告できる一つの連絡先を決める

<div class="warning">
<strong>もし誤って入力したら</strong><br>
まず利用を止め、サービス名、アカウント、日時、入力データ、共有先、履歴・保持設定を記録します。共有リンクやトークンを無効化し、社内のセキュリティ・法務・個人情報保護担当と提供者へ連絡します。証拠となる履歴を慌てて消す前に、調査に必要な記録を保全してください。個人情報保護委員会への報告・本人通知は、要配慮情報、財産被害、不正目的、件数などの法定類型を含め個別に判断します。「AIへ誤入力した全件が自動的に報告対象」とも、「学習オフだから何もしなくてよい」とも決めつけないでください。[漏えい等報告の案内](https://www.ppc.go.jp/news/kaiseihou_feature/roueitouhoukoku_gimuka/)
</div>

セキュリティは、仕事を止めるための壁ではありません。守るべきものを見分け、安心して前へ進むためのガードレールです。

「個人情報があるからAI禁止」から、**「このデータを、この契約と権限なら、ここまで使える」**へ。地域企業、学校、福祉施設のように人手と時間が限られる現場ほど、この切り替えでAIの価値と安全を両立できます。

### よくある質問

**Q. 顧客の名前を1件入力しただけで、違法ですか？**

入力だけで一律に違法とは決まりません。利用目的、本人同意の要否、委託・第三者提供の関係、提供者側の利用、契約、外国での取扱いなどで判断します。社内規程や顧客との契約違反になる場合もあります。迷う場合は入力せず、個人情報保護担当や専門家へ確認してください。

**Q. ChatGPTの「学習に使わない」を選べば顧客情報を入れてよいですか？**

それだけでは足りません。学習利用と保存、監視ログ、共有、コネクター、会社の承認は別です。まずデータを減らし、会社が契約・管理する環境を使います。

**Q. Microsoft 365 Copilotなら顧客情報を扱えますか？**

組織アカウントと企業向け保護は重要な条件ですが、何でも無条件に扱えるわけではありません。既存のSharePoint権限、保持、DLP、監査、接続機能、社内の利用目的を確認します。

**Q. 顧客DBをAI分析したい場合は全面的に諦めるべきですか？**

いいえ。まず集計・匿名化・仮名化・列削除で目的を達成できるか試します。実データが必要なら、専用API、保持制御、アクセス制御、処理契約、閉じたネットワークなどを設計し、法務・セキュリティ審査を通します。一般チャットへDB全体を貼る方法は選びません。

<div class="cta">
<strong>AI相談では、現場の業務を見ながら「使えるAIルール」をA4一枚に整理します。</strong>
<p>地域事業者、学校、福祉施設、個人事業主向けに、禁止事項だけでなく、問い合わせ要約、資料作成、コーディングなどをどの条件なら進められるかを一緒に決めます。</p>
<a href="/#contact">AI活用と情報管理を相談する</a>
</div>

### 参考にした主な資料

- [個人情報保護委員会: 生成AIサービスの利用に関する注意喚起等](https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/)
- [経済産業省: AI事業者ガイドライン第1.2版](https://www.meti.go.jp/shingikai/mono_info_service/ai_shakai_jisso/20260331_report.html)
- [OpenAI: Enterprise privacy and data commitments](https://learn.chatgpt.com/docs/enterprise/work-admin-faq#how-does-chatgpt-work-support-enterprise-privacy-and-data-commitments)
- [OpenAI API: Your data](https://developers.openai.com/api/docs/guides/your-data)
- [Microsoft: Privacy and protections in Microsoft 365 Copilot](https://learn.microsoft.com/en-ca/copilot/privacy-and-protections)
- [Microsoft: Data, Privacy, and Security for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/security-microsoft-365-copilot)
- [OWASP: Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [NCSC: Guidelines for secure AI system development](https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development/introduction)
- [NIST: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

<p class="note">この記事は2026年8月1日時点の公開情報を基にした一般的な解説で、個別案件の法的助言ではありません。法令上の用語と日常語は範囲が異なります。製品仕様、保持期間、管理機能、法令・ガイドラインは変わるため、導入時点の契約と公式文書を確認してください。</p>

</div>
