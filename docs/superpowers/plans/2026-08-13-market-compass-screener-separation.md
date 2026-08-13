# Market Compass Screener Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 既存の相場羅針盤URLと総合表示を維持したまま、財務一次スクリーニングを独立サービス化し、相場羅針盤内の全機能を保護された独立管理ページとして提供する。

**Architecture:** `market-compass-screener` は株価・財務・配当・出典を正規化して12項目を評価する非公開Vercel APIとし、AI相談は既存管理認証を持つBFFと表示だけを担当する。AI相談からサービスへはサーバー間トークンで接続し、サービス停止時は既存の価格モメンタム表示だけへフォールバックする。

**Tech Stack:** Node.js 20、TypeScript 5、Vercel Functions、Node test runner + `tsx`、Supabase PostgreSQL、既存のHTML/CSS/vanilla JavaScript管理画面。

## Global Constraints

- 既存URL `https://aiclimb.vercel.app/admin/command-center/trade` と現在の総合表示を残す。
- 新ページは `market`、`screener`、`security`、`trade-plan`、`trade-plans`、`trades`、`market-sources` の7画面とし、共通管理メニューから到達可能にする。
- スクリーニング結果は「一次調査候補」「監視」「優先度を下げる」「データ不足」とし、「買い」「売り」「推奨」を表示しない。
- 財務判定は日本株を対象とする。米国株は既存の価格候補表示を維持し、財務判定対象外と明記する。
- 数値には対象期間、取得日時、出典、予想値または実績値の区別を付け、欠損を0へ変換しない。
- 一般企業の自己資本比率40%基準を銀行・保険・REITへ適用しない。不動産は負債・CFも併記する。
- `MARKET_COMPASS_SERVICE_TOKEN` はブラウザ、HTML、JSONレスポンス、ログへ出さない。
- 新サービスはトークン未設定を503、ヘッダー欠落を401、不一致を403で返す。`/api/health` は秘密を含まない。
- Supabaseは専用 `market_compass` スキーマを使い、全テーブルでRLSを有効にする。
- 公開、注文、売買、証券口座連携、自動取引は実装しない。
- PC 1440pxとiPhone 390pxで固定メニュー、横スクロール、表、フォーム、コントラスト、コンソールエラーを確認する。

---

## File Map

### New repository: `C:\Project\market-compass-screener`

- `package.json`, `tsconfig.json`, `vercel.json`: Node/TypeScript/Vercel構成とテスト・型検査・cron。
- `src/contracts.ts`: APIとルールエンジンが共有する型。
- `src/auth.ts`, `src/http.ts`: サービス間認証、入力制限、JSON応答。
- `src/rules.ts`, `src/overall.ts`: 12項目の純粋判定と総合状態。
- `src/providers/yahoo.ts`: 株価、年次財務、配当履歴の取得・正規化。
- `src/providers/edinet.ts`, `src/providers/jquants.ts`, `src/providers/jpx.ts`: 設定時の一次情報補完と未設定状態の明示。
- `src/collect.ts`: 出典優先順位、競合、鮮度、欠損を統合。
- `src/repository.ts`: Supabaseへのスナップショットと実行結果保存。
- `src/service.ts`: 市場候補・銘柄詳細・複数銘柄スクリーニングのユースケース。
- `api/health.ts`, `api/v1/market.ts`, `api/v1/screens.ts`, `api/v1/securities/[symbol].ts`, `api/v1/sources/status.ts`, `api/cron/refresh.ts`: Vercel API。
- `supabase/migrations/20260813000000_market_compass_schema.sql`: 専用スキーマ、テーブル、索引、RLS。
- `tests/fixtures/*.json`, `tests/*.test.ts`: ルール、欠損、業種、取得、認証、API契約のテスト。
- `.env.example`, `README.md`: 秘密を含まない設定と運用手順。

### Existing repository: `C:\Project\AI相談`

