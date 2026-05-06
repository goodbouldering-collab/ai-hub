/**
 * AI（Claude）が生成した HTML を、カラーミーテンプレに書き込む前に
 * allowlist 方式で安全化する。
 *
 * 許可タグ: h2, h3, p, ul, ol, li, strong, em, br, a (href のみ)
 * その他のタグは除去（中身の text は保持）。属性は a の href のみ許可。
 *
 * 軽量実装。完璧な sanitizer ではない（DOMPurify を入れるほどでもないため）。
 * カラーミーテンプレはユーザー入力を直接受け付けるわけではないが、AI 出力に
 * <script> 等が混入する可能性に対する最低限の防御層として置く。
 */

const ALLOWED_TAGS = new Set([
  "h2",
  "h3",
  "p",
  "ul",
  "ol",
  "li",
  "strong",
  "em",
  "b",
  "i",
  "br",
  "a",
  "small",
]);

// タグ全体（開始タグ・終了タグ・自己終了）を捕捉
const TAG_RE = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)(\s[^>]*)?\/?\s*>/g;

export function sanitizeArticleHtml(input: string): string {
  if (!input) return "";
  let out = String(input);

  // 1. <script>/<style> ブロックを内容ごと削除
  out = out.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "");
  out = out.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, "");

  // 2. on* イベントハンドラ属性は完全に削除（タグ内）
  out = out.replace(/\son[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "");

  // 3. javascript: の href / src を削除
  out = out.replace(/(href|src)\s*=\s*("javascript:[^"]*"|'javascript:[^']*'|javascript:[^\s>]+)/gi, "");

  // 4. allowlist 外のタグを除去（中身の text は残す）
  out = out.replace(TAG_RE, (match, slash, name, attrs) => {
    const tag = String(name).toLowerCase();
    if (!ALLOWED_TAGS.has(tag)) return "";
    // a タグは href のみ許可、それ以外の属性は捨てる
    if (tag === "a" && !slash) {
      const href = /\bhref\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrs || "");
      const url = href?.[2] ?? href?.[3] ?? href?.[4] ?? "";
      if (!url || /^javascript:/i.test(url)) return "<a>";
      return `<a href="${escapeAttr(url)}" rel="noopener noreferrer">`;
    }
    // それ以外の許可タグは属性を全部捨てて素のタグだけ通す
    return slash ? `</${tag}>` : `<${tag}>`;
  });

  return out.trim();
}

function escapeAttr(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
