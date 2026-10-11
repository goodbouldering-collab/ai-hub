# AI相談のヒーロー「光の輪」

最終更新: 2026-10-12。画像・実装・ローカル検証・PR統合・本番公開・本番画面確認済み。

青緑の透明なガラスの輪と小さな暖色の光で、「対話から、自分の経験と可能性がひらく」を表す。Codex built-in image generationでオリジナル1枚を新規生成した。写真・アニメ・人物・ロボット・文字は使わない。

- [原画と最終プロンプト](../assets/hero-glass-20261012/PROMPT.md)。1254×1254pxのPNGを保存。同一画像の1200px WebP（122,050 bytes）と640px（45,524 bytes）をレスポンシブ配信する。Sharpでサイズ・形式のみ変換。
- PCは見出し左・アート右。すりガラスの面と輪郭を重ね、スマートフォンはアートから見出しへ続ける。表示時の浮き上がり1.5秒と緩やかなズーム4.2秒で静止し、動きを減らす設定ではアニメーションを止める。
- 本人指定の3行見出し・メニュー選択・AI実力診断を保持。削除済みのサイト診断、旧相談写真、講習／受講資料のリンク行を復活させない。reel講座を含む7メニューとブログも保持する。
- `core/glass_hero.py` と `glass-hero.css` が描画の正本。`core/diagnosis_copy.py` から日次再生成にも適用し、共有デコレーターが新アートを旧写真へ置き換えない。公開資産の再生成は `scripts/build_glass_hero_release.py`。

## 検証・公開

基準は `.submenu-buttons-release-20261012-first`。本番トップのSHA一致を確認し、公開612資産と最新管理Workerを固定。トップHTMLだけ変更してWebP2サイズを追加し、残る611資産とWorkerの不変を機械検査する。変更しない公開資産はハードリンクで共有し、編集するトップは独立コピーを作る。

工程の証拠: `tmp/delivery/20261012-glass-hero-art.json` と同名フォルダ。公開元は中央台帳の `work/genspark-profile-edit/cloudflare-runtime`。生成物への混入を防ぐため、統合済みSHAを `core.autocrlf=false` でarchiveして再生成する。

- Python19件（診断、focused UX、editorial home、home updates）、Cloudflare7件、公開経路検査PASS。通常の共有デコレーター＋診断処理を通した再生成で画像1枚・7講座・削除済み要素・再適用の同一性を確認。
- AI相談の既存Chromeへ接続。古いタブへの再接続がタイムアウトしたため同じChromeに確認用タブを作成。PC1440px、820px、390px、320pxで画像読込・見出し・横はみ出しなしを確認。メニュー選択ダイアログが開くこと、動きを減らす設定で画像とガラス面のanimationがnoneになることを確認した。
- Node24.15.0、Python3.12、画像変換は既設Sharp。ビルド候補はトップHTMLとWebP2点のみ変更し、611資産と最新管理Workerが一致。

プレビュー: http://127.0.0.1:4099/ 。親PID43628、2026-10-14 02:09:47 JST終了予定。制作worktreeはプレビューと証拠のため保持し、停止後に固有ファイルを確認して整理する。

## 本番確認

PR #161の2チェック成功後、`6897d6c6ff93653300068687cff219877e927b1a` へ統合。コミット済み12入力をarchiveして再生成し、ブラウザ確認したプレビューとの一致と中央ForDeployガード成功を確認した。初回Cloudflare version `a5fd4be8-97de-4691-80f6-36bd52943286`。Wrangler4.90.0。登録公開元の既存変更・ステージを保持して統合した。

本番Chromeの1440px・390pxで画像とガラスの重なり、指定見出し、画像読込、横はみ出しなしを確認。メニュー選択ダイアログ、AI実力診断への移動と最初の設問、スマホメニューの表示も確認。最初の閲覧は旧キャッシュだったが、再読込後に新しい画像とスタイルを確認した。

トップ・ニュース・ブログ・既存記事・WebP2点のSHAが生成物と一致。旧記事の307転送先も同一内容、health200・管理入口303・管理API401・ログイン200を確認。トップのSHA256は `ff8297fcc391fe54aa8ad02c09c0670cef7dd0aad78906ec1f35fcbcd4165311`。公開資産614件のうち611件と管理Workerが基準から不変。今回の残件なし。

最終の配備SHA・Cloudflare version・工程検査結果は登録公開元 `tmp/delivery/20261012-glass-hero-art.json` を参照。画面証拠は同名フォルダの `live-desktop.jpg` と `live-mobile.jpg`。原画は `assets/hero-glass-20261012/original.png` に保持。

確認済みURL: https://aiclimb.aiclimb.workers.dev/