- `api/_lib/market-compass-client.ts`: サービスURL・トークン・タイムアウトを一箇所に閉じ込めるBFFクライアント。
- `api/_lib/command-center-market.ts`: 現行価格取得をフォールバックとして保持。
- `api/admin/command-center-market.ts`: 新サービス優先、失敗時は現行価格取得へ戻す。
- `api/admin/command-center-screen.ts`, `command-center-security.ts`, `command-center-market-sources.ts`: 管理認証付きBFF。
- `api/admin/command-center-page.ts`, `vercel.json`: 7つの独立ページと3つのBFFルートを許可。
- `site/static/admin/command-center.html`: 相場羅針盤の第2階層メニュー。
- `site/static/admin/command-center.js`: 総合画面を共通部品へ分割し、7画面を描画。
- `site/static/admin/command-center.css`: 判定カード、出典、警告、モバイル表示。
- `site/static/admin/admin-menu.js`: 共通モバイル管理メニューに相場羅針盤ページ一覧を表示。
- `tests/command-center-*.test.mjs`: ルート、認証、トークン非露出、フォールバック、表示契約。
- `.env.example`, `README.md`: `MARKET_COMPASS_SERVICE_URL` とサービス間トークンの説明。

---

### Task 1: Create the isolated service scaffold and authentication contract

**Files:**
- Create: `C:\Project\market-compass-screener\package.json`
- Create: `C:\Project\market-compass-screener\tsconfig.json`
- Create: `C:\Project\market-compass-screener\vercel.json`
- Create: `C:\Project\market-compass-screener\src\auth.ts`
- Create: `C:\Project\market-compass-screener\src\http.ts`
- Create: `C:\Project\market-compass-screener\api\health.ts`
- Create: `C:\Project\market-compass-screener\tests\auth.test.ts`

**Interfaces:**
- Produces: `authorizeService(req: IncomingMessage): AuthResult` where `AuthResult` is `{ ok: true } | { ok: false; status: 401 | 403 | 503; code: string }`.
- Produces: `json(res, status, payload)` and `readJson(req, maxBytes)` for all API handlers.

- [ ] **Step 1: Write the failing authentication test**

```ts
test("service token contract is explicit", () => {
  assert.deepEqual(authorizeService(request({} as never), {}), { ok: false, status: 503, code: "service_token_unset" });
  assert.deepEqual(authorizeService(request({} as never), { MARKET_COMPASS_SERVICE_TOKEN: "secret" }), { ok: false, status: 401, code: "service_token_required" });
  assert.deepEqual(authorizeService(request({ "x-market-compass-service-token": "wrong" }), { MARKET_COMPASS_SERVICE_TOKEN: "secret" }), { ok: false, status: 403, code: "service_token_invalid" });
  assert.deepEqual(authorizeService(request({ "x-market-compass-service-token": "secret" }), { MARKET_COMPASS_SERVICE_TOKEN: "secret" }), { ok: true });
});
```

- [ ] **Step 2: Run the test and verify the missing module failure**

Run: `npm.cmd install && npm.cmd test -- tests/auth.test.ts`

Expected: FAIL because `src/auth.ts` does not exist.

- [ ] **Step 3: Implement constant-time token validation and bounded JSON parsing**

```ts
export function authorizeService(req: IncomingMessage, env = process.env): AuthResult {
  const expected = env.MARKET_COMPASS_SERVICE_TOKEN?.trim();
  if (!expected) return { ok: false, status: 503, code: "service_token_unset" };
  const supplied = header(req, "x-market-compass-service-token");
  if (!supplied) return { ok: false, status: 401, code: "service_token_required" };
  return safeEqual(supplied, expected) ? { ok: true } : { ok: false, status: 403, code: "service_token_invalid" };
}
```

- [ ] **Step 4: Add an unauthenticated secret-free health handler and Vercel limits**

`GET /api/health` returns only `{ "ok": true, "service": "market-compass-screener", "version": 1 }`. Configure Node 20, a 10-second function timeout, and cron `0 22 * * 1-5` (JST 07:00 on weekdays).

- [ ] **Step 5: Run tests and type checking**

Run: `npm.cmd test && npm.cmd run typecheck`

Expected: PASS with no token value in snapshots or output.

- [ ] **Step 6: Commit the scaffold**

```powershell
git add package.json package-lock.json tsconfig.json vercel.json src api tests
git commit -m "feat: scaffold protected market compass service"
```

### Task 2: Define normalized evidence and implement the 12 screening rules

