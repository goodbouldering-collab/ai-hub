# AIハブ本番 404 調査：CEO 用 Vercel Dashboard ステップ

## 状況

- 本番 https://aiclimb.vercel.app/ が **404 NOT_FOUND**
- でも `/watch/`、`/admin`、`/admin/docs`、`/lectures/` は **200 で生きている**
- GitHub `main` には正しい `site/dist/index.html` (5/13 16:38 push) が存在
- **Vercel が GitHub の最新 commit を反映していない**ことが確定済

## 調査手順（CEO Dashboard 操作・所要 5 分）

### Step 1: Vercel Dashboard を開く

1. https://vercel.com/dashboard にログイン（goodbouldering@gmail.com）
2. プロジェクト一覧から **`ai-hub`** をクリック

### Step 2: Deployments タブを見る（最重要）

上部メニュー「**Deployments**」をクリック。

**見るポイント**:

| チェック項目 | 期待値 | 異常時の意味 |
|---|---|---|
| 最上段（最新）の commit hash | `c62dcdf` または `0c446e0` | 古い hash しか出てない → **GitHub 連携が切れている** |
| 最上段の Status | `● Ready` (緑) | `● Error` (赤) → **ビルド失敗** / `● Queued` → 詰まっている |
| 最上段の時刻 | 直近 1〜2 時間以内 | 何時間も前 → **デプロイがトリガーされていない** |
| Production バッジ | 最新に付いているか | 古い deployment に付いている → **手動 promote 必要** |

**スクリーンショットを撮って本部に送ってもらえると一発で原因判明します**。

### Step 3: 最新 deployment をクリックして詳細を見る

最上段（または `c62dcdf` の deployment）をクリック → **Build Logs** タブ。

**見るポイント**:

- 赤いエラー行があるか
- "No Output Directory found" のような警告
- `site/dist` が見つからない系のメッセージ

### Step 4: Settings → Git を確認

左メニュー「**Settings**」→ 「**Git**」。

| チェック項目 | 期待値 |
|---|---|
| Connected Git Repository | `goodbouldering-collab/ai-hub` |
| Production Branch | `main` |
| Auto Deploy from Push | ✅ Enabled |
| Ignored Build Step | 空 or `git diff ...` 形式 |

### Step 5: Settings → Build & Development Settings

左メニュー「**Settings**」→ 「**Build & Development Settings**」。

| 項目 | 期待値（おそらく） |
|---|---|
| Framework Preset | `Other` |
| Build Command | （空 or オーバーライド無効） |
| Output Directory | **`site/dist`** ← ここが最も怪しい |
| Install Command | （空 or オーバーライド無効） |

**Output Directory が `site/dist` になっているか確認してほしい**。違う値が入っていたら教えてください。

---

## 想定パターン別の対処

### パターン A: Deployments に最新 commit が出ていない
→ Settings → Git → "Reconnect" を実行 / または vercel.json に dummy 変更 + commit + push で強制トリガー

### パターン B: Deployments に出ているが Status = Error
→ Build Logs を読んでエラー内容を本部に共有してもらう

### パターン C: Deployments は Ready だが Production バッジが付いていない
→ 最新 deployment の右端「⋯」→ "Promote to Production"

### パターン D: Output Directory が `site/dist` 以外
→ `site/dist` に変更 → 再デプロイ

### パターン E: 全部正常に見えるのに 404
→ Settings → Domains で `aiclimb.vercel.app` がどの deployment を指しているか確認

---

## 本部側の準備

CEO が Dashboard を見ている間、本部は以下を準備：

1. ✅ `site/dist/index.html` を commit 済（最新 `bfae728f`）
2. ✅ `daily.yml` を `site/dist/index.html` も commit back するよう修正済
3. ⏸ 上記が反映されるためには **Vercel デプロイが GitHub から正しく取得すること**が必要
4. ⏸ 原因判明次第、必要なら追加 hotfix を投入

CEO が Dashboard を見て**「画面に何が出ているか」**を教えてくれれば、最短 1 メッセージで対処手順を出します。
