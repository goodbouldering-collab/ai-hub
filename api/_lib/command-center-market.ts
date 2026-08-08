export type CommandCenterCandidate = {
  symbol: string;
  name: string;
  market: "JP" | "US";
  exchange: string;
  currency: "JPY" | "USD";
  price: number;
  changePercent: number;
  score: number;
  confidence: number;
  decision: "buy_candidate" | "watch" | "avoid";
  whyNow: string;
  firstRisk: string;
  investableWhen: string;
  killCondition: string;
  history: number[];
  updatedAt: string;
  sourceIds: string[];
  margin: { status: "unknown"; buyable: false; sellable: null; kind: string; sourceId: string; checkedAt: string; note: string };
};

export type CommandCenterMarketPayload = {
  mode: "live" | "partial" | "unavailable";
  asOf: string;
  freshnessLabel: string;
  sourcePosture: string;
  marketStance: string;
  candidates: CommandCenterCandidate[];
  marketPulse: Array<{ label: string; value: string; change: number; direction: "up" | "down" | "flat"; sourceId: string }>;
  sources: Array<{ id: string; name: string; status: "connected" | "delayed" | "missing" | "available"; note: string; url: string }>;
  missingEvidence: string[];
};

const DEFAULT_SYMBOLS = ["6857", "7011", "8035", "5803", "9984", "7203", "NVDA", "AVGO", "MSFT", "META", "AMZN", "PLTR", "TSM", "AAPL"];
const META: Record<string, { name: string; market: "JP" | "US"; exchange: string; currency: "JPY" | "USD" }> = {
  "6857": { name: "アドバンテスト", market: "JP", exchange: "東証", currency: "JPY" },
  "7011": { name: "三菱重工業", market: "JP", exchange: "東証", currency: "JPY" },
  "8035": { name: "東京エレクトロン", market: "JP", exchange: "東証", currency: "JPY" },
  "5803": { name: "フジクラ", market: "JP", exchange: "東証", currency: "JPY" },
  "9984": { name: "ソフトバンクグループ", market: "JP", exchange: "東証", currency: "JPY" },
  "7203": { name: "トヨタ自動車", market: "JP", exchange: "東証", currency: "JPY" },
  NVDA: { name: "NVIDIA", market: "US", exchange: "NASDAQ", currency: "USD" },
  AVGO: { name: "Broadcom", market: "US", exchange: "NASDAQ", currency: "USD" },
  MSFT: { name: "Microsoft", market: "US", exchange: "NASDAQ", currency: "USD" },
  META: { name: "Meta Platforms", market: "US", exchange: "NASDAQ", currency: "USD" },
  AMZN: { name: "Amazon", market: "US", exchange: "NASDAQ", currency: "USD" },
  PLTR: { name: "Palantir", market: "US", exchange: "NASDAQ", currency: "USD" },
  TSM: { name: "TSMC ADR", market: "US", exchange: "NYSE", currency: "USD" },
  AAPL: { name: "Apple", market: "US", exchange: "NASDAQ", currency: "USD" },
};

type YahooPayload = { chart?: { result?: Array<{ meta?: Record<string, unknown>; timestamp?: number[]; indicators?: { quote?: Array<{ close?: Array<number | null>; volume?: Array<number | null> }> } }> } };

function canonical(symbol: string): string { return symbol.toUpperCase().replace(/\.T$/, ""); }
function providerSymbol(symbol: string): string { return /^\d{4}$/.test(symbol) ? `${symbol}.T` : symbol; }
function meta(symbol: string) {
  return META[symbol] ?? META[canonical(symbol)] ?? { name: canonical(symbol), market: /^\d{4}/.test(symbol) ? "JP" as const : "US" as const, exchange: /^\d{4}/.test(symbol) ? "東証" : "海外", currency: /^\d{4}/.test(symbol) ? "JPY" as const : "USD" as const };
}
function signal(prices: number[], volumes: number[]) {
  const current = prices.at(-1) ?? 0;
  const previous = prices.at(-2) ?? current;
  const fiveAgo = prices.at(-6) ?? previous;
  const change = previous > 0 ? ((current - previous) / previous) * 100 : 0;
  const momentum = fiveAgo > 0 ? ((current - fiveAgo) / fiveAgo) * 100 : 0;
  const recentVolume = volumes.slice(-5).reduce((sum, value) => sum + value, 0) / Math.max(1, volumes.slice(-5).length);
  const baseVolume = volumes.slice(-20).reduce((sum, value) => sum + value, 0) / Math.max(1, volumes.slice(-20).length);
  const volumeBoost = baseVolume > 0 && recentVolume > baseVolume * 1.2 ? 8 : 0;
  const score = Math.max(0, Math.min(100, Math.round(52 + momentum * 4 + change * 2 + volumeBoost)));
  return { score, confidence: Math.max(20, Math.min(95, Math.round(48 + Math.abs(momentum) * 3))), decision: score >= 74 ? "buy_candidate" as const : score >= 58 ? "watch" as const : "avoid" as const };
}

