---
title: "CodexのWorktreeが3分でわかる：ローカル・Git・ブランチ・PR・デプロイの使い分け"
date: 2026-07-24
role: ブログ兼説明資料 / Codex・Git初心者向け
gen_by: 由井 辰美 / AI相談
summary: CodexのLocal、Worktree、sandbox、branch、stage、commit、push、pull request、deployの違いを、町のパン屋さんのたとえと実務フローでやさしく整理します。
audience: Gitの言葉が多く、Codexでどの作業場所を選べばよいか迷う地域事業者、講座受講者、非エンジニア
duration: 10分
goal: 作業の大きさと現在のGit状態から、LocalかWorktreeかを選び、公開までの現在地を説明できる
---

<style>
.codex-git-guide{--cg-blue:#2563eb;--cg-blue-soft:#eff6ff;--cg-green:#15803d;--cg-green-soft:#f0fdf4;--cg-orange:#c2410c;--cg-orange-soft:#fff7ed;--cg-purple:#7e22ce;--cg-purple-soft:#faf5ff;--cg-ink:#172033;--cg-soft:#475569;--cg-line:#cbd5e1;color:var(--cg-ink)}
.codex-git-guide *{box-sizing:border-box}
.codex-git-guide h2{margin-top:2.6rem}
.codex-git-guide h3{margin-top:2rem}
.codex-git-guide p,.codex-git-guide li{line-height:1.85}
.codex-git-guide .lead{font-size:1.12rem;color:var(--cg-soft)}
.codex-git-guide .conclusion{margin:1.4rem 0;padding:1.25rem 1.4rem;border-left:6px solid var(--cg-blue);background:var(--cg-blue-soft);border-radius:8px}
.codex-git-guide .conclusion strong{display:block;font-size:1.25rem;margin-bottom:.45rem}
.codex-git-guide .analogy-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:1.2rem 0 1.8rem}
.codex-git-guide .analogy-card{border:1px solid var(--cg-line);border-radius:10px;padding:1rem;background:#fff}
.codex-git-guide .analogy-card b{display:block;margin-bottom:.35rem}
.codex-git-guide .analogy-card span{color:var(--cg-soft);font-size:.94rem;line-height:1.7}
.codex-git-guide .flow{margin:1.4rem 0 1.8rem;padding:1rem;border:1px solid var(--cg-line);border-radius:12px;background:#f8fafc}
.codex-git-guide .flow-start{padding:.8rem 1rem;text-align:center;background:var(--cg-ink);color:#fff;border-radius:8px;font-weight:700}
.codex-git-guide .flow-choice{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
.codex-git-guide .flow-lane{padding:1rem;border:2px solid var(--cg-blue);border-radius:10px;background:#fff}
.codex-git-guide .flow-lane.worktree{border-color:var(--cg-purple)}
.codex-git-guide .flow-lane b{display:block;font-size:1.05rem;margin-bottom:.3rem}
.codex-git-guide .flow-lane span{color:var(--cg-soft);font-size:.92rem;line-height:1.65}
.codex-git-guide .flow-arrow{text-align:center;font-size:1.4rem;color:var(--cg-soft);line-height:1}
.codex-git-guide .flow-steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:12px}
.codex-git-guide .flow-step{min-height:108px;padding:.85rem;border:1px solid var(--cg-line);border-radius:9px;background:#fff}
.codex-git-guide .flow-step b{display:block;margin-bottom:.25rem}
.codex-git-guide .flow-step span{font-size:.88rem;line-height:1.55;color:var(--cg-soft)}
.codex-git-guide .flow-step.public{border-color:var(--cg-green);background:var(--cg-green-soft)}
.codex-git-guide table{width:100%;border-collapse:collapse;margin:1rem 0 1.8rem;font-size:.94rem}
.codex-git-guide th{padding:.75rem;text-align:left;background:var(--cg-ink);color:#fff}
.codex-git-guide td{padding:.75rem;border-bottom:1px solid var(--cg-line);vertical-align:top;line-height:1.7}
.codex-git-guide td:first-child{font-weight:700;white-space:nowrap}
.codex-git-guide .decision{margin:1rem 0 1.8rem;padding:1.1rem 1.3rem;background:var(--cg-orange-soft);border:1px solid #fdba74;border-radius:10px}
.codex-git-guide .case{margin:1rem 0;padding:1rem 1.15rem;border:1px solid var(--cg-line);border-radius:10px;background:#fff}
.codex-git-guide .case b{color:var(--cg-blue)}
.codex-git-guide pre{padding:1rem 1.1rem;overflow:auto;border-radius:10px;background:#0f172a;color:#e2e8f0;line-height:1.7}
.codex-git-guide .state-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:1rem 0 1.8rem}
.codex-git-guide .state{padding:1rem;border-radius:10px;border:1px solid var(--cg-line);background:#fff}
.codex-git-guide .state b{display:block;margin-bottom:.3rem}
.codex-git-guide .state.local{border-top:5px solid var(--cg-orange)}
.codex-git-guide .state.preview{border-top:5px solid var(--cg-purple)}
.codex-git-guide .state.production{border-top:5px solid var(--cg-green)}
.codex-git-guide .prompt{white-space:pre-wrap}
.codex-git-guide .one-minute{margin:1rem 0 1.8rem;padding:1.2rem 1.3rem;border:2px dashed var(--cg-blue);border-radius:10px;background:#fff}
@media(max-width:780px){
  .codex-git-guide .analogy-grid,.codex-git-guide .state-list{grid-template-columns:1fr}
  .codex-git-guide .flow-choice{grid-template-columns:1fr}
  .codex-git-guide .flow-steps{grid-template-columns:1fr 1fr}
  .codex-git-guide td:first-child{white-space:normal}
}
@media(max-width:480px){.codex-git-guide .flow-steps{grid-template-columns:1fr}}
</style>

<div class="codex-git-guide" markdown="1">

「LocalとWorktreeは何が違うの？」「ブランチを作ったら保存されたの？」「コミットしたら公開されたの？」。

Codexで仕事を始めると、似た言葉が一度に出てきます。難しいのは操作より、**それぞれが何を分けているのか**です。

このページでは、町のパン屋さんにたとえて、作業開始から本番公開までを一本につなげます。

<div class="conclusion">
<strong>最初に覚えるのは「場所・安全・記録・相談・公開」の5つだけ</strong>
Local / Worktreeは作業場所、sandboxは安全柵、Gitは記録、Pull Requestは公開前の相談、Deployはお客様に見せる公開作業です。
</div>

## まず、町のパン屋さんで考える

新しいパンを作る仕事で考えてみます。

<div class="analogy-grid">
  <div class="analogy-card"><b>Local＝いつもの厨房</b><span>普段使っているプロジェクトフォルダを、そのまま編集します。</span></div>
  <div class="analogy-card"><b>Worktree＝別に借りた試作厨房</b><span>同じ店の材料とレシピを使いながら、別案を邪魔せず作れます。</span></div>
  <div class="analogy-card"><b>Sandbox＝厨房の安全柵</b><span>入ってよい場所、触ってよい道具、外へ出てよい範囲を決めます。</span></div>
  <div class="analogy-card"><b>Branch＝「夏の新作」札</b><span>どの改善案を進めているか分かる名前を付けます。</span></div>
  <div class="analogy-card"><b>Commit＝日付入りの試作記録</b><span>その時点の変更を、説明つきで後から戻れる形に残します。</span></div>
  <div class="analogy-card"><b>Pull Request＝試食会</b><span>公式メニューへ入れる前に、変更点を見せて相談・確認します。</span></div>
</div>

最後に、採用したレシピを本店のメニューへ入れるのが**Merge**、実際に店頭へ並べるのが**Deploy**です。

つまり、コミットしても、プッシュしても、Pull Requestを作っても、まだお客様には見えていません。

## 利用図：Codexの作業開始から本番公開まで

<div class="flow" role="img" aria-label="CodexでLocalまたはWorktreeを選び、sandboxの中で作業し、branch、commit、push、pull request、merge、deploy、本番確認へ進む流れ">
  <div class="flow-start">依頼する前に、作業の大きさと今のGit状態を見る</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-choice">
    <div class="flow-lane">
      <b>Localを選ぶ</b>
      <span>小さな変更・作業中の変更がない・いつもの環境ですぐ確認したい</span>
    </div>
    <div class="flow-lane worktree">
      <b>Worktreeを選ぶ</b>
      <span>大きな変更・別案・並行作業・Localに未コミット変更がある</span>
    </div>
  </div>
  <div class="flow-arrow">↓ どちらもPC内で動き、sandboxの安全範囲がかかる ↓</div>
  <div class="flow-steps">
    <div class="flow-step"><b>1. Branch</b><span>この変更専用の名前札</span></div>
    <div class="flow-step"><b>2. 編集・テスト</b><span>ファイルを直し、ローカル画面で確認</span></div>
    <div class="flow-step"><b>3. Stage</b><span>今回の記録へ入れる変更だけ選ぶ</span></div>
    <div class="flow-step"><b>4. Commit</b><span>説明つきの復元地点を作る</span></div>
    <div class="flow-step"><b>5. Push</b><span>BranchとCommitをGitHubへ送る</span></div>
    <div class="flow-step"><b>6. Pull Request</b><span>変更を見せ、相談・レビューする</span></div>
    <div class="flow-step"><b>7. Merge</b><span>確認済みの変更をmainへ合流</span></div>
    <div class="flow-step public"><b>8. Deploy・本番確認</b><span>公開し、本番URLで結果を確かめる</span></div>
  </div>
</div>

この図の重要点は、**LocalとWorktreeは最初に選ぶ作業場所で、その後のGitの流れは同じ**ということです。

## 似ている言葉を、何を分ける機能かで整理する

| 用語 | 何を分ける？ | やさしい意味 | これだけでは起きないこと |
|---|---|---|---|
| Local | 作業場所 | いつものプロジェクトフォルダ | 自動では保存・公開されない |
| Worktree | 作業場所 | 同じGitリポジトリから作る別の作業場 | バックアップや公開にはならない |
| Sandbox | 権限・安全範囲 | Codexが触ってよい場所の柵 | コードの間違いまでは防げない |
| Branch | 変更の系列 | 1つの改善案につける名前 | ファイルのコピー場所そのものではない |
| Stage | 次の記録範囲 | コミットへ入れる変更を選ぶ | まだ履歴には残らない |
| Commit | 履歴 | 説明つきの保存地点 | GitHubにも本番にも自動では届かない |
| Push | 送信 | ローカルの履歴をGitHubへ送る | mainへの採用や本番公開ではない |
| Pull Request | 相談・レビュー | この変更をmainへ入れてよいか確認する場 | 作っただけでは採用されない |
| Merge | 採用 | 変更をmainへ合流する | デプロイ設定がなければ公開されない |
| Deploy | 公開反映 | 実行環境やWebへ成果物を置く | 正しく表示された保証にはならない |
| 本番確認 | 完了確認 | 実際のURL・画面・APIで確かめる | ここを飛ばすと「公開したつもり」になる |

## 一番混同しやすい4組

### 1. LocalとSandboxは別

Localは「どのフォルダで作業するか」です。Sandboxは「その作業中にどこまで触ってよいか」です。

LocalでもWorktreeでも、Sandboxは使われます。たとえば「このプロジェクト内は編集できるが、別事業のフォルダや外部ネットワークは確認が必要」という安全枠を作れます。

### 2. WorktreeとBranchは別

Worktreeは**実際の別フォルダ**です。Branchは**変更履歴につける名前**です。

Codexが作るWorktreeは、最初はBranchへつながっていない `detached HEAD` の状態になることがあります。作業を残してPushやPull Requestへ進むなら、Codex画面の「Create branch here」などでBranchを作ります。

同じBranchをLocalとWorktreeの両方で同時に開くことはできません。Gitが「どちらの作業場が正しいBranchなのか」を決められなくなるためです。

### 3. CommitとPushは別

Commitは自分のPC内の履歴です。Pushは、その履歴をGitHubへ送る操作です。

たとえるなら、Commitは厨房の試作ノートへ記録すること。Pushは、そのノートの写しを本部へ送ることです。

### 4. MergeとDeployは別

MergeはGitの履歴をmainへ採用すること。Deployは採用した成果物を実際のWeb環境へ置くことです。

VercelなどとGitHubを連携している場合は、mainへのMergeをきっかけに自動Deployされます。ただし、処理の失敗や古いキャッシュもあるため、最後は本番URLで確認します。

## LocalかWorktreeか、5問で決める

<div class="decision">
<ol>
  <li>Gitリポジトリですか？ <strong>いいえ → Local。</strong> WorktreeはGitがないと使えません。</li>
  <li>Localに未コミットの変更がありますか？ <strong>はい → Worktree。</strong> 別の仕事を混ぜないようにします。</li>
  <li>同時に別の変更を進めますか？ <strong>はい → Worktree。</strong></li>
  <li>変更が1ファイル程度で、すぐ戻せますか？ <strong>はい → Localでも十分。</strong></li>
  <li>いつもの開発サーバーやPC固有の設定でしか確認できませんか？ <strong>はい → Local、またはWorktreeからLocalへHandoff。</strong></li>
</ol>
</div>

迷った時の標準は、**小さくてきれいな作業場ならLocal、混ざりそうならWorktree**です。

## 状態表示は「ローカル・プレビュー・本番」の3つに分ける

<div class="state-list">
  <div class="state local"><b>ローカル</b>自分のPCだけ。例：<code>http://localhost:3000</code></div>
  <div class="state preview"><b>プレビュー</b>確認用URL。関係者に見せられるが、本番とは別。</div>
  <div class="state production"><b>本番</b>利用者が使う正式URL。実際に開いて確認して初めて完了。</div>
</div>

「ビルド成功」「コミット済み」「Push済み」「プレビュー確認済み」は、すべて本番確認前の状態です。

完了報告では、次のように言い分けます。

- ローカル：ビルドと画面確認まで完了
- プレビュー：Pull Requestの確認用URLで動作確認済み
- 本番：Merge・Deploy後、正式URLで画面と主要機能を確認済み

## 実例1：案内文の誤字を1か所直す

<div class="case">
<b>おすすめ：Local</b>

Localがきれいで、対象ファイルが1つなら、いつものフォルダで直します。差分を確認し、必要なテストをしてCommitします。チーム運用ならPushとPull Requestへ進みます。
</div>

Localに別作業の未コミット変更があるなら、誤字修正でもWorktreeへ分けたほうが安全です。変更の大きさだけでなく、**今の作業場がきれいか**で判断します。

## 実例2：トップページを別案で作り直す

<div class="case">
<b>おすすめ：Worktree</b>

本線を壊さず、専用Worktreeと専用Branchで進めます。ローカル表示、PC幅、スマホ幅、リンク、フォームを確認してからPushします。Pull RequestのプレビューURLを関係者へ見せ、採用後にMergeします。
</div>

別案が不採用でも、いつものLocalはそのままです。これがWorktreeの大きな利点です。

## 実例3：AI相談の資料を追加する

このAI相談サイトでは、GitHubの `main` とVercel本番がつながっています。資料追加の安全な流れは次の通りです。

<pre><code>最新の origin/main
  ↓
資料追加専用 Worktree
  ↓
codex/add-codex-worktree-guide Branch
  ↓
content/blog に原稿を追加
  ↓
ローカルビルド・リンク・PC/スマホ確認
  ↓
Commit → Push → Pull Request
  ↓
Preview URLで確認
  ↓ CEO承認
Merge
  ↓
VercelへProduction Deploy
  ↓
https://ai-hub-jp.vercel.app の対象ページを確認</code></pre>

ここで大切なのは、Pull Requestを作った時点では「公開候補」、Preview URLは「確認用」、本番URLを確認して初めて「公開完了」と言うことです。

## Codex画面での基本操作

### Worktreeで始める

1. 新しいCodexタスクを作る
2. 入力欄の下で **Worktree** を選ぶ
3. 開始元のBranchを選ぶ。通常は最新の `main`
4. 作業を依頼する
5. 残す変更なら **Create branch here** でBranchを作る
6. 差分とテスト結果を確認する
7. Commit、Push、Pull Requestへ進む

いつものIDEや開発サーバーで確認したい時は、**Hand off** でWorktreeからLocalへ移します。

### Localで始める

1. 最初に `git status` で作業中の変更を確認する
2. 今回の変更と混ざらないことを確かめる
3. 必要なら専用Branchを作る
4. 小さく変更し、差分・テスト・画面を確認する
5. Stage、Commit、Push、Pull Requestへ進む

## コマンドで見るとこうなる

Codex画面だけでも操作できます。裏側を知りたい人向けの最小例です。

```powershell
# 今の状態を見る
git status

# 最新のmainを開始点に、別の作業場とBranchを作る
git fetch origin main
git worktree add -b codex/new-guide C:\tmp\new-guide origin/main

# 今回の変更だけ選び、履歴に残す
git add content/blog/new-guide.md
git commit -m "docs: add Codex worktree guide"

# GitHubへ送り、Pull Requestを作る
git push -u origin codex/new-guide
gh pr create
```

Deployの方法はプロジェクトごとに違います。GitHubとVercelが連携していれば、BranchのPushでPreview、mainへのMergeでProduction Deployとなる構成が一般的です。

## そのまま使えるCodex依頼文

### 安全な作業場所を選ばせる

<pre class="prompt"><code>このリポジトリのGit状態を最初に確認してください。
今回の作業と関係ない未コミット変更がある場合は、触らずに、
最新のorigin/mainを開始点とする専用Worktreeと専用Branchで進めてください。

完了時は次を分けて報告してください。
1. ローカルで確認したこと
2. プレビューで確認したこと
3. 本番で確認したこと

Commit、Push、Pull Request、Deployは同じ意味として扱わないでください。
外部公開や本番変更の前には確認を求めてください。</code></pre>

### Pull Requestまで頼む

<pre class="prompt"><code>この変更を専用Branchで実装し、差分、テスト、PC幅、スマホ幅を確認してください。
関係ない変更は含めないでください。
確認後にCommitとPushを行い、変更内容と確認方法が分かるPull Requestを作ってください。
本番へのMergeとDeployはまだ行わないでください。</code></pre>

### 本番公開まで頼む

<pre class="prompt"><code>承認済みのPull Requestを本番へ反映してください。
Merge、Deploy、正式な本番URLでの確認まで進めてください。
完了報告には、推測ではない本番URL、確認したページまたはAPI、
未完了があれば理由と次の1手を書いてください。</code></pre>

## よくある勘違い

| 勘違い | 正しくは |
|---|---|
| Worktreeなら絶対安全 | 作業は分かれるが、削除や外部操作の安全はSandbox・権限・確認が担当 |
| Branchを作れば保存完了 | Commitして初めて履歴になる |
| CommitすればGitHubにある | Pushするまでは基本的に自分のPC内 |
| Pushすれば本番に出る | Branch設定やCI/CD構成による |
| Pull Requestを作れば採用済み | まだ提案・確認中 |
| Previewが動けば公開完了 | 本番URLは別。Merge後のProductionを確認する |
| Deploy成功なら確認不要 | 正しいページ、データ、権限、表示を本番で確かめる |
| Sandboxがあるから内容も正しい | Sandboxは行動範囲の柵。内容の品質は差分・テスト・人の確認が必要 |

## 人に説明する60秒台本

<div class="one-minute">
CodexのLocalは「いつもの厨房」、Worktreeは「別の試作厨房」です。Sandboxは、どちらの厨房でもCodexが触ってよい範囲を決める安全柵です。Branchは新作につける名前札、Commitは日付入りの試作記録、Pushは記録をGitHubへ送ることです。Pull Requestは本店へ採用する前の試食会、Mergeは公式レシピへの採用、Deployは実際に店頭へ並べることです。だから、CommitやPull Requestではまだ公開されていません。最後に本番URLを開いて確認して、初めて完了です。
</div>

## 最低限の確認リスト

- [ ] 今のLocalに、別作業の未コミット変更がないか見た
- [ ] 小さな作業はLocal、混ざりそうな作業はWorktreeにした
- [ ] 今回専用のBranch名を付けた
- [ ] Stageへ関係ない変更を入れていない
- [ ] Commitメッセージで「何を変えたか」が分かる
- [ ] Push、Pull Request、Merge、Deployを別々に確認した
- [ ] ローカル・プレビュー・本番を言い分けた
- [ ] 本番では正式URLと主要機能を実際に確認した
- [ ] 公開・課金・DB変更・外部送信は承認後に行った

## 公式情報

- [Codex Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Codex Sandbox](https://learn.chatgpt.com/docs/sandboxing)
- [Codex environments](https://learn.chatgpt.com/docs/environments/modes)
- [Git worktree公式ドキュメント](https://git-scm.com/docs/git-worktree)
- [GitHub: Pull Requestとは](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
- [Vercel: Preview Deploymentの共有](https://vercel.com/docs/deployments/sharing-deployments)

</div>
