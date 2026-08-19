import test from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { PassThrough } from 'node:stream';
import iconv from 'iconv-lite';

import {
  analyzeSeoLlmoDocument,
  assertPublicAuditTarget,
  buildSeoLlmoReport,
  createPinnedLookup,
  decodeDocumentBuffer,
  isPublicIpAddress,
  normalizeAuditUrl,
  parseRobotsAccess,
  requestPublicDocument,
  runSeoLlmoAudit,
} from '../api/_lib/seo-llmo-audit.mjs';

const RICH_HTML = `<!doctype html>
<html lang="ja">
<head>
  <title>彦根のAI業務改善相談｜山田商店</title>
  <meta name="description" content="彦根の小さな事業者向けに、AIを使った業務改善と集客支援を行います。初回相談から実装まで伴走します。">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta property="og:title" content="彦根のAI業務改善相談">
  <link rel="canonical" href="https://example.com/">
  <script type="application/ld+json">{
    "@context":"https://schema.org",
    "@graph":[
      {"@type":"Organization","name":"山田商店","url":"https://example.com/"},
      {"@type":"LocalBusiness","name":"山田商店","address":"滋賀県彦根市","telephone":"0749-00-0000"},
      {"@type":"Person","name":"山田太郎","jobTitle":"代表"}
    ]
  }</script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}</script>
</head>
<body>
  <header><a href="/">山田商店</a><a href="/about">運営者情報</a></header>
  <main>
    <h1>彦根の事業者のためのAI業務改善相談</h1>
    <h2>事務作業が重い、時間がない、告知が苦手という悩みを整理します</h2>
    <p>${'現場の仕事を確認し、無理なく続けられる手順へ整えます。'.repeat(30)}</p>
    <p>滋賀県彦根市で、導入事例とお客様の声を公開しています。代表者と支援実績も確認できます。</p>
    <a href="/contact">無料相談を予約する</a>
    <a href="tel:0749000000">電話で問い合わせる</a>
    <a href="mailto:info@example.com">メールで相談する</a>
    <a href="/price">料金を見る</a>
    <img src="team.webp" alt="彦根で相談を受ける代表者">
  </main>
  <footer><a href="/privacy">プライバシーポリシー</a><address>〒522-0000 滋賀県彦根市</address></footer>
</body>
</html>`;

test('public URLs are normalized while local, credentialed, and non-standard targets are rejected', () => {
  assert.equal(normalizeAuditUrl('example.com/path').href, 'https://example.com/path');
  assert.equal(normalizeAuditUrl('https://EXAMPLE.com').href, 'https://example.com/');

  for (const value of [
    'http://127.0.0.1/',
    'http://localhost/',
    'https://service.internal/',
    'https://user:pass@example.com/',
    'https://example.com:8443/',
    'file:///etc/passwd',
  ]) {
    assert.throws(() => normalizeAuditUrl(value), /公開|URL|ポート|認証/);
  }
});

test('private, loopback, link-local, and documentation addresses are never public targets', () => {
  for (const address of ['127.0.0.1', '10.0.0.2', '169.254.1.1', '172.20.0.1', '192.168.1.2', '192.0.2.10', '::1', '::127.0.0.1', 'fc00::1', 'fe80::1', 'fec0::1']) {
    assert.equal(isPublicIpAddress(address), false, address);
  }
  assert.equal(isPublicIpAddress('93.184.216.34'), true);
  assert.equal(isPublicIpAddress('2606:2800:220:1:248:1893:25c8:1946'), true);
});

test('pinned DNS lookup follows both Node single-address and all-address callback contracts', () => {
  const lookup = createPinnedLookup({ address: '93.184.216.34', family: 4 });
  let singleArgs;
  let allArgs;
  lookup('example.com', { all: false }, (...args) => { singleArgs = args; });
  lookup('example.com', { all: true }, (...args) => { allArgs = args; });

  assert.deepEqual(singleArgs, [null, '93.184.216.34', 4]);
  assert.deepEqual(allArgs, [null, [{ address: '93.184.216.34', family: 4 }]]);
});

test('Japanese HTML is decoded from declared EUC-JP and Shift_JIS encodings', () => {
  const eucHtml = '<html><head><title>彦根の相談</title></head><body>業務改善</body></html>';
  assert.equal(
    decodeDocumentBuffer(iconv.encode(eucHtml, 'euc-jp'), 'text/html; charset=EUC-JP'),
    eucHtml,
  );

  const shiftJisHtml = '<html><head><meta charset="Shift_JIS"><title>地域支援</title></head><body>相談予約</body></html>';
  assert.equal(decodeDocumentBuffer(iconv.encode(shiftJisHtml, 'shift_jis')), shiftJisHtml);
});

