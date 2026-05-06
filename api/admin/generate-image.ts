import { ValidationError, withAdmin } from "../_lib/http.js";
import { generateImageBytes } from "../_lib/ai.js";
import { uploadPublicImage } from "../_lib/storage.js";

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const prompt = String(body?.prompt || "").trim();
  const filenameHint = String(body?.filenameHint || "group").trim();
  if (!prompt) throw new ValidationError("prompt is required");
  const { bytes, contentType } = await generateImageBytes(prompt);
  const safeName = `${filenameHint.replace(/[^\w-]/g, "_")}.png`;
  const url = await uploadPublicImage(bytes, safeName, contentType);
  res.status(200).json({ url });
});
