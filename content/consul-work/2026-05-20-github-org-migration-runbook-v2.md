# GitHub Org 移管 実行手順書 v2（新Org作成＋全リポTransfer・現実版）

**作成: 2026-05-20 / 対象: 由井辰美 / 所要: 1.5〜2.5時間**

> ⚠️ v1（2026-05-20-github-org-conversion-runbook.md）は**廃止**。
> GitHub が「個人→Organization 公式変換」機能を廃止していたため
> （実画面で "Your personal account cannot be converted to an organization" を確認）。
> 本 v2 が唯一実行可能な方式。v1 は参照しないこと。

## 確定事項（2026-05-20 CEO 決定・実画面で検証済）

| 項目 | 確定値 |
|---|---|
| 方式 | **新Org作成 ＋ 全リポを個別 Transfer**（GitHub が指示する唯一の道） |
| 新Org名 | **`climbingconsul`**（GitHub作成画面で available 確認済・ハイフンなし） |
| Org オーナー | `goodbouldering-collab`（既存個人のまま。これが Org 作成者＝初期Owner） |
| 個人アカウントの扱い | `goodbouldering-collab` は**個人のまま生存**（v1の「ログイン不可化」リスクは消滅） |
| `lossismore@gmail.com` | **不要になった**（個人アカウント乗り換えが発生しないため。0-1 は無効化） |
| 2人目 Owner | 実在の信頼できる予備管理者（**未確定**・決まり次第 STEP 5） |
| 解決する単一障害点 | #1 GitHub 単一アカウント（影響8+事業） |

## v1 から消えたリスク / 新たに増えた手間

| 観点 | v1公式変換（廃止） | v2 新Org＋Transfer（実行する方式） |
|---|---|---|
| 個人アカウント | ログイン不可化（怖い） | **生存（安全）** |
| 逆変換不可リスク | あった | **ほぼ無い**（Transfer は個別・1本ずつ確認しながら戻せる） |
| リポURL | 不変 | **変わる**（goodbouldering-collab/x → climbingconsul/x。GitHubが自動リダイレクト） |
| Vercel連携 | 自動生存 | **8プロジェクト個別に再確認が要る**（STEP 4） |
| CI クロスリポ依存 | 影響軽微 | **CONSUL_REPO_PAT が確実に壊れる**（STEP 3 で対処必須） |

---

## Transfer 対象リポジトリ（実リモート確定・8本）

監査の推定と実際が一部相違していたため、`git remote` 実測で確定した正本：

| # | 事業 | 現リポ | Transfer後 | ローカルパス |
|---|---|---|---|---|
| 1 | みんなのWA | goodbouldering-collab/minanowa | climbingconsul/minanowa | C:\VSCode\Project\みんなのWA |
| 2 | N-デザイン | goodbouldering-collab/n-design | climbingconsul/n-design | C:\VSCode\Project\N-デザイン |
| 3 | ビジネス21 | goodbouldering-collab/business21 | climbingconsul/business21 | C:\VSCode\Project\ビジネス21 |
| 4 | トラスト | goodbouldering-collab/trust | climbingconsul/trust | C:\VSCode\Project\トラスト |
| 5 | Notエステ | goodbouldering-collab/notesthe | climbingconsul/notesthe | C:\VSCode\Project\Notエステ\web |
| 6 | ClimbHero | goodbouldering-collab/Climbhero | climbingconsul/Climbhero | C:\VSCode\Project\ClimbHero |
| 7 | ai-hub | goodbouldering-collab/ai-hub | climbingconsul/ai-hub | C:\VSCode\Project\ai-hub |
| 8 | consul | goodbouldering-collab/consul | climbingconsul/consul | C:\VSCode\Project\consul |

> グッぼる/プロギング/カラッと/ファディーは git 管理外（カラーミー/Shopify/再生成中）。
> Transfer 対象外。引き継ぎ書には「Git 管理外事業」として別途明記する。

---

## ⚠️ 移管順序の鉄則（CONSUL_REPO_PAT 問題）

ai-hub の `.github/workflows/sync-consul-docs.yml` が `CONSUL_REPO_PAT` で
`goodbouldering-collab/consul` を clone/push している。Transfer すると：

- consul のURLが変わる → ai-hub の CI が古いURLを参照 → **無言で同期停止**
- かつ secrets-inventory で「CONSUL_REPO_PAT は既に失効疑い」と既知