**Files:**
- Create: `C:\Project\market-compass-screener\src\contracts.ts`
- Create: `C:\Project\market-compass-screener\src\rules.ts`
- Create: `C:\Project\market-compass-screener\src\overall.ts`
- Create: `C:\Project\market-compass-screener\tests\fixtures\general-growth.json`
- Create: `C:\Project\market-compass-screener\tests\fixtures\missing-and-loss.json`
- Create: `C:\Project\market-compass-screener\tests\fixtures\sector-profiles.json`
- Create: `C:\Project\market-compass-screener\tests\rules.test.ts`

**Interfaces:**
- Produces: `NormalizedSecurity`, `FinancialPeriod`, `DividendYear`, `EvidenceRef`, `RuleResult`, `ScreenResult`, `MetricStatus`, `OverallStatus`.
- Produces: `evaluateRules(security: NormalizedSecurity): RuleResult[]` with IDs `growth_3y`, `equity_ratio`, `payout_ratio`, `dividend_growth_years`, `per`, `operating_cash_flow`, `interest_bearing_debt`, `eps_growth`, `dividend_cash_cover`, `one_off_profit`, `company_forecast`, `historical_valuation`.
- Produces: `classifyOverall(results: RuleResult[]): { status: OverallStatus; coverage: number; failedCritical: string[] }`.

- [ ] **Step 1: Write table-driven failing tests for every rule**

```ts
const expected = new Map([
  ["growth_3y", "pass"], ["equity_ratio", "pass"], ["payout_ratio", "pass"],
  ["dividend_growth_years", "pass"], ["per", "pass"], ["operating_cash_flow", "pass"],
  ["interest_bearing_debt", "pass"], ["eps_growth", "pass"], ["dividend_cash_cover", "pass"],
  ["one_off_profit", "pass"], ["company_forecast", "pass"], ["historical_valuation", "pass"],
]);
for (const item of evaluateRules(generalGrowthFixture)) assert.equal(item.status, expected.get(item.id), item.id);
```

Add explicit cases for negative EPS, zero profit, missing capex, changing fiscal-period length, three consecutive debt increases, negative OCF, missing forecast, source conflict, bank, insurance, real estate, and REIT.

- [ ] **Step 2: Run the tests and verify the missing evaluator failure**

Run: `npm.cmd test -- tests/rules.test.ts`

Expected: FAIL because `evaluateRules` is undefined.

- [ ] **Step 3: Implement typed rule helpers without truthy numeric checks**

```ts
type MetricStatus = "pass" | "check" | "fail" | "na" | "missing";

function strictlyIncreasing(values: Array<number | null>): MetricStatus {
  if (values.some((value) => value === null)) return "missing";
  const [a, b, c] = values as number[];
  return a < b && b < c ? "pass" : "fail";
}
```

Each `RuleResult` must contain `label`, `status`, `value`, `threshold`, `explanation`, `periods`, `observedAt`, `evidence`, and `missingFields`.

- [ ] **Step 4: Implement exact sector behavior**

Use `general`, `bank`, `insurance`, `real_estate`, and `reit`. Return `na` for the general-equity rule on bank/insurance/REIT. Return `check` rather than a mechanical fail for real estate and include net D/E and debt evidence. Return `na` for rules that do not map to REIT accounting.

- [ ] **Step 5: Implement overall classification**

Coverage is rules with `pass|check|fail` divided by applicable rules. Below 60% is `insufficient_data`; a critical failure in growth, OCF, forecast, or positive earnings is `deprioritize`; remaining checks or coverage below 80% are `watch`; otherwise `research_candidate`.

- [ ] **Step 6: Run all rule tests and commit**

Run: `npm.cmd test -- tests/rules.test.ts && npm.cmd run typecheck`

Expected: PASS for all fixtures.

```powershell
git add src/contracts.ts src/rules.ts src/overall.ts tests
git commit -m "feat: evaluate twelve fundamental screening checks"
```

### Task 3: Collect Yahoo market/fundamental data and expose source quality