test('DNS resolution and streaming responses obey one absolute audit deadline', async () => {
  const delayedLookup = async () => {
    await new Promise((resolve) => setTimeout(resolve, 80));
    return [{ address: '93.184.216.34', family: 4 }];
  };
  await assert.rejects(
    assertPublicAuditTarget('https://example.com/', delayedLookup, Date.now() + 20),
    /時間|timeout/i,
  );

  const requestFactory = (_options, onResponse) => {
    const request = new EventEmitter();
    let interval;
    let finish;
    request.end = () => {
      const response = new PassThrough();
      response.statusCode = 200;
      response.headers = { 'content-type': 'text/html; charset=utf-8' };
      onResponse(response);
      interval = setInterval(() => response.write('x'), 5);
      finish = setTimeout(() => { clearInterval(interval); response.end(); }, 120);
    };
    request.destroy = (error) => {
      clearInterval(interval);
      clearTimeout(finish);
      queueMicrotask(() => request.emit('error', error));
    };
    return request;
  };
  await assert.rejects(
    requestPublicDocument('https://slow.example/', {
      lookup: async () => [{ address: '93.184.216.34', family: 4 }],
      requestFactory,
      timeoutMs: 1_000,
      deadlineAt: Date.now() + 35,
    }),
    /時間|timeout/i,
  );
});

test('a redirect is rejected before transport when its DNS resolves to a private address', async () => {
  let transportCalls = 0;
  const requestFactory = (_options, onResponse) => {
    transportCalls += 1;
    const request = new EventEmitter();
    request.end = () => {
      const response = new PassThrough();
      response.statusCode = 302;
      response.headers = { location: 'https://private.example/' };
      onResponse(response);
      response.end();
    };
    request.destroy = (error) => queueMicrotask(() => request.emit('error', error));
    return request;
  };
  const lookup = async (hostname) => hostname === 'private.example'
    ? [{ address: '127.0.0.1', family: 4 }]
    : [{ address: '93.184.216.34', family: 4 }];

  await assert.rejects(
    requestPublicDocument('https://example.com/', { lookup, requestFactory, deadlineAt: Date.now() + 500 }),
    /公開インターネット/,
  );
  assert.equal(transportCalls, 1);
});

test('a response larger than the configured bound is rejected without returning its body', async () => {
  const requestFactory = (_options, onResponse) => {
    const request = new EventEmitter();
    request.end = () => {
      const response = new PassThrough();
      response.statusCode = 200;
      response.headers = { 'content-type': 'text/html; charset=utf-8' };
      onResponse(response);
      response.end(Buffer.alloc(20_000, 0x61));
    };
    request.destroy = (error) => queueMicrotask(() => request.emit('error', error));
    return request;
  };

  await assert.rejects(
    requestPublicDocument('https://large.example/', {
      lookup: async () => [{ address: '93.184.216.34', family: 4 }],
      requestFactory,
      maxBytes: 16_384,
      deadlineAt: Date.now() + 500,
    }),
    /容量|large/i,
  );
});

test('OAI-SearchBot access is evaluated independently from GPTBot training access', () => {
  const splitPolicy = parseRobotsAccess(`
User-agent: GPTBot
Disallow: /

User-agent: OAI-SearchBot
Disallow:
`, 'OAI-SearchBot');
  assert.equal(splitPolicy.allowed, true);
  assert.equal(splitPolicy.explicit, true);

  const globalBlock = parseRobotsAccess('User-agent: *\nDisallow: /\n', 'OAI-SearchBot');
  assert.equal(globalBlock.allowed, false);
  assert.equal(globalBlock.explicit, false);
});

test('a well-formed local business page earns a complete evidence-backed readiness report', () => {
  const page = analyzeSeoLlmoDocument(RICH_HTML, 'https://example.com/');
  assert.equal(page.title, '彦根のAI業務改善相談｜山田商店');
  assert.equal(page.h1Count, 1);
  assert.deepEqual(page.structuredDataTypes.sort(), ['LocalBusiness', 'Organization', 'Person']);

  const report = buildSeoLlmoReport({
    page: { status: 200, finalUrl: 'https://example.com/', ...page },
    robots: { status: 200, body: 'User-agent: OAI-SearchBot\nDisallow:\nUser-agent: *\nAllow: /\n' },
    sitemap: { status: 200, body: '<?xml version="1.0"?><urlset><url><loc>https://example.com/</loc></url></urlset>' },
    context: { audience: '彦根の小規模事業者', problem: '事務作業が重い', desiredAction: '相談予約', isLocalBusiness: true },
  });

  assert.equal(report.score, 100, report.checks.filter(({ passed }) => !passed).map(({ id }) => id).join(', '));
  assert.equal(report.categories.length, 4);
  assert.equal(report.categories.reduce((sum, category) => sum + category.score, 0), 100);
  assert.equal(report.priorities.length, 0);
  assert.equal(report.limits.rankingGuarantee, false);
});

