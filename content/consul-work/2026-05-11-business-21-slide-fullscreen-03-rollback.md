# 2026-05-11/12 ビジネス21 スライド v3 ロールバック顛末

## 結論

v3「フルブリード可変レイアウト」は **PC Chrome で最大化すると画面が真っ黒になる重大不具合**を起こし、即時ロールバック。CEO 判断で**v2.0 で当面運用、スマホ横持ちの余白問題は受け入れ**。

## タイムライン (2026-05-11 〜 05-12)

| 時刻 | 出来事 |
|---|---|
| 〜 | CEO 「PC同様に横向きで画面いっぱい」依頼 |
| 1段 | overlay 化（v2.1相当）を実装、CEO 同意。ただし git にコミットしないまま v3 へ進む |
| 2段 | CEO 「フルブリード可変レイアウトに作り直す」依頼 |
| 2段 | v3 実装。container-type: size + zoom + Container Queries 採用 |
| デプロイ | コミット `1688412` を本番 push、Vercel READY |
| 報告 | CEO テスト: PC Chrome で最大化 → **画面真っ黒** |
| 修正試行 | コミット `9e5378b` で flex を absolute inset-0 に変更 → **依然真っ黒** |
| ロールバック | `git revert 9e5378b 1688412` → 本番は `de5b4e7` (中身は `22b4173` 安定版) |
| 判断 | CEO: 「このまま一旦保留 (v2.0 で運用)」 |

## 不具合の推定原因

PC Chrome のネイティブ Fullscreen API (`element.requestFullscreen()`) と以下の v3 で追加した CSS の組み合わせが矛盾を起こした可能性が高い:

1. ホスト要素 (SlideShell の root) が `position: fixed inset-0` + `requestFullscreen` で持っていかれた
2. その内側に `container-type: size` を持つ子を置き、`w-full h-full` で充填しようとした
3. ネイティブ全画面中、ブラウザは `<html>` 全体を全画面として描画するが、ホスト要素の `position: fixed` の参照系が変わり、子の `absolute inset-0` も期待した位置に来ない
4. 結果として CQ コンテナの高さが 0 になり、内部の zoom 値 (clamp や container query 解決) も失敗して非表示

実機 PC で `F` キーをローカル dev で押してから push しなかったのが致命的な失敗。 **「型チェック通過」と「Vercel ビルド成功」は実機での描画確認の代わりにならない**。

## 反省点 (memory に書く価値があるルール候補)

- **CSS の `position: fixed` + `container-type: size` + ネイティブ Fullscreen API の組み合わせは検証コストが高い**。pure CSS だけで完結すると思っても、ブラウザのフルスクリーン領域変更時に挙動が壊れる
- **フロントの大規模 CSS 変更は、必ず実機で F キー (or 該当機能) を踏んでから push する**。型チェック・ビルド成功は描画確認の代用にならない
- **作業ステップは小さく刻んで commit する**。v2.1 (overlay 化のみ) を commit せず v3 (フルブリード化) に進んだため、ロールバック地点が選べなくなり「v2.0 まで戻す」しかなくなった

## 現在の状態

- 本番: `https://business21.vercel.app` ← `de5b4e7` (内容は `22b4173` と同一)
- スマホ横持ち余白: 残存 (受け入れ済)
- PC 全画面: 正常動作 (元々の状態)

## 将来的な対応 (CEO 判断時)

選択肢を残しておく:

1. **overlay 化のみ再導入 (低リスク)**: v3 を完全に捨て、最初の overlay 化修正のみ復元。スマホ余白の 8 割は解消できる
2. **Reveal.js 移植検討**: 自作 SlideShell の限界を認め、Reveal.js / Spectacle 等に乗せ替え。デッキの移植コスト見積もり必要
3. **このまま据え置き**: 営業ツールとして必要十分なら追加投資しない

CEO の指示があったタイミングで再検討する。

## 学習価値の高い差分

```diff
- transform: scale(<computed>);   /* 全体縮小 — 必ず黒帯、レイアウト計算崩れない */
+ container-type: size;            /* CQ 起点 — 親の明示的 size 必須、Fullscreen API と衝突 */
+ zoom: <clamp>;                   /* 子要素一括スケール — 設計は綺麗だが副作用検証コスト大 */
```

特に **`container-type: size`** は便利だがブラウザ・コンテキストとの相互作用が予想しづらく、本番投入は十分な実機検証が前提になる。
