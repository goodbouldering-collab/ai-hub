# トップページのブログを以前のリスト表示へ戻した記録

2026-10-10。依頼は、現在の記事内容を保ったまま、トップページのブログ表示を1週間以上前へ戻すこと。

## 公開した表示

9月30日の `080d49ef` にある「日付＋記事名」の最新2件リストを復元した。ヒーロー直下のAIニュースと並べ、スマートフォンでは縦に配置する。10月9日・10月5日の最新記事とブログ一覧へのリンクを維持した。下段の重複する最新ブログ欄はなくした。

記事本文、画像、ブログ一覧、ニュース本文、講習欄の文言・料金・申込先・小型表示は変更していない。日次更新でも同じ表示になるよう `core/home_updates.py` と共通CSSへ反映した。

## 統合と本番

- 実装PR: https://github.com/goodbouldering-collab/ai-hub/pull/122
- 最終head: `91c9d886b1166837d661a9c1ce37655c0a11441a`
- 統合・公開SHA: `458a3485aad3219dcb206626ba1e7523a77c3f80`
- Cloudflare Worker: `aiclimb`、Wrangler 4.143.1
- Version: `7dac22b6-8810-45ef-9f95-9756fac79763`
- Deployment: `2e03affe-5ee0-450d-b9bf-9ecad5f810c8`、100%配信
- 公開URL: https://aiclimb.aiclimb.workers.dev/

台帳の `work/genspark-profile-edit/cloudflare-runtime` から `default -ForDeploy` 成功後に公開した。`wrangler-profile-release.jsonc` を使い、統合済みWorkerのGit blobを新規成果物の `runtime/` に配置して配信した。Worker本体のSHA256、公開後のetag・runtime・bindingは直前の公開版と一致する。

## 内容不変の確認

直前の `.daily-news-release-20261010` を出力ハッシュ付きmanifestで固定し、`scripts/build_home_blog_text_list_release.py` で再生成した。556ファイルのうち変更は `index.html` の1件、555件は不変。記事全資産、ブログ欄以外のホームHTML、講習欄のHTML・CSSを照合した。

登録公開元にあった別作業の14ファイルは統合前後のSHA256が一致。公開承認待ちのJPC実績変更や未コミットWorkerは今回の配信へ入れていない。Present.mdは本番確認後、今回の記録部分だけ別途更新した。

## 検証

- ホーム5件・日次ホーム生成4件・Cloudflare runtime 7件・管理Worker 2件、計18テスト成功。
- Git差分検査、ローカルCloudflareガード、PRの2チェック、assets検証成功。
- 本番16資産のSHA256が成果物と一致。health・ブログ記事・管理ログイン画面は200、未認証管理APIは401、旧Codex記事の3URLは301。
- Codex内ブラウザで1440×1000と390×844を確認。横はみ出しなし、最新2件の日付・題名、スマートフォンのメニューとブログ位置への移動、最新記事と一覧への遷移を確認。
- `AI相談 - Chrome.lnk` は `Profile 1` と確認済み。接続がなくネイティブ起動も利用できないため、許可済みのCodex内ブラウザを使用した。Chrome Profile 1自体での確認は未実施。
- 公開工程記録は、後続の文書更新前に `DELIVERY_VERIFIED`。

## 引き継ぎ

現在の公開資産は登録公開元の `.home-blog-text-list-release-20261010/public`。`verification.json` と本番を照合し、次回の基準にする。直前のdaily版は今回の入力証拠として保持し、最新出力と混同しない。

今回の証拠は登録公開元の `tmp/delivery/20261010-home-blog-list-restore/`。工程記録は事業ルートの `tmp/delivery/20261010-home-blog-list-restore.json`。検証時の作業ディレクトリ不一致は正しいruntimeディレクトリで解消し、古いWranglerの試行はdry-runのみで終了した。

ローカルプレビュー: http://127.0.0.1:4026/ 、親PID 21164、2026-10-12 22:48:02 JST終了予定。制作物は事業ルート `tmp/delivery/20261010-home-blog-list-restore/candidate/` に保持する。管理画面の本人ログイン後受入とJPC公開承認待ちは別作業として継続する。
