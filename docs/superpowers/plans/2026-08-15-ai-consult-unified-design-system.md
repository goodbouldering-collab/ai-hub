# AI相談 統合デザインシステム実装計画

> 実行方針: 専用worktreeでTDD、PC/390px実画面QA、mainへのfast-forward push、Vercel本番確認まで連続実行する。

## Task 1: 契約テストを追加する

- `tests/design-system-contract.test.mjs` を追加する。
- 共通トークン、公開参照ページ、ビルド出力、管理画面の読込契約、ナビ現在地、アクセシブル状態を検証する。
- 実装前に対象テストが失敗することを確認する。

## Task 2: Foundationsと参照ページを実装する

- `site/static/design-system/tokens.css` に意味トークンを定義する。
- `site/static/design-system/index.html` と `design-system.css` に、対象者、導線、色、文字、コンポーネント、状態、PC/390pxルール、画面別契約を実画面化する。
- 参照ページにスキップリンク、意味見出し、フォーカス、reduced motionを実装する。

## Task 3: 公開トップへ適用する

- `site/build_portal.py` が共通トークンを読み込むようにする。
- 既存のFocus系変数を意味トークンへ接続する。
- CTA階層と既存レイアウトは保持し、フォーカスと状態の共通ルールを強化する。

## Task 4: 管理4領域へ適用する

- `admin-common.css` の最終レイヤーを共通トークンへ接続する。
- Blog/Reelのlegacy変数を意味トークンへ接続する。
- Command Centerの変数を同じ意味トークンへ接続する。
- 共通管理メニューのモバイル運用項目に「デザインシステム」を追加し、現在地を示す。

## Task 5: 検証する

- デザインシステム契約テスト、全Nodeテスト、Python全テスト、TypeScript、静的ビルドを実行する。
- ローカルで公開トップ、デザイン参照、Blog、Reel、Command CenterをPC/390pxで確認する。
- 横幅超過、見出し順、ラベル、キーボードフォーカス、メニュー開閉、console errorを確認する。

## Task 6: 公開する

- scoped diffをレビューしてcommitする。
- origin/mainの更新を再確認し、fast-forward可能な状態でpushする。
- Vercelの本番デプロイ完了を確認する。
- 本番URLで公開トップ、デザイン参照、管理対象画面、共通CSS/JS、主要API境界をPC/390pxで再確認する。
