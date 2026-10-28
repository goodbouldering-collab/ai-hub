# サイト診断とPlaces検索の参考順位

最終更新: 2026-10-28。店舗の検索露出を確認したい事業者向け。

サイトから店舗名・地域・業種を抽出する。候補をGoogle Mapsで開き、所在地と名称が合う店舗を選ぶ。そのPlace IDを「地域＋業種」の関連度順検索で照合し、取得時点の参考位置を表示する。Google検索のローカルパックやGoogle Maps画面のMEO順位ではない。取得件数に対象がなければ順位未確認とし、圏外順位やゼロを作らない。

## 無料の範囲と残件

- Text Search (New)のFieldMaskは `places.id,places.attributions,nextPageToken` に固定。無料のText Search Essentials (IDs Only)のみ。店舗名・住所・評価・口コミ・座標の有料フィールドやPlace Detailsは呼ばない。有料SKUへの切替なし。
- 2026-10-28確認のGoogle公式価格表ではIDs Onlyは無料・回数無制限。ただしGoogle Cloudの課金アカウント有効化とPlaces API (New)用キーは必要。レート上限は別に存在する。
- 候補は最大5件・1リクエスト。参考順位は最大3ページ・60件。結果は継続保存せず、現在地も取得しない。複数店舗は利用者に選択させる。
- 既存Worker `aiclimb` のsecret一覧に `GOOGLE_PLACES_API_KEY` は未登録。Google実測は未確認。UIは準備中表示、通常のサイト診断は利用できる。

## 接続手順

1. AI相談で利用する既存Google Cloudプロジェクトを照合。他事業のキーを流用しない。課金設定の新設、規約同意、新規キーは本人の操作・承認境界を守る。
2. Places API (New)用キーにAPI制限を設定し、利用量・上限を確認。ブラウザ制限キーをサーバーへ転用しない。
3. 中央台帳のworkingDirectoryでForDeployガード後、`wrangler secret put GOOGLE_PLACES_API_KEY --config wrangler-profile-release.jsonc` の対話入力に本人が入力。チャット・引数・Gitへキーを置かない。
4. GET `/api/meo-places` の `configured:true` は存在確認だけ。実店舗をMapsで照合し、候補検索→選択→参考順位を本番検証して接続完了。エラー時に有料フィールドへ切り替えない。

## 実装・検証・復旧

- `api/_lib/meo-places.mjs`: 店舗推定とGoogle ID検索。`deployment/meo-diagnosis/worker.mjs`: 2つの公開診断API以外を既存admin-workspace Workerへ委譲。本番で503だった診断APIを今回復旧。
- 既存Node版の解析・採点を再利用。Cloudflareで非対応のDNS lookup/HTTP pinningを使わず、DNS検証・各リダイレクト検証・本文上限・締切付きの公開fetchに適合。利用者のCookie/Authやprivate bindingsは転送しない。呼出し制限はisolateごと20回/10分で、グローバル上限保証ではない。
- `npm run verify:meo`、`npm --prefix cloudflare-runtime test`、`node .github/scripts/check-cloudflare-deployment.mjs`。新しいActions・定期処理なし。
- `scripts/build_meo_release.mjs <baseline/public> <new-output>` は登録公開元の `.codex-update-release-20261028/public` 781資産を全ハッシュ照合し、診断の3資産変更＋meo.mjs追加だけを許可。778資産を保持。Worker bundleもcommitし、統合SHAから再生成・照合後、正本workingDirectoryからguard→deployする。
- 復旧は対象変更をrevert PRで統合し、そのSHAと直前baselineをguard後に配備。キー撤回だけならPlacesは準備中へ戻る。実行担当はこの診断チャット、定期処理なし。
- Node 24.15.0 / Wrangler 4.127.1。27 API/解析テスト＋既存7件成功。実workerdでグッぼるHTML（EUC-JP）から日本語名・地域・ボルダリングを抽出。IABで390px表示・入力・準備中を確認。参考順位3番目と条件変更時の消去は明示したテストデータのUI検証でありGoogle実測ではない。
- Pythonの診断ページ既存13テストは10件成功、ホーム配置に関する3件が失敗。同じ13件を変更前のorigin/mainでも実行し、同じ3件の失敗・追加の回帰0を確認（`tmp/python-regression.json`）。公開ホームはハッシュ一致で保持し、この作業では古いホーム配置テストを変更していない。
- ローカル4457の親PID47412・期限2026-11-01 20:38:06 JST。テスト専用4458は親PID44608・期限20:40:52 JST。再起動等では保持保証なし。
- 画面は既存の青・白と入力部品を継承し、SEOスコアの次に店舗情報を配置。「参考順位」「検索語」「日時」を併記。別ページや地図UIの新設は不要と判断。
- 計測準備票 `D:/Project/docs/analytics-readiness/projects/02-AI相談.md` を確認。GA4/GSC・タグ・DNSの変更なし。
- 公開実績の正本: 登録公開元 `tmp/delivery/20261028-places-meo-diagnosis.json`。キー接続は別の残件として維持。

## 公式根拠

- https://developers.google.com/maps/documentation/places/web-service/text-search
- https://developers.google.com/maps/billing-and-pricing/pricing
- https://developers.google.com/maps/documentation/places/web-service/usage-and-billing
- https://developers.google.com/maps/documentation/places/web-service/policies
- https://developers.cloudflare.com/workers/runtime-apis/nodejs/dns/
- https://developers.cloudflare.com/workers/runtime-apis/nodejs/http/
