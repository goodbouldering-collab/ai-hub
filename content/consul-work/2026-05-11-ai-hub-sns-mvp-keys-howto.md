# SNS MVP — API キー取得手順書

作成: 2026-05-11  
対象: AIハブ (`c:\VSCode\Project\ai-hub`) SNS 一括投稿 MVP

---

## X (Twitter) API キー取得手順

### 所要時間

15〜30 分（アカウント審査が通っている前提）

### 前提条件

- X アカウントが Developer Portal に登録済みであること
- アカウントが電話番号認証済みであること

### 手順

1. **Developer Portal にアクセス**
   - URL: https://developer.twitter.com/en/portal/dashboard
   - 自分の X アカウントでログイン

2. **プロジェクト・アプリを作成**
   - 左サイドバー「Projects & Apps」→「Overview」→「+ Add App」
   - App 名: `ai-hub-sns` (任意)
   - 利用目的は「Making a bot」または「Building tools for myself」を選択

3. **アプリの権限設定**
   - 作成したアプリ → 「Settings」タブ
   - 「User authentication settings」→「Set up」をクリック
   - **App permissions**: `Read and write`（投稿に必要）
   - **Type of App**: `Web App, Automated App or Bot`
   - **Callback URI**: 使用しないが入力が必須のため `https://aiclimb.vercel.app/callback` などを入れる
   - **Website URL**: `https://aiclimb.vercel.app`
   - 「Save」

4. **キーを取得**
   - アプリ → 「Keys and tokens」タブ
   - **Consumer Keys** セクション:
     - `API Key` → `X_API_KEY` に設定
     - `API Key Secret` → `X_API_SECRET` に設定
   - **Authentication Tokens** セクション:
     - 「Access Token and Secret」→「Generate」をクリック
     - `Access Token` → `X_ACCESS_TOKEN` に設定
     - `Access Token Secret` → `X_ACCESS_TOKEN_SECRET` に設定
   - **重要**: 生成直後しか Secret は表示されない。必ず安全な場所に保存すること

5. **Free プランの制限**
   - 投稿: 月 500 ツイートまで（Free Tier）
   - 投稿専用: `tweet.write` スコープのみ必要
   - 読み取り: 月 1,500 リクエストまで（今回は使わない）

### Vercel に設定する環境変数

| 変数名 | 取得元 |
|---|---|
| `X_API_KEY` | Consumer Keys → API Key |
| `X_API_SECRET` | Consumer Keys → API Key Secret |
| `X_ACCESS_TOKEN` | Access Token and Secret → Access Token |
| `X_ACCESS_TOKEN_SECRET` | Access Token and Secret → Access Token Secret |

---

## Threads API キー取得手順

### 所要時間

30〜60 分（Meta アカウント審査・App Review が不要な場合は短縮可能）

### 前提条件

- Threads アカウントが存在すること
- Meta for Developers にアカウントを登録済みであること
- Threads アカウントとMeta アカウントが連携済みであること

### 手順

1. **Meta for Developers にアクセス**
   - URL: https://developers.facebook.com/
   - 「My Apps」→「Create App」

2. **アプリを作成**
   - App type: 「Consumer」または「Business」を選択
   - App Name: `ai-hub-sns` (任意)
   - Business account: 個人利用なら「Create and Use a Business Account」をスキップ可

3. **Threads API を追加**
   - アプリの Dashboard → 「Add a Product」
   - 「Threads API」を見つけて「Set up」をクリック

4. **Threads User ID を取得**
   - 取得方法 1: Threads のプロフィール URL `https://www.threads.net/@ユーザー名`
     - ブラウザの開発者ツール or `curl` で確認できる場合がある
   - 取得方法 2: Threads API 経由
     ```
     curl "https://graph.threads.net/v1.0/me?fields=id,username&access_token=<アクセストークン>"
     ```
   - 返ってくる `id` フィールドが `THREADS_USER_ID`

5. **アクセストークンを生成**
   - アプリの「Threads API」→「Generate Access Token」
   - 自分の Threads アカウントでログインして認可
   - 短期トークン（1時間）が発行される

6. **長期トークンに交換**（重要: 短期トークンは 1 時間で失効）
   ```
   curl "https://graph.threads.net/refresh_access_token?grant_type=th_refresh_token&access_token=<短期トークン>"
   ```
   - または Threads API の「Token Debugger」ページで延長
   - 長期トークンは **60日間有効**。有効期限が近くなったら再実行すること

7. **制限**
   - テキスト投稿: 500文字まで
   - レート制限: 250 投稿/24時間
   - App Review: 一般公開は不要（自分のアカウントだけなら `Development Mode` で OK）

### Vercel に設定する環境変数

| 変数名 | 取得元 |
|---|---|
| `THREADS_USER_ID` | Threads アカウントの数値ID（`/me` API で取得）|
| `THREADS_ACCESS_TOKEN` | 長期アクセストークン（60日ごとに更新必要）|

---

## Vercel 環境変数の登録方法

1. Vercel Dashboard → `ai-hub` プロジェクト → 「Settings」→「Environment Variables」
2. 上記の変数を1つずつ追加:
   - `Environment`: Production (および必要に応じて Preview)
   - `Value`: 取得したキーをそのまま貼り付け
3. 「Save」後、**Redeploy** が必要（Settings 変更は既存デプロイに自動反映されない）
   - 「Deployments」タブ → 最新デプロイ → 「Redeploy」

---

## Supabase マイグレーション実行

`portal.sns_posts` テーブルの作成が必要です。

### 手順

1. Supabase Dashboard → `zrawhzwtppmlxyhngnju` プロジェクト → 「SQL Editor」
2. 以下のファイルの内容を貼り付けて実行:
   - `c:\VSCode\Project\ai-hub\supabase\migrations\20260511_portal_sns_posts.sql`
3. エラーなく完了すれば OK

または Supabase CLI を使う場合:
```bash
supabase db push --db-url "postgresql://postgres:パスワード@db.zrawhzwtppmlxyhngnju.supabase.co:5432/postgres"
```

---

## 動作確認チェックリスト（キー投入後）

- [ ] Vercel 環境変数に `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET` を登録した
- [ ] Vercel 環境変数に `THREADS_USER_ID` / `THREADS_ACCESS_TOKEN` を登録した
- [ ] Vercel Redeploy を実行した
- [ ] Supabase `portal.sns_posts` テーブルを作成した
- [ ] `/admin/sns-post` にアクセスして「接続状態」欄に「X API: OK」「Threads API: OK」と表示される
- [ ] AI 下書き生成ボタンでテキストが生成される（`ANTHROPIC_API_KEY` が必要）
- [ ] X のチェックボックスにチェックを入れて投稿 → X のタイムラインに表示される
- [ ] Threads のチェックボックスにチェックを入れて投稿 → Threads のプロフィールに表示される
- [ ] 「投稿履歴」セクションに投稿ログが表示される（Supabase `portal.sns_posts` に記録されている）
- [ ] 未設定の SNS のチェックボックスが disabled になっている
