/**
 * portal スキーマ用 Supabase クライアントと sns_posts mapper。
 * ai_watch.* スキーマとは完全分離。
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { requireEnv } from "./config.js";

let _supa: SupabaseClient | null = null;
function client(): SupabaseClient {
  if (_supa) return _supa;
  const url = requireEnv("SUPABASE_URL");
  const key = requireEnv("SUPABASE_SERVICE_ROLE_KEY");
  _supa = createClient(url, key, { auth: { persistSession: false } });
  return _supa;
}

export type SnsPostStatus = "pending" | "ok" | "error" | "skipped";

export type SnsPostRow = {
  id: number;
  created_at: string;
  text: string;
  image_url: string | null;
  x_status: SnsPostStatus;
  x_post_id: string | null;
  x_error: string | null;
  threads_status: SnsPostStatus;
  threads_post_id: string | null;
  threads_error: string | null;
};

export type SnsPost = {
  id: number;
  createdAt: string;
  text: string;
  imageUrl: string | null;
  xStatus: SnsPostStatus;
  xPostId: string | null;
  xError: string | null;
  threadsStatus: SnsPostStatus;
  threadsPostId: string | null;
  threadsError: string | null;
};

function rowToSnsPost(row: SnsPostRow): SnsPost {
  return {
    id: row.id,
    createdAt: row.created_at,
    text: row.text,
    imageUrl: row.image_url,
    xStatus: row.x_status,
    xPostId: row.x_post_id,
    xError: row.x_error,
    threadsStatus: row.threads_status,
    threadsPostId: row.threads_post_id,
    threadsError: row.threads_error,
  };
}

export type InsertSnsPost = {
  text: string;
  imageUrl?: string | null;
  xStatus: SnsPostStatus;
  xPostId?: string | null;
  xError?: string | null;
  threadsStatus: SnsPostStatus;
  threadsPostId?: string | null;
  threadsError?: string | null;
};

export async function insertSnsPost(data: InsertSnsPost): Promise<SnsPost> {
  const supa = client() as any;
  const { data: row, error } = await supa
    .schema("portal")
    .from("sns_posts")
    .insert({
      text: data.text,
      image_url: data.imageUrl ?? null,
      x_status: data.xStatus,
      x_post_id: data.xPostId ?? null,
      x_error: data.xError ?? null,
      threads_status: data.threadsStatus,
      threads_post_id: data.threadsPostId ?? null,
      threads_error: data.threadsError ?? null,
    })
    .select()
    .single();
  if (error) throw new Error(`sns_posts insert failed: ${error.message}`);
  return rowToSnsPost(row as SnsPostRow);
}

export async function listSnsPosts(limit = 30): Promise<SnsPost[]> {
  const supa = client() as any;
  const { data, error } = await supa
    .schema("portal")
    .from("sns_posts")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);
  if (error) throw new Error(`sns_posts select failed: ${error.message}`);
  return (data as SnsPostRow[]).map(rowToSnsPost);
}
