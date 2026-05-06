import { createClient } from "@supabase/supabase-js";

const BUCKET = process.env.SUPABASE_BUCKET || "ai-hub-public";

function client() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set");
  return createClient(url, key, { auth: { persistSession: false } });
}

export async function uploadPublicImage(
  bytes: Uint8Array,
  filename: string,
  contentType: string,
): Promise<string> {
  const supa = client();
  const path = `colorme-groups/${Date.now()}_${filename.replace(/[^\w.-]/g, "_")}`;
  const { error } = await supa.storage.from(BUCKET).upload(path, bytes, {
    contentType,
    upsert: false,
  });
  if (error) throw new Error(`Supabase upload failed: ${error.message}`);
  const { data } = supa.storage.from(BUCKET).getPublicUrl(path);
  return data.publicUrl;
}
