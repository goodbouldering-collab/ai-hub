> ⚠️ **2026-05-17 訂正**: 本書 §0 の「hero 列は本番未適用（code:42703）」は**実機検証で誤りと判明**。`hero_*` 列は本番に存在し HTTP 200。真の問題は本番データの文字化けだった。**ヒーロー編集化は完了済み**（→ [2026-05-17-n-design-hero-cms-fix.md](2026-05-17-n-design-hero-cms-fix.md) が正）。本書はヒーロー以外のセクション本文（services/value/flow/faq 等）の新規実装計画として引き続き有効。

# N-デザイン トップページ「セクション本文」管理画面編集化 — 差分設計書

**作成日**: 2026-05-17（日）
**対象事業**: N-デザイン（`C:\VSCode\Project\N-デザイン\`）
**ステータス**: 📋 差分設計書（実装未着手）。事業リポ書き込みは [consul 鉄則](../CLAUDE.md)により **CEO 承認後**
**確定スコープ（2026-05-16 CEO 回答）**: ヒーロー＋主要テキストセクション編集 / データ層は Supabase `site_profile` + `*-data.ts` フォールバック

---

## 0. この設計書の前提（調査で確定した事実）

| 事実 | 状態 | 出典 |
|---|---|---|
| ヒーロー編集 UI・タブ・読み出し側コード | ✅ **完成済み**（2026-05-15・別セッション実装） | [hero-tab.tsx](../../N-デザイン/components/admin/tabs/hero-tab.tsx) / [use-home-data.ts](../../N-デザイン/lib/hooks/use-home-data.ts) |
| `site_profile.hero_*` 列の本番 Supabase 適用 | ❌ **未適用**（実測 `code:42703 column does not exist`）| [20260515000000_site_profile_hero.sql](../../N-デザイン/supabase/migrations/20260515000000_site_profile_hero.sql) がローカルにあるが SQL Editor 未実行 |
| 他8マイグレーション | ✅ 適用済（本番実測 200）| — |
| **セクション本文**（services/value/flow/faq/repair/difference） | ❌ **編集 UI・スキーマ・読み出し連携すべて未実装**。純粋なコード定数 | [home-content.ts](../../N-デザイン/lib/data/home-content.ts) |

→ **本件（セクション本文編集）は完全新規実装**。ただし hero と同じ「SQL ファイルを作って本番適用を忘れる」罠を**繰り返さないこと**を設計に組み込む（§6）。

---

## 1. 編集対象と非対象（確定）

| セクション | データ定数 | 編集化 | 備考 |
|---|---|---|---|
| ヒーロー | `hero-data.ts` | （別件・実装済・本番適用待ち） | 本書スコープ外。§6 で適用手順だけ言及 |
| サービス6項目 | `serviceItems` | ✅ 対象 | **Icon あり**（要マッピング層） |
| 対応範囲4群 | `repairItems` | ✅ 対象 | **Icon あり** |
| 強み4項目 | `valuePoints` | ✅ 対象 | **Icon あり** |
| 差別化6項目 | `differenceItems` | ✅ 対象 | **Icon あり** |
| 流れ6ステップ | `flowSteps` | ✅ 対象 | **Icon あり** |
| FAQ 13問 | `faqItems` | ✅ 対象 | **Icon なし**・但し §3 の SEO 整合制約あり |
| 会社プロフィール | `site_profile`（既存） | （実装済） | 本書スコープ外 |
| works / blog | Supabase | 既存 CRUD | スコープ外 |

---

## 2. 最大の技術的難所：Icon（LucideIcon）は DB に保存できない

`serviceItems` 等は `Icon: LucideIcon`（React コンポーネント参照）を持つ。これは JSON / Supabase に直列化できない。`faq.tsx` のように `services.tsx` も `service.Icon` を **JSX として直接レンダリング**している（[services.tsx:35](../../N-デザイン/components/sections/services.tsx) `<service.Icon ... />`）。

### 解決：文字列キー ↔ LucideIcon マッピング層を新設

```
lib/icon-map.ts （新規）
  import { House, Sofa, Droplets, ... } from "lucide-react";
  export const ICON_MAP = { House, Sofa, Droplets, Wrench, ... } as const;
  export type IconKey = keyof typeof ICON_MAP;
  export const resolveIcon = (key: string): LucideIcon =>
    ICON_MAP[key as IconKey] ?? House;  // 不正キーは安全なデフォルト
