export const TABLES = Object.freeze({
  'command_center.projects': 'business_id', 'command_center.tasks': 'id',
  'command_center.directives': 'id', 'command_center.directive_executions': 'id',
  'command_center.trades': 'id', 'command_center.trade_plans': 'id',
  'command_center.relay_state': 'id', 'command_center.relay_requests': 'id',
  'command_center.relay_nonces': 'nonce', 'ai_watch.articles': 'hash', 'portal.sns_posts': 'id',
});
export class Conflict extends Error {}
const hasAuxiliaryTable = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
const now = () => new Date().toISOString();
export function identity(namespace, row) {
  if (!hasAuxiliaryTable(TABLES, namespace) || !row || typeof row !== 'object' || Array.isArray(row)) throw Error('Invalid auxiliary record');
  const key = String(row[TABLES[namespace]] ?? '');
  const owner = namespace.startsWith('command_center.') && !namespace.includes('.relay_') ? row.owner_id : '';
  if (!key || key.length > 256 || typeof owner !== 'string' || owner.length > 120 || (namespace.startsWith('command_center.') && !namespace.includes('.relay_') && !owner)) throw Error('Invalid auxiliary identity');
  const payload = JSON.stringify(row);
  if (new TextEncoder().encode(payload).length > 96 * 1024) throw Error('Auxiliary record too large');
  return { key, owner, payload };
}
export function auxiliaryStore(db) {
  if (!db?.prepare || !db?.batch) throw Error('Auxiliary D1 is not configured');
  const statement = (sql, ...args) => db.prepare(sql).bind(...args);
  const check = result => { if (result?.success === false) throw Error('Auxiliary D1 operation failed'); return result; };
  return {
    async raw(namespace) {
      if (!hasAuxiliaryTable(TABLES, namespace)) throw Error('Invalid auxiliary table');
      return (check(await statement('SELECT payload, revision FROM auxiliary_records WHERE namespace = ? ORDER BY record_key', namespace).all()).results || []).map(item => ({row: JSON.parse(item.payload), revision: item.revision}));
    },
    async list(namespace, owner) {
      if (!hasAuxiliaryTable(TABLES, namespace)) throw Error('Invalid auxiliary table');
      return (check(await statement('SELECT payload, revision FROM auxiliary_records WHERE namespace = ? AND owner_id = ? ORDER BY record_key', namespace, owner).all()).results || []).map(item => ({row: JSON.parse(item.payload), revision: item.revision}));
    },
    async get(namespace, key, owner) {
      if (!hasAuxiliaryTable(TABLES, namespace)) throw Error('Invalid auxiliary table');
      const item = await statement('SELECT payload, revision FROM auxiliary_records WHERE namespace = ? AND record_key = ? AND owner_id = ?', namespace, key, owner).first();
      return item ? { row: JSON.parse(item.payload), revision: item.revision } : null;
    },
    async insert(namespace, row) {
      const {key, owner, payload} = identity(namespace, row);
      const result = check(await statement('INSERT OR IGNORE INTO auxiliary_records(namespace, record_key, owner_id, payload) VALUES (?, ?, ?, ?)', namespace, key, owner, payload).run());
      if (result.meta?.changes !== 1) throw new Conflict('Record already exists');
    },
    async update(namespace, key, owner, change) {
      const old = await this.get(namespace, key, owner);
      if (!old) throw new Conflict('Record not found');
      const row = change(old.row);
      const next = identity(namespace, row);
      if (next.key !== key || next.owner !== owner) throw Error('Identity cannot change');
      const result = check(await statement('UPDATE auxiliary_records SET payload = ?, revision = revision + 1 WHERE namespace = ? AND record_key = ? AND owner_id = ? AND revision = ?', next.payload, namespace, key, owner, old.revision).run());
      if (result.meta?.changes !== 1) throw new Conflict('Record changed; reload and retry');
    },
    async removeClosedTrade(key, owner) {
      const result = check(await statement("DELETE FROM auxiliary_records WHERE namespace = 'command_center.trades' AND record_key = ? AND owner_id = ? AND json_extract(payload, '$.status') = 'closed'", key, owner).run());
      if (result.meta?.changes !== 1) throw new Conflict('Closed trade not found');
    },
    async executeTrade(input, owner) {
      const plan = await this.get('command_center.trade_plans', input.id, owner);
      if (!plan || plan.row.status !== 'approved') throw new Conflict('Approved plan not found');
      const tradeId = crypto.randomUUID(), timestamp = now();
      const row = {id: tradeId, owner_id: owner, traded_at: input.tradedAt, market: plan.row.market, symbol: plan.row.symbol, direction: plan.row.direction, status: 'open', entry_price: input.entryPrice, quantity: input.quantity, risk_amount: input.riskAmount, pnl: 0, memo: '相場羅針盤の承認済みプランから作成', created_at: timestamp, updated_at: timestamp};
      // D1 batch is one transaction. Both statements match the same revision;
      // the second concurrent execution cannot create an orphan or duplicate trade.
      const results = await db.batch([
        statement("INSERT INTO auxiliary_records(namespace, record_key, owner_id, payload) SELECT 'command_center.trades', ?, ?, ? FROM auxiliary_records WHERE namespace = 'command_center.trade_plans' AND record_key = ? AND owner_id = ? AND revision = ? AND json_extract(payload, '$.status') = 'approved'", tradeId, owner, JSON.stringify(row), input.id, owner, plan.revision),
        statement("UPDATE auxiliary_records SET payload = json_set(payload, '$.status', 'executed', '$.trade_id', ?, '$.updated_at', ?), revision = revision + 1 WHERE namespace = 'command_center.trade_plans' AND record_key = ? AND owner_id = ? AND revision = ? AND json_extract(payload, '$.status') = 'approved'", tradeId, timestamp, input.id, owner, plan.revision),
      ]);
      results.forEach(check);
      if (results.some(result => result.meta?.changes !== 1)) throw new Conflict('Plan changed; reload and retry');
    },
    async upsertArticles(articles) {
      const newHashes = [], existingHashes = [], timestamp = now();
      for (const article of articles) {
        const row = {...article, first_seen: timestamp, last_seen: timestamp};
        const {key, payload} = identity('ai_watch.articles', row);
        const result = check(await statement("INSERT OR IGNORE INTO auxiliary_records(namespace, record_key, owner_id, payload) VALUES ('ai_watch.articles', ?, '', ?)", key, payload).run());
        if (result.meta?.changes === 1) newHashes.push(key);
        else {
          check(await statement("UPDATE auxiliary_records SET payload = json_set(payload, '$.last_seen', ?), revision = revision + 1 WHERE namespace = 'ai_watch.articles' AND record_key = ?", timestamp, key).run());
          existingHashes.push(key);
        }
      }
      return {newHashes, existingHashes};
    },
  };
}