async function fetchSeries(symbol: string): Promise<CommandCenterCandidate | null> {
  const timer = AbortSignal.timeout(7_500);
  const response = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(providerSymbol(symbol))}?range=6mo&interval=1d&events=div%2Csplits`, { headers: { accept: "application/json", "user-agent": "AIHubCommandCenter/1.0" }, signal: timer });
  if (!response.ok) return null;
  const payload = await response.json() as YahooPayload;
  const result = payload.chart?.result?.[0];
  const closes = result?.indicators?.quote?.[0]?.close ?? [];
  const volumes = result?.indicators?.quote?.[0]?.volume ?? [];
  const timestamps = result?.timestamp ?? [];
  const prices = closes.flatMap((value) => Number.isFinite(Number(value)) && Number(value) > 0 ? [Number(value)] : []);
  if (prices.length < 10) return null;
  const latestPrice = Number(result?.meta?.regularMarketPrice ?? prices.at(-1));
  if (!Number.isFinite(latestPrice) || latestPrice <= 0) return null;
  prices[prices.length - 1] = latestPrice;
  const previous = Number(prices.at(-2) ?? result?.meta?.previousClose ?? 0);
  const updatedAt = Number(result?.meta?.regularMarketTime) ? new Date(Number(result?.meta?.regularMarketTime) * 1_000).toISOString() : new Date(Number(timestamps.at(-1)) * 1_000).toISOString();
  const evaluated = signal(prices, volumes.map((value) => Number(value) || 0));
  const details = meta(symbol);
  return {
    symbol: canonical(symbol), ...details, price: latestPrice,
    changePercent: previous > 0 ? Number((((latestPrice - previous) / previous) * 100).toFixed(2)) : 0,
    ...evaluated,
    whyNow: evaluated.score >= 74 ? "直近の価格推移と出来高が上向きです。" : "条件が揃うまで値動きを確認します。",
    firstRisk: "公開市場データは遅延や欠損の可能性があります。",
    investableWhen: "一次情報と現在値を再確認できたとき。",
    killCondition: "20日トレンドが崩れ、前提が変わったとき。",
    history: prices.slice(-60), updatedAt, sourceIds: ["WEB"],
    margin: { status: "unknown", buyable: false, sellable: null, kind: "現物確認のみ", sourceId: "CASH-ONLY", checkedAt: new Date().toISOString(), note: "信用取引の可否は表示しません。" },
  };
}

function demoCandidate(symbol: string): CommandCenterCandidate {
  const details = meta(symbol);
  return { symbol: canonical(symbol), ...details, price: 0, changePercent: 0, score: 0, confidence: 20, decision: "avoid", whyNow: "市場データを取得できませんでした。", firstRisk: "データ未取得のため判断できません。", investableWhen: "データ取得後に再評価します。", killCondition: "データが欠けた状態では判断しません。", history: [], updatedAt: new Date().toISOString(), sourceIds: [], margin: { status: "unknown", buyable: false, sellable: null, kind: "現物確認のみ", sourceId: "CASH-ONLY", checkedAt: new Date().toISOString(), note: "信用取引の可否は表示しません。" } };
}

export async function buildCommandCenterMarket(requestedSymbols: string[]): Promise<CommandCenterMarketPayload> {
  const configured = `${process.env.MARKET_SCAN_SYMBOLS_JP ?? ""},${process.env.MARKET_SCAN_SYMBOLS_US ?? ""}`.split(/[\s,]+/).map((value) => value.trim().toUpperCase()).filter((value) => /^[A-Z0-9.\-]{1,12}$/.test(value));
  const symbols = [...new Set([...requestedSymbols, ...configured, ...DEFAULT_SYMBOLS])].slice(0, 24);
  const settled = await Promise.allSettled(symbols.map((symbol) => fetchSeries(symbol)));
  const candidates = settled.map((item, index) => item.status === "fulfilled" && item.value ? item.value : demoCandidate(symbols[index])).sort((left, right) => right.score - left.score);
  const liveCount = candidates.filter((candidate) => candidate.sourceIds.length > 0).length;
  return {
    mode: liveCount === candidates.length ? "live" : liveCount ? "partial" : "unavailable",
    asOf: new Date().toISOString(), freshnessLabel: liveCount ? "公開市場データ（遅延の可能性あり）" : "データ未取得",
    sourcePosture: "外部APIの鍵はサーバー側だけで使用し、レスポンスには含めません。",
    marketStance: candidates.filter((candidate) => candidate.score >= 74).length >= 2 ? "上向き候補あり" : "様子見",
    candidates,
    marketPulse: [{ label: "候補数", value: String(candidates.filter((candidate) => candidate.score >= 74).length), change: 0, direction: "flat", sourceId: liveCount ? "WEB" : "NONE" }],
    sources: [{ id: "WEB", name: "公開市場データ", status: liveCount ? "delayed" : "missing", note: liveCount ? "Yahoo Financeの公開チャートを参照" : "取得できませんでした", url: "https://finance.yahoo.com/" }, { id: "PRIMARY", name: "一次情報確認", status: "available", note: "売買判断前に一次情報を再確認", url: "https://www.sec.gov/edgar/search/" }],
    missingEvidence: ["公開データはリアルタイム保証ではありません。", "売買判断・注文執行は行いません。"],
  };
}
