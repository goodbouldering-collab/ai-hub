/**
 * X (Twitter) と Threads の投稿 API クライアント。
 * 環境変数未設定の SNS は status: "skipped" を返す（段階導入対応）。
 *
 * X: OAuth 1.0a 署名（oauth-1.0a + crypto）
 * Threads: Meta Graph API（Bearer トークン）
 */

import crypto from "node:crypto";

export type SnsPostResult = {
  status: "ok" | "error" | "skipped";
  postId?: string;
  error?: string;
};

// ──────────────────────────────────────────────
// OAuth 1.0a 署名（X API v2 用）
// oauth-1.0a パッケージの代わりに Node.js crypto で直接実装。
// 外部パッケージ依存を最小化しつつ仕様準拠。
// ──────────────────────────────────────────────

function percentEncode(s: string): string {
  return encodeURIComponent(s).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`);
}

function buildOauthSignature(
  method: string,
  url: string,
  params: Record<string, string>,
  consumerSecret: string,
  tokenSecret: string,
): string {
  const sortedParams = Object.entries(params)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${percentEncode(k)}=${percentEncode(v)}`)
    .join("&");
  const base = [method.toUpperCase(), percentEncode(url), percentEncode(sortedParams)].join("&");
  const signingKey = `${percentEncode(consumerSecret)}&${percentEncode(tokenSecret)}`;
  return crypto.createHmac("sha1", signingKey).update(base).digest("base64");
}

function buildOauthHeader(
  method: string,
  url: string,
  consumerKey: string,
  consumerSecret: string,
  accessToken: string,
  accessTokenSecret: string,
): string {
  const nonce = crypto.randomBytes(16).toString("hex");
  const timestamp = String(Math.floor(Date.now() / 1000));
  const oauthParams: Record<string, string> = {
    oauth_consumer_key: consumerKey,
    oauth_nonce: nonce,
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: timestamp,
    oauth_token: accessToken,
    oauth_version: "1.0",
  };
  const signature = buildOauthSignature(method, url, oauthParams, consumerSecret, accessTokenSecret);
  oauthParams.oauth_signature = signature;
  const headerValue = Object.entries(oauthParams)
    .map(([k, v]) => `${percentEncode(k)}="${percentEncode(v)}"`)
    .join(", ");
  return `OAuth ${headerValue}`;
}

// ──────────────────────────────────────────────
// X (Twitter) v2 投稿
// ──────────────────────────────────────────────

function hasXCredentials(): boolean {
  return Boolean(
    process.env.X_API_KEY &&
    process.env.X_API_SECRET &&
    process.env.X_ACCESS_TOKEN &&
    process.env.X_ACCESS_TOKEN_SECRET,
  );
}

export async function postToX(text: string): Promise<SnsPostResult> {
  if (!hasXCredentials()) {
    return { status: "skipped", error: "X API credentials not configured" };
  }
  const consumerKey = process.env.X_API_KEY!;
  const consumerSecret = process.env.X_API_SECRET!;
  const accessToken = process.env.X_ACCESS_TOKEN!;
  const accessTokenSecret = process.env.X_ACCESS_TOKEN_SECRET!;

  const url = "https://api.twitter.com/2/tweets";
  const method = "POST";
  const authHeader = buildOauthHeader(method, url, consumerKey, consumerSecret, accessToken, accessTokenSecret);

  try {
    const res = await fetch(url, {
      method,
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });
    const body = await res.json() as any;
    if (!res.ok) {
      const msg = body?.detail || body?.title || JSON.stringify(body).slice(0, 300);
      return { status: "error", error: `X API ${res.status}: ${msg}` };
    }
    const postId = body?.data?.id as string | undefined;
    return { status: "ok", postId };
  } catch (e: any) {
    return { status: "error", error: e?.message || "X fetch failed" };
  }
}

// ──────────────────────────────────────────────
// Threads（Meta Graph API）投稿
// 2-step: コンテナ作成 → 公開
// ──────────────────────────────────────────────

function hasThreadsCredentials(): boolean {
  return Boolean(process.env.THREADS_USER_ID && process.env.THREADS_ACCESS_TOKEN);
}

export async function postToThreads(text: string): Promise<SnsPostResult> {
  if (!hasThreadsCredentials()) {
    return { status: "skipped", error: "Threads API credentials not configured" };
  }
  const userId = process.env.THREADS_USER_ID!;
  const token = process.env.THREADS_ACCESS_TOKEN!;
  const baseUrl = "https://graph.threads.net/v1.0";

  try {
    // Step 1: コンテナ作成
    const createRes = await fetch(
      `${baseUrl}/${userId}/threads?media_type=TEXT&text=${encodeURIComponent(text)}&access_token=${token}`,
      { method: "POST" },
    );
    const createBody = await createRes.json() as any;
    if (!createRes.ok) {
      const msg = createBody?.error?.message || JSON.stringify(createBody).slice(0, 300);
      return { status: "error", error: `Threads create container ${createRes.status}: ${msg}` };
    }
    const containerId = createBody?.id as string | undefined;
    if (!containerId) {
      return { status: "error", error: "Threads: no container id returned" };
    }

    // Step 2: 公開
    const publishRes = await fetch(
      `${baseUrl}/${userId}/threads_publish?creation_id=${containerId}&access_token=${token}`,
      { method: "POST" },
    );
    const publishBody = await publishRes.json() as any;
    if (!publishRes.ok) {
      const msg = publishBody?.error?.message || JSON.stringify(publishBody).slice(0, 300);
      return { status: "error", error: `Threads publish ${publishRes.status}: ${msg}` };
    }
    const postId = publishBody?.id as string | undefined;
    return { status: "ok", postId };
  } catch (e: any) {
    return { status: "error", error: e?.message || "Threads fetch failed" };
  }
}

export function snsCredentialStatus(): {
  xConfigured: boolean;
  threadsConfigured: boolean;
} {
  return {
    xConfigured: hasXCredentials(),
    threadsConfigured: hasThreadsCredentials(),
  };
}
