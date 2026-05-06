import { withAdmin } from "../_lib/http.js";

export default withAdmin({ method: "GET" }, async ({ res }) => {
  res.status(200).json({
    ok: true,
    now: new Date().toISOString(),
    env: {
      hasColorme: Boolean(process.env.COLORME_ACCESS_TOKEN),
      hasAnthropic: Boolean(process.env.ANTHROPIC_API_KEY),
      hasOpenAI: Boolean(process.env.OPENAI_API_KEY),
      hasSupabase: Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY),
    },
  });
});
