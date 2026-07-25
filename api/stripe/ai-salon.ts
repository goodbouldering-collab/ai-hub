import type { VercelReq, VercelRes } from "../_lib/auth.js";
import {
  AI_SALON_PLAN,
  publicOrigin,
  requiredStripeEnv,
  stripePost,
} from "../_lib/stripe.js";

const PRICE_ENV = "STRIPE_AI_SALON_PRICE_ID";

export default async function handler(req: VercelReq, res: VercelRes) {
  if ((req.method || "GET").toUpperCase() !== "POST") {
    res.setHeader("Allow", "POST");
    return sendError(res, 405, "有料登録ボタンからお進みください。");
  }

  try {
    const priceId = requiredStripeEnv(PRICE_ENV);
    const origin = publicOrigin(req);
    const params = new URLSearchParams();
    params.set("mode", "subscription");
    params.set(
      "success_url",
      `${origin}/api/stripe/salon-access?session_id={CHECKOUT_SESSION_ID}`,
    );
    params.set("cancel_url", `${origin}/#seven-day-courses`);
    params.set("locale", "ja");
    params.set("line_items[0][price]", priceId);
    params.set("line_items[0][quantity]", "1");
    params.set("client_reference_id", `${AI_SALON_PLAN}-${Date.now()}`);
    params.set("metadata[plan]", AI_SALON_PLAN);
    params.set("subscription_data[metadata][plan]", AI_SALON_PLAN);
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
        publicMessage: "決済画面を開始できませんでした。",
      });
    }

    res.statusCode = 303;
    res.setHeader("Location", session.url);
    res.setHeader("Cache-Control", "no-store");
    return res.end();
  } catch (error: any) {
    return sendError(
      res,
      Number(error?.status) || 500,
      error?.publicMessage || "決済画面を開始できませんでした。",
    );
  }
}

function sendError(res: VercelRes, status: number, message: string) {
  setSecurityHeaders(res);
  res.statusCode = status;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.end(
    pageShell(
      "AIオンラインサロン 有料登録",
      `<span class="eyebrow">AI ONLINE SALON</span>
       <h1>決済画面を開けませんでした</h1>
       <p>${escapeHtml(message)}</p>
       <a class="button secondary" href="/#seven-day-courses">サロン案内へ戻る</a>`,
    ),
  );
}

function setSecurityHeaders(res: VercelRes) {
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.setHeader("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
}

function pageShell(title: string, body: string): string {
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(title)}</title><style>
  :root{color-scheme:light;font-family:Inter,"Noto Sans JP",system-ui,sans-serif;color:#172238;background:#f4f6ff}
  *{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;background:linear-gradient(145deg,#f4f1ff,#fff 52%,#eef2ff)}
  main{width:min(100%,640px);padding:clamp(28px,6vw,52px);border:1px solid rgba(83,103,217,.2);border-radius:24px;background:rgba(255,255,255,.96);box-shadow:0 24px 70px rgba(38,54,112,.12)}
  .eyebrow{color:#5367d9;font-size:11px;font-weight:900;letter-spacing:.12em}h1{margin:12px 0 10px;font-size:clamp(26px,5vw,42px);line-height:1.2}p{margin:0 0 24px;color:#607089;line-height:1.8}
  .button{min-height:48px;display:inline-flex;align-items:center;justify-content:center;padding:12px 20px;border-radius:12px;background:#5367d9;color:#fff;font-weight:900;text-decoration:none}.button.secondary{background:#eef1ff;color:#3448bd}
  </style></head><body><main>${body}</main></body></html>`;
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