```

- DB / JSON には `icon: "House"`（**文字列**）で保存
- 表示時に `resolveIcon(item.icon)` で LucideIcon に変換 → `<Icon />`
- 管理画面ではアイコンを**ドロップダウン選択**（自由入力にすると不正キーで描画崩れ）。選択肢は `ICON_MAP` のキー一覧から生成
- `home-content.ts` の既存定数を「**文字列キー版**」に書き換える必要がある（`Icon: House` → `icon: "House"`）。各セクションコンポーネント（services/why-komuten/flow）も `<service.Icon>` → `<ResolvedIcon>` に修正。**これは破壊的変更なので段階移行**（§5）

---

## 3. FAQ 固有の制約：SEO 構造化データとの整合

`faqItems` は3箇所で使われ、編集化すると整合維持が必須:

| 使用箇所 | 用途 | 影響 |
|---|---|---|
| [faq.tsx:42](../../N-デザイン/components/sections/faq.tsx) | トップに先頭6件抜粋 | 表示のみ |
| [app/faq/page.tsx:47](../../N-デザイン/app/faq/page.tsx) | **`FAQPage` JSON-LD の `mainEntity`** | **SEO/LLMO**。編集が構造化データに直結 |
| [app/faq/page.tsx:64](../../N-デザイン/app/faq/page.tsx) | `groupByCategory(faqItems)` | **FAQ にカテゴリ属性が必要**。現 `faqItems` は `{q,a}` のみでカテゴリ列が無い → `groupByCategory` の実装を要確認（暗黙のカテゴリ分けロジックがある可能性） |

→ FAQ 編集スキーマは `{ q, a, category? }` を持たせる。編集後も `app/faq/page.tsx` の `FAQPage` JSON-LD が壊れないことを実装時に必ず確認（親 CLAUDE.md「ブログ記事の多重管理に注意」と同種の整合問題）。

---

## 4. データ層設計（既存二層戦略に従う）

CEO 確定どおり Supabase `site_profile` + `*-data.ts` フォールバック。hero と同じパターンで一貫させる。

### スキーマ追加（新規マイグレーション）

`supabase/migrations/20260517000000_site_profile_sections.sql`（新規）:

```sql
alter table site_profile add column if not exists sections_content jsonb default '{}'::jsonb;
-- 構造: { services:[{icon,title,description,iconClass,color,border}],
--        repairItems:[{icon,category,items:[...]}],
--        valuePoints:[{icon,title,body}],
--        differenceItems:[{icon,text}],
--        flowSteps:[{icon,step,title,body}],
--        faqItems:[{q,a,category}] }
update site_profile set sections_content = coalesce(sections_content, '{}'::jsonb) where id='main';
notify pgrst, 'reload schema';
```

- **単一 jsonb 列**にまとめる（hero が `hero_*` を平坦列にしたのと違い、セクションは配列構造が多く列数が爆発するため jsonb が適切）。`blogs.faq_items` が既に jsonb 運用なので前例あり
- `color`/`border`/`iconClass` 等の Tailwind クラス文字列も保存対象（`serviceItems` はこれらを持つ）。**ただし任意クラス文字列を DB から注入するのは XSS ではないが Tailwind purge の対象外になりビルド時に消える危険**。→ 対策：クラスは固定パレットの enum 選択にする（自由入力させない）

### 読み出し（`use-home-data.ts` 拡張）

既存 `use-home-data.ts` の `site_profile` SELECT は既に `select("*")`。戻り値に `sections` を追加し、`home-content.ts` をフォールバックに降格:

```ts
const [sections, setSections] = useState(defaultSections);  // = home-content.ts 由来
// site_profile 取得時:
if (data?.sections_content && Object.keys(data.sections_content).length)
  setSections(mergeWithDefaults(data.sections_content));  // 欠損キーは default で補完
