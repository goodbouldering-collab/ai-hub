# Project全体の親共通シークレット（.env.shared）導入

- **日付**: 2026-05-28
- **対象**: 全事業（12事業）
- **目的**: VSCode/Claude Code/Codex/他CLI問わず、Project全体で**AI系APIキーを1ファイルで管理**できる仕組みを構築

## 何が変わったか

### Before（誤認識との実態）
- 親共通の `.env` 系ファイルは**存在しなかった**（CEO認識「2層構造になっている」と実態にズレ）
- 6事業に `.env.local` あり / 6事業に無し
- `ANTHROPIC_API_KEY` 行があったのは **AI診断マッチング・トラスト** の2事業のみ

### After（このセッションで構築）
- **`C:\VSCode\Project\.env.shared`** 新規作成（AI系キー集約・gitignored）
- **全12事業に `.env.shared` のハードリンク**を配置（mklink /H・Win権限不要）
- 親を編集すると全12事業に**即時反映**（同一ファイル実体を共有）
- **既存の各事業の `.env.local` は1文字も触っていない**（事業固有のSupabase/Stripe等は従来どおり）

## 2層構造（確定版）

```
C:\VSCode\Project\
├── .env.shared              ← 親共通（AI系のみ）★新規・gitignore済
├── .gitignore               ← .env.shared を明示追加
│
├── AI診断マッチング/
│   ├── .env.shared          ← ハードリンク（親と同一実体）
│   ├── .env.local           ← 事業固有キー（既存維持）
│   └── next.config.js       ← .env.shared を読むコードを追加★
├── ai-hub/.env.shared       ← ハードリンク
├── Notエステ/web/.env.shared ← ハードリンク
├── N-デザイン/.env.shared    ← ハードリンク
├── ビジネス21/.env.shared    ← ハードリンク
├── カラッと/.env.shared      ← ハードリンク
├── ClimbHero/.env.shared    ← ハードリンク
├── ファディー/.env.shared    ← ハードリンク
├── みんなのWA/.env.shared    ← ハードリンク
├── グッぼる/.env.shared      ← ハードリンク
├── トラスト/.env.shared      ← ハードリンク
└── プロギング/.env.shared    ← ハードリンク
```

### `.env.shared` に入れるキー（事業横断・dev用1本）
- `ANTHROPIC_API_KEY` — Claude
- `OPENAI_API_KEY` — GPT
- `GOOGLE_PLACES_API_KEY` — GBP照合
- `GOOGLE_PAGESPEED_API_KEY` — 速度実測

### `.env.local` に置く（事業固有・既存維持）
- `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY`（事業ごとに別プロジェクト）
- `STRIPE_*`（事業ごとに別アカウント）
- `RESEND_*`（事業ごとに別ドメイン）
- `LINE_*`（事業ごとに別Bot）

## 優先順位（重要）

Next.js 等の各事業のコードは：
1. **`.env.local`**（事業固有・最優先）
2. **`.env.shared`**（親共通・フォールバック）

つまり**事業固有が常に親共通を上書きできる**。事業ごとに別キーが必要になったら .env.local に書けばよい。

## CEOがやること（このタスク後）

1. **Anthropic Console**で Workspace `dev-shared` を作成 → キー1本発行
2. **`C:\VSCode\Project\.env.shared`** を開いて `ANTHROPIC_API_KEY=` 行にそのキーを貼る
3. 保存 → **全12事業に即時反映完了**

（任意）OpenAI / Google / Resend も同様に dev共有キーを発行して .env.shared に追加

## Next.js事業のコード変更（AI診断マッチングのみ実施・他事業は必要時に同じ手順）

`next.config.js` の冒頭に `.env.shared` を読み込むコードを追加：

```javascript
const fs = require("fs");
const path = require("path");
const sharedPath = path.join(__dirname, ".env.shared");
if (fs.existsSync(sharedPath)) {
  const lines = fs.readFileSync(sharedPath, "utf8").split(/\r?\n/);
  for (const raw of lines) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 0) continue;
    const key = line.slice(0, eq).trim();
    const val = line.slice(eq + 1).trim().replace(/^["']|["']$/g, "");
    if (key && val && !process.env[key]) {
      process.env[key] = val;
    }
  }
}
```

build 通過確認済（AI診断マッチング）。

## Vercel本番への影響

**影響なし**。`.env.shared` はローカル開発（dev）専用。Vercel本番は引き続き Project Settings の Environment Variables を使う。

## なぜハードリンクか（シンボリックリンクではなく）

Windowsでシンボリックリンク作成には管理者権限または開発者モード有効化が必要。CEO環境は管理者権限なしのため、ハードリンク（mklink /H）にフォールバック。ハードリンクは：
- ファイルに対し権限不要で作成可
- 同じiノードを指すため、親を編集すると全リンクに即時反映
- 親ファイルを削除しても各リンクは残る（独立した実体として動き続ける）= バックアップとしても機能

唯一の制約：**ファイルシステムを跨げない**（同一ボリューム内のみ）。Project全体が `C:` 配下なので問題なし。

## 検証済み

- `.env.shared` が全12事業から読める（テンプレ見出しが同一であることを確認）
- AI診断マッチング の `npm run build` 通過
- 既存6事業の `.env.local` は1文字も変更なし

## 次のステップ（CEO判断）

1. **Anthropic Workspace `dev-shared` 作成 + キー発行**（CEO作業・15分）
2. **`.env.shared` にキーを貼って保存**（CEO作業・1分）
3. **AI診断マッチングで実URL診断を通す**（私が dev サーバ再起動して画面確認）
4. （後日）他のNext.js事業にも next.config.js の同じ7行を追加するタイミングを判断

## 追記：`clients.code-workspace` の設定変更（2026-05-28 同日・CEO指示）

`.env.shared` を VSCode エクスプローラに表示・クリック1回で開く運用に変更:

```json
"explorer.excludeGitIgnore": false,        // .gitignoreで除外しているファイルもエクスプローラに表示
"workbench.editor.enablePreview": false,   // クリックで「正規タブ」として開く（プレビュー無効）
"workbench.editor.enablePreviewFromQuickOpen": false,  // Ctrl+Pからも正規タブ
"workbench.list.openMode": "singleClick"   // シングルクリック開きを明示
```

### トレードオフ（記録）

- **得**: `.env.shared` / `.env.local` 等が見える・クリック1回で開ける・タブが残る
- **失**: `.gitignore`除外の秘密ファイルが全部エクスプローラに表示される（画面共有/スクショ時要注意）・タブが増えやすい（`Ctrl+W` で閉じる運用）

### 戻したくなったら

`clients.code-workspace` の上記4キーを削除すれば VSCode デフォルト挙動に戻る。
