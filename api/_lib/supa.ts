/**
 * Supabase service_role クライアント（DB アクセス用・共通）
 *
 * storage.ts は Storage 専用にクライアントを内包しているが、
 * /ops のプロンプト永続化は DB テーブルアクセスなので汎用クライアントを切り出す。
 * 生成パターンは storage.ts と同一（auth.persistSession:false / service_role）。
 */
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { requireEnv } from "./config.js";

let _db: SupabaseClient | null = null;

export function db(): SupabaseClient {
  if (_db) return _db;
  const url = requireEnv("SUPABASE_URL");
  const key = requireEnv("SUPABASE_SERVICE_ROLE_KEY");
  _db = createClient(url, key, { auth: { persistSession: false } });
  return _db;
}
