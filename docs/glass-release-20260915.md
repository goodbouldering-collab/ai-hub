# 全ページのグラスデザイン公開

前回のデザインコミットfa7448cを、台帳登録済み公開元へ限定統合する。現在のプロフィール変更と全公開文章を維持し、共通の透過面・画像レイヤー・光の追従を適用。

## 再現

1. 既存build-profile-release.pyで検証済みプロフィール版を再現する。
2. build-glass-release.pyがglass-baseline.jsonの全463資産とruntime15モジュールを検証し、.glass-releaseへコピーして装飾だけ適用する。
3. verify_glass_art.pyで全HTML・操作・画像・既存JS、ログイン、runtimeを比較する。
4. 確定コミットをorigin/mainへ統合後、登録cwdでガード実行。Wranglerでruntimeをdry-run bundleしてから、同じ登録設定のentry/assetsを明示して公開する。

今回のビルドではspeaker_contentの再生成を使わない。最新の略歴やプロフィール導線、ニュース本文を装飾処理で書き換えない。元のdirty公開物は入力にしない。

2026-09-15にVercel MCPで既知の運用チーム goodboulderings-projects のプロジェクト一覧が空、ai-hubも404であることを読取確認。Vercelへの変更操作は実行しない。

公開先はaiclimb.aiclimb.workers.dev。PC/スマホの目視検証は専用ブラウザ接続の制限により未完了。内容保持・操作の自動テスト・本番HTTP確認と区別して報告する。

## 本番完了（2026-09-15）

- ユーザーがpushを明示許可し、公開ソース `45765034b43b9346be04fe0271f2e6062021532d` をGitHub mainへ統合。デプロイ前のHEADとorigin/main一致、tracked/untracked source cleanを確認。
- 確定SHAから463資産とruntimeを再生成し、検証済み候補との全ハッシュ一致を確認。公開先ガードはdeploymentAllowed=true。
- 公開Worker: `aiclimb`、Version `e5689a85-52cc-4e20-8fa7-04c73e4feafc`。Cloudflare配信一覧で100%を確認。
- 本番URL: https://aiclimb.aiclimb.workers.dev
- トップ、講師紹介、ブログ一覧、指定記事、受講資料一覧、AIニュース、診断、CSS、JSの9資産がHTTP200かつ確定版SHA256と一致。
- `/health` 200、`/admin` 303でログインへ、`/api/admin/ping` 401、`/admin/login` 200。ログインの新CSS/JS読み込みタグを確認。
- 公開HTML186件・管理HTML2件の本文と操作保持、非表示資産275件・認証等13モジュール一致、動きのテスト11件成功。
- 目視・実機確認は未実施。ブラウザ接続制限による残件であり、本番HTTP・ハッシュ検証とは区別する。
- 証跡: `.glass-release/verification.json`、`live-verification.json`、`deploy.log`。公開バンドルは`.glass-release/compiled/public-entry.js`。

本節の追加は記録のみ。公開済みアプリケーションのソースSHAは上記4576503。
