# Dependabot脆弱性修正 実装計画

> **実行日:** 2026-08-22
> **対象:** `goodbouldering-collab/ai-hub` の未解決Dependabotアラート42件

## 目的

重複アラートを5つの依存更新単位にまとめ、1件ずつ更新・テスト・コミットする。最後に全体テスト、本番ビルド、Vercel本番反映、GitHub上のアラート再確認まで行う。

## Global Constraints

- 最新の `origin/main` から作った隔離worktreeだけを変更し、元のdirtyなmain checkoutには触れない。
- 更新単位は次の順序で適用し、各単位を別コミットにする。
  1. `media/output/myreel/2026-08-10-ai-experience-3d-reality/requirements.txt` の Pillow
  2. `media/output/myreel/2026-08-06-ai-work-design-future/requirements.txt` の Pillow
  3. `package-lock.json` の form-data
  4. `package-lock.json` の ws
  5. `package-lock.json` の js-yaml
- Pillowは `12.3.0`、form-dataは `4.0.6`、wsは `8.21.3`、js-yamlは3系の脆弱性解消版 `3.15.1` へ更新する。
- 既存Dependabot PR #40、#41、#42の差分を再利用し、同じ目的の別PRは作らない。
- 各更新後に対象テストと依存監査を実行する。テストが生成する `site/dist/**` 等の無関係な差分はコミットしない。
- 依存更新以外のアプリ仕様、UI、本文、公開データは変更しない。
- 最終完了条件は、Python/Node全テスト、型検査、依存監査、本番ビルドが成功し、Vercel本番がReady、GitHubの該当Dependabotアラートが解消済みであること。

## Task 1: 隔離環境と変更前基準を確立する

**Files:** 変更なし

1. Node 20以上とPython環境を確認する。
2. `npm.cmd ci` でlockfileどおりにNode依存を再現する。
3. Python仮想環境へ `requirements.txt` を導入し、`python -m pip check` を通す。
4. `node_modules\.bin\tsc.cmd -p tsconfig.json` を実行する。
5. `node --test tests/*.test.mjs bridge/bridge.test.mjs` と `npm.cmd run test:market-compass` を実行する。
6. `python -m unittest discover -s tests -p "test_*.py"` を実行する。
7. `npm.cmd audit --json` で変更前の脆弱性を記録する。
8. テスト生成差分を復元し、worktreeが計画書以外cleanであることを確認する。

## Task 2: 2026-08-10リールのPillowを更新する

**Files:**
- Modify: `media/output/myreel/2026-08-10-ai-experience-3d-reality/requirements.txt`

1. `Pillow==11.3.0` を `Pillow==12.3.0` に変更する。
2. 仮想環境へ対象requirementsを導入し、`python -m pip check` を通す。
3. 同ディレクトリの `test_build_reel.py` だけを実行する。
4. 一時ディレクトリへ `create_frame(0, BEATS[0])` を実行し、生成画像が `1080x1920`・RGBであることを確認する。
5. 変更が1行だけであることを確認し、個別コミットする。

## Task 3: 2026-08-06リールのPillowを更新する

**Files:**
- Modify: `media/output/myreel/2026-08-06-ai-work-design-future/requirements.txt`

1. `Pillow==11.3.0` を `Pillow==12.3.0` に変更する。
2. 仮想環境へ対象requirementsを導入し、`python -m pip check` を通す。
3. 同ディレクトリの `test_build_reel.py` だけを実行する。
4. 一時ディレクトリへ `create_frame(0, BEATS[0])` を実行し、生成画像が `1080x1920`・RGBであることを確認する。
5. 変更が1行だけであることを確認し、個別コミットする。

## Task 4: form-dataを更新する

**Files:**
- Modify: `package-lock.json`

1. Dependabot PR #41と同じlockfile差分で form-dataを `4.0.6` に更新する。
2. `npm.cmd ci` でlockfileを再現する。
3. Node全テスト、TypeScript型検査、`npm.cmd audit --json` を実行する。
4. form-dataの該当アラートが監査結果から消えたことを確認し、個別コミットする。

## Task 5: wsを更新する

**Files:**
- Modify: `package-lock.json`

1. Dependabot PR #42と同じlockfile差分で wsを `8.21.3` に更新する。
2. `npm.cmd ci` でlockfileを再現する。
3. Node全テスト、TypeScript型検査、`npm.cmd audit --json` を実行する。
4. wsの該当アラートが監査結果から消えたことを確認し、個別コミットする。

## Task 6: js-yamlを更新する

**Files:**
- Modify: `package-lock.json`

1. `gray-matter` 配下の許容範囲を保ったまま、js-yamlを `3.15.1` へlockする。
2. `npm.cmd ci` でlockfileを再現する。
3. Node全テスト、TypeScript型検査、`npm.cmd audit` と `npm.cmd audit --omit=dev` を実行する。
4. npm監査が0件であることを確認し、個別コミットする。

## Task 7: 全体検証と本番反映

**Files:** 依存更新以外の生成差分は残さない

1. `python -m unittest discover -s tests -p "test_*.py"` を再実行する。
2. Node全テスト、market-compassテスト、TypeScript型検査を再実行する。
3. `python site/build_site.py` とVercelローカルビルドを実行する。
4. `git diff --check`、コミット一覧、変更ファイル一覧をレビューする。
5. 全体コードレビューを行い、問題があれば修正・再検証する。
6. `main` へ反映してpushし、Vercel本番デプロイがReadyになるまで確認する。
7. 本番URLの主要ページ/APIを確認する。
8. GitHub APIでDependabotアラートと既存PRの状態を再確認する。
