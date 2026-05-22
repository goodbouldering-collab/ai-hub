# Notエステ トップページデザインを N-デザインのトーンに寄せる改修

日付: 2026-05-22
事業: Notエステ（`C:\VSCode\Project\Notエステ\web`）
依頼: 「Notエステのデザイン全体を N-デザインに類似させて」

## 方針（CEO 合意済み・AskUserQuestion）

- 寄せ度合い: **トーンは寄せる・業種色（エステの高級感）は残す**
- 主軸カラー: **おまかせ** → 青ではなく N-デザインのアンバー基調を継承（既存ゴールド #b8860b と地続き）
- 見出しフォント: **明朝体（Shippori Mincho）のまま維持**（エステの上品さ優先・CEO 選択）

### 調査で判明した重要点
Notエステは元々 N-デザインと同型基盤（Next.js 15 + Tailwind + Noto Sans JP + グラスモーフィズム + Reveal + Sticky CTA）。
むしろ Notエステの方が装飾は豊富。差分は「色とトーン」と「セクション見出しの作法」に集約。

## 実装（N-デザインの "作法" を移植）

1. **tailwind.config.ts**: `deep`/`deepAlt`（引き締まったダークセクション用）カラー + `tilt` シャドウ追加
2. **app/globals.css**: `.section-number`（大型番号ユーティリティ）+ `.tilt-card`（ホバー3D・prefers-reduced-motion 対応）追加
3. **components/SectionHeader.tsx 新規**: N-デザインの section-header.tsx を移植。
   - 「大型番号 → アクセント線+バッジ → 見出し → 説明」の縦リズム
   - 見出しは font-display（明朝）維持・Reveal 内包・light/dark tone 対応
4. **app/(frontend)/page.tsx**: 全15セクションの見出しを SectionHeader に統一（番号 01〜15）。
   - ハンドコースセクションを `bg-deep` のダーク背景に変更（N-デザイン流のセクションリズム）

## Codex セカンドオピニオン（/codex:rescue → codex:codex-rescue）

CLAUDE.md 自律委任ポリシー（事業フォルダのコード修正直後）に基づき発火。指摘と対応:
- ① アクセスセクションの二重 Reveal → **修正**（外側 Reveal を div 化、SectionHeader 内 Reveal に一本化）
- ② ダークセクションのコントラスト → card-glass は白背景なので可読・**誤認**（実害なし確認）
- ③ aria-hidden 大型番号の SEO/SR 影響 → **問題なし**
- ④ 番号飛び03→05 → DOM 順は 03(セミセルフ)→04(サブスク)→05(ハンド)で**正しい・誤認**。FAQ アイコンも既に HelpCircle で**誤認**
- 追加で SectionHeader(mb-12) と grid(mt-12) の余白二重を発見 → mt-12 grid 7箇所除去・mb-12 補完

## 検証
- `npm run build` 成功（安全ゲート① クリア）
- 差分に秘密情報なし（安全ゲート② クリア）

## 残課題
- サブページ（services / blog 個別等）は今回トップのみ対応。必要なら同じ SectionHeader を展開可能
- 本番デプロイ（main push）は CEO 確認待ち

2026-05-22 codex:codex-rescue 発火（Notエステ/トップ刷新のセカンドオピニオン/3点修正に反映）
