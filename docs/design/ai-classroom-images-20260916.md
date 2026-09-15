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
- 既存のグラスデザイン操作テストも実行。
- 4枚の原画像は目視済み。PC/iPhoneのページ目視は、AI相談用ブラウザ接続の確認待ち。

## 公開手順

対象のみcommitしGitHub mainとHEADを一致させる。確定SHAから `.glass-release` を再生成し、候補の全ハッシュと比較。登録cwd `work/genspark-profile-edit/cloudflare-runtime` で中央ForDeployガードを通し、既存の `wrangler-profile-release.jsonc` に検証済みruntimeと `.glass-release/public` を明示して公開する。

本番のトップ・4画像・CSS/JS・講師・ブログ・記事・受講資料・AIニュース・health・admin・未認証APIを確認し、SHA・Version・結果を記録する。

既存Vercel運用チームのプロジェクト一覧は2026-09-16に読取確認し空。リポジトリのCloudflare配備はmanual、Vercelへの変更は行わない。
