# グッぼる SNS自動化 準備書

- 事業: gubble
- 状態: draft
- 正本: [gubble.md](../gubble.md), [ai-hub.md](../ai-hub.md)
- 関連ファイル: `C:\VSCode\Project\グッぼる\media\`, `C:\VSCode\Project\_shared\media-kit\`, `C:\VSCode\Project\ai-hub\api\admin\sns-post.ts`
- 次アクション: ffmpeg導入、Meta/YouTubeの認可準備、AIハブ投稿基盤の拡張設計レビュー

## 結論

グッぼるのSNS自動化は、最初から全媒体へ完全自動投稿するのではなく、次の4段階で作る。

| Phase | 対象 | 内容 | 目安 |
|---|---|---|---|
| 0 | 素材生成 | 画像、縦動画、字幕、投稿文を自動生成。投稿は手動 | 1日 |
| 1 | 承認UI | AIハブ `/admin` に「生成、確認、投稿予約、履歴」を集約 | 2-3日 |
| 2 | Meta系 | Instagram / Reels / Facebook / Threads をAPI投稿 | 1-2週 + App Review |
| 3 | YouTube | ShortsをYouTube Data APIでアップロード | 1週 + YouTube API監査 |

理由は2つ。1つ目は、Instagram / Facebook / Threads はMeta Graph系で認可、公開URL、App Reviewがボトルネックになる。2つ目は、YouTube upload はOAuthとAPI監査が必要で、事前審査なしに本番自動投稿へ進むと止まりやすい。

運用上の推奨は、最初の30投稿は「自動生成 + 人間承認 + API投稿」にする。30投稿で失敗率、文字切れ、動画の見切れ、投稿タイミングを見てから、在庫連動や定例投稿だけを自動公開に進める。

## 既存資産

### グッぼる側

`C:\VSCode\Project\グッぼる\media\` はすでにSNS素材置き場として成立している。

| 既存ファイル | 役割 |
|---|---|
| `media/brand.json` | ブランド色、表示名、背景色 |
| `media/package.json` | 画像、動画、字幕、AI画像生成のnpm scripts |
| `media/cards/*.json` | SNSカード入力 |
| `media/clips/*.mp4` | 実写素材 |
| `media/clips/captions.json` | 字幕焼き込み用 |
| `media/output/` | 生成物。gitignore済み |

既存script:

```powershell
cd C:\VSCode\Project\グッぼる\media
npm.cmd run banner
npm.cmd run topo
npm.cmd run video
npm.cmd run caption
npm.cmd run image -- --prompt "ボルダリングジムの壁、暖色照明" --name wall
npm.cmd run image-imagen -- --prompt "ボルダリングジムの壁、暖色照明" --name wall
```

PowerShellでは `npm` がExecutionPolicyで止まるため、当面は `npm.cmd` を使う。

### 共有media-kit側

`C:\VSCode\Project\_shared\media-kit\` に共有ロジックがある。

| 機能 | 現状 |
|---|---|
| SNSバナー | `@napi-rs/canvas` で X 1200x675 / 縦 1080x1920 / 正方形 1080x1080 を生成 |
| 動画変換 | `ffmpeg` で横、縦、正方形を書き出し |
| 字幕 | `ffmpeg` + ASSで縦動画へテロップ焼き込み |
| AI画像 | OpenAI `gpt-image-1` / Google Imagen 4 の2系統 |

2026-06-05時点のローカル確認:

| 項目 | 状態 |
|---|---|
| Node | `v24.15.0` |
| npm | `npm.cmd 11.12.1` は動作 |
| npm.ps1 | PowerShell実行ポリシーで停止 |
| ffmpeg | PATH上に未導入 |
| ffprobe | PATH上に未導入 |
| winget | PATH上に未導入 |

動画自動化の最初の実作業はffmpeg導入。`winget` が使える環境なら `winget install Gyan.FFmpeg`、使えない場合は手動展開または既存ポータブルツール置き場へ配置する。導入後にVS Codeを再起動し、`ffmpeg -version` / `ffprobe -version` を確認する。

### AIハブ側

AIハブにはすでにSNS投稿のMVPがある。

| 既存ファイル | 現状 |
|---|---|
| `api/_lib/sns.ts` | X + Threads のテキスト投稿クライアント |
| `api/admin/sns-post.ts` | 投稿API。現状は140文字以内、X/Threadsのみ |
| `api/admin/sns-draft.ts` | ClaudeでSNS下書き生成 |
| `api/admin/sns-history.ts` | 投稿履歴 |
| `site/static/admin/sns-post.html` | 管理画面 |
| `supabase/migrations/20260511_portal_sns_posts.sql` | `portal.sns_posts` ログ |

ただし現状テーブルは `x_status` / `threads_status` の列固定なので、Instagram / Facebook / YouTube まで広げるなら、1投稿に複数媒体をぶら下げる `portal.sns_post_targets` 方式へ拡張した方がよい。

## 生成から投稿までの標準フロー

1. 種を作る
   - 商品入荷、課題更新、イベント、カフェ、ブログ記事、カテゴリ(cate)強化記事からテーマを選ぶ。
   - 数字根拠を最低1つ入れる。例: 割引率、残数、開催日時、グレード、比較対象。

2. 投稿文を作る
   - グッぼるトーン: 異端OK、難しい用語OK、数字根拠必須。
   - 1テーマから5媒体分を生成する。
   - Instagramは説明寄り、Threadsは短文連投可、Facebookは地域・イベント寄り、Shorts/Reelsは最初2秒のフック重視。

3. 画像を作る
   - 実写写真があるならカード化。
   - 写真がないならAI画像。ただし商品そのもの、人物の実在写真、ロゴをAIで捏造しない。
   - 規格は最低3種類: 1080x1080、1080x1920、1200x675。

4. 動画を作る
   - 実写クリップがある場合: `video/export.sh` で縦・正方形へ変換し、`caption.mjs` で字幕焼き込み。
   - クリップがない場合: Remotionでカード画像、商品写真、テキストを15-45秒の縦動画にする。
   - BGMや流行音源は自動投稿では使わない。権利事故を避けるため、無音または自社管理音源だけにする。

5. 公開URLへ置く
   - Meta系APIは画像・動画の公開URLをGraph APIが取得する方式が中心。
   - Supabase StorageまたはCloudflare R2で、投稿前だけ公開可能なURLを発行する。
   - ローカル `media/output/` のファイルパスはAPI投稿に使えない。

6. 承認する
   - AIハブ `/admin` で、媒体別プレビュー、文字数、動画長、公開URL、投稿先を確認。
   - 初期30投稿は人間承認必須。

7. 投稿してログを残す
   - 成功、失敗、外部post id、エラー、生成元素材、再投稿可否をSupabaseに残す。
   - 投稿失敗時は再実行できるが、同じ媒体へ二重投稿しないように `idempotency_key` を持つ。

## 媒体別の制約

2026-06-05時点の一次情報確認。実装直前に再確認する。

| 媒体 | 投稿方式 | 必要なもの | 注意 |
|---|---|---|---|
| Instagram Feed | Instagram Content Publishing API | IG Professional account、Meta App、`instagram_content_publish`、公開画像URL | コンテナ作成後にpublish。24時間あたりの投稿上限に注意 |
| Instagram Reels | Instagram Reels Publishing API | 公開MP4 URL、IG user id、Meta権限 | Reels用の動画仕様に合わせる。公開URL必須 |
| Threads | Threads API | `threads_basic`、`threads_content_publish`、Threads user id、公開画像/動画URL | `threads` コンテナ作成後、`threads_publish` |
| Facebook Page | Pages API | Page access token、`pages_manage_posts`、`pages_read_engagement` | 事業ページ投稿。個人アカウント自動投稿ではない |
| Facebook Reels | Facebook Video/Reels API | Page id、動画アップロードセッション | start/upload/status/finishの分割フロー |
| YouTube Shorts | YouTube Data API `videos.insert` | OAuth client、`youtube.upload`、チャンネル接続、API監査 | 縦または正方形、3分以内。未検証アプリは制約が強い |

外部仕様ソース:

- Meta Postman Workspace - Instagram API: https://www.postman.com/meta/instagram/overview
- Meta Postman Workspace - Threads API: https://www.postman.com/meta/threads/overview
- Meta Postman Workspace - Facebook API: https://www.postman.com/meta/facebook/overview
- Meta Postman Workspace - Facebook Reels Publishing API: https://www.postman.com/meta/facebook/request/plp0a9n/facebook-reels-publishing-api
- YouTube Data API `videos.insert`: https://developers.google.com/youtube/v3/docs/videos/insert
- YouTube Help - three-minute Shorts: https://support.google.com/youtube/answer/15424877
- Remotion render docs: https://www.remotion.dev/docs/render

## 推奨フォーマット

| 用途 | サイズ | 動画長 | 備考 |
|---|---:|---:|---|
| Instagram Feed / Facebook画像 | 1080x1080 | - | 汎用カード |
| Reels / Shorts / Stories系 | 1080x1920 | 15-45秒から開始 | 3分以内でも、まず45秒以下 |
| X / OGP / 横長 | 1200x675 | - | 既存banner出力で対応 |
| Facebook横動画 | 1920x1080 | 15-60秒 | 必要になってから |

初期テンプレは4つで足りる。

| テンプレ | 内容 | 自動化しやすさ |
|---|---|---|
| 新課題 | グレード、核心、日時、写真/短クリップ | 高 |
| 商品入荷 | 商品名、特徴、価格/割引率、購入URL | 高 |
| イベント | 日時、対象、定員、申込導線 | 高 |
| 技術解説 | 1ムーブ、1道具、1誤解を30秒で説明 | 中 |

## DB拡張案

既存の `portal.sns_posts` はX/Threads固定列なので、媒体追加に弱い。次の形にする。

```sql
create table portal.sns_campaigns (
  id bigserial primary key,
  business_slug text not null default 'gubble',
  title text not null,
  source_type text not null,
  source_ref text,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  approved_at timestamptz,
  approved_by text
);

create table portal.sns_assets (
  id bigserial primary key,
  campaign_id bigint not null references portal.sns_campaigns(id),
  kind text not null,
  format text not null,
  storage_url text not null,
  width int,
  height int,
  duration_sec numeric,
  checksum text,
  created_at timestamptz not null default now()
);

create table portal.sns_post_targets (
  id bigserial primary key,
  campaign_id bigint not null references portal.sns_campaigns(id),
  platform text not null,
  text text not null,
  asset_id bigint references portal.sns_assets(id),
  scheduled_at timestamptz,
  published_at timestamptz,
  status text not null default 'pending',
  external_post_id text,
  external_url text,
  error text,
  idempotency_key text unique,
  created_at timestamptz not null default now()
);
```

## 環境変数チェックリスト

実値はMarkdownに書かない。

| 系統 | 変数名案 |
|---|---|
| 共通 | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_BUCKET` |
| 画像生成 | `OPENAI_API_KEY`, `GEMINI_API_KEY` |
| X既存 | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` |
| Threads | `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN` |
| Meta共通 | `META_APP_ID`, `META_APP_SECRET`, `META_BUSINESS_ID` |
| Instagram | `IG_USER_ID`, `IG_ACCESS_TOKEN` |
| Facebook | `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN` |
| YouTube | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` |
| 運用通知 | `ADMIN_USER`, `ADMIN_PASS`, `SLACK_WEBHOOK_URL` またはメール通知先 |

## 管理画面に必要な機能

| 画面/機能 | 必須度 | 内容 |
|---|---|---|
| 生成フォーム | 高 | テーマ、投稿種別、媒体、CTA、根拠数字を入力 |
| 媒体別プレビュー | 高 | 文字数、画像、動画、改行、URLを表示 |
| 素材アップロード | 高 | 既存写真/動画をSupabase Storageへ置く |
| 自動生成 | 高 | カード、AI画像、縦動画、字幕を生成 |
| 承認ボタン | 高 | 初期30投稿は必須 |
| 投稿実行 | 高 | 媒体ごとのAPI結果を記録 |
| 失敗再実行 | 中 | `idempotency_key` で二重投稿防止 |
| 投稿予約 | 中 | Vercel CronまたはGitHub Actionsで定刻投稿 |
| インサイト取得 | 低 | Meta/YouTubeの再認可後に拡張 |

## 実装順

### Step 1: ローカル素材生成を固める

- `ffmpeg` / `ffprobe` を入れる。
- `C:\VSCode\Project\グッぼる\media` で `npm.cmd run banner` を確認。
- 実写クリップから `vertical` / `square` / `horizontal` を生成できるか確認。
- `caption` を実行し、テロップが日本語で崩れないか見る。

完了条件:

- `media/output/` に `1080x1920` と `1080x1080` の動画が出る。
- 30秒以内のテスト動画が1本作れる。

### Step 2: AIハブを「投稿前ダッシュボード」にする

- 既存 `/admin/sns-post` をテキストのみから素材付きへ拡張。
- `portal.sns_campaigns` / `portal.sns_assets` / `portal.sns_post_targets` を追加。
- 生成物をSupabase Storageへアップロードし、公開URLを発行。

完了条件:

- 投稿しなくても、1キャンペーンに5媒体分のテキストと3素材を保存できる。
- 生成履歴を30件見られる。

### Step 3: ThreadsとInstagram画像投稿

- Threadsは既存 `api/_lib/sns.ts` を拡張し、画像/動画付きにする。
- InstagramはContent Publishing APIで画像投稿から始める。
- Reelsは動画URLの安定配信とエンコード確認後に追加。

完了条件:

- Threads画像投稿1件、Instagram画像投稿1件がAPIで成功。
- 失敗時のエラーがSupabaseに残る。

### Step 4: Facebook Page / Reels

- Facebook Page投稿を追加。
- Facebook Reelsはアップロードセッション型なので、画像投稿とは別クライアントにする。

完了条件:

- Facebook Pageへ画像投稿1件。
- Reelsはテスト動画1件。

### Step 5: YouTube Shorts

- OAuth clientを作り、`youtube.upload` の認可を取る。
- YouTube Data API `videos.insert` で限定公開アップロードを試す。
- YouTube API監査が必要なら、用途、保存データ、削除導線、プライバシーポリシーを準備する。

完了条件:

- 30秒の縦動画を限定公開でアップロード。
- 投稿URLと動画IDがログに残る。

## 投稿テーマの初期キュー

最初の20本はこの配分で作る。

| 種別 | 本数 | 例 |
|---|---:|---|
| 新課題 | 6 | 「今週の5級/初段、核心だけ30秒」 |
| 商品 | 6 | 「UP-MOCC 25%OFF、足型で向く人/向かない人」 |
| 技術 | 4 | 「ヒールフックが抜ける理由3つ」 |
| 店舗/カフェ | 2 | 「登った後に15分で回復する導線」 |
| イベント | 2 | 「初心者講習、親子体験、遠征前チェック」 |

媒体別に同文コピーしない。1テーマから下記へ変換する。

| 媒体 | 文章の型 |
|---|---|
| Instagram | 写真/動画の説明 + 体験価値 + CTA |
| Threads | 1主張 + 1数字 + 反論含み |
| Facebook | 地域/来店/イベント文脈 |
| Reels | 2秒フック + 3カット + 最後に店名 |
| Shorts | 1ネタ完結。45秒以下から開始 |

## 自動投稿の安全ゲート

| リスク | ゲート |
|---|---|
| 事実誤り | 価格、日時、在庫、定員は自動生成テキストに任せず、入力データから差し込む |
| 権利 | BGM、他人の映像、顔が明確な客映像は自動投稿対象外 |
| 二重投稿 | `idempotency_key` を媒体別に持つ |
| 炎上/誤解 | 初期30投稿は承認必須。商品批評は「向く/向かない」を明記 |
| API失敗 | 失敗媒体だけ再実行。全媒体再投稿しない |
| 秘密情報 | APIキーはVercel/Supabase環境変数。MarkdownやDB本文に置かない |

## Codex実装時の作業メモ

- 事業フォルダ `C:\VSCode\Project\グッぼる\` へのコード書き込みはCEO承認後。
- まずは consul/AIハブ側に設計、DB、管理画面、投稿APIを置くのが自然。
- グッぼるmediaは素材生成レイヤとして読み取り/実行し、生成物をStorageへ移す。
- 本番投稿APIは必ず確認モーダル付き。完全自動は定例テンプレが30件以上安定してから。
- 本番デプロイや事業リポpushを行った場合は、AGENTS.mdの安全ゲートと本番URL表示ルールに従う。

## 今日の未完了/ブロッカー

- ffmpeg / ffprobe / winget がPATH上にないため、動画書き出しと字幕焼き込みは未検証。
- Meta App、Instagram professional account連携、Facebook Page access token、Threads token、YouTube OAuthは未確認。
- 外部API仕様は2026-06-05時点で確認したが、実装直前に再確認が必要。
- 今回は事業リポへ書き込んでいない。グッぼる側の実装はCEO承認後に行う。
