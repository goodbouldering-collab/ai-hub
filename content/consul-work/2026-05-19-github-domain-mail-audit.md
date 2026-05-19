# GitHub / ドメイン / メール転送 テナンシー監査レポート

**調査日**: 2026-05-19
**調査者**: Claude Code + Codex (read-only)
**情報源**: 各事業フォルダの .git/config, CLAUDE.md, *.md, .env.example, consul/ 事業情報ファイル, CI workflows

---

## 1. サマリ — 単一障害点（危険度順）

| 順位 | 障害点 | 影響事業数 | 概要 |
|---|---|---|---|
| 🔴 1 | **GitHub 単一アカウント goodbouldering-collab** | 8+ 事業 | 全リポジトリが1つのアカウント/Orgに集約。アカウント停止・パスワード漏洩・規約違反で全事業のソースコード・CI・デプロイが同時停止 |
| 🔴 2 | **個人 Gmail goodbouldering@gmail.com への問い合わせ集約** | 4事業確認済・7+推定 | 開発者個人 Gmail が受信窓口。引き継ぎ後にアクセス権がなくなると問い合わせが不達になる |
| 🟠 3 | **ドメイン/DNS 管理者が非明示** | 独自ドメイン保有全事業（推定8事業） | goodbouldering.com / n-design.work / minanowa.com 等のレジストラ・管理者がリポからは特定不可。誰が更新料を払っているか不明 |
| 🟠 4 | **Vercel・Cloudflare アカウントの単一人格依存** | 全Vercel/CF事業（推定9事業） | 同一人物がすべてのダッシュボードを管理。引き継ぎ者への権限移譲手続きが未整備 |
| 🟡 5 | **CI クロスリポ依存（CONSUL_REPO_PAT）** | ai-hub 対 consul（2事業） | sync-consul-docs.yml が CONSUL_REPO_PAT で consul リポを clone/push。PAT 失効 = 同期停止（過去3週間遅延の実績あり） |

---

## 2. レイヤー1：GitHub 所有権

### 2-1. 事業 → GitHub リポジトリ 対応表

| 事業 | リモート URL | リポジトリ名 | git 管理状況 |
|---|---|---|---|
| グッぼる | 未確認（.git なし） | — | git 管理外（カラーミーショップ上で運用） |
| プロギング | 未確認（.git なし） | — | git 管理外（カラーミーショップ上で運用） |
| Notエステ | https://github.com/goodbouldering-collab/notesthe.git | notesthe | web/ サブディレクトリに .git あり |
| N-デザイン | https://github.com/goodbouldering-collab/n-design.git | n-design | .git あり |
| ビジネス21 | https://github.com/goodbouldering-collab/business21-kanri.git | business21-kanri | .git あり |
| カラッと | 未確認 | — | Shopify テーマ管理の可能性あり・要確認 |
| ClimbHero | https://github.com/goodbouldering-collab/ClimbHero.git（CLAUDE.md より推定） | ClimbHero | .git あり |
| ファディー | 未確認 | — | 再生成中のため未確定・要確認 |
| みんなのWA | https://github.com/goodbouldering-collab/minanowa.git（CI設定より推定） | minanowa | .git あり |
| ai-hub | https://github.com/goodbouldering-collab/ai-hub.git | ai-hub | .git あり |
| トラスト | https://github.com/goodbouldering-collab/trust.git（CLAUDE.md より推定） | trust | .git あり |
| consul | https://github.com/goodbouldering-collab/consul.git | consul | .git あり（本リポ） |

**情報源**: 各フォルダ .git/config の remote.origin.url、各 CLAUDE.md の GitHub URL 記述

### 2-2. goodbouldering-collab の正体（個人 / Organization）

**リポから判定不可・要 GitHub ダッシュボード確認**

リポから確認できた事実:
- 全リポの remote origin が https://github.com/goodbouldering-collab/ 配下に集中
- consul CLAUDE.md に git user: goodbouldering-collab として記載
- メール goodbouldering@gmail.com（由井辰美）が開発者として全事業に対応
- CODEOWNERS ファイルは確認されていない
- GitHub Organization 特有の org レベル設定ファイルは発見されていない

**推定**: 個人アカウント goodbouldering-collab として運用している可能性が高い（Org であれば通常メンバー管理ファイルが存在する）。ただし GitHub の Web UI / API でしか確定できない。

### 2-3. リポ間依存（CI クロスリポ参照）

| ワークフロー | ホストリポ | 依存先リポ | 依存内容 | 認証 |
|---|---|---|---|---|
| ai-hub/.github/workflows/sync-consul-docs.yml | ai-hub | goodbouldering-collab/consul | consul のドキュメントを ai-hub に同期（git clone / push） | CONSUL_REPO_PAT（GitHub Secret） |

**情報源**: C:/VSCode/Project/ai-hub/.github/workflows/sync-consul-docs.yml

