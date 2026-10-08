---
title: "自動化できていなかったのは、開発環境だった｜Codex CloudとSSDの話"
date: 2026-10-05
updated: 2026-10-08
authorship_note: "※内容は運営者が考え、AIで整えています。"
role: ブログ / Codex・開発環境
gen_by: 由井辰美 / AI相談
summary: "GitHubとCodex Cloudで自由になり、買ったSSDを売ろうとした私が、結局2TBを増設すると決めた理由。並行作業の見渡しやすさと、手元に残す安心の話です。"
image: /img/blog-cloud-ssd-hero-20261005.webp
status: published
---

<figure>
<img class="cloud-ssd-hero" src="/img/blog-cloud-ssd-hero-20261005.webp" alt="PCの部品と、スマホから頼めるクラウドの仕事場" width="1672" height="941" decoding="async">
<figcaption>PCへの依存を減らす。そのつもりが、話には続きがあった。挿絵は説明用のイメージです。</figcaption>
</figure>

コードを書く時間は減った。なのに、開発の準備やPCの世話は減らない。

Codexを使い始めて、開発速度は一気に上がった。コード、修正、テスト、Gitへのコミット。かなりAIに任せられる。

「開発、かなり自動化できたな」

そう思っていた。SSDが足りなくなるまでは。

## AIを使いながら、熱伝導パッドを調べていた {#hardware}

<figure>
<img src="/img/blog-cloud-ssd-hardware-20261005.webp" alt="SSD、ヒートシンク、熱伝導パッドを比較する手元" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>AIがコードを書く横で、人間は部品を調べていた。</figcaption>
</figure>

足りないなら、増やせばいい。2TBのSSDを探したが、思ったより高い。

「Gen3？ Gen4？」「2枚使える？」「発熱は？」「ヒートシンクは？」

気づけば、開発を自動化しているはずの人間が、**熱伝導パッドの厚みを調べていた。**

外出先でも開発したくて、HOME PCを常時起動し、iPhoneからリモート接続する環境も作った。でも、離れられるのはPCの前だけ。電源、スリープ、自宅回線、Windows Updateの世話は残る。

最新のAIを働かせるために、人間がPCを寝かせない。結局、PCを介護している。

## PCを経由しなければ、もっと自由になれる {#cloud}

<figure>
<img src="/img/blog-cloud-ssd-cloud-20261005.webp" alt="自宅PCへのリモート接続と、スマホから直接クラウドへ頼む方法" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>席から離れることと、手元のPCが眠っていても仕事が進むことは違う。</figcaption>
</figure>

そこでCodex Cloudを試した。

> iPhone → リモート → HOME PC → Codex → GitHub<br>
> これを、iPhone → Codex Cloud → GitHubへ。

[手元のPCがスリープ中でも、クラウドの仕事は進む](https://learn.chatgpt.com/docs/cloud)。独立した仕事なら、バグ修正、新機能、調査を別々に頼み、自分は次の仕事へ移れる。戻ってから結果を確認し、変更を合わせる。

すべての処理が何倍も速くなるわけではない。**人間が待たなくていい時間が増える。** 私にとっては、そちらが大きかった。

## GitHubに置くのは、コードと「仕事場の作り方」 {#github}

<figure>
<img src="/img/blog-cloud-ssd-github-20261005.webp" alt="原本のコードとセットアップ手順から、別のPCとクラウドに仕事場を再現する図" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>一台のPCに閉じ込めず、仕事場を作り直せるようにする。</figcaption>
</figure>

コードに加え、道具のバージョンやセットアップ手順もGitHubに置く。対応する別のPCやクラウドで、それを取得して環境を作り直す。

**GitHubを経由して、開発環境のコピーや移動も自動化できる。** パスワードやAPIキーはGitHubに入れず、移動先で別に設定する。

Codex Cloudも、[準備した環境からタスクごとに仕事場を作れる](https://learn.chatgpt.com/docs/environments/cloud-environments)。一番自動化できていなかったのは、開発環境だったのだ。

ただ、その結論にたどり着く少し前。私は中古オークションで、2TBのSSDを買ってしまっていた。

「あれ？ このSSD、いらなくない？」

またオークションに出品した。前の話は、ここで終わっていた。

## 売るはずのSSDを、結局増設することにした {#local}

<figure>
<img src="/img/blog-cloud-ssd-local-20261006.webp" alt="プロジェクトごとに並行作業を整理したPCと、増設用SSD、別媒体のバックアップ" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>任せる場所だけでなく、見渡しやすさと戻れる場所も大事だった。</figcaption>
</figure>

でも、一人で複数の開発を並行しているうちに、別の不便に気づいた。

ローカルのCodexでは、左側にプロジェクトが並び、その下にセッションが積み重なる。「何を進めて、どこへ戻るか」が見渡しやすい。

私が使ったクラウド側の画面では、GitHub経由のセッションを追う形になり、この整理の感覚を得にくかった。履歴が消えるという話ではない。**プロジェクトの下に仕事が蓄積されて見えること**が、私には大事だった。

いつかクラウドのGitHubリポジトリも、同じようにプロジェクトとして並んでほしい。これは今後への期待だ。それまでは、この使いやすさも選びたい。

そして、もう一つ。バックアップだ。

仮にアカウント停止や障害でChatGPTやCodexが使えなくなっても、成果物を手元に残し、別媒体にもバックアップしておけば、コードを取り戻して別の環境で続けやすい。SSDを増設するだけでは、バックアップにはならない。

Codexには、保存済みの会話を再開する方法もある。たとえばCLIの `codex resume`。ただし、これは消えたファイルや停止したアカウントを復旧する機能とは別だ。

こうして私は、**結局、2TBのSSDを増設することにした。**

> SSDが足りない → 買う → Cloudを試す → 売ろうとする → 整理しやすさと備えを考える → やっぱり増設。今ここ。

GitHubを原本にする。Cloudに仕事を任せる。ローカルには、見渡せる仕事場を残す。

アップグレードすべきだったのは、開発環境についての自分の考え方だった。**自由になるために、手元に残すものもある。**

そして今回、一番自動化できなかったのは――私のSSDをめぐる迷走だった。

---

まず一つのプロジェクトを、GitHubとバックアップから作り直せる状態にしてみる。[AIの使い方や仕事の整え方を相談する](/#contact)。

<details>
<summary>補足：何を、どこから復元する？</summary>
<p><strong>コードと開発環境</strong><br>GitHubに保存済みのリポジトリを取得し、記録したバージョンとセットアップ手順で再構築します。未コミットの変更、Git管理外の素材、ローカルの設定は別途バックアップが必要です。秘密情報は安全な保管先から設定します。PC全体を丸ごとコピーする仕組みではありません。</p>
<p><strong>Codexの会話</strong><br>CLIでは <code>codex resume</code> で保存済みセッションを選び、<code>codex resume --last</code> で現在の作業フォルダの直近セッションを再開できます。会話の保存状態と利用可能なアカウントが前提で、プロジェクトのファイルを復元する操作ではありません。<a href="https://learn.chatgpt.com/docs/developer-commands#codex-resume">公式の再開コマンド</a>を参照してください。</p>
<p><strong>バックアップ</strong><br>作業用SSDとは別の媒体にも保存し、実際に戻せるか確認します。GitHubへの保存、成果物の復元、会話の再開、アカウントの復旧はそれぞれ別です。</p>
<p>技術説明の確認日：2026年10月6日。購入・再出品・増設の判断と画面の使用感は運営者本人の体験です。画面の整理方法は利用環境やバージョンで変わり得ます。</p>
</details>
