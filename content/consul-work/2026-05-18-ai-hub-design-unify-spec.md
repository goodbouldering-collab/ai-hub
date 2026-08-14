# AIハブ サイト内デザイン統一 指示書（Codex 委任用）

- **日付**: 2026-05-18
- **事業**: AIハブ（`C:\VSCode\Project\ai-hub\`）
- **発注**: CEO 由井辰美 →「トップページのデザインに全て細部まで合わせて」
- **CEO 承認状態**: 方針「段階的・見た目優先」を CEO 選択済（実装着手の最終承認は本書提示後に取得）
- **基準（正本）**: トップページ `index.html` = `site/build_portal.py` の `PORTAL_CSS`
- **本番URL**: `https://aiclimb.vercel.app/`（変更しない・このまま）

## 背景：デザインが割れている根本原因

サイトが**2つの生成系統**に分裂している:

| 系統 | 生成元 | CSS定数 | 生成ページ |
|---|---|---|---|
| **A（基準）** | `site/build_portal.py` | `PORTAL_CSS`（147行〜・約560行） | **index.html（トップ）** |
| **B（合わせる側）** | `site/build_site.py` | `CSS`（313行〜・約599行）+ `CONTENT_CSS`（912行〜・約584行） | speaker / profile / portfolio / lectures(index) / watch(index, 日次, archive) |

カラートークン（`:root`）とフォントは既に両系統でほぼ一致済み。**ズレているのはコンポーネントの細部実装**。

## 一致済み（触らない）

`PORTAL_CSS` と `build_site.py CSS` の `:root` は以下が完全一致。**変数の値は変更しない**:
`--bg-base:#f8fafc` / `--bg-white:#ffffff` / `--text:#0f172a` / `--text-soft:#334155` / `--primary:#2563eb` / `--primary-soft:#3b82f6` / `--primary-bg:#eff6ff` / font-family（apple-system 系）

## 統一タスク（B を A に細部まで合わせる）

`site/build_site.py` の `CSS` と `CONTENT_CSS` を編集し、以下を `PORTAL_CSS` の値・実装に揃える。**`PORTAL_CSS`（トップ）側は基準なので原則変更しない**（トップ専用レイアウト = `.hero` `.stats-strip` `.services-grid` `.service-card` `.hero-blob` `.hero-badge` は他ページに移植しない。これらはトップ専用）。

### T1. 共通基盤の同値化（最優先・低リスク）
`build_site.py CSS` の以下セレクタを `PORTAL_CSS` の対応セレクタと**ピクセル単位で一致**させる:
- `body`（背景：トップは単色基調。`build_site.py` 側の `radial-gradient` 多重背景 + `background-attachment: fixed` を **PORTAL_CSS の body 背景に置換**）
- `.container`（max-width / padding を PORTAL_CSS に合わせる）
- `header.site-header` / `.site-header-inner` / `.site-logo` / `.site-logo .dot` / `.login-btn` / `.scrolled` 状態（PORTAL_CSS が正・差分を吸収）
- `::selection`

### T2. ナビゲーションの統一（中リスク）
- `build_site.py` 側の旧タブ UI（`.genre-tabs` `.genre-tab` `.sub-tabs` `.sub-tab`）は **watch ページの機能上必要なら残す**が、**配色・角丸・hover を PORTAL_CSS の `.site-nav a` / `.nav-link` のトーンに合わせる**（`--primary-bg` hover・`--primary` active）。機能 DOM は壊さない
- 他ページ（speaker/profile/portfolio/lectures）のヘッダーは既に `render_top_nav()` 共通化済 → CSS だけ PORTAL_CSS 準拠に

### T3. ボタン体系の移植（中リスク）
`PORTAL_CSS` の `.btn` / `.btn-primary` / `.btn-secondary` / `.btn-ghost`（影・角丸・hover transform 含む）を `build_site.py CSS` に**そのままコピー**。他ページ内の既存ボタン的要素（`.back-to-top` 等）も見た目をこのトーンに寄せる（機能は維持）

### T4. カード装飾の調和（CONTENT_CSS・要注意）
`CONTENT_CSS` の独自カード（`.pf-card` `.tr-grid` `.tr-section` `.content-toc` `.content-wrap` 等）を、`PORTAL_CSS` の `.service-card` の**装飾言語**（border / border-radius / box-shadow / hover の translateY と shadow 強度 / 余白）に合わせる。
- **構造（grid 列数・コンテンツ量依存のレイアウト）は変えない**。変えるのは「枠線・角丸・影・hover・余白・見出し色」の見た目だけ
- `.content-wrap a:hover` の `--accent3`（ピンク）など PORTAL_CSS に無いアクセントは **PORTAL_CSS のトーン（`--primary` 系）に置換**
- `.grad`（虹色グラデ見出し）が他ページにあれば、トップの見出し表現に合わせる（トップが単色なら単色へ）

