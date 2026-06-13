import { lookup } from "node:dns/promises";
import { isIP } from "node:net";
import { ValidationError, withAdmin } from "../_lib/http.js";

const MAX_HTML_BYTES = 512 * 1024;
const MAX_REDIRECTS = 3;
const FETCH_TIMEOUT_MS = 12000;

type SocialLink = {
  platform: string;
  url: string;
  handle: string;
};

type IntakeResult = {
  inputUrl: string;
  finalUrl: string;
  title: string;
  siteName: string;
  description: string;
  canonicalUrl: string;
  imageUrl: string;
  language: string;
  emails: string[];
  phones: string[];
  socialLinks: SocialLink[];
  suggestions: {
    title: string;
    theme: string;
    articleHtml: string;
    imagePrompt: string;
    dashboardConfig: {
      channelInput: string;
      accounts: Record<string, Record<string, string>>;
    };
  };
};

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const inputUrl = normalizeInputUrl(String(body?.url || ""));
  const { finalUrl, html } = await fetchPublicHtml(inputUrl);
  const result = analyzeHtml(inputUrl, finalUrl, html);
  res.status(200).json({ ok: true, ...result });
});

function normalizeInputUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) throw new ValidationError("url is required");
  const withScheme = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
  let parsed: URL;
  try {
    parsed = new URL(withScheme);
  } catch {
    throw new ValidationError("url is invalid");
  }
  if (!["http:", "https:"].includes(parsed.protocol)) {
    throw new ValidationError("http/https URL only");
  }
  parsed.hash = "";
  return parsed.toString();
}

async function fetchPublicHtml(url: string, redirectCount = 0): Promise<{ finalUrl: string; html: string }> {
  const parsed = new URL(url);
  await assertPublicHostname(parsed.hostname);

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const response = await fetch(parsed.toString(), {
      redirect: "manual",
      signal: controller.signal,
      headers: {
        "accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
        "user-agent": "AIHubSiteIntake/1.0 (+https://ai-hub-jp.vercel.app/admin)",
      },
    });

    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (!location) throw new ValidationError("redirect location is empty");
      if (redirectCount >= MAX_REDIRECTS) throw new ValidationError("too many redirects");
      const next = new URL(location, parsed).toString();
      return fetchPublicHtml(next, redirectCount + 1);
    }

    if (!response.ok) {
      throw new ValidationError(`homepage fetch failed: HTTP ${response.status}`);
    }

    const contentLength = Number(response.headers.get("content-length") || 0);
    if (contentLength > MAX_HTML_BYTES) {
      throw new ValidationError(`homepage is too large (>${MAX_HTML_BYTES} bytes)`);
    }

    return { finalUrl: parsed.toString(), html: await readLimitedText(response) };
  } finally {
    clearTimeout(timer);
  }
}

async function assertPublicHostname(hostname: string): Promise<void> {
  const lower = hostname.toLowerCase();
  if (lower === "localhost" || lower.endsWith(".localhost")) {
    throw new ValidationError("localhost is not allowed");
  }
  if (isIP(lower)) {
    if (isPrivateAddress(lower)) throw new ValidationError("private IP is not allowed");
    return;
  }
  let addresses: Array<{ address: string; family: number }>;
  try {
    addresses = await lookup(lower, { all: true, verbatim: false });
  } catch {
    throw new ValidationError("hostname could not be resolved");
  }
  if (!addresses.length) throw new ValidationError("hostname has no address");
  if (addresses.some((entry) => isPrivateAddress(entry.address))) {
    throw new ValidationError("private network destination is not allowed");
  }
}

function isPrivateAddress(address: string): boolean {
  const mapped = address.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/i);
  if (mapped) return isPrivateAddress(mapped[1]);

  if (address.includes(":")) {
    const lower = address.toLowerCase();
    return lower === "::1" || lower === "::" || lower.startsWith("fc") || lower.startsWith("fd") || lower.startsWith("fe80:");
  }

  const parts = address.split(".").map((part) => Number(part));
  if (parts.length !== 4 || parts.some((part) => !Number.isInteger(part) || part < 0 || part > 255)) return true;
  const [a, b] = parts;
  return (
    a === 0 ||
    a === 10 ||
    a === 127 ||
    a >= 224 ||
    (a === 100 && b >= 64 && b <= 127) ||
    (a === 169 && b === 254) ||
    (a === 172 && b >= 16 && b <= 31) ||
    (a === 192 && b === 168) ||
    (a === 198 && (b === 18 || b === 19))
  );
}

