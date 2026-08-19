const ALLOWED_RELAY_REQUESTS = [
  { method: 'POST', pattern: /^\/v1\/runs$/ },
  { method: 'GET', pattern: /^\/v1\/runs\/[A-Za-z0-9_-]+$/ },
  { method: 'POST', pattern: /^\/v1\/runs\/[A-Za-z0-9_-]+\/(?:interrupt|adjust)$/ },
  { method: 'POST', pattern: /^\/v1\/runs\/[A-Za-z0-9_-]+\/approvals\/[^/]+$/ },
  { method: 'POST', pattern: /^\/v1\/seo-diagnoses$/ },
  { method: 'GET', pattern: /^\/v1\/seo-diagnoses\/[A-Za-z0-9_-]+$/ },
];

export function isAllowedRelayRequest(method, path) {
  const normalizedMethod = String(method || '').toUpperCase();
  const normalizedPath = String(path || '');
  return ALLOWED_RELAY_REQUESTS.some((entry) => entry.method === normalizedMethod && entry.pattern.test(normalizedPath));
}
