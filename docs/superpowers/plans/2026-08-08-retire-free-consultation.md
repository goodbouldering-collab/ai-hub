# 無料相談廃止と申込導線の再編 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通常の公開サイトから無料相談を廃止し、60秒診断を完了した人だけが無料相談を選べる例外を残しつつ、他の申込導線をAI個別相談またはAIエージェント講習へ正しく振り分ける。

**Architecture:** `site/build_portal.py` を唯一の申込導線定義として更新し、個別相談、AIエージェント講習、診断内限定無料相談のURLを定数化する。ホーム、JSON-LD、公開ブログは有料メニューだけを参照し、60秒診断だけが `free` 結果から無料相談URLを参照する。静的生成で `site/dist/` へ反映する。

**Tech Stack:** Python 3.12、静的HTML生成、`unittest`、Vercel、Square Appointments。

## Global Constraints

- 無料相談、無料で相談、初回無料、0円の入口整理、旧無料相談Square URLは、60秒診断モーダルの選択肢と `free` 結果以外の公開生成物と再利用可能なサイト生成ソースに残さない。
- 課題整理・導入設計はAI個別相談（60分・5,500円）へ、実作業を作りながら学ぶ導線はAIエージェント講習（120分・5,500円）へ送る。
- 個別相談URLは `https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP`、AIエージェント講習URLは `https://goodbouldering.com/?pid=188553378` を使う。
- 診断内限定の無料相談URLは `https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE` とし、JSON-LDには載せない。
- `content/consul-work/` の過去施策記録と、Square・カラーミー側の設定は変更しない。
- 既存のユーザー変更は触れず、隔離した作業ツリーのブランチだけを更新する。

---

### Task 1: 無料相談廃止の回帰契約を追加する

**Files:**
- Create: `tests/test_free_consultation_retirement.py`
- Modify: `tests/test_hero_60sec_diagnosis.py`

**Interfaces:**
- Consumes: `site/dist/index.html`、`site/dist/blog/2026-07-27-codex-remote-ssh-rdp.html`、`site/build_portal.py`。
- Produces: 公開ページ・構造化データ・60秒診断の申込先を検査する `FreeConsultationRetirementTests`。

- [ ] **Step 1: 失敗する公開導線テストを書く**

```python
OLD_FREE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
)
INDIVIDUAL_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
)
AGENT_URL = "https://goodbouldering.com/?pid=188553378"

def test_free_consultation_is_limited_to_the_diagnosis_modal(self):
    before_modal, modal = self.index_html.split("<div class='diagnose-modal'", 1)
    self.assertNotIn("無料相談", before_modal)
    self.assertNotIn(OLD_FREE_URL, before_modal)
    self.assertIn("無料相談で入口を整理したい", modal)
    self.assertIn(OLD_FREE_URL, modal)
    self.assertNotIn("無料相談", self.remote_blog_html)
    self.assertNotIn(OLD_FREE_URL, self.remote_blog_html)

def test_schema_keeps_paid_individual_consultation_and_agent_course(self):
    services = json.loads(self.json_ld)["@graph"]
    names = {service.get("name") for service in services}
    self.assertNotIn("AI無料相談 入口整理", names)
    individual = next(service for service in services if service.get("name") == "AI個別相談 しっかり60分")
    self.assertEqual("5500", individual["offers"]["price"])
    self.assertEqual(INDIVIDUAL_URL, individual["offers"]["url"])
    agent = next(service for service in services if service.get("name") == "AIエージェント講習 120分")
    self.assertEqual(AGENT_URL, agent["offers"]["url"])
```

- [ ] **Step 2: 失敗を確認する**

Run:

```powershell
$python = 'C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = "$PWD\.venv\Lib\site-packages"
& $python -m unittest tests.test_free_consultation_retirement tests.test_hero_60sec_diagnosis -v
```

