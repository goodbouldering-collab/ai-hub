# Vercel($20/月1本) → Cloudflare 全面移行は、いま本当に得か（経営判断分析）

- **作成**: 2026-05-22
- **依頼者**: CEO（由井辰美）
- **分析**: advisor（opus）+ Vercel API 実測 + WebSearch 裏取り
- **対象範囲**: 全Vercel事業（7事業）一括移行の検討（CEO確認済み）

---

## 1. 結論（3行）

**移行は推奨しない。** Vercel は既に **$20/月×1チーム集約済み**で、CEO の値ごろ前提（$20×N）は崩れている。7事業の OpenNext 移行工数（推計 **合計110〜175時間**）と恒久的な検証コスト・トラスト本稼働(8/1)直前のリスクが、年間最大 $180（≒2.8万円）の節約を桁違いに上回る。**やるなら1事業もやらず据え置き**が最適解。

---

## 2. CEO の前提崩れ（最重要・最初に直視）

| CEO の当初認識 | 実測事実（Vercel API で確認） | 含意 |
|---|---|---|
| 「$20 が事業ごと＝$20×7=$140/月」 | team `goodboulderings-projects`・**Pro 1本($20/月)に10プロジェクト全集約**（billing.plan=pro, active） | **$140 ではなく $20。節約見込みは実在しない** |
| 「Cloudflare の方が商用で安い」 | Cloudflare 商用も実運用なら Workers Paid **$5/月**が事実上必須 | 移行後コスト $5/月。**月の差は $15、年 $180** |

**実測コマンド結果（2026-05-22）**:
- `GET /v2/teams` → チーム1個のみ（`team_W9SCRWFpcGCWp6mtYgFIGXXw` / slug `goodboulderings-projects`）
- `GET /v2/teams/{id}` → `billing.plan=pro`, `billing.status=active`
- `GET /v9/projects` → 10プロジェクト全部この1チーム配下（ai-hub / minanowa / notesthe / n-design / business21 / trust / cma-vibe-0514-051921 / fadie-v2 / climbing-shoe-search / ambassador）

### さらに重い前提崩れ：10日前に自分で「Cloudflare撤退」を承認している

2026-05-12（`work/2026-05-12-render-cloudflare-slow-migration.md`）で CEO 自身が「**Cloudflare から撤退して Vercel に集約する**」ロードマップを承認。動機は「**コンソールが多すぎてしんどい・管理プラットフォームを減らしたい**」。

→ **今回の相談はその方針の180度反転**。CF全面移行すると、当時嫌った「複数コンソール」が「Cloudflare + Supabase（D1寄せなら実質DB2系統）」に変わるだけで、**「管理を減らす」目的は1ミリも達成されない**。

**本当に解きたい問題は「Vercel か Cloudflare か」ではなく「コンソール疲れをどう減らすか」**。それなら答えは移行ではない（§5）。

---

## 3. 6論点の数字比較

### 論点0: Vercelの商用利用は規約上クリアか（CEO追加質問・2026-05-22 公式ドキュメント確認）

**結論: 完全にクリア。むしろ好条件。**

| 確認項目 | 公式ドキュメントの事実 |
|---|---|
| 商用利用の可否 | 公式原文「Hobby teams are restricted to non-commercial personal use only. **All commercial usage requires either a Pro or Enterprise plan.**」→ **Proにいる限りクリア**。7事業の決済・広告・受託制作・寄付はすべて commercial usage 定義に該当するが、Pro なので問題なし |
| 1チームに何事業まで | **上限なし**。制限はリソース使用量(fair use)の閾値のみで、プロジェクト数・事業数での課金や制限は存在しない |
| $20の課金構造 | **Platform fee $20/月（固定）= deploying seat 1個 + $20分の使用クレジット込み**。CEOは1人運用なので $20/月で確定。seatは事業を増やしても増えない（deployする人を2人目以降に増やすときだけ +$20/人） |
| クレジット内包 | $20には**$20分の使用クレジットが内包**。さらに月1TB転送+1000万エッジreq+関数1000GB-Hrは別枠で込み（これを超えてから$20クレジット消費 → 使い切って初めて従量）。**実質「$20払うがその$20はほぼ使い切らない」状態** |