return { works, blogPreviews, profile, hero, sections };
```

- 各セクションコンポーネント（services/faq/flow/why-komuten）を `home-content.ts` 直 import → `useHomeData().sections` 受け取りに変更（hero が `copy={hero}` を受けるのと同じ形）
- ⚠️ `faq.tsx` は client、`services.tsx` は **server component**（`"use client"` 無し）。`useHomeData` は client hook なので、**`services.tsx` を client 化するか、page.tsx でデータを渡す**設計判断が要る。hero は page.tsx 経由で `copy` を渡しているので**同じく page.tsx でまとめて渡す方式が一貫**（services を不要に client 化しない）

---

## 5. 段階移行プラン（破壊的変更を安全に）

`home-content.ts` の `Icon: House` → `icon: "House"` 化は全セクション波及。一度に変えると事故る。

| Step | 内容 | リスク |
|---|---|---|
| S1 | `lib/icon-map.ts` 新設（既存に影響なし・純追加） | なし |
| S2 | `home-content.ts` に**文字列キー版を併存追加**（`serviceItemsV2` 等）。旧定数は残す | なし（純追加） |
| S3 | 各セクションコンポーネントを V2 + `resolveIcon` 参照に切替。表示が旧と一致することをローカル実機で確認（親 feedback「描画系は実機で踏む」） | 中（要実機確認） |
| S4 | `site_profile_sections.sql` 作成 → **本番 Supabase で実行**（§6 厳守）| 中 |
| S5 | `use-home-data` で `sections_content` 優先・フォールバック実装 | 中 |
| S6 | `/admin` に「セクション本文」タブ新設（`hero-tab.tsx` を雛形に踏襲） | 低 |
| S7 | 旧定数（`serviceItems` 等 V1）削除・参照ゼロを確認 | 低（後方互換ハック禁止の親方針に従い最後に掃除） |

---

## 6. hero の二の轍を踏まないための鉄則（本設計書の核心）

hero 機能は「コード完成・SQL ファイル作成済み・**本番 Supabase 未適用**」で実質動いていなかった。同じ失敗を防ぐ:

> **マイグレーション SQL を作ったら、その場で「本番 Supabase SQL Editor で実行」までを1つのタスクとして完了させる。** ファイル作成＝完了ではない。

- S4 完了の定義 = SQL ファイル作成 **かつ** 本番で `curl .../rest/v1/site_profile?select=sections_content&limit=1` が **200** を返すこと（hero 調査で使った非破壊検証と同じ手法）
- 本番 Supabase 操作は consul 鉄則で **CEO 明示指示が必要**。実装が S4 に到達したら、CEO に「この SQL を Supabase ダッシュボードで実行してください（または `SUPABASE_ACCESS_TOKEN` 経由実行の許可をください）」と**明示的に確認**する
- **ついでに提案**: 本件着手前に、未適用の hero マイグレーション（`20260515000000_site_profile_hero.sql`）も同時に本番適用してしまうのが効率的（どちらも `site_profile` への `add column if not exists`・冪等・低リスク）。CEO 判断事項

---

## 7. 実装フェーズ（CEO 承認後）

| Phase | 内容 | 事業リポ書込 | 本番DB操作 |
|---|---|---|---|
| **P1** | S1〜S3（icon-map / V2定数併存 / コンポーネント切替 + 実機確認） | 要 CEO 承認 | なし |
| **P2** | S4（sections マイグレーション作成 **＋本番適用**）。hero 未適用分も同時適用を CEO に提案 | — | **要 CEO 明示 GO** |
| **P3** | S5〜S6（読み出し連携 + /admin タブ新設） | 要 CEO 承認 | なし |
| **P4** | S7（旧定数掃除）+ スモークテスト（`npm run test:smoke`）+ FAQ JSON-LD 整合確認 | 要 CEO 承認 | なし |

---

## 8. 結論（CEO への要点）

1. **セクション本文編集はゼロから新規実装**（hero と違いコードも無い）。最大の難所は **Icon を文字列キー化するマッピング層**と、それに伴う `home-content.ts` 全セクションの破壊的書き換え。§5 の段階移行で安全に進める
2. **FAQ は SEO 構造化データ（`FAQPage` JSON-LD）に直結**。編集化は表示だけでなく `app/faq/page.tsx` の整合維持が必須
3. **hero の教訓を制度化**：マイグレーションは「本番適用＋200検証」までやって初めて完了。本件着手時に未適用の hero SQL も同時適用するのを推奨（CEO 判断）
4. 次アクション: 本設計書を CEO がレビュー → P1 着手承認。なお **hero 本番未適用問題は本件と独立して残っている**（CEO が選択肢3を選んだため）。hero を先に直すか本件と同時かは CEO 判断

---

**最終更新**: 2026-05-17（初版・セクション本文編集の差分設計。実装未着手。hero 本番未適用問題は別件として継続）
