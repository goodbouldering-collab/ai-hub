// Only the unmetered Text Search Essentials (IDs Only) fields are permitted.
// Pricing/fields checked against Google documentation on 2026-10-28.
export const PLACES_FIELD_MASK = 'places.id,places.attributions,nextPageToken';
const ENDPOINT = 'https://places.googleapis.com/v1/places:searchText';
const text = (value, limit = 160) => String(value ?? '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, limit);
export class PlacesError extends Error {
  constructor(code, message, status = 400) { super(message); this.code = code; this.status = status; }
}
const types = {
  Restaurant: 'レストラン', CafeOrCoffeeShop: 'カフェ', BeautySalon: '美容室', HairSalon: '美容室',
  HealthClub: 'ジム', SportsActivityLocation: 'スポーツ施設', Dentist: '歯科', AutoRepair: '自動車修理',
  LodgingBusiness: '宿泊施設', Hotel: 'ホテル', RealEstateAgent: '不動産', Store: '店舗',
};

export function extractLocalProfile(html, page = {}) {
  const nodes = [];
  const walk = (value, depth = 0) => {
    if (!value || typeof value !== 'object' || depth > 12 || nodes.length > 500) return;
    if (Array.isArray(value)) return value.forEach(item => walk(item, depth + 1));
    if (value.name && value.address) nodes.push(value);
    for (const item of Object.values(value)) if (typeof item === 'object') walk(item, depth + 1);
  };
  for (const block of String(html).matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)) {
    try { walk(JSON.parse(block[1])); } catch {}
  }
  // Keep multiple locations visible; never silently merge branches.
  const profiles = nodes.slice(0, 8).map(node => {
    const address = node.address;
    const area = typeof address === 'string' ? address : [address.addressRegion, address.addressLocality].filter(Boolean).join('');
    const nodeTypes = [].concat(node['@type'] || []);
    return { storeName: text(node.name), area: text(area, 100), keyword: types[nodeTypes.find(t => types[t])] || '', source: '構造化データ' };
  });
  const meta = String(html).match(/<meta\b[^>]*(?:property|name)=["']og:site_name["'][^>]*content=["']([^"']+)/i)?.[1];
  const content = [page.title, page.description, page.h1, page.visibleText].filter(Boolean).join(' ');
  const fallback = {
    storeName: text(meta || page.h1 || page.title).split(/[|｜]/)[0].trim(),
    area: text(content.match(/(?:東京都|北海道|(?:京都|大阪)府|[^\s、。<>]{2,3}県)[^\s、。<>]{1,12}?[市区町村]/)?.[0] || '', 100),
    keyword: ['ボルダリング', 'クライミング', '美容室', '整体', 'エステ', 'カフェ', '歯科', 'ジム', '工務店', 'レストラン', 'ホテル'].find(word => content.includes(word)) || '',
    source: 'ページの見出し・本文から推定',
  };
  const generic = ['スポーツ施設', '店舗', '宿泊施設'];
  const keyword = generic.includes(profiles[0]?.keyword) ? fallback.keyword || profiles[0].keyword : profiles[0]?.keyword || fallback.keyword;
  return { ...fallback, ...(profiles[0] || {}), keyword, alternatives: profiles, requiresConfirmation: true };
}

export function mapsUrl(query, placeId = '') {
  const url = new URL('https://www.google.com/maps/search/');
  url.searchParams.set('api', '1'); url.searchParams.set('query', query);
  if (placeId) url.searchParams.set('query_place_id', placeId);
  return url.href;
}

export async function runPlacesSearch(input, { apiKey, fetchImpl = fetch, now = () => new Date().toISOString() } = {}) {
  if (!apiKey) throw new PlacesError('places_not_configured', '店舗検索は準備中です。運営者によるGoogle Places APIの接続が必要です。', 503);
  const action = input?.action;
  if (!['candidates', 'rank'].includes(action)) throw new PlacesError('invalid_action', '店舗検索からやり直してください。');
  const storeName = text(input.storeName); const area = text(input.area, 100); const keyword = text(input.keyword, 100);
  if (!storeName || !area) throw new PlacesError('missing_location', '店舗名と市区町村を入力してください。');
  const placeId = text(input.placeId, 200);
  if (action === 'rank' && (!/^[A-Za-z0-9_-]{10,200}$/.test(placeId) || input.confirmed !== true)) throw new PlacesError('confirm_store', 'Google Mapsで対象店舗を確認し、候補を選んでください。');
  if (action === 'rank' && (!keyword || keyword === storeName || keyword.includes(storeName))) throw new PlacesError('invalid_keyword', '店舗名ではなく、探されたい業種を入力してください（例：カフェ）。');
  const query = action === 'candidates' ? `${area} ${storeName}` : `${area} ${keyword}`;
  const found = []; const attributions = []; const tokens = new Set();
  let pageToken; let hasMore = false;
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 18_000);
  try {
    for (let page = 0; page < (action === 'rank' ? 3 : 1); page++) {
      const response = await fetchImpl(ENDPOINT, {
        method: 'POST', redirect: 'error', signal: controller.signal,
        headers: { 'Content-Type': 'application/json', 'X-Goog-Api-Key': apiKey, 'X-Goog-FieldMask': PLACES_FIELD_MASK },
        body: JSON.stringify({ textQuery: query, languageCode: 'ja', regionCode: 'JP', rankPreference: 'RELEVANCE', pageSize: action === 'rank' ? 20 : 5, ...(pageToken ? {pageToken} : {}) }),
      });
      // Do not expose provider error bodies (which may contain credentials).
      if (!response.ok) throw new PlacesError(response.status === 429 ? 'places_quota' : 'places_unavailable', response.status === 429 ? 'Googleの利用上限に達しました。時間をおいて再度お試しください。' : 'Googleの店舗検索に接続できません。運営者がAPI設定を確認する必要があります。', response.status === 429 ? 429 : 502);
      const data = await response.json();
      if (!data || (data.places !== undefined && !Array.isArray(data.places))) throw new Error('invalid_response');
      for (const place of data.places || []) {
        if (!/^[A-Za-z0-9_-]{10,200}$/.test(place.id || '')) throw new Error('invalid_place');
        found.push(place.id);
        for (const entry of place.attributions || []) {
          if (entry.provider && /^https:\/\//.test(entry.providerUri || '')) attributions.push({ provider: text(entry.provider), uri: entry.providerUri });
        }
      }
      hasMore = Boolean(data.nextPageToken);
      if (!hasMore || (action === 'rank' && found.includes(placeId))) break;
      if (tokens.has(data.nextPageToken)) throw new Error('repeated_page');
      tokens.add(data.nextPageToken); pageToken = data.nextPageToken;
    }
  } catch (error) {
    if (error instanceof PlacesError) throw error;
    throw new PlacesError('places_failed', '店舗検索を完了できませんでした。時間をおいて再度お試しください。', 502);
  } finally { clearTimeout(timer); }
  const common = { query, checkedAt: now(), attributions, provider: 'Google Maps', billingMode: 'ids-only', hasMore, examined: found.length };
  if (action === 'candidates') return { ...common, candidates: [...new Set(found)].map(id => ({ id, mapsUrl: mapsUrl(query, id) })) };
  const index = found.indexOf(placeId);
  return { ...common, rank: index < 0 ? null : index + 1, placeId, mapsUrl: mapsUrl(`${area} ${storeName}`, placeId), searchUrl: mapsUrl(query),
    disclaimer: 'Places APIが返した関連度順の参考値です。Google検索・Googleマップの実際のMEO順位とは異なり、検索位置や利用者によって変わります。地域名を検索語に指定し、現在地は取得していません。' };
}
