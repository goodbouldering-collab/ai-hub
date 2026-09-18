# Cloudflare・EmDash・WebMCP 解説記事

- 対象：告知・サイト更新・問い合わせに時間を取られている地域事業者、講師、施設運営者。
- 記事：`content/blog/2026-09-18-cloudflare-emdash-webmcp.md`
- 画像：`site/static/img/blog-cloudflare-ai-*-20260918.png`（ヒーロー1枚、H2用4枚）
- 公開予定URL：`https://aiclimb.aiclimb.workers.dev/blog/2026-09-18-cloudflare-emdash-webmcp.html`
- 行動：よく聞かれる質問を3つ整え、AIに任せる仕事を1つ決める。
- 事実確認：`sources.md`。導入の店舗シーンは架空と明記。実在の導入例はCloudflare公式ブログのEmDash移行。
- 編集設計：`brief.md`。画像プロンプト・alt・キャプション：`image-prompts.json`。
- 公開指示：ユーザーの「コミットプロリクデプロイして」により、この原稿の公開が承認済み。

## 再生成と検証

既存本番を検証済みスナップショットから複製し、記事と画像5枚を追加。トップのブログカード・ブログ一覧・サイトマップだけを更新する。既存記事・デザイン・管理/APIのruntimeを保持し、全ファイルのハッシュを検証する。

```powershell
python -m pip install -r deployment/cloudflare-blog/requirements.txt
python scripts/build_cloudflare_blog_release.py --baseline <verified-release-directory> --output .editorial-release-cloudflare-blog-<unique-label>
```

`deployment/cloudflare-blog/baseline.json` が基準リリースのSHA・Cloudflareバージョン・manifestハッシュを固定する。公開直前に現行本番バージョンと一致することを確認する。同時に別の公開が進んでいれば、最新の検証済み基準に更新し、再生成・再検証・コミットする。

正本main統合後、中央台帳のworkingDirectoryから生成・ガード・デプロイを行い、`verification.json` と公開記録を出力ディレクトリへ保存する。候補フォルダは本番の正本として扱わない。