**Files:**
- Create: `C:\Project\market-compass-screener\src\providers\yahoo.ts`
- Create: `C:\Project\market-compass-screener\src\providers\edinet.ts`
- Create: `C:\Project\market-compass-screener\src\providers\jquants.ts`
- Create: `C:\Project\market-compass-screener\src\providers\jpx.ts`
- Create: `C:\Project\market-compass-screener\src\collect.ts`
- Create: `C:\Project\market-compass-screener\tests\fixtures\yahoo-chart.json`
- Create: `C:\Project\market-compass-screener\tests\fixtures\yahoo-timeseries.json`
- Create: `C:\Project\market-compass-screener\tests\providers.test.ts`

**Interfaces:**
- Produces: `fetchYahooSecurity(symbol, fetchImpl): Promise<ProviderResult>`.
- Produces: `collectSecurity(symbol, dependencies): Promise<NormalizedSecurity>`.
- `ProviderResult` includes `status`, `observedAt`, `evidence`, `values`, `missingFields`, and `warnings`.

- [ ] **Step 1: Write fixture tests for Japanese symbol canonicalization and raw-unit preservation**

```ts
test("Yahoo maps 6857 to 6857.T and preserves period/evidence", async () => {
  const result = await fetchYahooSecurity("6857", fixtureFetch);
  assert.equal(result.security.symbol, "6857");
  assert.equal(result.security.financialPeriods.length, 3);
  assert.ok(result.security.financialPeriods.every((period) => period.endDate && period.currency === "JPY"));
  assert.ok(result.evidence.every((item) => item.url && item.observedAt));
});
```

Also test HTTP errors, aborts, partial JSON, null values, dividend aggregation by fiscal year, and a provider conflict.

- [ ] **Step 2: Run the provider tests and verify failure**

Run: `npm.cmd test -- tests/providers.test.ts`

Expected: FAIL because the providers do not exist.

- [ ] **Step 3: Implement Yahoo chart and fundamentals-timeseries adapters**

Use native `fetch` with `AbortSignal.timeout(7000)`, a stable user-agent, up to three retries only for 429/5xx, and a total request budget of 20 seconds per symbol. Request chart prices/dividends and these annual types when available: revenue, operating income, equity, assets, operating cash flow, total debt, diluted EPS, free cash flow, net income, capex, and cash dividends paid.

- [ ] **Step 4: Implement optional primary-source adapters**

`edinet.ts` reports `missing_configuration` unless `EDINET_API_KEY` is set. `jquants.ts` reports `missing_configuration` unless its configured credential set is complete. `jpx.ts` normalizes locally cached sector/listed-company data and reports its download date. None may substitute fabricated zeroes.

- [ ] **Step 5: Merge with explicit source priority and conflict markers**

Company IR/EDINET/J-Quants values outrank Yahoo values only when periods and units match. If two non-null values for the same metric/period differ by more than 1%, retain both evidence records and add `source_conflict`; do not silently overwrite.

- [ ] **Step 6: Run provider tests, a bounded live smoke test, and commit**

Run: `npm.cmd test -- tests/providers.test.ts && npm.cmd run smoke -- 6857`

Expected: fixture tests PASS; live smoke returns a price and either financial values or named missing fields without throwing.

```powershell
git add src/providers src/collect.ts tests package.json package-lock.json
git commit -m "feat: collect sourced Japanese market fundamentals"
```

### Task 4: Add persistence and service use cases

**Files:**
- Create: `C:\Project\market-compass-screener\supabase\migrations\20260813000000_market_compass_schema.sql`
- Create: `C:\Project\market-compass-screener\src\repository.ts`
- Create: `C:\Project\market-compass-screener\src\service.ts`
- Create: `C:\Project\market-compass-screener\tests\repository.test.ts`
- Create: `C:\Project\market-compass-screener\tests\service.test.ts`

**Interfaces:**
- Produces: `screenSymbols({ symbols, filters }, deps): Promise<ScreenResponse>`.
- Produces: `getSecurity(symbol, deps): Promise<SecurityResponse>`.
- Produces: `getMarket(symbols, deps): Promise<MarketResponse>` compatible with the current command-center candidate fields plus `providerMode` and `screenStatus`.
- Produces: `getSourceStatus(deps): Promise<SourceStatusResponse>`.
- Produces: `MarketCompassRepository.saveSnapshot`, `saveScreenRun`, and `latestSnapshot`.