Expected: モーダル外の `無料相談` と旧Square URL、無料のJSON-LDサービス、ヒーローの旧CTAを検出して失敗する。診断モーダル内の例外はまだ未実装のため、その契約も失敗する。

- [ ] **Step 3: 60秒診断の目的別CTA契約を追加する**

`tests/test_hero_60sec_diagnosis.py` を、単一の予約URLではなく次の5結果を検査するよう更新する。

```python
expected_routes = {
    "start": ("AI個別相談を予約する", INDIVIDUAL_URL),
    "promotion": ("AIエージェント講習を予約する", AGENT_URL),
    "office": ("AI個別相談を予約する", INDIVIDUAL_URL),
    "flow": ("AI個別相談を予約する", INDIVIDUAL_URL),
    "free": ("無料相談の日程を選ぶ", OLD_FREE_URL),
}
for key, (label, url) in expected_routes.items():
    self.assertIn(f"{key}: {{", self.index_html)
    self.assertIn(label, self.index_html)
    self.assertIn(url, self.index_html)
```

- [ ] **Step 4: テストの失敗内容を確認する**

Run the same command as Step 2.

Expected: `promotion` が講習URLを持たず、`free` 結果が診断内無料URLを持たず、その他の結果が個別相談URLを持たず、ヒーローと問い合わせ欄が旧無料URLを使っているため失敗する。

- [ ] **Step 5: テスト追加をコミットする**

```powershell
git add tests/test_free_consultation_retirement.py tests/test_hero_60sec_diagnosis.py
git commit -m "test: cover free consultation retirement"
```

### Task 2: 公開コピー・予約先・構造化データを置き換える

**Files:**
- Modify: `site/build_portal.py:119-320`
- Modify: `site/build_portal.py:9710-10343`
- Modify: `site/build_portal.py:10466-11868`
- Modify: `site/build_portal.py:14500-14755`
- Modify: `content/blog/2026-07-27-codex-remote-ssh-rdp.md:281`

**Interfaces:**
- Consumes: Task 1の `OLD_FREE_URL`、`INDIVIDUAL_URL`、`AGENT_URL` と結果キー `start` / `promotion` / `office` / `flow` / `free`。
- Produces: `INDIVIDUAL_CONSULT_BOOK_URL`、`DIAGNOSIS_FREE_CONSULT_BOOK_URL`、目的別 `RESULT` CTA、無料相談を含まないJSON-LDと、診断内だけに無料相談を閉じ込めた公開コピー。

- [ ] **Step 1: 個別相談URLを明示的な定数に置き換える**

`site/build_portal.py` の旧 `CONSULT_BOOK_URL` を削除し、次の定数を導入する。

```python
INDIVIDUAL_CONSULT_BOOK_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
)
AI_AGENT_COURSE_URL = "https://goodbouldering.com/?pid=188553378"
DIAGNOSIS_FREE_CONSULT_BOOK_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
)
```

JSON-LDの `plans` から `AI無料相談 入口整理` を削除し、`AI個別相談 しっかり60分` の `Offer` と `Service` に `INDIVIDUAL_CONSULT_BOOK_URL` を設定する。

- [ ] **Step 2: 先のテストを通す最小実装を行う**

ヒーロー、問い合わせ欄、ヘッダー、モバイルメニュー、フッター、FAQ、コース説明の無料相談表記を、次の目的別コピーへ変更する。

```text
AI個別相談を予約する
AI個別相談の日程を選ぶ
AI個別相談で、今の課題を整理する
60分・5,500円
```

「投稿文や画像などを一つ作る」「講習で作りながら学びたい」を含む60秒診断の `promotion` 結果だけは、次のCTAを表示する。

```text
AIエージェント講習を予約する
120分・5,500円
```

`start`、`office`、`flow` は個別相談のCTAとする。診断の第3問は「個別相談で課題を整理したい」と「無料相談で入口を整理したい」を選べるようにし、後者は `free` の結果を直接優先する。`free` の主CTAは次の文言とURLにする。

