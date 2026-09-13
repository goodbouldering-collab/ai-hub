# Genspark自己紹介の取り込み

## 目的・編集元

- 由井辰美の以前の自己紹介を、現在の講師紹介ページのデザインに合わせて掲載する。
- 原資料: `config/profile.yaml`。記録されている出典は https://www.genspark.ai/api/code_sandbox_light/preview/598e1ca9-55a0-42ef-94b1-2c2072dee9f3 。2026-09-13の再取得はAccess deniedで失敗したため、保存済み経歴を使用。
- 今回の文章正本: `content/speaker.md` の「これまでの歩み」。現在の活動・価値観は依頼時に提供された事業背景を使用。
- 元資料の金額・順位・利用人数など、再確認できない主張は新規掲載しない。元資料は保持する。

## 表示

- 既存の講師紹介・公開実績・写真・問い合わせ導線を保持。
- プロフィールと講習の考え方の間に5項目の経歴を追加。
- 上部にページ内リンクを追加。既存の見出し・本文CSSを使用し、色・レイアウト・ブレークポイントは追加しない。
- `site/build_site.py` の `build_speaker_page()` で生成し、`cloudflare-runtime/public/speaker.html` に配置。

## 検証・公開条件

- 講師紹介のビルド成功。既存 `test_speaker_achievements.py` の2件成功。
- HTML差分は経歴本文とページ内リンクのみ。既存CSS変更なし。
- Genspark元URLの再取得、PC/iPhoneのブラウザ実画面確認は未完了。
- 正本 `cloudflare-runtime` で公開先ガードは通過。ただし既存の未コミット変更193件が公開元に残っており、デプロイ前コミット標準を満たさない。本作業では他作業をまとめてコミット・上書きしない。
- 次の作業: 既存公開元変更の統合を完了し、正本HEADと統合SHAを一致させ、画面確認後に確定SHAをデプロイ。公開先は https://aiclimb.aiclimb.workers.dev/speaker.html#career 。未公開のため完了URLとして扱わない。
