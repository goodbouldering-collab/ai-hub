import { ValidationError, withAdmin } from "../_lib/http.js";
import { generateArticleDrafts } from "../_lib/ai.js";

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const theme = String(body?.theme || "").trim();
  const count = Math.min(Math.max(Number(body?.count) || 3, 1), 5);
  if (!theme) throw new ValidationError("theme is required");
  const drafts = await generateArticleDrafts(theme, count);
  res.status(200).json({ drafts });
});
