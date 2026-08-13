type MarketCompassEnvironment = Record<string, string | undefined>;

export type MarketCompassClientDependencies = {
  env?: MarketCompassEnvironment;
  fetchImpl?: typeof fetch;
};

export class MarketCompassUnavailableError extends Error {
  readonly status: number;

  constructor(message = "Market Compass service is unavailable", status = 503) {
    super(message);
    this.name = "MarketCompassUnavailableError";
    this.status = status;
  }
}

function configuredBaseUrl(env: MarketCompassEnvironment): URL {
  const raw = env.MARKET_COMPASS_SERVICE_URL?.trim();
  if (!raw) throw new MarketCompassUnavailableError("Market Compass service is not configured", 503);

  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    throw new MarketCompassUnavailableError("Market Compass service URL is invalid", 503);
  }

  const isLoopback = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
  if (env.NODE_ENV === "production" && url.protocol !== "https:") {
    throw new MarketCompassUnavailableError("Market Compass service requires HTTPS in production", 503);
  }
  if (url.protocol !== "https:" && !(url.protocol === "http:" && isLoopback)) {
    throw new MarketCompassUnavailableError("Market Compass service URL must use HTTPS or a local HTTP address", 503);
  }
  return url;
}

function safeServicePath(path: string): string {
  if (!/^\/api\/v1\/[A-Za-z0-9][A-Za-z0-9/?=&._%-]*$/.test(path)) {
    throw new MarketCompassUnavailableError("Market Compass service path is not allowed", 503);
  }
  return path;
}

export async function callMarketCompass<T = unknown>(
  path: string,
  init: RequestInit = {},
  dependencies: MarketCompassClientDependencies = {},
): Promise<T> {
  const env = dependencies.env ?? process.env;
  const token = env.MARKET_COMPASS_SERVICE_TOKEN?.trim();
  if (!token) throw new MarketCompassUnavailableError("Market Compass service is not configured", 503);

  const baseUrl = configuredBaseUrl(env);
  const requestUrl = new URL(safeServicePath(path), `${baseUrl.origin}/`);
  const headers = new Headers(init.headers);
  headers.set("accept", "application/json");
  headers.set("x-market-compass-service-token", token);
  if (init.body && !headers.has("content-type")) headers.set("content-type", "application/json");

  let response: Response;
  try {
    response = await (dependencies.fetchImpl ?? fetch)(requestUrl, {
      ...init,
      headers,
      signal: init.signal ?? AbortSignal.timeout(7_500),
    });
  } catch {
    throw new MarketCompassUnavailableError("Market Compass service request failed", 503);
  }

  if (!response.ok) {
    const status = response.status >= 400 && response.status <= 599 ? response.status : 503;
    throw new MarketCompassUnavailableError("Market Compass service returned an error", status);
  }

  try {
    return await response.json() as T;
  } catch {
    throw new MarketCompassUnavailableError("Market Compass service returned invalid JSON", 502);
  }
}
