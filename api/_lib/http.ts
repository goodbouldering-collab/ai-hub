/**
 * Vercel Functions 共通ユーティリティ。
 * - readJson: body を1MB上限で安全に JSON 化
 * - sendError: エラー応答 shape の一元化
 * - methodGuard: 許容 HTTP method 以外を 405 で弾く
 * - withAdmin: requireAdminAuth + methodGuard + JSON parse + エラーハンドリングを1関数にまとめる
 *
 * すべての admin endpoint はこのファイルを経由すること。
 */

import { requireAdminAuth, type VercelReq, type VercelRes } from "./auth.js";

const MAX_BODY_BYTES = 1024 * 1024; // 1MB（カラーミーのテンプレ HTML が乗ることを想定して余裕）

export class ConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConfigError";
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ValidationError";
  }
}

export async function readJson(req: VercelReq): Promise<any> {
  if (req.body && typeof req.body === "object") return req.body;
  const lenHeader = req.headers["content-length"];
  if (typeof lenHeader === "string" && Number(lenHeader) > MAX_BODY_BYTES) {
    throw new ValidationError(`request body too large (>${MAX_BODY_BYTES} bytes)`);
  }
  const chunks: Buffer[] = [];
  let total = 0;
  for await (const c of req as any) {
    const buf = c as Buffer;
    total += buf.length;
    if (total > MAX_BODY_BYTES) {
      throw new ValidationError(`request body too large (>${MAX_BODY_BYTES} bytes)`);
    }
    chunks.push(buf);
  }
  const text = Buffer.concat(chunks).toString("utf-8");
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch (e: any) {
    throw new ValidationError(`invalid JSON: ${e.message}`);
  }
}

export type ErrorShape = { error: string; detail?: unknown };

export function sendError(
  res: VercelRes,
  status: number,
  message: string,
  detail?: unknown,
): void {
  const body: ErrorShape = { error: message };
  if (detail !== undefined) body.detail = detail;
  res.status(status).json(body);
}

export function methodGuard(
  req: VercelReq,
  res: VercelRes,
  allowed: string | string[],
): boolean {
  const list = Array.isArray(allowed) ? allowed : [allowed];
  const method = (req.method || "GET").toUpperCase();
  if (!list.includes(method)) {
    sendError(res, 405, `method not allowed (allowed: ${list.join(",")})`);
    return false;
  }
  return true;
}

export type Handler<T = unknown> = (ctx: {
  req: VercelReq;
  res: VercelRes;
  body: any;
}) => Promise<T> | T;

export type WithAdminOptions = {
  method?: string | string[];
  parseBody?: boolean; // デフォルト: POST/PUT/PATCH なら true
};

/**
 * すべての admin endpoint をラップする統一エントリ:
 *  - 管理画面のパスワード認証チェック (auth.ts)
 *  - HTTP method ガード
 *  - JSON body の安全な読み込み（必要な場合）
 *  - 例外を ConfigError / ValidationError / 一般 Error に分けて適切な status で返す
 */
export function withAdmin(
  options: WithAdminOptions,
  handler: Handler,
): (req: VercelReq, res: VercelRes) => Promise<void> {
  return async (req, res) => {
    if (!requireAdminAuth(req, res)) return;
    if (options.method && !methodGuard(req, res, options.method)) return;

    let body: any = {};
    const method = (req.method || "GET").toUpperCase();
    const shouldParse =
      options.parseBody ?? ["POST", "PUT", "PATCH"].includes(method);
    if (shouldParse) {
      try {
        body = await readJson(req);
      } catch (e: any) {
        if (e instanceof ValidationError) {
          sendError(res, 413, e.message);
        } else {
          sendError(res, 400, e?.message || "invalid request body");
        }
        return;
      }
    }

    try {
      await handler({ req, res, body });
    } catch (e: any) {
      if (e instanceof ConfigError) {
        sendError(res, 500, `[config] ${e.message}`);
      } else if (e instanceof ValidationError) {
        sendError(res, 400, e.message);
      } else if (typeof e?.status === "number") {
        // 上流 API エラー (colorme/anthropic/openai) の status を踏襲
        sendError(res, e.status, e.message || "upstream error", e.body);
      } else {
        sendError(res, 500, e?.message || "internal error");
      }
    }
  };
}
