/**
 * GET  /api/admin/sns-post  → SNS 投稿 UI HTML を返す（Basic 認証付き）
 * POST /api/admin/sns-post  → X + Threads に投稿し、portal.sns_posts にログを記録
 *
 * POST body:
 *   text: string          投稿テキスト（必須）
 *   postToX: boolean      X に投稿するか（true / false）
 *   postToThreads: boolean Threads に投稿するか（true / false）
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ValidationError, withAdmin } from "../_lib/http.js";
import { postToX, postToThreads, snsCredentialStatus } from "../_lib/sns.js";
import { insertSnsPost, type SnsPostStatus } from "../_lib/supabase-portal.js";
import type { VercelReq, VercelRes } from "../_lib/auth.js";

let cachedHtml: string | null = null;

function getSnsPostHtml(): string {
  if (!cachedHtml) {
    const p = join(process.cwd(), "site", "static", "admin", "sns-post.html");
    cachedHtml = readFileSync(p, "utf-8");
  }
  return cachedHtml;
}

const getHandler = withAdmin({ method: "GET" }, async ({ res }) => {
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(getSnsPostHtml());
});

const postHandler = withAdmin({ method: "POST" }, async ({ res, body }) => {
  const text = String(body?.text || "").trim();
  if (!text) throw new ValidationError("text is required");
  if (text.length > 140) throw new ValidationError("text must be 140 chars or less");

  const wantX = body?.postToX === true;
  const wantThreads = body?.postToThreads === true;
  if (!wantX && !wantThreads) throw new ValidationError("at least one platform must be selected");

  const creds = snsCredentialStatus();

  const [xResult, threadsResult] = await Promise.all([
    wantX ? postToX(text) : Promise.resolve({ status: "skipped" as const, error: "not requested" }),
    wantThreads ? postToThreads(text) : Promise.resolve({ status: "skipped" as const, error: "not requested" }),
  ]);

  const post = await insertSnsPost({
    text,
    xStatus: xResult.status as SnsPostStatus,
    xPostId: xResult.postId ?? null,
    xError: xResult.error ?? null,
    threadsStatus: threadsResult.status as SnsPostStatus,
    threadsPostId: threadsResult.postId ?? null,
    threadsError: threadsResult.error ?? null,
  });

  res.status(200).json({
    post,
    x: xResult,
    threads: threadsResult,
    credentialStatus: creds,
  });
});

export default async function handler(req: VercelReq, res: VercelRes): Promise<void> {
  const method = (req.method || "GET").toUpperCase();
  if (method === "GET") {
    return getHandler(req, res);
  }
  return postHandler(req, res);
}
