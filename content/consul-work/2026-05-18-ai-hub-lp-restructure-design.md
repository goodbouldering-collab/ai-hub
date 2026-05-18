# AIハブ TOP LP型再構成 + 管理画面UI統一 設計書

- **日付**: 2026-05-18
- **事業**: AIハブ（`C:\VSCode\Project\ai-hub\`）
- **発注**: CEO「メニューにある項目を全てTOPのセクションに追加、構成を考えてページも作る。管理ページも同じUIで完全統一」
- **CEO確定方針**: ① TOP = 1ページLP型（全セクション集約・個別ページは詳細版として残す） ② 管理画面は /admin・/ops・ローカルFastAPI の3つすべて TOP と同じUIに統一
- **基準デザイン**: トップ PORTAL_CSS（先のデザイン統一作業で全ページ統一済み）

## 現状のTOPセクション構成（build_portal.py）

```
hero → stats → gallery(事例) → services(提供6つ) → works(事業ポートフォリオ)
  → flow(依頼の流れ) → profile(簡易プロフィール) → news(講習資料3件) → faq → contact
```

## メニュー項目（build_site.py NAV）とのギャップ

| メニュー | href | TOP対応 | 対応方針 |
|---|---|---|---|
| 講師紹介 | speaker.html | **なし** | 新規セクション `#speaker` 追加（content/speaker.md から要約） |
| 経歴 | profile.html | 簡易 `#profile` のみ | `#profile` を config/profile.yaml の timeline/stats で充実化 |
| 実績 | portfolio.html | works(事業)とは別物 | 新規セクション `#portfolio` 追加（config/portfolio.yaml 14件） |
| 講習資料 | lectures/index.html | news 3件プレビュー | `#lectures` セクションに拡充（全件 + DL動線） |
| プログラミングマップ | programming-map.html | なし | `#lectures` 内にリンクカードで内包（現lectures踏襲） |
| 過去ログ | archive.html | なし | フッターリンク扱い（LPに節は作らない） |

## 再構成後のTOPセクション構成（案）

```
hero
 → stats
 → speaker      ★新規：講師紹介（content/speaker.md 要約 + 詳細ページへ）
 → profile      ◇拡充：経歴（profile.yaml の timeline/stats/tech）
 → services     （現状維持：提供6つ）
 → portfolio    ★新規：制作実績（portfolio.yaml 14件カード + 詳細ページへ）
 → works        （現状維持：事業ポートフォリオ）
 → lectures     ◇拡充：講習資料（全件 + programming-map リンク + DL動線）
 → gallery      （現状維持：事例ギャラリー）
 → flow         （現状維持：依頼の流れ）
 → faq          （現状維持）
 → contact      （現状維持）
footer：過去ログ / 各詳細ページへのリンク
```

セクション順序の意図：**人物(speaker→profile)→ できること(services)→ 証拠(portfolio→works)→ 学べる(lectures)→ 事例→流れ→FAQ→CTA** という説得の流れ（LPのセオリー：誰が→何を→実績→行動）。

## ナビゲーション改修

- トップナビの各項目を **アンカーリンク（`#speaker` 等）に変更**（LP内スクロール）
- 各セクション末尾に「詳細を見る →」リンクで個別ページ（speaker.html等）へ誘導
- 個別ページ（speaker/profile/portfolio/lectures）は**詳細版として存続**（SEO・直リンク用）

## 実装タスク

| # | 内容 | 対象 | リスク |
|---|---|---|---|
| L1 | `_render_speaker_section()` 新規（speaker.md 要約） | build_portal.py | 中 |
| L2 | `_render_profile()` を profile.yaml の timeline/stats で拡充 | build_portal.py | 中 |
| L3 | `_render_portfolio_section()` 新規（portfolio.yaml 14件） | build_portal.py | 中 |
| L4 | `_render_lectures_section()` 新規（全lectures + pmap + DL） | build_portal.py | 中 |
| L5 | render_portal のセクション組み立て順を新構成に再配置 | build_portal.py | 高（順序変更） |
| L6 | ナビをアンカーリンク化 + 各セクションに詳細ページ導線 | build_portal.py | 中 |
| L7 | 管理画面UI統一：/admin・/ops・ローカルFastAPI を PORTAL トーンに | static/admin/* static/ops/* admin/server.py 由来HTML | 中 |
| L8 | ビルド検証・トップ以外の個別ページが壊れていないこと | python site/build_site.py | — |

## 厳守事項

1. `site/dist/` 直接編集禁止。生成元（build_portal.py / build_site.py / static/）を編集
2. 個別ページ（speaker/profile/portfolio/lectures.html）は**詳細版として残す**（消さない）
3. PORTAL_CSS のデザイン言語を踏襲（先の統一作業の成果を壊さない）
4. content/*.md・config/*.yaml の**コンテンツソースは改変しない**（表示の組み替えのみ）
5. 機能DOM・JSフック・カラーミーマーカーを壊さない
6. `.env`/トークンに触れない・http:// を増やさない
7. commit/push は安全ゲート（ビルド完走・秘密情報なし・意味ある単位）通過後

## 完了条件

- `python site/build_site.py` 完走
- TOPに speaker/profile/portfolio/lectures セクションが追加され、ナビがアンカー化
- 個別詳細ページが従来通り存続・破損なし
- /admin・/ops・ローカルFastAPI が TOP と同じデザイン言語
