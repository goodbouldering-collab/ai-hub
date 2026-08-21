import { lookup as dnsLookup } from 'node:dns/promises';
import { request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import { isIP } from 'node:net';
import iconv from 'iconv-lite';

const MAX_URL_LENGTH = 2_048;
const DEFAULT_TIMEOUT_MS = 10_000;
const DEFAULT_MAX_BYTES = 1_250_000;
const MAX_REDIRECTS = 4;
const DNS_TIMEOUT_MS = 3_000;
const DEFAULT_AUDIT_DEADLINE_MS = 24_000;

export class SeoLlmoAuditError extends Error {
  constructor(code, message, status = 422) {
    super(message);
    this.name = 'SeoLlmoAuditError';
    this.code = code;
    this.status = status;
  }
}

const blockedHostname = (hostname) => {
  const value = String(hostname || '').toLowerCase().replace(/\.$/, '');
  if (!value || value === 'localhost' || !value.includes('.')) return true;
  return ['.localhost', '.local', '.internal', '.home', '.lan', '.test', '.invalid'].some((suffix) => value.endsWith(suffix));
};

const remainingTime = (deadlineAt) => Math.max(0, Number(deadlineAt) - Date.now());

async function withDeadline(promise, deadlineAt, error) {
  const waitMs = remainingTime(deadlineAt);
  if (waitMs <= 0) throw error;
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => { timer = setTimeout(() => reject(error), waitMs); }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

export function isPublicIpAddress(address) {
  const version = isIP(String(address || ''));
  if (version === 4) {
    const parts = address.split('.').map(Number);
    if (parts.length !== 4 || parts.some((part) => !Number.isInteger(part) || part < 0 || part > 255)) return false;
    const [a, b, c] = parts;
    if (a === 0 || a === 10 || a === 127 || a >= 224) return false;
    if (a === 100 && b >= 64 && b <= 127) return false;
    if (a === 169 && b === 254) return false;
    if (a === 172 && b >= 16 && b <= 31) return false;
    if (a === 192 && b === 168) return false;
    if (a === 192 && b === 0 && c === 0) return false;
    if (a === 192 && b === 0 && c === 2) return false;
    if (a === 198 && (b === 18 || b === 19)) return false;
    if (a === 198 && b === 51 && c === 100) return false;
    if (a === 203 && b === 0 && c === 113) return false;
    return true;
  }
  if (version === 6) {
    const value = address.toLowerCase().split('%')[0];
    if (value === '::' || value === '::1') return false;
    if (value.startsWith('::ffff:')) {
      const mapped = value.slice(7);
      return isIP(mapped) === 4 && isPublicIpAddress(mapped);
    }
    if (value.startsWith('::')) return false;
    if (value.startsWith('fc') || value.startsWith('fd')) return false;
    if (/^fe[89a-f]/.test(value) || value.startsWith('ff')) return false;
    if (value.startsWith('2001:db8:') || value === '2001:db8::') return false;
    return true;
  }
  return false;
}

export function normalizeAuditUrl(input) {
  const raw = String(input || '').trim();
  if (!raw || raw.length > MAX_URL_LENGTH) {
    throw new SeoLlmoAuditError('invalid_url', '公開ページのURLを入力してください。', 400);
  }
  const candidate = /^[a-z][a-z\d+.-]*:\/\//i.test(raw) ? raw : `https://${raw}`;
  let url;
  try {
    url = new URL(candidate);
  } catch {
    throw new SeoLlmoAuditError('invalid_url', 'URLの形式を確認してください。', 400);
  }
  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new SeoLlmoAuditError('invalid_protocol', 'http または https の公開URLだけ診断できます。', 400);
  }
  if (url.username || url.password) {
    throw new SeoLlmoAuditError('credentials_not_allowed', '認証情報を含むURLは診断できません。', 400);
  }
  const defaultPort = url.protocol === 'https:' ? '443' : '80';
  if (url.port && url.port !== defaultPort) {
    throw new SeoLlmoAuditError('port_not_allowed', '標準ポートの公開URLだけ診断できます。', 400);
  }
  if (blockedHostname(url.hostname)) {
    throw new SeoLlmoAuditError('host_not_public', '公開インターネット上のURLだけ診断できます。', 400);
  }
  if (isIP(url.hostname) && !isPublicIpAddress(url.hostname)) {
    throw new SeoLlmoAuditError('ip_not_public', '公開インターネット上のURLだけ診断できます。', 400);
  }
  url.hash = '';
  return url;
}

async function resolvePublicAddresses(url, lookup = dnsLookup, deadlineAt = Date.now() + DNS_TIMEOUT_MS) {
  if (isIP(url.hostname)) return [{ address: url.hostname, family: isIP(url.hostname) }];
  let addresses;
  try {
    const dnsDeadline = Math.min(deadlineAt, Date.now() + DNS_TIMEOUT_MS);
    addresses = await withDeadline(
      Promise.resolve().then(() => lookup(url.hostname, { all: true, verbatim: true })),
      dnsDeadline,
      new SeoLlmoAuditError('request_timeout', 'URLの確認が時間内に終わりませんでした。'),
    );
  } catch (error) {
    if (error instanceof SeoLlmoAuditError) throw error;
    throw new SeoLlmoAuditError('dns_failed', 'URLの接続先を確認できませんでした。', 422);
  }
  if (!Array.isArray(addresses) || addresses.length === 0 || addresses.some(({ address }) => !isPublicIpAddress(address))) {
    throw new SeoLlmoAuditError('dns_not_public', '公開インターネット上の接続先だけ診断できます。', 400);
  }
  return addresses;
}

export async function assertPublicAuditTarget(input, lookup = dnsLookup, deadlineAt = Date.now() + DNS_TIMEOUT_MS) {
  const url = input instanceof URL ? normalizeAuditUrl(input.href) : normalizeAuditUrl(input);
  await resolvePublicAddresses(url, lookup, deadlineAt);
  return url;
}

export function createPinnedLookup(selected) {
  const result = { address: selected.address, family: selected.family };
  return function pinnedLookup(_hostname, lookupOptions, callback) {
    if (lookupOptions?.all) {
      callback(null, [result]);
      return;
    }
    callback(null, result.address, result.family);
  };
}

const normalizeEncoding = (value) => {
  const encoding = String(value || '').trim().toLowerCase().replace(/["']/g, '');
  if (['utf8', 'utf-8'].includes(encoding)) return 'utf-8';
  if (['shift_jis', 'shift-jis', 'sjis', 'x-sjis', 'windows-31j', 'cp932'].includes(encoding)) return 'shift_jis';
  if (['euc-jp', 'euc_jp', 'eucjp'].includes(encoding)) return 'euc-jp';
  if (['iso-2022-jp', 'jis'].includes(encoding)) return 'iso-2022-jp';
  return encoding;
};

export function decodeDocumentBuffer(buffer, contentType = '') {
  const source = Buffer.isBuffer(buffer) ? buffer : Buffer.from(buffer || '');
  if (source.length >= 3 && source[0] === 0xef && source[1] === 0xbb && source[2] === 0xbf) {
    return iconv.decode(source, 'utf-8');
  }
  if (source.length >= 2 && source[0] === 0xff && source[1] === 0xfe) return iconv.decode(source, 'utf-16le');
  if (source.length >= 2 && source[0] === 0xfe && source[1] === 0xff) return iconv.decode(source, 'utf-16be');

  const headerEncoding = String(contentType).match(/charset\s*=\s*["']?\s*([^\s;"']+)/i)?.[1] || '';
  const preview = source.subarray(0, 4_096).toString('latin1');
  const metaEncoding = preview.match(/<meta\b[^>]*\bcharset\s*=\s*["']?\s*([^\s"'/>;]+)/i)?.[1]
    || preview.match(/<meta\b[^>]*\bcontent\s*=\s*["'][^"']*charset\s*=\s*([^\s;"']+)/i)?.[1]
    || preview.match(/<\?xml\b[^>]*\bencoding\s*=\s*["']([^"']+)/i)?.[1]
    || '';
  const encoding = normalizeEncoding(headerEncoding || metaEncoding || 'utf-8');
  return iconv.decode(source, iconv.encodingExists(encoding) ? encoding : 'utf-8');
}

export async function requestPublicDocument(input, options = {}) {
  const lookup = options.lookup ?? dnsLookup;
  const timeoutMs = Math.min(Math.max(Number(options.timeoutMs) || DEFAULT_TIMEOUT_MS, 1_000), 15_000);
  const maxBytes = Math.min(Math.max(Number(options.maxBytes) || DEFAULT_MAX_BYTES, 16_384), 1_500_000);
  const deadlineAt = Number(options.deadlineAt) || Date.now() + timeoutMs;
  const startUrl = input instanceof URL ? normalizeAuditUrl(input.href) : normalizeAuditUrl(input);

  const requestOnce = async (url, redirectsLeft) => {
    const addresses = await resolvePublicAddresses(url, lookup, deadlineAt);
    const selected = addresses.find(({ family }) => Number(family) === 4) ?? addresses[0];
    const requestImpl = options.requestFactory ?? (url.protocol === 'https:' ? httpsRequest : httpRequest);
    const requestTime = Math.min(timeoutMs, remainingTime(deadlineAt));
    if (requestTime <= 0) throw new SeoLlmoAuditError('request_timeout', 'ページの応答が時間内に返りませんでした。');
    return new Promise((resolve, reject) => {
      let settled = false;
      let timer;
      const settle = (handler, value) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        handler(value);
      };
      const fail = (error) => settle(reject, error instanceof SeoLlmoAuditError
        ? error
        : new SeoLlmoAuditError('request_failed', 'ページを取得できませんでした。', 422));
      const request = requestImpl({
        protocol: url.protocol,
        hostname: url.hostname,
        port: url.port || undefined,
        path: `${url.pathname}${url.search}`,
        method: 'GET',
        servername: url.hostname,
        headers: {
          accept: options.accept || 'text/html,application/xhtml+xml;q=0.9,text/plain;q=0.7,application/xml;q=0.6,*/*;q=0.1',
          'accept-encoding': 'identity',
          'user-agent': 'AI-Sodan-SEO-LLMO-Audit/1.0 (+https://aiclimb.vercel.app/seo-llmo-diagnosis/)',
        },
        lookup: createPinnedLookup(selected),
      }, (response) => {
        const status = Number(response.statusCode) || 0;
        const location = response.headers.location;
        if (status >= 300 && status < 400 && location) {
          // The redirect target is all we need. Destroy the old response so an
          // endless 3xx body cannot keep its socket alive after this request.
          response.destroy();
          clearTimeout(timer);
          if (redirectsLeft <= 0) {
            fail(new SeoLlmoAuditError('too_many_redirects', 'リダイレクトが多すぎるため診断を停止しました。'));
            return;
          }
          let next;
          try {
            next = normalizeAuditUrl(new URL(location, url).href);
          } catch (error) {
            fail(error);
            return;
          }
          requestOnce(next, redirectsLeft - 1).then(
            (value) => settle(resolve, value),
            (error) => fail(error),
          );
          return;
        }

        const chunks = [];
        let size = 0;
        response.on('data', (chunk) => {
          size += chunk.length;
          if (size > maxBytes) {
            response.destroy(new SeoLlmoAuditError('response_too_large', 'ページ容量が大きすぎるため診断を停止しました。'));
            return;
          }
          chunks.push(chunk);
        });
        response.on('end', () => {
          const contentType = String(response.headers['content-type'] || '').toLowerCase();
          settle(resolve, {
            status,
            finalUrl: url.href,
            contentType,
            body: decodeDocumentBuffer(Buffer.concat(chunks), contentType),
          });
        });
        response.on('error', fail);
      });
      timer = setTimeout(() => request.destroy(new SeoLlmoAuditError('request_timeout', 'ページの応答が時間内に返りませんでした。')), requestTime);
      request.on('error', fail);
      request.end();
    });
  };

  return requestOnce(startUrl, MAX_REDIRECTS);
}

const decodeEntities = (value) => String(value || '')
  .replace(/&nbsp;/gi, ' ')
  .replace(/&amp;/gi, '&')
  .replace(/&quot;/gi, '"')
  .replace(/&#39;|&apos;/gi, "'")
  .replace(/&lt;/gi, '<')
  .replace(/&gt;/gi, '>')
  .replace(/&#(\d+);/g, (_match, code) => String.fromCodePoint(Number(code)))
  .replace(/&#x([\da-f]+);/gi, (_match, code) => String.fromCodePoint(Number.parseInt(code, 16)));

const cleanText = (value) => decodeEntities(String(value || '').replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim();

const attributes = (tag) => {
  const values = {};
  const source = String(tag || '').replace(/^<\/?[a-z\d:-]+/i, '').replace(/\/?\s*>$/, '');
  const pattern = /([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
  for (const match of source.matchAll(pattern)) values[match[1].toLowerCase()] = decodeEntities(match[2] ?? match[3] ?? match[4] ?? '');
  return values;
};

const collectStructuredDataTypes = (value, output = new Set()) => {
  if (Array.isArray(value)) {
    for (const item of value) collectStructuredDataTypes(item, output);
    return output;
  }
  if (!value || typeof value !== 'object') return output;
  const type = value['@type'];
  for (const item of Array.isArray(type) ? type : [type]) if (typeof item === 'string' && item.trim()) output.add(item.trim());
  for (const child of Object.values(value)) collectStructuredDataTypes(child, output);
  return output;
};

const alignmentScore = (left, right) => {
  const normalize = (value) => cleanText(value).toLowerCase().replace(/[\s\p{P}\p{S}]/gu, '');
  const first = normalize(left);
  const second = normalize(right);
  if (first.length < 2 || second.length < 2) return 0;
  const grams = (value) => new Set([...Array(Math.max(0, value.length - 1))].map((_, index) => value.slice(index, index + 2)));
  const a = grams(first);
  const b = grams(second);
  const overlap = [...a].filter((item) => b.has(item)).length;
  return overlap / Math.max(1, Math.min(a.size, b.size));
};

export function analyzeSeoLlmoDocument(html, pageUrl) {
  const source = String(html || '');
  const title = cleanText(source.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)?.[1] || '');
  const htmlTag = source.match(/<html\b[^>]*>/i)?.[0] || '';
  const meta = [...source.matchAll(/<meta\b[^>]*>/gi)].map((match) => attributes(match[0]));
  const links = [...source.matchAll(/<link\b[^>]*>/gi)].map((match) => attributes(match[0]));
  const anchors = [...source.matchAll(/<a\b[^>]*>/gi)].map((match) => attributes(match[0]));
  const images = [...source.matchAll(/<img\b[^>]*>/gi)].map((match) => attributes(match[0]));
  const h1s = [...source.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)].map((match) => cleanText(match[1])).filter(Boolean);
  const h2s = [...source.matchAll(/<h2\b[^>]*>([\s\S]*?)<\/h2>/gi)].map((match) => cleanText(match[1])).filter(Boolean);
  const description = meta.find((item) => item.name?.toLowerCase() === 'description')?.content?.trim() || '';
  const robotsMeta = meta.filter((item) => ['robots', 'googlebot'].includes(item.name?.toLowerCase())).map((item) => item.content || '').join(',').toLowerCase();
  const canonical = links.find((item) => String(item.rel || '').toLowerCase().split(/\s+/).includes('canonical'))?.href || '';
  const ogTitle = meta.find((item) => item.property?.toLowerCase() === 'og:title')?.content || '';
  const ogDescription = meta.find((item) => item.property?.toLowerCase() === 'og:description')?.content || '';
  const jsonLdBlocks = [...source.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];
  const structuredDataTypes = new Set();
  for (const block of jsonLdBlocks) {
    try { collectStructuredDataTypes(JSON.parse(block[1]), structuredDataTypes); } catch {}
  }
  const visibleText = cleanText(source
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<(script|style|noscript|svg|template)\b[\s\S]*?<\/\1>/gi, ' '));
  const bodyText = visibleText.toLowerCase();
  const hrefs = anchors.map((item) => String(item.href || '').trim());
  const contactLinkCount = hrefs.filter((href) => /^(?:mailto:|tel:)|(?:contact|inquiry|reserve|booking|line\.me)/i.test(href)).length;
  const hasCta = /(相談|予約|申し込|申込|問い合わせ|問合せ|資料請求|見積|購入|参加|contact|book|reserve|get started)/i.test(visibleText);
  const hasPricing = /(料金|価格|費用|プラン|月額|税込|円(?:\s|<|$)|price|pricing)/i.test(visibleText);
  const hasTrustSignals = /(運営者|会社概要|代表者|著者|監修|実績|事例|お客様の声|利用者の声|プライバシー|特定商取引|about|testimonial|case stud)/i.test(bodyText);
  const hasLocalInfo = /(〒\s*\d{3}|住所|所在地|営業時間|アクセス|滋賀|彦根|市|町|県|address|opening hours)/i.test(visibleText) && contactLinkCount > 0;
  const hasAnalytics = /(googletagmanager\.com|google-analytics\.com|\bgtag\s*\(|G-[A-Z0-9]{6,}|plausible\.io|clarity\.ms|matomo)/i.test(source);
  const imageAltCount = images.filter((image) => Object.hasOwn(image, 'alt')).length;
  const viewport = meta.find((item) => item.name?.toLowerCase() === 'viewport')?.content || '';
  const language = attributes(htmlTag).lang || '';

  return {
    pageUrl: String(pageUrl || ''),
    title,
    description,
    h1Count: h1s.length,
    h1: h1s[0] || '',
    h2Count: h2s.length,
    canonical,
    language,
    viewport,
    noindex: /(?:^|[,\s])noindex(?:[,\s]|$)/i.test(robotsMeta),
    structuredDataTypes: [...structuredDataTypes].sort(),
    jsonLdCount: jsonLdBlocks.length,
    visibleText,
    visibleTextLength: visibleText.length,
    imageCount: images.length,
    imageAltCount,
    imageAltRatio: images.length ? imageAltCount / images.length : 1,
    contactLinkCount,
    hasCta,
    hasPricing,
    hasTrustSignals,
    hasLocalInfo,
    hasAnalytics,
    hasOgp: Boolean(ogTitle && (ogDescription || description)),
    titleH1Alignment: alignmentScore(title, h1s[0] || ''),
  };
}

export function parseRobotsAccess(text, userAgent, pathname = '/') {
  const groups = [];
  let current = { agents: [], rules: [] };
  const flush = () => {
    if (current.agents.length) groups.push(current);
    current = { agents: [], rules: [] };
  };
  for (const rawLine of String(text || '').split(/\r?\n/)) {
    const line = rawLine.replace(/#.*$/, '').trim();
    if (!line) { flush(); continue; }
    const index = line.indexOf(':');
    if (index < 0) continue;
    const key = line.slice(0, index).trim().toLowerCase();
    const value = line.slice(index + 1).trim();
    if (key === 'user-agent') {
      if (current.rules.length) flush();
      current.agents.push(value.toLowerCase());
    } else if (['allow', 'disallow'].includes(key) && current.agents.length) {
      current.rules.push({ type: key, path: value });
    }
  }
  flush();
  const target = String(userAgent || '').toLowerCase();
  const exact = groups.filter((group) => group.agents.includes(target));
  const selected = exact.length ? exact : groups.filter((group) => group.agents.includes('*'));
  const rules = selected.flatMap((group) => group.rules)
    .filter((rule) => rule.path && pathname.startsWith(rule.path))
    .sort((left, right) => right.path.length - left.path.length || (left.type === 'allow' ? -1 : 1));
  return { allowed: rules[0]?.type !== 'disallow', explicit: exact.length > 0, matchedRule: rules[0] || null };
}

const categoryDefinitions = [
  { id: 'discoverability', name: '発見・クロール', maxScore: 30 },
  { id: 'clarity', name: '内容の明確さ', maxScore: 30 },
  { id: 'trust', name: '信頼・主体', maxScore: 25 },
  { id: 'action', name: '行動・計測', maxScore: 15 },
];

const check = (category, id, weight, passed, title, reason, action, evidence) => ({
  category, id, weight, passed: Boolean(passed), title, reason, action, evidence: String(evidence || ''),
});

const levelForScore = (score) => {
  if (score >= 85) return { id: 'strong', label: '伝わる土台が整っています' };
  if (score >= 65) return { id: 'steady', label: 'あと少し整えると強くなります' };
  if (score >= 45) return { id: 'developing', label: '重要な土台から改善できます' };
  return { id: 'starting', label: 'まず見つけてもらう入口を整えましょう' };
};

export function buildSeoLlmoReport({ page, robots, sitemap, context = {} }) {
  const pageOk = page.status >= 200 && page.status < 400;
  const robotsOk = robots.status >= 200 && robots.status < 300;
  const sitemapOk = sitemap.status >= 200 && sitemap.status < 300 && /<(?:urlset|sitemapindex)\b/i.test(sitemap.body || '');
  const oaiAccess = robotsOk ? parseRobotsAccess(robots.body, 'OAI-SearchBot') : { allowed: false, explicit: false, matchedRule: null };
  const types = new Set(page.structuredDataTypes || []);
  const hasEntity = [...types].some((type) => /^(?:Organization|LocalBusiness|Person|EducationalOrganization|NGO|WebSite)$/i.test(type));
  const localRequired = Boolean(context.isLocalBusiness);
  const contextText = [page.title, page.description, page.h1, page.visibleText].filter(Boolean).join(' ');
  const matchContext = (value) => {
    const expected = cleanText(value).slice(0, 240);
    if (!expected) return { passed: true, score: 1, evidence: '入力なし（採点対象外）' };
    const score = alignmentScore(expected, contextText);
    return {
      passed: score >= 0.2,
      score,
      evidence: `入力「${expected}」との一致度 ${Math.round(score * 100)}%`,
    };
  };
  const audienceMatch = matchContext(context.audience);
  const problemMatch = matchContext(context.problem);
  const actionMatch = matchContext(context.desiredAction);
  const checks = [
    check('discoverability', 'reachable', 6, pageOk, '公開ページへ到達できる状態にする', 'ページへ安定して到達できません。', 'URL、SSL、ホスティング、公開設定を確認する。', `HTTP ${page.status || 0}`),
    check('discoverability', 'indexable', 5, pageOk && !page.noindex, 'noindexを意図どおりにする', '検索対象ページにnoindexがある可能性があります。', '公開したいページからnoindexを外し、意図的な非公開ページだけに残す。', page.noindex ? 'noindexあり' : 'noindexなし'),
    check('discoverability', 'robots', 2, robotsOk, 'robots.txtを確認できるようにする', 'robots.txtを確認できません。', 'サイト直下のrobots.txtを公開し、必要なクローラを誤って遮断していないか確認する。', `HTTP ${robots.status || 0}`),
    check('discoverability', 'sitemap', 4, sitemapOk, 'XMLサイトマップを公開する', '有効なsitemap.xmlを確認できません。', '公開URLを列挙したXMLサイトマップを作り、robots.txtとSearch Consoleから案内する。', `HTTP ${sitemap.status || 0}`),
    check('discoverability', 'canonical', 3, Boolean(page.canonical), 'canonicalを設定する', '正規URLを示すcanonicalがありません。', '同じ内容のURLが複数ある場合も、代表URLを絶対URLで指定する。', page.canonical || '未検出'),
    check('discoverability', 'title', 4, Boolean(page.title), 'ページタイトルを具体化する', 'titleを確認できません。', '誰の何を解決するページかを、固有名と主要テーマを含む自然な一文で書く。', page.title || '未検出'),
    check('discoverability', 'h1', 3, page.h1Count === 1, '主題をH1で一つにする', page.h1Count ? 'H1が複数あります。' : 'H1がありません。', 'ページの主題を一つのH1で明示し、titleと同じ方向を向ける。', `H1 ${page.h1Count || 0}件`),
    check('discoverability', 'oai-searchbot', 3, robotsOk && oaiAccess.allowed, 'OpenAI検索クローラの扱いを確認する', 'OAI-SearchBotがrobots.txtで遮断されているか、robots.txtを確認できません。', 'ChatGPT検索へ出したい場合はOAI-SearchBotを不必要に遮断しない。GPTBotの学習設定とは分けて判断する。', oaiAccess.matchedRule ? `${oaiAccess.matchedRule.type}: ${oaiAccess.matchedRule.path}` : robotsOk ? '遮断ルールなし' : '未確認'),

    check('clarity', 'description', 3, page.description.length >= 50, '説明文で対象者と価値を伝える', 'meta descriptionがないか短すぎます。', '対象者、悩み、得られる変化を自然な説明文にまとめる。', page.description ? `${page.description.length}文字` : '未検出'),
    check('clarity', 'visible-text', 3, page.visibleTextLength >= 400, '本文で独自の答えを示す', '公開HTMLから読める本文が少ない状態です。', 'サービスの対象、進め方、実例、根拠、次の行動を、画像だけにせず本文で説明する。', `${page.visibleTextLength || 0}文字`),
    check('clarity', 'audience-match', 2, audienceMatch.passed, '届けたい対象者をページで明示する', '入力した対象者を公開ページから十分に確認できません。', 'title、説明文、H1、冒頭文のいずれかへ、届けたい相手を自然な言葉で明示する。', audienceMatch.evidence),
    check('clarity', 'problem-match', 2, problemMatch.passed, '相手の悩みを本文で言葉にする', '入力した相手の悩みを公開ページから十分に確認できません。', '相手が普段使う言葉で悩みを示し、その後に解決方法と得られる変化を続ける。', problemMatch.evidence),
    check('clarity', 'h2', 3, page.h2Count >= 1, '見出しで内容を整理する', '内容を分けるH2を確認できません。', '悩み、方法、実例、料金、FAQなどを意味のあるH2で整理する。', `H2 ${page.h2Count || 0}件`),
    check('clarity', 'language', 2, Boolean(page.language), 'ページ言語を明示する', 'html要素のlangを確認できません。', '日本語ページならhtml要素へ lang="ja" を設定する。', page.language || '未検出'),
    check('clarity', 'viewport', 3, /width\s*=\s*device-width/i.test(page.viewport || ''), 'スマートフォン表示を宣言する', 'viewport設定を確認できません。', 'width=device-widthを含むviewportを設定し、実機幅でも確認する。', page.viewport || '未検出'),
    check('clarity', 'image-alt', 3, page.imageAltRatio >= 0.8, '意味のある画像へ代替文を付ける', '代替文のない画像が多い状態です。', '内容を伝える画像へ用途が分かるaltを付け、装飾画像は空altにする。', `${page.imageAltCount || 0}/${page.imageCount || 0}件`),
    check('clarity', 'structured-data', 5, page.jsonLdCount > 0, '見える内容と一致する構造化データを付ける', 'JSON-LDを確認できません。', 'Organization、Person、LocalBusiness、Articleなど、画面に見える事実だけをJSON-LDで表す。', page.structuredDataTypes?.join(', ') || '未検出'),
    check('clarity', 'title-h1', 4, page.titleH1Alignment >= 0.2, 'titleとH1の主題をそろえる', 'titleとH1から同じ主題を十分に確認できません。', '検索結果の約束とページ冒頭の主題を同じ対象者・悩み・価値へそろえる。', `一致度 ${Math.round((page.titleH1Alignment || 0) * 100)}%`),

    check('trust', 'entity', 6, hasEntity, '運営主体を機械にも示す', '誰が提供するサイトかを示す主要なSchemaを確認できません。', '画面上の運営者情報と一致するOrganization、Person、LocalBusiness等を設定する。', page.structuredDataTypes?.join(', ') || '未検出'),
    check('trust', 'trust-signals', 5, page.hasTrustSignals, '運営者・実績・方針を公開する', '運営者、実績、事例、プライバシー等の信頼材料が弱い状態です。', '自慢ではなく、支援例、改善前後、責任者、問い合わせ先、方針を確認できる形にする。', page.hasTrustSignals ? '信頼語を検出' : '未検出'),
    check('trust', 'contact', 4, page.contactLinkCount > 0, '連絡先を辿れるリンクにする', '電話、メール、問い合わせ等の連絡リンクを確認できません。', '利用者が迷わず連絡できる電話、メール、フォーム、予約リンクを置く。', `${page.contactLinkCount || 0}件`),
    check('trust', 'local-context', 4, !localRequired || page.hasLocalInfo, '地域情報を具体化する', '地域事業として必要な所在地・対応地域・アクセス情報が不足しています。', '所在地、対応地域、営業時間、アクセス、地域での支援例を見える本文にする。', localRequired ? (page.hasLocalInfo ? '地域情報あり' : '地域情報なし') : '地域店舗向け項目は対象外'),
    check('trust', 'organization-schema', 3, types.has('Organization') || types.has('LocalBusiness') || types.has('EducationalOrganization') || types.has('NGO'), '組織情報を一貫させる', '組織を示す構造化データを確認できません。', '名称、URL、所在地、連絡先など、画面と一致する組織情報を設定する。', [...types].join(', ') || '未検出'),
    check('trust', 'person-schema', 3, types.has('Person'), '責任を持つ人を明示する', '著者・代表者を示すPerson情報を確認できません。', 'プロフィールや記事の著者を、画面上の説明と一致するPersonとして示す。', types.has('Person') ? 'Personあり' : '未検出'),

    check('action', 'cta', 2, page.hasCta, '主な次の行動を一つ示す', '相談、予約、申込などの明確な行動を確認できません。', 'ページの目的に合う主CTAを一つ決め、冒頭と説明後に分かりやすく置く。', page.hasCta ? '行動語あり' : '未検出'),
    check('action', 'action-match', 2, actionMatch.passed, '促したい行動とCTAをそろえる', '入力した「促したい行動」を公開ページから十分に確認できません。', '主CTAの文言とリンク先を、入力した行動へそろえ、冒頭と説明後に配置する。', actionMatch.evidence),
    check('action', 'contact-action', 3, page.contactLinkCount > 0, 'CTAを実際の連絡先へつなぐ', '行動文から連絡・予約へ進めない可能性があります。', 'ボタンを有効なフォーム、予約、電話、メールへつなぎ、リンク切れを確認する。', `${page.contactLinkCount || 0}件`),
    check('action', 'pricing', 2, page.hasPricing, '料金や利用条件を確認しやすくする', '料金・費用・プランの情報を確認できません。', '価格を公開できない場合も、見積条件や相談後の流れを説明する。', page.hasPricing ? '料金語あり' : '未検出'),
    check('action', 'analytics', 2, page.hasAnalytics, '改善を測れる状態にする', '一般的なアクセス解析タグを公開HTMLから確認できません。', '同意やプライバシーに配慮し、問い合わせ到達と主要ページを測れるようにする。', page.hasAnalytics ? '計測タグあり' : '未検出'),
    check('action', 'ogp', 2, page.hasOgp, '共有時の見え方を整える', 'OGPのタイトル・説明を確認できません。', 'SNSやメッセージ共有で内容が分かるOGPを設定する。', page.hasOgp ? 'OGPあり' : '未検出'),
    check('action', 'https', 2, String(page.finalUrl || page.pageUrl || '').startsWith('https://'), 'HTTPSで安全に公開する', '最終URLがHTTPSではありません。', 'HTTPSへ統一し、HTTPから正規URLへ転送する。', page.finalUrl || page.pageUrl || '未確認'),
  ];

  const categories = categoryDefinitions.map((definition) => {
    const categoryChecks = checks.filter((item) => item.category === definition.id);
    return {
      ...definition,
      score: categoryChecks.filter((item) => item.passed).reduce((sum, item) => sum + item.weight, 0),
      passed: categoryChecks.filter((item) => item.passed).length,
      total: categoryChecks.length,
    };
  });
  const score = categories.reduce((sum, category) => sum + category.score, 0);
  const priorities = checks.filter((item) => !item.passed)
    .sort((left, right) => right.weight - left.weight)
    .slice(0, 6)
    .map((item) => ({
      priority: item.weight >= 5 ? 'high' : item.weight >= 3 ? 'medium' : 'low',
      title: item.title,
      reason: item.reason,
      action: item.action,
      evidence: item.evidence,
      category: item.category,
    }));

  return {
    score,
    level: levelForScore(score),
    categories,
    priorities,
    checks,
    page: {
      status: page.status || 0,
      finalUrl: page.finalUrl || page.pageUrl || '',
      title: page.title || '',
      description: page.description || '',
      h1: page.h1 || '',
      visibleTextLength: page.visibleTextLength || 0,
      structuredDataTypes: page.structuredDataTypes || [],
    },
    crawler: {
      robotsStatus: robots.status || 0,
      oaiSearchBotAllowed: robotsOk ? oaiAccess.allowed : null,
      oaiSearchBotExplicit: robotsOk ? oaiAccess.explicit : null,
      note: 'OAI-SearchBotはChatGPT検索用、GPTBotは学習用です。別々に設定できます。',
    },
    context: {
      audience: String(context.audience || ''),
      problem: String(context.problem || ''),
      desiredAction: String(context.desiredAction || ''),
      isLocalBusiness: Boolean(context.isLocalBusiness),
    },
    limits: { rankingGuarantee: false, aiCitationGuarantee: false, liveBrowserRendering: false },
    disclaimer: 'この点数は公開HTMLから確認できる準備度です。検索順位やAI回答への掲載を保証しません。',
  };
}

const safeContext = (value = {}) => ({
  audience: String(value.audience || '').trim().slice(0, 160),
  problem: String(value.problem || '').trim().slice(0, 240),
  desiredAction: String(value.desiredAction || '').trim().slice(0, 160),
  isLocalBusiness: Boolean(value.isLocalBusiness),
});

export async function runSeoLlmoAudit(input, dependencies = {}) {
  const lookup = dependencies.lookup ?? dnsLookup;
  const requestDocument = dependencies.requestDocument ?? requestPublicDocument;
  const deadlineAt = Number(dependencies.deadlineAt) || Date.now() + DEFAULT_AUDIT_DEADLINE_MS;
  const target = await assertPublicAuditTarget(input?.url, lookup, deadlineAt);
  const pageResponse = await requestDocument(target, {
    lookup, deadlineAt, accept: 'text/html,application/xhtml+xml;q=0.9', maxBytes: DEFAULT_MAX_BYTES,
  });
  const finalUrl = await assertPublicAuditTarget(pageResponse.finalUrl || target.href, lookup, deadlineAt);
  if (pageResponse.contentType && !/(?:text\/html|application\/xhtml\+xml)/i.test(pageResponse.contentType)) {
    throw new SeoLlmoAuditError('not_html', 'HTMLの公開ページを指定してください。', 422);
  }
  const resource = async (pathname, accept) => {
    const url = new URL(pathname, finalUrl.origin);
    try {
      return await requestDocument(url, { lookup, deadlineAt, accept, maxBytes: 300_000, timeoutMs: 8_000 });
    } catch {
      return { status: 0, finalUrl: url.href, contentType: '', body: '' };
    }
  };
  const [robots, sitemap] = await Promise.all([
    resource('/robots.txt', 'text/plain,*/*;q=0.1'),
    resource('/sitemap.xml', 'application/xml,text/xml,text/plain,*/*;q=0.1'),
  ]);
  const page = analyzeSeoLlmoDocument(pageResponse.body, finalUrl.href);
  const report = buildSeoLlmoReport({
    page: { ...page, status: pageResponse.status, finalUrl: finalUrl.href },
    robots,
    sitemap,
    context: safeContext(input?.context),
  });
  return { ...report, targetUrl: target.href, auditedUrl: finalUrl.href, auditedAt: new Date().toISOString() };
}