async function readLimitedText(response: Response): Promise<string> {
  const body = response.body as any;
  if (!body?.getReader) {
    const text = await response.text();
    return text.slice(0, MAX_HTML_BYTES);
  }
  const reader = body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > MAX_HTML_BYTES) {
      await reader.cancel();
      throw new ValidationError(`homepage is too large (>${MAX_HTML_BYTES} bytes)`);
    }
    chunks.push(value);
  }
  return Buffer.concat(chunks).toString("utf-8");
}

function analyzeHtml(inputUrl: string, finalUrl: string, html: string): IntakeResult {
  const base = new URL(finalUrl);
  const metadata = extractMetadata(html, base);
  const jsonLd = extractJsonLd(html, base);
  const socialLinks = uniqueSocialLinks([...extractSocialLinks(html, base), ...jsonLd.socialLinks]);
  const emails = uniqueStrings([...extractMailto(html), ...jsonLd.emails]).slice(0, 5);
  const phones = uniqueStrings([...extractTel(html), ...jsonLd.phones]).slice(0, 5);
  const title = firstNonEmpty(metadata.ogTitle, metadata.twitterTitle, metadata.title, jsonLd.name);
  const description = firstNonEmpty(metadata.description, metadata.ogDescription, metadata.twitterDescription, jsonLd.description);
  const siteName = firstNonEmpty(metadata.siteName, jsonLd.name, deriveSiteName(title, base.hostname));
  const imageUrl = firstNonEmpty(metadata.ogImage, metadata.twitterImage, jsonLd.image, metadata.icon);
  const canonicalUrl = firstNonEmpty(metadata.canonical, finalUrl);
  const dashboardConfig = buildDashboardConfig(socialLinks, canonicalUrl);
  const safeTitle = siteName || title || base.hostname;
  const safeDescription = description || `${safeTitle} の公式サイトから取得した基本情報です。`;

  return {
    inputUrl,
    finalUrl,
    title,
    siteName,
    description,
    canonicalUrl,
    imageUrl,
    language: metadata.language,
    emails,
    phones,
    socialLinks,
    suggestions: {
      title: safeTitle,
      theme: [safeTitle, safeDescription, canonicalUrl].filter(Boolean).join("\n"),
      articleHtml: buildArticleHtml(safeTitle, safeDescription, canonicalUrl, socialLinks),
      imagePrompt: `${safeTitle} のホームページ内容をもとにした管理画面用のアイキャッチ。実在ロゴ、人物の顔、商品そのものを捏造せず、サービスの雰囲気が伝わる明るい写真風。`,
      dashboardConfig,
    },
  };
}

