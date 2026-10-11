# 診断をブログの上へ

2026-10-11。対象: https://aiclimb.aiclimb.workers.dev/ 。本人が画面で選択した「あなたのAI実力を試す」「サイトのAI対応を調べる」の2ボタンを、ブログの直前へ移動する。

「まずは診断で、次の一歩を。」「自分のAI活用力やサイトの課題を、ここからチェック。」を追加。既存ボタン文言・リンク・診断機能は維持。PCは2列、スマートフォンは1列で、AI実力診断を先に表示する。

## 検証と公開

- `core/diagnosis_copy.py` の生成に反映し、日次再生成後も位置と案内を保持する。Python24件、Cloudflare7件、既存のニュース公開検査が成功。
- 直前の公開版 `.news-below-blog-20261011-final` のホームと本番のSHA一致を確認。新しいbuilderは600資産中index.htmlだけを変更し、診断グループと専用CSS以外のバイト、599資産、Workerを保持する。
- アプリ内ブラウザ1440px/390pxで横はみ出しなし、順序、2診断へのリンク遷移を確認。既存AI相談Chromeの接続が応答しないため代替を利用。
- 公開前。PR統合後、登録元 `work/genspark-profile-edit/cloudflare-runtime`、target defaultから中央ForDeployガードを通し、確定SHAの生成物を公開する。

工程: 事業ルート `tmp/delivery/20261011-diagnosis-above-blog.json`。候補と証拠は `tmp/diagnosis-above-blog/`。ローカルプレビュー http://127.0.0.1:4039/ 、親PID45360、2026-10-13 20:20:19 JST終了予定。旧作業worktreeはAGENTS差分と証拠を保全したまま再利用。