```text
無料相談の日程を選ぶ
https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE
```

診断スクリプトは同点順序に依存させず、`free` を選んだ時点で `forcedResult = 'free'` を保存する。結果表示では `forcedResult || scoreBestResult` を使う。

```javascript
var forcedResult = null;

if (opt.getAttribute('data-key') === 'free') forcedResult = 'free';

var best = forcedResult || scoreBestResult();
```

- [ ] **Step 3: 公開ブログのCTAを置き換える**

`content/blog/2026-07-27-codex-remote-ssh-rdp.md` のリンクを次に置き換える。

```html
<a href="/#contact">AI個別相談でPC構成を整理する</a>
```

- [ ] **Step 4: 対象テストを通す**

Run:

```powershell
$python = 'C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = "$PWD\.venv\Lib\site-packages"
& $python site\build_portal.py
& $python -m unittest tests.test_free_consultation_retirement tests.test_hero_60sec_diagnosis -v
```

Expected: 診断モーダル外の無料相談表記・旧URL・0円Offerがなく、`start` / `promotion` / `office` / `flow` / `free` のCTA先が仕様どおりになる。

- [ ] **Step 5: 導線実装をコミットする**

```powershell
git add site/build_portal.py content/blog/2026-07-27-codex-remote-ssh-rdp.md site/dist/index.html site/dist/blog/2026-07-27-codex-remote-ssh-rdp.html
git commit -m "feat: route free consultation traffic to paid offers"
```

### Task 3: 生成物・回帰・本番を検証する

**Files:**
- Modify: `site/dist/index.html`
- Modify: `site/dist/blog/2026-07-27-codex-remote-ssh-rdp.html`
- Verify: `tests/`

**Interfaces:**
- Consumes: Task 2で更新した生成ソースとブログMarkdown。
- Produces: 無料相談が60秒診断内だけに限定された公開静的サイトと、検証済みのmainデプロイ。

- [ ] **Step 1: 静的サイト全体を生成する**

```powershell
$python = 'C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = "$PWD\.venv\Lib\site-packages"
$env:AIWATCH_PORTFOLIO_NO_FETCH = '1'
& $python site\build_portal.py
& $python site\build_site.py
```

- [ ] **Step 2: 公開生成物の禁止語と旧予約先を検査する**

```powershell
rg -n -i '無料相談|無料で相談|初回無料|AW5O5XSBHLEHYUBHLZUGFKYE' site\dist
```

Expected: `site/dist/index.html` の60秒診断モーダルにだけ無料相談と旧Square URLが残り、その他の公開ファイルとモーダル外には残らない。過去施策記録の `content/consul-work/` はこの検査対象に含めない。

- [ ] **Step 3: 全自動テストと差分検査を通す**

```powershell
$python = 'C:\Users\yui\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = "$PWD\.venv\Lib\site-packages"
& $python -m unittest discover -s tests -v
git diff --check
```

Expected: 全テストが成功し、空白エラーがない。

- [ ] **Step 4: 本番反映前に最新mainを取り込む**

```powershell
git fetch origin main
git rebase origin/main
```

Expected: 競合なし。競合した場合は無料相談導線に関わる行だけを解消し、他の変更を保持する。

- [ ] **Step 5: mainへ反映してVercel本番を確認する**

```powershell
git push origin HEAD:main
```

確認するURLは `https://ai-hub-jp.vercel.app`。PC幅とiPhone幅で、ヒーロー、60秒診断の5結果、問い合わせ欄、モバイルメニュー、ブログCTAを確認する。外部予約ページは開かず、`href`、`target="_blank"`、文言、横スクロールなしをブラウザーで確認する。

- [ ] **Step 6: 最終コミットの状態を確認する**

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected: 作業ツリーがクリーンで、`HEAD` と `origin/main` が同じコミットを指す。