**リスク**: CONSUL_REPO_PAT が失効すると ai-hub の同期 CI が無言で失敗する（過去に約3週間の遅延実績あり）。

---

## 3. レイヤー2：独自ドメイン

### 3-1. 事業 → ドメイン → ホスティング 対応表

| 事業 | 本番ドメイン | ホスティング | DNS/レジストラ手がかり |
|---|---|---|---|
| グッぼる | goodbouldering.com | カラーミーショップ | リポから判定不可・要レジストラ確認 |
| プロギング | plogging.jp（推定） | カラーミーショップ | リポから判定不可・要レジストラ確認 |
| Notエステ | notesthe.com | Vercel（notesthe.vercel.app） | Cloudflare DNS 管理の可能性あり（CLAUDE.md 記述） |
| N-デザイン | n-design.work | Vercel（n-design-lemon.vercel.app） | リポから判定不可・要レジストラ確認 |
| ビジネス21 | 不明（business21-kanri.vercel.app が確認済） | Vercel | 独自ドメイン有無・リポから判定不可 |
| カラッと | karatto.life（CLAUDE.md より） | Shopify + Cloudflare Workers | Cloudflare DNS 管理の可能性あり |
| ClimbHero | リポから判定不可 | Cloudflare Pages/Workers（CLAUDE.md 記述） | Cloudflare DNS 管理の可能性あり |
| ファディー | 未設定（再生成中） | Vercel（予定） | — |
| みんなのWA | minanowa.com | Vercel（2026-04-30 移行済） | リポから判定不可・要レジストラ確認 |
| ai-hub | ai-hub-jp.vercel.app（本番正本） | Vercel | vercel.app サブドメインのみ（独自ドメイン未設定） |
| トラスト | trustagent2015.com（consul/トラスト.md より） | Vercel | リポから判定不可・要レジストラ確認 |
| consul | — | — | 公開サイトなし（経営本部リポ） |

**情報源**: 各事業 CLAUDE.md の本番 URL 記述、consul/ 各事業情報ファイル、CLAUDE.md 集約マイグレーション計画表

### 3-2. 独自ドメイン有無の分類

**独自ドメインあり（確認または推定）**:
- goodbouldering.com（グッぼる）
- plogging.jp（プロギング・推定）
- notesthe.com（Notエステ）
- n-design.work（N-デザイン）
- karatto.life（カラッと）
- minanowa.com（みんなのWA）
- trustagent2015.com（トラスト）
- ビジネス21（独自ドメイン名は要 Vercel ダッシュボード確認）

**vercel.app サブドメインのみ / 独自ドメイン未設定**:
- ai-hub（ai-hub-jp.vercel.app が本番正本）
- ファディー（再生成中・未設定）

**不明（要ダッシュボード確認）**:
- ClimbHero（Cloudflare 集約だがドメイン名リポから特定不可）

---

## 4. レイヤー3：メール転送 / 送受信

### 4-1. 事業 → 受信アドレス → 送信サービス 対応表

| 事業 | 問い合わせ受信アドレス | 送信サービス | 個人Gmail依存 |
|---|---|---|---|
| グッぼる | goodbouldering@gmail.com（CLAUDE.md） | 不明 | YES（確認済） |
| プロギング | 不明（リポ未確認） | 不明 | リポから判定不可 |
| Notエステ | 不明（.env.example に変数あり・値は未確認） | Resend 使用の可能性（RESEND 系キーあり） | 要確認 |
| N-デザイン | 不明（constants.ts 未確認） | 不明 | リポから判定不可 |
| ビジネス21 | goodbouldering@gmail.com（SPEC.md / CLAUDE.md より） | 不明 | YES（確認済） |
| カラッと | 不明 | 不明 | リポから判定不可 |
| ClimbHero | 不明（CLAUDE.md に問い合わせ先記述なし） | 不明 | リポから判定不可 |
| ファディー | 不明（再生成中） | 不明 | リポから判定不可 |
| みんなのWA | 不明（minanowa.com のフォーム通知先） | 不明 | 要確認 |
| ai-hub | goodbouldering@gmail.com（ai-hub.md より） | GitHub Actions（通知） | YES（確認済） |
| トラスト | 不明（LINE Bot 通知 + 管理者メール） | Resend 使用の可能性（.env.example に RESEND 系キー） | 要確認 |
| consul | goodbouldering@gmail.com（CLAUDE.md） | — | YES（本部連絡先） |

**情報源**: 各 CLAUDE.md、consul 事業情報ファイル、.env.example（値なし・キー名のみ）

### 4-2. goodbouldering@gmail.com 集約が確認された事業

**確認済（リポに直接記述あり）**:
1. グッぼる — CLAUDE.md 連絡先
2. ビジネス21 — SPEC.md / CLAUDE.md 通知先
3. ai-hub — ai-hub.md 連絡先
4. consul — CLAUDE.md オーナー連絡先（由井辰美）

