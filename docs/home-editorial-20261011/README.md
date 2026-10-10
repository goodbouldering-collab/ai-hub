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

## 公開結果

- [PR #124](https://github.com/goodbouldering-collab/ai-hub/pull/124) はCloudflareチェック2件成功後に統合。公開SHA `40ce7c95f97e9cfec199543615f59cf958d9f186`、PR head `c1c71917c830f1d946b7fccb44d7dff06c98b8c3`。
- 登録公開元をfast-forwardし、別作業15ファイルの内容と無関係なステージ済みエントリをハッシュ・index比較で保全。Present.mdのJPC公開承認待ち記録もローカルに保持する。
- 統合SHAから `.editorial-release-20261011-final` を生成。入力はすべてcommit済み、WorkerはGitの確定blobから抽出し、作業中のWorker差分を混入させていない。
- target default のガード成功後、Wrangler 4.143.1で公開。2026-10-11 00:37 JST、version `3121c0bc-72a6-446f-84bc-28ddb1c2a3a6`、deployment `42993aec-e913-466b-b24c-60c326c46129`、100%配信。
- [トップ](https://aiclimb.aiclimb.workers.dev/)、[全一覧](https://aiclimb.aiclimb.workers.dev/blog/)、[AIニュース・Codex](https://aiclimb.aiclimb.workers.dev/ai-news/) を検証。本番35資産が生成物と一致し、記事10本は元の内容のまま。/health・/admin・既存記事は200、保護された /api/admin/ping は401、旧Codex記事3経路は301を保持。
- 本番でもPC1440px、スマートフォン390/360pxの表示・操作を確認。全一覧11画像は末尾までスクロールして読込確認。講習カードの高さは候補版と一致。メニュー開閉、もっと見る、講習詳細の展開に問題なし。
- `delivery-status.mjs check` は文書更新前に `DELIVERY_VERIFIED`。証拠は登録公開元 `tmp/delivery/20261011-home-editorial-design/` の production-hashes.json / production-feature.txt / production-visual.json / delivery-check.txt。
- 今後の公開基準は `.editorial-release-20261011-final/public` と verification.json。公開後のPresent.md・本記録のみの更新ではサイトを再デプロイしない。

基準: 登録公開元の .home-blog-text-list-release-20261010/。再生成:
```powershell
python -B -X utf8 scripts/build_home_editorial_release.py --baseline <基準フォルダ> --output <新規リリースフォルダ>
```
統合SHAの入力だけで再生成し、台帳の work/genspark-profile-edit/cloudflare-runtime で default -ForDeploy ガードを通して公開する。Workerはコミット済み deployment/my-workflows/published-worker.mjs から抽出する。

工程記録: 事業ルート tmp/delivery/20261011-home-editorial-design.json。検証証拠: 同名フォルダ。
プレビュー: http://127.0.0.1:4027/ 、親PID 49588、2026-10-13 00:24:30 JST終了予定。旧プレビュー4026は前回の比較用に保持。
