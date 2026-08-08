export type CommandCenterOwnerId = string;

export type CommandCenterProject = {
  businessId: string;
  displayName: string;
  status: string;
  statusLabel: string;
  productionUrl: string;
  hint: string;
  lastReviewDate: string;
};

export type CommandCenterTask = {
  id: string;
  businessId: string;
  title: string;
  reason: string;
  priority: number;
  status: "today" | "planned" | "waiting" | "done" | string;
  dueDate: string;
  effort: string;
  blocker: string;
  category: string;
  createdAt: string;
  updatedAt: string;
};

export type CommandCenterDirective = {
  id: string;
  businessId: string;
  mode: "research" | "draft" | "implement" | "hold" | string;
  instruction: string;
  createdAt: string;
  createdAtLabel?: string;
};

export type CommandCenterExecution = {
  id: string;
  directiveId: string;
  ownerId: string;
  businessId: string;
  mode: string;
  instruction: string;
  status: string;
  summary: string;
  result: string;
  error: string;
  threadId: string;
  version: number;
  hasChanges: boolean;
  startedAt: string;
  completedAt: string;
  updatedAt: string;
};

export type CommandCenterTrade = {
  id: string;
  tradedAt: string;
  market: string;
  symbol: string;
  direction: "long" | "short" | string;
  status: "open" | "closed" | string;
  entryPrice: number;
  quantity: number;
  riskAmount: number;
  pnl: number;
  memo: string;
};

export type CommandCenterTradePlan = {
  id: string;
  market: string;
  symbol: string;
  name: string;
  tradeStyle: "cash" | "margin" | string;
  direction: "long" | "short" | string;
  signalScore: number;
  referencePrice: number;
  quantity: number;
  stopPrice: number;
  targetPrice: number;
  maxLoss: number;
  thesis: string;
  invalidation: string;
  sourceAsOf: string;
  status: "draft" | "approved" | "executed" | "cancelled" | string;
  tradeId: string;
  createdAt: string;
  updatedAt: string;
};

export type CommandCenterDashboard = {
  ownerId: string;
  projects: CommandCenterProject[];
  tasks: CommandCenterTask[];
  directives: CommandCenterDirective[];
  executions: CommandCenterExecution[];
  trades: CommandCenterTrade[];
  tradePlans: CommandCenterTradePlan[];
  generatedAt: string;
};

export type CommandCenterSnapshotRow = Record<string, unknown>;

export type CommandCenterMigrationSnapshot = {
  schemaVersion: 1;
  source: "execution-command-room" | string;
  exportedAt: string;
  tables: {
    projects: CommandCenterSnapshotRow[];
    tasks: CommandCenterSnapshotRow[];
    directives: CommandCenterSnapshotRow[];
    directive_executions: CommandCenterSnapshotRow[];
    trades: CommandCenterSnapshotRow[];
    trade_plans: CommandCenterSnapshotRow[];
  };
};

export type CommandCenterUpsertResult = {
  ownerId: string;
  counts: Record<keyof CommandCenterMigrationSnapshot["tables"], number>;
};
