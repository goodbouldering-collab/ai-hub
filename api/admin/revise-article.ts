import { ValidationError, withAdmin } from "../_lib/http.js";
import { reviseArticle } from "../_lib/ai.js";

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const title = String(body?.title || "").trim();
  const html = String(body?.html || "").trim();
  const instruction = String(body?.instruction || "").trim();
  if (!title || !html || !instruction) {
    throw new ValidationError("title, html, instruction are required");
  }
  const out = await reviseArticle({ title, html }, instruction);
  res.status(200).json(out);
});