**要確認（断定不可）**:
- Notエステ、みんなのWA、トラスト — .env の ADMIN_EMAIL 等の変数の実値
- プロギング、N-デザイン、カラッと、ClimbHero、ファディー — 情報不足

---

## 5. 引き継ぎ観点での要対応事項

### レイヤー1：GitHub 対応

| 対応内容 | 優先度 | 方法 |
|---|---|---|
| goodbouldering-collab の正体を確認（個人 vs Organization） | 高 | GitHub ダッシュボードで確認 |
| 引き継ぎ先を Collaborator または Org メンバーとして追加 | 高 | GitHub Settings → Collaborators or Organization Members |
| 個人アカウントなら GitHub Organization に昇格させてから引き継ぎ | 推奨 | GitHub Docs: Converting a user to an organization |
| CONSUL_REPO_PAT の所有者・有効期限を確認・引き継ぎ先で再発行 | 中 | ai-hub Settings → Secrets → Environments |
| 台帳で足りるもの: 各リポ名と用途の一覧 | 低 | 本レポート 2-1 で完了 |

### レイヤー2：ドメイン 対応

| 対応内容 | 優先度 | 方法 |
|---|---|---|
| 各独自ドメインのレジストラ・管理者・更新期限を台帳化 | 高 | レジストラ管理画面で確認（お名前.com / Cloudflare Registrar 等） |
| ドメイン管理者メールアドレスが個人 Gmail の場合、事業用メールに変更 | 高 | レジストラ設定変更 |
| Vercel Team のオーナー権限を引き継ぎ先アカウントに移譲 | 中 | Vercel Dashboard → Settings → Members → Transfer Ownership |
| Cloudflare アカウントの管理権限を引き継ぎ先に付与 | 中 | Cloudflare → Manage Account → Members |
| 台帳で足りるもの: ドメイン → ホスティング対応表 | 低 | 本レポート 3-1 で完了 |

### レイヤー3：メール 対応

| 対応内容 | 優先度 | 方法 |
|---|---|---|
| 各事業の問い合わせ受信先を個人 Gmail から事業用メールに変更 | 高 | constants.ts / .env / フォーム設定の変更 |
| 送信サービス（Resend 等）の API キーを引き継ぎ先管理アカウントで再発行 | 高 | Resend / SendGrid ダッシュボード |
| Gmail の転送・フィルタ設定を確認し、引き継ぎ後に通知が届く経路を確保 | 中 | Gmail 設定 → 転送と POP/IMAP |
| 台帳で足りるもの: 事業別メール受信先の確認 | 低 | — |

---

## 6. 調査の限界

以下の項目はリポジトリのファイルからは判定できず、ダッシュボード/レジストラ直接確認が必須:

| 項目 | 確認先 |
|---|---|
| goodbouldering-collab が個人アカウントか GitHub Organization か | GitHub.com → Settings または Profile |
| 各リポの Collaborator 一覧・管理者設定 | GitHub → リポ Settings → Collaborators and teams |
| 各独自ドメインのレジストラ・有効期限・自動更新設定 | レジストラ管理画面 |
| ドメイン管理者メールアドレスの実値 | レジストラ管理画面 |
| Vercel Team の所有者・メンバー一覧 | Vercel Dashboard → Settings → Members |
| Cloudflare アカウントの管理者・メンバー一覧 | Cloudflare Dashboard → Manage Account → Members |
| カラーミーショップ（グッぼる/プロギング）のアカウント管理者 | カラーミーショップ管理画面 |
| Shopify（カラッと）のアカウント管理者・スタッフ設定 | Shopify 管理画面 |
| Resend / SendGrid の API キー所有者・組織設定 | Resend / SendGrid ダッシュボード |
| Gmail 転送・エイリアス設定 | Gmail → 設定 → 転送と POP/IMAP |
| ビジネス21 の独自ドメイン名（vercel.app 以外） | Vercel Dashboard → ビジネス21プロジェクト → ドメイン設定 |
| ClimbHero の本番ドメイン名 | Cloudflare Dashboard + ClimbHero CLAUDE.md 詳細確認 |
| 各事業の .env の ADMIN_EMAIL / CONTACT_EMAIL の実値 | Vercel Dashboard → Environment Variables |
| CONSUL_REPO_PAT の有効期限・スコープ | ai-hub → Settings → Secrets → Environments |

---

*本レポートは read-only 調査。コード変更なし。*
*情報源: .git/config, CLAUDE.md 各種, consul/*.md, .env.example（値なし・キー名のみ）, CI workflows*

---

2026-05-19 codex:codex-rescue 発火（全事業/GitHub・ドメイン・メール転送3レイヤ横断監査・入口判定で5ファイル以上横断のため着手前にサブエージェント委任/GitHub単一アカウント8+事業集中・個人Gmail集約4事業確認を検出）