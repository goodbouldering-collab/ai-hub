# Render / Cloudflare 撤退「ゆっくり版」ロードマップ（2026-05-12）

## CEO 判断（2026-05-12 確定）

| 項目 | 判断 |
|---|---|
| Cloudflare 撤退の動機 | **管理プラットフォームを減らしたい・コンソール多すぎてしんどい** |
| Render 破棄 | **今すぐは消さない・消せる状態だけ整えておく** |
| ClimbHero MAU | **10未満（実質誰も見ていない）** |
| ClimbHero 将来 | **復活させたい気持ちは残っている** |
| ClimbHero スタンス | **シナリオ A'（冷凍保存付き廃止）をゆっくり進める** |

**意味**: 「いつでも削除ボタンを押せる」状態に持っていくことが今のゴール。実際の削除は CEO のタイミング次第。

---

# Phase 0: 「いつでも消せる」状態を作る（即時 Δ 1 週間）

## 0-1. Render（今すぐ・3 分で完了可能）

### CEO 用手順カード

```
URL:   https://dashboard.render.com/
時間:  3分
影響:  ゼロ（本番サービス 0・課金 0）
復旧:  Vercel に同コードあり・必要なら数分で再構築可
```

**手順**:
1. ログイン（goodbouldering@gmail.com）
2. 左メニュー「Services」→ 残存サービス（あれば）「Settings」→ 最下部「Delete Service」
3. 「Account Settings」→ 「Billing」→ プランが Free か確認
4. 「Account Settings」→ 「Profile」最下部「Delete Account」
5. メールアドレス入力 → 確定 → 確認メールのリンククリック

**やる時期**: CEO の任意のタイミング（今日でも 3 ヶ月後でも影響なし）

## 0-2. Cloudflare 棚卸し（本部側で先に把握する）

CEO が破棄判断するときに「これだけ動いてた」と一発で見えるよう、本部で全アセット一覧を作る。

**必要な情報**（CEO に Cloudflare Dashboard で確認してもらう or `wrangler` ログイン取得）:
- Workers 一覧（実は 4 本以上動いている可能性）
- D1 一覧（`webapp-production` = ClimbHero 専用、`fadyhikone-production` = ファディー旧専用と確定済 / 2026-05-13）
- KV 一覧
- R2 バケット一覧
- DNS Zone 一覧（管理しているドメイン）
- Email Routing 設定
- WAF / Rate Limit ルール

→ **次回 CEO セッション時に Cloudflare Dashboard スクショ依頼 or `wrangler login` を CEO 端末で実施**

---

# Phase 1: ClimbHero 冷凍保存（CEO の手が空いたとき・1〜2 週間）

## 1-1. データ救出（4〜8h）

```bash
# D1 全テーブルダンプ（Cloudflare Workers から）
cd C:\VSCode\Project\ClimbHero
wrangler d1 export webapp-production --output=consul/work/_archive/climb-hero-d1-2026-05-12.sql

# R2 バケット中身（有効化されていれば）
wrangler r2 object list UPLOADS
# （ファイルがあれば rclone で Supabase Storage へ）
```

→ ダンプファイルは **`c:\VSCode\Project\consul\work\_archive\`** に保管（git LFS 検討）

## 1-2. プロンプト・コード資産の抽出（2〜4h）

`src/index.tsx`（6,800 行）から AI 解析部分だけ切り出す:
- 動画メタデータ抽出プロンプト → AIハブの `/lectures/` に流用可
- 多言語翻訳プロンプト → AIハブ運用で活用
- 動画分類タグ生成ロジック → 将来の復活時に再利用

→ **AIハブの `content/prompts/climb-hero-archive/`** に保存

## 1-3. GitHub アーカイブ化（30 分）

```bash
cd C:\VSCode\Project\ClimbHero
# README に「冬眠中・復活可能」と明記
echo "# ClimbHero - HIBERNATING (since 2026-XX-XX)" > README.md
git add README.md && git commit -m "chore: mark as hibernating"
git push

# GitHub Web UI で Settings → 最下部「Archive this repository」
```

## 1-4. 冬眠ページ設置（2〜4h）

`project-02ceb497.pages.dev` を **静的 1 ページ**に置き換え:

```html
<!DOCTYPE html>
<html>
<head><title>ClimbHero — Currently Hibernating</title></head>
<body>
  <h1>ClimbHero is hibernating 🧗‍♂️</h1>
  <p>This climbing video aggregation service is on pause as we focus on other projects.</p>
  <p>Will return when the time is right.</p>
  <p><a href="https://goodbouldering.com">→ Visit our climbing gym</a></p>
  <p><a href="https://ai-hub-jp.vercel.app">→ See our other projects</a></p>
