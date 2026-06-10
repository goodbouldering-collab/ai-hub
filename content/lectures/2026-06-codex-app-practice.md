---
title: "Codex実践 スライド+動画  構築と応用"
date: 2026-06-10
role: 講習資料 / Codex実践
gen_by: Codex
summary: Codexアプリを実務で使うための応用編。プロジェクトとフォルダ管理、Local/Worktree/Cloud、skills、plugins、MCP、hooks、rules、automations、設定、隠れ機能、公式アップデート確認先までを実例中心に整理。
---

<style>
.codex-onboard{--ink:var(--text,#0f172a);--soft:var(--text-soft,#334155);--mut:var(--muted,#64748b);--line:var(--line,#e2e8f0);--pri:var(--primary,#2563eb);--bg:#fff;--wash:#f8fafc;--teal:#0f8b8d;--coral:#e85d5a;--green:#2f9d58;--amber:#f2b705;color:var(--ink);}
.codex-onboard *{box-sizing:border-box;}
.codex-hero{margin:4px 0 26px;padding:28px;border:1px solid var(--line);border-radius:10px;background:linear-gradient(135deg,#eef6ff 0%,#fff 48%,#effcf6 100%);box-shadow:0 18px 50px rgba(15,23,42,.08);}
.codex-hero h2{margin:0 0 10px;font-size:clamp(30px,4.4vw,52px);line-height:1.15;letter-spacing:0;color:var(--ink);}
.codex-hero p{margin:0;font-size:17px;line-height:1.85;color:var(--soft);}
.codex-source{font-size:13px;line-height:1.8;color:var(--mut);margin:10px 0 22px;}
.codex-source a{font-weight:700;}
.codex-video{margin:8px 0 18px;background:#111827;border-radius:8px;padding:10px;box-shadow:0 18px 50px rgba(15,23,42,.18);}
.codex-video video{display:block;width:100%;border-radius:6px;background:#000;}
.codex-video-script{margin:8px 0 28px;background:#111827;border-radius:8px;padding:20px 22px;box-shadow:0 18px 50px rgba(15,23,42,.18);color:#e5e7eb;}
.codex-video-script h3{margin:0 0 12px;color:#fff;font-size:22px;}
.codex-video-script p,.codex-video-script li{color:#e5e7eb;line-height:1.75;font-size:14px;}
.codex-video-script ol{margin:10px 0 0;padding-left:1.25em;}
.codex-note{border:1px solid var(--line);border-left:5px solid var(--pri);background:var(--wash);border-radius:8px;padding:16px 18px;margin:16px 0 26px;font-size:15px;line-height:1.85;color:var(--soft);}
.codex-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0 28px;}
.codex-grid.two{grid-template-columns:repeat(2,1fr);}
.codex-grid.four{grid-template-columns:repeat(4,1fr);}
.codex-card{background:var(--bg);border:1px solid var(--line);border-top:5px solid var(--accent,var(--pri));border-radius:8px;padding:18px;box-shadow:0 8px 26px rgba(15,23,42,.05);}
.codex-card h3,.codex-card h4{margin:0 0 8px;font-size:20px;line-height:1.35;color:var(--ink);}
.codex-card p,.codex-card li{font-size:14px;line-height:1.8;color:var(--soft);}
.codex-card ul{margin:8px 0 0;padding-left:1.2em;}
.codex-label{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:800;letter-spacing:.06em;color:#fff;background:var(--accent,var(--pri));border-radius:999px;padding:3px 10px;margin-bottom:10px;}
.codex-flow{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:18px 0 28px;}
.codex-step{position:relative;background:#fff;border:1px solid var(--line);border-radius:8px;padding:16px 14px;min-height:122px;}
.codex-step b{display:block;font-size:17px;color:var(--ink);margin-bottom:6px;}
.codex-step span{font-size:13px;line-height:1.7;color:var(--soft);}
.codex-table{width:100%;border-collapse:collapse;margin:14px 0 28px;font-size:14px;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden;}
.codex-table th{background:#17202a;color:#fff;text-align:left;padding:12px 14px;font-size:13px;}
.codex-table td{border-top:1px solid var(--line);padding:12px 14px;vertical-align:top;color:var(--soft);line-height:1.75;}
.codex-table td:first-child{font-weight:800;color:var(--ink);white-space:nowrap;}
.codex-call{background:linear-gradient(135deg,#17202a,#2563eb);color:#fff;border-radius:8px;padding:22px 24px;margin:26px 0;}
.codex-call b{display:block;font-size:24px;line-height:1.35;margin-bottom:8px;}
.codex-call p{margin:0;line-height:1.8;color:rgba(255,255,255,.92);}
.codex-slide-deck{display:grid;gap:18px;margin:14px 0 34px;counter-reset:slide;}
.codex-slide{position:relative;min-height:260px;padding:30px;border-radius:10px;border:1px solid var(--line);background:#fff;box-shadow:0 12px 34px rgba(15,23,42,.07);overflow:hidden;}
.codex-slide:before{counter-increment:slide;content:counter(slide,decimal-leading-zero);position:absolute;right:22px;top:18px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:44px;font-weight:900;color:rgba(37,99,235,.10);line-height:1;}
.codex-slide h3{position:relative;margin:0 0 14px;font-size:clamp(26px,3vw,38px);line-height:1.22;color:var(--ink);}
.codex-slide p{position:relative;margin:0 0 14px;font-size:17px;line-height:1.8;color:var(--soft);}
.codex-slide ul{position:relative;margin:12px 0 0;padding-left:1.2em;}
.codex-slide li{font-size:16px;line-height:1.75;margin:4px 0;color:var(--soft);}
.codex-slide strong{color:var(--ink);}
.codex-slide.dark{background:linear-gradient(135deg,#111827,#1d4ed8);border-color:#1d4ed8;color:#fff;}
.codex-slide.dark h3,.codex-slide.dark p,.codex-slide.dark li{color:#fff;}
.codex-slide.dark:before{color:rgba(255,255,255,.14);}
.codex-prompt{background:#0f172a;color:#e5e7eb;border-radius:8px;padding:16px 18px;margin:10px 0 20px;font-size:14px;line-height:1.8;white-space:pre-wrap;}
.codex-tree{background:#0f172a;color:#e5e7eb;border-radius:8px;padding:16px 18px;margin:12px 0 24px;overflow:auto;font-size:13px;line-height:1.7;}
.codex-check li{margin:7px 0;}
@media(max-width:860px){.codex-grid,.codex-grid.two,.codex-grid.four,.codex-flow{grid-template-columns:1fr}.codex-card h3,.codex-card h4{font-size:18px}.codex-table{font-size:13px}.codex-table td:first-child{white-space:normal}.codex-hero,.codex-slide{padding:22px}.codex-slide{min-height:auto}}
</style>

<div class="codex-onboard">

<div class="codex-hero">
<h2>Codex実践 スライド+動画  構築と応用</h2>
<p>準備編で「開く、頼む、確認する」まで進んだ人向けに、ここでは実際の運用を組みます。プロジェクトの分け方、フォルダの置き方、AGENTS.md、.codex/config.toml、skills、plugins、MCP、hooks、rules、automations、レビュー、ブラウザ確認、公式更新の追い方までを、仕事で使う前提でまとめます。</p>
</div>

<p class="codex-source">
公式確認: <a href="https://developers.openai.com/codex" target="_blank" rel="noopener">OpenAI Developers Codex Docs</a>、
<a href="https://openai.com/codex/" target="_blank" rel="noopener">Codex公式サイト</a>、
<a href="https://openai.com/academy/codex-for-work/" target="_blank" rel="noopener">Codex for work</a>、
<a href="https://developers.openai.com/codex/changelog" target="_blank" rel="noopener">Codex Changelog</a>、
<a href="https://developers.openai.com/codex/feature-maturity" target="_blank" rel="noopener">Feature Maturity</a>、
<a href="https://openai.com/index/codex-for-every-role-tool-workflow/" target="_blank" rel="noopener">Codex for every role, tool, and workflow</a> を参照。新機能の一次確認先として
<a href="https://x.com/OpenAI" target="_blank" rel="noopener">X: @OpenAI</a>、
<a href="https://x.com/OpenAIDevs" target="_blank" rel="noopener">X: @OpenAIDevs</a>、
<a href="https://openai.com/news/" target="_blank" rel="noopener">OpenAI News</a>、
<a href="https://github.com/openai/codex/releases" target="_blank" rel="noopener">openai/codex Releases</a> も掲載します。
</p>

<h2>動画版</h2>

<div class="codex-video">
<video controls playsinline preload="metadata" poster="./assets/codex-app-practice-poster.png">
  <source src="./assets/codex-app-practice.webm" type="video/webm">
</video>
</div>

<div class="codex-video-script">
<h3>収録用ナレーション構成 18分</h3>
<p>上の動画は実践編の要点を短く見せるスライド動画です。講師が長尺で収録する場合は、以下の台本に沿って各章を画面共有し、プロジェクトフォルダ、設定ファイル、レビュー画面、ブラウザ確認の順に見せます。</p>
<ol>
<li>0:00 導入。Codexは「1回使うアプリ」ではなく「仕事場を育てるアプリ」。</li>
<li>1:30 Project、Thread、Local、Worktree、Cloudを実例で分ける。</li>
<li>3:30 フォルダ設計。置いてよい資料、置かない秘密情報、成果物の置き場。</li>
<li>5:30 AGENTS.md、.codex/config.toml、.agents/skills の役割を見せる。</li>
<li>8:00 skills と plugins。作業手順と外部接続の違い。</li>
<li>10:30 hooks、rules、permissions。自動チェックと安全枠。</li>
<li>13:00 automations。Triage、thread automation、project automationの違い。</li>
<li>15:30 隠れ機能。deep links、slash commands、pets、memories、appshots、annotations、Sites。</li>
<li>17:00 公式アップデート先。X、Changelog、Feature Maturity、GitHub releases。</li>
</ol>
</div>

<h2>スライド版</h2>

<div class="codex-slide-deck" aria-label="Codex実践スライド">
<section class="codex-slide dark">
<h3>1. 導入の次は「仕事場づくり」</h3>
<p>Codexは単発の相談先ではなく、プロジェクト、履歴、差分、設定、連携を持つ作業場です。</p>
<ul>
<li>Projectで作業範囲を分ける</li>
<li>Threadで目的を分ける</li>
<li>設定と手順をファイルに残す</li>
</ul>
</section>

<section class="codex-slide">
<h3>2. Local / Worktree / Cloud</h3>
<p>同じCodexでも、どこで動かすかで安全性と速度が変わります。</p>
<ul>
<li>Local: 手元のフォルダを直接編集</li>
<li>Worktree: Gitの別作業場で並行作業</li>
<li>Cloud: 設定済み環境でリモート実行</li>
</ul>
</section>

<section class="codex-slide">
<h3>3. フォルダは「見せるもの」と「守るもの」を分ける</h3>
<p>Codexに見せる資料、作らせる成果物、見せない秘密情報を最初に分けます。</p>
<ul>
<li>docs: 方針と手順</li>
<li>content: 原稿と素材</li>
<li>outputs: 生成物</li>
<li>.env: 見せない、コミットしない</li>
</ul>
</section>

<section class="codex-slide">
<h3>4. AGENTS.mdは毎回言わないルール</h3>
<p>確認コマンド、禁止事項、言葉づかい、公開前チェックをAGENTS.mdに置きます。</p>
<ul>
<li>リポジトリ全体のルール</li>
<li>サブフォルダごとの上書き</li>
<li>導入編と実践編の共通土台</li>
</ul>
</section>

<section class="codex-slide">
<h3>5. 差分、レビュー、ブラウザ確認</h3>
<p>実務では「作った」より「確認できた」を重視します。</p>
<ul>
<li>review paneで差分を見る</li>
<li>inline commentsで直す場所を示す</li>
<li>in-app browserやChromeで表示を見る</li>
</ul>
</section>

<section class="codex-slide">
<h3>6. skillは作業手順書</h3>
<p>同じ依頼を何度もするなら、skillにします。Codexは必要な時だけSKILL.mdを読みます。</p>
<ul>
<li>講習資料を作る手順</li>
<li>週次レポート形式</li>
<li>公開前レビューの型</li>
</ul>
</section>

<section class="codex-slide">
<h3>7. pluginは道具箱</h3>
<p>pluginはskills、apps、MCP serversをまとめて配布できる単位です。</p>
<ul>
<li>Google DriveやGmailを使う</li>
<li>FigmaやCanvaで制作する</li>
<li>GitHubやSlack、Linearとつなぐ</li>
</ul>
</section>

<section class="codex-slide">
<h3>8. hooksとrulesは自動ガード</h3>
<p>hooksは作業の節目でスクリプトを走らせます。rulesはsandbox外コマンドの許可、確認、禁止を決めます。</p>
<ul>
<li>秘密情報チェック</li>
<li>危険コマンドのブロック</li>
<li>完了時の検証メモ</li>
</ul>
</section>

<section class="codex-slide">
<h3>9. automationは定期作業</h3>
<p>毎朝、毎週、一定間隔で戻ってくる仕事はautomationにします。</p>
<ul>
<li>Triageに結果を出す</li>
<li>thread automationで同じ会話に戻る</li>
<li>worktreeで本線を汚さず動かす</li>
</ul>
</section>

<section class="codex-slide">
<h3>10. 隠れ機能を覚える</h3>
<p>Command menu、slash commands、deep links、pets、memories、appshotsは、分かると作業速度が上がります。</p>
<ul>
<li>/plan /goal /review /status /mcp</li>
<li>codex://settings や codex://skills</li>
<li>Appshots、Memories、Codex pets</li>
</ul>
</section>

<section class="codex-slide">
<h3>11. 公式発表を見る場所を固定する</h3>
<p>Codexは更新が速いので、古い講習資料だけで判断しません。</p>
<ul>
<li>X: @OpenAI / @OpenAIDevs</li>
<li>Codex Changelog</li>
<li>Feature Maturity</li>
<li>GitHub releases</li>
</ul>
</section>

<section class="codex-slide dark">
<h3>12. 実務の完成条件</h3>
<p>実践編のゴールは、Codexを使えることではなく、仕事の流れが再現できることです。</p>
<ul>
<li>置き場が決まっている</li>
<li>手順が残っている</li>
<li>確認が自動化されている</li>
<li>公開前にレビューできる</li>
</ul>
</section>
</div>

<div class="codex-call">
<b>実践編の基本式は「Project + Rules + Skill + Review + Automation」。</b>
<p>毎回の依頼文を長くするのではなく、プロジェクトにルールを置き、繰り返す作業をskillにし、危険な作業をhooks/rulesで止め、定期作業をautomationに回します。</p>
</div>

<h2>実運用のフォルダ設計</h2>

<div class="codex-note">
初心者ほど、最初に大きなリポジトリを丸ごと渡しがちです。実務では「Codexに見せる場所」を意図的に小さくします。プロジェクトごとにフォルダを分け、不要な秘密情報や過去データを混ぜないことが安全と速度の両方に効きます。
</div>

<pre class="codex-tree"><code>C:\VSCode\Project\
  ai-hub\
    AGENTS.md                         # このプロジェクトのCodex向けルール
    .codex\
      config.toml                     # プロジェクト固有のCodex設定
      hooks.json                      # 共有する自動チェック
      rules\
        default.rules                 # 許可、確認、禁止するコマンド
    .agents\
      skills\
        lecture-builder\
          SKILL.md                    # 講習資料を作る手順
        publish-check\
          SKILL.md                    # 公開前チェックの手順
      plugins\
        marketplace.json              # repo内のpluginカタログ
    content\
      lectures\                       # 編集ソース
      assets\                         # 画像、PDF、動画素材
    site\
      build_site.py                   # ビルド
      dist\                           # 生成物
    docs\
      operations\                     # 運用手順
    outputs\
      reports\                        # 定期出力
    .env                              # 秘密情報。見せない、コミットしない
</code></pre>

<div class="codex-grid three">
<div class="codex-card" style="--accent:#2563eb"><span class="codex-label">Project</span><h3>1事業1プロジェクト</h3><p>AIハブ、みんなのWA、N-Designのように事業ごとにProjectを分けます。違う事業の秘密情報や方針が混ざらないようにします。</p></div>
<div class="codex-card" style="--accent:#0f8b8d"><span class="codex-label">Thread</span><h3>1目的1スレッド</h3><p>「講習資料を作る」「公開前レビュー」「Vercelデプロイ確認」のように、会話の目的を分けます。あとで検索しやすくなります。</p></div>
<div class="codex-card" style="--accent:#e85d5a"><span class="codex-label">Worktree</span><h3>大きい変更は別作業場</h3><p>トップページ刷新、管理画面変更、依存関係更新などはWorktreeに逃がします。Localで作業中の状態を壊さず試せます。</p></div>
</div>

<h2>設定の層</h2>

<table class="codex-table">
<tr><th>層</th><th>置き場所</th><th>何を書くか</th><th>実例</th></tr>
<tr><td>Prompt / Thread</td><td>今の会話</td><td>一回限りの条件、今日だけの判断、止めたい範囲</td><td>「今回は公開しない」「まず調査だけ」「日本語で説明」</td></tr>
<tr><td>AGENTS.md</td><td>repo rootや下位フォルダ</td><td>毎回守るプロジェクトルール、ビルド、検証、禁止事項</td><td>「site/build_site.pyで再ビルド」「本番確認URLを報告」</td></tr>
<tr><td>.codex/config.toml</td><td>projectまたはuser</td><td>model、reasoning、sandbox、approval、MCP、feature flags</td><td>workspace-write、on-request、web_search、memories</td></tr>
<tr><td>skills</td><td>.agents/skills or ~/.agents/skills</td><td>繰り返し使う作業手順</td><td>講習資料作成、PRレビュー、週次レポート</td></tr>
<tr><td>plugins</td><td>Plugin Directory / marketplace</td><td>skills、apps、MCP serversをまとめた道具箱</td><td>Google Drive、Figma、Canva、GitHub、Data Analytics</td></tr>
<tr><td>MCP</td><td>config.toml or plugin</td><td>外部ツール、DB、ブラウザ、社内ツールへの接続</td><td>OpenAI Docs MCP、Figma MCP、Playwright MCP、Sentry MCP</td></tr>
<tr><td>hooks</td><td>hooks.json or config.toml</td><td>作業前後に自動で走るチェック</td><td>PreToolUseで危険コマンド検査、Stopで完了ログ</td></tr>
<tr><td>rules</td><td>.codex/rules/*.rules or ~/.codex/rules</td><td>sandbox外コマンドのallow / prompt / forbidden</td><td>gh pr viewはprompt、rmはforbidden</td></tr>
<tr><td>automations</td><td>Codex sidebar</td><td>定期実行、監視、リマインド、同じthreadへの戻り</td><td>毎週金曜の進捗要約、PR状態確認、サイト更新確認</td></tr>
<tr><td>memories</td><td>~/.codex/memories</td><td>過去の作業から引き継ぐ傾向、好み、注意点</td><td>「この人は日本語説明を好む」「このrepoはVercel本番確認まで」</td></tr>
</table>

<h2>Codex公式用語フルマップ</h2>

<table class="codex-table">
<tr><th>用語</th><th>講習での説明</th><th>使う場面</th></tr>
<tr><td>Codex app</td><td>デスクトップで複数のCodex作業を並行管理する中心画面。</td><td>日常の実務、レビュー、ブラウザ確認、automation管理。</td></tr>
<tr><td>Codex CLI</td><td>terminal-firstのCodex。コマンドで実行、設定、確認する。</td><td>開発者がCLIで高速に作業する時。</td></tr>
<tr><td>IDE Extension</td><td>VS Codeなどのエディタと連動するCodex。</td><td>開いているファイルの文脈を使って直す時。</td></tr>
<tr><td>Codex web / Cloud</td><td>Webやcloud environmentでリモートに実行するCodex。</td><td>手元PCから切り離して作業する時。</td></tr>
<tr><td>Project</td><td>Codexが作業するフォルダ単位。</td><td>事業、アプリ、資料集ごとに分ける。</td></tr>
<tr><td>Thread</td><td>ChatGPTのchatに近い、1つの作業会話。</td><td>目的ごとに分けて履歴検索する。</td></tr>
<tr><td>Local</td><td>現在のプロジェクトフォルダを直接使うmode。</td><td>すぐ確認したい小さな作業。</td></tr>
<tr><td>Worktree</td><td>Git worktreeを使う別作業場。</td><td>大きな変更、並行作業、automation。</td></tr>
<tr><td>Cloud</td><td>remote/cloud environmentで実行するmode。</td><td>セットアップ済み環境で実行したい時。</td></tr>
<tr><td>Handoff</td><td>threadをLocalとWorktreeの間で移す流れ。</td><td>背景で作った変更を手元に持ってくる。</td></tr>
<tr><td>Codex-managed worktree</td><td>Codexが軽量に作る使い捨て寄りのworktree。</td><td>1スレッド1作業場で試す。</td></tr>
<tr><td>Permanent worktree</td><td>長く使うworktreeをプロジェクト化したもの。</td><td>継続的な検証環境や別ブランチ作業。</td></tr>
<tr><td>Detached HEAD</td><td>worktreeがまだブランチ名を持たず、特定commit上で作業している状態。</td><td>Codexが複数worktreeを作る時の初期状態。</td></tr>
<tr><td>Review pane</td><td>Git diffを見て、stage/revert/commentできる画面。</td><td>採用判断、差分確認、公開前レビュー。</td></tr>
<tr><td>Diff panel</td><td>変更差分を見るパネル。</td><td>変更内容の読み合わせ。</td></tr>
<tr><td>Inline comments</td><td>diffの行に直接つける修正指示。</td><td>「ここだけ直して」を精密に伝える。</td></tr>
<tr><td>Stage / Unstage / Revert</td><td>採用、採用解除、取り消し。</td><td>一部だけ採用したい時。</td></tr>
<tr><td>Commit / Push / PR</td><td>変更を履歴に残し、GitHubへ送り、Pull Requestを作る。</td><td>公開前の通常開発フロー。</td></tr>
<tr><td>Integrated terminal</td><td>thread内の組み込みterminal。</td><td>build、test、git status、dev server。</td></tr>
<tr><td>Local environments</td><td>worktree用setup scriptsやactionsを定義する設定。</td><td>npm install、build、dev server起動をボタン化。</td></tr>
<tr><td>Setup scripts</td><td>worktree作成時に自動実行する環境準備。</td><td>依存関係install、初期build。</td></tr>
<tr><td>Actions</td><td>よく使うコマンドをCodexアプリ上部のボタンにする。</td><td>Run、Test、Build、Preview。</td></tr>
<tr><td>In-app browser</td><td>Codex内ブラウザ。ログイン不要ページの確認向け。</td><td>localhost、file preview、公開ページ確認。</td></tr>
<tr><td>Browser use</td><td>Codexがin-app browserをクリック、入力、スクショ確認する機能。</td><td>表示崩れ再現、画面操作テスト。</td></tr>
<tr><td>Browser comments</td><td>画面上の場所にコメントをつける機能。</td><td>ボタン、カード、グラフの具体的修正。</td></tr>
<tr><td>Chrome extension</td><td>ログイン済みChromeをCodexが使うための拡張。</td><td>Gmail、Salesforce、会員画面、社内ツール。</td></tr>
<tr><td>Computer Use</td><td>Windows/macOSアプリを見て、クリックし、入力する機能。</td><td>GUIだけで再現する不具合、デスクトップアプリ確認。</td></tr>
<tr><td>Appshots</td><td>macOSの前面ウィンドウをCodex threadへ送る機能。</td><td>画面の状態を見せて相談する。</td></tr>
<tr><td>Command menu</td><td>Cmd/Ctrl+Kなどで開くコマンドメニュー。</td><td>設定、pet、reload skills、各種操作。</td></tr>
<tr><td>Slash commands</td><td>/で呼ぶ操作コマンド。</td><td>/plan、/goal、/review、/status、/mcp、/feedback。</td></tr>
<tr><td>/plan</td><td>複数手順の計画モード。</td><td>大きな作業を始める前。</td></tr>
<tr><td>/goal</td><td>持続的な完了目標を設定する。</td><td>長い作業を完了条件まで走らせる。</td></tr>
<tr><td>/review</td><td>コードレビューを開始する。</td><td>未コミット変更やPR差分の確認。</td></tr>
<tr><td>/status</td><td>thread ID、context、rate limitsなどを確認。</td><td>長い作業の状態確認。</td></tr>
<tr><td>/mcp</td><td>MCP serverの接続状態を確認。</td><td>FigmaやDocs接続が動かない時。</td></tr>
<tr><td>/feedback</td><td>ログ付きでフィードバックを送る。</td><td>Codex自体の不具合報告。</td></tr>
<tr><td>$skill</td><td>skillを明示起動する書き方。</td><td>$skill-creator、$imagegen、$my-skill。</td></tr>
<tr><td>@plugin</td><td>pluginやconnectorを明示して使う書き方。</td><td>@Chrome、@Browser、@Canvaなど。</td></tr>
<tr><td>Steer</td><td>Codex実行中に途中で軌道修正する操作。</td><td>「やっぱり削除でなく書き換えにして」。</td></tr>
<tr><td>Voice dictation</td><td>声でpromptを入力する機能。</td><td>長い依頼を話して入力。</td></tr>
<tr><td>Floating pop-out window</td><td>会話を別ウィンドウに出す機能。</td><td>ブラウザやエディタ横に置く。</td></tr>
<tr><td>Deep links</td><td>codex://でCodex内の画面を開くURL。</td><td>codex://settings、codex://skills、codex://automations。</td></tr>
<tr><td>Codex pets</td><td>進行中作業を見せる任意の小さな表示。</td><td>バックグラウンド作業の状態確認。</td></tr>
<tr><td>Profile</td><td>活動insights、tokens、streaksなどを見る設定領域。</td><td>利用状況を確認する。</td></tr>
<tr><td>Personalization</td><td>Friendly / Pragmatic / Noneやcustom instructions。</td><td>話し方と個人ルールの調整。</td></tr>
<tr><td>Context-aware suggestions</td><td>戻るべき作業候補を出す機能。</td><td>中断した仕事の再開。</td></tr>
<tr><td>Archived threads</td><td>アーカイブ済みthread一覧。</td><td>過去作業の復元。</td></tr>
<tr><td>Memories</td><td>過去threadから有用な文脈を引き継ぐ機能。</td><td>好み、注意点、技術スタックの再利用。</td></tr>
<tr><td>Chronicle</td><td>画面文脈からmemoryを補助するresearch preview。</td><td>対応環境で最近の作業文脈を拾う。</td></tr>
<tr><td>Automations</td><td>定期実行や監視をCodexに任せる機能。</td><td>毎朝brief、週次報告、PR確認。</td></tr>
<tr><td>Triage</td><td>automation結果の受信箱。</td><td>新しい発見があったrunを確認。</td></tr>
<tr><td>Standalone automation</td><td>毎回独立して走るautomation。</td><td>週次レポート、複数project監視。</td></tr>
<tr><td>Project automation</td><td>特定projectで走るautomation。</td><td>サイト更新確認、依存関係チェック。</td></tr>
<tr><td>Thread automation</td><td>同じthreadへ戻るheartbeat型automation。</td><td>デプロイ待ち、PRチェック、長いレビュー。</td></tr>
<tr><td>Custom schedule / cron</td><td>任意の実行スケジュール。</td><td>毎週月曜9時、毎日17時など。</td></tr>
<tr><td>AGENTS.md</td><td>Codexが作業前に読むproject guidance。</td><td>毎回守るルール、検証、公開条件。</td></tr>
<tr><td>AGENTS.override.md</td><td>一時的または近い階層の上書き指示。</td><td>特定フォルダだけルールを変える。</td></tr>
<tr><td>project_doc_fallback_filenames</td><td>AGENTS.md以外の名前を指示ファイルとして読む設定。</td><td>TEAM_GUIDE.mdを使っているrepo。</td></tr>
<tr><td>config.toml</td><td>Codexの主要設定ファイル。</td><td>model、sandbox、approval、MCP、feature flags。</td></tr>
<tr><td>CODEX_HOME</td><td>Codexの設定、認証、state、memoriesの基準フォルダ。</td><td>個人用とautomation用のprofile分離。</td></tr>
<tr><td>Project trust</td><td>project-local .codexを読み込んでよいかの信頼判断。</td><td>安全なrepoだけproject hooks/configを有効化。</td></tr>
<tr><td>Profiles</td><td>名前付き設定layer。</td><td>deep-review、fast-scanなどを切り替える。</td></tr>
<tr><td>Feature flags</td><td>optional/experimental機能のON/OFF。</td><td>hooks、memories、multi_agent、undoなど。</td></tr>
<tr><td>Sandbox</td><td>Codexがコマンド実行時に触れる範囲。</td><td>安全に自動作業させる。</td></tr>
<tr><td>read-only</td><td>読むだけのsandbox mode。</td><td>調査、レビュー、初見repo。</td></tr>
<tr><td>workspace-write</td><td>workspace内を書ける標準的mode。</td><td>通常の実装作業。</td></tr>
<tr><td>danger-full-access</td><td>sandbox制限を外す強いmode。</td><td>理解している高度作業だけ。</td></tr>
<tr><td>Approval policy</td><td>いつCodexが許可を求めるか。</td><td>untrusted、on-request、never。</td></tr>
<tr><td>approvals_reviewer</td><td>許可判断を誰が見るか。</td><td>userまたはauto_review。</td></tr>
<tr><td>Auto-review</td><td>承認要求をreviewer agentに回す仕組み。</td><td>低中リスクの承認を自動評価。</td></tr>
<tr><td>Permissions</td><td>read/write/deny、network、profilesでアクセスを定義。</td><td>.env deny、docs read、workspace write。</td></tr>
<tr><td>rules</td><td>コマンドprefixのallow/prompt/forbidden。</td><td>安全なghコマンドだけ許可。</td></tr>
<tr><td>prefix_rule</td><td>rulesで使うコマンドprefix定義。</td><td>["gh","pr","view"]をpromptにする。</td></tr>
<tr><td>hooks</td><td>agent loopの節目に自作scriptを差し込む仕組み。</td><td>秘密情報検査、検証、ログ、memory作成。</td></tr>
<tr><td>PreToolUse</td><td>tool使用前のhook event。</td><td>危険コマンドを事前確認。</td></tr>
<tr><td>PermissionRequest</td><td>許可要求時のhook event。</td><td>承認理由を検査。</td></tr>
<tr><td>PostToolUse</td><td>tool使用後のhook event。</td><td>結果ログや追加検査。</td></tr>
<tr><td>UserPromptSubmit</td><td>ユーザーprompt送信時のhook event。</td><td>秘密情報貼り付け防止。</td></tr>
<tr><td>Stop</td><td>turn停止時のhook event。</td><td>完了ログ、継続判断。</td></tr>
<tr><td>PreCompact / PostCompact</td><td>context圧縮前後のhook event。</td><td>長期作業の記録補助。</td></tr>
<tr><td>SubagentStart / SubagentStop</td><td>subagent開始/終了時のhook event。</td><td>並行調査のログ管理。</td></tr>
<tr><td>Skills</td><td>Codexが再利用する作業手順。</td><td>SKILL.md、scripts、references。</td></tr>
<tr><td>Progressive disclosure</td><td>必要になるまでskill本体を読まない仕組み。</td><td>contextを節約する。</td></tr>
<tr><td>Explicit invocation</td><td>$skill-nameで明示的に呼ぶ。</td><td>確実に特定skillを使う。</td></tr>
<tr><td>Implicit invocation</td><td>descriptionに合う時にCodexがskillを選ぶ。</td><td>自然文で作業を頼む。</td></tr>
<tr><td>agents/openai.yaml</td><td>skillのUI表示、policy、dependenciesを補足するmetadata。</td><td>アイコン、default prompt、MCP依存。</td></tr>
<tr><td>Plugins</td><td>skills、apps、MCP serversをまとめる配布単位。</td><td>チームやworkspaceに共有。</td></tr>
<tr><td>Plugin Directory</td><td>Codex app内のplugin一覧。</td><td>Curated by OpenAI、Shared with you、Created by you。</td></tr>
<tr><td>Marketplace</td><td>plugin catalog。</td><td>repoや個人でplugin配布。</td></tr>
<tr><td>Apps / Connectors</td><td>GitHub、Gmail、Google Driveなどの認証済み接続。</td><td>私的データや業務ツールを扱う。</td></tr>
<tr><td>MCP servers</td><td>Model Context Protocolで外部tool/contextをつなぐserver。</td><td>Figma、Docs、Playwright、Sentry。</td></tr>
<tr><td>STDIO server</td><td>ローカルコマンドとして起動するMCP server。</td><td>npxで起動するdeveloper docs serverなど。</td></tr>
<tr><td>Streamable HTTP server</td><td>URLで接続するMCP server。</td><td>remote MCP、OAuth連携。</td></tr>
<tr><td>OAuth / bearer token</td><td>MCPやappの認証方式。</td><td>Google、Figma、社内ツール。</td></tr>
<tr><td>Server instructions</td><td>MCP serverが返す全体指示。</td><td>tool利用の順序や制約。</td></tr>
<tr><td>Web search</td><td>Codexのfirst-party web search。</td><td>cached / live / disabledを使い分ける。</td></tr>
<tr><td>Image generation</td><td>thread内で画像生成や編集を行う機能。</td><td>UI素材、バナー、背景、placeholder。</td></tr>
<tr><td>Subagents</td><td>並行して別agentに調査やレビューを任せる機能。</td><td>セキュリティ、テスト、保守性を分担。</td></tr>
<tr><td>Main agent</td><td>判断と統合をする中心agent。</td><td>最終方針と成果物をまとめる。</td></tr>
<tr><td>Agent thread</td><td>subagent側のthread。</td><td>並行調査の詳細確認。</td></tr>
<tr><td>Sites</td><td>Codexで作ったinteractive website/appをURL共有する新機能。</td><td>workspace向けdashboard、planner、hub。</td></tr>
<tr><td>Annotations</td><td>作成物の一部を指して修正する仕組み。</td><td>site、documents、spreadsheets、slidesの局所修正。</td></tr>
<tr><td>Feature Maturity</td><td>機能のExperimental / Beta / Stableなどの成熟度。</td><td>本番運用に使う前の確認。</td></tr>
<tr><td>Changelog</td><td>Codexの変更履歴。</td><td>講習資料の更新、機能追加確認。</td></tr>
</table>

<h2>skillsの作り方</h2>

<div class="codex-note">
skillは「自分の仕事の型」です。短い説明で起動条件を明確にし、必要ならreferencesやscriptsを持たせます。まずは1作業1skill。大きな万能skillを作らない方が安定します。
</div>

<div class="codex-grid two">
<div class="codex-card" style="--accent:#2563eb">
<h3>実例: 講習資料skill</h3>
<div class="codex-prompt">---
name: lecture-builder
description: 講習資料をAIハブのcontent/lectures形式で作る時に使う。タイトル、summary、スライド、動画台本、実例、確認リストを含める。
---

1. 既存講習資料の文体を確認する。
2. frontmatterを作る。
3. 受講者向けの短いスライドを先に作る。
4. 本文は実例、表、テンプレートを多めにする。
5. site/build_site.pyで再ビルドできる形にする。</div>
</div>
<div class="codex-card" style="--accent:#0f8b8d">
<h3>実例: 公開前チェックskill</h3>
<div class="codex-prompt">---
name: publish-check
description: サイトや講習資料を公開する前に、差分、ビルド、リンク、秘密情報、公式URL、最終報告を確認する時に使う。
---

1. git diffを確認する。
2. 秘密情報が混じっていないか確認する。
3. ビルドまたは該当チェックを実行する。
4. 主要URLを確認する。
5. 何を確認したか短く報告する。</div>
</div>
</div>

<h2>pluginsの使い方</h2>

<table class="codex-table">
<tr><th>plugin/connector</th><th>使う理由</th><th>実務プロンプト例</th></tr>
<tr><td>GitHub</td><td>PR、issue、review、CI確認。</td><td>@GitHub このPRの未対応コメントを確認し、修正候補を重大度順に出して。</td></tr>
<tr><td>Google Drive</td><td>Docs、Sheets、Slidesの社内資料を使う。</td><td>@Google Drive 最新の講習メモを探し、今週のスライドに使える項目をまとめて。</td></tr>
<tr><td>Gmail</td><td>メール文脈を使った返信や要約。</td><td>@Gmail 今日の未返信メールから、返信が必要なものだけ下書きして。</td></tr>
<tr><td>Google Calendar</td><td>予定、会議準備、日次brief。</td><td>@Google Calendar 明日の予定を見て、準備が必要な会議だけ箇条書きにして。</td></tr>
<tr><td>Figma</td><td>デザイン読み取り、画面案、プロトタイプ。</td><td>@Figma この画面案を営業資料向けに整理して、実装時のUI注意点を出して。</td></tr>
<tr><td>Canva</td><td>SNS投稿、資料、ブランド素材。</td><td>@Canva この講習内容からInstagram用告知画像を3案作って。</td></tr>
<tr><td>Browser</td><td>localhostやfile previewを確認。</td><td>@Browser http://localhost:3000 を開いて、モバイル表示の崩れを確認して。</td></tr>
<tr><td>Chrome</td><td>ログイン済みChromeが必要なサイト。</td><td>@Chrome 管理画面にログイン済みの状態で、この設定ページの表示を確認して。</td></tr>
<tr><td>Computer Use</td><td>Windows/macOSアプリのGUI操作。</td><td>@Computer このデスクトップアプリを開き、設定画面の文言崩れを確認して。</td></tr>
<tr><td>OpenAI Developers</td><td>OpenAI公式docs確認。</td><td>@OpenAI Developers Codexのhooksとrulesの違いを公式docsで確認して。</td></tr>
<tr><td>Vercel</td><td>Next.js、deploy、環境変数、ログ確認。</td><td>@Vercel 本番deployの失敗理由を確認し、修正箇所を特定して。</td></tr>
<tr><td>Supabase</td><td>DB schema、SQL、Storage、RLS。</td><td>@Supabase このテーブルのRLSを読んで、管理画面の更新権限を確認して。</td></tr>
<tr><td>Shopify</td><td>Admin GraphQL、Liquid、Hydrogen、POS。</td><td>@Shopify 商品メタフィールドのGraphQL更新案を公式docsに沿って作って。</td></tr>
</table>

<h2>公式role-specific plugins</h2>

<table class="codex-table">
<tr><th>公式plugin</th><th>何を任せるか</th><th>実例</th></tr>
<tr><td>Data analytics</td><td>分析、原因調査、KPI、dashboard、report。</td><td>売上CSV、GA4、GSC、メモを渡して、週次KPIレポートを作る。</td></tr>
<tr><td>Creative production</td><td>広告、商品画像、campaign board、制作案。</td><td>新講習の告知文、画像案、SNS投稿をまとめる。</td></tr>
<tr><td>Sales</td><td>商談準備、follow-up、優先顧客、forecast。</td><td>顧客メモとメール履歴から、次回提案の論点を作る。</td></tr>
<tr><td>Product design</td><td>プロトタイプ、user flow、画面改善、Figma連携。</td><td>管理画面のスクショから、改善案と実装タスクを作る。</td></tr>
<tr><td>Public equity investing</td><td>上場企業調査、決算分析、投資仮説。</td><td>決算資料とニュースを読んで、投資仮説の変化を整理する。</td></tr>
<tr><td>Investment banking</td><td>M&A、pitch、比較会社、diligence。</td><td>買収候補リストから、初期pitch資料の構成を作る。</td></tr>
</table>

<h2>hooksとrulesの実例</h2>

<div class="codex-grid two">
<div class="codex-card" style="--accent:#e85d5a">
<h3>hookで止める例</h3>
<p>UserPromptSubmitでAPIキーらしき文字列を検出し、貼り付けを止める。PreToolUseで危険な削除コマンドを検査する。Stopで「確認したこと」をログに残す。</p>
<div class="codex-prompt">使いどころ:
- 秘密情報の貼り付け防止
- 破壊的コマンドの事前検査
- 完了時の品質チェック
- 会話要約やmemory候補の生成</div>
</div>
<div class="codex-card" style="--accent:#f2b705">
<h3>ruleで許可する例</h3>
<p>毎回使う安全なコマンドはrulesでpromptまたはallowに寄せます。危険なコマンドはforbiddenにします。rulesは「外へ出るコマンド」の門番です。</p>
<div class="codex-prompt">prefix_rule(
  pattern = ["gh", "pr", "view"],
  decision = "prompt",
  justification = "PR閲覧は承認つきで許可"
)

prefix_rule(
  pattern = ["rm"],
  decision = "forbidden",
  justification = "削除はPowerShellで対象確認後に個別承認"
)</div>
</div>
</div>

<h2>automationsの実例</h2>

<table class="codex-table">
<tr><th>種類</th><th>使う時</th><th>プロンプト例</th></tr>
<tr><td>Thread automation</td><td>同じ会話で継続確認したい。</td><td>このthreadに30分後戻って、Vercel deployが完了しているか確認し、失敗ならログを見て次の修正案を出して。</td></tr>
<tr><td>Standalone automation</td><td>毎回独立してよい定期作業。</td><td>毎週金曜17時に、今週の講習資料変更、未完了タスク、次週の候補を短い週報にしてTriageへ出して。</td></tr>
<tr><td>Project automation</td><td>特定projectを定期確認する。</td><td>毎朝8時にこのAIハブprojectを確認し、講習資料、トップページ、AI Watch出力に新しい差分があれば要約して。</td></tr>
<tr><td>Skill-driven automation</td><td>形式を固定したい。</td><td>毎週月曜に $publish-check を使い、site/distの主要ページと公式更新URLの確認結果をレポートして。</td></tr>
</table>

<h2>設定の隠れ機能</h2>

<table class="codex-table">
<tr><th>設定/機能</th><th>見落としがちな価値</th><th>使い方</th></tr>
<tr><td>Prevent sleep while running</td><td>長い作業中にPC sleepで止まる事故を減らす。</td><td>Settings > General。</td></tr>
<tr><td>Detail level</td><td>作業ログを詳しく見るか、会話をすっきりさせるかを選ぶ。</td><td>初心者はDefault、検証時はCoding mode。</td></tr>
<tr><td>Keyboard Shortcuts</td><td>よく使う操作を覚えると作業が速い。</td><td>Command menu、toggle terminal、find in thread。</td></tr>
<tr><td>Git settings</td><td>branch naming、force push、commit/PR文の生成方針を揃える。</td><td>チームで命名ルールを固定。</td></tr>
<tr><td>Browser use allowlist/blocklist</td><td>Codexが触ってよいサイトを制御する。</td><td>localhostは許可、機密サイトは必要時だけ。</td></tr>
<tr><td>Computer Use allowlist</td><td>どのアプリをCodexに触らせるか管理する。</td><td>信頼するアプリだけAlways allow。</td></tr>
<tr><td>Personalization</td><td>Friendly / Pragmatic / Noneで話し方を調整。</td><td>実務ではPragmaticが向く。</td></tr>
<tr><td>Custom instructions</td><td>個人の既定指示を入れる。</td><td>ただしプロジェクト必須ルールはAGENTS.mdへ。</td></tr>
<tr><td>Context-aware suggestions</td><td>再開すべき作業を提案してくれる。</td><td>中断が多い運用で有効。</td></tr>
<tr><td>Memories</td><td>過去の傾向を引き継ぐ。</td><td>ONにする前に、秘密情報を入れない運用にする。</td></tr>
<tr><td>Archived threads</td><td>閉じた会話を戻せる。</td><td>過去の講習資料作成threadを探す。</td></tr>
<tr><td>Deep links</td><td>Codex画面へ直接移動するURL。</td><td>codex://settings、codex://skills、codex://automations。</td></tr>
<tr><td>codex://plugins/install</td><td>plugin install flowを開く。</td><td>チーム導入資料にリンクを貼る。</td></tr>
<tr><td>codex://threads/new?prompt=&path=</td><td>特定folderとpromptで新規threadを開始。</td><td>講習の演習リンクを作る。</td></tr>
<tr><td>Appshots hotkey</td><td>前面アプリをすぐCodexへ共有。</td><td>macOSで画面状態を説明する手間を減らす。</td></tr>
<tr><td>Codex pets</td><td>進行中のCodex状態を小さく表示。</td><td>background taskを見失わない。</td></tr>
</table>

<h2>公式アップデートの確認先</h2>

<table class="codex-table">
<tr><th>確認先</th><th>URL</th><th>見るタイミング</th></tr>
<tr><td>Codex公式サイト</td><td><a href="https://openai.com/codex/" target="_blank" rel="noopener">https://openai.com/codex/</a></td><td>全体像、対応OS、代表機能を説明する前。</td></tr>
<tr><td>OpenAI Academy Codex</td><td><a href="https://openai.com/academy/codex-for-work/" target="_blank" rel="noopener">https://openai.com/academy/codex-for-work/</a></td><td>非エンジニア向けの実務例を探す時。</td></tr>
<tr><td>OpenAI Developers Codex Docs</td><td><a href="https://developers.openai.com/codex" target="_blank" rel="noopener">https://developers.openai.com/codex</a></td><td>設定名、機能名、公式用語を確認する時。</td></tr>
<tr><td>Codex Changelog</td><td><a href="https://developers.openai.com/codex/changelog" target="_blank" rel="noopener">https://developers.openai.com/codex/changelog</a></td><td>講習資料を更新する時、新機能を確認する時。</td></tr>
<tr><td>Feature Maturity</td><td><a href="https://developers.openai.com/codex/feature-maturity" target="_blank" rel="noopener">https://developers.openai.com/codex/feature-maturity</a></td><td>Experimental / Beta / Stableを判断する時。</td></tr>
<tr><td>Codex role/plugin発表</td><td><a href="https://openai.com/index/codex-for-every-role-tool-workflow/" target="_blank" rel="noopener">https://openai.com/index/codex-for-every-role-tool-workflow/</a></td><td>role-specific plugins、Sites、annotationsを説明する時。</td></tr>
<tr><td>X: OpenAI</td><td><a href="https://x.com/OpenAI" target="_blank" rel="noopener">https://x.com/OpenAI</a></td><td>OpenAI全体の大きな発表を追う時。</td></tr>
<tr><td>X: OpenAI Developers</td><td><a href="https://x.com/OpenAIDevs" target="_blank" rel="noopener">https://x.com/OpenAIDevs</a></td><td>Codex、API、SDK、開発者向け更新を追う時。</td></tr>
<tr><td>OpenAI News</td><td><a href="https://openai.com/news/" target="_blank" rel="noopener">https://openai.com/news/</a></td><td>製品横断の公式発表を追う時。</td></tr>
<tr><td>openai/codex Releases</td><td><a href="https://github.com/openai/codex/releases" target="_blank" rel="noopener">https://github.com/openai/codex/releases</a></td><td>CLIやオープンソース側のreleaseを追う時。</td></tr>
</table>

<h2>実務プロンプト集</h2>

<div class="codex-grid two">
<div class="codex-card" style="--accent:#2563eb">
<h3>プロジェクト初回整理</h3>
<div class="codex-prompt">このプロジェクトを読んで、Codex運用向けに次を整理してください。
1. 主要フォルダと役割
2. ビルド、テスト、プレビューの確認方法
3. AGENTS.mdに追加すべきルール
4. secretsや触らない方がよい場所
まだファイルは編集しないでください。</div>
</div>
<div class="codex-card" style="--accent:#0f8b8d">
<h3>skill化候補の抽出</h3>
<div class="codex-prompt">このrepoで繰り返し発生しそうな作業を10個挙げてください。
それぞれについて、promptで足りるもの、AGENTS.mdに書くもの、skill化すべきもの、automation化すべきものに分類してください。</div>
</div>
<div class="codex-card" style="--accent:#e85d5a">
<h3>公開前レビュー</h3>
<div class="codex-prompt">この変更を公開前レビューしてください。
実装はしないで、重大度順に、表示崩れ、リンク切れ、秘密情報、古い公式URL、検証不足を指摘してください。
最後に、公開してよいか、止めるべきかを一行で判断してください。</div>
</div>
<div class="codex-card" style="--accent:#f2b705">
<h3>automation設計</h3>
<div class="codex-prompt">この作業をautomation化する前提で設計してください。
1. standalone / project / thread のどれがよいか
2. 実行頻度
3. 何を見て、何があれば報告するか
4. 誤検知を減らす条件
5. 最初に手動テストするprompt</div>
</div>
</div>

<h2>運用チェックリスト</h2>

<ul class="codex-check">
<li>プロジェクトごとにCodexで開くフォルダが決まっている。</li>
<li>AGENTS.mdに、確認コマンド、公開ルール、秘密情報の扱いが書かれている。</li>
<li>Local、Worktree、Cloudを作業の大きさで使い分けられる。</li>
<li>Review paneでdiff、inline comments、stage、revertを使える。</li>
<li>in-app browser、Chrome extension、Computer Useの違いを説明できる。</li>
<li>繰り返す作業をskillsにし、外部接続が必要な作業をplugins/MCPで扱える。</li>
<li>hooksとrulesで、自動チェックと安全なコマンド許可を分けられる。</li>
<li>automationsのTriage、standalone、project、thread automationを使い分けられる。</li>
<li>Memories、Appshots、deep links、Codex pets、annotations、Sitesを「使う場面」まで説明できる。</li>
<li>X、OpenAI News、Codex Changelog、Feature Maturity、GitHub releasesの確認先が資料内にある。</li>
</ul>

<h2>講師向けの進行メモ</h2>

<ol>
<li>最初に「Codexは仕事場を育てるアプリ」と言う。</li>
<li>ProjectとThreadを、フォルダと会話の違いとして説明する。</li>
<li>Localは手元、Worktreeは別作業場、Cloudはリモート実行、と短く分ける。</li>
<li>AGENTS.md、.codex/config.toml、skills、plugins、MCP、hooks、rules、automationsを「設定の層」として並べる。</li>
<li>一気に全部設定させない。まずAGENTS.md、次にskill、必要になったらplugin/MCP、最後にhooks/automation。</li>
<li>受講者には公式更新先をブックマークさせる。Xは速報、Changelogは仕様確認、Feature Maturityは本番判断に使う。</li>
</ol>

</div>
