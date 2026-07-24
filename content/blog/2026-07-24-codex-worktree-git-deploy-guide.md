---
title: "CodexのWorktree入門：いつもの場所と別の場所"
date: 2026-07-24
role: ブログ兼説明資料 / Codex・Git初心者向け
gen_by: 由井 辰美 / AI相談
summary: CodexのLocal、Worktree、Git、Pull Request、Deployの役割を、町のパン屋さんにたとえて簡単に説明します。
image: /img/blog-codex-worktree-guide-hero-labels-v2-20260724.webp
audience: Codexを使いたいが、Gitの言葉が難しいと感じる地域事業者、講座受講者、非エンジニア
duration: 5分
goal: LocalとWorktreeを使い分け、作業中・確認中・公開済みの違いを説明できる
---

<style>
.simple-codex-guide{--sc-blue:#2563eb;--sc-teal:#0f8f8a;--sc-green:#4f8f27;--sc-orange:#d97706;--sc-purple:#7c3aed;--sc-ink:#172033;--sc-soft:#526071;--sc-line:#dbe4ed;color:var(--sc-ink)}
.simple-codex-guide *{box-sizing:border-box}
.simple-codex-guide h2{margin-top:2.8rem}
.simple-codex-guide h3{margin-top:2rem}
.simple-codex-guide p,.simple-codex-guide li{line-height:1.85}
.simple-codex-guide .guide-figure{width:min(100%,960px);margin:1rem auto 2rem}
.simple-codex-guide .guide-figure img{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;border:1px solid var(--sc-line);border-radius:18px;background:#f7fbff;box-shadow:0 14px 36px rgba(23,32,51,.1)}
.simple-codex-guide .guide-figure figcaption{margin:.7rem auto 0;color:var(--sc-soft);font-size:.9rem;line-height:1.65;text-align:center}
.simple-codex-guide .guide-hero{margin-top:0}
.simple-codex-guide .first-message{margin:1.4rem 0;padding:1.25rem 1.4rem;border-left:6px solid var(--sc-blue);background:#eff6ff;border-radius:10px}
.simple-codex-guide .first-message strong{display:block;font-size:1.25rem;margin-bottom:.45rem}
.simple-codex-guide .role-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:1.2rem 0 1.8rem}
.simple-codex-guide .role-card{padding:1rem;border:1px solid var(--sc-line);border-radius:12px;background:#fff}
.simple-codex-guide .role-card b{display:block;margin-bottom:.35rem;color:var(--sc-blue)}
.simple-codex-guide .role-card span{display:block;color:var(--sc-soft);font-size:.92rem;line-height:1.65}
.simple-codex-guide .choice-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:1.2rem 0 1.8rem}
.simple-codex-guide .choice-card{padding:1.2rem;border:2px solid var(--sc-blue);border-radius:14px;background:#fff}
.simple-codex-guide .choice-card.worktree{border-color:var(--sc-teal)}
.simple-codex-guide .choice-card b{display:block;font-size:1.12rem;margin-bottom:.5rem}
.simple-codex-guide .choice-card ul{margin:.5rem 0 0;padding-left:1.25rem}
.simple-codex-guide .rule{margin:1rem 0 1.8rem;padding:1rem 1.2rem;border-radius:12px;background:#fff7ed;border:1px solid #fdba74}
.simple-codex-guide .journey{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:1.2rem 0 1.8rem}
.simple-codex-guide .journey-step{padding:1rem .8rem;border:1px solid var(--sc-line);border-radius:12px;background:#fff;text-align:center}
.simple-codex-guide .journey-step b{display:block;margin-bottom:.35rem}
.simple-codex-guide .journey-step span{font-size:.88rem;line-height:1.55;color:var(--sc-soft)}
.simple-codex-guide .state-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:1rem 0 1.8rem}
.simple-codex-guide .state{padding:1rem;border-radius:12px;border:1px solid var(--sc-line);background:#fff}
.simple-codex-guide .state b{display:block;margin-bottom:.3rem}
.simple-codex-guide .state.local{border-top:5px solid var(--sc-orange)}
.simple-codex-guide .state.preview{border-top:5px solid var(--sc-purple)}
.simple-codex-guide .state.production{border-top:5px solid var(--sc-green)}
.simple-codex-guide .one-minute{margin:1rem 0 1.8rem;padding:1.2rem 1.3rem;border:2px dashed var(--sc-blue);border-radius:12px;background:#fff}
@media(max-width:800px){
  .simple-codex-guide .role-grid{grid-template-columns:1fr 1fr}
  .simple-codex-guide .journey{grid-template-columns:1fr 1fr}
}
@media(max-width:560px){
  .simple-codex-guide .role-grid,.simple-codex-guide .choice-grid,.simple-codex-guide .journey,.simple-codex-guide .state-list{grid-template-columns:1fr}
}
</style>

<div class="simple-codex-guide" markdown="1">

<figure class="guide-figure guide-hero">
  <img src="/img/blog-codex-worktree-guide-hero-labels-v2-20260724.webp" alt="作業する、記録する、相談する、公開するというCodexの仕事の流れ" loading="eager" decoding="async">
  <figcaption>Codexの仕事は、作る、記録する、相談する、公開する、という順番です。</figcaption>
</figure>

Codexを使うと、Local、Worktree、Commit、Pull Requestなど、似た言葉がたくさん出てきます。

全部を一度に覚える必要はありません。まずは、**どこで作るか、どう記録するか、いつ公開されるか**だけ分かれば十分です。

<div class="first-message">
<strong>最初に覚えるのは5つだけ</strong>
作業場所、安全柵、記録、相談、公開。この5つに分けると、Gitの言葉が整理できます。
</div>

## まず、5つの役割だけ覚える

<figure class="guide-figure">
  <img src="/img/blog-codex-worktree-guide-spaces-labels-v2-20260724.webp" alt="Localはいつもの場所、Worktreeは別の場所、Sandboxは安全柵という説明図" loading="lazy" decoding="async">
  <figcaption>LocalとWorktreeは作業場所、SandboxはCodexが触ってよい範囲を決める安全柵です。</figcaption>
</figure>

町のパン屋さんで考えると、役割は次の5つです。

<div class="role-grid">
  <div class="role-card"><b>作業場所</b><span>LocalまたはWorktreeで作ります。</span></div>
  <div class="role-card"><b>安全柵</b><span>Sandboxが触ってよい範囲を守ります。</span></div>
  <div class="role-card"><b>記録</b><span>Commitで変更を残します。</span></div>
  <div class="role-card"><b>相談</b><span>Pull Requestで変更を見せます。</span></div>
  <div class="role-card"><b>公開</b><span>MergeとDeployで本番へ出します。</span></div>
</div>

パン屋さんにたとえると、Localは**いつもの厨房**、Worktreeは**別に借りた試作厨房**です。

Commitは試作ノートへの記録、Pull Requestは試食会、Deployは店頭へ並べる作業です。

大切なのは、**Commitしただけでは公開されない**ということです。

## LocalとWorktreeは、こう選ぶ

<figure class="guide-figure">
  <img src="/img/blog-codex-worktree-guide-choose-labels-v2-20260724.webp" alt="小さな修正はLocal、別案や並行作業はWorktreeを選ぶ説明図" loading="lazy" decoding="async">
  <figcaption>小さく単独の修正ならLocal、別案や他の仕事と混ざりそうならWorktreeが安心です。</figcaption>
</figure>

<div class="choice-grid">
  <div class="choice-card">
    <b>Localが向いている時</b>
    <ul>
      <li>誤字やリンクを1か所直す</li>
      <li>今の作業場に別の変更がない</li>
      <li>いつもの環境ですぐ確認したい</li>
    </ul>
  </div>
  <div class="choice-card worktree">
    <b>Worktreeが向いている時</b>
    <ul>
      <li>トップページを別案で作る</li>
      <li>ほかの作業も同時に進んでいる</li>
      <li>今の作業場に未保存の変更がある</li>
    </ul>
  </div>
</div>

<div class="rule">
<strong>迷った時の決め方：</strong>小さく、ほかの仕事と混ざらないならLocal。少しでも混ざりそうならWorktree。
</div>

Branchは、作業につける**名前札**です。Worktreeという別の作業場に「トップページ改善」などの名前札をつける、と考えると分かりやすくなります。

## 公開までは、この順番

<figure class="guide-figure">
  <img src="/img/blog-codex-worktree-guide-flow-labels-v2-20260724.webp" alt="作る、選ぶ、記録、送る、公開という作業の流れ" loading="lazy" decoding="async">
  <figcaption>難しい操作名より、今どの段階にいるかを意識することが大切です。</figcaption>
</figure>

<div class="journey">
  <div class="journey-step"><b>1. 作る</b><span>LocalかWorktreeで変更します。</span></div>
  <div class="journey-step"><b>2. 選ぶ</b><span>今回残す変更だけ選びます。</span></div>
  <div class="journey-step"><b>3. 記録</b><span>Commitで履歴に残します。</span></div>
  <div class="journey-step"><b>4. 送る</b><span>GitHubへ送り、Pull Requestで確認します。</span></div>
  <div class="journey-step"><b>5. 公開</b><span>Merge、Deploy、本番確認まで進めます。</span></div>
</div>

完了した場所は、次の3つに分けて伝えます。

<div class="state-list">
  <div class="state local"><b>ローカル</b>自分のPCで確認できた状態。</div>
  <div class="state preview"><b>プレビュー</b>関係者が確認できる公開前の状態。</div>
  <div class="state production"><b>本番</b>正式URLで利用者が見られる状態。</div>
</div>

CommitやPull Requestは、まだ公開途中です。Deployが終わり、**正式な本番URLを実際に開いて確認した時点**で公開完了です。

### 人に説明するなら

<div class="one-minute">
Localはいつもの作業場所、Worktreeは別の作業場所です。Sandboxは安全柵、Commitは記録、Pull Requestは公開前の相談です。MergeとDeployで本番へ出し、正式URLを確認して完了です。
</div>

### 最後に確認すること

- 今の作業はLocalとWorktreeのどちらが安全か
- Commit、Pull Request、公開を同じ意味にしていないか
- 今はローカル、プレビュー、本番のどこにいるか
- 本番URLを実際に開いて確認したか

</div>
