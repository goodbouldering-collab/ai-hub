# content/ — AI相談の編集ソース

AI相談のサイトに出す静的コンテンツの一次ソースです。Markdownを編集して `python site/build_site.py` を実行すると、`site/dist/` にHTMLが書き出されます。本番はmainへのpush後、Vercelへ反映されます。

## ファイル

| パス | 生成先 | 用途 |
|---|---|---|
| `speaker.md` | `site/dist/speaker.html` | 講師紹介（由井辰美）。AI講習の進行メモ・作成アプリ・関わっているWebサイト・参考リンクまで一元管理 |
| `lectures/*.md` | `site/dist/lectures/<slug>.html` | 同じ説明順で作る受講資料の個別ページ |
| `assets/` | `site/dist/assets/` | 画像・PDFなどの添付物 |

## 受講資料の共通ルール

- タイトルはfrontmatterの`title`に書き、本文はH2とH3で整理する
- 個別の`<style>`や専用レイアウトを本文へ入れず、共通テンプレートを使う
- 専門用語は初めて出た場所で日常の言葉へ置き換える
- 演習は1つに絞り、最後に完了を判断できるチェックを付ける
- 画像やPDFは`lectures/assets/`へ入れ、`./assets/xxx`で参照する
- 重複資料を一覧から外す場合は、URLを残したまま`listed: false`を設定する

### frontmatterのひな形

```yaml
---
title: 資料のタイトル
date: 2026-07-16
role: 受講資料
gen_by: 由井 辰美 / AI相談
summary: 一覧で表示する短い説明
audience: この資料を読む人
duration: 10分
goal: 読み終えた時にできること
category: ai-start
learning_order: 1
level: 入門
listed: true
---
```

`category`は`ai-start`、`ai-work`、`ai-salon`、`climbing`から選びます。AIアプリサイト自作講習・相談は独立ページとして扱います。`learning_order`はカテゴリの中での順番です。

### 見出しの順番

```markdown
## この資料は誰向けか
## 今日できるようになること
## まず結論
## 順番に理解する本文
## 具体例 / やってみる
## できたかチェック
## 次に読む資料
## 用語・出典
```

## 新しい受講資料を追加する

```powershell
python site/build_site.py
# site/dist/lectures/<slug>.html と一覧を確認する
```

公開前に、見出し順、対象者、所要時間、リンク、PC幅とスマホ幅、一覧の前後導線を確認します。
