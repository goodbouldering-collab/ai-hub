---
title: Codexアプリ導入手順 スライド・動画つき初期設定ガイド
date: 2026-06-05
role: 講習資料 / Codex導入
gen_by: Codex
summary: ChatGPTは使えるがCodexアプリは初めての人向けに、導入手順・最初の依頼・安全装置・独立レビューを、ページ内スライドと動画で見られる講習資料。
---

<style>
.codex-onboard{--ink:var(--text,#0f172a);--soft:var(--text-soft,#334155);--mut:var(--muted,#64748b);--line:var(--line,#e2e8f0);--pri:var(--primary,#2563eb);--bg:#fff;--wash:#f8fafc;--teal:#0f8b8d;--coral:#e85d5a;--green:#2f9d58;--amber:#f2b705;color:var(--ink);}
.codex-onboard *{box-sizing:border-box;}
.codex-hero{margin:4px 0 26px;padding:28px;border:1px solid var(--line);border-radius:10px;background:linear-gradient(135deg,#eff6ff 0%,#fff 54%,#ecfdf5 100%);box-shadow:0 18px 50px rgba(15,23,42,.08);}
.codex-hero h2{margin:0 0 10px;font-size:clamp(30px,4.5vw,52px);line-height:1.15;letter-spacing:0;color:var(--ink);}
.codex-hero p{margin:0;font-size:17px;line-height:1.85;color:var(--soft);}
.codex-source{font-size:13px;line-height:1.8;color:var(--mut);margin:10px 0 22px;}
.codex-source a{font-weight:700;}
.codex-video{margin:8px 0 28px;background:#111827;border-radius:8px;padding:10px;box-shadow:0 18px 50px rgba(15,23,42,.18);}
.codex-video video{display:block;width:100%;border-radius:6px;background:#000;}
.codex-note{border:1px solid var(--line);border-left:5px solid var(--pri);background:var(--wash);border-radius:8px;padding:16px 18px;margin:16px 0 26px;font-size:15px;line-height:1.85;color:var(--soft);}
.codex-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0 28px;}
.codex-grid.two{grid-template-columns:repeat(2,1fr);}
.codex-card{background:var(--bg);border:1px solid var(--line);border-top:5px solid var(--accent,var(--pri));border-radius:8px;padding:18px;box-shadow:0 8px 26px rgba(15,23,42,.05);}
.codex-card h3,.codex-card h4{margin:0 0 8px;font-size:20px;line-height:1.35;color:var(--ink);}
.codex-card p,.codex-card li{font-size:14px;line-height:1.8;color:var(--soft);}
.codex-card ul{margin:8px 0 0;padding-left:1.2em;}
.codex-label{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:800;letter-spacing:.06em;color:#fff;background:var(--accent,var(--pri));border-radius:999px;padding:3px 10px;margin-bottom:10px;}
.codex-flow{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0 28px;}
.codex-step{position:relative;background:#fff;border:1px solid var(--line);border-radius:8px;padding:16px 14px;min-height:120px;}
.codex-step b{display:block;font-size:18px;color:var(--ink);margin-bottom:6px;}
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
.codex-check li{margin:7px 0;}
@media(max-width:760px){.codex-grid,.codex-grid.two,.codex-flow{grid-template-columns:1fr}.codex-card h3,.codex-card h4{font-size:18px}.codex-table{font-size:13px}.codex-table td:first-child{white-space:normal}.codex-hero,.codex-slide{padding:22px}.codex-slide{min-height:auto}}
</style>

<div class="codex-onboard">

<div class="codex-hero">
<h2>Codexは、作業場を持つAI共同作業者。</h2>
<p>このページは、Codexアプリの導入手順を「短い動画」と「投影しやすいスライド」で見られる講習用ページです。AIコーディング実装講習とは別資料として、初回講習の入口に置きます。</p>
</div>

<p class="codex-source">
公式確認: OpenAI の <a href="https://openai.com/codex/get-started/" target="_blank" rel="noopener">Get started with Codex</a> と
<a href="https://openai.com/academy/codex-how-to-start/" target="_blank" rel="noopener">How to get started with Codex</a> を元に、講習向けに手順を短く整理しています。
</p>

<h2>動画版</h2>

<div class="codex-video">
<video controls playsinline preload="metadata" poster="./assets/codex-app-onboarding-poster.png">
  <source src="./assets/codex-app-onboarding.webm" type="video/webm">
</video>
</div>

<h2>スライド版</h2>

<div class="codex-slide-deck" aria-label="Codex導入手順スライド">
<section class="codex-slide dark">
<h3>1. Codexは「会話」ではなく「作業場」</h3>
<p>ChatGPTは相談相手。Codexはフォルダを読み、編集し、確認まで進める共同作業者です。</p>
<ul>
<li>作業フォルダを選ぶ</li>
<li>小さなタスクを渡す</li>
<li>差分を見て採用する</li>
</ul>
</section>

<section class="codex-slide">
<h3>2. 最初はChatGPTでログイン</h3>
<p>公式手順はシンプルです。Codexを開き、ChatGPTアカウントでサインインします。</p>
<ul>
<li>Codexを開く</li>
<li>ChatGPTでサインイン</li>
<li>プロジェクトを選ぶ</li>
</ul>
</section>

<section class="codex-slide">
<h3>3. フォルダかGitリポジトリを選ぶ</h3>
<p>Codexが触れる場所を先に限定します。ここが安全装置の第一歩です。</p>
<ul>
<li>作業用フォルダを1つ選ぶ</li>
<li>最初は空フォルダでもよい</li>
<li>秘密情報が入った場所は避ける</li>
</ul>
</section>

<section class="codex-slide">
<h3>4. 最初の依頼は小さく</h3>
<p>いきなり公開サイト全体を任せません。1ファイル、1画面、1文章から始めます。</p>
<ul>
<li>「このフォルダを見て説明して」</li>
<li>「小さく直せる候補を3つ出して」</li>
<li>「変更前に確認して」</li>
</ul>
</section>

<section class="codex-slide">
<h3>5. 画面と差分で確認する</h3>
<p>Codexの成果は、言葉ではなく結果で確認します。</p>
<ul>
<li>ブラウザ表示を見る</li>
<li>変更差分を見る</li>
<li>リンク・画像・文字サイズを確認する</li>
</ul>
</section>

<section class="codex-slide">
<h3>6. 公開前は独立レビュー</h3>
<p>作った直後は見落としが出ます。別視点で壊れそうな点を先に出します。</p>
<ul>
<li>表示崩れ</li>
<li>リンク切れ</li>
<li>秘密情報の混入</li>
<li>公開前に止めるべき変更</li>
</ul>
</section>
</div>

<div class="codex-note">
この資料は、ChatGPTを使ったことがあり、ChatGPTで小さなプロジェクト作成も試したことがある人向けです。目的は「Codexをノーコードの魔法ボタンとして誤解せず、作業を任せて、差分を見て、採用判断できる状態」にすることです。
</div>

<h2>この講習で一番伝えること</h2>

<div class="codex-call">
<b>Codexは、会話だけのAIではなく「作業場を持つAI共同作業者」です。</b>
<p>ファイルを読み、編集し、コマンドを実行し、ブラウザで確認できます。だからこそ、作らせっぱなしにせず、差分確認と独立レビューをセットにします。</p>
</div>

<div class="codex-grid three">
<div class="codex-card" style="--accent:#2563eb"><span class="codex-label">1</span><h3>小さく頼む</h3><p>最初は見出し変更、色調整、README要約など、失敗しても直しやすい作業から始めます。</p></div>
<div class="codex-card" style="--accent:#2f9d58"><span class="codex-label">2</span><h3>画面で確認する</h3><p>BrowserやChromeで表示を見ます。コードだけを見て「できた」と判断しません。</p></div>
<div class="codex-card" style="--accent:#e85d5a"><span class="codex-label">3</span><h3>独立レビューで選ぶ</h3><p>作った人とは別の視点で、壊れそうな点、仕様漏れ、テスト不足を先に出します。</p></div>
</div>

<h2>ChatGPTとの違い</h2>

<table class="codex-table">
<tr><th>項目</th><th>ChatGPT</th><th>Codexアプリ</th></tr>
<tr><td>役割</td><td>会話で相談し、文章や案を作る</td><td>プロジェクトを読み、編集し、実行と確認まで手伝う</td></tr>
<tr><td>作業場所</td><td>基本はチャット内</td><td>ローカルフォルダ、GitHub、worktreeなどの作業場を持つ</td></tr>
<tr><td>確認</td><td>ユーザーが別で確認することが多い</td><td>テスト、ビルド、ブラウザ確認、レビューまで流れにできる</td></tr>
<tr><td>初心者の期待値</td><td>「答えを出してくれる」</td><td>「作業を任せ、差分を見て採用する」</td></tr>
</table>

<h2>初回導入でやること</h2>

<div class="codex-flow">
<div class="codex-step"><b>1. 開く</b><span>作りたいサイト、資料、アプリのフォルダをCodexで開きます。</span></div>
<div class="codex-step"><b>2. 目的を書く</b><span>何を作るか、どこを確認するかを短く指定します。</span></div>
<div class="codex-step"><b>3. 小さく依頼</b><span>まずは1画面、1文章、1機能だけ任せます。</span></div>
<div class="codex-step"><b>4. 見て選ぶ</b><span>表示確認、差分確認、独立レビューで採用を決めます。</span></div>
</div>

<h3>最初から触らなくてよいもの</h3>

<div class="codex-grid two">
<div class="codex-card" style="--accent:#64748b">
<h3>後回しでよい</h3>
<ul>
<li>モデル選択の細かい調整</li>
<li>approval設定の全項目</li>
<li>MCPサーバーの細かい設定例</li>
<li>プラグイン開発やmanifest詳細</li>
<li>CLIコマンドの網羅</li>
</ul>
</div>
<div class="codex-card" style="--accent:#2563eb">
<h3>最初に決める</h3>
<ul>
<li>どのフォルダで作業するか</li>
<li>何ができたら完了か</li>
<li>どの画面やコマンドで確認するか</li>
<li>公開前に誰目線でレビューするか</li>
<li>秘密情報や触ってはいけない場所</li>
</ul>
</div>
</div>

<h2>Codex独自用語カード</h2>

<table class="codex-table">
<tr><th>用語</th><th>初心者向けの意味</th><th>初回での扱い</th></tr>
<tr><td>AGENTS.md</td><td>Codexへの会社ルール。毎回言わなくていいことを書く場所</td><td>最初に確認。なければ簡単に作る</td></tr>
<tr><td>worktree</td><td>別フォルダの作業場。本線を汚さず別案を試す</td><td>複数案や大きな変更で使う</td></tr>
<tr><td>独立レビュー</td><td>作った人とは別視点のチェック。褒めるよりリスク優先</td><td>公開前、アップロード前に必ず使う</td></tr>
<tr><td>sandbox</td><td>Codexが触れる範囲を制限する安全枠</td><td>「勝手に壊さない」ための仕組みとして理解</td></tr>
<tr><td>approval</td><td>危ない操作や外部アクセスの前に止まる確認</td><td>削除、外部接続、秘密情報では慎重に判断</td></tr>
<tr><td>hooks</td><td>作業前後に自動で走るチェック係</td><td>初回は存在だけ理解。自作は後回し</td></tr>
<tr><td>MCP</td><td>外部ツールへの接続口。Codexに道具を増やす仕組み</td><td>仕組みとして理解。詳細設定は必要時</td></tr>
<tr><td>Apps / Connectors</td><td>GitHub、Gmail、Figmaなど、実際につなぐサービス</td><td>ログイン済みサービスを扱う時に使う</td></tr>
<tr><td>Browser</td><td>Codex内ブラウザ。ローカルサイトの確認に向く</td><td>表示確認の基本</td></tr>
<tr><td>Chrome</td><td>自分のログイン済みChromeを使う</td><td>会員画面、管理画面、ログイン必須ページで使う</td></tr>
<tr><td>Computer Use</td><td>WindowsアプリやPC操作を扱う</td><td>ブラウザ外の画面操作が必要な時だけ</td></tr>
<tr><td>goal</td><td>完了条件を持たせる考え方</td><td>長い作業では「どこまでやったら完了か」を指定</td></tr>
<tr><td>automation</td><td>定期チェックや後追いを任せる仕組み</td><td>毎週確認、監視、リマインドなどで使う</td></tr>
</table>

<h2>公式ロール別プラグイン</h2>

<div class="codex-note">
OpenAIは2026年6月2日の公式発表
<a href="https://openai.com/index/codex-for-every-role-tool-workflow/" target="_blank" rel="noopener">Codex for every role, tool, and workflow</a>
で、Codexを職種ごとの仕事に合わせるロール別プラグインを発表しました。ここでいうプラグインは、スキル、アプリ連携、MCP、手順、素材をまとめた「仕事別の道具箱」です。
</div>

<table class="codex-table">
<tr><th>公式プラグイン</th><th>向いている人</th><th>できることの例</th></tr>
<tr><td>Data analytics</td><td>分析担当、経営、現場リーダー</td><td>データを調べる、指標変化の理由を説明する、レポートやダッシュボードを作る</td></tr>
<tr><td>Creative production</td><td>マーケ、制作、EC、広告担当</td><td>企画書からキャンペーン案、広告バリエーション、商品ライフスタイル画像、EC向け画像セットを作る</td></tr>
<tr><td>Sales</td><td>営業、CS、商談担当</td><td>優先アカウントの抽出、商談準備、フォローアップ、顧客情報更新、失注リスク確認を行う</td></tr>
<tr><td>Product design</td><td>プロダクト担当、UI/UX、事業企画</td><td>初期アイデアを試作品にする、ユーザーフローを監査する、ライブURLやスクリーンショットからプロトタイプを作る</td></tr>
<tr><td>Public equity investing</td><td>投資、IR分析、上場企業調査</td><td>決算レビュー、企業比較、投資仮説の強弱確認、市場情報の整理を行う</td></tr>
<tr><td>Investment banking</td><td>投資銀行、M&A、財務アドバイザー</td><td>ピッチ資料、類似企業・類似取引分析、デューデリジェンス内容をクライアント向け資料にまとめる</td></tr>
</table>

<div class="codex-card" style="--accent:#0f8b8d">
<h3>初心者向けの覚え方</h3>
<p>「プラグインを入れる」とは、Codexにその仕事の進め方と接続先をまとめて渡すことです。たとえばCreative productionなら制作系、Salesなら営業系、Product designなら試作品づくりの作業を始めやすくなります。</p>
</div>

<div class="codex-note">
公式テンプレートは <a href="https://github.com/openai/role-specific-plugins" target="_blank" rel="noopener">openai/role-specific-plugins</a> にも公開されています。講習では作成手順まで深掘りせず、「どの仕事をCodexに任せやすくなるか」を先に理解します。
</div>

<h2>プラグインを構成する6要素</h2>

<div class="codex-note">
公式ロール別プラグインと、下の6要素は別物です。ロール別プラグインの中に、必要に応じて skills / hooks / scripts / assets / MCP / apps が入っています。全部を最初から使う必要はありません。
</div>

<table class="codex-table">
<tr><th>種類</th><th>言い換え</th><th>何に使うか</th><th>初回教材での扱い</th></tr>
<tr><td>skills</td><td>作業手順書</td><td>特定作業の進め方をCodexに渡す</td><td>必須。例だけ見る</td></tr>
<tr><td>hooks</td><td>自動チェック係</td><td>作業前後にlint、記録、確認などを走らせる</td><td>概念だけ。設定は後回し</td></tr>
<tr><td>scripts</td><td>便利ボタンの中身</td><td>よく使う処理を実行ファイルにまとめる</td><td>軽く触れる</td></tr>
<tr><td>assets</td><td>素材箱</td><td>画像、テンプレ、サンプル素材を置く</td><td>軽く触れる</td></tr>
<tr><td>MCP</td><td>外部サービスへの接続口</td><td>DB、ブラウザ、独自ツールなどにつなぐ</td><td>例だけ。深掘り不要</td></tr>
<tr><td>apps</td><td>実際につなぐアプリ</td><td>GitHub、Gmail、Figma、Canvaなどの連携先</td><td>実用例として見せる</td></tr>
</table>

<h3>「フックがあります」の意味</h3>

<div class="codex-card" style="--accent:#f2b705">
<h3>作業のタイミングで、自動処理が走る可能性があるというサインです。</h3>
<p>たとえば、編集後に整形する、実行前に危険操作を止める、完了後に記録する、といった用途です。初心者は「自動チェック係がいる」と覚えれば十分です。</p>
</div>

<h2>独立レビューの依頼テンプレート</h2>

<div class="codex-prompt">この変更を独立レビューしてください。
実装はしないで、初心者にも分かるように、壊れそうな点を重大度順に指摘してください。
特に、表示崩れ、リンク切れ、説明不足、公開前に止めるべき点を見てください。</div>

<h2>実装依頼のテンプレート</h2>

<div class="codex-prompt">このフォルダで、〇〇を作ってください。
AGENTS.mdのルールに従ってください。
最後に、ブラウザ表示と主要リンクを確認し、何を確認したか報告してください。</div>

<h2>アップロード前チェック</h2>

<ul class="codex-check">
<li>受講者が「最初に何を開いて、何を頼めばよいか」分かる。</li>
<li>Codexがノーコード魔法ではなく、作業を任せて確認するアプリだと伝わる。</li>
<li>AGENTS.md、worktree、独立レビュー、hooks、MCP、Appsの意味が短く説明されている。</li>
<li>OpenAI公式のロール別プラグイン6種類が入っている。</li>
<li>プラグインを構成する6要素、skills / hooks / scripts / assets / MCP / apps が入っている。</li>
<li>Browser、Chrome、Computer Use の使い分けが入っている。</li>
<li>公開前に独立レビューを入れる流れになっている。</li>
</ul>

<h2>講師向けの進行メモ</h2>

<ol>
<li>最初に「Codexは作業場を持つAI」と言う。</li>
<li>次に「ノーコードでも始められるが、確認と採用判断は必要」と言う。</li>
<li>画面を見る道具、独立レビュー、worktreeを早めに紹介する。</li>
<li>公式ロール別プラグイン6種類は「仕事別の道具箱」として見せる。</li>
<li>skills / hooks / scripts / assets / MCP / apps は、プラグインの中身として区別して説明する。</li>
<li>設定の全項目説明、MCPの詳細設定、プラグイン開発は別講座に分ける。</li>
</ol>

</div>
