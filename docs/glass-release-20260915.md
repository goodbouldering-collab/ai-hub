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