- [ ] **Step 1: Write schema and repository contract tests**

Assert that the migration creates `market_compass.securities`, `financial_periods`, `price_snapshots`, `dividend_history`, `screen_runs`, `screen_results`, and `source_snapshots`; enables RLS for all seven; and creates unique/source-period indexes.

- [ ] **Step 2: Run repository tests and verify failure**

Run: `npm.cmd test -- tests/repository.test.ts tests/service.test.ts`

Expected: FAIL because the migration and service are absent.

- [ ] **Step 3: Implement optional-but-explicit persistence**

When both `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` exist, persist normalized records using the service role on the server. When either is missing, keep live computation working and return `persistence: "disabled"`; never expose the key.

- [ ] **Step 4: Implement bounded screening orchestration**

Accept 1-24 unique symbols matching `^\d{4}$` for financial screening. Limit concurrency to 4, return per-symbol failures as `insufficient_data`, and return `asOf`, `freshness`, `sourceIds`, `missingEvidence`, `dataCoverage`, and `disclaimer` at response and result level.

- [ ] **Step 5: Run service tests and commit**

Run: `npm.cmd test -- tests/repository.test.ts tests/service.test.ts && npm.cmd run typecheck`

Expected: PASS for live-persistence-disabled and mocked-persistence-enabled paths.

```powershell
git add supabase src/repository.ts src/service.ts tests
git commit -m "feat: persist and orchestrate screening runs"
```

### Task 5: Expose protected Vercel API endpoints

**Files:**
- Create: `C:\Project\market-compass-screener\api\v1\market.ts`
- Create: `C:\Project\market-compass-screener\api\v1\screens.ts`
- Create: `C:\Project\market-compass-screener\api\v1\securities\[symbol].ts`
- Create: `C:\Project\market-compass-screener\api\v1\sources\status.ts`
- Create: `C:\Project\market-compass-screener\api\cron\refresh.ts`
- Create: `C:\Project\market-compass-screener\tests\api.test.ts`
- Create: `C:\Project\market-compass-screener\.env.example`
- Create: `C:\Project\market-compass-screener\README.md`

**Interfaces:**
- `GET /api/v1/market?symbols=6857,7011`
- `POST /api/v1/screens` body `{ "symbols": ["6857"], "filters": { "overall": ["research_candidate", "watch"] } }`
- `GET /api/v1/securities/6857`
- `GET /api/v1/sources/status`
- `GET /api/cron/refresh` protected by Vercel's `Authorization: Bearer ${CRON_SECRET}` header.

- [ ] **Step 1: Write handler tests for methods, auth, validation, limits, and no-store headers**

Each private handler must return 405 for a wrong method, the auth status contract from Task 1, 400 for invalid symbols/body, 200 for valid mocked service output, and `Cache-Control: private, no-store, max-age=0`.

- [ ] **Step 2: Run API tests and verify failure**

Run: `npm.cmd test -- tests/api.test.ts`

Expected: FAIL because the API handlers are absent.

- [ ] **Step 3: Implement thin handlers using only Task 1 and Task 4 interfaces**

Handlers parse and validate requests, call one service function, and serialize errors. They do not contain screening formulas or provider-specific parsing.

- [ ] **Step 4: Document configuration, data limitations, and human verification links**

README lists Yahoo!ファイナンス、IR BANK、企業IR、EDINET, states that Yahoo access is unofficial/delayed, explains optional EDINET/J-Quants/Supabase settings, and states that output is primary screening rather than investment advice.

- [ ] **Step 5: Run the full service gate and commit**

Run: `npm.cmd test && npm.cmd run typecheck && npm.cmd run build`

Expected: all tests PASS and Vercel build succeeds.

```powershell
git add api tests .env.example README.md package.json vercel.json
git commit -m "feat: expose protected screening API"
```

### Task 6: Add the AIclimb BFF client and failure fallback

**Files:**
- Create: `api/_lib/market-compass-client.ts`
- Modify: `api/admin/command-center-market.ts`
- Create: `api/admin/command-center-screen.ts`
- Create: `api/admin/command-center-security.ts`
- Create: `api/admin/command-center-market-sources.ts`
- Modify: `tests/command-center-api-contract.test.mjs`
- Create: `tests/command-center-market-compass-client.test.mjs`

