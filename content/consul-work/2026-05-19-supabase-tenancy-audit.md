# Supabase テナンシー監査 2026-05-19

> 作成: 2026-05-19 / 調査者: Claude Code（Codex スキャン結果を統合）
> 目的: クライアント引き継ぎ向け。「この Supabase プロジェクトが解約されると何事業が同時に止まるか」を明示する。

---

## 1. サマリ

| 項目 | 値 |
|---|---|
| 検出ユニーク Supabase プロジェクト数 | **2** |
| うち複合プロジェクト（相乗り）数 | **2**（全て複合） |
| 単独専有プロジェクト数 | **0** |
| 最多相乗り | `uffodcgcpykrdawyeekx`（**5事業**：Notエステ / N-デザイン / みんなのWA / トラスト / ファディー） |
| 2位 | `zrawhzwtppmlxyhngnju`（**2事業**：ビジネス21 / ai-hub） |

### 解約波及リスク（高い順）

| 順位 | Supabase 参照ID | 影響事業数 | 影響事業 |
|---|---|---|---|
| 1位（最危険） | `uffodcgcpykrdawyeekx` | **5事業** | Notエステ・N-デザイン・みんなのWA・トラスト・ファディー |
| 2位 | `zrawhzwtppmlxyhngnju` | **2事業** | ビジネス21・ai-hub |

---

## 2. 事業 → Supabase プロジェクト参照ID 対応表

| 事業名 | Supabase 参照ID（subdomain） | 専有/相乗り | 発見箇所（代表） |
|---|---|---|---|
| グッぼる | 未検出 | — | グッぼる/CLAUDE.md（方針記載のみ・参照IDなし） |
| プロギング | 未検出 | — | プロギング/CLAUDE.md（方針記載のみ・参照IDなし） |
| Notエステ | `uffodcgcpykrdawyeekx` | **相乗り** | Notエステ/web/DEPLOY_GUIDE.md:84、Notエステ/web/supabase/migrations/20260503000000_admin_security.sql:5 |
| N-デザイン | `uffodcgcpykrdawyeekx` | **相乗り** | N-デザイン/scripts/run-sql-mgmt-api.mjs:7、N-デザイン/package.json:14 |
| ビジネス21 | `zrawhzwtppmlxyhngnju` | **相乗り** | ビジネス21/.github/workflows/supabase-backup.yml:54、ビジネス21/DEPLOYMENT.md:90 |
| カラッと | 未検出（Supabase未使用） | — | Shopify + Cloudflare Workers/D1 構成（カラッと/CLAUDE.md・カラッと/line-crm/README.md） |
| ClimbHero | 未検出（Supabase未使用） | — | Cloudflare完全集約・「Supabaseは使わない」明記（ClimbHero/CLAUDE.md） |
| ファディー | `uffodcgcpykrdawyeekx`（推定） | **相乗り**（fadieスキーマ） | ファディー/CLAUDE.md:19（「Supabase Postgres（fadieスキーマで相乗り）」と明記） |
| みんなのWA | `uffodcgcpykrdawyeekx` | **相乗り** | みんなのWA/.env.example:9 |
| ai-hub | `zrawhzwtppmlxyhngnju` | **相乗り** | ai-hub/.env.example:10、ai-hub/supabase/migrations/20260517_ops_prompts.sql:8 |
| トラスト | `uffodcgcpykrdawyeekx` | **相乗り** | トラスト/supabase/site/APPLY_GUIDE.md:10、トラスト/supabase/home-shift/APPLY_GUIDE.md:9 |

---

## 3. 複合プロジェクトの内訳

### プロジェクト A：`uffodcgcpykrdawyeekx`（5事業相乗り）

相乗り事業: **Notエステ / N-デザイン / みんなのWA / トラスト / ファディー（推定）**

#### テーブル境界の推測

**Notエステ**
- 証跡: Notエステ/web/supabase/migrations/20260503000000_admin_security.sql:5
- Notエステ/web/migration-data/legacy-posts.json:12 ほか（legacy posts 移行データ）
- 推定テーブル: posts、admin 系

**N-デザイン**
- 証跡: N-デザイン/scripts/run-sql-mgmt-api.mjs:7（Management API 経由でスキーマ操作）
- N-デザイン/package.json:14
- migration ファイルは確認できず（スクリプト直接実行型のため境界不明確）

**みんなのWA**
- 証跡: みんなのWA/.env.example:9（NEXT_PUBLIC_SUPABASE_URL に参照ID）
- migration ファイルは未確認

**トラスト**
- 証跡: トラスト/supabase/site/APPLY_GUIDE.md:10,11,22
- トラスト/supabase/home-shift/APPLY_GUIDE.md:9,10,20,54
- 2サブシステム（site / home-shift）が同プロジェクトに接続

**ファディー（推定）**
- 証跡: ファディー/CLAUDE.md:19 に「Supabase Postgres（fadieスキーマで相乗り）」と設計意図を明記
- schema prefix `fadie` で論理分離の設計だが、同一 Supabase プロジェクト内
- 再生成中のため .env には参照IDなし（推定ステータス）

---

### プロジェクト B：`zrawhzwtppmlxyhngnju`（2事業相乗り）

