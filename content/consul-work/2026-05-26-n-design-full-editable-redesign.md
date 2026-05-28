# N-デザイン 全テキスト編集化＋メニュー番号統一 再設計（Codex 実装委任用 RFC）

CEO 指示（2026-05-26）:
1. TOP だけでなく**全ページの全テキストを管理画面で編集可能**に（編集漏れを洗い出して追記）
2. **サイドメニュー（SectionNav）・ハンバーガー（header）・管理ページ**を**常に同じ番号で揃える**
3. **全ページに「戻る」＋関連一覧**がある（PageNav で対応済み・検証のみ）
4. 全体を見渡して再設計

## 現状の事実（調査済み）

### データ駆動の確立パターン
- `site_profile` テーブル（id='main'）に JSON/スカラーカラム → `lib/hooks/use-home-data.ts` で読込 → フォールバックは `lib/data/*`
- 既存編集可能: Hero / Profile / Works / Testimonials / Services / Blog / Grants
- アイコンは文字列 `iconName` で保存し、表示側で lucide マッパー変換（services が採用済み）

### 編集できないハードコード（要対応）
| セクション | データ元 | 件数 |
|---|---|---|
| Why（強み） | `home-content.ts` valuePoints / differenceItems + why-komuten.tsx 内の見出し・説明文 | 4 + 6 |
| Flow（流れ） | `home-content.ts` flowSteps | 6 |
| FAQ | `home-content.ts` faqItems | 14 |
| Location（アクセス） | location.tsx 内直書き（住所/電話/営業時間/地図） | — |
| Contact（種別） | contact.tsx 内 CONTACT_TYPES | 7 |
| PriceTable 価格行 | `config/constants.ts` PRICE_RANGES | 11 |
| 独立ページ about/access | 大半は site_profile.company_* でカバー済、見出し等の固定文言が残る | — |

### メニュー番号の現状
- SectionNav（左固定・`components/section-nav.tsx`）: 13 セクション・連番 01〜13 表示
- header（`components/header.tsx`）: 同じ 13 セクション（sectionLinks）+ pageLinks(about)。番号表示なし
- 管理タブ（`app/admin/page.tsx`）: dashboard/hero/profile/works/testimonials/services/grants/blog/contacts/account。番号なし・並び順バラバラ
- → **3 者が別々に配列を持っている。これを 1 つに集約する**

## 設計

### 設計1: セクション定義の single source 化（最重要・要件2の核心）

新規 `lib/data/site-sections.ts` を作り、番号体系の唯一の正本にする:

```ts
export type SiteSection = {
  no: number;            // 01, 02, ... 表示番号
  id: string;            // アンカー id（hero, why, ...）
  label: string;         // メニュー表示名（強み 等）
  adminTab: string;      // 対応する管理タブ key（why, flow, ...）。編集UIが無いものは null
  href: string;          // "/#hero" など
};
export const SITE_SECTIONS: SiteSection[] = [ ... 13件 ... ];
```

- SectionNav・header の sectionLinks・管理画面のタブメニューは**すべて SITE_SECTIONS を map して描画**する（ハードコード配列を撤廃）
- 管理画面のタブにも `no`（01〜）を表示し、3 者で番号が常に一致
- about 等のページリンクは別途 `PAGE_LINKS` として分離（セクションではないため番号体系外）

### 設計2: 未対応セクションの DB 化（要件1）

`site_profile` に JSON カラムを追加（既存 service_items 方式を踏襲・新テーブルを乱立させない）:

| 追加カラム | 型 | 中身 |
|---|---|---|
| why_heading / why_lead | text | Why 見出し・説明文 |
| why_value_points | jsonb | [{iconName,title,body}] 4件 |
| why_difference_items | jsonb | [{iconName,text}] 6件 |
| flow_steps | jsonb | [{iconName,step,title,body}] 6件 |
| faq_items | jsonb | [{q,a}] 14件 |
| location_* | text | 住所/電話/営業時間/地図URL（company_* と重複するものは company_* を正本にして location は参照） |
| contact_types | jsonb | [string] 7件 |
| price_ranges | jsonb | PRICE_RANGES 相当（category/scope/priceMin/priceMax/duration/note） |

- 各セクションコンポーネントは `use-home-data` 経由で DB 値を受け取り、無ければ `lib/data/*` のデフォルトにフォールバック（既存と同じ二層戦略）
- マイグレーション: `supabase/migrations/<timestamp>_section_content.sql`（ALTER TABLE site_profile ADD COLUMN ...）

### 設計3: 管理画面のタブ拡張（要件1）

`components/admin/tabs/` に新タブを追加（services-tab.tsx の作りを踏襲）:
- `why-tab.tsx` … 見出し/説明文/4強み（iconName セレクト+title+body）/6違いバッジ
- `flow-tab.tsx` … 6ステップ
- `faq-tab.tsx` … FAQ 項目（追加/削除/並べ替え）
- `location-tab.tsx` … 住所/電話/営業時間/地図
- `contact-tab.tsx` … 相談種別の編集（contacts 受信一覧の ContactsTab とは別）
- `price-tab.tsx` … 価格テーブル行
- すべて site_profile に upsert（saveProfile を拡張 or タブ別 save）
- アイコンは iconName 文字列のセレクト（候補は lucide の使用中アイコン名リストを定数化）

### 設計4: 戻る＋関連一覧（要件3）

- 前タスクで全公開ページに PageNav 配置済み（詳細=戻る+一覧 / 一覧=戻るのみ）
- 検証のみ。漏れがあれば追加

## 実装順序（Codex への指示）

1. `lib/data/site-sections.ts`（single source）を作り、SectionNav・header・管理タブメニューを全部それ参照に置換 → 3者の番号が常に一致
2. マイグレーション SQL で site_profile にカラム追加
3. `use-home-data.ts` に新フィールドの読込＋フォールバック追加
4. why/flow/faq/location/contact/price の各セクションを DB 値参照に書き換え（iconName マッパー整備）
5. 管理タブ（why/flow/faq/location/contact/price）を追加し saveProfile 拡張
6. ビルド通過確認

## 注意・制約
- **site_profile の DB 値が本番の正本**（コード編集だけでは反映されない・既知の落とし穴）。フォールバックはあくまで DB 未設定時
- iconName 方式: DB に Lucide コンポーネントは保存不可。文字列名で持ち、表示側マッパー（services の既存実装を共通化）
- 既存の編集可能セクション（Hero/Services/Profile 等）の挙動は壊さない
- commit→push、本番URL明示（https://n-design.work）
