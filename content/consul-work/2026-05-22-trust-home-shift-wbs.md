# プロジェクト名: home-shift 4棟体制本稼働（2026-08-01）

## 今週CEOがやるべきこと（3行）

1. **LINE Developersでチャネルを2つ作成**（Messaging API + LINE Login・同一Provider）し、トークン/シークレット/LIFF IDを取得する（これが最初のクリティカルパスボトルネック）
2. **取得した9個の値をVercel環境変数に登録**する（ANTHROPIC_API_KEYも含め計10個未設定・LIFF IDは先に仮置き値でも可）
3. **`STAFF_ENROLLMENT_CODE`の文言を決める**（例：「トラスト2026」など・スタッフに配布する合言葉）

---

## ゴール

LINE Bot + LIFF でスタッフが希望を提出し、管理者がワンコマンドでシフト表（PNG）を生成・全員配信できるシステムを2026-08-01に4棟17名で本稼働させる。月20時間のExcel作業をゼロにする。

## 期日

2026-08-01（4棟体制開始日。逆算残り10週間）

---

## ターゲット期日の意味

| マイルストーン | 期日 | 説明 |
|---|---|---|
| LINE接続完了 | 05-29 | これ以降すべての実装が進める前提 |
| home-shift schema本番適用 | 06-05 | スタッフ登録・希望収集が動く前提 |
| LIFF実装完了 | 06-13 | スタッフが実際に操作できる状態 |
| シフト生成完成 | 06-27 | AI生成・PNG配信の核心 |
| 本番統合テスト開始 | 07-04 | 実スタッフ数名で動作確認 |
| リハーサル運用（7月分シフト） | 07-15 | 実際に7月シフトをシステムで作る |
| 4棟本稼働 | 08-01 | |

---

## タスクリスト（全体）

### PHASE A: CEO手動ゲート（最優先・これが詰まると全部止まる）

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | クリティカル |
|---|---|---|---|---|---|---|---|
| A1 | LINE DevelopersでProviderを作成またはトラスト用に確認 | CEO手動 | Provider ID | - | 05-26 | pending | ★ |
| A2 | Messaging APIチャネル作成（LINE公式アカウント） | CEO手動 | `LINE_CHANNEL_ACCESS_TOKEN` / `LINE_CHANNEL_SECRET` | A1 | 05-26 | pending | ★ |
| A3 | LINE Loginチャネル作成（同一Provider） | CEO手動 | `LINE_LOGIN_CHANNEL_ID` / `LINE_LOGIN_CHANNEL_SECRET` | A1 | 05-26 | pending | ★ |
| A4 | LIFFアプリ登録2本（shift-request / shift-view）・LIFF ID取得 | CEO手動 | `NEXT_PUBLIC_LIFF_ID_SHIFT_REQUEST` / `NEXT_PUBLIC_LIFF_ID_SHIFT_VIEW` | A3 | 05-27 | pending | ★ |
| A5 | Vercel環境変数に未設定の10変数を登録（ANTHROPIC_API_KEY含む） | CEO手動 | Vercel Dashboard設定完了 | A2,A3,A4 | 05-29 | pending | ★ |
| A6 | WebhookURLをLINE Developersに登録（`trust-nine-tau.vercel.app/api/line/webhook`） | CEO手動 | Webhook検証「成功」 | A2,A5 | 05-29 | pending | ★ |
| A7 | `STAFF_ENROLLMENT_CODE`の文言決定（例：「トラスト2026」） | CEO判断 | 合言葉文字列 | - | 05-26 | pending | |
| A8 | Supabase `trust_home_shift` schema本番適用（CEO手動DDL） | CEO手動 | home-shiftスキーマ8テーブル存在確認 | A5 | 06-05 | pending | ★ |
| A9 | マスタデータ初期投入（棟4件・スタッフ17名・shift_patterns・constraints） | CEO手動+developer | seedデータ本番DB反映 | A8 | 06-12 | pending | |
| A10 | 管理者のLINE User ID確認・`ADMIN_LINE_USER_IDS`設定 | CEO手動 | 環境変数登録 | A5 | 05-29 | pending | |

> A1〜A6は一連の操作で1〜2時間で完了可能。LINE Developers Console（developers.line.biz）にログインして順番に進める。
> A4のLIFF登録では、URLを `https://trust-nine-tau.vercel.app/home-shift/liff/shift-request` と `…/shift-view` にセットする。
> A8は `トラスト/supabase/home-shift/migrations/0001_init_schema.sql` の内容をSupabase DashboardのSQL Editorに貼り付けて実行する（trust_site適用と同じ手順）。

---