**Interfaces:**
- Produces: `callMarketCompass<T>(path: string, init?: RequestInit): Promise<T>`.
- The three new handlers remain wrapped in `withAdmin` and never return `MARKET_COMPASS_SERVICE_TOKEN`.
- Existing market handler returns new service data when connected and `buildCommandCenterMarket(symbols)` output plus `providerMode: "local_fallback"` on timeout, 401/403/503, or 5xx.

- [ ] **Step 1: Write static and executable contract tests**

```js
assert.match(client, /x-market-compass-service-token/);
assert.doesNotMatch(client, /console\.log\([^)]*TOKEN/);
for (const file of ["command-center-screen.ts", "command-center-security.ts", "command-center-market-sources.ts"]) {
  assert.match(await source(file), /withAdmin/);
  assert.match(await source(file), /private, no-store/);
}
```

Mock `global.fetch` to assert a 7.5-second abort signal, server-only header injection, service response pass-through, and local market fallback.

- [ ] **Step 2: Run tests and verify failure**

Run: `node --test tests/command-center-api-contract.test.mjs tests/command-center-market-compass-client.test.mjs`

Expected: FAIL because the client and handlers are absent.

- [ ] **Step 3: Implement the client with an allowlisted base URL**

Require `MARKET_COMPASS_SERVICE_URL` to be HTTPS in production, strip trailing slashes, accept only `/api/v1/` paths, inject the token header server-side, and map network errors to `MarketCompassUnavailableError` without including response bodies containing secrets.

- [ ] **Step 4: Implement handlers and current-market fallback**

Forward only validated symbol/filter fields. The screen/security/source handlers return 503 with `{ error: "market_compass_unavailable" }` when disconnected; only the existing market handler uses local price fallback so `/trade` remains useful.

- [ ] **Step 5: Run tests and commit**

Run: `node --test tests/command-center-api-contract.test.mjs tests/command-center-market-compass-client.test.mjs`

Expected: PASS.

```powershell
git add api tests
git commit -m "feat: connect command center to market screener"
```

### Task 7: Add independent protected routes and complete menus

**Files:**
- Modify: `api/admin/command-center-page.ts`
- Modify: `vercel.json`
- Modify: `site/static/admin/command-center.html`
- Modify: `site/static/admin/admin-menu.js`
- Modify: `tests/command-center-contract.test.mjs`
- Modify: `tests/command-center-rendered-html.test.mjs`

**Interfaces:**
- Adds views `market`, `screener`, `security`, `trade-plan`, `trade-plans`, `trades`, `market-sources`.
- Adds routes `/admin/command-center/<view>` and BFF rewrites `/api/admin/command-center/screen`, `/security`, `/market-sources`.

- [ ] **Step 1: Extend failing route/menu tests with all seven paths**

```js
const marketViews = ["market", "screener", "security", "trade-plan", "trade-plans", "trades", "market-sources"];
for (const view of marketViews) {
  assert.ok(sources.includes(`/admin/command-center/${view}`), view);
  assert.match(html, new RegExp(`/admin/command-center/${view}`), view);
}
```

Assert that the global mobile menu contains each label, the desktop global bar contains only the top-level 相場羅針盤 entry, and no secret name/value is rendered.

- [ ] **Step 2: Run route tests and verify failure**

Run: `node --test tests/command-center-contract.test.mjs tests/command-center-rendered-html.test.mjs`

Expected: FAIL on the new paths.

- [ ] **Step 3: Add exact rewrites and allowlisted views**

Add explicit page rewrites before the generic `:view` rewrite. Add exact BFF rewrites. Keep every page behind `command-center-page.ts` and `withAdmin`.

- [ ] **Step 4: Add a two-tier market menu**

Keep the first-tier command-center nav compact. Under every market-related view render a `.cc-market-nav` with labels: 相場羅針盤、市場候補、財務スクリーナー、銘柄詳細、取引プラン作成、登録プラン、取引記録、データ収集状況. On iPhone it remains horizontally scrollable with a visible current item.

- [ ] **Step 5: Run tests and commit**

Run: `node --test tests/command-center-contract.test.mjs tests/command-center-rendered-html.test.mjs`

