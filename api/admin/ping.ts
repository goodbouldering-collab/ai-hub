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
      hasAiSalonStripe: Boolean(
        process.env.STRIPE_SECRET_KEY &&
          process.env.STRIPE_AI_SALON_PRICE_ID &&
          process.env.AI_SALON_LINE_INVITE_URL,
      ),
      hasSupabase: Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY),
    },
    snsCreds: snsCredentialStatus(),
  });
});