相乗り事業: **ビジネス21 / ai-hub**

**ビジネス21**
- 証跡: ビジネス21/.github/workflows/supabase-backup.yml:54
- ビジネス21/DEPLOYMENT.md:90、ビジネス21/SETUP.md:49

**ai-hub**
- 証跡: ai-hub/.env.example:10
- ai-hub/supabase/migrations/20260517_ops_prompts.sql:8（ops_prompts テーブル）
- ai-hub/content/consul-work/2026-05-11-ai-hub-sns-mvp-keys-howto.md:152
- ai-hub/content/consul-work/2026-05-17-ai-hub-aiwatch-autopublish-design.md:84

---

## 4. 引き継ぎ観点での要対応事項

### 最優先：分離を検討すべき複合プロジェクト

#### `uffodcgcpykrdawyeekx`（Notエステ / N-デザイン / みんなのWA / トラスト / ファディー）

- **リスク**: この1プロジェクトが解約・障害・Free プラン pause になると 5事業が同時停止
- **特に危険**: トラスト（障害者グループホーム・シフト管理）は24時間稼働系サービス。Notエステ（商用エステ予約）と同一プロジェクト内という構造は、民間サービス障害が福祉インフラに波及するリスクを持つ
- **引き継ぎ時の説明**: 「このSupabaseプロジェクトのパスワード・課金・MFAを5社が共有しています」
- **推奨対応**:
  1. トラストを最優先で単独プロジェクトへ分離（福祉事業・法令遵守必須）
  2. 次点でみんなのWA（コミュニティ系・データ量が少なく移行コスト低）
  3. ファディーは再生成完了時に新規プロジェクトで起こす（既存移行不要）

#### `zrawhzwtppmlxyhngnju`（ビジネス21 / ai-hub）

- **リスク**: 2事業同時停止。ai-hub はポートフォリオ系で業務影響は軽微
- **ビジネス21は個人情報（外国人技能実習生）を扱う業務システム**。ai-hub（個人ポートフォリオ）と同居している点をクライアントに説明できるようにしておく
- **推奨対応**: ビジネス21を単独プロジェクトへ分離するか、少なくともテーブルにスキーマ prefix を付けて論理分離を明示する

### 台帳への明記で足りる事項

| 事業 | 状態 | 対応 |
|---|---|---|
| グッぼる / プロギング | Supabase 接続未検出 | 使用開始時に参照IDを台帳に記録するフローを設ける |
| カラッと | Shopify + Cloudflare D1（Supabase なし） | 引き継ぎ書に「Supabase を使わない事業」として明記 |
| ClimbHero | Cloudflare 完全集約（Supabase なし） | 引き継ぎ書に「Cloudflare D1 専用」として明記 |
| ファディー | 再生成中・参照ID未確定 | 再生成完了後に台帳を更新 |

---

## 5. 調査の限界・確認できなかった点

1. **グッぼる・プロギングの Supabase 参照IDが未検出**
   両フォルダとも CLAUDE.md に「Supabase 使用予定」の記述はあるが、.env や config.toml、ソースファイル内に 20 文字参照IDのリテラルが見つからなかった。未着手か、環境変数が Vercel Dashboard のみに設定されている可能性。

2. **ファディーの参照IDは「推定」**
   CLAUDE.md に「uffodcgcpykrdawyeekx に相乗り」という記述があるが、.env ファイルに参照IDの直書きがない（再生成中のため未設定）。CLAUDE.md の記述を根拠にした推定であり、Vercel/Supabase ダッシュボードでの実確認を推奨。

3. **テーブル・スキーマ境界の完全な把握が困難**
   N-デザイン・みんなのWA・ビジネス21 については migration ファイルの全量確認が未実施。同一プロジェクト内のテーブル名称や RLS 設定を確認するには Supabase Dashboard の Table Editor / SQL Editor での直接確認が必要。

4. **_archive フォルダは調査対象外**
   「uffodcgcpykrdawyeekx が _archive/fadie-v2 に出現」という既知ヒントは確認したが、現行事業フォルダではないため本レポートの本文には含めていない。_archive のデータが本番 DB に存在するかは別途確認が必要。

5. **Supabase プロジェクト名（ダッシュボード表示名）は未確認**
   参照ID uffodcgcpykrdawyeekx / zrawhzwtppmlxyhngnju が Supabase Dashboard でどのプロジェクト名として登録されているかは、https://app.supabase.com/ にログインして直接確認すること。

6. **Free プランか Pro プランかは未確認**
   課金プランにより「7日無アクセスで pause」リスクの有無が変わる。トラスト（uffodcgcpykrdawyeekx）が Free プランの場合、シフト管理システムが無アクセス7日で停止するリスクがあり、優先確認事項。

---

*本レポートは Codex（OpenAI）によるファイルスキャン結果を Claude Code が統合・整形したもの。引き継ぎの起点として使用し、Supabase Dashboard での実地確認を必ず追加すること。*

---

2026-05-19 codex:codex-rescue 発火（全事業/Supabaseテナンシー横断スキャン・入口判定で5ファイル以上横断のため着手前にサブエージェント委任/複合2件・最危険uffodcgcpykrdawyeekx 5事業相乗りを検出）