</body>
</html>
```

→ Cloudflare Pages の元プロジェクトを残しつつ、`src/index.tsx` を上記静的 HTML に置き換える PR

## 1-5. AIハブの 10 事業カードに「冬眠中」バッジ表示（30 分）

`config/businesses.yaml` の ClimbHero エントリに `status: hibernating` を追加し、
`build_portal.py` で「冬眠中」バッジを表示するよう調整。

---

# Phase 2: ファディー旧 Cloudflare クリーンアップ（CEO 任意・30 分）

ファディーは既に再生成方針確定（Vercel + Supabase 構成）。旧 Cloudflare アセットは廃棄予定。

**2026-05-13 訂正**: 以前 consul に「`webapp-production` (`2faec3c4-...`) もファディー旧資産」と記録されていたが、`ファディー\fadyhikone\wrangler.jsonc` を直接読んで実体確認した結果**誤記録と判明**。`webapp-production` は **ClimbHero 専用**の D1 / Worker。
→ ファディー旧の実資産は **`fadyhikone-production` のみ**。`webapp-production` への言及を本ロードマップから削除。

```bash
# ファディー\fadyhikone\ 配下で実行
wrangler delete fadyhikone-production           # Worker 削除
wrangler d1 delete fadyhikone-production        # D1 削除（ID: 3c41910c-1b96-47ad-99e7-604df7428bdb）
```

**注意**: ClimbHero の `webapp-production` (`2faec3c4-115c-434f-9144-af1380440b7c`) は **Phase 1 の冷凍保存対象**であり、Phase 2 では **絶対に触らない**。

---

# Phase 3: LINE Webhook 4 本の Vercel 移行（1〜2 ヶ月・段階的）

| 順 | プロジェクト | Worker | 移行先 | 工数 |
|---|---|---|---|---|
| 1 | カラット | `karatto-line-crm` | Vercel API Route | 1日 |
| 2 | ぐっぼる | `line-harness-goodbouldering` | Vercel API Route | 0.5日 |
| 3 | notエステ | `line-harness-notesthe` | Vercel API Route | 0.5日 |
| 4 | ファディー旧 | `fadyhikone-production` | （Phase 2 で削除済） | - |

**各案件の手順**:
1. Vercel に `/api/webhook/line/<事業名>` を新設・既存 Worker のロジックを TypeScript で移植
2. ローカルで動作確認 → Preview Deploy → CEO 動作確認
3. LINE Developer Console で Webhook URL を Cloudflare → Vercel に切替
4. 本番 LINE で動作確認（実際にメッセージ送って返信が来るか）
5. 1 週間問題なければ Cloudflare Worker 削除

**注意**: 移行中は LINE 接続が一時的に不安定になる可能性。**事業ごとに切り替えタイミングを CEO 確認**

---

# Phase 4: DNS 移行（Phase 3 並行可・1 週間）

## 移行対象ドメイン候補（要 Phase 0-2 棚卸し確認）

| ドメイン | 現状 DNS | 切替先候補 |
|---|---|---|
| `minanowa.com` | Cloudflare | Vercel DNS |
| `karatto.life` | 不明 | Vercel DNS |
| `goodbouldering.com` | カラーミー直 or Cloudflare | カラーミー直のままでよい |
| その他 | 不明 | - |

**手順（ドメインごと）**:
1. Vercel Dashboard でドメイン追加 → nameserver 情報取得
2. ドメインレジストラ側で nameserver 変更（Cloudflare → Vercel）
3. 伝播待ち（最大 48h）
4. 疎通確認

**注意**: 切り替え忘れたドメインは **完全アクセス不能**。Phase 0-2 の棚卸しで取りこぼし防止が最優先。

---

# Phase 5: Cloudflare アカウント削除（最終ステップ・3 分）

Phase 0〜4 すべて完了後:

1. Cloudflare Dashboard で残全 Workers / KV / R2 / D1 / Email Routing / Zone を削除
2. Members → Profile → 最下部「Delete Account」
3. 確認メールに従い完全削除

---

# 全体スケジュール感（「ゆっくり版」）

| 期間 | アクション |
|---|---|
| **〜1 週間以内** | Phase 0（Render 手順カード渡し済 + Cloudflare 棚卸し） |
| **1 ヶ月目** | Phase 1（ClimbHero 冷凍保存） |
| **2 ヶ月目** | Phase 2（ファディー旧クリーンアップ）+ Phase 3 開始（LINE Webhook 1〜2 件） |
| **3 ヶ月目** | Phase 3 完了 + Phase 4（DNS 移行） |
| **4 ヶ月目** | Phase 5（Cloudflare アカウント削除） |

→ **2026-09 までに Cloudflare 完全撤退**を目標とする「ゆっくりロードマップ」

CEO のリソース次第で 3〜6 ヶ月の幅で柔軟に動かす。

---

# 次のアクション

- **本日中**: 本ロードマップを CEO に提示・承認確認
- **CEO がやる気になったとき**: Phase 0-1（Render 削除）から着手
- **Phase 0-2 のために**: 次セッションで Cloudflare 棚卸しを最優先（CEO 端末で `wrangler login` or Dashboard スクショ依頼）

## 注意：「冷凍保存付き廃止」の補足

「ClimbHero を将来復活させたい」CEO 意思に対して:
- ✅ コード（GitHub アーカイブ）・データ（D1 ダンプ）・プロンプト（AIハブ移植）の3点セットで保全
- ✅ ドメイン (`project-02ceb497.pages.dev`) は冬眠ページで生かす（SEO 残存）
- ✅ AIハブで「冬眠中」バッジ表示で意思可視化
- ⚠️ 復活時は **D1 → Supabase Postgres へのデータ流し込み** + **Vercel + Supabase で再実装**（Cloudflare に戻すのは推奨しない・親 CLAUDE.md 集約方針に反する）
