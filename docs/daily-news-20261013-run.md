# 2026-10-13 AIニュース・Codex更新

状態: Git統合・Cloudflare公開・本番検証済み。

直近48時間（日本時間10月11日朝〜13日朝）の公式5件を採用。全URL HTTP200・本文と表示日を確認。発表元はMicrosoft2、AWS1、Google1、IBM1。F1の4月導入事例は10月12日の記事紹介、Google拡充は今月後半予定、StudentSimは研究段階と明記。HCLTechの候補は本文取得が2回timeoutとなり採用しなかった。

Codex: October 5–9, 2026 / rust-v0.162.1 / fingerprint 1b7838fead7502d54cdae13e02c5f89ae7065b1f33a1d86ccddd6b1af05e61ed。検証済みfetch/fingerprint/update_articleで差分なし、全バイト維持。

基準: .hero-three-actions-release-final/public、616資産、source e803e0e84f3c89e4603afd0713e6b69593e32edd。全manifest、本番6SHA、更新前再生成差分0。最新の講習ヒーロー・3入口・7講座とブログを保持。候補はindex.html、ai-news/index.html、sitemap.xmlの3資産のみ変更。管理Worker SHA 644f3ee74fc80f7bb4e59fd08816a51da64beb901b719f1c13b953e72f87cdd3 は不変。

57 tests / assets / deployment policy / diff check成功。検証スクリプトの入口リンク期待値を最新公開の3入口へ更新。最初のテストは疎なcheckoutの不足とTEMP権限で失敗し、必要Pythonファイルの展開とプロジェクト内TEMPで解消した。画像のみhardlink、書換対象のtextは独立copy。

証拠はoutputs/daily-20261013、工程はtmp/delivery/20261013-daily-ai-news.json。元のdirty・stagedと事業ルート旧mainを保全。Vercel、SNS、メール、課金、認証、DNS、別定期は変更しない。

## 公開結果

- PR #170の2チェック成功、commit `99cd199720273ff24b1f638770437e9da704a4b7`、統合・公開SHA `34cc1e740acd2b43da5d2507c8b42b0407cea34f`。67 Git blob入力をcore.autocrlf=falseのarchiveで抽出し、候補616資産と全ハッシュ一致。登録公開元HEADの一致確認。未公開JPC差分は入力へ混ぜない。
- 中央ForDeployとdry-run成功、既存Workerをno-bundle/keep-varsで維持。Cloudflare version `0eef9738-a0b3-45c4-a10b-1210d2b9382b`、deployment `c1ff3168-00f5-4895-9c1a-81f01f66ab23`、100%。Worker etag/bindings/runtime不変。
- --live成功。独立5件、トップ3件、ブログ除外、旧3URL301、healthと既存記事200、管理入口のログイン遷移後200、管理API401。配信HTML・ヒーロー画像等9SHA一致。
- 既存Chrome接続browser3で本番URLを確認。PC1440px／スマホ390pxでトップと独立ページ、もっと見る遷移、ニュース/Codex同じ30px・800見出し、目次なし、横はみ出しなし。確認画像4枚を保存し、viewportはreset済み。
- 既存8作業ファイルとstaged差分を保全。Present.mdとhome.htmlの重複はバックアップ後に3方向統合し、JPCの未公開URL修正も保持。旧事業ルートmainを変更しない。
- DELIVERY_VERIFIED成功。文書更新のみ別PRで統合し、内容が変わらないサイトは再デプロイしない。次回baselineは `.daily-news-release-20261013-verified/public`、verification.json、production-summary.jsonを最新本番と照合する。