Expected: PASS.

```powershell
git add api/admin/command-center-page.ts vercel.json site/static/admin tests
git commit -m "feat: expose market compass admin pages"
```

### Task 8: Split the current combined renderer and add the screener/detail UI

**Files:**
- Modify: `site/static/admin/command-center.js`
- Modify: `site/static/admin/command-center.css`
- Create: `tests/command-center-market-ui.test.mjs`
- Modify: `tests/command-center-rendered-html.test.mjs`

**Interfaces:**
- Produces shared render helpers `marketSection`, `tradePlanSection`, `tradePlansSection`, `tradesSection`, `screenResultCard`, and `sourceEvidenceList`.
- Produces view functions `renderMarket`, `renderScreener`, `renderSecurity`, `renderTradePlan`, `renderTradePlans`, `renderTrades`, `renderMarketSources`.
- `renderTrade` composes the first four existing sections and a link to the new financial screener.

- [ ] **Step 1: Write UI contract tests before changing the renderer**

Assert every view appears in the dispatcher, `/trade` still calls market and renders the plan/list/history section IDs, screener posts to `/api/admin/command-center/screen`, detail reads and validates a four-digit `symbol`, source view calls `/market-sources`, and all external evidence links include `target="_blank" rel="noreferrer"`.

- [ ] **Step 2: Run UI tests and verify failure**

Run: `node --test tests/command-center-market-ui.test.mjs tests/command-center-rendered-html.test.mjs`

Expected: FAIL because the new render functions are absent.

- [ ] **Step 3: Extract current sections without changing their behavior**

Keep current trade-plan payload field names (`market`, `symbol`, `tradeStyle`, `direction`, `thesis`) and existing `postData({ action: "create_trade_plan" })`. Render the same market table, saved plans, and trade records in `/trade` and their corresponding independent pages.

- [ ] **Step 4: Implement the screener form and results**

Accept comma/space/newline-separated four-digit Japanese symbols, normalize and deduplicate up to 24, show a clear validation error, submit JSON, and render summary counts plus one card per symbol. Each card shows overall Japanese label, data coverage, 12 rows with five statuses, periods, thresholds, explanation, missing evidence, and a detail link.

- [ ] **Step 5: Implement detail and source-status views**

Detail shows company, price/as-of, three-year table, dividends, 12 checks, source/freshness, Yahoo/IR BANK/company IR/EDINET verification links, and the warning “購入判断ではなく一次スクリーニングです”. Source status shows connected/delayed/missing/configuration-missing, last success, latency, and missing evidence without printing credentials.

- [ ] **Step 6: Add responsive and accessible styles**

Use existing color variables. Add distinct non-color text labels for all statuses, focus-visible styling, `aria-live` for screen progress, 44px mobile controls, responsive cards, and table wrappers that contain horizontal overflow. Do not add a second page-level hamburger.

- [ ] **Step 7: Run UI tests and commit**

Run: `node --test tests/command-center-market-ui.test.mjs tests/command-center-rendered-html.test.mjs`

Expected: PASS.

```powershell
git add site/static/admin tests
git commit -m "feat: render independent market compass screens"
```

### Task 9: Complete configuration, regression tests, and local browser QA

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `tests/command-center-contract.test.mjs`
- Modify: `tests/command-center-api-contract.test.mjs`
- Modify: `tests/command-center-market-ui.test.mjs`
- Create: `scripts/verify-market-compass.mjs`

**Interfaces:**
- Produces: `npm.cmd run verify:market-compass` in AI相談, covering API contracts and rendered routes without secrets.

- [ ] **Step 1: Add environment and operating documentation**

Document `MARKET_COMPASS_SERVICE_URL`, `MARKET_COMPASS_SERVICE_TOKEN`, new project health URL, source limitations, fallback behavior, exact page list, and rollback procedure (remove service env or revert the AI相談 integration commit; `/trade` local fallback remains).

- [ ] **Step 2: Add a full regression command**

The script runs TypeScript no-emit checking, all `command-center*.test.mjs`, existing bridge tests, and static secret scans for `MARKET_COMPASS_SERVICE_TOKEN=` and actual token-like strings.

