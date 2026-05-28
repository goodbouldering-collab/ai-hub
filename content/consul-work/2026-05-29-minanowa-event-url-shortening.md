# みんなのWA：イベントURL短縮（/event/<long-id> → /e/<6文字>）

## 経緯

ドメイン切替（`minanowa.com` → `minnanowa.net`）の完了後、CEO から「各イベントのURLをできるだけ短くして」と依頼。
現状の URL は `https://minnanowa.net/event/event-1770746627765-d5t70066i` で全長 57 文字、SNS/LINE シェア時に長すぎる。

## 設計判断

- **方式**: 短いコード `/e/<6文字>`（Option B：人間可読より最短優先）
- **アルファベット**: Base57（`a-zA-Z0-9` から `0/O/1/l/I` を除外。誤打防止）
- **長さ**: 6文字 = 57^6 ≈ 約 332 億通り（衝突確率ほぼゼロ）
- **既存URLの扱い**: 301 リダイレクトで /e/<code> に流す（SEO・SNS共有保護）

### URL 長さの比較（数字根拠）

| 区分 | URL | 文字数 |
|---|---|---|
| 旧 | `https://minnanowa.net/event/event-1779865700109-9vqnaefug` | 57 |
| 新 | `https://minnanowa.net/e/EMYm6R` | 30 |
| 削減 | 27 文字（**約 47% 短縮**） | |

## 実装の進め方

- **入口判定**: 5 ファイル以上の横断改修＋DBマイグレーション込みのため「重い」と判断し、入口で Codex に丸投げ（`codex:codex-rescue` サブエージェント・ [CLAUDE.md](../CLAUDE.md) §入口での重さ見積もり原則 に準拠）
- **コスト報告ゲート**: 1セッション 1回（3回まで余裕）
- **Codex の出来高**:
  - 骨格部分（migration / short-code 生成 / SSR新ハンドラ / 旧301化 / supabase-store の双方向マッピング）が揃った
  - **不足していたもの**: `vercel.json` の rewrites、`index.html` 内 9箇所の URL組立箇所、`api/ssr/sitemap.js` の URL生成、`handleDeepLink` の正規表現拡張
- **Claude による補足**: 上記の不足を Claude が完成（重い実装本体は Codex、最後の詰めは Claude）

## 実装ファイル（commit `550d597`）

| ファイル | 内容 |
|---|---|
| `supabase/migrations/0008_event_short_code.sql` | `events.short_code TEXT` 列追加 + 既存全レコードへ Base57 一斉割当 + UNIQUE INDEX |
| `lib/short-code.js` | `crypto.randomBytes` ベースの偏りない短縮コード生成器 |
| `lib/supabase-store.js` | `eventFromRow` / `eventToRow` の双方向マッピング、`writeAll` で未付与イベントに自動付与、`getEventByShortCode` / `generateUniqueShortCode` 追加 |
| `api/ssr/event/short/[code].js` | 新SSRハンドラ（OGタグ + Event JSON-LD） |
| `api/ssr/event/short/[code]/ics.js` | 新ICSエンドポイント |
| `api/ssr/event/[id].js` | 旧URLハンドラを 301 退化させた薄い実装に書き換え |
| `api/ssr/event/[id]/ics.js` | 旧ICSも 301 化 |
| `vercel.json` | `/e/:code` / `/e/:code/ics` の rewrites 追加 |
| `api/ssr/sitemap.js` | short_code を優先して sitemap.xml に出力 |
| `index.html` | 9箇所の `/event/${ev.id}` 組立を `(ev.shortCode ? 'e/'+shortCode : 'event/'+id)` フォールバックに切替 + `handleDeepLink` で `/e/` パス対応 |

## 本番反映

1. **本番Supabase migration 適用**: `$env:SUPABASE_ACCESS_TOKEN` を使い Management API `POST /v1/projects/{ref}/database/query` 経由で SQL 実行（`Status: Created` + 既存6件全部に short_code 埋まり確認）
2. **コード commit & push**: `main` push で Vercel 自動本番デプロイ
3. **疎通確認実測**:

```
GET https://minnanowa.net/e/EMYm6R                                      → 200 / 395KB HTML
GET https://minnanowa.net/event/event-1779865700109-9vqnaefug           → 301 → /e/EMYm6R
```

## 残課題

1. ~~LINEで実シェアして OG画像が表示されるか~~（要確認・後日CEOがスマホで実施）
2. 既存ユーザーのLINEブックマーク等で 301 が正しく辿れることの確認
3. 旧 `minanowa.com → minnanowa.net` DNS伝播完了確認（別作業）

## 委任ログ

2026-05-29 codex:codex-rescue 発火（みんなのWA / 5ファイル以上の横断改修+DBマイグレーション、入口判定で重いと見て委任 / Codex骨格作成→Claude仕上げで完成。本番デプロイ確認済）

🌐 Deploy URL: https://minnanowa.net （短縮URL例: https://minnanowa.net/e/EMYm6R ）