### PHASE B: LINE接続・疎通確認（developer / A5,A6完了後）

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | クリティカル |
|---|---|---|---|---|---|---|---|
| B1 | Webhook受付ルート拡張（テスト応答・イベント種別ログ） | developer | `/api/line/webhook` がfollow/messageに200応答 | A5,A6 | 05-30 | pending | ★ |
| B2 | LINE公式アカウントにテストフォローして疎通確認 | CEO手動 | Vercel logsで受信確認 | B1 | 05-30 | pending | |
| B3 | リッチメニュー作成（「希望提出」「シフト確認」「提出状況」3ボタン・画像込み） | developer | LINE公式アカウントにリッチメニュー表示 | B1 | 06-06 | pending | |

---

### PHASE C: LIFF実装・スタッフ希望提出フロー（Phase 1）

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | クリティカル |
|---|---|---|---|---|---|---|---|
| C1 | LIFF SDKセットアップ・`liff.init()`動作確認 | developer | `/home-shift/liff/shift-request` がLINE内で開く | A4,A5,A8 | 06-06 | pending | ★ |
| C2 | 希望提出カレンダーUI実装（日付タップでoff/×/日/夜のトグル・月希望日数入力） | developer | 全画面操作がiPhoneのLINE内ブラウザで動作 | C1 | 06-13 | pending | ★ |
| C3 | 希望提出サブミット実装（`shift_requests`テーブルへのupsert・RLS対応） | developer | Supabase `shift_requests`にデータが入る | C2,A8 | 06-13 | pending | ★ |
| C4 | シフト確認LIFF実装（確定シフト表示・月の勤務サマリ） | developer | `/home-shift/liff/shift-view` が自分のシフトを表示 | C1,A8 | 06-20 | pending | |
| C5 | iPhoneカレンダー登録機能（`.ics`生成・「カレンダーに追加」ボタン） | developer | iPhoneの標準カレンダーにシフトが登録される | C4 | 06-27 | pending | |

---

### PHASE D: 管理者機能・希望状況管理（Phase 1・管理者側）

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | |
|---|---|---|---|---|---|---|---|
| D1 | 提出状況管理UI実装（`/admin`希望管理タブの送信ボタン有効化・提出済/未提出一覧） | developer | 管理者画面で提出率が見える | C3 | 06-13 | pending | |
| D2 | LINE Botで提出状況照会（「提出状況」テキスト→Flex Message一覧返信） | developer | 管理者がLINEで確認できる | B1,D1 | 06-20 | pending | |
| D3 | 未提出者へのリマインダー一括送信実装（管理画面の「一括リマインド」ボタン） | developer | 未提出スタッフにLINE通知が飛ぶ | D2 | 06-20 | pending | |
| D4 | 毎月25日朝の自動リマインダー（Vercel Cron・UTC 21:00） | developer | Vercel cron jobが月25日に発火・Webhook経由で通知 | D3 | 06-27 | pending | |

---

### PHASE E: シフト生成AI・PNG出力（Phase 2・最重量）

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | クリティカル |
|---|---|---|---|---|---|---|---|
| E1 | Claude APIシフト生成プロンプト設計（棟×日×スタッフのJSONスキーマ定義込み） | developer | プロンプト + 出力スキーマのドキュメント（`docs/home-shift/PROMPT.md`） | A5 | 06-06 | pending | ★ |
| E2 | シフト生成サービス実装（`lib/home-shift/shift-generator.ts`・制約チェッカー連携） | developer | 希望データ→シフトJSON生成が動作するユニットテスト | E1 | 06-20 | pending | ★ |
| E3 | シフト表PNG生成（`@vercel/og`・棟ごと1枚・Noto Sans JP・1ヶ月カレンダー形式） | developer | 棟ごとのシフト表PNG（Edge Functionで生成・URLアクセスで確認） | E2 | 06-27 | pending | ★ |
| E4 | 自然言語修正コマンド（「西山さんの3日を休みに」→差分適用→再チェック） | developer | LINE上でテキスト修正が適用される | E2,B1 | 07-04 | pending | |
| E5 | シフト生成→画像送信フロー（Botが4棟分画像をFlex Messageで送信） | developer | 管理者LINEに4棟シフト画像が届く | E3,B1 | 07-04 | pending | ★ |
| E6 | メトリクス表示（夜勤偏り・希望充足率・配置基準クリア状況） | developer | シフト生成結果に数値サマリが付く | E5 | 07-04 | pending | |

---