**移行判断への影響**: Cloudflare Workers Paid $5/月には**このクレジット内包構造がなく純従量**。Vercelの$20は「商用規約クリア + 枠超過なし + クレジット内包」とセットなので、年$180の節約メリットは**さらに薄まる**。

**唯一の注意点**: deploying seat を増やさないこと。将来エンジニアを雇い2人目がdeployすると +$20/月/人。ただしViewer（閲覧・コメント）は無制限無料なので、2029Q2撤退戦略の後継者引き継ぎでも譲渡完了まではViewerで足りる。

出典: [Fair Use Guidelines（公式・2026-02-27更新）](https://vercel.com/docs/limits/fair-use-guidelines) / [Pro Plan（公式・2026-02-26更新）](https://vercel.com/docs/plans/pro-plan)

---

### 論点1: コスト（最重要）

| 項目 | Vercel Pro（現状） | Cloudflare 全面移行後 |
|---|---|---|
| 基本月額 | **$20/月固定（1チーム集約済）** | Workers Paid **$5/月**（商用実運用で事実上必須） |
| 関数実行 | 約1,000 GB-hours/月込み | 1,000万req + 30M CPU-ms/月、超過 $0.30/百万req |
| 帯域 | 1TB/月込み、超過 $0.15/GB | **実質無制限・無料**（CFの強み） |
| Image最適化 | $0.05/1k変換（無料枠後） | 5,000変換/月無料、以降 $0.50/1k |
| Pro のクレジット | $20/月の使用クレジット付（超過相殺） | なし（純従量） |
| **7事業合算の現実月額** | **$20（超過していない＝クレジット内）** | **$5〜10（推測）** |

**年間節約は最大 $180（約2.8万円）**。これが「7事業を OpenNext 化する」対価。CEO 時給を仮に5,000円とすれば移行工数だけで55-87万円相当 → **回収に20〜30年**。

### 論点2: CDN速度・無料枠

| 項目 | Cloudflare | Vercel |
|---|---|---|
| 拠点数 | **330+都市**（人口95%に50ms以内） | 126 PoP / 94都市 / compute 20リージョン |
| アーキ | 全拠点で compute（真の分散エッジ） | ハブ&スポーク（PoPキャッシュ・compute集約） |
| 無料枠 | 10万req/日・商用OK | Hobby は商用NG |

**1000人規模での体感差: ほぼ出ない（根拠つき推測）**。7事業の利用者は彦根・滋賀中心の国内ユーザー → Vercel 東京リージョン(hnd1)で十分近い。CF「330都市」の優位はグローバル分散ユーザー（ClimbHeroのような世界配信）でのみ効く。1000人は同時接続でなく月間想定値で、秒間reqに換算すれば極小。**国内向け業務系で330 vs 94は計測誤差レベル**。

### 論点3: Next.js 親和性

| 項目 | Vercel | Cloudflare(OpenNext) |
|---|---|---|
| Next.js 15/16 | 公式・最速・即日対応 | Next.js 16全マイナー対応・15最新対応（14はQ1 2026終了） |
| Server Actions | ネイティブ・最安定 | 対応するが**Node runtime必須・Edge非対応** |
| ISR | ネイティブ | stale-while-revalidate で代替（挙動差あり） |
| Image最適化 | 標準（コード変更不要） | 要設定・一部 `unoptimized` 回避策 |
| 一部 Node API | 全対応 | **Workers で使えないNode APIあり**（bcrypt等注意） |

**CLAUDE.md の「OpenNext検証コスト > Vercel月$20」は2026時点でも妥当**。OpenNextは成熟したがISR挙動差・Edge非対応・Node API欠落は残存。集約済み$20が確定した今、不等式は前より**Vercel有利に傾いている**。

### 論点4: セキュリティ・ログイン1000人

**論点の核心の誤解**: 「ログイン1000人のセキュリティ」は**ホスティング（Vercel/CF）の問題ではなく、Supabase Auth + RLS + セッション管理の問題**。トラストの認証は LINE Login + iron-session + Supabase RLS で、Vercel でも CF でも認証ロジックは1行も変わらない。

CFの無料WAFは魅力だが、**親CLAUDE.md推奨の「DNSをCloudflareにしてVercel前段にCF WAFを被せる二段構成」が既に可能** → ホスティングを移さずWAFだけCFで被せられる。**WAF目的なら全面移行は不要**。

### 論点5: Supabase + D1統合で管理は減るか → **減らない。むしろ増える**

| 観点 | 実態 |
|---|---|
| D1 と Supabase は別物 | D1=Cloudflare SQLite / Supabase=Postgres。**「統合」概念が成立しない**（互換性なし） |
| 現状のDB | 4事業が**1つのSupabase Postgresに相乗り**（org単位・現Free）。管理は実質1コンソール |
| D1に寄せると | Supabase(Postgres/RLS/Auth/Storage)を捨ててD1(SQLite/認証なし/Storageなし)へ → **Auth/Storage/RLSを全部別物で作り直す**。みんなのWA画像もR2へ再移行 |
| 結果 | DBが**Postgres系統 + D1系統の2分裂**、または全面D1化なら**認証基盤の全面再実装** |

**CEOの「SupabaseをD1統合で管理を減らせる」は技術的に逆**。Supabaseは親CLAUDE.mdが「全プロジェクト共通DB層・不変・可搬性高い（Postgresはどこでも動く）」と位置づけた背骨。**D1に寄せると可搬性（=2029Q2全事業手放しの撤退戦略の前提）を自ら破壊する**。撤退時に後継エンジニアへ渡すなら汎用Postgres(Supabase)が圧倒的に引き継ぎやすい。

### 論点6: コンソール数（CEOの本来目的）

| | 現状 | CF全面移行後 |
|---|---|---|
| コンソール | Vercel + Cloudflare + Supabase | Cloudflare + Supabase（D1寄せなら実質DB2系統） |
| 数 | 3 | 2〜3（減ったように見えてCF内管理対象が激増） |

**「コンソールを減らす」目的なら正解は逆**。2026-05-12ロードマップどおり**Cloudflare撤退 → Vercel + Supabase の2コンソール**が目的に直行する。

---

## 4. ブランチ移行ケースの工数・リスク・切り戻しコスト

CEO依頼の「ブランチ切ってOpenNext化→CFデプロイ→検証→切戻し可能」前提。

### 1事業あたり工数（推計）

| 工程 | 時間 |
|---|---|
| ブランチ作成・`@opennextjs/cloudflare`導入・wrangler設定 | 2-3h |
| Edge runtime行除去・Node API依存の修正 | 3-6h |
| Server Actions / ISR 挙動差の検証・修正 | 4-8h |
| Image最適化のCF対応（or Supabase Storage origin化） | 2-4h |
| 環境変数のVercel→CF移植 | 1-2h |
| Previewデプロイ・実機検証・CEO確認 | 3-5h |
| **1事業計** | **15-28h** |

### 7事業合計

| 区分 | 事業 | 推計 |
|---|---|---|
| 軽量(LP系) | Nデザイン | 12-18h |
| 中量 | みんなのWA・AIハブ・ファディー | 各15-22h |
| 重量(業務系) | Notエステ・ビジネス21・トラスト | 各20-30h |
| **合計** | **7事業** | **110〜175h（推計）** |

> 「初回移行」のみの数字。OpenNextの**追従検証コスト（Next.js上げるたびに挙動差再検証）が恒久発生**する点が一発工数より重い。

### リスク

| リスク | 深刻度 | 備考 |
|---|---|---|
| Server Actions 挙動差 | 中 | Notエステ/ビジネス21/トラストの管理画面で顕在化しうる |
| ISR→SWR代替の挙動差 | 中 | ビジネス21はISR最適化済＝影響直撃 |
| Image最適化無効化 | 低-中 | Supabase Storage origin化で回避可だが工数 |
| Node API欠落(bcrypt等) | 中 | トラストのiron-session要確認 |
| **トラスト8/1本稼働直前の不安定化** | **高** | **最大リスク**。4棟・スタッフ17名・個人情報・法令遵守。2ヶ月前に基盤総入れ替えは事故誘発 |
| 本番切替ダウンタイム | 低 | ブランチ運用で最小化可 |
| DNS切替 | 中 | 取りこぼすとアクセス不能 |

### 切り戻しコスト

| 要素 | 戻せるか |
|---|---|
| コード | ✅ ブランチ破棄で完全に戻る |
| Vercel本番 | ✅ mainを触らなければ無傷 |
| 環境変数 | △ CF側に投入したsecretは手動削除（残骸） |
| **DNS** | ⚠️ CFに向けた後Vercelに戻すと最大48h伝播。**この間は不完全に戻る** |
| **D1にデータ移行した場合** | ❌ **完全には戻せない**。D1↔Supabaseは別物、書き戻し手作業＝**片道切符ポイント** |

**結論**: コードはブランチで戻せるが、**本番DNS切替・D1データ移行を一度でも本番でやると「完全な切り戻し」は崩れる**。気軽に試して戻せるのは**OpenNextビルド検証まで**。そこから先（本番DNS・データ移行）は不可逆領域。

---

## 5. 推奨アクション

### やるべきこと（CEO本来目的=コンソール削減に直行）

1. **全面移行はしない**。$180/年の節約のために110-175h+恒久検証コスト+トラスト本稼働リスクは経済的に破綻。
2. **2026-05-12の自分のロードマップに戻る**＝Cloudflare**撤退**方向。LINE Webhook 4本をVercel API Routeに移し、ClimbHero冷凍、DNSもVercelへ → **Vercel + Supabase の2コンソール**で「しんどい」が解消。移行と真逆だが目的に直行。
3. **WAFが本当に欲しいなら**ホスティングを動かさず**DNSだけCloudflare経由でVercel前段にCF WAFを被せる二段構成**（親CLAUDE.md推奨）。全面移行不要でCFの無料WAF/Bot対策が手に入る。
4. **Supabaseは死守**。D1寄せは可搬性（=2029Q2撤退時の後継エンジニア引き継ぎ）を破壊し、撤退戦略と正面衝突。

### 据え置くもの

- Vercel Pro 1チーム集約（現状最適・$20固定）
- Supabase相乗り（Free→トラスト8/1前のPro昇格判断は別件で保留中）
- ClimbHeroのCloudflare集約（例外継続・冷凍方針も既定）

### もし「それでも試したい」なら最小実験

**Nデザイン1事業だけ**ブランチでOpenNext化（最軽量・12-18h・本番DNS触らない・Preview URLで体感確認のみ）。これで「OpenNext検証コスト > 月$20」仮説を実データ確認できる。**トラスト/ビジネス21/Notエステは絶対に実験台にしない**（業務系・本稼働近い・個人情報）。

---

## 6. この推奨を覆す閾値（撤退基準＝監視ポイント）

- ①Vercel月額が従量超過込みで **$50超を恒常的に超える**
- ②帯域が **1TB/月を継続超過**（Vercel超過$0.15/GB vs CF無料で逆転しうる。月800GB超え始めたら再分析）
- ③国外ユーザーが **全体の30%超**（CFの330都市が効く）
- 将来グローバル展開＋大量メディア配信（ClimbHero復活時など）になればCF優位に転じる → その時は事業単位で再検討
- Vercelが値上げ or Pro $40化したら再計算

現状はどれも遠い。

---

## 出典

- [Cloudflare Workers Pricing (公式)](https://developers.cloudflare.com/workers/platform/pricing/)
- [Cloudflare Images Pricing (公式)](https://developers.cloudflare.com/images/pricing/)
- [Vercel Pricing (公式)](https://vercel.com/pricing) / [Image Optimization Pricing](https://vercel.com/docs/image-optimization/limits-and-pricing)
- [OpenNext Cloudflare (公式)](https://opennext.js.org/cloudflare)
- [Cloudflare 300+ cities network](https://blog.cloudflare.com/cloudflare-connected-in-over-300-cities/)
- 内部正本: `work/2026-05-12-render-cloudflare-slow-migration.md`（CEO過去判断=CF撤退方向）/ `トラスト.md`（8/1本稼働・Supabase相乗りFree）/ 親 `CLAUDE.md`（Vercel集約方針・OpenNext不等式）

**推測と明記した箇所**: 7事業合算の実従量($5-10/月)、1事業あたり移行工数(15-28h)、1000人規模の体感差、帯域将来予測 — いずれもWebSearchの実数（料金・拠点数・OpenNext対応）を土台にした見積もりで実機計測値ではない。確定数値はVercel APIの集約事実($20×1)とWebSearch取得の公式料金のみ。
