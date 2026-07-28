import type { VercelReq, VercelRes } from "../_lib/auth.js";
import {
  AI_SALON_ITEM_NAME,
  requiredSquareEnv,
  salonOpenChatUrl,
  salonPriceYen,
  squareJson,
} from "../_lib/square.js";

type SquareOrder = {
  id?: string;
  location_id?: string;
  state?: string;
  total_money?: { amount?: number; currency?: string };
  line_items?: Array<{ name?: string }>;
};

export default async function handler(req: VercelReq, res: VercelRes) {
  if ((req.method || "GET").toUpperCase() !== "GET") {
    res.setHeader("Allow", "GET");
    return renderError(res, 405, "この操作には対応していません。");
  }

  try {
    const orderId = firstQuery(req.query?.orderId ?? req.query?.order_id);
    if (!orderId || !/^[A-Za-z0-9_-]{8,192}$/.test(orderId)) {
      return renderError(
        res,
        400,
        "決済情報を確認できません。Squareの決済完了画面から開き直してください。",
      );
    }

    const result = await squareJson<{ order?: SquareOrder }>(
      `/v2/orders/${encodeURIComponent(orderId)}`,
      { method: "GET" },
    );
    const order = result.order;
    const expectedLocation = requiredSquareEnv("SQUARE_LOCATION_ID");
    const expectedAmount = salonPriceYen();
    const hasSalonItem = order?.line_items?.some(
      (item) => item.name === AI_SALON_ITEM_NAME,
    );
    const isPaid =
      order?.state === "COMPLETED" &&
      order?.location_id === expectedLocation &&
      order?.total_money?.currency === "JPY" &&
      order?.total_money?.amount === expectedAmount &&
      hasSalonItem;

    if (!isPaid) {
      return renderError(
        res,
        403,
        "AIオンラインサロンの決済完了を確認できませんでした。",
      );
    }

    return renderAccess(res, salonOpenChatUrl());
  } catch (error: any) {
    return renderError(
      res,
      Number(error?.status) || 500,
      error?.publicMessage || "決済情報を確認できませんでした。",
    );
  }
}

function renderAccess(res: VercelRes, openChatUrl: string) {
  res.statusCode = 200;
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
  return res.end(`<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>決済完了 | AIオンラインサロン</title>
<style>
:root{font-family:Inter,"Noto Sans JP",system-ui,sans-serif;color:#071c38;background:#f3f6fb}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px}
main{width:min(560px,100%);padding:32px;border:1px solid #dbe4ef;border-radius:20px;background:#fff;box-shadow:0 24px 60px rgba(7,28,56,.10)}
.ok{display:grid;place-items:center;width:54px;height:54px;border-radius:50%;color:#fff;background:#16a56a;font-size:25px;font-weight:950}
h1{margin:18px 0 0;font-size:clamp(28px,7vw,40px);letter-spacing:-.04em}p{color:#52657a;line-height:1.75}
a.cta{min-height:54px;display:flex;align-items:center;justify-content:center;margin-top:22px;border-radius:10px;color:#fff;background:#06c755;font-size:15px;font-weight:950;text-decoration:none}
a.cta:hover{background:#05a847}.note{padding:14px;border-radius:10px;background:#f0f7ff;color:#24344a;font-size:12px}
</style></head><body><main>
<div class="ok">✓</div><h1>決済を確認しました</h1>
<p>Square決済時に入力した名前で、LINEオープンチャットの参加申請を送ってください。管理者が決済名と照合して承認します。</p>
<a class="cta" href="${escapeHtml(openChatUrl)}" rel="noreferrer noopener">LINEオープンチャットへ進む</a>
<p class="note">招待URLの共有はお控えください。決済を確認できない参加申請は承認されません。</p>
</main></body></html>`);
}

function renderError(res: VercelRes, status: number, message: string) {
  res.statusCode = status;
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
  return res.end(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<body style="font-family:system-ui,sans-serif;padding:40px;line-height:1.7"><h1>決済を確認できません</h1>
<p>${escapeHtml(message)}</p><p><a href="/api/square/ai-salon-checkout">決済画面へ戻る</a></p></body>`);
}

function firstQuery(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] || "" : value || "";
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
