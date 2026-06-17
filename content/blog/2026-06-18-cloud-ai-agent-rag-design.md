---
title: "クラウドAIエージェント時代のRAG設計"
date: 2026-06-18
role: ブログ / RAG設計・AIエージェント
gen_by: 由井 辰美 / AIハブ
summary: AIに資料を入れるだけではなく、どの情報をどの順番で見てもらうかを設計する。プロから初心者まで、RAGを仕事で使うための考え方を整理する。
image: /img/blog-rag-daily-agent-20260618.svg
---

<figure>
  <img src="/img/blog-rag-daily-agent-20260618.svg" alt="クラウドAIエージェントが毎日、売上、問い合わせ、レビュー、競合情報を確認する図解" loading="eager" decoding="async">
  <figcaption>クラウドAIエージェントは、一度の質問よりも、毎日の確認と提案で力を発揮する。</figcaption>
</figure>

＼皆さん、クラウドAIエージェント向けにRAGを設計していますか？／

AIは「質問するもの」から、「仕事を任せるもの」へ変わりつつあります。

そこで重要になるのがRAGです。技術用語として見ると少し難しく感じますが、仕事の現場で考えるなら、RAGはまず **「AI専用の資料棚」** です。

ただし、資料棚を作るだけでは足りません。プロとしてAIを業務に組み込みたい人も、これからコーディングやAIを習いたい人も、最初に押さえるべきなのは同じです。

**AIに何を聞くかではなく、AIにどの順番で考えてもらうか。**

ここを設計できるかどうかで、AIの答えは大きく変わります。

## RAGは「AI専用の資料棚」

<figure>
  <img src="/img/blog-rag-library-agent-20260618.svg" alt="PDF、議事録、マニュアル、売上、顧客情報をAI専用の資料棚として整理する図解" loading="lazy" decoding="async">
  <figcaption>RAGは、AIが必要な時に外部資料や社内データを探しに行けるようにする仕組み。</figcaption>
</figure>

RAGとは、AIが外部の資料やデータを取りに行き、それをもとに回答するための仕組みです。

PDF、議事録、マニュアル、商品情報、顧客情報、売上データ、問い合わせ履歴、レビュー、過去のブログ。こうした資料を、AIが必要な時に探しに行ける状態にしておく。

これがRAGの出発点です。

> 「AI専用の資料棚」

このたとえは、初心者にもプロにも使いやすいと思います。なぜなら、RAGの価値は「AIに情報を渡すこと」だけではなく、「AIが迷わず取り出せる状態にしておくこと」だからです。

図書館に100万冊の本があっても、どの棚を探せばよいかわからなければ役に立ちません。AIも同じです。

「資料を入れればAIは賢くなる」

そう考えたくなりますが、実際には違います。AIに必要なのは、資料の量だけではなく、探し方の設計です。

## 大事なのは「どの順番で見に行くか」

<figure>
  <img src="/img/blog-rag-search-order-20260618.svg" alt="AIが売上、利益率、在庫、レビュー、SEOの順番で確認するRAG設計の図解" loading="lazy" decoding="async">
  <figcaption>資料が増えるほど、AIには「まず何を見るか」という順番が必要になる。</figcaption>
</figure>

RAGを設計するとき、いちばん大事なのは資料名の一覧ではありません。

> RAGは図書館。
>
> クラウドAIエージェントは司書。
>
> RAG設計とは、「どの情報を、どの順番で見に行くか」を決めること。

たとえば「売上が落ちたら」とAIに任せる場合、いきなり改善案を出してもらっても仕事では使いにくい。

先に売上を見る。次に利益率を見る。次に在庫を見る。レビューを見る。競合を見る。最後に改善案を出す。

この順番があるから、AIの提案は現場で判断できる形になります。

```text
「売上が落ちたら」

売上データを見る
↓
利益率を見る
↓
在庫を見る
↓
レビューを見る
↓
競合を見る
↓
改善案を出す
```

この流れを決めておくだけでも、立派なRAG設計です。

AIに「考えて」と頼む前に、何を見て、何を後回しにするかを決める。ここが、これからのAI活用で差になる部分です。

## EC・交流会・ブログでは見る順番が変わる

<figure>
  <img src="/img/blog-rag-business-flow-20260618.svg" alt="ECと交流会でAIが見るべき情報の順番が違うことを示す図解" loading="lazy" decoding="async">
  <figcaption>RAG設計は業種や目的ごとに変わる。正解は一つではなく、仕事の流れに合わせる。</figcaption>
</figure>

RAG設計は、業務ごとに変わります。

ECなら、AIに見てほしい順番は次のようになるかもしれません。

```text
売上
↓
利益率
↓
在庫
↓
レビュー
↓
SEO
```

売れていても利益率が低ければ、広告を強める前に見直す必要があります。在庫が少なければ、販促より先に仕入れを確認します。レビューが悪ければ、SEOより先に商品説明や品質の確認が必要です。

交流会なら、順番は変わります。

```text
参加者
↓
業種
↓
課題
↓
紹介先
```

ここでは「誰が来たか」だけでは足りません。その人が何に困っているか、誰とつなぐと価値が出るか、次にどんな連絡をすべきかが大切です。

ブログ運用なら、検索語、顧客の悩み、商品情報、過去記事、競合記事を見る順番が必要になります。コーディング学習なら、作りたい画面、今のコード、エラー、公式ドキュメント、確認手順の順番が役に立ちます。

同じRAGでも、EC、交流会、ブログ、コーディング学習では資料棚も司書の動きも変わります。だからこそ、最初に業務を分解することが必要です。

## 最後に、人間が確認する場所を決める

<figure>
  <img src="/img/blog-rag-human-gate-20260618.svg" alt="業務分解、資料整理、順番決定、自動化範囲、人間確認範囲の5ステップ図解" loading="lazy" decoding="async">
  <figcaption>AIに任せる範囲と、人間が確認する範囲を分けると、業務に入れやすくなる。</figcaption>
</figure>

これからのクラウドAIエージェントは、毎日同じ確認を自動で行うようになります。

- 売上を確認する
- 問い合わせを確認する
- レビューを確認する
- 競合を確認する
- 次に書くブログや投稿の案を出す

その時、RAG設計がないと、情報は大量にあるのに何を優先して見るべきかわからず迷子になります。

逆にRAG設計ができていると、AIは次のような提案まで出しやすくなります。

> 「在庫が危険です」
>
> 「今週はこの商品を推してください」
>
> 「このブログを書くべきです」
>
> 「この顧客へ連絡した方が良いです」

RAG設計の第一歩は、とてもシンプルです。

1. 業務を分解する
2. 使う資料を整理する
3. 判断する順番を決める
4. 自動化する範囲を決める
5. 人間が確認する範囲を決める

AIに任せるとは、何でも自由に考えさせることではありません。見る資料、見る順番、判断基準、人間が止める場所を決めておくことです。

これからはAIに何を聞くかではなく、AIにどのように考えてもらうか。

その設計力が、企業の差になっていくと思います。

### 参考リンク

- [AWS: What is RAG? Retrieval-Augmented Generation explained](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [Google Cloud: What is Retrieval-Augmented Generation (RAG)?](https://cloud.google.com/use-cases/retrieval-augmented-generation)
- [Microsoft Learn: Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)
- [IBM Think: What is retrieval augmented generation?](https://www.ibm.com/think/topics/retrieval-augmented-generation)
