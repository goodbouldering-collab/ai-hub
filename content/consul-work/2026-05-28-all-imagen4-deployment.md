# 2026-05-28 全事業 Imagen 4 (Google) 画像生成基盤配備

## 経緯

CEO 依頼：「claude code から codex を使って画像生成できるようにして」
→ 事実調査の結果：

- Codex CLI（`@openai/codex` 0.130.0）はコーディングエージェントで画像生成不可
- consul には既に `_shared/media-kit/image-gen/gen.mjs`（OpenAI gpt-image-1 / dall-e-3）が配備済み
- CEO 追加質問「image2 は」「Google Imagen 3/4 を使いたい」を経て、**Imagen 4 を OpenAI と並列で配備**する方針確定

## 実装

### 新規ファイル
- [`_shared/media-kit/image-gen/gen-imagen.mjs`](../../_shared/media-kit/image-gen/gen-imagen.mjs) — Google Imagen 4 を Gemini API（`:predict` エンドポイント）で叩く独立スクリプト。`parseArgs` を `brand.mjs` から流用し、CLI 互換性を gen.mjs と揃えた（`--prompt` / `--out` / `--name` / `--n`）。加えて `--aspect 1:1|3:4|4:3|9:16|16:9`、`--model imagen-4.0-{fast,standard,ultra}-generate-001` を追加。

### 7事業の `media/package.json` に `image-imagen` スクリプト追加
グッぼる / プロギング / ClimbHero / カラッと / Notエステ / みんなのWA / N-デザイン
全て `node ../../_shared/media-kit/image-gen/gen-imagen.mjs --out output` を呼ぶ。

### README 更新
[`_shared/media-kit/README.md`](../../_shared/media-kit/README.md) に OpenAI vs Imagen の使い分け表と料金（$0.02 / $0.04 / $0.06）追記。

## ハマったポイント

### ① CEO の「もう .env に書いてある」が事実と相違
共有キット直下にも環境変数にも `GEMINI_API_KEY` は存在せず。**入口で実体確認しないと進めない**と判断し、推測せず止めた。Google AI Studio で発行→PowerShell で `Out-File -Encoding utf8 -NoNewline` で .env 作成（PowerShell 既定 UTF-16 BOM だと Node 読めない・親 CLAUDE.md 記載どおり）。

### ② Free Tier で Imagen が叩けない
初回テストで 400 INVALID_ARGUMENT・メッセージは「Imagen 3 is only available on paid plans」だが**実態は Imagen 4 含む Imagen 系列全部が Paid 必須**。Gemini テキスト無料枠は維持されるが Imagen だけ請求アカウント有効化が要る。事前調査時の公式ドキュメントには明記されておらず、エラー初遭遇で発覚。**次回以降の新規 Google API 連携では「無料枠の対象モデル」を事前確認するチェックリスト項目に加える**。

### ③ 初回成功直後の ECONNRESET（一過性）
請求有効化直後の最初のリクエストで undici が ECONNRESET 切断。即リトライで成功（同一プロンプト・同一パラメータ）。**Google 側の課金プラン昇格直後のセッション初期化に約1〜2分要する可能性**あり。今後の運用で初回ハマったら自動 1 回リトライを `gen-imagen.mjs` に入れることも検討（ただし本番運用で再現性出るまでは入れない）。

### ④ 配備事業の git 所属が3パターン混在
- claude-workspace 追跡: プロギング（+ _shared/media-kit/）
- 独立リポ: ClimbHero / みんなのWA / N-デザイン
- 親 `.gitignore` 対象（git に乗らない）: グッぼる / カラッと / Notエステ
ローカル動作はする（gitに乗らないだけ）。後者3事業はバックアップ手段を別途検討要。

## 動作確認

```powershell
cd C:\VSCode\Project\グッぼる\media
npm run image-imagen -- --prompt "明るく自然光が入る屋内ボルダリングジム、カラフルなホールド、誰もいない、ワイドショット、写真風" --name test-gym --aspect 16:9
```

- 出力: `グッぼる/media/output/test-gym-2026-05-28T08-39-11-1.png`（1.77MB / 約1408×768px / 16:9）
- 実費: $0.02（imagen-4.0-fast-generate-001 既定）
- 品質: 天窓・カラフルホールド・ボリューム・パッドまで再現・写真風で実用品質

## 残課題

- **予算アラート未設定**: Google Cloud Billing で月額閾値アラート（推奨 $20/月）を設定して暴走防止。次セッションで CEO に提案
- **Vercel デプロイ影響なし確認は未実施**: N-デザイン・みんなのWA は main push で本番デプロイされるが、media/ は Next.js ビルドに含まれないので影響ゼロのはず。念のため次セッションで `gh run list` 確認
- **OpenAI vs Imagen 比較**: 同プロンプト・同事業で1枚ずつ生成して見比べる比較レポートは未実施（CEO 判断）

## push 状況（CLAUDE.md 2026-05-17 ルール準拠）

| リポ | コミット | 状態 |
|---|---|---|
| claude-workspace | ccbadc6 | ✅ push 済（gen-imagen.mjs + プロギング/media + README） |
| ClimbHero | 9d38875 | ✅ push 済 |
| みんなのWA | 600a872 | ✅ push 済 |
| n-design | 99be638 | ✅ push 済 |
| グッぼる/カラッと/Notエステ media/ | — | gitに乗らない（親 .gitignore 対象・ローカル配備のみ） |

## 関連

- 親 CLAUDE.md「全プロジェクト共通の教訓」に Imagen 4 配備状況を反映するか要検討（CEO 確認後）
- メモリ `codex-cannot-generate-images.md` に Imagen 配備済み旨を追記済み