**鉄則**：
1. **ai-hub と consul は最後に、かつ連続で**Transfer する（間に他を挟まない）
2. consul Transfer 直後に sync-consul-docs.yml のリポ参照を新URLへ修正
3. CONSUL_REPO_PAT を新規発行し直し、ai-hub の GitHub Secret を更新
4. → これは Claude が修正PRを作れる（STEP 6）。CEO はトリガーだけ

順序：**1〜6（独立リポ）を先に → 7 ai-hub → 8 consul → CI修復（STEP 6）**

---

## STEP 0：事前準備（15分）

- [ ] 0-1. （旧0-1 lossismore は無効化。新規アカウント作成は発生しない）
- [ ] 0-2. 全リポ一覧スクショ保存：
      https://github.com/goodbouldering-collab?tab=repositories を画面保存（移管後の照合用）
- [ ] 0-3. 静かなタイミング確認：進行中の重要 PR / CI 実行中でないこと
      （特に ai-hub の Actions が回っていないタイミング）
- [ ] 0-4. ローカルの全リポに未コミット変更がないか確認
      （Transfer 自体はリモート操作だが、直後に remote URL 張り替えるため綺麗な状態が安全）
- [ ] 0-5. Bitwarden 無料アカウント作成（2FAリカバリ・新Org情報の退避先）
- [ ] 0-6. Vercel ダッシュボードにログインできることを事前確認（STEP 4 で即使う）

---

## STEP 1：新Organization `climbingconsul` を作成（5分）

`goodbouldering-collab` でログイン中の状態で：

1. [ ] https://github.com/account/organizations/new を開く
2. [ ] プラン選択 → **Free** を選択
3. [ ] **Organization name** に `climbingconsul` を入力（available 確認済）
4. [ ] Contact email：引き継ぎ観点では**事業用アドレス推奨**だが、当面 goodbouldering@gmail.com で可
      （後で変更可。ここは詰まらない）
5. [ ] 「This organization belongs to」→ **My personal account**（個人事業）を選択
6. [ ] 作成完了 → https://github.com/climbingconsul が開けることを確認 → [ ] 確認済
7. [ ] Org Settings → 自分（goodbouldering-collab）が **Owner** ロールであることを確認

---

## STEP 2：独立リポ6本を Transfer（各5分・計30分）

CI クロス依存のない #1〜#6 を先に。**1本ずつ・確認しながら**。

各リポについて繰り返す（#1 minanowa から順に）：

1. [ ] https://github.com/goodbouldering-collab/<repo>/settings を開く
2. [ ] 最下部 **Danger Zone** → **「Transfer ownership」**（"Transfer" ボタン）
3. [ ] 新オーナーに **`climbingconsul`** を入力
4. [ ] 確認のためリポ名をタイプ → Transfer 実行
5. [ ] https://github.com/climbingconsul/<repo> が開けることを確認
6. [ ] **ローカルの remote URL を張り替える**（該当事業フォルダで）：
   ```
   git remote set-url origin https://github.com/climbingconsul/<repo>.git
   git remote -v   # 新URLになったか確認
   ```
   ※この git 操作は Claude が代行可（CEO 承認のもと・各事業フォルダ）

進捗：
- [ ] #1 minanowa  - [ ] #2 n-design  - [ ] #3 business21
- [ ] #4 trust  - [ ] #5 notesthe  - [ ] #6 Climbhero

---

## STEP 3：ai-hub → consul を連続 Transfer（15分・鉄則区間）

ここは順序厳守。間に休憩や他作業を挟まない。

1. [ ] #7 ai-hub を Transfer（STEP 2 と同じ手順）→ ローカル remote 張り替え
2. [ ] #8 consul を Transfer（**このリポ**）→ ローカル remote 張り替え：
   ```
   git remote set-url origin https://github.com/climbingconsul/consul.git
   ```
3. [ ] この時点で sync-consul-docs.yml は壊れている（想定内）。STEP 6 で直す
4. [ ] 8本すべて https://github.com/climbingconsul?tab=repositories に揃ったか
      0-2 のスクショと照合 → [ ] 全8本確認

---

## STEP 4：Vercel 連携の再確認（30分・8プロジェクト）

Transfer でリポURLが変わったため、Vercel の Git 連携が切れている可能性。
GitHub 自動リダイレクトで生きている場合もあるが**全件確認が必須**。

