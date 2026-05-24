# AIハブ 講師紹介ビジュアル — コピペ実行用プロンプト（2026-05-24）

> 既存の詳細版: `ai-hub/content/consul-work/2026-05-22-aihub-speaker-image-brief.md`（3案＋仕様の解説）
> このファイルは「**そのまま貼って生成 → URL入れるだけ**」の実行用1枚。推奨の案B（クライミング×テクノロジー融合）に絞った。

---

## ① どのツールで作るか（おすすめ順）

| ツール | 入口 | 商用利用 | 備考 |
|---|---|---|---|
| **ChatGPT (DALL-E 3 / GPT画像)** | ChatGPT Plus内「画像を作って」 | 可（権利はユーザー帰属） | 月額内・最短。下のプロンプトをそのまま貼る |
| **Nano Banana (Gemini画像)** | Gemini / Geminiアプリ | 可 | CEOが講習で推している。下のプロンプトを貼る |
| **Midjourney** | Discord / Web | 可（Pro以上） | 末尾の `--ar 4:3 --style raw --v 7` 付きで貼る |

横長 **4:3** で出す（講師セクションは左右分割レイアウト）。

---

## ② コピペするプロンプト（案B：クライミング×テクノロジー融合）

### 英語版（DALL-E / Midjourney / Nano Banana 共通・推奨）

```
Cinematic abstract artwork: textured rock surface of a bouldering wall, seen from a climber's close perspective.
The rock texture is overlaid with glowing circuit board patterns and flowing code streams, as if the stone and digital technology have fused together.
Chalk dust particles float in the air, dissolving into data particles and light fragments.
Color palette: base tones of deep charcoal and slate gray for the rock, illuminated by electric blue (#2563EB), violet (#8B5CF6), and neon pink (#EC4899) streaks of light flowing through the cracks.
Background fades into deep navy (#0A0F1C).
Mood: raw, powerful, cutting-edge, and slightly otherworldly.
No human face, no text, no logos.
Photorealistic digital art, 8K, ultra-detailed macro photography aesthetic.
Aspect ratio 4:3 landscape.
```

Midjourney の場合は末尾に追加 → `--ar 4:3 --style raw --q 2 --v 7`

### 日本語版（ChatGPT / Gemini に日本語で頼みたいとき）

```
ボルダリング壁の岩肌のクローズアップに、青(#2563EB)→紫(#8B5CF6)→ピンク(#EC4899)に光る電子回路のパターンとコードの流れが重なった、映画的で抽象的なアートを作って。
チョークの粉が空中でデータ粒子・光の破片に変わっていく。岩はダークチャコール〜スレートグレー、背景は深いネイビー(#0A0F1C)にフェード。
力強く最先端で、少し幻想的な雰囲気。
顔・文字・ロゴは一切入れない。フォトリアルなデジタルアート、8K、横長4:3。
```

### 避ける要素（プロンプトに含めない／出たら作り直す）
- 人物の顔・全身
- オレンジ・黄色・ベージュなどの暖色（サイトの禁止色）
- 明るい昼間トーン・白背景
- カラビナ・ロープ等のスポーツ器具の写実描写（ビジネス寄りにする）

---

## ③ 生成後の差し替え手順（CEO作業 → 私が実装）

1. 生成画像を保存（できれば WebP、なければ JPG/PNG。横長4:3、600px幅以上）
2. **画像の置き場所** … どちらか：
   - **A. Supabase Storage**（`ai-hub-public` バケット） → パブリックURLを取得
   - **B. リポジトリに直接置く**（`ai-hub/site/static/img/speaker-hero.webp`）→ 私がパスを通す。**外部ストレージ不要・一番楽**
3. CEO は「この画像で」と私に渡す（URL or ファイル）。あとは私が：
   - `ai-hub/content/speaker.md` の frontmatter `avatar_url:` に設定
   - `python site/build_site.py` でビルド
   - 安全ゲート通過 → `git push`（main = Vercel即本番）
   - 🌐 Deploy URL を報告

> **B案（リポに直接置く）が最短**。画像ファイルを `ai-hub/site/static/img/` に置いてくれれば、URLは `/img/speaker-hero.webp` で通る。Supabaseの設定もアップロードも不要。

---

## ④ 現状の仕組み（参考・私が確認済み）

- 未設定時は CSS アート（「由 / CLIMBER × CODER」プレースホルダ）が出る実装（`build_portal.py` の `_render_speaker_section()`）
- `avatar_url` に値が入ると `<img>` に切り替わる。**URLを入れるだけで反映**される
- 本番: https://ai-hub-jp.vercel.app （`ai-hub-jp.vercel.app` が正本・`ai-hub.vercel.app` ではない）
