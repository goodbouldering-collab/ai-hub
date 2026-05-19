# 【廃止】GitHub 個人→Organization 変換 実行手順書（v1）

> ⚠️ **このv1は廃止。参照禁止。**
> GitHub が「個人→Organization 公式変換」機能を廃止していたため
> （2026-05-20 実画面で "Your personal account cannot be converted to an
> organization. You must create a new organization and transfer..." を確認）。
> **正本は [v2: 新Org作成＋全リポTransfer](2026-05-20-github-org-migration-runbook-v2.md)**。
> 以下は経緯保存のため残置するのみ。実行に使わないこと。

---

**作成: 2026-05-20 / 対象: 由井辰美 / 所要: 45〜60分**

## 確定した方式（2026-05-20 CEO 決定）

| 項目 | 決定 |
|---|---|
| 対象アカウント | `goodbouldering-collab`（個人と確定済・CODEOWNERS等のガバナンスファイル0件の傍証とも一致） |
| 変換方式 | **GitHub 公式「個人→Organization 変換」**（アカウントそのものを Org 化。全リポ・URL・Star 維持、Vercel連携も生存） |
| 2人目 Owner | **信頼できる予備管理者**（家族/共同事業者など、由井不在時に動ける個人を1名） |
| 解決する単一障害点 | #1 GitHub 単一アカウント（影響8+事業）。これ単体でバス係数 1→2 |

---

## ⚠️ 着手前の最重要警告（ここを誤ると復旧困難）

1. **変換後、`goodbouldering-collab` では個人ログインできなくなる**。
   GitHub の変換は「この個人アカウント＝Org の器」にする処理。あなたの人格は
   **別の新規個人アカウント**に移し、それを Org の Owner として招く形になる。
   → **新個人アカウント用の「未使用メールアドレス」が事前に1個必須**。
   `goodbouldering@gmail.com` は現アカウントで使用中なので**そのままは使えない**。
   - 推奨：`goodbouldering+gh@gmail.com`（Gmailのエイリアス。+以降は無視され同じ受信箱に届く）
   - または事業用ドメインのメール（引き継ぎ観点ではこちらがより堅い）

2. **Vercel 連携**：公式変換はリポURL（`github.com/goodbouldering-collab/<repo>`）が
   **変わらない**ため、Vercel の Git 連携は原則そのまま生きる。ただし変換直後に
   各 Vercel プロジェクトで「GitHub App のアクセス権を Org に再付与」する確認が要る
   （手順は STEP 5）。**全リポ Transfer 方式と違いここが楽なのが公式変換を選んだ理由**。

3. **2FA 必須**：Org 変換後、Owner には 2要素認証を強制する設定が推奨。
   新個人アカウント・予備管理者の両方で 2FA を有効化し、**リカバリコードを Bitwarden へ**。

4. **やってはいけない**：焦って先に新アカウントを作らない。STEP 1 の順序を守る
   （新アカウント先行作成 → 同一メール衝突で詰む典型事故）。

---

## STEP 0：事前準備（15分・変換前に必ず全部完了）

- [ ] 0-1. 新個人アカウント用メールを決める：__________
      （推奨 `goodbouldering+gh@gmail.com`。受信できることをテスト送信で確認）
- [ ] 0-2. 2人目 Owner（予備管理者）の GitHub アカウント名 or 招待先メールを確定：__________
      予備管理者がまだ GitHub 未登録なら、先に登録してもらう
- [ ] 0-3. 現状の全リポ一覧をスクショ保存（変換後の照合用）：
      https://github.com/goodbouldering-collab?tab=repositories を画面保存
- [ ] 0-4. 進行中の重要 PR/Issue がないタイミングを選ぶ（変換中は数分操作不可になりうる）
- [ ] 0-5. Bitwarden（無料）アカウントだけ先に作っておく（リカバリコード退避先。
      [マスタープラン フェーズ2](2026-05-19-handoff-master-plan.md) 参照）

> 0-1 が最重要。ここのメールを既存使用中アドレスにすると変換ウィザードで止まる。

---

## STEP 1：個人→Organization 変換の実行（10分）

1. [ ] `goodbouldering-collab` でログインした状態で
       **Settings**（右上アバター → Settings）を開く
2. [ ] 左メニュー最下部 **Access** 群 → 一番下までスクロール
3. [ ] **「Organizations」** セクション →
       **「Turn <goodbouldering-collab> into an organization」** をクリック
       （直リンク: https://github.com/account/organizations/convert ）
4. [ ] 警告画面を読む（「個人アカウントは Org になり、ログイン不可になる」旨）
5. [ ] **「Transfer my user account to a new organization」** を選択して続行
6. [ ] プラン選択 → **Free** を選ぶ（プライベートリポ無制限・Actions も現状規模で無料枠内）
7. [ ] 「この Org の管理を引き継ぐ新個人アカウント」の指定を求められる：
   - 既に新個人アカウントを作ってある場合 → そのユーザー名を入力
   - まだない場合 → ウィザード内の案内に従い **STEP 0-1 で決めたメール**で新規作成
