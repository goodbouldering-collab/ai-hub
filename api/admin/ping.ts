import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";

export default async function handler(req: VercelReq, res: VercelRes) {
  if (!requireBasicAuth(req, res)) return;
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
}
