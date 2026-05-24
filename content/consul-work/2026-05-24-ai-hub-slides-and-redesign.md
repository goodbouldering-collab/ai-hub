# 2026-05-24 ぐっぼるスライド作成 → AIハブ公開 → デザイン改修

## 概要

ぐっぼる「クライミングの歴史」講習スライド（Marp）を作成し、AIハブに正本を移して公開。
編集→push で公開HTML/PDFが常に最新反映される仕組みを構築。あわせて AIハブ全体の
デザインをダーク基調維持のままグラスモーフィズム化した。事業略称: ai-hub / gubble。

## 1. スライド作成（グッぼる）

CEO 依頼「クライミングの歴史」を初心者向け講習用にスライド化。ぐっぼるトーン
（クライミング歴30年・媚びない・固有名そのまま・数字根拠）で作成。

- 形式: **Marp**（Markdown スライド）。HTML/PDF にエクスポート可能
- 構成を「年表羅列」→「謎・対立・人間ドラマ」のストーリー設計に作り直し（CEO指示）
- **第I部（世界史編）**: 1786モンブラン→種目分化→道具がブランドを生んだ
  （パタゴニア=シュイナードのクリーンクライミング転向 / ノースフェイス=北壁の名）→五輪
- **第II部（日本史・ぐっぼる編）**: 登山からの独立→城ヶ崎/小川山/瑞牆→ジム100軒未満→500軒以上
  →平山ユージ1998WC初V/楢崎智亜2017世界選手権V→ぐっぼる=文化の渡し場（3業態統合の理由）
- 各部にスライド＋動画ナレーション台本をセットで作成
- 史実（年号・創業秘話・五輪経緯）は WebSearch で裏取り、各台本末尾に出典明記
- 置き場（作成時）: `C:\VSCode\Project\グッぼる\スライド\`（原本は残置）

## 2. AIハブへ公開（正本一本化）

CEO 方針「編集を常に反映する直リンク」「AIハブにスライドも乗せて公開」に従い、
スライド正本を AIハブに移して AIハブのビルドで Marp 生成する構成に確定。

- `ai-hub/content/slides/` にスライド正本(.md)＋台本を配置（ASCIIスラッグ: climbing-history-1/2）
- `site/build_site.py` に `build_slides()` 追加: content/slides/*.md → Marp で /slides/*.html 自動生成
  - Marp 不在環境はスキップする fail-safe / Windows の npx.cmd 解決 / --no-stdin 対応
- PDF は事前生成して `site/static/slides/` から配信（CIでChromium DLを避ける）
- 参考資料ページ `content/lectures/2026-05-climbing-history.md` を追加し /slides/ へ直リンク
- `pages.yml` に Node 20 セットアップ追加
- 講習資料一覧（teaching_resources.yaml）にスライド直リンクを追加
- 公開確認: GitHub Pages で全URL HTTP 200・リンク切れなし

公開URL（GitHub Pages）:
- https://goodbouldering-collab.github.io/ai-hub/lectures/2026-05-climbing-history.html
- https://goodbouldering-collab.github.io/ai-hub/slides/climbing-history-1.html / -2.html

## 3. デザイン改修（AIハブ全ページ）

CEO 指示「並べ方・見せ方が古い。文字ベースを保ちつつインタラクティブに。
グラスモーフィズムをもっと」。現状は "Obsidian Solid"（ダーク高級ミニマル＋
ブルータリズム＝角丸0・影なし・グラデ廃止）で、この硬さが古さの主因と診断。

方針: **ダーク基調は維持し、ブルータリズムの硬さをグラスの柔らかさに転換**。

- `:root`: 影 none→ガラス影に復活、--glass-bg/border 半透明強化、
  --glass-hi/--glass-blur/--radius 追加（ダーク/ライト両対応）
- カード/ヘッダー/ドロップに 半透明背景+backdrop-blur+1px光彩ボーダー+上端ハイライト
- 角丸 6px×34箇所 → 16px に底上げ
- スクロールでふわっと出る reveal（IntersectionObserver・prefers-reduced-motion尊重）
- 文字ベースのタイポグラフィ（serif見出し/mono装飾/字間）は維持
- 対象: build_portal.py の PORTAL_CSS（正本）＋ build_site.py の CSS/CONTENT_CSS
- ローカルビルド exit 0・トップ/講習資料一覧をスクショ目視確認
- push 時 non-fast-forward（自動ジョブのcommit先行）→ 生成物stash→rebase→push で解消
- 本番反映を curl 実測で確認（glass-blur/radius/IntersectionObserver/backdrop-filter）

## 残課題・申し送り

1. **ライトテーマ未目視**: 変数は両対応で書いたがダークのみスクショ確認。要確認
2. **Node 20 非推奨**: GitHub Actions が 2026-06-02 に Node 24 強制へ。pages.yml の
   actions バージョン更新がいずれ必要（現時点は動作に影響なし）
3. **Vercel側のHTMLスライド配信**: build_site.py は GitHub Pages 経路で動く。Vercel 本番
   （ai-hub-jp.vercel.app）でも HTML スライドを出すなら Vercel ダッシュボードの
   buildCommand に Node+Marp 実行の追加が必要（未対応・継続課題）
4. **グッぼる原本**: スライド原本はグッぼる側に残置（指示どおり）。正本は AIハブに移管済み

## push 履歴（ai-hub / origin/main = 即本番デプロイ）

- スライド公開: `6c754b6..db69434`
- 講習資料リンク追加: `db69434..ecc2d2c`
- デザイン改修: `dd8fc5c..544db8b`（rebase後）

2026-05-24 codex:rescue 発火（ai-hub/Marpスライド公開ビルド実装/HTML生成成功・Windows互換は手元修正）
2026-05-24 codex:codex-rescue 発火（ai-hub/デザイン改修/サンドボックス設定で詰まりClaude直接実装に切替）
