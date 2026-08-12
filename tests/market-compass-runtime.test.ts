import assert from "node:assert/strict";
import type { IncomingMessage } from "node:http";
import { Readable } from "node:stream";
import test from "node:test";

import { createAdminSessionCookie } from "../api/_lib/auth.js";
import { callMarketCompass, MarketCompassUnavailableError } from "../api/_lib/market-compass-client.js";
import { createCommandCenterMarketHandler } from "../api/admin/command-center-market.js";
import { createCommandCenterMarketSourcesHandler } from "../api/admin/command-center-market-sources.js";
import { createCommandCenterScreenHandler } from "../api/admin/command-center-screen.js";
import { createCommandCenterSecurityHandler } from "../api/admin/command-center-security.js";

class FakeResponse {
  statusCode = 0;
  headers = new Map<string, string>();
  payload: unknown;
  setHeader(name: string, value: string | number | readonly string[]) { this.headers.set(name.toLowerCase(), String(value)); return this; }
  status(code: number) { this.statusCode = code; return this; }
  json(body: unknown) { this.payload = body; return this; }
  send(body: unknown) { this.payload = body; return this; }
  end(body?: unknown) { this.payload = body; return this; }
}

function adminRequest(method: string, url: string, body?: unknown): IncomingMessage & { body?: unknown; query?: Record<string, string | string[]> } {
  process.env.ADMIN_PASS = "admin-pass-for-test";
  process.env.ADMIN_SESSION_SECRET = "admin-session-secret-for-test";
  const cookie = createAdminSessionCookie().split(";")[0];
  const request = Readable.from([]) as IncomingMessage & { body?: unknown; query?: Record<string, string | string[]> };
  request.method = method;
  request.url = url;
  request.body = body;
  request.headers = { cookie, accept: "application/json" };
  return request;
}

const localPayload = {
  mode: "live",
  asOf: "2026-08-13T00:00:00.000Z",
  freshnessLabel: "公開市場データ",
  sourcePosture: "公開値",
  marketStance: "様子見",
  candidates: [
    { symbol: "6857", name: "旧日本株", market: "JP", exchange: "東証", currency: "JPY", price: 100, changePercent: 1, score: 80, confidence: 80, decision: "buy_candidate", whyNow: "価格", firstRisk: "遅延", investableWhen: "確認後", killCondition: "前提崩れ", history: [99, 100], updatedAt: "2026-08-13T00:00:00.000Z", sourceIds: ["WEB"], margin: { status: "unknown", buyable: false, sellable: null, kind: "現物", sourceId: "CASH", checkedAt: "2026-08-13T00:00:00.000Z", note: "" } },
    { symbol: "NVDA", name: "NVIDIA", market: "US", exchange: "NASDAQ", currency: "USD", price: 200, changePercent: 2, score: 75, confidence: 70, decision: "buy_candidate", whyNow: "価格", firstRisk: "遅延", investableWhen: "確認後", killCondition: "前提崩れ", history: [198, 200], updatedAt: "2026-08-13T00:00:00.000Z", sourceIds: ["WEB"], margin: { status: "unknown", buyable: false, sellable: null, kind: "現物", sourceId: "CASH", checkedAt: "2026-08-13T00:00:00.000Z", note: "" } }
  ],
  marketPulse: [],
  sources: [],
  missingEvidence: []
};

const servicePayload = {
  mode: "live",
  providerMode: "market_compass_service",
  asOf: "2026-08-13T01:00:00.000Z",
  freshnessLabel: "公開市場・財務データ",
  sourcePosture: "出典明示",
  marketStance: "一次調査候補あり",
  candidates: [{ ...localPayload.candidates[0], name: "アドバンテスト", decision: "research_candidate", dataCoverage: 83, missingEvidence: ["company_forecast"] }],
  marketPulse: [],
  sources: [{ id: "YAHOO", name: "Yahoo", status: "available", note: "遅延あり", url: "https://finance.yahoo.co.jp/" }],
  missingEvidence: ["company_forecast"],
  disclaimer: "一次スクリーニング"
};

test("market compass client enforces HTTPS/path/token and injects the token server-side", async () => {
  let captured: { url: string; init: RequestInit } | undefined;
  const result = await callMarketCompass<{ ok: boolean }>("/api/v1/market?symbols=6857", {}, {
    env: { NODE_ENV: "production", MARKET_COMPASS_SERVICE_URL: "https://screen.example.com", MARKET_COMPASS_SERVICE_TOKEN: "service-secret" },
    fetchImpl: async (url, init) => {
      captured = { url: String(url), init: init ?? {} };
      return Response.json({ ok: true });
    }
  });
  assert.deepEqual(result, { ok: true });
  assert.equal(captured?.url, "https://screen.example.com/api/v1/market?symbols=6857");
  const headers = new Headers(captured?.init.headers);
  assert.equal(headers.get("x-market-compass-service-token"), "service-secret");
  assert.ok(captured?.init.signal instanceof AbortSignal);
  assert.doesNotMatch(JSON.stringify(result), /service-secret/);

  await assert.rejects(() => callMarketCompass("/api/v1/market", {}, { env: {} }), /not configured/);
  await assert.rejects(() => callMarketCompass("/api/private/other", {}, { env: { MARKET_COMPASS_SERVICE_URL: "https://screen.example.com", MARKET_COMPASS_SERVICE_TOKEN: "x" } }), /path/);
  await assert.rejects(() => callMarketCompass("/api/v1/market", {}, { env: { NODE_ENV: "production", MARKET_COMPASS_SERVICE_URL: "http://screen.example.com", MARKET_COMPASS_SERVICE_TOKEN: "x" } }), /HTTPS/);
});

