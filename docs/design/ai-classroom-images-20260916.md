# AI教室の画像差し替え

## 変更

2026-09-16。共通デザインで使う4枚を、映画的な奥行きのあるAI教室のイメージへ差し替え。実際に学ぶ大人と講師、パソコン、人とAIをつなぐ青緑・真珠色・淡い金色の光の流れを描いた。

- 保存先: `site/static/design-system/studio/images/{hero,learn,build,connect}.png`
- 生成: OpenAI built-in `image_gen`。全画像1536×1024 PNG、生成原本のまま。
- 全制作指示: [4本のプロンプト](ai-classroom-images-20260916-prompts.json)
- `core/studio_design.py` の対応する7個の画像説明も更新。文章・レイアウト・CSS・JS・操作・実際の講師写真・会場画像・実績サイト画像は維持。
- 写っている人物は生成された架空の参加者。実際の講習写真や講師本人のポートレートとして扱わない。

## 検証

直前の公開版を `.profile-release/image-refresh-baseline-20260916` に保全し、既存の `build-glass-release.py` で登録済みソースから再生成。

- 全463資産を比較。変更はPNG4枚とトップの画像説明7箇所のみ。
- トップHTMLは画像説明を戻すとバイト一致。458資産、CSS/JS、ランタイム15モジュールは変更なし。
- 4枚のPNG形式・1536×1024・生成原本とのSHA256一致を確認。
- 既存のグラスデザイン操作テスト11件が成功。
- 4枚の原画像は目視済み。PC/iPhoneのページ目視は、AI相談用ブラウザ接続の確認待ち。

## 公開手順

対象のみcommitしGitHub mainとHEADを一致させる。確定SHAから `.glass-release` を再生成し、候補の全ハッシュと比較。登録cwd `work/genspark-profile-edit/cloudflare-runtime` で中央ForDeployガードを通し、既存の `wrangler-profile-release.jsonc` に検証済みruntimeと `.glass-release/public` を明示して公開する。

本番のトップ・4画像・CSS/JS・講師・ブログ・記事・受講資料・AIニュース・health・admin・未認証APIを確認し、SHA・Version・結果を記録する。

既存Vercel運用チームのプロジェクト一覧は2026-09-16に読取確認し空。リポジトリのCloudflare配備はmanual、Vercelへの変更は行わない。

## 本番反映結果

- 公開ソース: `9731b48a1a0f8ee7a3ded6d11b72ee7280102aa5`。デプロイ直前にHEADとGitHub mainの一致、未コミット・未追跡ソースがないことを確認。
- Cloudflare Worker `aiclimb`、Version `955d1282-9f75-4a02-856b-ccf92034bbe5`。APIで100%配信を確認。
- 公開URL: https://aiclimb.aiclimb.workers.dev
- トップ・4画像・CSS/JS・講師紹介・ブログ一覧・指定記事・受講資料・AIニュースの12資産がHTTP200かつ確定版SHA256と一致。
- `/health` 200、`/admin` 303でログインへ、`/api/admin/ping` 401、`/admin/login` 200。認証処理の変更なし。
- 公開トップの画像参照9箇所を確認。画像キャッシュは `public, max-age=0, must-revalidate`。
- GitHubのCloudflare配備ガードとPagesワークフローが成功。
- [検証結果JSON](ai-classroom-images-20260916-verification.json) に画像寸法・ハッシュ・各URLの結果を保存。PC/iPhoneのページ目視は専用ブラウザ接続後の残件。

本節と検証結果JSONの追加は記録のみ。公開済み画像のソースSHAは上記9731b48。
