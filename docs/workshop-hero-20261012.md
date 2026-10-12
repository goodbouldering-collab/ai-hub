# AIエージェント講習のヒーロー（2026-10-12）

状態: PR統合・Cloudflare本番公開・実画面確認済み。今回の公開残件なし。

## 変更

抽象的なガラスの輪を、講師と受講者が仕事を持ち込んでAIエージェントを学ぶ、生成イメージ1枚に変更。画面の「依頼・実行・確認」、成果物を指す手、気づきのある表情を主役にした。実在の講習記録と混同しないよう「AIエージェント講習のイメージ」と表示する。

PCでは画面ほぼ全幅に表示し、余白側へすりガラスの見出しを重ねる。1300px以下は画像の下に見出しを配置。スマートフォンは人物と実演画面を中心に表示。短いフェードと、動きを減らす端末設定に対応する。本文・3行見出し・診断・7講座・最新ニュースとその位置は変えない。

原本1672×941 PNG、内蔵image_genで生成。SharpでWebP1672px（195,322bytes）と800px（77,038bytes）へ変換。[原本・最終プロンプト](../assets/hero-workshop-20261012/PROMPT.md)。旧原本・旧配信画像は保持する。

## 検証

- `python -m unittest tests.test_diagnosis_buttons tests.test_focused_ux tests.test_editorial_home tests.test_home_updates -v`: 19成功。
- `npm --prefix cloudflare-runtime test`: 7成功。公開経路検査PASS（既存のpartial注記あり）。
- 全HTMLから今回のfigureとstyleを除いた内容が前後一致。再適用は冪等、日次装飾の再生成後も新画像1枚・7講座・削除済み導線を保持。
- 最新正常版 `.daily-news-release-20261012-verified` のmanifest614資産を照合し、トップ・ニュース・ブログ・sitemapの本番SHAも一致。変更はindex.htmlと新画像2ファイル、613資産とWorker SHA `644f3ee74fc80f7bb4e59fd08816a51da64beb901b719f1c13b953e72f87cdd3` を保持。
- Chrome DevTools接続で1440px・820px・390px・320pxを確認。人物と実演画面、見出しの可読性、横はみ出しなしを検証。CUAはkernel assetsのパスが見つからず、仕様内のリセット・再初期化も失敗したため検証ブラウザへ切替。
- スクリーンショットはツール出力で確認。ファイル保存はChromeツールのworkspace設定により拒否されたため、別経路で同じ保存を迂回していない。
- 48時間プレビュー: http://127.0.0.1:4101/ 、親PID61912、2026-10-14 09:10:57 JST終了予定。
- Node24.15.0／Python3.12／Wrangler4.90.0。実行証拠は `tmp/delivery/20261012-hero-agent-workshop/` と同名JSON。

## 公開結果

- [PR #166](https://github.com/goodbouldering-collab/ai-hub/pull/166)、ソースcommit `aa877c1391ea9da2fc5fa887cd5bdde7e2b34c8c`、統合・初回公開SHA `6149051b8a3818dc8a7875054901a7243d784be8`。Cloudflare公開先チェック2件成功後に統合。
- 確定Git blob12入力から再生成し、プレビューのHTMLと一致。初回候補はCRLF変換を厳密検査が検出し不採用。`git -c core.autocrlf=false archive` で作り直し、入力とGit blobの完全一致を確認してから公開した。
- 登録元のForDeployガードとdry-run成功、Cloudflare version `d8742250-5ba6-4741-98c0-9a2e4ae9ec63`。index.html＋画像2点だけを公開し、613資産と管理Workerを保持。
- 本番10経路のHTTP・公開6資産のSHA一致。トップ・ニュース・ブログ・既存記事・画像2点を照合。health200、管理入口303、未認証管理API401、login200を確認。
- Chrome DevTools接続の検証ブラウザで本番PC1440px／スマートフォン390pxを実画面確認。画像1枚の読込、講師と受講者・実演画面、3行見出し、7講座、横はみ出しなし。メニュー開閉、メニュー選択フロー、AI実力診断ページへの遷移が成功。
- 登録公開元ではPresent.mdだけを3方向で統合し、他の7ローカル差分と既存ステージを保全。事業ルートの旧HEADは変更していない。
- 公開結果の記録を統合した最終SHA・versionは `tmp/delivery/20261012-hero-agent-workshop.json` を参照。記録統合後も616公開資産とWorkerが同一であることを照合する。
- 次回の正常版は登録元 `.workshop-hero-release-20261012-final/public`。verification.jsonと最新本番を照合して使う。旧 `.daily-news-release-20261012-verified` は今回の比較基準として保持。

確認URL: https://aiclimb.aiclimb.workers.dev/