test("market compass client maps upstream failures without reflecting response bodies", async () => {
  const promise = callMarketCompass("/api/v1/market", {}, {
    env: { MARKET_COMPASS_SERVICE_URL: "https://screen.example.com", MARKET_COMPASS_SERVICE_TOKEN: "service-secret" },
    fetchImpl: async () => new Response("service-secret upstream detail", { status: 503 })
  });
  await assert.rejects(promise, (error: unknown) => {
    assert.ok(error instanceof MarketCompassUnavailableError);
    assert.equal(error.status, 503);
    assert.doesNotMatch(error.message, /service-secret|upstream detail/);
    return true;
  });
});

test("market handler replaces local Japanese data, preserves US data, and removes buy wording", async () => {
  const handler = createCommandCenterMarketHandler({
    callService: async () => servicePayload,
    buildLocal: async () => localPayload
  });
  const response = new FakeResponse();
  await handler(adminRequest("GET", "/api/admin/command-center/market"), response as never);
  assert.equal(response.statusCode, 200);
  const payload = response.payload as typeof servicePayload & { candidates: Array<{ symbol: string; decision: string }>; providerMode: string };
  assert.equal(payload.providerMode, "market_compass_service");
  assert.deepEqual(payload.candidates.map((item) => item.symbol), ["6857", "NVDA"]);
  assert.equal(payload.candidates[0].decision, "research_candidate");
  assert.equal(payload.candidates[1].decision, "research_candidate");
  assert.doesNotMatch(JSON.stringify(payload), /buy_candidate|sell_candidate|買い推奨|売り推奨/);
  assert.equal(response.headers.get("cache-control"), "private, no-store, max-age=0");
});

test("market handler falls back to sanitized local data when the service is unavailable", async () => {
  const handler = createCommandCenterMarketHandler({
    callService: async () => { throw new MarketCompassUnavailableError("unavailable", 503); },
    buildLocal: async () => localPayload
  });
  const response = new FakeResponse();
  await handler(adminRequest("GET", "/api/admin/command-center/market"), response as never);
  const payload = response.payload as { providerMode: string; candidates: Array<{ decision: string }>; missingEvidence: string[] };
  assert.equal(response.statusCode, 200);
  assert.equal(payload.providerMode, "local_fallback");
  assert.deepEqual(payload.candidates.map((item) => item.decision), ["research_candidate", "research_candidate"]);
  assert.ok(payload.missingEvidence.includes("財務スクリーナーへ接続できないため価格データへフォールバックしました。"));
});

test("screen, security, and source BFFs validate inputs and stay admin-gated", async () => {
  const calls: Array<{ path: string; init?: RequestInit }> = [];
  const callService = async (path: string, init?: RequestInit) => { calls.push({ path, init }); return { ok: true }; };
  const screen = createCommandCenterScreenHandler({ callService });
  const security = createCommandCenterSecurityHandler({ callService });
  const sources = createCommandCenterMarketSourcesHandler({ callService });

  const screenResponse = new FakeResponse();
  await screen(adminRequest("POST", "/api/admin/command-center/screen", { symbols: ["6857"] }), screenResponse as never);
  assert.equal(screenResponse.statusCode, 200);
  assert.equal(calls[0].path, "/api/v1/screens");
  assert.equal(JSON.parse(String(calls[0].init?.body)).symbols[0], "6857");

  const invalidScreen = new FakeResponse();
  await screen(adminRequest("POST", "/api/admin/command-center/screen", { symbols: ["NVDA"] }), invalidScreen as never);
  assert.equal(invalidScreen.statusCode, 400);

  const securityResponse = new FakeResponse();
  await security(adminRequest("GET", "/api/admin/command-center/security?symbol=6857"), securityResponse as never);
  assert.equal(calls[1].path, "/api/v1/securities/6857");

  const sourceResponse = new FakeResponse();
  await sources(adminRequest("GET", "/api/admin/command-center/market-sources"), sourceResponse as never);
  assert.equal(calls[2].path, "/api/v1/sources/status");

  const unauthenticated = new FakeResponse();
  const request = Readable.from([]) as IncomingMessage;
  request.method = "GET";
  request.url = "/api/admin/command-center/market-sources";
  request.headers = { accept: "application/json" };
  await sources(request as never, unauthenticated as never);
  assert.equal(unauthenticated.statusCode, 401);
});
