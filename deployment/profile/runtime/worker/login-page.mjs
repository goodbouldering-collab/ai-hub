// Login markup retained from api/admin/login.ts at d7cc730.
export function loginPage(safeNext, error = '', logout = false) {
  return `<!doctype html>
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
    .back-link {
      min-height: 44px;
      margin-top: 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      color: var(--ink);
      font-size: 14px;
      font-weight: 800;
      text-decoration: none;
    }
    .back-link:hover,
    .back-link:focus-visible {
      border-color: var(--blue);
      color: var(--blue);
      outline: none;
      box-shadow: 0 0 0 4px rgba(7, 95, 200, .1);
    }
  </style>
<link id="studio-design" rel="stylesheet" href="/design-system/studio/studio.css?v=20260914">
</head>
<body class="studio-theme studio-admin studio-login">
  <main>
    <div class="brand"><strong>AI相談</strong><span>彦根</span></div>
    <h1>${logout ? '管理画面ログアウト' : '管理画面ログイン'}</h1>
    <p>${logout ? 'このブラウザの管理画面からログアウトします。' : 'ユーザー名は不要です。管理用パスワードだけ入力してください。'}</p>
    ${error ? `<div class="error">${escapeHtml(error)}</div>` : ""}
    <form method="post" action="${logout ? '/admin/logout' : '/admin/login'}" autocomplete="on">
      <input type="hidden" name="next" value="${escapeHtml(safeNext)}">
      ${logout ? '' : '<label for="password">管理パスワード</label><input id="password" name="password" type="password" autocomplete="current-password" required autofocus>'}
      <button type="submit">${logout ? 'ログアウト' : 'ログイン'}</button>
    </form>
    <a class="back-link" href="/">← 公開ページへ戻る</a>
    <p class="note">ログイン状態はこの端末のブラウザにだけ保存されます。</p>
  </main>
</body>
</html>`;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}
