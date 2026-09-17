# AI相談 — Human work / Layered glass

2026-09-18。抽象的な風景を、PCを使って仕事を前へ進める写実的な人物・道具のイメージへ置き換える。地域の事業者がAIを相談し、学び、実際の仕事で確かめるサービスとのつながりを優先した。

## 画像と配置

| 素材 | 内容 | 配置 | WebP bytes |
|---|---|---|---:|
| human-hero | 事業者と相談役がPCの画面を一緒に確かめる | トップ主画像 | 123196 |
| human-learn | ノートPCとノートを使う学習 | 基本・個別講習、進め方 | 116452 |
| human-build | コードとWebアプリを確認する制作 | コーディング・伴走支援、進め方 | 122112 |
| human-connect | PCとタブレットを囲む協働 | サロン・サイト制作 | 135986 |
| human-practice | PCを操作する手元と仕事のノート | 主画像内の小写真、講師欄、自己紹介、進め方、ログイン | 125168 |

OpenAI built-in ImageGenで新規生成。1536×1024。架空の成人と作業場であり、実際の講師・受講者・講習写真ではない。本人写真は表示しない。実会場、実績サイト画面、受講資料の説明図は、それぞれの情報を伝える元の素材を維持する。

生成原本: `human-glass-originals/human-*.png`。完全な制作指示: `human-glass-20260918-prompts.json`。配信先: `site/static/design-system/studio/images/human-*.webp`。Sharp quality 86 / effort 6でWebPへ形式変換。内容を変える加工は行っていない。5枚合計622914 bytes。

## レイアウトとUX

- 自然光、木、ガラス、生成り、セージ、濃い青緑で統一する。画面内のPCと人の表情を主役にする。
- トップは12列グリッドで写真に本文パネルを重ね、さらにPCの手元写真と小さな半透明パネルを重ねる。スマートフォンでは人物写真の下辺に本文を重ねる。
- 講習カードは写真から本文が56px、スマートフォンでは48px重なる。本文・料金・詳細・予約ボタンを同じ本文面に含め、詳細が伸びても隣の操作を覆わない。
- 講師欄・自己紹介は手元写真に本文パネルを重ねる。生成人物を本人の肖像に見せない。
- 透明面は濃い文字、白い縁、14〜24pxの背景ぼかしで読みやすさを保つ。管理・記事では透明度を抑える。
- フォーカスを明示し、主要CTAは48px以上。装飾写真はaria-hidden、空alt、pointer-events:none。動きを減らす設定とタッチ操作では装飾の動きを抑える。背景ぼかし非対応時には本文面を不透明にする。

## 検証と公開

最新公開版5857da935eeca43a20ae8a5bec9398dbb855f4ccを基準に装飾し、古い見出しへ戻さない。公開186HTML、管理2HTML、ログインの本文・リンク・フォーム・スクリプトを比較する。処理の冪等性、本人写真の不使用、新画像の配置、装飾が操作を含まないことを `scripts/verify_editorial_release.py` で検証する。

実行:

```powershell
python scripts/build-editorial-release.py --baseline 'C:/Project/AI相談/work/genspark-profile-edit/.editorial-release-codex-header-20260918' --output outputs/editorial-preview-human-glass-v1
node --test tests/studio-glass-motion.test.mjs
python scripts/preview_studio_design.py --release outputs/editorial-preview-human-glass-v1 --port 8768
```

画面確認は許可済みのアプリ内ブラウザで実施。1440px・390pxで主画像、講習詳細、自己紹介、共通メニュー、案内フロー、管理・ログインの読みやすさと操作を確認する。受講申込や管理保存は実行しない。

本番は依頼分をコミットしてPR経由でmainへ統合後、中央台帳の正本へfast-forwardし、同じSHAから再生成する。デプロイガードを通したCloudflare Worker aiclimbへ配信する。`scripts/verify_editorial_live.py` で実URL・画像・CSS・canonical・管理認証の18項目を確認し、リリースフォルダ内のproduction-summary.jsonに統合SHA、PR、Cloudflare version、画面確認を保存する。

公開URL: https://aiclimb.aiclimb.workers.dev/