### PHASE F: 確定・配信・admin統合（Phase 3）

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | |
|---|---|---|---|---|---|---|---|
| F1 | 確定処理実装（`shifts`テーブルにstatusカラムをconfirmedへ更新） | developer | 確定ボタンでDBが確定状態になる | E5 | 07-04 | pending | |
| F2 | 確定後スタッフ個別配信（各スタッフに自分のシフト画像をLINE送信） | developer | 全スタッフのLINEに自分のシフトが届く | F1 | 07-11 | pending | ★ |
| F3 | `/admin`シフト管理タブ統合（生成→確認→確定の一連フロー・UI実装） | developer | 管理者がブラウザからもシフト操作できる | E5,F1 | 07-11 | pending | |
| F4 | シフト交換申請フロー（「交換を申請」ボタン→相手に通知→双方承認） | developer | LINE上でシフト交換が完結 | F2 | 07-18 | pending | |

---

### PHASE G: 本番統合テスト・リハーサル・本番移行

| # | タスク | 担当 | 成果物 | 依存 | 期日 | 状態 | クリティカル |
|---|---|---|---|---|---|---|---|
| G1 | スタッフ登録リハーサル（実スタッフ数名がenroll・LINE連携） | CEO手動+developer | 3名以上がDBに登録済み | A9,C1 | 07-04 | pending | ★ |
| G2 | 7月シフトをシステムで生成（本番データで初回シミュレーション） | CEO手動+developer | 7月シフト案が管理者LINEに届く（本運用と同じフロー） | G1,E5 | 07-15 | pending | ★ |
| G3 | 管理者向け操作マニュアル作成（`docs/home-shift/OPERATION.md`） | developer | A4ページ以内のPDF or Markdown | G2 | 07-18 | pending | |
| G4 | Supabase Freeプラン→Pro昇格判断（スタッフ個人情報を本番で扱う時点で推奨） | CEO判断 | 昇格またはFree継続の判断記録 | G1 | 07-01 | pending | |
| G5 | 全スタッフ登録・初期マスタ確認（17名全員のLINE連携） | CEO手動+developer | `staffs`テーブルに17名 | G1 | 07-18 | pending | ★ |
| G6 | 8月シフト希望収集（7/25〜27・本番運用） | CEO手動 | 17名分の希望が`shift_requests`に存在 | G5 | 07-27 | pending | ★ |
| G7 | 8月シフト生成・確定・全員配信（本稼働） | CEO手動+developer | 全スタッフのLINEに8月シフトが届く | G6 | 08-01 | pending | ★ |

---

## クリティカルパス（これが詰まると全体が止まる）

```
A1-A3（LINE チャネル作成）
  ↓
A4（LIFF登録）→ A5（env変数登録）→ A6（Webhook登録）
  ↓                    ↓
B1（Webhook疎通）     A8（DB schema適用）
  ↓                    ↓
C1（LIFF init）←──────┘
  ↓
C2-C3（希望提出UI+submit）
  ↓
E2（シフト生成）← E1（プロンプト設計）
  ↓
E3（PNG生成）→ E5（Bot配信）
  ↓
F1-F2（確定・全員配信）
  ↓
G2（7月リハーサル）→ G5-G7（8月本稼働）
```

**最初のボトルネック**: A1〜A6はすべてCEO手動で、技術的に自動化不可。これが完了しないとB1以降のdeveloper作業が全滅する。今週中（05-26〜05-29）に完了させること。

---

## 週次マイルストーン

| 週 | 期間 | マイルストーン | CEOアクション | developerアクション |
|---|---|---|---|---|
| W1 | 05-22〜05-29 | **LINE接続ゲート突破** | A1〜A7・A10 完了（LINE Console操作） | A5完了後にB1着手・プロンプト設計E1開始 |
| W2 | 05-30〜06-05 | **Webhook疎通・DB適用** | A8（home-shift schema適用） | B1完了・B2疎通確認・E1完成 |
| W3 | 06-06〜06-13 | **LIFF動作・希望提出フローα** | マスタデータ初期投入A9参加 | B3・C1・C2・E2着手 |
| W4 | 06-14〜06-20 | **希望提出フロー完成・提出管理** | スタッフ2〜3名でテスト提出 | C3・C4・D1・D2・D3完了 |
| W5 | 06-21〜06-27 | **シフト生成完成・PNG配信** | シフト生成テスト立会 | E2・E3・E5・D4完了 |
| W6 | 06-28〜07-04 | **全フロー結合・管理者統合** | G4判断（Pro昇格） | E4・E6・F1・G1並行 |
| W7 | 07-05〜07-11 | **確定配信・admin統合** | G1（スタッフ登録リハ） | F2・F3完了 |
| W8 | 07-12〜07-18 | **7月リハーサル運用** | G2（7月シフト本番生成）・マニュアル確認 | G3・F4 |
| W9 | 07-19〜07-27 | **全スタッフ登録・8月希望収集** | G5・G6 | バグ修正対応 |
| W10 | 07-28〜08-01 | **本番稼働** | G7（8月シフト確定配信） | 緊急対応待機 |

