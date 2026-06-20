import type { VercelReq, VercelRes } from "../_lib/auth.js";
import {
  MONTHLY_SUPPORT_PLAN,
  publicOrigin,
  requiredStripeEnv,
  stripePost,
  supportTermMonths,
} from "../_lib/stripe.js";

const PRICE_ENV = "STRIPE_MONTHLY_SUPPORT_PRICE_ID";

export default async function handler(req: VercelReq, res: VercelRes) {
  const method = (req.method || "GET").toUpperCase();
  if (method !== "GET" && method !== "POST") {
    return sendError(req, res, 405, "method not allowed");
  }

  try {
    const priceId = requiredStripeEnv(PRICE_ENV);
    const termMonths = supportTermMonths();
    const origin = publicOrigin(req);
    const successUrl =
      process.env.STRIPE_SUCCESS_URL || `${origin}/?stripe=success#contact`;
    const cancelUrl = process.env.STRIPE_CANCEL_URL || `${origin}/#packages`;

    const params = new URLSearchParams();
    params.set("mode", "subscription");
    params.set("success_url", successUrl);
    params.set("cancel_url", cancelUrl);
    params.set("locale", "ja");
    params.set("billing_address_collection", "auto");
    params.set("phone_number_collection[enabled]", "true");
    params.set("line_items[0][price]", priceId);
    params.set("line_items[0][quantity]", "1");
    params.set("client_reference_id", `${MONTHLY_SUPPORT_PLAN}-${Date.now()}`);
    params.set("metadata[plan]", MONTHLY_SUPPORT_PLAN);
    params.set("metadata[term_months]", String(termMonths));
    params.set("subscription_data[metadata][plan]", MONTHLY_SUPPORT_PLAN);
    params.set("subscription_data[metadata][term_months]", String(termMonths));
    if (process.env.STRIPE_ALLOW_PROMOTION_CODES === "true") {
      params.set("allow_promotion_codes", "true");
    }
    if (process.env.STRIPE_AUTOMATIC_TAX === "true") {
      params.set("automatic_tax[enabled]", "true");
    }

    const session = await stripePost("/checkout/sessions", params);
    if (typeof session?.url !== "string") {
      throw Object.assign(new Error("Stripe did not return a checkout URL"), {
        status: 502,
        publicMessage: "Stripe checkout could not be started.",
      });
    }

    if (method === "POST" || acceptsJson(req)) {
      res.setHeader("Cache-Control", "no-store");
      return res.status(200).json({ ok: true, url: session.url, id: session.id });
    }

    res.statusCode = 303;
    res.setHeader("Location", session.url);
    res.setHeader("Cache-Control", "no-store");
    return res.end();
  } catch (error: any) {
    return sendError(
      req,
      res,
      Number(error?.status) || 500,
      error?.publicMessage || error?.message || "Stripe checkout error",
      error?.message,
    );
  }
}

function acceptsJson(req: VercelReq): boolean {
  const accept = req.headers.accept;
  const value = Array.isArray(accept) ? accept.join(",") : accept || "";
  return value.includes("application/json");
}

function sendError(
  req: VercelReq,
  res: VercelRes,
  status: number,
  message: string,
  detail?: unknown,
) {
  res.setHeader("Cache-Control", "no-store");
  if (acceptsJson(req)) {
    return res.status(status).json({ ok: false, error: message, detail });
  }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.statusCode = status;
  return res.end(
    "<!doctype html><meta charset='utf-8'>" +
      "<body style='font-family:system-ui,sans-serif;padding:40px;line-height:1.7'>" +
      "<h1>Stripe checkout is not ready</h1>" +
      `<p>${escapeHtml(message)}</p>` +
      "<p><a href='/#packages'>Back to plans</a></p>" +
      "</body>",
  );
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (ch) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[ch];
  });
}