test('optional audience, problem, and action inputs affect the matching readiness checks', () => {
  const page = analyzeSeoLlmoDocument(RICH_HTML, 'https://example.com/');
  const base = {
    page: { status: 200, finalUrl: 'https://example.com/', ...page },
    robots: { status: 200, body: 'User-agent: *\nAllow: /\n' },
    sitemap: { status: 200, body: '<urlset><url><loc>https://example.com/</loc></url></urlset>' },
  };
  const aligned = buildSeoLlmoReport({
    ...base,
    context: { audience: '彦根の小規模事業者', problem: '事務作業が重い', desiredAction: '相談予約' },
  });
  const unrelated = buildSeoLlmoReport({
    ...base,
    context: { audience: '東京の獣医師', problem: '宇宙旅行の予約', desiredAction: '採用応募' },
  });

  assert.ok(unrelated.score < aligned.score, `${unrelated.score} should be below ${aligned.score}`);
  assert.deepEqual(
    unrelated.checks.filter(({ id }) => ['audience-match', 'problem-match', 'action-match'].includes(id)).map(({ passed }) => passed),
    [false, false, false],
  );
  assert.match(unrelated.priorities.map(({ title }) => title).join('\n'), /対象者|悩み|行動/);
});

test('an empty alt is valid for decorative images while a missing alt is not', () => {
  const decorative = analyzeSeoLlmoDocument('<html><body><img src="line.svg" alt=""></body></html>', 'https://example.com/');
  const missing = analyzeSeoLlmoDocument('<html><body><img src="photo.jpg"></body></html>', 'https://example.com/');
  assert.equal(decorative.imageAltRatio, 1);
  assert.equal(missing.imageAltRatio, 0);
});

test('a sparse page returns concrete high-impact fixes instead of a ranking promise', () => {
  const page = analyzeSeoLlmoDocument('<html><body><p>hello</p><img src="x.png"></body></html>', 'https://example.com/');
  const report = buildSeoLlmoReport({
    page: { status: 200, finalUrl: 'https://example.com/', ...page },
    robots: { status: 404, body: '' },
    sitemap: { status: 404, body: '' },
    context: { audience: '', problem: '', desiredAction: '', isLocalBusiness: false },
  });

  assert.ok(report.score < 40, report.score);
  assert.ok(report.priorities.length >= 3);
  const priorityTitles = report.priorities.map(({ title }) => title).join('\n');
  assert.match(priorityTitles, /タイトル|H1|サイトマップ|canonical|説明文/);
  assert.equal(report.limits.rankingGuarantee, false);
  assert.match(report.disclaimer, /順位|掲載/);
});

test('the live audit validates the target before any network request and scans the three public resources', async () => {
  let calls = [];
  let resourcesInFlight = 0;
  let maximumResourcesInFlight = 0;
  const requestDocument = async (url) => {
    calls.push(url.href);
    if (['/robots.txt', '/sitemap.xml'].includes(url.pathname)) {
      resourcesInFlight += 1;
      maximumResourcesInFlight = Math.max(maximumResourcesInFlight, resourcesInFlight);
      await new Promise((resolve) => setTimeout(resolve, 15));
      resourcesInFlight -= 1;
    }
    if (url.pathname === '/robots.txt') return { status: 200, finalUrl: url.href, contentType: 'text/plain', body: 'User-agent: *\nAllow: /' };
    if (url.pathname === '/sitemap.xml') return { status: 200, finalUrl: url.href, contentType: 'application/xml', body: '<urlset></urlset>' };
    return { status: 200, finalUrl: url.href, contentType: 'text/html', body: RICH_HTML };
  };
  const lookup = async () => [{ address: '93.184.216.34', family: 4 }];

  const report = await runSeoLlmoAudit({ url: 'example.com', context: { isLocalBusiness: true } }, { requestDocument, lookup });
  assert.equal(report.targetUrl, 'https://example.com/');
  assert.deepEqual(calls, ['https://example.com/', 'https://example.com/robots.txt', 'https://example.com/sitemap.xml']);
  assert.equal(maximumResourcesInFlight, 2);

  calls = [];
  await assert.rejects(
    runSeoLlmoAudit({ url: 'http://127.0.0.1/' }, { requestDocument, lookup }),
    /公開|URL/,
  );
  assert.equal(calls.length, 0);
});
