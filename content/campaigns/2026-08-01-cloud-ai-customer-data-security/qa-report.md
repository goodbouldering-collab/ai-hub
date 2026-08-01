# QAレポート

確認日: 2026-08-01

## ビルド

- コマンド: `C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe site\build_site.py`
- 結果: 成功
- 生成件数: blog 13件、lectures 7件、slides 2件、watch 110件
- 対象HTML: `site/dist/blog/2026-08-01-ai-personal-data-boundary.html`

## 組み込み

- 記事ページ: 生成済み
- ブログ一覧: 先頭カードに表示
- OGP: 最終タイトル、summary、WebPヒーロー画像を反映
- sitemap.xml: 対象URLを生成対象として確認
- H2: 4件
- figure: ヒーロー1件 + H2専用4件
- 本文中の外部参考リンク: 23件

## 画像

| 画像 | WebPサイズ |
|---|---:|
| hero | 200,478 bytes |
| rule | 153,100 bytes |
| flow | 94,126 bytes |
| database | 119,822 bytes |
| controls | 158,962 bytes |

全5枚を目視し、文字化け・実在の個人情報・ブランドロゴ・透かしがないことを確認。PNG原本からWebPへ変換し、記事ではWebPのみ参照する。

## PC幅 1440 × 1000

- H1: 改行されるが欠落なし
- ヘッダー: ナビゲーション表示正常
- 本文幅: 約1094px
- ページ横幅: viewport内に収まり、ページ全体の横スクロールなし
- DB比較表: コンテナ内に収まる
- ヒーロー画像: 読み込み・表示正常

## iPhone幅 390 × 844

- モバイルメニュー: 表示
- PCナビ: 非表示
- H1: 幅343px内に収まり、文字欠けなし
- ページ横幅: viewport内に収まり、ページ全体の横スクロールなし
- 7境界カード: 1列
- 4色分類: 1列
- DB比較表: 302pxの表示枠内で横スクロール可能（表本体740px）
- ヒーロー・H2画像5枚: `naturalWidth=1672`、全件読み込み成功
- ブログ一覧: 先頭カードの画像・タイトル・要約を確認
- ブラウザコンソール: warning/errorなし

## 公開状況

- ユーザーが2026-08-01に直接公開を承認済み
- commit / push / Vercel本番デプロイ: 実行待ち
- 本番URLの到達・OGP・sitemap確認: 実行待ち
