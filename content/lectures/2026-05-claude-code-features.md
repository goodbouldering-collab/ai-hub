---
title: Claude Code 2026 棚卸し — 開発フローを変えた機能だけ
date: 2026-05-21
role: 開発メモ / インフォグラフィック
gen_by: 由井 辰美 / AIハブ
summary: 2026年1月〜5月のClaude Codeリリースから「実際に手元の開発フローが変わった」機能だけを、タイムライン・カテゴリカード・コマンド早見表のインフォグラフィックで一望する。コマンド名・設定キー・出荷時期(Week番号)は公式 changelog / What's new で裏取り済み。
---

<style>
.cc-info{--ink:var(--text,#0f172a);--soft:var(--text-soft,#334155);--mut:var(--muted,#64748b);--ln:var(--line,#e2e8f0);--pri:var(--primary,#2563eb);--pribg:var(--primary-bg,#eff6ff);--em:var(--emerald,#10b981);--am:var(--amber,#f59e0b);--pk:var(--pink,#ec4899);font-feature-settings:"palt";}
.cc-info *{box-sizing:border-box;}
.cc-note{background:var(--pribg);border:1px solid var(--ln);border-left:4px solid var(--pri);border-radius:12px;padding:14px 18px;font-size:14px;color:var(--soft);line-height:1.8;margin:8px 0 28px;}
.cc-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:0 0 36px;}
.cc-stat{background:var(--bg-white,#fff);border:1px solid var(--ln);border-radius:16px;padding:18px 16px;text-align:center;box-shadow:0 8px 28px rgba(15,23,42,.06);}
.cc-stat b{display:block;font-size:30px;line-height:1.1;color:var(--pri);font-weight:800;letter-spacing:-.02em;}
.cc-stat span{display:block;margin-top:6px;font-size:12px;color:var(--mut);font-weight:600;letter-spacing:.03em;}
.cc-h{font-size:13px;font-weight:800;letter-spacing:.14em;color:var(--mut);text-transform:uppercase;margin:40px 0 16px;display:flex;align-items:center;gap:10px;}
.cc-h::after{content:"";flex:1;height:1px;background:var(--ln);}
.cc-time{position:relative;margin:0 0 8px;padding-left:26px;}
.cc-time::before{content:"";position:absolute;left:7px;top:6px;bottom:6px;width:2px;background:linear-gradient(var(--pri),var(--pk));}
.cc-row{position:relative;padding:10px 0 16px;}
.cc-row::before{content:"";position:absolute;left:-23px;top:14px;width:12px;height:12px;border-radius:50%;background:var(--bg-white,#fff);border:3px solid var(--pri);}
.cc-wk{display:inline-block;font-size:11px;font-weight:800;color:#fff;background:var(--pri);border-radius:999px;padding:2px 10px;letter-spacing:.04em;}
.cc-when{font-size:12px;color:var(--mut);margin-left:8px;}
.cc-row p{margin:6px 0 0;font-size:14px;color:var(--soft);line-height:1.7;}
.cc-row code{background:var(--pribg);color:var(--pri);padding:1px 6px;border-radius:6px;font-size:13px;font-weight:600;}
.cc-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.cc-card{background:var(--bg-white,#fff);border:1px solid var(--ln);border-radius:16px;padding:20px;box-shadow:0 8px 28px rgba(15,23,42,.05);border-top:4px solid var(--accent,var(--pri));}
.cc-card.em{--accent:var(--em);} .cc-card.am{--accent:var(--am);} .cc-card.pk{--accent:var(--pk);} .cc-card.pri{--accent:var(--pri);}
.cc-card h4{margin:0 0 4px;font-size:17px;color:var(--ink);font-weight:800;}
.cc-card .sub{font-size:12px;color:var(--mut);margin:0 0 12px;font-weight:600;}
.cc-card ul{margin:0;padding:0;list-style:none;}
.cc-card li{padding:8px 0;border-top:1px dashed var(--ln);font-size:13.5px;color:var(--soft);line-height:1.65;}
.cc-card li:first-child{border-top:none;}
.cc-card code{background:#0f172a;color:#e2e8f0;padding:2px 7px;border-radius:6px;font-size:12.5px;font-weight:600;white-space:nowrap;}
.cc-card .tag{display:inline-block;font-size:10px;font-weight:800;color:var(--accent,var(--pri));background:color-mix(in srgb,var(--accent,var(--pri)) 12%,transparent);border-radius:999px;padding:1px 8px;margin-left:6px;letter-spacing:.04em;vertical-align:1px;}
.cc-cheat{width:100%;border-collapse:collapse;font-size:13px;margin:4px 0;background:var(--bg-white,#fff);border:1px solid var(--ln);border-radius:14px;overflow:hidden;}
.cc-cheat th{background:#0f172a;color:#fff;text-align:left;padding:11px 14px;font-size:12px;letter-spacing:.05em;}
.cc-cheat td{padding:10px 14px;border-top:1px solid var(--ln);color:var(--soft);vertical-align:top;}
.cc-cheat td code{background:var(--pribg);color:var(--pri);padding:2px 7px;border-radius:6px;font-weight:700;font-size:12.5px;white-space:nowrap;}
.cc-cheat tr:nth-child(even) td{background:#f8fafc;}
.cc-flag{background:linear-gradient(135deg,var(--pri),var(--pk));color:#fff;border-radius:18px;padding:24px 26px;margin:36px 0 12px;box-shadow:0 16px 44px rgba(37,99,235,.28);}
.cc-flag b{font-size:22px;font-weight:800;display:block;margin-bottom:8px;letter-spacing:-.01em;}
.cc-flag p{margin:0;font-size:14px;line-height:1.8;opacity:.96;}
.cc-flag .big{font-size:34px;font-weight:900;}
.cc-src{font-size:12px;color:var(--mut);line-height:1.8;border-top:1px solid var(--ln);margin-top:34px;padding-top:16px;}
@media(max-width:680px){.cc-stats{grid-template-columns:repeat(2,1fr);}.cc-grid{grid-template-columns:1fr;}.cc-stat b{font-size:24px;}}
</style>

<div class="cc-info">

<div class="cc-note">公式 changelog と週次ダイジェスト（code.claude.com）を引いて確認した内容だけを載せている。試していない伝聞や、名前があやしいものは落とした。ここのコマンド名・設定キーはそのまま打って動く前提。<b>Week番号</b>は2026年の週（W13≒3月下旬 〜 W20≒5月中旬）。</div>

<div class="cc-stats">
<div class="cc-stat"><b>Jan→May</b><span>対象期間</span></div>
<div class="cc-stat"><b>14</b><span>採り上げた機能</span></div>
<div class="cc-stat"><b>+50%</b><span>週次上限 (〜7/13)</span></div>
<div class="cc-stat"><b>Opus 4.7</b><span>既定モデル (Max/Team)</span></div>
</div>

<div class="cc-h">⏱ タイムライン — 何がいつ来たか</div>
<div class="cc-time">
<div class="cc-row"><span class="cc-wk">W13</span><span class="cc-when">3月下旬</span><p><b>Auto Mode</b>（<code>auto</code> 権限モード, 研究プレビュー）/ Windows <b>PowerShell ネイティブ対応</b></p></div>
<div class="cc-row"><span class="cc-wk">W14</span><span class="cc-when">3月末〜4月頭</span><p><b>Computer use in CLI</b>（研究プレビュー）— GUI をクリックして変更を検証</p></div>
<div class="cc-row"><span class="cc-wk">W15</span><span class="cc-when">4月上旬</span><p><b>バックグラウンドセッション</b> <code>claude --bg</code> 確定 / <b>Ultraplan</b> / <b>Monitor</b> ツール / <code>/loop</code></p></div>
<div class="cc-row"><span class="cc-wk">W16</span><span class="cc-when">4月中旬</span><p><b>Opus 4.7</b> 既定化 / <code>/effort</code> スライダー化・最上位 <code>xhigh</code> 追加</p></div>
<div class="cc-row"><span class="cc-wk">W19</span><span class="cc-when">5月頭</span><p><code>autoMode.hard_deny</code> / プラグイン <code>.zip</code>・URL 読み込み / <code>worktree.bgIsolation</code></p></div>
<div class="cc-row"><span class="cc-wk">W20</span><span class="cc-when">5月中旬</span><p><b>Agent View</b> <code>claude agents</code> / <code>/goal</code> 自走ループ</p></div>
<div class="cc-row"><span class="cc-wk">5/13</span><span class="cc-when">5月中旬</span><p><b>週次上限 +50%</b>（〜7/13 の期間限定）</p></div>
</div>

<div class="cc-h">🧩 並列運用が「前提」になった三点セット</div>
<div class="cc-grid">
<div class="cc-card pri">
<h4>バックグラウンドセッション<span class="tag">W15</span></h4>
<p class="sub">ターミナルを開きっぱなしにしない</p>
<ul>
<li><code>claude --bg</code> で投入、会話中は <code>/bg</code></li>
<li>監督プロセスが裏で面倒を見る方式（Q1から育って4月に確定）</li>
<li>単独だと「投げっぱなし」。下の2つとセットで初めて効く</li>
</ul>
</div>
<div class="cc-card pri">
<h4>Agent View<span class="tag">W20</span></h4>
<p class="sub">全セッションを1画面で監視</p>
<ul>
<li><code>claude agents</code>（スラッシュ無し）で起動</li>
<li>状態（作業中 / 入力待ち / 完了）を一覧表示</li>
<li>その場で dispatch・peek・attach/detach。並列の最大の苦痛を解消</li>
</ul>
</div>
<div class="cc-card pri">
<h4>/goal 自走ループ<span class="tag">W20</span></h4>
<p class="sub">完了条件を渡して放流する</p>
<ul>
<li><code>/goal &lt;完了条件&gt;</code> が満たされるまでターン跨ぎで継続</li>
<li>経過時間・ターン数・トークン数がライブ表示</li>
<li>「テストが全部通るまで」を条件にした夜間バッチ的開発の核</li>
</ul>
</div>
<div class="cc-card pri">
<h4>Monitor ツール<span class="tag">W15</span></h4>
<p class="sub">裏のイベントを会話に流し込む</p>
<ul>
<li>バックグラウンドのログ・プロセスをリアルタイム取り込み</li>
<li><code>--bg</code> の様子を <code>sleep</code> ポーリングせず拾える</li>
</ul>
</div>
</div>

<div class="cc-h">🔐 権限まわり — 「全許可」と「全確認」の間</div>
<div class="cc-grid">
<div class="cc-card em">
<h4>Auto Mode<span class="tag">W13</span></h4>
<p class="sub">安全は自動承認・危険はブロック</p>
<ul>
<li>権限モード <code>auto</code>（研究プレビュー）</li>
<li>分類モデル（Sonnet 4.6）が裏で判定</li>
<li>「全YOLO許可」の恐怖と「毎回Enter」の苦行の中間</li>
</ul>
</div>
<div class="cc-card em">
<h4>hard_deny / dontAsk<span class="tag">W19</span></h4>
<p class="sub">絶対に触らせない操作の保険</p>
<ul>
<li><code>autoMode.hard_deny</code> 配列で無条件ブロック</li>
<li><code>rm -rf</code>・本番DB書き込み等を機械的に止める</li>
<li>全部を事前許可リストでしか通さない <code>dontAsk</code> も別途</li>
</ul>
</div>
</div>

<div class="cc-h">⚡ 効かせどころ & クラウド往復</div>
<div class="cc-grid">
<div class="cc-card am">
<h4>Opus 4.7 + /effort<span class="tag">W16</span></h4>
<p class="sub">推論の出し入れ</p>
<ul>
<li>Max/Team Premium で Opus 4.7 が既定</li>
<li><code>/effort</code> がスライダー化、最上位 <code>xhigh</code> 追加</li>
<li><code>${CLAUDE_EFFORT}</code> で skill/bash から現在値が読める</li>
<li>難所だけ <code>xhigh</code>、定型は控えめ、と1セッション内で出し入れ</li>
</ul>
</div>
<div class="cc-card am">
<h4>Ultraplan + /loop<span class="tag">W15</span></h4>
<p class="sub">設計と実装の場所を分ける</p>
<ul>
<li><b>Ultraplan</b>: クラウドで計画下書き → Webでレビュー → 手元/リモートで実行</li>
<li><code>/loop &lt;間隔&gt;</code>: 定期タスク。間隔省略で自己ペース常駐</li>
</ul>
</div>
</div>

<div class="cc-h">🛠 プラグイン & 環境</div>
<div class="cc-grid">
<div class="cc-card pk">
<h4>公式マーケットプレイス<span class="tag">W19</span></h4>
<p class="sub">拡張は公式内で完結させる</p>
<ul>
<li><code>/plugin</code>（<b>単数</b>）で Discover タブ → <code>claude-plugins-official</code></li>
<li>5月時点で公式101本、コミュニティ含め1,000本超</li>
<li><code>.zip</code> アーカイブ・URL からの読み込みにも対応</li>
</ul>
</div>
<div class="cc-card pk">
<h4>環境まわり<span class="tag">W13–W19</span></h4>
<p class="sub">OS差・隔離の制御</p>
<ul>
<li><b>PowerShell ネイティブ</b>: Windows で Git Bash 必須でなくなった</li>
<li><b>Computer use in CLI</b>: GUI 操作で変更を検証（研究プレビュー）</li>
<li><code>worktree.bgIsolation</code>: 隔離 worktree か作業コピー直編集かを選択</li>
</ul>
</div>
</div>

<div class="cc-h">📋 コマンド早見表</div>
<table class="cc-cheat">
<tr><th>コマンド / 設定</th><th>用途</th><th>時期</th></tr>
<tr><td><code>claude --bg</code> / <code>/bg</code></td><td>バックグラウンドでタスクを走らせる</td><td>W15</td></tr>
<tr><td><code>claude agents</code></td><td>全セッションを1画面で監視・操作</td><td>W20</td></tr>
<tr><td><code>/goal &lt;条件&gt;</code></td><td>完了条件まで自走</td><td>W20</td></tr>
<tr><td><code>auto</code> モード</td><td>安全は自動承認・危険はブロック</td><td>W13</td></tr>
<tr><td><code>autoMode.hard_deny</code></td><td>無条件で蹴る固いルール</td><td>W19</td></tr>
<tr><td><code>/effort xhigh</code></td><td>推論を最大に効かせる</td><td>W16</td></tr>
<tr><td><code>/loop &lt;間隔&gt;</code></td><td>定期/常駐タスク</td><td>W15</td></tr>
<tr><td><code>/plugin</code></td><td>公式マーケットプレイス閲覧・導入</td><td>W19</td></tr>
<tr><td><code>worktree.bgIsolation</code></td><td>バックグラウンドの隔離方式を選択</td><td>W19</td></tr>
</table>

<div class="cc-flag">
<b>今が回し時</b>
<p><span class="big">+50%</span> — 週次上限が <b>5月13日</b> から <b>7月13日まで</b> 増量（Pro / Max / Team / シート制 Enterprise 対象、無料枠は対象外。SpaceX との計算資源契約が背景という報道）。<br><br><code style="background:rgba(255,255,255,.2);padding:2px 7px;border-radius:6px;">--bg</code> + <code style="background:rgba(255,255,255,.2);padding:2px 7px;border-radius:6px;">/goal</code> + <b>Auto Mode</b> が揃って「放流して自走させる」開発がやっと成立した時期に、上限が1.5倍。フル回転させるなら今。</p>
</div>

<div class="cc-src">
出典: Claude Code 公式 changelog / What's new（週次ダイジェスト, code.claude.com）、Anthropic Engineering（Auto Mode）、Claude Code Plugin Marketplace（anthropics/claude-plugins-official）、週次上限拡大の各報道。<br>
関連: <a href="../index.html">AIハブ トップ</a> ・ <a href="./2026-04-ai-kihon.html">受講資料 入門 #01</a> ・ <a href="../speaker.html">講師紹介</a>
</div>

</div>