各 Vercel プロジェクトで：
1. [ ] Vercel → プロジェクト → Settings → Git
2. [ ] 接続が `climbingconsul/<repo>` を指しているか確認
3. [ ] 切れていたら → Disconnect → Reconnect で `climbingconsul/<repo>` を再選択
4. [ ] 「Vercel GitHub App needs access to climbingconsul org」警告が出たら承認
5. [ ] 軽微な空コミット push → 自動デプロイされるかで疎通確認

確認対象（Vercel運用7事業）：
- [ ] minanowa  - [ ] n-design  - [ ] business21
- [ ] trust  - [ ] notesthe  - [ ] ai-hub
- [ ]（ClimbHero は Cloudflare 集約。Vercel ではなく Cloudflare 側 GitHub 連携を確認）

---

## STEP 5：2人目 Owner 追加（5分・★バス係数2の本体・予備管理者確定後★）

**ここまでは「Org化しただけ・Owner1名＝まだ単一障害点」。**
予備管理者が決まったらここで初めてバス係数2になる。

1. [ ] climbingconsul → People → Invite member → 予備管理者を招待
2. [ ] ロールを **Owner** に設定（Member 不可）
3. [ ] Org Settings → Authentication security → 2FA 必須化を ON
4. [ ] 予備管理者本人に「由井不在時の GitHub 最終権限保持者」と口頭共有
5. [ ] → **この時点で承認#1（GitHubレイヤ）クリア**

> 予備管理者未確定の間は、台帳に「**Org化済・Owner1名・予備管理者未確定＝
> 引き継ぎ未完了**」と正直に記録。「Org化＝対策済」と誤記録しないこと。

---

## STEP 6：CI クロスリポ依存の修復（Claude 代行可・15分）

consul Transfer で壊れた sync-consul-docs.yml を直す：

1. [ ] ai-hub/.github/workflows/sync-consul-docs.yml の
      consul リポ参照を `climbingconsul/consul` に修正（Claude が修正PR作成）
2. [ ] `CONSUL_REPO_PAT` を新規発行（goodbouldering-collab → Settings →
      Developer settings → PAT。スコープは repo 最小限。期限は要設定）
3. [ ] ai-hub の GitHub Secret `CONSUL_REPO_PAT` を新値に更新（CEO 操作）
4. [ ] sync-consul-docs.yml を手動 trigger → 同期成功を確認
5. [ ] secrets-inventory.md の CONSUL_REPO_PAT 行を更新（Claude 代行）

---

## STEP 7：台帳反映（Claude 代行・5分）

CEO は移管完了を報告するだけ。以下は Claude が work/ 文書を更新：

- [ ] secrets-inventory.md に GitHub Org 行・新URL を反映
- [ ] handoff-master-plan.md フェーズ1の進捗更新（**完了ではなく「Owner1名・予備管理者待ち」**）
- [ ] dashboard-checklist.md ブロックA・承認マトリクスの GitHub 行を更新
      （予備管理者確定まで「○」にしない）
- [ ] 各事業の CLAUDE.md / 事業情報ファイルの GitHub URL 記述を新Orgに更新
- [ ] 新Org名・予備管理者・2FAリカバリを Bitwarden「_共通」へ（場所のみ台帳記載）

---

## ロールバック

- STEP 1 のみ（Org作成だけ）で中断 → 空 Org が残るだけ。実害なし・後で削除可
- STEP 2-3 で個別リポを戻したい → Transfer は逆向きに再実行可
  （climbingconsul/x → goodbouldering-collab/x へ Transfer し直し）。v1 と違い**戻せる**
- Vercel 連携が全断 → STEP 4 の再接続で回復（リポ自体は無事なので最悪でも復旧可能）
- 迷ったら STEP を進めず CEO 判断を仰ぐ（特に STEP 3 鉄則区間）

---

## 関連文書

- ~~v1 手順書（廃止）~~ 2026-05-20-github-org-conversion-runbook.md ← 参照禁止
- [マスタープラン](2026-05-19-handoff-master-plan.md)
- [4レイヤ監査](2026-05-19-github-domain-mail-audit.md)
- [承認チェックリスト](2026-05-19-handoff-dashboard-checklist.md)
- [シークレット台帳](2026-05-17-secrets-inventory.md)
