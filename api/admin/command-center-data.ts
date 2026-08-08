import { withAdmin } from "../_lib/http.js";
import {
  closeTrade,
  createCommandCenterDirective,
  createCommandCenterTask,
  createTrade,
  createTradePlan,
  deleteClosedTrade,
  executeTradePlan,
  loadCommandCenter,
  recordCommandCenterExecution,
  updateCommandCenterTask,
  updateTradePlan,
} from "../_lib/command-center-db.js";

const OWNER_ID = process.env.COMMAND_CENTER_OWNER_ID || "site-owner";
const taskStatuses = new Set(["today", "planned", "waiting", "done"]);
const directiveModes = new Set(["research", "draft", "implement", "hold"]);
const executionStatuses = new Set(["starting", "running", "waiting_approval", "completed", "failed", "interrupted"]);
const tradeDirections = new Set(["long", "short"]);
const tradeStyles = new Set(["cash", "margin"]);

function stringValue(value: unknown, max: number, fallback = ""): string {
  return typeof value === "string" ? value.trim().slice(0, max) : fallback;
}
function finite(value: unknown, fallback = 0): number { const parsed = typeof value === "number" ? value : Number(value); return Number.isFinite(parsed) ? parsed : fallback; }
function dateValue(value: unknown): string { const candidate = stringValue(value, 20); return /^\d{4}-\d{2}-\d{2}$/.test(candidate) ? candidate : ""; }
function invalid(res: any, error: string) { res.status(400).json({ error }); }
function response(res: any, data: unknown) { res.setHeader("Cache-Control", "private, no-store, max-age=0"); res.setHeader("Pragma", "no-cache"); res.status(200).json(data); }

export default withAdmin({ method: ["GET", "POST"] }, async ({ req, res, body }) => {
  if ((req.method || "GET").toUpperCase() === "GET") { response(res, await loadCommandCenter(OWNER_ID)); return; }
  const action = stringValue(body?.action, 40);
  if (action === "update_task") {
    const id = stringValue(body?.id, 120); const status = stringValue(body?.status, 20);
    if (!id || !taskStatuses.has(status)) return invalid(res, "invalid_task_update");
    await updateCommandCenterTask(id, status, OWNER_ID);
  } else if (action === "create_task") {
    const businessId = stringValue(body?.businessId, 80); const title = stringValue(body?.title, 180); const dueDate = dateValue(body?.dueDate);
    if (!businessId || !title || !dueDate) return invalid(res, "invalid_task");
    await createCommandCenterTask({ businessId, title, dueDate, priority: Math.max(1, Math.min(5, finite(body?.priority, 2))), reason: stringValue(body?.reason, 500) }, OWNER_ID);
  } else if (action === "create_directive") {
    const businessId = stringValue(body?.businessId, 80); const mode = stringValue(body?.mode, 20); const instruction = stringValue(body?.instruction, 800);
    if (!businessId || !instruction || !directiveModes.has(mode)) return invalid(res, "invalid_directive");
    await createCommandCenterDirective({ id: stringValue(body?.id, 120) || undefined, businessId, mode, instruction }, OWNER_ID);
  } else if (action === "record_execution") {
    const id = stringValue(body?.id, 120); const directiveId = stringValue(body?.directiveId, 120); const businessId = stringValue(body?.businessId, 80); const mode = stringValue(body?.mode, 20); const instruction = stringValue(body?.instruction, 800); const status = stringValue(body?.status, 30);
    if (!id || !directiveId || !businessId || !instruction || !directiveModes.has(mode) || !executionStatuses.has(status)) return invalid(res, "invalid_execution");
    await recordCommandCenterExecution({ id, directiveId, businessId, mode, instruction, status, summary: stringValue(body?.summary, 2_000), result: stringValue(body?.result, 50_000), error: stringValue(body?.error, 2_000), threadId: stringValue(body?.threadId, 200), version: Math.max(1, Math.min(100, finite(body?.version, 1))), hasChanges: body?.hasChanges === true, startedAt: stringValue(body?.startedAt, 40), completedAt: stringValue(body?.completedAt, 40) }, OWNER_ID);
  } else if (action === "create_trade") {
    const tradedAt = dateValue(body?.tradedAt); const market = stringValue(body?.market, 40); const symbol = stringValue(body?.symbol, 40).toUpperCase(); const direction = stringValue(body?.direction, 10);
    if (!tradedAt || !market || !/^[A-Z0-9.\-]{1,40}$/.test(symbol) || !tradeDirections.has(direction)) return invalid(res, "invalid_trade");
    await createTrade({ tradedAt, market, symbol, direction, entryPrice: Math.max(0, finite(body?.entryPrice)), quantity: Math.max(0, finite(body?.quantity)), riskAmount: Math.max(0, finite(body?.riskAmount)), memo: stringValue(body?.memo, 500) }, OWNER_ID);
  } else if (action === "create_trade_plan") {
    const market = stringValue(body?.market, 40); const symbol = stringValue(body?.symbol, 40).toUpperCase(); const tradeStyle = stringValue(body?.tradeStyle, 10); const direction = stringValue(body?.direction, 10);
    if (!market || !/^[A-Z0-9.\-]{1,40}$/.test(symbol) || !tradeStyles.has(tradeStyle) || !tradeDirections.has(direction)) return invalid(res, "invalid_trade_plan");
    await createTradePlan({ market, symbol, name: stringValue(body?.name, 120), tradeStyle, direction, signalScore: Math.max(0, Math.min(100, finite(body?.signalScore))), referencePrice: Math.max(0, finite(body?.referencePrice)), quantity: Math.max(0, finite(body?.quantity)), stopPrice: Math.max(0, finite(body?.stopPrice)), targetPrice: Math.max(0, finite(body?.targetPrice)), maxLoss: Math.max(0, finite(body?.maxLoss)), thesis: stringValue(body?.thesis, 1_000), invalidation: stringValue(body?.invalidation, 1_000), sourceAsOf: stringValue(body?.sourceAsOf, 50) }, OWNER_ID);
  } else if (action === "approve_trade_plan" || action === "cancel_trade_plan") {
    const id = stringValue(body?.id, 120); if (!id) return invalid(res, "invalid_trade_plan_update");
    await updateTradePlan(id, action === "approve_trade_plan" ? "approved" : "cancelled", OWNER_ID);
  } else if (action === "execute_trade_plan") {
    const id = stringValue(body?.id, 120); const tradedAt = dateValue(body?.tradedAt); const entryPrice = finite(body?.entryPrice); const quantity = finite(body?.quantity);
    if (!id || !tradedAt || entryPrice <= 0 || quantity <= 0) return invalid(res, "invalid_trade_execution");
    await executeTradePlan({ id, tradedAt, entryPrice, quantity, riskAmount: Math.max(0, finite(body?.riskAmount)) }, OWNER_ID);
  } else if (action === "close_trade") {
    const id = stringValue(body?.id, 120); const pnl = finite(body?.pnl, Number.NaN); if (!id || !Number.isFinite(pnl)) return invalid(res, "invalid_trade_close");
    await closeTrade(id, pnl, OWNER_ID);
  } else if (action === "delete_trade") {
    const id = stringValue(body?.id, 120); if (!id) return invalid(res, "invalid_trade_delete"); await deleteClosedTrade(id, OWNER_ID);
  } else return invalid(res, "unknown_action");
  response(res, await loadCommandCenter(OWNER_ID));
});
