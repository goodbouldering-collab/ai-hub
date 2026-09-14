# AI相談・プロフィール公開元

2026-09-15にユーザーが、コミット済み分離フォルダーを正式公開元として登録しデプロイする変更を承認。

- 台帳正本: `C:/Project/docs/cloudflare-targets.json`
- projectRoot: `C:/Project/AI相談`
- workingDirectory: `work/genspark-profile-edit/cloudflare-runtime`
- configPath: `work/genspark-profile-edit/cloudflare-runtime/wrangler-profile-release.jsonc`
- target: `default / aiclimb / https://aiclimb.aiclimb.workers.dev`

## 現行版の保全

基準は公開中Version `4f27c998-4b43-4197-bc82-73f89489b599`、ソース `83563e3c453c7390249e471f4a3cdae18981b640` の463資産。`baseline.json` に全資産と15ランタイムモジュールのSHA256を記録。更新差分は `index.html` と `speaker.html` のみ。

`published-worker.mjs` はこの版のバンドルそのもの。SHA256 `acd95c8bb58afad658b3a756908e5ec38ac6c9614a892ef31c42a42854cfd98c` をビルドで検証し、no_bundleで無変換配信する。認証値は含まれず、既存secret bindingは `--keep-vars` で維持する。runtimeディレクトリとlockfileはその再現・比較用の記録。

元の作業ツリーの未コミットpublic/workerは入力にしない。署名済みではないため、baseline.jsonの由来を公開Version・既存の検証記録と照合する。別デプロイがあればその版を再確認してから進める。

## 公開手順

1. 作業ツリーをクリーンにし、対象ソースをGitHub mainへ統合する。
2. `python scripts/build-profile-release.py C:/Project/AI相談/cloudflare-runtime/.daily-news-release-20260914` で確定SHAから再生成。既存スナップショット全463資産のSHA不一致なら停止。
3. 生成される `.profile-release/verification.json` の変更が2資産のみであることを確認。
4. 台帳workingDirectoryから `powershell -ExecutionPolicy Bypass -File C:/Project/scripts/assert-cloudflare-target.ps1 -ProjectRoot C:/Project/AI相談 -TargetKey default -ForDeploy`。
5. 同じ場所で `wrangler deploy --config wrangler-profile-release.jsonc --keep-vars`。HEAD、main、配信注記のSHA一致を必須とする。
6. 本番のトップ、speaker、health、blog、既存記事、adminを確認し、トップ・speakerのハッシュとバージョン100%配信を記録。

今後の変更では、この公開元の生成手順を使用する。旧rootのwranglerや旧一括ビルドで現在の公開内容を上書きしない。
