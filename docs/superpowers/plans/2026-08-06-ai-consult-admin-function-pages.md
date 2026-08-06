# Feature Implementation Plan

> Execute this plan with the `superpowers:executing-plans` skill (inline) or the `superpowers:subagent-driven-development` skill (delegated), preserving the accepted design specification.

## Goal

AI相談の管理機能を、管理入口からそれぞれ独立したURLへ到達できる状態として固定する。`/admin` は集計・全体状況を表示しない作業入口とし、ブログの7工程、リール、SNS投稿、SNS分析、AI相談、OPSを共通メニューで往復できるようにする。

## Architecture

- `/admin` は `api/admin/index.ts` が認証ミドルウェア `withAdmin` を通して `site/static/admin/hub.html` を返す。
- 管理画面の共通ヘッダーは `site/static/admin/admin-menu.js`、共通スタイルは `site/static/admin/admin-common.css` に集約する。
- URLから工程を判定するブログ管理画面は `site/static/admin/blog.html` と `/admin/blog/:section` のrewriteで提供し、工程間の下書きは既存の `sessionStorage` に限定する。
- `vercel.json` が各公開URLを既存の認証済みAPIハンドラーにrewriteし、`/admin/docs` は `/ops` にredirectする。
- 今回のベースブランチには承認済み挙動を実装済みのため、最初に回帰契約テストで実態を固定する。テストで差分が出た場合だけ、該当する最小のソースを直す。

## Tech Stack

- Vercel Serverless Functions / TypeScript
- 静的HTML・CSS・JavaScript
- Python `unittest`
- Vercel CLI とブラウザ検証

## Global Constraints

- 管理画面は `withAdmin` を通る既存の認証境界を維持する。認証情報・顧客情報を追加保存または表示しない。
- 「恋愛相談」への名称変更・ページ追加はしない。正式名称はAI相談のままとする。
- `/admin` に全体状況、横断ダッシュボード、集計値、監視値を戻さない。保守用の `/admin/status` は既存互換のまま残しても、共通メニューと入口カードには載せない。
- 顧客への送信、SNSへの投稿、決済、外部サービスの書き込みは実行しない。
- PC幅と390px幅で、共通メニュー、リンク、横スクロール、画像読み込みを確認する。
- 既存の公開ページ・既存URL・D1データには変更を加えない。

## File Structure

```text
api/admin/
  index.ts                                     # 必要時のみ: /admin が hub.html を返す入口
site/static/admin/
  hub.html                                     # 必要時のみ: 作業入口カードと全体状況非表示
  admin-menu.js                                # 必要時のみ: 共通メニューの独立URL
  blog.html                                    # 必要時のみ: ブログ7工程のURL切替とsessionStorage
vercel.json                                    # 必要時のみ: 独立URLのrewrite・/admin/docs redirect
docs/superpowers/plans/
  2026-08-06-ai-consult-admin-function-pages.md
```

## Implementation Steps

### 1. 実ルーティングを基準に管理導線を検証する

**Files:**
- Verify: `api/admin/index.ts`, `site/static/admin/hub.html`, `site/static/admin/admin-menu.js`, `site/static/admin/blog.html`, `vercel.json`

1. `api/admin/index.ts` が `withAdmin` を通し、`hub.html` を返すことを確認する。旧来の `index.html` を入口に戻さない。
2. ログイン済みブラウザで `/admin` を開き、作業入口カードと共通メニューに、ブログ・リール・SNS投稿・SNS分析・AI相談・OPS・公開ページ・ログアウトがあることを確認する。
3. `/admin/blog` と `status`、`settings`、`articles`、`generate`、`editor`、`publish` の6サブパスを直接開き、URLごとに該当工程の見出しが表示されることを確認する。
4. `/admin/apps/reel/`、`/admin/sns-post`、`/admin/gubble-sns`、`/admin/chat`、`/ops` を直接開き、管理メニューを維持したまま目的の画面が表示されることを確認する。
5. `/admin/status` が共通メニューと入口カードに出ないこと、`/admin/docs` と `/admin/docs/` が `/ops` へ一時redirectされることを確認する。
6. 390px幅でメニューを開閉し、全リンクに到達でき、横スクロールが発生しないことを確認する。

### 2. 契約違反がある場合だけ、最小の画面・ルーティング修正を行う

**Files (only if the matching test fails):**
- Modify: `api/admin/index.ts`
- Modify: `site/static/admin/hub.html`
- Modify: `site/static/admin/admin-menu.js`
- Modify: `site/static/admin/blog.html`
- Modify: `vercel.json`

