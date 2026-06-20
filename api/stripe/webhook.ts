import type { VercelReq, VercelRes } from "../_lib/auth.js";
import {
  MONTHLY_SUPPORT_PLAN,
  addMonthsUnix,
  readRawBody,
  requiredStripeEnv,
  stripePost,
  supportTermMonths,
  verifyStripeSignature,
} from "../_lib/stripe.js";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: VercelReq, res: VercelRes) {
  if ((req.method || "POST").toUpperCase() !== "POST") {
    return res.status(405).json({ ok: false, error: "method not allowed" });
  }

  try {
    const rawBody = await readRawBody(req);
    const signature = Array.isArray(req.headers["stripe-signature"])
      ? req.headers["stripe-signature"][0]
      : req.headers["stripe-signature"];
    const webhookSecret = requiredStripeEnv("STRIPE_WEBHOOK_SECRET");
    if (!verifyStripeSignature(rawBody, signature, webhookSecret)) {
      return res.status(400).json({ ok: false, error: "invalid signature" });
    }

    const event = JSON.parse(rawBody);
    if (
      event.type === "checkout.session.completed" ||
      event.type === "checkout.session.async_payment_succeeded"
    ) {
      await handleCheckoutSession(event);
    }

    return res.status(200).json({ ok: true, received: true });
  } catch (error: any) {
    const status = Number(error?.status) || 500;
    return res.status(status).json({
      ok: false,
      error: error?.message || "stripe webhook error",
    });
  }
}

async function handleCheckoutSession(event: any): Promise<void> {
  const session = event?.data?.object;
  if (session?.metadata?.plan !== MONTHLY_SUPPORT_PLAN) return;

  const subscriptionId =
    typeof session.subscription === "string"
      ? session.subscription
      : session.subscription?.id;
  if (!subscriptionId) return;

  const termMonths = parseTermMonths(session.metadata?.term_months);
  const createdAt = Number(session.created || event.created || Date.now() / 1000);
  const cancelAt = addMonthsUnix(createdAt, termMonths);

  const params = new URLSearchParams();
  params.set("cancel_at", String(cancelAt));
  params.set("metadata[plan]", MONTHLY_SUPPORT_PLAN);
  params.set("metadata[term_months]", String(termMonths));
  params.set("metadata[cancel_at_source]", "ai-hub-webhook");

  await stripePost(`/subscriptions/${encodeURIComponent(subscriptionId)}`, params);
}

function parseTermMonths(value: unknown): number {
  const parsed = Number(value);
  if (Number.isFinite(parsed) && parsed >= 1) {
    return Math.min(Math.floor(parsed), 36);
  }
  return supportTermMonths();
}
