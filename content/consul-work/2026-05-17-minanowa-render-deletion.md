# みんなのWA Render Starter 完全削除 — 実行手順書

**作成日**: 2026-05-17（日）
**指示**: CEO「みんなのWAの Render 削除も実行」
**ステータス**: ✅ **完了**（2026-05-17 CEO が Render ダッシュボードで delete 実行 → Claude が本番巻き添えなし実測確認 → 記録3ファイル更新済）

---

## なぜ Claude が実削除できないか

- Render の delete は Render ダッシュボード or Render API のみ。Claude には `RENDER_API_KEY` も Render ログイン情報もない（御社の秘密情報4系統に Render 認証は存在しない＝[secrets-inventory](2026-05-17-secrets-inventory.md) で確認済み）
- みんなのWA は事業フォルダ＝[consul 鉄則3](../CLAUDE.md) のインフラ操作に該当
- 削除は**不可逆**（設定・環境変数・デプロイ履歴が完全消滅。suspend と違い復旧不可）

→ 役割分担：**Claude が安全性検証＋手順書＋削除後の記録更新**を担い、**実 delete は CEO がダッシュボードで実行**。

## 安全性検証（2026-05-17 実測・削除して問題ないことの根拠）

| 項目 | 結果 |
|---|---|
| `minanowa.com` 本番 | ✅ 200 正常（Cloudflare DNS → Vercel・実コンテンツ396KB配信） |
| `minanowa.vercel.app` | ✅ 200 正常（Server=Vercel） |
| Render の本番関与 | ❌ なし（2026-04-30 09:06 suspend 済・本番未使用） |
| 削除条件「Vercel 安定運用1〜2週間」 | ✅ クリア（移行 2026-04-30 → 本日 2026-05-17 = **17日間**安定） |
| ローカル復旧手段 | ✅ `server.js`（旧Express）がローカル/復旧用に残置・Render なしでも復旧可能 |

**結論: Render 削除に技術的ブロッカーなし。** Vercel 単独で17日間正常稼働、Render は suspend 済みで本番に無関与、削除条件も充足。

## CEO 実行手順（Render ダッシュボード・所要1〜2分）

1. https://dashboard.render.com/ にログイン
2. みんなのWA の Render サービス（Starter プラン・2026-04-30 に suspend したもの）を開く
3. **Settings タブ最下部 → 「Delete Service」**（または「Delete Web Service」）をクリック
4. 確認ダイアログにサービス名を入力して削除確定
5. 削除完了後、Claude に「みんなのWA Render 削除完了」と一言伝える

> 💡 削除前の保険（任意）: Settings の Environment Variables を一度スクショ/コピーしておくと、万一の再構築時に楽。ただし本番は Vercel に完全移行済みなので実用上は不要。

## 削除完了後に Claude が更新するファイル（CEO の完了報告後に実施）

1. `consul/minanowa.md` L33: 「2026-04-30 09:06 suspend、完全削除は様子見」→「**2026-05-17 完全削除済**」
2. `consul/minanowa.md` L47: 「Render Starter の完全削除（…確認後）」のタスク行を削除（完了済みのため）
3. 親 `C:\VSCode\Project\CLAUDE.md` 計画表 #5 みんなのWA 状態: 「Render は同日 suspend／完全削除は様子見」→「**Render 完全削除済（2026-05-17）**」
4. `consul/work/2026-05-17-secrets-inventory.md` 過去検討記録に1行追記（Render 認証はそもそも保管庫に無かった旨は既出なので追記不要、削除完了の事実のみ）

→ 親 CLAUDE.md は別リポ `claude-workspace`。consul 鉄則5（共有基盤変更は CEO 指示必須）に基づき、本手順書での更新は今回の CEO 指示「Render 削除も実行」に紐づく記録更新として実施する。