---

## CEOが「今週やること」詳細手順（A1〜A7・A10）

### 手順（所要時間：1〜2時間）

1. `https://developers.line.biz` にログイン（LINEアカウントで）
2. 「Providers」→「Create a new provider」→ 名前「トラストエージェント」
3. 「Create a Messaging API channel」
   - アイコン：トラスト社ロゴ
   - チャネル名：「トラスト ホームシフト」
   - 完了後：Channel secret・Channel access token(long-lived)をメモ
4. 同じProviderで「Create a LINE Login channel」
   - チャネル名：「トラスト Login」
   - アプリタイプ：「Web app」
   - 完了後：Channel ID・Channel secretをメモ
5. LINE LoginチャネルのLIFF設定を開く → 「Add」
   - 名前：「shift-request」
   - タイプ：Full（カレンダーUIのため）
   - エンドポイント：`https://trust-nine-tau.vercel.app/home-shift/liff/shift-request`
   - LIFF IDをメモ
   - もう1つ追加：名前「shift-view」・エンドポイント `…/shift-view`・LIFF IDをメモ
6. Vercel Dashboard（`https://vercel.com`）→ トラストプロジェクト → Settings → Environment Variables
   - 以下を追加（Production・Preview・Development全部にチェック）:
   - `ANTHROPIC_API_KEY` ← Anthropic ConsoleのAPI Key
   - `LINE_CHANNEL_ACCESS_TOKEN` ← 3でメモした値
   - `LINE_CHANNEL_SECRET` ← 3でメモした値
   - `LINE_LOGIN_CHANNEL_ID` ← 4でメモした値
   - `LINE_LOGIN_CHANNEL_SECRET` ← 4でメモした値
   - `NEXT_PUBLIC_LIFF_ID_SHIFT_REQUEST` ← 5でメモした値
   - `NEXT_PUBLIC_LIFF_ID_SHIFT_VIEW` ← 5でメモした値
   - `ADMIN_LINE_USER_IDS` ← 自分（臼井代表）のLINE User ID（LINEのプロフィール設定で確認可）
   - `STAFF_ENROLLMENT_CODE` ← 決めた合言葉（例：「トラスト2026」）
7. Messaging API設定 → Webhook → 「Use webhook」ON → URL：`https://trust-nine-tau.vercel.app/api/line/webhook` → 「Verify」→「成功」を確認

---

## リスク・注意事項

| リスク | 影響度 | 対策 |
|---|---|---|
| CEOが今週のLINE Console操作を後回しにする | 致命的（全タスクが連鎖して1週間以上後ズレ） | W1終了時点（05-29）を「Go/NoGo」ゲートに設定。未完了なら日程見直しを協議 |
| Supabase Free 7日pauseリスク（本番スタッフ個人情報） | 高 | G4（07-01）でPro昇格を判断。本稼働前に決定必須。$25/月・org単位なのでn-designほか同時昇格になる点を認識した上で判断 |
| シフト生成AI（Opus 4.7）のタイムアウト（Vercel Pro 60秒制限） | 中 | 4棟×17名×31日のJSONは重い。E2実装時にストリーミング+制約チェッカー分離で対処。必要なら生成をバックグラウンド化 |
| LIFFがiPhone LINE内ブラウザで動かない（カメラ・位置情報外）| 低 | カレンダーUIは標準DOM操作のみ・位置情報不使用。ただしLIFF SDKのバージョン固定必須（`@line/liff@2.x`） |
| home-shift schemaとtrust_siteの共存（PGRST002問題） | 中 | 2026-05-20の記録より：`trust_home_shift`をExposed schemasに追加するとスキーマキャッシュがスタックする既知挙動あり。A8適用後に別途PostgREST公開設定の手順を踏む（developerが手順書作成） |
| スタッフがLINE友だち追加を拒否・音信不通 | 中 | G1で少人数から始め、リハーサルで「友だち追加してください」フォローをCEOが直接案内 |
| 期日直前の棟追加（4棟目の開設日未定） | 中 | マスタの`homes.is_active`フラグで棟を動的有効化できる設計のため、開設タイミングは柔軟対応可能 |

## 完了の定義

- **05-29**: VercelのLogs画面でLINEからのWebhookイベントが受信できる（B2）
- **06-13**: テストスタッフ（CEO自身）がLIFF shift-requestで希望を提出でき、Supabaseに記録される（C3）
- **07-15**: 7月シフトが実際にAIで生成され、4棟分のPNG画像が管理者LINEに届く（G2）
- **08-01**: 全スタッフ17名に8月の確定シフトがLINE送信される（G7）・「完全稼働」

---

最終更新: 2026-05-22（pm初版作成）
