import {
  createAdminSessionCookie,
  hasValidAdminSession,
  isAdminPassword,
  safeNextPath,
  type VercelReq,
  type VercelRes,
} from "../_lib/auth.js";

export default async function handler(req: VercelReq, res: VercelRes) {
  const method = (req.method || "GET").toUpperCase();
  const next = getNext(req);

  if (method === "GET") {
    if (hasValidAdminSession(req)) {
      redirect(res, next);
      return;
    }
    sendLoginPage(res, next);
    return;
  }

  if (method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    res.status(405).send("Method not allowed");
    return;
  }

  const form = await readForm(req);
  const password = form.get("password") || "";
  const formNext = safeNextPath(form.get("next") || next);

  if (!isAdminPassword(password)) {
    sendLoginPage(res, formNext, "パスワードが違います。もう一度入力してください。", 401);
    return;
  }

  res.setHeader("Set-Cookie", createAdminSessionCookie());
  redirect(res, formNext);
}

function getNext(req: VercelReq): string {
  const queryNext = req.query?.next;
  if (queryNext) return safeNextPath(queryNext);
  try {
    const url = new URL(req.url || "/admin/login", "https://ai-hub-jp.vercel.app");
    return safeNextPath(url.searchParams.get("next"));
  } catch {
    return "/admin";
  }
}

async function readForm(req: VercelReq): Promise<URLSearchParams> {
  if (req.body && typeof req.body === "object") {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(req.body)) {
      params.set(key, Array.isArray(value) ? String(value[0] ?? "") : String(value ?? ""));
    }
    return params;
  }

  const chunks: Buffer[] = [];
  for await (const chunk of req as any) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return new URLSearchParams(Buffer.concat(chunks).toString("utf-8"));
}

function redirect(res: VercelRes, location: string): void {
  res.status(303);
  res.setHeader("Location", safeNextPath(location));
  res.send("Redirecting");
}

function sendLoginPage(
  res: VercelRes,
  next: string,
  error = "",
  status = 200,
): void {
  const safeNext = safeNextPath(next);
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.status(status).send(`<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>AI相談</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #0A1728;
      --muted: #526174;
      --line: #CBD9E8;
      --blue: #075FC8;
      --paper: #ffffff;
      --wash: #F5F9FD;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
      padding: 24px;
      color: var(--ink);
      background: linear-gradient(180deg, #FFFFFF 0%, #EAF6FF 100%);
    }
    main {
      width: min(420px, 100%);
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #FFFFFF;
      box-shadow: 0 24px 60px rgba(7, 54, 105, .13);
    }
    .brand {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      margin-bottom: 20px;
      color: var(--ink);
      background: transparent;
      font-size: 23px;
      font-weight: 900;
      letter-spacing: -.02em;
    }
    .brand strong { color: var(--blue); }
    h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.3;
      letter-spacing: 0;
    }
    p {
      margin: 10px 0 20px;
      color: var(--muted);
      line-height: 1.8;
      font-size: 14px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      color: #263447;
      font-size: 13px;
      font-weight: 800;
    }
    input {
      width: 100%;
      height: 48px;
      padding: 0 13px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--wash);
      color: var(--ink);
      font-size: 16px;
      outline: none;
    }
    input:focus {
      border-color: var(--blue);
      background: var(--paper);
      box-shadow: 0 0 0 4px rgba(7, 95, 200, .13);
    }
    button {
      width: 100%;
      min-height: 48px;
      margin-top: 16px;
      border: 0;
      border-radius: 8px;
      color: #fff;
      background: var(--blue);
      font-size: 15px;
      font-weight: 900;
      cursor: pointer;
      box-shadow: 0 14px 34px rgba(7, 95, 200, .22);
    }
    .error {
      margin: 0 0 14px;
      padding: 10px 12px;
      border: 1px solid rgba(190, 18, 60, .25);
      border-radius: 8px;
      background: #FFF1F2;
      color: #9F1239;
      font-size: 13px;
      font-weight: 800;
    }
    .note {
      margin: 14px 0 0;
      color: #6A7688;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <main>
    <div class="brand"><strong>AI相談</strong><span>彦根</span></div>
    <h1>管理画面ログイン</h1>
    <p>ユーザー名は不要です。管理用パスワードだけ入力してください。</p>
    ${error ? `<div class="error">${escapeHtml(error)}</div>` : ""}
    <form method="post" action="/admin/login" autocomplete="on">
      <input type="hidden" name="next" value="${escapeHtml(safeNext)}">
      <label for="password">管理パスワード</label>
      <input id="password" name="password" type="password" autocomplete="current-password" required autofocus>
      <button type="submit">ログイン</button>
    </form>
    <p class="note">ログイン状態はこの端末のブラウザにだけ保存されます。</p>
  </main>
</body>
</html>`);
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => {
    switch (char) {
      case "&":
        return "&amp;";
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case '"':
        return "&quot;";
      default:
        return "&#39;";
    }
  });
}
