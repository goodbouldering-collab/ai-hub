import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { requireEnv } from "./config.js";

function bucket(): string {
  return process.env.SUPABASE_BUCKET || "ai-hub-public";
}

let _supa: SupabaseClient | null = null;
function client(): SupabaseClient {
  if (_supa) return _supa;
  const url = requireEnv("SUPABASE_URL");
  const key = requireEnv("SUPABASE_SERVICE_ROLE_KEY");
  _supa = createClient(url, key, { auth: { persistSession: false } });
  return _supa;
}

export async function uploadPublicImage(
  bytes: Uint8Array,
  filename: string,
  contentType: string,
): Promise<string> {
  const supa = client();
  const b = bucket();
  const path = `colorme-groups/${Date.now()}_${filename.replace(/[^\w.-]/g, "_")}`;
  const { error } = await supa.storage.from(b).upload(path, bytes, {
    contentType,
    upsert: false,
  });
  if (error) throw new Error(`Supabase upload failed: ${error.message}`);
  const { data } = supa.storage.from(b).getPublicUrl(path);
  return data.publicUrl;
}
