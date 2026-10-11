# 診断をブログの上へ

2026-10-11。対象: https://aiclimb.aiclimb.workers.dev/ 。本人が画面で選択した「あなたのAI実力を試す」「サイトのAI対応を調べる」の2ボタンを、ブログの直前へ移動する。

「まずは診断で、次の一歩を。」「自分のAI活用力やサイトの課題を、ここからチェック。」を追加。既存ボタン文言・リンク・診断機能は維持。PCは2列、スマートフォンは1列で、AI実力診断を先に表示する。

## 検証と公開

- `core/diagnosis_copy.py` の生成に反映し、日次再生成後も位置と案内を保持する。Python24件、Cloudflare7件、既存のニュース公開検査が成功。
- 最初の検証時は `.news-below-blog-20261011-final` と本番のSHA一致を確認。その後、並行PR #140の連絡先更新を統合し、`.ai-business-contact-20261011-final` を新しい基準に採用。公開直前に本番とのSHA一致を確認済み。新しいbuilderは600資産中index.htmlだけを変更し、診断グループと専用CSS以外のバイト、599資産、Workerを保持する。
- アプリ内ブラウザ1440px/390pxで横はみ出しなし、順序、2診断へのリンク遷移を確認。既存AI相談Chromeの接続が応答しないため代替を利用。
- PR [#141](https://github.com/goodbouldering-collab/ai-hub/pull/141) の公開SHA `e6577d19b1ee5503225fde44627ba9233a6aae12` から再生成し、候補との600資産・Worker一致を確認。登録元 `work/genspark-profile-edit/cloudflare-runtime`、target defaultで中央ForDeployガード成功後、Wrangler4.143.1で公開。Cloudflare version `c27dbfad-f10a-4c03-8c4c-1ce5899a3ad6`。
- 本番PC1440px/スマートフォン390pxで診断→ブログ→ニュースの表示、横はみ出しなし、2つの診断画面へのクリック遷移を確認。診断データ送信はしていない。ホーム・両診断ページのSHA一致、health200・管理経路・API401・旧Codex URL転送も確認。既存の別作業17ファイル・ステージを保全。
- 公開資産は登録元 `.diagnosis-above-blog-20261011-final`、確定入力は `.diagnosis-above-blog-20261011-source`。Git/PR/証拠/本番応答の完了検査は `DELIVERY_VERIFIED`。今回の依頼の残件なし。文書の事後更新は別PRで共有し、公開SHAは変更しない。

工程: 事業ルート `tmp/delivery/20261011-diagnosis-above-blog.json`。候補と証拠は `tmp/diagnosis-above-blog/`。ローカルプレビュー http://127.0.0.1:4039/ 、親PID45360、2026-10-13 20:20:19 JST終了予定。旧作業worktreeはAGENTS差分と証拠を保全したまま再利用。

本番証拠は登録元 `tmp/delivery/20261011-diagnosis-above-blog/` のdeploy.txt、live-http.json、live-feature.txt、live-browser.json、live-desktop.png、live-mobile.png。