function extractMetadata(html: string, base: URL): Record<string, string> {
  const title = decodeHtml(firstMatch(html, /<title[^>]*>([\s\S]*?)<\/title>/i));
  const language = firstMatch(html, /<html[^>]*\blang=["']?([^"'\s>]+)/i).toLowerCase();
  const metas: Record<string, string> = {};
  const metaRe = /<meta\b([^>]*?)>/gi;
  for (const match of html.matchAll(metaRe)) {
    const attrs = attrsToObject(match[1]);
    const key = (attrs.name || attrs.property || attrs["http-equiv"] || "").toLowerCase();
    const content = decodeHtml(attrs.content || "");
    if (key && content && !metas[key]) metas[key] = content;
  }
  const links: Record<string, string> = {};
  const linkRe = /<link\b([^>]*?)>/gi;
  for (const match of html.matchAll(linkRe)) {
    const attrs = attrsToObject(match[1]);
    const rel = (attrs.rel || "").toLowerCase();
    const href = absoluteUrl(attrs.href || "", base);
    if (!rel || !href) continue;
    if (rel.includes("canonical") && !links.canonical) links.canonical = href;
    if ((rel.includes("icon") || rel.includes("apple-touch-icon")) && !links.icon) links.icon = href;
  }
  return {
    title: cleanText(title),
    language,
    description: cleanText(metas.description || ""),
    ogTitle: cleanText(metas["og:title"] || ""),
    ogDescription: cleanText(metas["og:description"] || ""),
    ogImage: absoluteUrl(metas["og:image"] || "", base),
    siteName: cleanText(metas["og:site_name"] || ""),
    twitterTitle: cleanText(metas["twitter:title"] || ""),
    twitterDescription: cleanText(metas["twitter:description"] || ""),
    twitterImage: absoluteUrl(metas["twitter:image"] || "", base),
    canonical: links.canonical || "",
    icon: links.icon || "",
  };
}

function extractJsonLd(html: string, base: URL): {
  name: string;
  description: string;
  image: string;
  emails: string[];
  phones: string[];
  socialLinks: SocialLink[];
} {
  const out = { name: "", description: "", image: "", emails: [] as string[], phones: [] as string[], socialLinks: [] as SocialLink[] };
  const scriptRe = /<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  for (const match of html.matchAll(scriptRe)) {
    try {
      walkJsonLd(JSON.parse(decodeHtml(match[1])), base, out);
    } catch {
      // Ignore invalid structured data. The homepage can still be useful.
    }
  }
  out.emails = uniqueStrings(out.emails);
  out.phones = uniqueStrings(out.phones);
  out.socialLinks = uniqueSocialLinks(out.socialLinks);
  return out;
}

function walkJsonLd(value: any, base: URL, out: ReturnType<typeof extractJsonLd>): void {
  if (!value) return;
  if (Array.isArray(value)) {
    value.forEach((item) => walkJsonLd(item, base, out));
    return;
  }
  if (typeof value !== "object") return;
  if (!out.name && typeof value.name === "string") out.name = cleanText(value.name);
  if (!out.description && typeof value.description === "string") out.description = cleanText(value.description);
  if (!out.image) out.image = jsonLdImageUrl(value.image, base);
  if (typeof value.email === "string") out.emails.push(cleanText(value.email).replace(/^mailto:/i, ""));
  if (typeof value.telephone === "string") out.phones.push(cleanText(value.telephone).replace(/^tel:/i, ""));
  const sameAs = Array.isArray(value.sameAs) ? value.sameAs : [value.sameAs].filter(Boolean);
  for (const rawUrl of sameAs) {
    if (typeof rawUrl !== "string") continue;
    const url = absoluteUrl(rawUrl, base);
    const platform = detectPlatform(url);
    if (platform) out.socialLinks.push({ platform, url, handle: extractHandle(platform, url) });
  }
  if (value["@graph"]) walkJsonLd(value["@graph"], base, out);
}

function jsonLdImageUrl(value: any, base: URL): string {
  if (typeof value === "string") return absoluteUrl(value, base);
  if (Array.isArray(value)) return firstNonEmpty(...value.map((item) => jsonLdImageUrl(item, base)));
  if (value && typeof value === "object") return absoluteUrl(value.url || value.contentUrl || "", base);
  return "";
}

function extractSocialLinks(html: string, base: URL): SocialLink[] {
  const out: SocialLink[] = [];
  const anchorRe = /<a\b([^>]*?)>/gi;
  for (const match of html.matchAll(anchorRe)) {
    const href = absoluteUrl(attrsToObject(match[1]).href || "", base);
    const platform = detectPlatform(href);
    if (platform) out.push({ platform, url: href, handle: extractHandle(platform, href) });
  }
  return out;
}

function extractMailto(html: string): string[] {
  const out: string[] = [];
  for (const match of html.matchAll(/href=["']mailto:([^"'?#]+)[^"']*["']/gi)) out.push(decodeURIComponentSafe(match[1]));
  for (const match of html.matchAll(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi)) out.push(match[0]);
  return uniqueStrings(out.map((email) => email.toLowerCase()));
}

function extractTel(html: string): string[] {
  const out: string[] = [];
  for (const match of html.matchAll(/href=["']tel:([^"']+)["']/gi)) out.push(decodeURIComponentSafe(match[1]));
  return uniqueStrings(out.map(cleanText));
}

function buildDashboardConfig(socialLinks: SocialLink[], canonicalUrl: string): IntakeResult["suggestions"]["dashboardConfig"] {
  const byPlatform = new Map(socialLinks.map((link) => [link.platform, link]));
  const accounts: Record<string, Record<string, string>> = {
    youtube: {},
    instagram: {},
    reels: {},
    threads: {},
    facebook: {},
    x: {},
    gsc: { siteUrl: canonicalUrl },
    ga4: {},
  };
  for (const [platform, link] of byPlatform.entries()) {
    const value = link.handle || link.url;
    if (platform === "youtube") accounts.youtube = { account: value, source: link.url };
    if (platform === "instagram") {
      accounts.instagram = { username: value, source: link.url };
      accounts.reels = { username: value, source: link.url };
    }
    if (platform === "threads") accounts.threads = { username: value, source: link.url };
    if (platform === "facebook") accounts.facebook = { pageId: value, source: link.url };
    if (platform === "x") accounts.x = { username: value, source: link.url };
  }
  return {
    channelInput: byPlatform.get("youtube")?.url || "",
    accounts,
  };
}

function buildArticleHtml(title: string, description: string, canonicalUrl: string, socialLinks: SocialLink[]): string {
  const lines = [
    `<h2>${escapeHtml(title)}</h2>`,
    `<p>${escapeHtml(description)}</p>`,
    `<p><a href="${escapeHtml(canonicalUrl)}" target="_blank" rel="noopener">公式ページを見る</a></p>`,
  ];
  const selected = socialLinks.slice(0, 6);
  if (selected.length) {
    lines.push("<h3>関連SNS</h3>");
    lines.push("<ul>");
    for (const link of selected) {
      lines.push(`<li><a href="${escapeHtml(link.url)}" target="_blank" rel="noopener">${escapeHtml(labelForPlatform(link.platform, link.handle))}</a></li>`);
    }
    lines.push("</ul>");
  }
  return lines.join("\n");
}

function detectPlatform(rawUrl: string): string {
  if (!rawUrl) return "";
  let host = "";
  try {
    host = new URL(rawUrl).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "";
  }
  if (host.includes("youtube.com") || host === "youtu.be") return "youtube";
  if (host.includes("instagram.com")) return "instagram";
  if (host.includes("threads.net")) return "threads";
  if (host.includes("facebook.com") || host === "fb.me") return "facebook";
  if (host === "x.com" || host.includes("twitter.com")) return "x";
  if (host.includes("tiktok.com")) return "tiktok";
  if (host.includes("note.com")) return "note";
  if (host.includes("line.me")) return "line";
  if (host.includes("linkedin.com")) return "linkedin";
  return "";
}

function extractHandle(platform: string, rawUrl: string): string {
  try {
    const url = new URL(rawUrl);
    const parts = url.pathname.split("/").filter(Boolean);
    if (!parts.length) return "";
    if (platform === "youtube" && (parts[0].startsWith("@") || parts[0] === "channel")) return parts.slice(0, 2).join("/");
    if (platform === "facebook" && parts[0] === "pages" && parts[1]) return parts[1];
    return parts[0].replace(/^@/, "");
  } catch {
    return "";
  }
}

function attrsToObject(source: string): Record<string, string> {
  const attrs: Record<string, string> = {};
  const attrRe = /([:\w-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s"'>]+))/g;
  for (const match of source.matchAll(attrRe)) {
    attrs[match[1].toLowerCase()] = decodeHtml(match[3] || match[4] || match[5] || "");
  }
  return attrs;
}

function absoluteUrl(value: string, base: URL): string {
  const trimmed = cleanText(value);
  if (!trimmed || /^(data|javascript):/i.test(trimmed)) return "";
  try {
    const url = new URL(trimmed, base);
    if (!["http:", "https:"].includes(url.protocol)) return "";
    url.hash = "";
    return url.toString();
  } catch {
    return "";
  }
}

function firstMatch(source: string, re: RegExp): string {
  return source.match(re)?.[1] || "";
}

function firstNonEmpty(...values: string[]): string {
  return values.find((value) => cleanText(value))?.trim() || "";
}

function deriveSiteName(title: string, hostname: string): string {
  const cleaned = cleanText(title);
  if (cleaned) return cleaned.split(/\s[|\-–—]\s|｜/)[0]?.trim() || cleaned;
  return hostname.replace(/^www\./, "");
}

function uniqueSocialLinks(links: SocialLink[]): SocialLink[] {
  const seen = new Set<string>();
  const out: SocialLink[] = [];
  for (const link of links) {
    if (!link.url || seen.has(link.url)) continue;
    seen.add(link.url);
    out.push(link);
  }
  return out.slice(0, 20);
}

function uniqueStrings(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of values) {
    const value = cleanText(raw);
    if (!value || seen.has(value)) continue;
    seen.add(value);
    out.push(value);
  }
  return out;
}

function cleanText(value: string): string {
  return decodeHtml(String(value || "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
}

function decodeHtml(value: string): string {
  return String(value || "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(Number.parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, num) => String.fromCodePoint(Number.parseInt(num, 10)));
}

function decodeURIComponentSafe(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function escapeHtml(value: string): string {
  return String(value || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  }[char] || char));
}

function labelForPlatform(platform: string, handle: string): string {
  const names: Record<string, string> = {
    youtube: "YouTube",
    instagram: "Instagram",
    threads: "Threads",
    facebook: "Facebook",
    x: "X",
    tiktok: "TikTok",
    note: "note",
    line: "LINE",
    linkedin: "LinkedIn",
  };
  return `${names[platform] || platform}${handle ? ` / ${handle}` : ""}`;
}