1. 実ルーティング確認で `/admin` の入口が旧モノリシックHTMLを返していた場合、`api/admin/index.ts` を `hub.html` のみを返すように修正し、`withAdmin` は削除しない。
2. 共通メニューのURLが不足している、または `/admin/status` を含んでいる場合、`admin-menu.js` の `items` だけを修正する。各ページ固有のヘッダーを複製しない。
3. 入口カードに集計または全体状況が残る場合、`hub.html` から該当UI・リンクを削除し、既存の直接作業リンクを残す。
4. ブログ工程URLが欠ける場合、`blog.html` のパス解決と表示切替を補正し、入力中データの保持先は `sessionStorage` のままにする。
5. URLが404または認証されない場合だけ、`vercel.json` の既存rewriteを補正する。新しい公開APIや認証回避rewriteを追加しない。
6. 変更のたびに既存の全Pythonテスト、TypeScript型検査、実ルーティング確認を実行し、すべて成功するまで進める。

### 3. リポジトリの回帰検証と静的品質確認を行う

**Files:**
- Verify: `api/admin/index.ts`, `site/static/admin/hub.html`, `site/static/admin/admin-menu.js`, `site/static/admin/blog.html`, `vercel.json`

1. `python -m unittest discover -s tests -p 'test_*.py'` を実行する。
2. `npx.cmd tsc --noEmit` を実行してTypeScriptの型確認をする。
3. プロジェクト規則どおり `npm.cmd test` を実行する。現状 `package.json` に `test` スクリプトがないため、失敗する場合は、その事実を結果として記録し、テスト実行機構を無断で変更しない。
4. `git diff --check` を実行して不要な空白・改行エラーがないことを確認する。
5. `git diff -- <target files>` を確認し、承認範囲外の公開ページ・データ・認証設定が変わっていないことを確認する。

### 4. ローカルで認証済み導線と画面を確認する

**Files:**
- Verify: `site/static/admin/hub.html`, `site/static/admin/admin-menu.js`, `site/static/admin/admin-common.css`, `site/static/admin/blog.html`

1. ローカルサーバーを既存の安全な起動方法で起動し、ログイン済みブラウザセッションを再利用する。認証情報を表示・収集しない。
2. PC幅で `/admin` を開き、全体状況・横断集計がないこと、各作業カードと共通メニューが直接URLへ遷移することを確認する。
3. `/admin/blog` と6つのブログサブパスを開き、各URLが同じ管理画面の該当工程を初期表示することを確認する。
4. `/admin/apps/reel/`、`/admin/sns-post`、`/admin/gubble-sns`、`/admin/chat`、`/ops` を確認し、共通メニューと認証境界が維持されることを確認する。
5. 390px幅でメニューを開閉し、すべてのリンクに到達でき、横スクロールがなく、操作対象が隠れないことを確認する。

### 5. commit・push・本番保存後の到達性を確認する

**Files:**
- Verify deployed versions of all files above

1. 検証済み差分だけを `git status` と `git diff` で最終確認する。
2. 明確なコミットメッセージでcommitし、現在の作業ブランチをpushする。
3. リポジトリの通常のデプロイ手順で、同じcommitをVercel本番 `https://ai-hub-jp.vercel.app` に反映する。環境変数の変更や認証情報の出力はしない。
4. 本番で `/admin`、ブログ7URL、リール、SNS投稿、SNS分析、AI相談、OPSの主要到達性を確認する。認証画面が表示される経路は、認証保護されていることを成功条件とする。
5. 本番の公開トップページに回帰がないこと、代表画像が200であることを確認する。実行司令室専用APIは、AI相談の検証対象に含めない。
6. 報告では、ローカル検証済み・commit/push済み・本番反映済みを分けて記載し、未実行項目があれば理由を明記する。

## Verification Checklist

- `python -m unittest discover -s tests -p 'test_*.py'`
- `npx.cmd tsc --noEmit`
- `npm.cmd test`（スクリプト未定義なら、その結果を記録）
- `git diff --check`
- PC幅と390px幅のブラウザ確認
- Vercel本番の認証境界・主要管理URL・公開トップ・代表画像の確認

## Self-Review

- 設計書に定義した全URL、共通メニュー、ブログ7工程、全体状況を入口に戻さない条件を計画に含めた。
- 既存実装が設計を満たす場合に重複改修しない判断と、差分が出た場合の編集対象を明記した。
- 静的文字列だけを検査するテストは追加せず、認証済み実ルーティングとブラウザ表示で管理導線を確認する方針にした。
- 顧客データ、外部投稿、決済、認証回避を追加しない制約を各工程に反映した。
- 未確定の実装指示を含めていない。
