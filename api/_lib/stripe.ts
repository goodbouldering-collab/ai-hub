import { createHmac, timingSafeEqual } from "node:crypto";
import type { IncomingMessage } from "node:http";
import type { VercelReq } from "./auth.js";

export const STRIPE_API_VERSION =
  process.env.STRIPE_API_VERSION || "2026-05-27.dahlia";
export const MONTHLY_SUPPORT_PLAN = "monthly-support";
export const STRIPE_API_BASE = "https://api.stripe.com/v1";

export function requiredStripeEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw Object.assign(new Error(`${name} is not set`), {
      status: 500,
      publicMessage: "Stripe checkout is not configured yet.",
    });
  }
  return value;
}

export function supportTermMonths(): number {
  const raw = Number(process.env.STRIPE_SUPPORT_TERM_MONTHS || "6");
  if (!Number.isFinite(raw) || raw < 1) return 6;
  return Math.min(Math.floor(raw), 36);
}

export function publicOrigin(req: VercelReq): string {
  const configured = process.env.AIHUB_SITE_URL || process.env.AIWATCH_SITE_URL;
  if (configured) return configured.replace(/\/+$/, "");

  const host =
    firstHeader(req.headers["x-forwarded-host"]) ||
    firstHeader(req.headers.host) ||
    "ai-hub-jp.vercel.app";
  const proto = firstHeader(req.headers["x-forwarded-proto"]) || "https";
  return `${proto}://${host}`.replace(/\/+$/, "");
}

export async function stripePost(
  path: string,
  params: URLSearchParams,
): Promise<any> {
  const secret = requiredStripeEnv("STRIPE_SECRET_KEY");
  const response = await fetch(`${STRIPE_API_BASE}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${secret}`,
      "Content-Type": "application/x-www-form-urlencoded",
      "Stripe-Version": STRIPE_API_VERSION,
    },
    body: params.toString(),
  });

  const text = await response.text();
  const body = parseJson(text);
  if (!response.ok) {
    const message =
      body?.error?.message || `Stripe API request failed (${response.status})`;
    throw Object.assign(new Error(message), {
      status: response.status,
      detail: body,
      publicMessage: "Stripe checkout could not be started.",
    });
  }
  return body;
}

export async function readRawBody(req: IncomingMessage & { body?: any }): Promise<string> {
  if (typeof req.body === "string") return req.body;
  if (Buffer.isBuffer(req.body)) return req.body.toString("utf8");

  const chunks: Buffer[] = [];
  for await (const chunk of req as any) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString("utf8");
}

export function verifyStripeSignature(
  rawBody: string,
  signatureHeader: string | undefined,
  secret: string,
): boolean {
  if (!signatureHeader) return false;

  const parts = signatureHeader.split(",").map((part) => part.split("="));
  const timestamp = parts.find(([key]) => key === "t")?.[1];
  const signatures = parts
    .filter(([key]) => key === "v1")
    .map(([, value]) => value)
    .filter(Boolean);
  if (!timestamp || signatures.length === 0) return false;

  const ageSeconds = Math.abs(Date.now() / 1000 - Number(timestamp));
  if (!Number.isFinite(ageSeconds) || ageSeconds > 300) return false;

  const expected = createHmac("sha256", secret)
    .update(`${timestamp}.${rawBody}`, "utf8")
    .digest("hex");
  const expectedBuffer = Buffer.from(expected);
  return signatures.some((signature) => {
    const actualBuffer = Buffer.from(signature);
    return (
      actualBuffer.length === expectedBuffer.length &&
      timingSafeEqual(actualBuffer, expectedBuffer)
    );
  });
}

export function addMonthsUnix(epochSeconds: number, months: number): number {
  const date = new Date(epochSeconds * 1000);
  const day = date.getUTCDate();
  date.setUTCMonth(date.getUTCMonth() + months);
  if (date.getUTCDate() !== day) date.setUTCDate(0);
  return Math.floor(date.getTime() / 1000);
}

function firstHeader(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function parseJson(text: string): any {
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}
