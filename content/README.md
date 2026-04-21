# content/ — 編集ソース

AI-watch のサイトに出す「静的コンテンツ」の一次ソース。Markdown を編集して `python site/build_site.py` を実行すると、`site/dist/` に HTML が書き出される。

## ファイル

| パス | 生成先 | 用途 |
|---|---|---|
| `speaker.md` | `site/dist/speaker.html` | 講師紹介（由井辰美）。AI講習の進行メモ・作成アプリ・関わっているWebサイト・参考リンクまで一元管理 |
| `lectures/*.md` | `site/dist/lectures/<slug>.html` | 講習資料の個別ページ（これから追加） |
| `assets/` | `site/dist/assets/` | 画像・PDFなどの添付物 |

## 書き方のルール

- Markdown 準拠。タイトルは H1、節は H2、小項目は H3 で
- 外部URLは素のMarkdownリンク（`[text](url)`）で。絵文字プレフィックスは自由
- H1 直後に YAML フロントマターで `name`, `role`, `profile_url` 等のメタを書くと、ビルド時にヘッダーに展開される
- 資料やスクリーンショットは `assets/` に入れ、相対パス `./assets/xxx.png` で参照

## 新しい講習資料を追加する

```bash
# content/lectures/2026-04-ai-basics.md を作って編集
python site/build_site.py   # → site/dist/lectures/2026-04-ai-basics.html
git add content/lectures/ && git commit -m "docs: add lecture note"
git push    # Pages に自動反映
```
