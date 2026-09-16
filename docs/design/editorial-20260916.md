# AI相談: 人の可能性が広がるエディトリアルデザイン

2026-09-16。地域の仕事・暮らし・学びをAIで少し自由にするサイトとして、人物、手、湖畔、紙、銀の道を重ねた新しいアートを制作した。色数を増やさず、生成りと深い緑、黒白の人物写真、細い罫線、大きな見出しで表現する。

## 実装

- 新規アート4点をヒーローと講習6カードへ配置。画像内の人物・場面は架空のコラージュであり、実際の講師・受講実績として扱わない。
- 講師本人の既存写真 `/img/speaker.webp` を、ヒーローの小さな写真、トップ講師欄、自己紹介の主画像として使用。本人の顔を生成し直していない。
- スマートフォンでは見出し、アート、サービス説明の順に表示。本人写真は紙の写真カードとして重ねる。
- `editorial.css` を共通表示層へ追加。トップ・講師紹介・公開記事・管理・ログインを揃える。
- 既存の読了表示、マウスに反応する控えめな奥行き、カルーセル操作、詳細の開閉を維持。タッチと動きを減らす設定で装飾アニメーションを停止する。
- 公開中186 HTMLの本文・見出し・順序・リンク・フォーム・inline CSS/JS・metadataを機械比較。ニュースの内容や日付、料金、申込先を変更しない。

## 画像資産

生成ツール: OpenAI built-in ImageGen。完全な指示は `editorial-20260916-prompts.json`、生成原本は `editorial-originals/art-*.png`。配信版は `site/static/design-system/studio/images/art-*.webp`。

| 画像 | 意図 | 配信容量 |
|---|---|---:|
| hero | 人の手が道を開き、地域と新しい可能性につながる | 263,700 bytes |
| learn | 人物とノートの重なりから、学びの入口を表す | 272,902 bytes |
| build | 手、鉛筆、キーボードでアイデアを形にする | 220,172 bytes |
| connect | 世代の異なる人と湖畔の街をつなぐ | 190,152 bytes |

1536×1024の原寸を維持してSharpでWebP（quality 85、effort 6）に形式変換。構図や人物の編集なし。ヒーローは高優先度、講習画像は遅延読み込み。原本合計11,705,365 bytesから配信合計946,926 bytesへ約92%削減した。

参考調査: [Adobe 2026 Creative Trends](https://business.adobe.com/jp/resources/creative-trends-report.html)、[Adobeの日本向け制作例](https://blog.adobe.com/jp/publish/2026/01/22/how-creators-leveraging-adobe-2026-creative-trends-jp-3)。人の手触り、地域性、写真と空想の組み合わせを参考に、この事業向けに新規制作した。

## 検証

- 公開baseline: Cloudflare version `955d1282-9f75-4a02-856b-ccf92034bbe5`、source `9731b48a1a0f8ee7a3ded6d11b72ee7280102aa5`。
- `deployment/editorial/baseline.json` で公開済み463資産・15runtimeモジュールを固定し、未確認のローカル生成物を混ぜない。
- `scripts/build-editorial-release.py` は新しい出力先へコピーし、デザイン適用後に全件を照合。本人写真、参照画像、冪等性、管理HTML2件、認証以外の表示差分だけであることを検証する。
- 13runtimeモジュールはバイト単位で同一。管理HTMLとログインは共通テーマのタグ・body classだけを変更。
- `node --test tests/studio-glass-motion.test.mjs`: 11件成功。
- アプリ内ブラウザで1440px PC・390px iPhoneを確認。トップ、講習、自己紹介、ニュース、管理プレビュー、ログインを目視。横はみ出しなし。公開・管理モバイルメニュー、案内フローの次質問、講習詳細の開閉も確認。
- 管理プレビューはローカルの読み取り専用。認証や公開操作を行わず、本番では未認証境界を確認する。

## 公開元と再生成

実装用の隔離worktreeからコミット・PRを作成し、CI確認後にmainへ統合する。登録公開元 `C:/Project/AI相談/work/genspark-profile-edit` をそのSHAへFFし、コミット済みソースから再生成する。元のdirtyなルートmainは操作しない。

```powershell
python scripts/build-editorial-release.py --baseline .glass-release --output .editorial-release-20260916
```

`verification.json` の `source_inputs_clean:true`、source SHA、全資産・runtimeハッシュを確認する。新管理HTMLを含むruntimeを束ね直し、登録cwd `cloudflare-runtime` から中央ガードを通した上で公開する。

```powershell
$release = 'C:/Project/AI相談/work/genspark-profile-edit/.editorial-release-20260916'
$wrangler = 'C:/Project/NOKOSU/node_modules/.bin/wrangler.cmd'
& $wrangler deploy "$release/runtime/worker/public-entry.mjs" --config wrangler-glass-build.jsonc --assets "$release/public" --dry-run --outdir "$release/compiled"
# HEAD == origin/main == PR merge SHA とソースcleanを確認してから実施
powershell -ExecutionPolicy Bypass -File C:/Project/scripts/assert-cloudflare-target.ps1 -ProjectRoot 'C:/Project/AI相談' -TargetKey default -ForDeploy
& $wrangler deploy "$release/compiled/public-entry.js" --config wrangler-profile-release.jsonc --assets "$release/public" --no-bundle --keep-vars --message "Editorial design; source $sourceSha"
```

各コマンドの終了コードを確認して進める。設定既定の旧entry/assetsを使わない。dry-run専用の `wrangler-glass-build.jsonc` は既存の `deployment/profile/package-lock.json` に対応したsanitize-htmlの解決先を設定している。前回bundleのsourcemapに含まれる依存60ソースとインストール済み内容が一致し、17パッケージのversion/resolved/integrityもlockと一致することを確認した。Vercel・DNS・secret・DB設定の変更なし。デプロイ後のversion/SHA・主要route・実画像ハッシュ・PC/iPhone画面の結果をPRへ記録する。
