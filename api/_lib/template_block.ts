/**
 * カラーミーテンプレートのトップページ index.html に
 * AI 生成記事ブロックを <!-- BEGIN:AI_GROUP_ARTICLES --> ... <!-- END:AI_GROUP_ARTICLES -->
 * のマーカーで囲んで埋め込む / 抽出 / 削除する。
 *
 * - ブロックは複数の記事を含むコンテナで、最上部に挿入する
 * - マーカー範囲外は絶対に触らない（手動編集との衝突防止）
 * - グループID 単位の個別マーカーを内側に持つ:
 *     <!-- BEGIN:AI_GROUP_ARTICLE_<id> --> ... <!-- END:AI_GROUP_ARTICLE_<id> -->
 */

const OUTER_BEGIN = "<!-- BEGIN:AI_GROUP_ARTICLES -->";
const OUTER_END = "<!-- END:AI_GROUP_ARTICLES -->";

export function articleMarkers(groupId: number | string): { begin: string; end: string } {
  return {
    begin: `<!-- BEGIN:AI_GROUP_ARTICLE_${groupId} -->`,
    end: `<!-- END:AI_GROUP_ARTICLE_${groupId} -->`,
  };
}

export function ensureOuterBlock(html: string): string {
  if (html.includes(OUTER_BEGIN) && html.includes(OUTER_END)) return html;
  // <body> 直後に挿入（無ければ先頭）
  const bodyOpen = html.search(/<body[^>]*>/i);
  const empty = `${OUTER_BEGIN}\n${OUTER_END}\n`;
  if (bodyOpen === -1) return empty + html;
  const insertAt = bodyOpen + (html.match(/<body[^>]*>/i)?.[0].length ?? 0);
  return html.slice(0, insertAt) + "\n" + empty + html.slice(insertAt);
}

export function extractOuterBlock(html: string): string {
  const begin = html.indexOf(OUTER_BEGIN);
  const end = html.indexOf(OUTER_END);
  if (begin === -1 || end === -1) return "";
  return html.slice(begin + OUTER_BEGIN.length, end);
}

export function replaceOuterBlock(html: string, newInner: string): string {
  const ensured = ensureOuterBlock(html);
  const begin = ensured.indexOf(OUTER_BEGIN);
  const end = ensured.indexOf(OUTER_END);
  return (
    ensured.slice(0, begin + OUTER_BEGIN.length) +
    "\n" + newInner.trim() + "\n" +
    ensured.slice(end)
  );
}

export type ArticleBlock = {
  groupId: string;
  html: string; // marker 内部の HTML（マーカー自体は含まない）
};

export function listArticles(outerInner: string): ArticleBlock[] {
  const re = /<!-- BEGIN:AI_GROUP_ARTICLE_([\w-]+) -->([\s\S]*?)<!-- END:AI_GROUP_ARTICLE_\1 -->/g;
  const out: ArticleBlock[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(outerInner)) !== null) {
    out.push({ groupId: m[1], html: m[2].trim() });
  }
  return out;
}

export function upsertArticle(
  outerInner: string,
  groupId: number | string,
  innerHtml: string,
  position: "top" | "bottom" = "top",
): string {
  const { begin, end } = articleMarkers(groupId);
  const wrapped = `${begin}\n${innerHtml.trim()}\n${end}`;
  const re = new RegExp(
    `${escapeRegExp(begin)}[\\s\\S]*?${escapeRegExp(end)}`,
    "g",
  );
  if (re.test(outerInner)) {
    return outerInner.replace(re, wrapped);
  }
  // 新規挿入
  if (position === "top") return `${wrapped}\n${outerInner}`.trim() + "\n";
  return `${outerInner.trim()}\n${wrapped}\n`;
}

export function removeArticle(outerInner: string, groupId: number | string): string {
  const { begin, end } = articleMarkers(groupId);
  const re = new RegExp(
    `${escapeRegExp(begin)}[\\s\\S]*?${escapeRegExp(end)}\\n?`,
    "g",
  );
  return outerInner.replace(re, "");
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
