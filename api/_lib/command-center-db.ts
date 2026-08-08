import { db } from "./supa.js";
import type {
  CommandCenterDashboard,
  CommandCenterDirective,
  CommandCenterExecution,
  CommandCenterMigrationSnapshot,
  CommandCenterOwnerId,
  CommandCenterProject,
  CommandCenterTask,
  CommandCenterTrade,
  CommandCenterTradePlan,
  CommandCenterUpsertResult,
} from "./command-center-types.js";

const DEFAULT_OWNER_ID = "site-owner";
const OWNER_ID_MAX_LENGTH = 120;

type AnyRow = Record<string, any>;
type CommandCenterTable =
  | "projects"
  | "tasks"
  | "directives"
  | "directive_executions"
  | "trades"
  | "trade_plans";

function ownerId(value?: string): CommandCenterOwnerId {
  const candidate = (value || process.env.COMMAND_CENTER_OWNER_ID || DEFAULT_OWNER_ID).trim();
  if (!candidate || candidate.length > OWNER_ID_MAX_LENGTH) throw new Error("invalid command center owner");
  return candidate;
}

function table(name: CommandCenterTable): any {
  return (db() as any).schema("command_center").from(name);
}

function checkError(error: any, operation: string): void {
  if (error) throw new Error(`command center ${operation} failed: ${String(error.message || "database error")}`);
}

function text(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : value == null ? fallback : String(value);
}

