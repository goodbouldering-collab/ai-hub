import type { VercelReq } from "./auth.js";

export const AI_SALON_ITEM_NAME =
  process.env.SQUARE_AI_SALON_ITEM_NAME || "AIオンラインサロン";

export function publicOrigin(req: VercelReq): string {
  const configured =
    process.env.AIHUB_SITE_URL ||
    process.env.AIWATCH_SITE_URL ||
    process.env.PUBLIC_SITE_URL;
  if (configured) return new URL(configured).origin;

  const forwardedProto = firstHeader(req.headers["x-forwarded-proto"]);
  const forwardedHost = firstHeader(req.headers["x-forwarded-host"]);
  const host = forwardedHost || firstHeader(req.headers.host);
  if (!host) return "https://ai-hub-jp.vercel.app";
  const protocol = forwardedProto || (host.includes("localhost") ? "http" : "https");
  return `${protocol}://${host}`;
}

export function salonPriceYen(): number {
  const raw = requiredSquareEnv("SQUARE_AI_SALON_PRICE_YEN");
  const amount = Number(raw);
  if (!Number.isSafeInteger(amount) || amount <= 0) {
    throw configError("SQUARE_AI_SALON_PRICE_YEN must be a positive integer.");
  }
  return amount;
}

export function salonPlanVariationId(): string {
  return requiredSquareEnv("SQUARE_AI_SALON_PLAN_VARIATION_ID");
}

export function salonOpenChatUrl(): string {
  const raw = requiredSquareEnv("AI_SALON_OPENCHAT_URL");
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    throw configError("AI_SALON_OPENCHAT_URL must be a valid URL.");
  }
  if (
    url.protocol !== "https:" ||
    !["line.me", "lin.ee"].includes(url.hostname.toLowerCase())
  ) {
    throw configError("AI_SALON_OPENCHAT_URL must be an HTTPS LINE URL.");
  }
  return url.toString();
}

export async function squareJson<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const accessToken = requiredSquareEnv("SQUARE_ACCESS_TOKEN");
  const version = process.env.SQUARE_VERSION || "2026-05-20";
  const environment = (process.env.SQUARE_ENVIRONMENT || "production").toLowerCase();
  const base =
    environment === "sandbox"
      ? "https://connect.squareupsandbox.com"
      : "https://connect.squareup.com";

  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Square-Version": version,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });

  const text = await response.text();
  let body: any = {};
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = { raw: text };
    }
  }
  if (!response.ok) {
    const message =
      body?.errors?.[0]?.detail ||
      body?.errors?.[0]?.code ||
      `Square API error (${response.status})`;
    throw Object.assign(new Error(message), {
      status: response.status >= 500 ? 502 : response.status,
      publicMessage: "Squareの決済処理を開始できませんでした。",
    });
  }
  return body as T;
}

export function requiredSquareEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) throw configError(`${name} is not configured.`);
  return value;
}

function configError(message: string): Error {
  return Object.assign(new Error(message), {
    status: 503,
    publicMessage: "Square決済の設定が完了していません。",
  });
}

function firstHeader(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] || "" : value || "";
}
