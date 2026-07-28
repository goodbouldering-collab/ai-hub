import { withAdmin } from "../_lib/http.js";
import { snsCredentialStatus } from "../_lib/sns.js";

export default withAdmin({ method: "GET" }, async ({ res }) => {
  res.status(200).json({
    ok: true,
    now: new Date().toISOString(),
    env: {
      hasColorme: Boolean(process.env.COLORME_ACCESS_TOKEN),
      hasAnthropic: Boolean(process.env.ANTHROPIC_API_KEY),
      hasOpenAI: Boolean(process.env.OPENAI_API_KEY),
      hasStripe: Boolean(process.env.STRIPE_SECRET_KEY && process.env.STRIPE_WEBHOOK_SECRET),
      hasAiSalonSquare: Boolean(
        process.env.SQUARE_ACCESS_TOKEN &&
          process.env.SQUARE_LOCATION_ID &&
          process.env.SQUARE_AI_SALON_PRICE_YEN &&
          process.env.SQUARE_AI_SALON_PLAN_VARIATION_ID &&
          process.env.AI_SALON_OPENCHAT_URL,
      ),
      hasSupabase: Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY),
    },
    snsCreds: snsCredentialStatus(),
  });
});
