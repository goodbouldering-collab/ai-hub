# トップとブログ一覧の画像リスト化

2026-10-11。トップのブログとCodex情報を一緒にし、画像左・本文右の3件リストへ変更する。人物が登場し、内容が伝わる立体イラストを採用し、講習カードの縦幅を抑える。

## 変更

- トップは「今日のAIニュース5とCodex情報」と最新ブログ2件。「もっと見る」は /blog/ へ移動。
- ブログ一覧はCodex情報1件と既存公開記事10件。元のタイトル・日付・要約・リンクを保持。
- 新画像21点を制作。ホームの説明画像17箇所に10点を再利用し、記事一覧に11点。架空の成人を描いたクレイ・紙の立体表現。講師写真、会場、実績画面、Instagram、記事本文内の既存画像は保持。
- 講習6カードは画像と講習名・料金を横並びにし、説明・詳細・申込を全幅で表示。詳細は開くと全幅。本文・料金・リンク・詳細内容は一致検査。
- 日次ニュースと通常生成にも新表示を接続。通常ブログ一覧の公開境界は site/templates/ai-news/blog.html。ローカルMarkdownだけを理由に一覧へ追加しない。
- Cloudflareのみの公開方針に合わせ、旧GitHub Pagesのmain push自動公開を停止。手動用の履歴は保持。

## 制作と検証

デザイン検討、記事画像、ホーム画像・実装を分担。元PNGとプロンプトは事業ルート assets/home-editorial-20261011/、配信用WebPは site/static/design-system/studio/images/editorial-20261011/。21点合計1,352,274 bytes。画像生成はOpenAI組み込み機能を使用し、内容を変えずSharp 0.35.5でWebP圧縮。[採用画像manifest](artwork-manifest.json)にプロンプト・ハッシュを記録。

- Python 25件、Cloudflare・管理Worker 9件、計34テスト成功。runtimeテストの最初の実行場所違いは正しいruntimeディレクトリで再実行して解消。
- 公開中556資産を固定。変更は index.html と blog/index.html、追加21画像。他554資産とWorkerは不変。
- 記事本文全資産、ニュース本文、講習の本文・価格・詳細・申込先、その他のトップ文言・リンクを照合。
- Codex内ブラウザでPC1440px、スマートフォン390px、狭幅360pxを確認。画像と本文の重なり・横はみ出しなし。3件表示、もっと見る→11件、メニュー開閉、講習詳細の全幅展開を確認。
- 講習カード高さはPCで401/401/354/354/451/451pxから360/360/310/310/412/412pxへ。390px幅で448/397/371/371/548/413pxから397/351/347/325/519/391pxへ。
- AI相談用Chrome Profile 1は接続されておらず、ネイティブ起動は利用不可。共通手順に従いCodex内ブラウザで公開面を検証。Chromeへのログインは要求していない。
- 計測準備票を確認。Google側の設定やタグ追加は今回の範囲に含めない。

## 公開準備

現在はローカル検証済み。本番反映結果は公開後にここを更新する。

基準: 登録公開元の .home-blog-text-list-release-20261010/。再生成:
```powershell
python -B -X utf8 scripts/build_home_editorial_release.py --baseline <基準フォルダ> --output <新規リリースフォルダ>
```
統合SHAの入力だけで再生成し、台帳の work/genspark-profile-edit/cloudflare-runtime で default -ForDeploy ガードを通して公開する。Workerはコミット済み deployment/my-workflows/published-worker.mjs から抽出する。

工程記録: 事業ルート tmp/delivery/20261011-home-editorial-design.json。検証証拠: 同名フォルダ。
プレビュー: http://127.0.0.1:4027/ 、親PID 49588、2026-10-13 00:24:30 JST終了予定。旧プレビュー4026は前回の比較用に保持。
