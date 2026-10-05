---
title: "一番自動化できていなかったのは、開発環境だった｜Codex CloudとSSDの話"
date: 2026-10-05
updated: 2026-10-05
authorship_note: "※内容は運営者が考え、AIで整えています。"
role: ブログ / Codex・開発環境
gen_by: 由井辰美 / AI相談
summary: "AIで開発は速くなったのに、SSD選びと常時起動PCの世話は人間のまま。GitHubで環境を再現し、Codex Cloudへ仕事場を移して気づいたこと。買った2TB SSDを、また売るまでの話です。"
image: /img/blog-cloud-ssd-hero-20261005.webp
status: published
---

<figure>
<img src="/img/blog-cloud-ssd-hero-20261005.webp" alt="PCの部品を増やす働き方から、スマホでクラウドへ仕事を頼む働き方へ" width="1672" height="941" decoding="async">
<figcaption>PCを強くする前に、PCへの依存を減らせないか。挿絵はすべて説明用のイメージです。</figcaption>
</figure>

コードを書く時間は減った。なのに、開発の準備やPCの世話は減らない。

最近、Codexを使うようになって開発速度が一気に上がった。コード、修正、テスト、Gitへのコミット。かなりの部分をAIに任せられる。

「開発、かなり自動化できたな」

そう思っていた。SSDが足りなくなるまでは。

## AIに任せていたはずが、熱伝導パッドを調べていた {#hardware}

<figure>
<img src="/img/blog-cloud-ssd-hardware-20261005.webp" alt="コードが動く横でSSD、ヒートシンク、熱伝導パッドを比較する手元" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>開発が速くなるほど、PCを整える用事が増えていった。</figcaption>
</figure>

足りないなら、増やせばいい。2TBのSSDを探し始めた。

ところが、私が見た価格は思ったより高い。さらに「Gen3？ Gen4？」「このPCで2TBを2枚使える？」「発熱は？」「ヒートシンクは？」と調べることが増えていく。

気づけば、AIで開発を自動化しているはずの人間が、**熱伝導パッドの厚みを調べていた。**

そして、もう一つ。外出先からも開発したかった。

## リモートで席は離れた。でも、PCの世話は残った {#cloud}

<figure>
<img src="/img/blog-cloud-ssd-cloud-20261005.webp" alt="常時起動の自宅PCを使う方法と、スマホからクラウドへ依頼する方法の違い" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>席から離れることと、そのPCがなくても仕事が進むことは違う。</figcaption>
</figure>

HOME PCを常時起動し、iPhoneからリモート接続できるようにした。これで自由になった、と思った。

でも、リモートは「PCの前にいなくてもいい」だけだった。電源、スリープ、自宅回線、Windows Update、SSD容量。HOME PCの世話は残る。

最新のAIを働かせるために、人間がPCを寝かせない。**結局、人間がPCを介護している。**

だったら、仕事の経路からHOME PCを外せないか。

そこでCodex Cloudを使う発想になった。

> これまで：iPhone → リモート → HOME PC → Codex → GitHub<br>
> これから：iPhone → Codex Cloud → GitHub

私にとって、リモートはPCの前から自由になること。クラウドは、そのPC自体への依存を減らすことだった。

[Codex Cloudは、手元のPCがスリープ中でも作業を続けられる](https://learn.chatgpt.com/docs/cloud)。この違いが大きかった。

## GitHubに「環境の作り方」も置けば、引っ越しを自動化できる {#github}

<figure>
<img src="/img/blog-cloud-ssd-github-20261005.webp" alt="コードとセットアップ手順を一つの原本にまとめ、別のPCとクラウドで環境を再現する図" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>運ぶのは、コードと環境を作り直せる手順。</figcaption>
</figure>

さらに、開発環境も一台のPCに閉じ込めなくていい。

GitHubにコードだけでなく、使う道具の一覧、バージョン、セットアップ手順も置く。別のPCやクラウドでは、それを取得して必要なものをそろえる。

**GitHubを経由して、開発環境のコピーや移動も自動化できる。** 正確には、対応する環境で同じ仕事場を作り直す仕組みだ。パスワードやAPIキーはGitHubに入れず、移動先で別に設定する。

Codex Cloudでも、[リポジトリから道具を準備し、確認した環境をタスクごとに再利用できる](https://learn.chatgpt.com/docs/environments/cloud-environments)。GitHubを原本に、CloudをAIの仕事場に。手元のPCやiPhoneは、指示と確認の端末になる。

Cloudだから、すべての処理が何倍も速くなるわけではない。けれど、自宅PCの空き容量や起動状態を気にする時間は減らせる。

独立した仕事なら、AI①にバグ修正、AI②に新機能、AI③に調査。自分は別の仕事へ。戻ってから変更とテスト結果を確認し、合わせればいい。

**AI時代の速さは、人間が待たなくていい時間を、どれだけ増やせるか。**

もちろん、実機の動作や画面の確認など、必要なときはローカルに戻る。全部を移すより、PCに頼る場面を減らせばいい。

## そう気づく少し前に、2TBのSSDを買っていた {#resale}

<figure>
<img src="/img/blog-cloud-ssd-resale-20261005.webp" alt="買ったSSDを再びオークションに出品する様子を描いたイラスト" width="1672" height="941" loading="lazy" decoding="async">
<figcaption>考え方を変えるより、購入ボタンを押すほうが少し早かった。</figcaption>
</figure>

ただし、この話にはオチがある。

この結論にたどり着く少し前、私は結局、2TBのSSDを中古オークションで買ってしまった。

Codex Cloud中心に切り替えてから思った。

「あれ？ このSSD、いらなくない？」

現在、そのSSDは――またオークションに出品している。

> SSDが足りない → 規格と発熱を調べる → 2TBを買う → Cloudにする → また売る。今ここ。

2TBのSSDを買って、また売るところまでやって分かった。

AI時代、最初にアップグレードすべきだったのは、SSDでもPCでもない。**開発環境についての、自分の考え方だった。**

そして今回、一番自動化できなかったのは――私のSSD購入だった。

---

PCを買い足す前に、一つのプロジェクトを「GitHubから環境を再現できる状態」にしてみる。そこから始めるだけでも、仕事の渡し方は変えられます。[AIの使い方や仕事の整え方を相談する](/#contact)。

<details>
<summary>補足：環境のコピーとクラウドの違い</summary>
<p><strong>GitHubに置けばPC全体がコピーされる？</strong><br>いいえ。コード、依存関係、セットアップ手順を使って環境を再現します。OS固有のアプリ、認証、手元だけのファイルまで自動で移るわけではありません。</p>
<p><strong>クラウドなら確認も全部任せられる？</strong><br>変更とテスト結果のレビューは必要です。2026年10月5日確認の公式案内では、Codex CloudのComputer／browser useは未対応です。画面確認や実機依存の作業は、利用できるローカル環境と組み合わせます。</p>
<p>技術説明の確認日：2026年10月5日。出典：<a href="https://learn.chatgpt.com/docs/cloud">OpenAI「Codex Cloud」</a>、<a href="https://learn.chatgpt.com/docs/environments/cloud-environments">OpenAI「Cloud environments」</a>。SSDの購入・再出品と使用感は、運営者本人の体験です。</p>
</details>
