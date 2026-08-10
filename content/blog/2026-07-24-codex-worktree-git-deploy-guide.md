---
title: "Codexで安全に直して公開する：Worktree・Git・PRの役割"
date: 2026-07-24
authorship_note: "※この記事は、運営者が自ら考えた内容を、AIを使って読みやすく整えた記事です。"
role: ブログ兼説明資料 / Codex・Git初心者向け
gen_by: 由井 辰美 / AI相談
summary: Codexでサイトを直して公開するまでを、作業場所・記録・確認・公開の4段階に分けてやさしく説明します。
image: /img/blog-codex-guide-roles-explainer-v2-20260725.webp
audience: Codexを使いたいが、Gitの言葉が難しいと感じる地域事業者、講座受講者、非エンジニア
duration: 4分
goal: LocalとWorktreeを選び、Commit、Pull Request、Deployの違いを説明できる
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
.simple-codex-guide .role-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:1.2rem 0 1.8rem}
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
  <img src="/img/blog-codex-guide-roles-explainer-v2-20260725.webp" alt="Worktreeは作業を分ける、Commitは変更を保存する、Pull Requestは公開前に確認する、Deployは本番へ反映するという役割の図解" loading="eager" decoding="async">
  <figcaption>4つの用語を「何をするものか」で分けた図です。</figcaption>
</figure>

Codexでサイトを直す時、言葉の多さに戸惑うことがあります。

でも、最初から全部を覚える必要はありません。大切なのは、**作業する場所を選び、変更を記録し、確認してから公開すること**です。

<div class="first-message">
<strong>結論：Worktreeは、今の作業を守りながら別の修正をする場所です。</strong>
Gitは変更を記録し、Pull Requestは公開前に確認し、Deployで利用者に届けます。
</div>

## まず、全体の流れを見る

<figure class="guide-figure">
  <img src="/img/blog-codex-guide-flow-explainer-v2-20260725.webp" alt="Worktreeで作業を分け、サイトを直し、Commitで変更を残し、Pull Requestで確認し、Deployで本番へ出す5段階の図解" loading="lazy" decoding="async">
  <figcaption>作業を分けてから本番へ出すまでを、5つの行動で確認できます。</figcaption>
</figure>

役割は、次のように分けると簡単です。

<div class="role-grid">
  <div class="role-card"><b>Local・Worktree</b><span>どこで作業するかを決めます。</span></div>
  <div class="role-card"><b>Branch・Commit</b><span>何を直したか、記録を残します。</span></div>
  <div class="role-card"><b>Pull Request</b><span>公開する前に変更内容を確認します。</span></div>
  <div class="role-card"><b>Merge・Deploy</b><span>確認した変更を本番へ届けます。</span></div>
</div>

Sandboxは、Codexが触ってよい範囲を決める**安全のための枠**です。作業場所そのものではありません。

## LocalとWorktreeは、こう選ぶ

<figure class="guide-figure">
  <img src="/img/blog-codex-guide-local-worktree-explainer-v2-20260725.webp" alt="Localは今の作業場所で小さな修正向け、Worktreeは別の作業場所で並行作業や今の変更を守る時に使うという比較図" loading="lazy" decoding="async">
  <figcaption>ほかの作業と混ざりそうなら、Worktreeを選びます。</figcaption>
</figure>

<div class="choice-grid">
  <div class="choice-card">
    <b>Localでよい時</b>
    <ul>
      <li>誤字やリンクを1か所直す</li>
      <li>ほかの作業をしていない</li>
      <li>今ある変更と混ざる心配がない</li>
    </ul>
  </div>
  <div class="choice-card worktree">
    <b>Worktreeが安心な時</b>
    <ul>
      <li>別の案を試したい</li>
      <li>ほかの修正も同時に進んでいる</li>
      <li>今の作業をそのまま残したい</li>
    </ul>
  </div>
</div>

<div class="rule">
<strong>迷った時：</strong>ほかの作業と混ざらないならLocal。混ざりそうならWorktree。
</div>

Branchは、分けた作業につける**名前**です。Commitは、その作業の**保存記録**です。

## 公開は、本番URLを確認して完了

<figure class="guide-figure">
  <img src="/img/blog-codex-guide-release-explainer-v2-20260725.webp" alt="ローカルは自分のPCだけ、プレビューは関係者が確認、本番は利用者に公開される状態で、本番URLを開いて完了という図解" loading="lazy" decoding="async">
  <figcaption>本番URLを実際に開き、利用者向けの表示を確認して完了です。</figcaption>
</figure>

作業の状態は、3つに分けて伝えます。

<div class="state-list">
  <div class="state local"><b>ローカル</b>自分のPCで確認できた状態。</div>
  <div class="state preview"><b>プレビュー</b>関係者が確認できる公開前の状態。</div>
  <div class="state production"><b>本番</b>正式URLで利用者が見られる状態。</div>
</div>

Commitは記録、Pull Requestは公開前の確認です。どちらも、まだ本番公開ではありません。

Pull RequestをMergeし、Deployが終わり、**正式な本番URLを実際に開いて確認した時点**で完了です。

<div class="one-minute">
<strong>ひとことで説明すると：</strong><br>
Worktreeは作業を分ける場所、Gitは変更の記録、Pull Requestは公開前の確認、Deployは本番公開です。
</div>

最後に、次の3つだけ確認してください。

- ほかの作業と混ざりそうなら、Worktreeを使ったか
- Pull Requestで、公開する変更を確認したか
- 本番URLを開き、表示を確認したか

</div>