8. [ ] 確認チェックを入れて **変換実行**
9. [ ] 完了後、`https://github.com/goodbouldering-collab` を開き
       **Org 表示（People/Teams タブが出る）** になったことを確認 → [ ] 確認済

---

## STEP 2：新個人アカウントを Owner として確立（5分）

1. [ ] 変換で作成/指定した新個人アカウントでログインし直す
2. [ ] `goodbouldering-collab` Org → **People** タブ → 自分（新アカウント）が
       **Owner** ロールであることを確認 → [ ] 確認済
3. [ ] この新アカウントで **2FA を有効化**（Settings > Password and authentication）
4. [ ] 2FA リカバリコードを **Bitwarden の「_共通」Collection** に保存（紙にも控える）

---

## STEP 3：2人目 Owner（予備管理者）の追加（5分）★バス係数2の本体★

ここまでだと Owner はあなた1人＝まだ単一障害点。**ここで初めて2になる。**

1. [ ] `goodbouldering-collab` Org → **People** → **Invite member**
2. [ ] STEP 0-2 で確定した予備管理者を招待
3. [ ] 招待時 or 参加後にロールを **Owner** に設定
       （Member ではなく Owner。Member だと緊急時に権限不足）
4. [ ] 予備管理者に 2FA を有効化してもらう（Org で 2FA 必須化するなら必須）
5. [ ] 予備管理者本人に「あなたは由井不在時の GitHub 最終権限保持者」と口頭で共有
6. [ ] → この時点で **承認#1（GitHub レイヤ）の前提クリア**

---

## STEP 4：Org のセキュリティ初期設定（10分・推奨）

1. [ ] Org Settings → **Authentication security** → 「Require two-factor authentication」を ON
       （全メンバーに 2FA 強制。予備管理者の 2FA 設定後に ON にする）
2. [ ] Org Settings → **Member privileges** →
       「Base permissions」を **Read** に（不要な書き込み権限を配らない）
3. [ ] 必要なら **Team** を作って事業ごとにリポ権限を分離
       （クライアント担当を将来招くとき用。今は Owner 2名だけで可）
4. [ ] Org Settings → **Billing** → Free プランであること・将来 Team 機能で
       有料化が要るか把握（現状は Free で足りる）

---

## STEP 5：Vercel 連携の再確認（10分・壊れていないかの確認）

公式変換はリポURL不変なので**基本は連携継続**。だが GitHub App のスコープが
個人→Org に変わるため、各 Vercel プロジェクトで明示再付与が要る場合がある。

1. [ ] Vercel ダッシュボード → 任意のプロジェクト → Settings → Git
2. [ ] 接続先リポが `goodbouldering-collab/<repo>` のまま生きているか確認
3. [ ] 「GitHub App needs access to this organization」的な警告が出たら
       指示に従い `goodbouldering-collab` Org への Vercel GitHub App アクセスを承認
4. [ ] 1プロジェクトで test：軽微なコミットを push → Vercel が自動デプロイするか確認
5. [ ] 全プロジェクト分、連携生存を1つずつ確認（チェックリスト化）：
   - [ ] n-design  - [ ] business21-kanri  - [ ] minanowa
   - [ ] ai-hub  - [ ] notesthe  - [ ] trust  - [ ] consul  - [ ] ClimbHero

---

## STEP 6：台帳反映（5分・私=Claude が代行可）

- [ ] [secrets-inventory.md](2026-05-17-secrets-inventory.md) に GitHub Org 行を追加
- [ ] [handoff-master-plan.md](2026-05-19-handoff-master-plan.md) フェーズ1を [x] に
- [ ] [dashboard-checklist.md](2026-05-19-handoff-dashboard-checklist.md) ブロックA・承認マトリクスの GitHub 行を ○ に
- [ ] 新個人アカウント名・予備管理者名・Org名を Bitwarden「_共通」に記録
      （**このファイルには実名・メールを直書きしない**。台帳は場所だけ）

> STEP 6 は変換完了報告をくれれば Claude が work/ 文書側を更新する。

---

## ロールバック（変換がうまくいかなかった場合）

- 変換**実行前**（STEP 1-8 未完）なら：何もせず中断すれば現状維持。リスクなし
- 変換**実行後**に問題（Vercel 連携全断など）：
  - GitHub の Org→個人 逆変換は**公式には提供されていない**。これが「着手前警告」を
    重く書いた理由。STEP 0 を完了せず STEP 1 に進まないこと
  - Vercel 連携だけの問題なら STEP 5 の再付与で回復可能（リポは無事）
  - 判断に迷ったら変換を**完了させずに**中断し、CEO 判断を仰ぐ

---

## 関連文書

- [マスタープラン](2026-05-19-handoff-master-plan.md)
- [4レイヤ監査：GitHub/ドメイン/メール](2026-05-19-github-domain-mail-audit.md)
- [承認チェックリスト](2026-05-19-handoff-dashboard-checklist.md)
- [シークレット台帳](2026-05-17-secrets-inventory.md)
