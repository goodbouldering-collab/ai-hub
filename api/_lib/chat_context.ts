/**
 * /api/admin/chat 用のコンテキスト構築。
 *
 * 戦略（MVP）:
 *  - content/consul-work/*.md と config/businesses.yaml をビルド時 bundle 済み（vercel.json の includeFiles）
 *  - 質問文に含まれるキーワードでファイル名を簡易マッチし、ヒットした上位 N 件を全文で context に積む
 *  - ヒットゼロなら recent 8 件のタイトルと冒頭をサマリとして渡す
 *  - 全体で 12000 文字程度で打ち切る（Claude の system tokens を抑える）
 *
 * いずれ embedding + ベクタ検索に置き換えたいが、まずは grep ベースで実用範囲を見る。
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const MAX_CONTEXT_CHARS = 12_000;
const MAX_FILES = 5;

function consulWorkDir(): string {
  return join(process.cwd(), "content", "consul-work");
}

function safeRead(p: string): string {
  try {
    return readFileSync(p, "utf-8");
  } catch {
    return "";
  }
}

function listConsulWorkFiles(): string[] {
  try {
    return readdirSync(consulWorkDir()).filter((n) => n.endsWith(".md"));
  } catch {
    return [];
  }
}

/** タイトル（最初の H1 / H2）を抜き出す（フロントマターは飛ばす） */
function readTitle(text: string, fallback: string): string {
  let body = text;
  if (body.startsWith("---")) {
    const m = body.indexOf("\n---", 3);
    if (m !== -1) body = body.slice(m + 4);
  }
  for (const line of body.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (trimmed.startsWith("#")) return trimmed.replace(/^#+\s*/, "");
  }
  return fallback;
}

/**
 * 質問の中の日本語/英数字トークンを抜き出してファイル名にマッチ。
 * カタカナ語・事業名・カテゴリ名を拾えるよう 2文字以上のトークンを許容する。
 */
function tokenize(query: string): string[] {
  const cleaned = query
    .toLowerCase()
    .replace(/[、。「」『』,.!?！？\s]+/g, " ");
  return Array.from(new Set(cleaned.split(/\s+/).filter((t) => t.length >= 2)));
}

function scoreFile(name: string, tokens: string[]): number {
  const lower = name.toLowerCase();
  let s = 0;
  for (const t of tokens) {
    if (lower.includes(t)) s += 2;
    // 事業名の英日変換
    if (t === "グッぼる" && lower.includes("good")) s += 2;
    if (t === "ビジネス21" && lower.includes("business-21")) s += 2;
    if (t === "エステ" && lower.includes("este")) s += 2;
    if (t === "nデザイン" && lower.includes("n-design")) s += 2;
  }
  return s;
}

export function buildChatContext(userQuestion: string): string {
  const files = listConsulWorkFiles();
  if (files.length === 0) {
    return "(consul-work ドキュメントは現在利用できません)";
  }

  const tokens = tokenize(userQuestion);
  // スコア順
  const ranked = files
    .map((f) => ({ f, score: scoreFile(f, tokens) }))
    .sort((a, b) => b.score - a.score || (a.f < b.f ? 1 : -1)); // 同スコアなら新しい日付（降順）

  const top = ranked.filter((r) => r.score > 0).slice(0, MAX_FILES);

  // ヒット 0 のときは最新 8 件のタイトル列挙だけ
  if (top.length === 0) {
    const recent = files.sort().reverse().slice(0, 8);
    const lines: string[] = ["[social/work 最近の成果物（タイトルのみ・本文は質問キーワードでヒット時に展開）]"];
    for (const name of recent) {
      const text = safeRead(join(consulWorkDir(), name));
      lines.push(`- ${name}: ${readTitle(text, name).slice(0, 80)}`);
    }
    return lines.join("\n");
  }

  // ヒットしたファイルを全文で積む（合計 12000 文字に収める）
  const blocks: string[] = [];
  let total = 0;
  for (const { f } of top) {
    const text = safeRead(join(consulWorkDir(), f));
    if (!text) continue;
    const block = `### consul-work/${f}\n${text}\n`;
    if (total + block.length > MAX_CONTEXT_CHARS) {
      blocks.push(block.slice(0, MAX_CONTEXT_CHARS - total));
      total = MAX_CONTEXT_CHARS;
      break;
    }
    blocks.push(block);
    total += block.length;
  }
  return blocks.join("\n---\n");
}