- [ ] **Step 3: Run both repositories' complete local gates**

Run in the service: `npm.cmd ci && npm.cmd test && npm.cmd run typecheck && npm.cmd run build`.

Run in AI相談: `npm.cmd ci && npx.cmd tsc --noEmit && node --test tests/command-center*.test.mjs && npm.cmd run bridge:test`.

Expected: all commands exit 0.

- [ ] **Step 4: Start local previews and test authenticated flows**

Start both Vercel dev servers with hidden windows on different loopback ports. Verify health, missing/invalid/correct service token behavior, market, screen, security, sources, existing `/trade`, all seven new routes, form submission, and service-down fallback.

- [ ] **Step 5: Perform PC and iPhone browser QA**

At 1440px and 390px verify the shared fixed menu, shared hamburger, market subnav, current item, all cards/tables/forms, contrast, focus state, no page-level horizontal overflow, contained table overflow, and zero console errors. Save screenshots under an ignored verification directory.

- [ ] **Step 6: Commit verification support**

```powershell
git add .env.example README.md package.json scripts tests
git commit -m "test: verify market compass integration"
```

### Task 10: Create repositories, migrate schema, deploy, and verify production

**Files:**
- No source changes expected after all gates pass; deployment metadata remains ignored.

**Interfaces:**
- Produces GitHub repository `goodbouldering-collab/market-compass-screener`.
- Produces private service deployment in Vercel project `market-compass-screener`.
- Produces the unchanged AIclimb production domain with eight working market pages.

- [ ] **Step 1: Create and push the new GitHub repository**

Run from `C:\Project\market-compass-screener`:

```powershell
gh repo create goodbouldering-collab/market-compass-screener --private --source . --remote origin --push
```

Verify the remote is private and the pushed commit equals local HEAD.

- [ ] **Step 2: Apply the Supabase migration**

Use the configured shared Supabase project and apply only `20260813000000_market_compass_schema.sql`. Verify seven tables, expected indexes, and RLS enabled. Do not alter `ai_watch.*`.

- [ ] **Step 3: Deploy the new Vercel service and configure secrets**

Create/link Vercel project `market-compass-screener`, set a generated service token plus available Supabase/EDINET/J-Quants variables, and deploy production. Set the same token and service production URL only on the AI相談 Vercel project. Do not print secret values.

- [ ] **Step 4: Verify the service production contract**

Confirm health 200; market without token 401; market with wrong token 403; authorized market/screen/security/source status 200; responses contain no credentials; and one live Japanese symbol has price plus explicit values or named missing fields.

- [ ] **Step 5: Push the AI相談 branch and deploy preview**

Push the clean feature branch, deploy a Vercel preview, and verify authenticated `/trade` plus all seven new pages against the production service. Run PC/iPhone QA and console checks on preview.

- [ ] **Step 6: Merge/push to `main` and verify AIclimb production**

After all preview checks pass, update `main` with the reviewed commits, push, wait for Vercel READY, and verify these exact routes on `https://aiclimb.vercel.app`:

```text
/admin/command-center/trade
/admin/command-center/market
/admin/command-center/screener
/admin/command-center/security?symbol=6857
/admin/command-center/trade-plan
/admin/command-center/trade-plans
/admin/command-center/trades
/admin/command-center/market-sources
```

- [ ] **Step 7: Record final evidence**

Record both Vercel production URLs, deployed commit SHAs, API status matrix, authenticated page list, PC/iPhone viewport results, console status, fallback test, data-source gaps, and rollback command. If any route, auth flow, or service contract fails, do not call the work complete.

---

## Self-Review Record

- Spec coverage: the unchanged aggregate page, seven independent pages, all 12 rules, sector exceptions, evidence/freshness, private service auth, Supabase schema, fallback, tests, deployment, and production QA each map to a task above.
- Placeholder scan: no deferred implementation markers are used; optional providers have explicit `missing_configuration` behavior.
- Type consistency: `NormalizedSecurity` flows from providers to `evaluateRules`, then `ScreenResult`; API handlers call `service.ts`; AIclimb BFF consumes only versioned JSON and keeps the token server-side.
- Scope control: orders, brokerage integration, automated trading, and investment recommendations remain excluded.