### T5. アクセント変数の整理（低〜中リスク）
`build_site.py CSS` の `--accent2:#8b5cf6` / `--accent3:#ec4899` / `--glass-*` / `--shadow-card*` のうち、**PORTAL_CSS に存在しないものを使っている箇所**は PORTAL_CSS のトークン（`--primary` 系・PORTAL_CSS の影定義）に置換。未使用になった変数は削除可

## 厳守事項（事故防止）

1. **`site/dist/` を直接編集しない**。`dist/` は生成物。**必ず `build_site.py` / `build_portal.py`（生成元）を編集**し、ビルドで `dist/` を再生成して検証する
2. **`PORTAL_CSS`（トップ）は原則変更禁止**。トップが基準。例外的に変更が必要なら理由を明記して報告（CEO 判断）
3. **機能 DOM・JS フック（`id` / `data-*` / class の JS 参照）を壊さない**。CSS の見た目のみ変更
4. **カラーミー連携マーカー** `<!-- BEGIN:AI_GROUP_ARTICLES -->` 内側は触らない
5. **`http://` リテラルを増やさない**（親 CLAUDE.md ミックスコンテンツ規約）
6. ビルド検証コマンド: `cd C:\VSCode\Project\ai-hub && python site/build_site.py`（`_build_portal()` も内部呼出しされる）→ `site/dist/*.html` を目視差分
7. `.env` / トークンに触れない。秘密情報を diff に出さない
8. **commit / push はしない**。差分を作るところまで。レビューと push は Claude 側（consul 安全ゲート経由）が実施

## 完了条件

- `python site/build_site.py` がエラーなく完走
- `index.html`（トップ）の見た目が**変わっていない**こと（基準なので不変が正しい）
- speaker / profile / portfolio / lectures/index / watch/index がトップと**同じヘッダー・ボタン・カード・背景・余白の言語**になっている
- 変更が `build_site.py`（および必要なら `build_portal.py` だが原則不変）に閉じ、`dist/` は再生成結果のみ差分

## 成果報告フォーマット（Codex → Claude）

- 変更ファイルと行数
- T1〜T5 各タスクの実施可否と理由
- `PORTAL_CSS` を変更した場合はその全箇所と理由
- ビルド成否
- 残課題・判断を仰ぎたい点

---

## 実施結果（2026-05-18 Claude 実装）

2026-05-18 codex:codex-rescue 発火（ai-hub/デザイン統一の重い改修=入口判定で重い3条件該当/Codexサンドボックス書込拒否で実装不能→Claude直接実装に切替）

- **変更ファイル**: `site/build_site.py` のみ（+63/-54行・CSS と CONTENT_CSS のみ）。`build_portal.py`（PORTAL_CSS=基準）は**一切変更せず**
- **T1**（共通基盤）: 実施。`.container` 1100→1200px、`header.site-header` を PORTAL と同一の「無印=透明fixed / `.scrolled`=bg+blur」方式に。生成ページは `<header class='site-header scrolled'>` 静的付与のため JS 不要でトップと一致
- **T2**（ナビ/watch系）: 実施。`.group-label`/`.support-sns h2`/`header h1 .grad`/`.meta .rank`/`.thumb.placeholder` の虹色・紫・ピンクグラデを PORTAL 単色トーンへ
- **T3**（ボタン）: 実施。PORTAL の `.btn/.btn-primary/.btn-secondary/.btn-ghost` を CSS に同一定義で移植（CONTENT_CSS は `{CSS}{CONTENT_CSS}` 結合出力のため重複追加不要と判明）
- **T4**（カード/見出し）: 実施。`content-wrap`/`pf-card`/`tr-*`/`profile-*` のグラデ見出しを単色化、ピンクchip・紫グラデ背景を primary トーンへ、`.profile-stat` を PORTAL `.stat` と完全一致に
- **T5**（変数）: 実施。`--accent1/2/3` を全て `#2563eb`(primary) に統一（既存セレクタ参照を壊さず虹グラデを実質単色化）、`--glass-border` を `#e2e8f0`(=--line) 化、PORTAL の `--emerald/--amber/--pink` を追加
- **PORTAL_CSS 変更**: なし（基準のため不変が正しい）
- **ビルド**: `python site/build_site.py` EXIT 0 完走。**トップ index.html の md5 がビルド前後で完全一致**（`709d848c...`）＝基準は1pxも不変。生成物の旧トーン（虹グラデ/`#be185d`/`255,122,182`）は speaker/portfolio/profile/watch で全て 0 件
- **安全ゲート**: ①ビルド完走 ②diff に秘密情報 0 件 ③単一目的1コミット → 全通過
- **残課題**: なし（`var(--accent1)` 等の残存参照は値が primary のため見た目影響なし。将来の整理対象だが今回スコープ外）
