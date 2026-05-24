# GSC / GA4 自動閲覧基盤 — 全事業横断データ取得＆施策出力

- 起案: 2026-05-23（CEO指示）
- 方針確定（CEO回答）: **OAuth再認可で既存 google_ops 基盤を拡張 / GSC登録済み全事業一斉 / GSC+GA4両方**
- 担当: Claude（consul本部・単独実装）

## ゴール

各事業のGSC（検索順位/クエリ/CTR）とGA4（流入/行動/CV）を、consulから自動で読みに行き、
事業ごとに「参考データ→施策」を機械的に出力できる基盤を作る。

## 設計判断（なぜこうするか）

| 論点 | 決定 | 理由 |
|---|---|---|
| 認証方式 | 既存 `google_ops` OAuth に**スコープ追加して再認可** | トークン保管/自動refresh基盤が完成済み。SA方式はプロパティ毎の手動招待が要り全事業一斉と相性が悪い |
| トークン保管 | **ローカルJSON `token_<account>.json`（Supabase廃止）** | 2026-05-24 CEO指示。個人運用＋ローカル実行なので専用Supabaseプロジェクト(`consul-ops`)を増やす意味が薄い。`.env`/oauth_tokensテーブル/service_roleキー全部不要に。get_credentials()のインターフェースは不変なのでgsc/ga4/poc全部そのまま動く。**親CLAUDE.mdに全プロジェクト共通方針として記録** |
| 対象範囲 | GSC登録済み**全プロパティを `sites().list()` で自動列挙** | 「何社あるか」は認可後にAPIで判明する。手で事業リストを書かない＝取りこぼし防止 |
| GSC/GA4 | 両方。ただしAPIは別物 | GSC=Search Console API（`webmasters`/`searchconsole`）、GA4=Analytics Data API（`google-analytics-data`） |
| MCP | 使わない | 公式MCP未成熟・認証は結局OAuthが要る。API直叩きが安定 |
| 出力先 | `work/YYYY-MM-DD-<事業略称>-seo-report.md` | CLAUDE.md の作業ファイル規則準拠（フラット保存・日付プレフィックス） |

## 必要スコープ（再認可で追加）

```
# 既存（維持）
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/gmail.compose
# 追加
https://www.googleapis.com/auth/webmasters.readonly     ← GSC 読み取り
https://www.googleapis.com/auth/analytics.readonly       ← GA4 読み取り
```

両方 readonly。書き込みスコープは取らない（誤操作防止＝gmail.send を外した思想と同じ）。

## GCP側で有効化が必要なAPI（CEO作業・1回）

- Search Console API
- Google Analytics Data API（GA4）

## 実装ファイル構成

```
google_ops/scripts/
├─ authorize.py        ← SCOPES に webmasters.readonly / analytics.readonly を追加（再認可用）
├─ refresh.py          ← 変更なし（get_credentials がそのまま使える）
├─ gsc.py（新規）       ← Search Console クライアント。sites一覧/クエリ/ページ/期間比較
├─ ga4.py（新規）       ← GA4 Analytics Data クライアント。流入/CV/行動
└─ run_seo_report.py（新規） ← 全プロパティ列挙→GSC+GA4取得→事業別 work/レポート生成
```

## アカウント↔プロパティの紐付け

- `goodbouldering` アカウント: ぐっぼる系のGSC/GA4
- `lossismore` アカウント: CEO個人配下のプロパティ
- どちらにどの事業が紐づくかは `sites().list()` / GA4 Admin API の結果で**実測してから**マッピング表を確定する（推測しない）

## 施策ロジック（データ→提案の機械化・第1版）

各プロパティについて直近28日 vs 前28日を比較し、以下を自動抽出：
1. **順位下落クエリ**（順位悪化が大きい順）→ 該当ページのtitle/H1点検を促す
2. **CTR過少クエリ**（順位の割にCTRが低い＝title/description改善余地）
3. **表示増・クリック減**（潜在需要あり取りこぼし）
4. **GA4: 流入はあるが直帰/低CVのLP** → 導線改善

→ 機械抽出した数値に、Claude（advisor/marketer）が事業トーンで施策文を載せる二段構え。

## 進捗

- [x] requirements に google-analytics-data / google-analytics-admin 追加・install済
- [x] authorize.py スコープ追加（webmasters.readonly / analytics.readonly）
- [x] gsc.py / ga4.py / run_seo_report.py 実装・全モジュールimport検証OK
- [ ] **CEO: GCPでAPI2つ有効化（Search Console API / Analytics Data API）**
- [ ] **CEO: 再認可実行（authorize.py を両アカウントで・スコープ追加のため必須）**
- [ ] `--list` でプロパティ列挙→ SITE_TO_GA4 マッピング確定（GA4のproperty_id埋め）
- [ ] 第1回 全事業レポート生成（python scripts/run_seo_report.py）

### 重要な発見（2026-05-23）: これは「再認可」ではなく「初回認可」
- `.env` も `credentials.json` も**未作成**だった ＝ 既存のCalendar/Gmail連携も一度も認可されていない
- つまりフェーズA(Supabase)〜D(認可)を全部CEOが初回実施する必要がある
- CEO向け完全手順書を新規作成: [docs/05-seo-setup-walkthrough.md](../google_ops/docs/05-seo-setup-walkthrough.md)
- 既存 docs/02 はAPI有効化が2つ(Gmail/Calendar)しか書いていなかった → 05でGSC/GA4含め4つに補正

### 実装メモ
- GA4 Admin API は `google-analytics-data` に含まれず `google-analytics-admin` が別途必要だった（解決済）
- GSC siteUrl と GA4 property は体系が違うため自動紐付け不可。`--list` 出力を見て SITE_TO_GA4 を手動で埋める設計にした
- 既存 refresh.py は無改修で流用可能（get_credentials がスコープに依存しないため）