function number(value: unknown, fallback = 0): number {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function boolean(value: unknown): boolean {
  return value === true || value === 1 || value === "1" || value === "true";
}

function timestamp(value: unknown, fallback = new Date().toISOString()): string {
  const candidate = text(value);
  return candidate && !Number.isNaN(Date.parse(candidate)) ? new Date(candidate).toISOString() : fallback;
}

function emptyToNull(value: unknown): string | null {
  const candidate = text(value).trim();
  return candidate ? timestamp(candidate) : null;
}

function formatDateLabel(value: string): string {
  try {
    return new Intl.DateTimeFormat("ja-JP", {
      month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "Asia/Tokyo",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

async function readRows(name: CommandCenterTable, currentOwner: string, orderColumn: string, limit = 200): Promise<AnyRow[]> {
  const result = await table(name)
    .select("*")
    .eq("owner_id", currentOwner)
    .order(orderColumn, { ascending: false })
    .limit(limit);
  checkError(result.error, `${name} select`);
  return (result.data || []) as AnyRow[];
}

function mapProject(row: AnyRow): CommandCenterProject {
  return {
    businessId: text(row.business_id), displayName: text(row.display_name), status: text(row.status),
    statusLabel: text(row.status_label), productionUrl: text(row.production_url), hint: text(row.hint),
    lastReviewDate: text(row.last_review_date),
  };
}

function mapTask(row: AnyRow): CommandCenterTask {
  return {
    id: text(row.id), businessId: text(row.business_id), title: text(row.title), reason: text(row.reason),
    priority: number(row.priority, 2), status: text(row.status, "planned"), dueDate: text(row.due_date),
    effort: text(row.effort), blocker: text(row.blocker), category: text(row.category),
    createdAt: timestamp(row.created_at), updatedAt: timestamp(row.updated_at),
  };
}

function mapDirective(row: AnyRow): CommandCenterDirective {
  const createdAt = timestamp(row.created_at);
  return {
    id: text(row.id), businessId: text(row.business_id), mode: text(row.mode), instruction: text(row.instruction),
    createdAt, createdAtLabel: formatDateLabel(createdAt),
  };
}

function mapExecution(row: AnyRow): CommandCenterExecution {
  return {
    id: text(row.id), directiveId: text(row.directive_id), ownerId: text(row.owner_id),
    businessId: text(row.business_id), mode: text(row.mode), instruction: text(row.instruction),
    status: text(row.status), summary: text(row.summary), result: text(row.result), error: text(row.error),
    threadId: text(row.thread_id), version: number(row.version, 1), hasChanges: boolean(row.has_changes),
    startedAt: timestamp(row.started_at), completedAt: text(row.completed_at), updatedAt: timestamp(row.updated_at),
  };
}

function mapTrade(row: AnyRow): CommandCenterTrade {
  return {
    id: text(row.id), tradedAt: text(row.traded_at), market: text(row.market), symbol: text(row.symbol),
    direction: text(row.direction), status: text(row.status, "open"), entryPrice: number(row.entry_price),
    quantity: number(row.quantity), riskAmount: number(row.risk_amount), pnl: number(row.pnl), memo: text(row.memo),
  };
}

function mapTradePlan(row: AnyRow): CommandCenterTradePlan {
  return {
    id: text(row.id), market: text(row.market), symbol: text(row.symbol), name: text(row.name),
    tradeStyle: text(row.trade_style, "cash"), direction: text(row.direction, "long"),
    signalScore: number(row.signal_score), referencePrice: number(row.reference_price), quantity: number(row.quantity),
    stopPrice: number(row.stop_price), targetPrice: number(row.target_price), maxLoss: number(row.max_loss),
    thesis: text(row.thesis), invalidation: text(row.invalidation), sourceAsOf: text(row.source_as_of),
    status: text(row.status, "draft"), tradeId: text(row.trade_id), createdAt: timestamp(row.created_at),
    updatedAt: timestamp(row.updated_at),
  };
}

export async function loadCommandCenter(requestedOwnerId?: string): Promise<CommandCenterDashboard> {
  const currentOwner = ownerId(requestedOwnerId);
  const [projects, tasks, directives, executions, trades, tradePlans] = await Promise.all([
    readRows("projects", currentOwner, "display_name"),
    readRows("tasks", currentOwner, "updated_at"),
    readRows("directives", currentOwner, "created_at"),
    readRows("directive_executions", currentOwner, "updated_at"),
    readRows("trades", currentOwner, "traded_at"),
    readRows("trade_plans", currentOwner, "created_at"),
  ]);
  return {
    ownerId: currentOwner,
    projects: projects.map(mapProject),
    tasks: tasks.map(mapTask),
    directives: directives.map(mapDirective),
    executions: executions.map(mapExecution),
    trades: trades.map(mapTrade),
    tradePlans: tradePlans.map(mapTradePlan),
    generatedAt: new Date().toISOString(),
  };
}

export async function updateCommandCenterTask(id: string, status: string, requestedOwnerId?: string): Promise<void> {
  const result = await table("tasks").update({ status, updated_at: new Date().toISOString() })
    .eq("id", id).eq("owner_id", ownerId(requestedOwnerId));
  checkError(result.error, "task update");
}

export async function createCommandCenterTask(input: {
  businessId: string; title: string; dueDate: string; priority: number; reason?: string;
}, requestedOwnerId?: string): Promise<string> {
  const currentOwner = ownerId(requestedOwnerId);
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const result = await table("tasks").insert({
    id, business_id: input.businessId, title: input.title, reason: input.reason || "",
    priority: input.priority, status: "planned", due_date: input.dueDate, effort: "",
    blocker: "", category: "追加", owner_id: currentOwner, created_at: now, updated_at: now,
  });
  checkError(result.error, "task insert");
  return id;
}

export async function createCommandCenterDirective(input: {
  id?: string; businessId: string; mode: string; instruction: string;
}, requestedOwnerId?: string): Promise<string> {
  const currentOwner = ownerId(requestedOwnerId);
  const id = input.id || crypto.randomUUID();
  const now = new Date().toISOString();
  const result = await table("directives").insert({
    id, business_id: input.businessId, mode: input.mode, instruction: input.instruction,
    owner_id: currentOwner, created_at: now, updated_at: now,
  });
  checkError(result.error, "directive insert");
  return id;
}

export async function recordCommandCenterExecution(input: {
  id: string; directiveId: string; businessId: string; mode: string; instruction: string;
  status: string; summary?: string; result?: string; error?: string; threadId?: string;
  version?: number; hasChanges?: boolean; startedAt?: string; completedAt?: string;
}, requestedOwnerId?: string): Promise<void> {
  const currentOwner = ownerId(requestedOwnerId);
  const now = new Date().toISOString();
  const response = await table("directive_executions").upsert({
    id: input.id, directive_id: input.directiveId, owner_id: currentOwner, business_id: input.businessId,
    mode: input.mode, instruction: input.instruction, status: input.status, summary: input.summary || "",
    result: input.result || "", error: input.error || "", thread_id: input.threadId || "",
    version: input.version || 1, has_changes: Boolean(input.hasChanges), started_at: timestamp(input.startedAt, now),
    completed_at: emptyToNull(input.completedAt), updated_at: now,
  }, { onConflict: "id" });
  checkError(response.error, "execution upsert");
}

export async function createTradePlan(input: {
  market: string; symbol: string; name?: string; tradeStyle: string; direction: string;
  signalScore?: number; referencePrice?: number; quantity?: number; stopPrice?: number;
  targetPrice?: number; maxLoss?: number; thesis?: string; invalidation?: string; sourceAsOf?: string;
}, requestedOwnerId?: string): Promise<string> {
  const currentOwner = ownerId(requestedOwnerId);
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const response = await table("trade_plans").insert({
    id, market: input.market, symbol: input.symbol, name: input.name || "", trade_style: input.tradeStyle,
    direction: input.direction, signal_score: input.signalScore || 0, reference_price: input.referencePrice || 0,
    quantity: input.quantity || 0, stop_price: input.stopPrice || 0, target_price: input.targetPrice || 0,
    max_loss: input.maxLoss || 0, thesis: input.thesis || "", invalidation: input.invalidation || "",
    source_as_of: input.sourceAsOf || "", status: "draft", trade_id: "", owner_id: currentOwner,
    created_at: now, updated_at: now,
  });
  checkError(response.error, "trade plan insert");
  return id;
}

export async function updateTradePlan(id: string, status: "approved" | "cancelled", requestedOwnerId?: string): Promise<void> {
  const currentOwner = ownerId(requestedOwnerId);
  let query = table("trade_plans").update({ status, updated_at: new Date().toISOString() }).eq("id", id).eq("owner_id", currentOwner);
  query = status === "approved" ? query.eq("status", "draft") : query.in("status", ["draft", "approved"]);
  const response = await query;
  checkError(response.error, "trade plan update");
}

export async function createTrade(input: {
  tradedAt: string; market: string; symbol: string; direction: string;
  entryPrice: number; quantity: number; riskAmount: number; memo?: string;
}, requestedOwnerId?: string): Promise<string> {
  const currentOwner = ownerId(requestedOwnerId);
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const response = await table("trades").insert({
    id, traded_at: input.tradedAt, market: input.market, symbol: input.symbol, direction: input.direction,
    status: "open", entry_price: input.entryPrice, quantity: input.quantity, risk_amount: input.riskAmount,
    pnl: 0, memo: input.memo || "", owner_id: currentOwner, created_at: now, updated_at: now,
  });
  checkError(response.error, "trade insert");
  return id;
}

export async function executeTradePlan(input: {
  id: string; tradedAt: string; entryPrice: number; quantity: number; riskAmount: number;
}, requestedOwnerId?: string): Promise<string | null> {
  const currentOwner = ownerId(requestedOwnerId);
  const planResult = await table("trade_plans").select("*").eq("id", input.id).eq("owner_id", currentOwner).eq("status", "approved").maybeSingle();
  checkError(planResult.error, "trade plan lookup");
  if (!planResult.data) return null;
  const tradeId = await createTrade({
    tradedAt: input.tradedAt, market: text(planResult.data.market), symbol: text(planResult.data.symbol),
    direction: text(planResult.data.direction), entryPrice: input.entryPrice, quantity: input.quantity,
    riskAmount: input.riskAmount, memo: "相場羅針盤の承認済みプランから作成",
  }, currentOwner);
  const updateResult = await table("trade_plans").update({ status: "executed", trade_id: tradeId, updated_at: new Date().toISOString() })
    .eq("id", input.id).eq("owner_id", currentOwner).eq("status", "approved");
  checkError(updateResult.error, "trade plan execution");
  return tradeId;
}

export async function closeTrade(id: string, pnl: number, requestedOwnerId?: string): Promise<void> {
  const response = await table("trades").update({ status: "closed", pnl, updated_at: new Date().toISOString() })
    .eq("id", id).eq("owner_id", ownerId(requestedOwnerId));
  checkError(response.error, "trade close");
}

export async function deleteClosedTrade(id: string, requestedOwnerId?: string): Promise<void> {
  const response = await table("trades").delete().eq("id", id).eq("owner_id", ownerId(requestedOwnerId)).eq("status", "closed");
  checkError(response.error, "closed trade delete");
}

function migrationRows(snapshot: CommandCenterMigrationSnapshot, currentOwner: string) {
  const now = new Date().toISOString();
  const rows = snapshot.tables;
  return {
    projects: rows.projects.map((row) => ({
      business_id: text(row.business_id), display_name: text(row.display_name), status: text(row.status),
      status_label: text(row.status_label), production_url: text(row.production_url), hint: text(row.hint),
      last_review_date: text(row.last_review_date), owner_id: currentOwner,
      created_at: timestamp(row.created_at, now), updated_at: timestamp(row.updated_at, now),
    })),
    tasks: rows.tasks.map((row) => ({
      id: text(row.id), business_id: text(row.business_id), title: text(row.title), reason: text(row.reason),
      priority: number(row.priority, 2), status: text(row.status, "planned"), due_date: text(row.due_date),
      effort: text(row.effort), blocker: text(row.blocker), category: text(row.category), owner_id: currentOwner,
      created_at: timestamp(row.created_at, now), updated_at: timestamp(row.updated_at, now),
    })),
    directives: rows.directives.map((row) => ({
      id: text(row.id), business_id: text(row.business_id), mode: text(row.mode), instruction: text(row.instruction),
      owner_id: currentOwner, created_at: timestamp(row.created_at, now), updated_at: timestamp(row.updated_at, now),
    })),
    directive_executions: rows.directive_executions.map((row) => ({
      id: text(row.id), directive_id: text(row.directive_id), owner_id: currentOwner, business_id: text(row.business_id),
      mode: text(row.mode), instruction: text(row.instruction), status: text(row.status), summary: text(row.summary),
      result: text(row.result), error: text(row.error), thread_id: text(row.thread_id), version: number(row.version, 1),
      has_changes: boolean(row.has_changes), started_at: timestamp(row.started_at, now),
      completed_at: emptyToNull(row.completed_at), updated_at: timestamp(row.updated_at, now),
    })),
    trades: rows.trades.map((row) => ({
      id: text(row.id), traded_at: text(row.traded_at), market: text(row.market), symbol: text(row.symbol),
      direction: text(row.direction), status: text(row.status, "open"), entry_price: number(row.entry_price),
      quantity: number(row.quantity), risk_amount: number(row.risk_amount), pnl: number(row.pnl), memo: text(row.memo),
      owner_id: currentOwner, created_at: timestamp(row.created_at, now), updated_at: timestamp(row.updated_at, now),
    })),
    trade_plans: rows.trade_plans.map((row) => ({
      id: text(row.id), market: text(row.market), symbol: text(row.symbol), name: text(row.name),
      trade_style: text(row.trade_style, "cash"), direction: text(row.direction, "long"), signal_score: number(row.signal_score),
      reference_price: number(row.reference_price), quantity: number(row.quantity), stop_price: number(row.stop_price),
      target_price: number(row.target_price), max_loss: number(row.max_loss), thesis: text(row.thesis),
      invalidation: text(row.invalidation), source_as_of: text(row.source_as_of), status: text(row.status, "draft"),
      trade_id: text(row.trade_id), owner_id: currentOwner, created_at: timestamp(row.created_at, now),
      updated_at: timestamp(row.updated_at, now),
    })),
  };
}

async function upsertRows(name: CommandCenterTable, rows: AnyRow[], conflict: string): Promise<void> {
  if (!rows.length) return;
  const response = await table(name).upsert(rows, { onConflict: conflict });
  checkError(response.error, `${name} migration upsert`);
}

export async function upsertCommandCenterSnapshot(
  snapshot: CommandCenterMigrationSnapshot,
  requestedOwnerId?: string,
): Promise<CommandCenterUpsertResult> {
  if (snapshot.schemaVersion !== 1 || !snapshot.tables || snapshot.source !== "execution-command-room") {
    throw new Error("unsupported command center snapshot");
  }
  const currentOwner = ownerId(requestedOwnerId);
  const rows = migrationRows(snapshot, currentOwner);
  await upsertRows("projects", rows.projects, "business_id");
  await upsertRows("tasks", rows.tasks, "id");
  await upsertRows("directives", rows.directives, "id");
  await upsertRows("directive_executions", rows.directive_executions, "id");
  await upsertRows("trades", rows.trades, "id");
  await upsertRows("trade_plans", rows.trade_plans, "id");
  return {
    ownerId: currentOwner,
    counts: {
      projects: rows.projects.length,
      tasks: rows.tasks.length,
      directives: rows.directives.length,
      directive_executions: rows.directive_executions.length,
      trades: rows.trades.length,
      trade_plans: rows.trade_plans.length,
    },
  };
}

export async function countCommandCenterRows(requestedOwnerId?: string): Promise<Record<CommandCenterTable, number>> {
  const currentOwner = ownerId(requestedOwnerId);
  const names: CommandCenterTable[] = ["projects", "tasks", "directives", "directive_executions", "trades", "trade_plans"];
  const entries = await Promise.all(names.map(async (name) => {
    const result = await table(name).select("*", { count: "exact", head: true }).eq("owner_id", currentOwner);
    checkError(result.error, `${name} count`);
    return [name, Number(result.count || 0)] as const;
  }));
  return Object.fromEntries(entries) as Record<CommandCenterTable, number>;
}
