# 2026-05-22 AIハブ TOP をエージェント主導でシンプル化

## CEO 依頼
「TOPはシンプルにエージェントが作り直したものを検証して再度作り直して。エージェントが中心」
→ developer エージェントに新TOPを設計・実装させ、Claude が検証して仕上げる方式。

ai-hub commit `739e4cc`。本番 https://ai-hub-jp.vercel.app/ 反映・検証済み。

## 進め方
1. `build_portal.py`（2030行）を `build_portal.py.bak-20260522-0021` にバックアップ（`.gitignore` に `*.bak-*` 追加でcommit除外）
2. consul の **developer サブエージェント**に「申込み導線に絞った6セクション構成」を指示して再設計・実装させた
3. Claude が成果物を検証（trust but verify）

## エージェント成果物の検証結果（Claude による独立確認）

| 検証項目 | 結果 |
|---|---|
| セクション数 13→6 | ✅ top / packages / flow / speaker / faq / contact |
| Python構文・ビルド | ✅ `python site/build_portal.py` 成功 |
| HTML内JS構文 | ✅ node --check OK |
| 診断モーダル・ダークモード・PACKAGES3カード維持 | ✅ 全て残存 |
| 全画像 status200 | ✅（既存流用・新規追加なし） |
| iPhone390 はみ出し | ✅ scrollW===docW===390 |
| エージェント指摘の404リスク(portfolio/lectures) | ⚠️ 杞憂。本番200・ローカルにも存在を確認 |
| stats-strip がHTMLに1個残存 | ⚠️ 調査の結果、これは講師紹介(speaker)内の実績数字で別物。top-level STATS は正しく削除済み |

→ エージェント報告はおおむね正確。404リスクと stats-strip 残存は私が実地検証して**実害なし**と確認。手直し不要だった。

## 最終構成（6セクション）
1. **HERO**: 業務まるごと、AIに任せる。+ タイプライター + 受講プランCTA
2. **PACKAGES**: AI個別相談 / 講習会 / 伴走パック 3カード（画像付き）+ 60秒診断 + 補助金注記
3. **FLOW**: ご依頼の4ステップ
4. **SPEAKER**: 講師紹介1ブロック（実績数字込み・詳細は speaker.html へ）
5. **FAQ**: 4問アコーディオン
6. **CONTACT**: mailto + 実績/講習資料/自分ポータルの3リンクバー

## 削った/縮小
- 完全削除: STATS(top-level) / WORK GALLERY / SERVICES6カード / パララックスバンド / 事業ポートフォリオ全カード(biz-grid)
- 縮小: LECTURES常時展開 → リンクバーに統合、FAQ 5→4問

## 設計判断
- 関数定義（`_render_gallery` 等）は**残し**、`main()` の呼び出しだけ削る安全な変更（-67/+29行）。将来戻したくなったら呼び出しを足すだけ。
- 直近の作業（画像増量・パララックス）と方向性が逆（足す→引く）だが、CEO の「シンプルに」が最新意図。盛り込んだ資産はコードに眠っているので復活は容易。

## 委任ログ
2026-05-22 Agent(developer) 発火（ai-hub / TOP再設計シンプル化 / 成果は概ね正確・Claude検証で実害なしと確認し採用）。
Codex 委任ではなく consul の developer サブエージェント。エージェント中心という CEO 指定に沿った。
