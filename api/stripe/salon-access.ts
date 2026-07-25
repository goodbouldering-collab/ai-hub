import type { VercelReq, VercelRes } from "../_lib/auth.js";
import {
  AI_SALON_PLAN,
  requiredStripeEnv,
  stripeGet,
} from "../_lib/stripe.js";

const PRICE_ENV = "STRIPE_AI_SALON_PRICE_ID";
const LINE_INVITE_ENV = "AI_SALON_LINE_INVITE_URL";

export default async function handler(req: VercelReq, res: VercelRes) {
  if ((req.method || "GET").toUpperCase() !== "GET") {
    res.setHeader("Allow", "GET");
    return renderError(res, 405, "このページは決済完了後に開きます。");
  }

  const sessionId = firstQuery(req.query?.session_id);
  if (!isCheckoutSessionId(sessionId)) {
    return renderError(res, 400, "決済情報を確認できませんでした。");
  }

  try {
    const expectedPriceId = requiredStripeEnv(PRICE_ENV);
    const expand = new URLSearchParams();
    expand.append("expand[]", "line_items");
    expand.append("expand[]", "subscription");
    const session = await stripeGet(
      `/checkout/sessions/${encodeURIComponent(sessionId)}`,
      expand,
    );

    if (!hasSalonAccess(session, expectedPriceId)) {
      return renderError(
        res,
        403,
        "お支払いの完了を確認できませんでした。決済後にもう一度お開きください。",
      );
    }

    const lineInviteUrl = requiredStripeEnv(LINE_INVITE_ENV);
    if (!isHttpsUrl(lineInviteUrl)) {
      throw Object.assign(new Error(`${LINE_INVITE_ENV} must be an HTTPS URL`), {
        status: 500,
      });
    }
    return renderSuccess(res, lineInviteUrl);
  } catch (error: any) {
    return renderError(
      res,
      Number(error?.status) || 500,
      Number(error?.status) === 500
        ? "参加案内を準備中です。運営者へお問い合わせください。"
        : "決済情報を確認できませんでした。",
    );
  }
}

function hasSalonAccess(session: any, expectedPriceId: string): boolean {
  const subscription = session?.subscription;
  const subscriptionStatus =
    typeof subscription === "object" ? subscription?.status : undefined;
  const prices = Array.isArray(session?.line_items?.data)
    ? session.line_items.data.map((item: any) => item?.price?.id)
    : [];
  return (
    session?.mode === "subscription" &&
    session?.status === "complete" &&
    session?.payment_status === "paid" &&
    session?.metadata?.plan === AI_SALON_PLAN &&
    prices.includes(expectedPriceId) &&
    subscriptionStatus === "active"
  );
}

function renderSuccess(res: VercelRes, lineInviteUrl: string) {
  setSecurityHeaders(res);
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.end(
    pageShell(
      "AIオンラインサロン 参加案内",
      `<span class="eyebrow">PAYMENT CONFIRMED</span>
       <h1>有料登録が完了しました</h1>
       <p>下のボタンから、AI相談 彦根のLINEオープンチャットへお進みください。毎週火曜21:00のライブトーク案内をLINEでお届けします。</p>
       <a class="button" href="${escapeHtml(lineInviteUrl)}" target="_blank" rel="noopener noreferrer">LINEオープンチャットを開く →</a>
       <small>この参加用URLは、有料会員以外へ共有しないでください。</small>`,
    ),
  );
}

function renderError(res: VercelRes, status: number, message: string) {
  setSecurityHeaders(res);
  res.statusCode = status;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.end(
    pageShell(
      "AIオンラインサロン 参加案内",
      `<span class="eyebrow">AI ONLINE SALON</span>
       <h1>LINE参加案内を表示できません</h1>
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
  main{width:min(100%,680px);padding:clamp(28px,6vw,56px);border:1px solid rgba(83,103,217,.2);border-radius:24px;background:rgba(255,255,255,.97);box-shadow:0 24px 70px rgba(38,54,112,.12)}
  .eyebrow{color:#5367d9;font-size:11px;font-weight:900;letter-spacing:.12em}h1{margin:12px 0 10px;font-size:clamp(28px,5vw,44px);line-height:1.2}p{margin:0 0 24px;color:#607089;line-height:1.8}
  .button{min-height:50px;display:flex;align-items:center;justify-content:center;padding:13px 20px;border-radius:12px;background:#5367d9;color:#fff;font-weight:900;text-align:center;text-decoration:none}.button.secondary{display:inline-flex;background:#eef1ff;color:#3448bd}
  small{display:block;margin-top:14px;color:#7b879d;font-size:11px;line-height:1.6;text-align:center}
  </style></head><body><main>${body}</main></body></html>`;
}

function firstQuery(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

function isCheckoutSessionId(value: string): boolean {
  return /^cs_(?:test_|live_)?[A-Za-z0-9]{12,200}$/.test(value);
}

function isHttpsUrl(value: string): boolean {
  try {
    return new URL(value).protocol === "https:";
  } catch {
    return false;
  }
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
