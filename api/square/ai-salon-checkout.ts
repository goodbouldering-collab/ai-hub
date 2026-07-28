import { randomUUID } from "node:crypto";
import type { VercelReq, VercelRes } from "../_lib/auth.js";
import {
  AI_SALON_ITEM_NAME,
  publicOrigin,
  requiredSquareEnv,
  salonPlanVariationId,
  salonPriceYen,
  squareJson,
} from "../_lib/square.js";

type PaymentLinkResponse = {
  payment_link?: {
    id?: string;
    order_id?: string;
    url?: string;
  };
};

export default async function handler(req: VercelReq, res: VercelRes) {
  const method = (req.method || "GET").toUpperCase();
  if (method !== "GET" && method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    return sendError(res, 405, "この操作には対応していません。");
  }

  try {
    const priceYen = salonPriceYen();
    if (method === "GET") {
      return renderCheckoutIntro(res, priceYen);
    }

    const locationId = requiredSquareEnv("SQUARE_LOCATION_ID");
    const planVariationId = salonPlanVariationId();
    const origin = publicOrigin(req);
    const payload = {
      idempotency_key: randomUUID(),
      description: "AI相談 AIオンラインサロン参加",
      quick_pay: {
        name: AI_SALON_ITEM_NAME,
        price_money: { amount: priceYen, currency: "JPY" },
        location_id: locationId,
      },
      checkout_options: {
        redirect_url: `${origin}/api/square/ai-salon-access`,
        subscription_plan_id: planVariationId,
        allow_tipping: false,
        ask_for_shipping_address: false,
        custom_fields: [{ title: "LINEオープンチャット参加名" }],
      },
      payment_note: "AI相談 AIオンラインサロン月額参加費",
    };
    const result = await squareJson<PaymentLinkResponse>(
      "/v2/online-checkout/payment-links",
      { method: "POST", body: JSON.stringify(payload) },
    );
    const checkoutUrl = result.payment_link?.url;
    if (!checkoutUrl) {
      throw Object.assign(new Error("Square did not return a checkout URL."), {
        status: 502,
        publicMessage: "Squareの決済画面を開けませんでした。",
      });
    }

    res.statusCode = 303;
    res.setHeader("Location", checkoutUrl);
    res.setHeader("Cache-Control", "no-store");
    return res.end();
  } catch (error: any) {
    return sendError(
      res,
      Number(error?.status) || 500,
      error?.publicMessage || "Squareの決済画面を開けませんでした。",
    );
  }
}

function renderCheckoutIntro(res: VercelRes, priceYen: number) {
  res.statusCode = 200;
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
  return res.end(`<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AIオンラインサロン | AI相談</title>
<style>
:root{color-scheme:light;font-family:Inter,"Noto Sans JP",system-ui,sans-serif;color:#071c38;background:#f3f6fb}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px}
main{width:min(560px,100%);padding:30px;border:1px solid #dbe4ef;border-radius:20px;background:#fff;box-shadow:0 24px 60px rgba(7,28,56,.10)}
small{color:#075fc8;font-weight:900;letter-spacing:.1em}h1{margin:10px 0 0;font-size:clamp(28px,7vw,42px);letter-spacing:-.04em}
.price{margin:18px 0 0;font-size:28px;font-weight:950}.price span{font-size:13px;color:#64748b}
p{color:#52657a;line-height:1.75}ol{margin:22px 0;padding:0;display:grid;gap:10px;list-style:none}
li{display:grid;grid-template-columns:32px 1fr;gap:10px;align-items:center;color:#24344a;font-size:14px}
li b{display:grid;place-items:center;width:32px;height:32px;border-radius:9px;color:#fff;background:#075fc8}
button{width:100%;min-height:54px;margin-top:18px;border:0;border-radius:10px;color:#fff;background:#075fc8;font-size:15px;font-weight:950;cursor:pointer}
button:hover{background:#064ca1}.note{margin:11px 0 0;font-size:11px;text-align:center}
a{color:#075fc8;font-weight:800}
</style></head><body><main>
<small>SQUARE PAYMENT</small><h1>AIオンラインサロン</h1>
<div class="price">月額 ¥${priceYen.toLocaleString("ja-JP")} <span>税込</span></div>
<p>Squareの安全な決済画面で月額プランをお申し込み後、LINEオープンチャットの参加案内を表示します。</p>
<ol><li><b>1</b><span>Squareで決済</span></li><li><b>2</b><span>LINEで参加申請</span></li><li><b>3</b><span>決済名を確認して参加承認</span></li></ol>
<form method="post"><button type="submit">Squareの決済画面へ</button></form>
<p class="note">毎月自動更新です。決済前にLINEの招待URLは表示されません。</p>
<p><a href="/#seven-day-courses">← サロン案内へ戻る</a></p>
</main></body></html>`);
}

function sendError(res: VercelRes, status: number, message: string) {
  res.statusCode = status;
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
  return res.end(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<body style="font-family:system-ui,sans-serif;padding:40px;line-height:1.7"><h1>Square決済を開始できません</h1>
<p>${escapeHtml(message)}</p><p><a href="/#seven-day-courses">サロン案内へ戻る</a></p></body>`);
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
