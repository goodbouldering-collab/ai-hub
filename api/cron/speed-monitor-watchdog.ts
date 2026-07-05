import type { VercelReq, VercelRes } from "../_lib/auth.js";

type SpeedRow = {
  timestamp_utc?: string;
  local_time?: string;
  download_mbps?: number | null;
  upload_mbps?: number | null;
  latency_ms?: number | null;
  status?: string;
};

type SpeedPayload = {
  generated_at_utc?: string;
  summary?: {
    total?: number;
    latest?: SpeedRow | null;
    latest_with_metrics?: SpeedRow | null;
  };
  rows?: SpeedRow[];
};

const DEFAULT_MAX_AGE_MINUTES = 220;
const DEFAULT_DATA_PATH = "/data/speed-monitor.json";

function headerText(value: string | string[] | undefined): string {
  if (Array.isArray(value)) return value[0] || "";
  return value || "";
}

function isAuthorized(req: VercelReq): boolean {
  const userAgent = headerText(req.headers["user-agent"]);
  const authorization = headerText(req.headers.authorization);
  const cronSecret = process.env.CRON_SECRET;

  if (cronSecret && authorization === `Bearer ${cronSecret}`) {
    return true;
  }

  // This endpoint is read-only. Allow Vercel's cron user agent so the watchdog
  // still works on projects where CRON_SECRET has not been configured yet.
  return userAgent.includes("vercel-cron/1.0");
}

function buildDefaultDataUrl(req: VercelReq): string {
  const proto = headerText(req.headers["x-forwarded-proto"]) || "https";
  const host = headerText(req.headers["x-forwarded-host"]) || headerText(req.headers.host);
  if (host) return `${proto}://${host}${DEFAULT_DATA_PATH}`;
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}${DEFAULT_DATA_PATH}`;
  return `https://ai-hub-jp.vercel.app${DEFAULT_DATA_PATH}`;
}

function latestRow(payload: SpeedPayload): SpeedRow | null {
  if (payload.summary?.latest_with_metrics) return payload.summary.latest_with_metrics;
  if (payload.summary?.latest) return payload.summary.latest;
  const rows = payload.rows || [];
  for (let i = rows.length - 1; i >= 0; i -= 1) {
    const row = rows[i];
    if (row.download_mbps != null || row.upload_mbps != null || row.latency_ms != null) {
      return row;
    }
  }
  return rows[rows.length - 1] || null;
}

function parseTimestamp(row: SpeedRow | null): number {
  if (!row) return Number.NaN;
  const raw = row.timestamp_utc || row.local_time || "";
  return Date.parse(raw);
}

function maxAgeMinutes(): number {
  const raw = Number(process.env.SPEED_MONITOR_STALE_MINUTES || DEFAULT_MAX_AGE_MINUTES);
  return Number.isFinite(raw) && raw > 0 ? raw : DEFAULT_MAX_AGE_MINUTES;
}

export default async function handler(req: VercelReq, res: VercelRes) {
  res.setHeader("Cache-Control", "no-store");

  if ((req.method || "GET").toUpperCase() !== "GET") {
    return res.status(405).json({ ok: false, error: "method not allowed" });
  }
  if (!isAuthorized(req)) {
    return res.status(401).json({ ok: false, error: "unauthorized cron request" });
  }

  const dataUrl = process.env.SPEED_MONITOR_DATA_URL || buildDefaultDataUrl(req);
  const limitMinutes = maxAgeMinutes();

  try {
    const response = await fetch(`${dataUrl}${dataUrl.includes("?") ? "&" : "?"}t=${Date.now()}`, {
      headers: { accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) {
      return res.status(502).json({
        ok: false,
        error: "speed monitor data fetch failed",
        data_url: dataUrl,
        upstream_status: response.status,
      });
    }

    const payload = (await response.json()) as SpeedPayload;
    const latest = latestRow(payload);
    const latestMs = parseTimestamp(latest);
    if (!Number.isFinite(latestMs)) {
      return res.status(502).json({
        ok: false,
        error: "speed monitor latest timestamp is missing or invalid",
        data_url: dataUrl,
        total: payload.summary?.total ?? payload.rows?.length ?? 0,
      });
    }

    const ageMinutes = Math.round(((Date.now() - latestMs) / 60000) * 10) / 10;
    const stale = ageMinutes > limitMinutes;
    return res.status(stale ? 503 : 200).json({
      ok: !stale,
      stale,
      checked_at: new Date().toISOString(),
      max_age_minutes: limitMinutes,
      age_minutes: ageMinutes,
      latest,
      total: payload.summary?.total ?? payload.rows?.length ?? 0,
      data_url: dataUrl,
    });
  } catch (error: any) {
    return res.status(500).json({
      ok: false,
      error: "speed monitor watchdog failed",
      detail: error?.message || String(error),
      data_url: dataUrl,
    });
  }
}
