import { spawn } from "node:child_process";
import { createHash, createHmac, randomBytes, randomInt, timingSafeEqual } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { basename, dirname, isAbsolute, join, relative, resolve } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath, pathToFileURL } from "node:url";
import { NEXT_STAGES, STAGE_SCHEMAS } from "./contracts.mjs";

const BRIDGE_VERSION = "1.0.0";
const CODEX_SCHEMA_VERSION = "0.145.0-alpha.18";
const DEFAULT_PORT = 43117;
const MAX_BODY_BYTES = 64 * 1024;
const MAX_OUTPUT_CHARS = 120_000;
const COMMAND_ROOM_ORIGIN = "https://aiclimb.vercel.app";
const AI_CONSULT_ORIGIN = "https://aiclimb.vercel.app";
const terminalStatuses = new Set(["completed", "failed", "interrupted"]);
const executableModes = new Set(["research", "draft", "implement"]);

const appServerDirectory = dirname(fileURLToPath(import.meta.url));
const commandRoomRoot = resolve(appServerDirectory, "..");
const commandSkillPath = join(commandRoomRoot, ".agents", "skills", "command-room-executor", "SKILL.md");
const contentStatePath = join(appServerDirectory, ".local", "content-runs.json");
const bridgeAuthPath = join(appServerDirectory, ".local", "bridge-auth.json");
const contentBusinesses = new Map(loadJson(join(appServerDirectory, "businesses.json")).map((business) => [business.businessId, business]));

function safeEqual(left, right) {
  const a = Buffer.from(String(left));
  const b = Buffer.from(String(right));
  return a.length === b.length && timingSafeEqual(a, b);
}

function hashToken(value) {
  return createHash("sha256").update(value).digest("hex");
}

function isoNow() {
  return new Date().toISOString();
}

function truncate(value, length = 2_000) {
  const text = typeof value === "string" ? value : JSON.stringify(value ?? "");
  return text.length > length ? `${text.slice(0, length)}…` : text;
}

export function isAllowedOrigin(origin) {
  if (origin === COMMAND_ROOM_ORIGIN || origin === AI_CONSULT_ORIGIN) return true;
  try {
    const url = new URL(origin);
    return url.protocol === "http:" && (url.hostname === "localhost" || url.hostname === "127.0.0.1");
  } catch {
    return false;
  }
}

function loadJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function loadProjectConfig() {
  const base = loadJson(join(appServerDirectory, "projects.json"));
  const localPath = join(appServerDirectory, "projects.local.json");
  if (!existsSync(localPath)) return base;
  const local = loadJson(localPath);
  return { ...base, ...local, projects: { ...base.projects, ...local.projects } };
}

export class ProjectRegistry {
  constructor(config, options = {}) {
    this.config = config;
    this.commandRoot = options.commandRoot ?? commandRoomRoot;
    this.projectsRoot = resolve(options.projectsRoot ?? process.env.COMMAND_ROOM_PROJECTS_ROOT ?? resolve(this.commandRoot, ".."));
    this.exists = options.exists ?? ((path) => existsSync(path) && statSync(path).isDirectory());
  }

  all() {
    return Object.keys(this.config.projects ?? {}).map((businessId) => this.lookup(businessId));
  }

  lookup(businessId) {
    const entry = this.config.projects?.[businessId];
    if (!entry || typeof entry.folder !== "string" || !entry.folder.trim()) {
      return { businessId, available: false, reason: "ローカルプロジェクトが未設定です" };
    }
    const root = resolve(this.projectsRoot, entry.folder);
    const relation = relative(this.projectsRoot, root);
    if (!relation || relation.startsWith("..") || isAbsolute(relation)) {
      return { businessId, available: false, reason: "許可範囲外のプロジェクトです" };
    }
    if (!this.exists(root)) {
      return { businessId, available: false, reason: "このPCに対象フォルダがありません" };
    }
    return { businessId, available: true, root, folder: entry.folder };
  }

  publicList() {
    return this.all().map(({ businessId, available, reason }) => ({ businessId, available, reason: reason ?? null }));
  }
}

export class PairingAuthority {
  constructor(options = {}) {
    this.now = options.now ?? (() => Date.now());
    this.codeFactory = options.codeFactory ?? (() => String(randomInt(100_000, 1_000_000)));
    this.tokenFactory = options.tokenFactory ?? (() => randomBytes(32).toString("base64url"));
    this.capabilities = new Map();
    this.rotateCode();
  }

  rotateCode() {
    this.code = this.codeFactory();
    this.codeExpiresAt = this.now() + 10 * 60_000;
    return this.code;
  }

  pair(code, origin) {
    if (this.now() > this.codeExpiresAt || !safeEqual(code, this.code)) return null;
    const credential = this.issue(origin);
    this.rotateCode();
    return credential;
  }

  issue(origin) {
    const token = this.tokenFactory();
    const csrf = this.tokenFactory();
    const expiresAt = this.now() + 8 * 60 * 60_000;
    this.capabilities.set(hashToken(token), { csrfHash: hashToken(csrf), origin, expiresAt });
    return { token, csrf, expiresAt: new Date(expiresAt).toISOString() };
  }

  authenticate(authorization, csrf, origin) {
    const token = authorization?.startsWith("Bearer ") ? authorization.slice(7) : "";
    const record = this.capabilities.get(hashToken(token));
    if (!record || record.origin !== origin || record.expiresAt < this.now()) return false;
    return safeEqual(record.csrfHash, hashToken(csrf ?? ""));
  }
}

function bridgeAuthSecret() {
  const configured = process.env.COMMAND_ROOM_BRIDGE_AUTH_SECRET?.trim();
  if (configured) return configured;
  if (!existsSync(bridgeAuthPath)) return "";
  try {
    const local = loadJson(bridgeAuthPath);
    return typeof local.secret === "string" ? local.secret.trim() : "";
  } catch {
    return "";
  }
}

const SAFE_APP_SERVER_ENVIRONMENT_KEYS = new Set([
  "ALLUSERSPROFILE", "APPDATA", "CI", "CODEX_HOME", "COMSPEC", "HOME", "HOMEDRIVE", "HOMEPATH",
  "LANG", "LC_ALL", "LC_CTYPE", "LOCALAPPDATA", "NUMBER_OF_PROCESSORS", "OS", "PATH", "PATHEXT",
  "PROCESSOR_ARCHITECTURE", "PROCESSOR_IDENTIFIER", "PROCESSOR_LEVEL", "PROCESSOR_REVISION", "PROGRAMDATA",
  "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432", "PUBLIC", "SHELL", "SYSTEMDRIVE", "SYSTEMROOT",
  "TEMP", "TERM", "TMP", "TMPDIR", "USERDOMAIN", "USERNAME", "USERPROFILE", "WINDIR",
  "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_RUNTIME_DIR",
]);

export function appServerChildEnvironment(source = process.env) {
  return Object.fromEntries(Object.entries(source).filter(([key]) => SAFE_APP_SERVER_ENVIRONMENT_KEYS.has(key.toUpperCase())));
}

export class OwnerAssertionVerifier {
  constructor(options = {}) {
    this.secret = options.secret ?? bridgeAuthSecret();
    this.ownerEmail = String(options.ownerEmail ?? process.env.COMMAND_ROOM_OWNER_EMAIL ?? "goodbouldering@gmail.com").toLowerCase();
    this.now = options.now ?? (() => Date.now());
    this.seenNonces = new Map();
  }

  verify(assertion, origin) {
    if (!this.secret || typeof assertion !== "string") return null;
    const [encoded, signature, extra] = assertion.split(".");
    if (!encoded || !signature || extra) return null;
    const expected = createHmac("sha256", this.secret).update(encoded).digest("base64url");
    if (!safeEqual(signature, expected)) return null;
    let payload;
    try {
      payload = JSON.parse(Buffer.from(encoded, "base64url").toString("utf8"));
    } catch {
      return null;
    }
    const now = this.now();
    const expiresAt = Number(payload.exp) * 1_000;
    const issuedAt = Number(payload.iat) * 1_000;
    const email = String(payload.sub ?? "").toLowerCase();
    const nonce = String(payload.nonce ?? "");
    if (
      payload.v !== 1 ||
      payload.aud !== "execution-command-room-bridge" ||
      payload.origin !== origin ||
      email !== this.ownerEmail ||
      !nonce ||
      !Number.isFinite(expiresAt) ||
      !Number.isFinite(issuedAt) ||
      expiresAt < now ||
      expiresAt > now + 2 * 60_000 ||
      issuedAt > now + 30_000 ||
      issuedAt < now - 2 * 60_000 ||
      this.seenNonces.has(nonce)
    ) return null;
    this.seenNonces.set(nonce, expiresAt);
    for (const [seenNonce, seenUntil] of this.seenNonces) {
      if (seenUntil < now) this.seenNonces.delete(seenNonce);
    }
    return { email, expiresAt: new Date(expiresAt).toISOString() };
  }
}

export class SitesRelayClient {
  constructor(options = {}) {
    this.url = options.url ?? `${COMMAND_ROOM_ORIGIN}/api/admin/command-center/relay`;
    this.secret = options.secret ?? bridgeAuthSecret();
    this.authority = options.authority;
    this.manager = options.manager;
    this.fetch = options.fetch ?? fetch;
    this.intervalMs = options.intervalMs ?? 1_500;
    this.processed = new Map();
    this.stopped = false;
    this.timer = null;
  }

  async signedPost(payload) {
    const body = JSON.stringify({ ...payload, nonce: randomBytes(18).toString("base64url") });
    const timestamp = String(Date.now());
    const signature = createHmac("sha256", this.secret).update(`${timestamp}.${body}`).digest("base64url");
    const response = await this.fetch(this.url, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-command-room-relay-timestamp": timestamp,
        "x-command-room-relay-signature": signature,
      },
      body,
    });
    if (!response.ok) throw new Error(`Sites relay failed (${response.status})`);
    return response.json();
  }

  async handleRequest(request) {
    if (this.processed.has(request.id)) return this.processed.get(request.id);
    const { method, path, body = {} } = request;
    let result;
    if (method === "POST" && path === "/v1/runs") {
      result = { statusCode: 202, response: this.manager.start(body) };
    } else {
      const runMatch = path.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)$/);
      const approvalMatch = path.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)\/approvals\/([^/]+)$/);
      const interruptMatch = path.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)\/interrupt$/);
      const adjustMatch = path.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)\/adjust$/);
      if (method === "GET" && runMatch) {
        const run = this.manager.get(runMatch[1]);
        result = { statusCode: run ? 200 : 404, response: run ?? { error: "run_not_found" } };
      } else if (method === "POST" && approvalMatch) {
        result = {
          statusCode: 200,
          response: await this.manager.answerApproval(approvalMatch[1], decodeURIComponent(approvalMatch[2]), body.action, body.answers ?? {}),
        };
      } else if (method === "POST" && interruptMatch) {
        result = { statusCode: 200, response: await this.manager.interrupt(interruptMatch[1]) };
      } else if (method === "POST" && adjustMatch) {
        result = { statusCode: 202, response: this.manager.adjust(adjustMatch[1], String(body.adjustment ?? "")) };
      } else {
        result = { statusCode: 404, response: { error: "relay_path_not_found" } };
      }
    }
    this.processed.set(request.id, result);
    if (this.processed.size > 200) this.processed.delete(this.processed.keys().next().value);
    return result;
  }

  async tick() {
    if (!this.secret || this.stopped) return;
    if (this.authority.now() > this.authority.codeExpiresAt) this.authority.rotateCode();
    const heartbeat = await this.signedPost({
      action: "heartbeat",
      pairCode: this.authority.code,
      pairExpiresAt: new Date(this.authority.codeExpiresAt).toISOString(),
      bridge: { version: BRIDGE_VERSION, codexSchemaVersion: CODEX_SCHEMA_VERSION, transport: "outbound-sites-relay" },
    });
    if (heartbeat.rotatePairCode) this.authority.rotateCode();
    for (const request of heartbeat.requests ?? []) {
      try {
        const completed = await this.handleRequest(request);
        await this.signedPost({ action: "complete", requestId: request.id, ...completed });
      } catch (error) {
        await this.signedPost({
          action: "complete",
          requestId: request.id,
          statusCode: 422,
          response: { error: truncate(error?.message ?? error, 500) },
        });
      }
    }
  }

  start() {
    if (!this.secret || this.timer) return;
    const run = async () => {
      if (this.stopped) return;
      try {
        await this.tick();
      } catch {}
      if (!this.stopped) this.timer = setTimeout(run, this.intervalMs);
    };
    void run();
  }

  close() {
    this.stopped = true;
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
  }
}

export class AppServerClient {
  constructor(options = {}) {
    this.executable = options.executable ?? process.env.CODEX_COMMAND ?? "codex";
    this.cwd = options.cwd ?? commandRoomRoot;
    this.spawnProcess = options.spawnProcess ?? spawn;
    this.pending = new Map();
    this.nextId = 1;
    this.handlers = [];
    this.stderr = "";
  }

  setHandlers({ onNotification, onServerRequest }) {
    this.handlers.push({ onNotification, onServerRequest });
  }

  async ensureStarted() {
    if (this.child && !this.child.killed) return;
    if (this.startPromise) return this.startPromise;
    this.startPromise = this.start().finally(() => { this.startPromise = null; });
    return this.startPromise;
  }

  async start() {
    const windowsPackagedCodex = process.platform === "win32" && this.executable === "codex";
    const windowsCodexScript = join(process.env.APPDATA ?? "", "npm", "node_modules", "@openai", "codex", "bin", "codex.js");
    const executable = windowsPackagedCodex
      ? process.execPath
      : this.executable;
    const args = windowsPackagedCodex
      ? [windowsCodexScript, "app-server", "-c", "service_tier=\"fast\""]
      : ["app-server", "-c", "service_tier=\"fast\""];
    this.child = this.spawnProcess(executable, args, {
      cwd: this.cwd,
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
      env: appServerChildEnvironment(),
    });
    this.child.stdout.setEncoding("utf8");
    this.child.stderr.setEncoding("utf8");
    this.child.stderr.on("data", (chunk) => { this.stderr = `${this.stderr}${chunk}`.slice(-4_000); });
    createInterface({ input: this.child.stdout, crlfDelay: Infinity }).on("line", (line) => this.handleLine(line));
    this.child.on("exit", (code) => this.handleExit(code));
    await new Promise((resolveSpawn, rejectSpawn) => {
      this.child.once("spawn", resolveSpawn);
      this.child.once("error", rejectSpawn);
    });
    try {
      await this.rawRequest("initialize", {
        clientInfo: { name: "execution-command-room", title: "実行司令室", version: BRIDGE_VERSION },
        capabilities: { experimentalApi: false },
      });
    } catch (error) {
      const details = this.stderr.trim();
      throw new Error(details ? `${error.message}: ${details}` : error.message);
    }
    this.notify("initialized", {});
  }

  handleLine(line) {
    let message;
    try { message = JSON.parse(line); } catch { return; }
    if (Object.hasOwn(message, "id") && !message.method) {
      const pending = this.pending.get(String(message.id));
      if (!pending) return;
      this.pending.delete(String(message.id));
      clearTimeout(pending.timer);
      if (message.error) pending.reject(new Error(message.error.message ?? "Codex App Server error"));
      else pending.resolve(message.result);
      return;
    }
    if (message.method && Object.hasOwn(message, "id")) {
      void this.handleServerRequest(message);
      return;
    }
    if (message.method) {
      for (const handler of this.handlers) handler.onNotification?.(message.method, message.params ?? {});
    }
  }

  async handleServerRequest(message) {
    try {
      for (const handler of this.handlers) {
        if (!handler.onServerRequest) continue;
        const result = await handler.onServerRequest(message);
        if (result === undefined) continue;
        if (result !== null) this.respond(message.id, result);
        return;
      }
      const method = message.method ?? "";
      if (method.includes("command") || method.includes("execCommand") || method.includes("file") || method.includes("Patch")) return this.respond(message.id, { decision: "decline" });
      if (method.includes("permissions")) return this.respond(message.id, { permissions: {}, scope: "turn" });
      if (method.includes("requestUserInput")) return this.respond(message.id, { answers: {} });
      this.respondError(message.id, new Error("未許可のApp Server要求です"));
    } catch (error) {
      this.respondError(message.id, error);
    }
  }

  handleExit(code) {
    const message = this.stderr.trim() || `Codex App Server stopped (${code ?? "unknown"})`;
    for (const entry of this.pending.values()) {
      clearTimeout(entry.timer);
      entry.reject(new Error(message));
    }
    this.pending.clear();
    this.child = null;
  }

  send(message) {
    if (!this.child?.stdin?.writable) throw new Error("Codex App Server is not running");
    this.child.stdin.write(`${JSON.stringify(message)}\n`);
  }

  rawRequest(method, params, timeoutMs = 45_000) {
    const id = this.nextId++;
    return new Promise((resolveRequest, rejectRequest) => {
      const timer = setTimeout(() => {
        this.pending.delete(String(id));
        rejectRequest(new Error(`${method} timed out`));
      }, timeoutMs);
      this.pending.set(String(id), { resolve: resolveRequest, reject: rejectRequest, timer });
      this.send({ id, method, params });
    });
  }

  async request(method, params, timeoutMs) {
    await this.ensureStarted();
    return this.rawRequest(method, params, timeoutMs);
  }

  notify(method, params) {
    this.send({ method, params });
  }

  respond(id, result) {
    this.send({ id, result });
  }

  respondError(id, error) {
    this.send({ id, error: { code: -32603, message: truncate(error?.message ?? error, 500) } });
  }

  close() {
    if (this.child && !this.child.killed) this.child.kill();
  }
}

const resultSchema = {
  type: "object",
  additionalProperties: false,
  required: ["status", "summary", "details", "artifacts", "verification", "nextActions", "requiresApproval"],
  properties: {
    status: { type: "string", enum: ["completed", "partial", "blocked"] },
    summary: { type: "string" },
    details: { type: "array", items: { type: "string" } },
    artifacts: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["label", "value", "kind"],
        properties: {
          label: { type: "string" },
          value: { type: "string" },
          kind: { type: "string", enum: ["file", "url", "note"] },
        },
      },
    },
    verification: { type: "array", items: { type: "string" } },
    nextActions: { type: "array", items: { type: "string" } },
    requiresApproval: { type: "boolean" },
  },
};

const modeInstructions = {
  research: "調査として、必要な一次情報と対象プロジェクトを確認し、事実を整理してください。変更は行わないでください。",
  draft: "下書きとして、再利用できる成果物を対象プロジェクト内に作成し、内容を検証してください。公開や送信はしないでください。",
  implement: "実装として、対象プロジェクトの実ファイルを変更し、通常のテストまで行ってください。プロジェクト規則が求める範囲を超える公開・送信・課金は承認なしに行わないでください。",
};

export function buildRunPrompt(run, options = {}) {
  if (options.adjustment) {
    return [
      "$command-room-executor",
      `対象事業ID: ${run.businessId}`,
      `元の指示: ${run.instruction}`,
      "これは同じ成果物への全体調整です。確定済み事実、事業境界、承認ゲートを維持してください。",
      `現在の構造化結果:\n${truncate(options.previousResult ?? run.output, 40_000)}`,
      `調整指示:\n${options.adjustment}`,
      "変更後の成果物を確認し、指定されたJSON Schemaで結果を返してください。",
    ].join("\n\n");
  }
  return [
    "$command-room-executor",
    `対象事業ID: ${run.businessId}`,
    `実行種別: ${run.mode}`,
    modeInstructions[run.mode],
    `実行する指示:\n${run.instruction}`,
    "表示や提案だけで終えず、この実行種別で完了と判断できるところまで実際に進めてください。",
    "完了・未完了・確認待ちを区別し、指定されたJSON Schemaで結果を返してください。",
  ].join("\n\n");
}

export function parseStructuredResult(output, fallbackStatus = "completed") {
  const cleaned = String(output ?? "").trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  try {
    const value = JSON.parse(cleaned);
    if (value && typeof value === "object") return value;
  } catch {}
  return {
    status: "partial",
    summary: cleaned || "実行結果を取得できませんでした",
    details: [], artifacts: [], verification: [], nextActions: [], requiresApproval: false,
  };
}

export function pickCompatibleModel(models) {
  const visible = (models ?? []).filter((model) => !model.hidden);
  return visible.find((model) => model.id === "gpt-5.6-sol" || model.model === "gpt-5.6-sol")
    ?? visible.find((model) => model.id === "gpt-5.5" || model.model === "gpt-5.5")
    ?? visible.find((model) => model.id === "gpt-5.4" || model.model === "gpt-5.4")
    ?? visible.find((model) => model.id === "gpt-5.2" || model.model === "gpt-5.2")
    ?? visible.find((model) => !String(model.id ?? model.model).startsWith("gpt-5.6"))
    ?? visible[0]
    ?? null;
}

function approvalKind(method) {
  if (method.includes("commandExecution") || method === "execCommandApproval") return "command";
  if (method.includes("fileChange") || method === "applyPatchApproval") return "file_change";
  if (method.includes("permissions")) return "permission";
  if (method.includes("requestUserInput")) return "user_input";
  if (method.includes("elicitation")) return "elicitation";
  return "unsupported";
}

function summarizeItem(item) {
  const type = item?.type ?? "work";
  const labels = {
    agentMessage: "結果をまとめています",
    commandExecution: "検証コマンドを実行しています",
    fileChange: "ファイルを更新しています",
    mcpToolCall: "連携機能を使っています",
    webSearch: "情報を確認しています",
    reasoning: "進め方を整理しています",
  };
  return labels[type] ?? "作業を進めています";
}

export class ExecutionManager {
  constructor(client, registry, options = {}) {
    this.client = client;
    this.registry = registry;
    this.skillPath = options.skillPath ?? commandSkillPath;
    this.runs = new Map();
    this.threadRuns = new Map();
    this.turnRuns = new Map();
    this.pendingApprovals = new Map();
    client.setHandlers({
      onNotification: (method, params) => this.onNotification(method, params),
      onServerRequest: (message) => this.onServerRequest(message),
    });
  }

  publicRun(run) {
    return {
      id: run.id,
      directiveId: run.directiveId,
      businessId: run.businessId,
      mode: run.mode,
      instruction: run.instruction,
      status: run.status,
      stage: run.stage,
      plan: run.plan,
      progress: run.progress.slice(-12),
      output: run.output,
      result: run.result,
      error: run.error,
      threadId: run.threadId,
      turnId: run.turnId,
      version: run.version,
      hasChanges: run.hasChanges,
      startedAt: run.startedAt,
      updatedAt: run.updatedAt,
      completedAt: run.completedAt,
      approvals: [...run.approvals.values()].map((approval) => approval.public),
    };
  }

  get(runId) {
    const run = this.runs.get(runId);
    return run ? this.publicRun(run) : null;
  }

  start(input) {
    if (!executableModes.has(input.mode)) throw new Error("この指示種別は実行できません");
    const project = this.registry.lookup(input.businessId);
    if (!project.available) throw new Error(project.reason);
    if (typeof input.instruction !== "string" || !input.instruction.trim()) throw new Error("指示内容がありません");
    const run = {
      id: randomBytes(12).toString("base64url"),
      directiveId: String(input.directiveId ?? "").slice(0, 120),
      businessId: input.businessId,
      mode: input.mode,
      instruction: input.instruction.trim().slice(0, 4_000),
      project,
      status: "starting",
      stage: "Codexへ接続しています",
      plan: [], progress: [], output: "", result: null, error: "",
      threadId: input.threadId ? String(input.threadId).slice(0, 200) : null,
      turnId: null,
      version: Math.max(1, Number(input.version) || 1),
      hasChanges: false,
      startedAt: isoNow(), updatedAt: isoNow(), completedAt: null,
      approvals: new Map(),
    };
    this.runs.set(run.id, run);
    this.trimRuns();
    void this.launch(run, {
      resume: Boolean(input.threadId),
      adjustment: input.adjustment ? String(input.adjustment).slice(0, 4_000) : null,
      previousResult: input.previousResult ? String(input.previousResult).slice(0, 50_000) : null,
    });
    return this.publicRun(run);
  }

  async launch(run, options = {}) {
    try {
      await this.client.ensureStarted();
      run.stage = "実行手順を読み込んでいます";
      run.updatedAt = isoNow();
      const [skillResponse, modelResponse] = await Promise.all([
        this.client.request("skills/list", { cwds: [commandRoomRoot, run.project.root], forceReload: true }),
        this.client.request("model/list", { includeHidden: false, limit: 100 }),
      ]);
      const skills = (skillResponse?.data ?? []).flatMap((entry) => entry.skills ?? []);
      const skill = skills.find((item) => item.name === "command-room-executor" && item.enabled);
      if (!skill) throw new Error("実行司令室の実行スキルを読み込めませんでした");
      const model = pickCompatibleModel(modelResponse?.data);
      if (!model) throw new Error("このCodex CLIで利用できるモデルがありません");

      const threadSettings = {
        cwd: run.project.root,
        approvalPolicy: "on-request",
        approvalsReviewer: "user",
        sandbox: "workspace-write",
        personality: "pragmatic",
        model: model.model ?? model.id,
      };
      if (options.resume) {
        await this.client.request("thread/resume", { threadId: run.threadId, ...threadSettings });
      } else {
        const response = await this.client.request("thread/start", threadSettings);
        run.threadId = response?.thread?.id;
      }
      if (!run.threadId) throw new Error("Codex threadを開始できませんでした");
      this.threadRuns.set(run.threadId, run.id);
      run.status = "running";
      run.stage = options.adjustment ? "全体調整を実行しています" : "指示を実行しています";
      run.updatedAt = isoNow();
      const response = await this.client.request("turn/start", {
        threadId: run.threadId,
        approvalPolicy: "on-request",
        approvalsReviewer: "user",
        model: model.model ?? model.id,
        input: [
          { type: "skill", name: skill.name, path: skill.path },
          { type: "text", text: buildRunPrompt(run, options) },
        ],
        outputSchema: resultSchema,
      });
      run.turnId = response?.turn?.id;
      if (run.turnId) this.turnRuns.set(run.turnId, run.id);
    } catch (error) {
      this.failRun(run, error);
    }
  }

  adjust(runId, adjustment) {
    const current = this.runs.get(runId);
    if (!current || current.status !== "completed") throw new Error("完了した実行だけ調整できます");
    if (!adjustment?.trim()) throw new Error("調整内容がありません");
    return this.start({
      directiveId: current.directiveId,
      businessId: current.businessId,
      mode: current.mode,
      instruction: current.instruction,
      threadId: current.threadId,
      version: current.version + 1,
      adjustment,
      previousResult: JSON.stringify(current.result ?? parseStructuredResult(current.output)),
    });
  }

  async interrupt(runId) {
    const run = this.runs.get(runId);
    if (!run || !run.threadId || !run.turnId || terminalStatuses.has(run.status)) throw new Error("停止できる実行がありません");
    run.stage = "停止しています";
    run.updatedAt = isoNow();
    await this.client.request("turn/interrupt", { threadId: run.threadId, turnId: run.turnId });
    return this.publicRun(run);
  }

  onNotification(method, params) {
    const runId = this.turnRuns.get(params.turnId) ?? this.threadRuns.get(params.threadId);
    const run = runId ? this.runs.get(runId) : null;
    if (!run) return;
    run.updatedAt = isoNow();
    if (method === "item/agentMessage/delta") {
      run.output = `${run.output}${params.delta ?? ""}`.slice(-MAX_OUTPUT_CHARS);
    } else if (method === "turn/plan/updated") {
      run.plan = Array.isArray(params.plan) ? params.plan.slice(0, 20) : [];
      run.stage = params.explanation ? truncate(params.explanation, 300) : "計画に沿って進めています";
    } else if (method === "item/started") {
      run.stage = summarizeItem(params.item);
      run.progress.push({ at: isoNow(), label: run.stage, state: "running" });
    } else if (method === "item/completed") {
      run.progress.push({ at: isoNow(), label: summarizeItem(params.item), state: "completed" });
    } else if (method === "turn/diff/updated") {
      run.hasChanges = Boolean(params.diff?.trim());
    } else if (method === "error") {
      run.error = truncate(params.error?.message ?? "実行中に問題が発生しました", 1_000);
      run.stage = params.willRetry ? "問題を修正して再試行しています" : "実行に失敗しました";
    } else if (method === "turn/completed") {
      const turnStatus = params.turn?.status ?? "completed";
      run.status = turnStatus === "inProgress" ? "running" : turnStatus;
      run.stage = run.status === "completed" ? "実行が完了しました" : run.status === "interrupted" ? "実行を停止しました" : "実行に失敗しました";
      run.completedAt = isoNow();
      run.result = parseStructuredResult(run.output, run.status);
      if (run.status === "failed" && !run.error) run.error = params.turn?.error?.message ?? "Codexの実行に失敗しました";
      run.approvals.clear();
    }
  }

  async onServerRequest(message) {
    if (message.method === "item/tool/call") {
      return { success: false, contentItems: [{ type: "inputText", text: "実行司令室では未許可の動的ツールです" }] };
    }
    const params = message.params ?? {};
    const runId = this.turnRuns.get(params.turnId) ?? this.threadRuns.get(params.threadId);
    const run = runId ? this.runs.get(runId) : null;
    if (!run) return undefined;
    const requestId = String(message.id);
    const kind = approvalKind(message.method);
    if (kind === "unsupported") return this.defaultDenial(message.method);
    const publicApproval = {
      id: requestId,
      kind,
      title: kind === "command" ? "コマンド実行の確認" : kind === "file_change" ? "ファイル変更の確認" : kind === "permission" ? "追加権限の確認" : kind === "user_input" ? "Codexからの確認" : "外部連携の確認",
      reason: truncate(params.reason ?? "続行するには確認が必要です", 800),
      command: kind === "command" ? truncate(params.command ?? "", 2_000) : "",
      target: kind === "file_change" && params.grantRoot ? basename(params.grantRoot) : "",
      questions: kind === "user_input" ? (params.questions ?? []).map((question) => ({
        id: truncate(question.id, 100), header: truncate(question.header, 100), question: truncate(question.question, 500), options: question.options ?? null, isSecret: Boolean(question.isSecret),
      })) : [],
      permission: kind === "permission" ? params.permissions : null,
    };
    const pending = { rpcId: message.id, method: message.method, params, public: publicApproval };
    run.approvals.set(requestId, pending);
    this.pendingApprovals.set(`${run.id}:${requestId}`, { run, pending });
    run.status = "waiting_approval";
    run.stage = "あなたの確認を待っています";
    run.updatedAt = isoNow();
    return null;
  }

  defaultDenial(method) {
    if (method.includes("command") || method.includes("execCommand")) return { decision: "decline" };
    if (method.includes("file") || method.includes("Patch")) return { decision: "decline" };
    if (method.includes("permissions")) return { permissions: {}, scope: "turn" };
    if (method.includes("requestUserInput")) return { answers: {} };
    if (method.includes("elicitation")) return { action: "decline", content: null };
    return { success: false, contentItems: [{ type: "inputText", text: "未許可の要求です" }] };
  }

  async answerApproval(runId, requestId, action, answers = {}) {
    const record = this.pendingApprovals.get(`${runId}:${requestId}`);
    if (!record) throw new Error("確認要求が見つかりません");
    const { run, pending } = record;
    const kind = pending.public.kind;
    let result;
    if (kind === "command" || kind === "file_change") {
      result = { decision: action === "allow" ? "accept" : action === "cancel" ? "cancel" : "decline" };
    } else if (kind === "permission") {
      result = { permissions: action === "allow" ? (pending.params.permissions ?? {}) : {}, scope: "turn", strictAutoReview: false };
    } else if (kind === "user_input") {
      const normalized = {};
      for (const question of pending.params.questions ?? []) {
        const value = answers[question.id];
        normalized[question.id] = { answers: Array.isArray(value) ? value.map(String) : value ? [String(value)] : [] };
      }
      result = { answers: normalized };
    } else {
      result = { action: action === "allow" ? "accept" : action === "cancel" ? "cancel" : "decline", content: action === "allow" ? answers : null };
    }
    this.client.respond(pending.rpcId, result);
    run.approvals.delete(requestId);
    this.pendingApprovals.delete(`${runId}:${requestId}`);
    if (!run.approvals.size && !terminalStatuses.has(run.status)) {
      run.status = "running";
      run.stage = "確認結果を反映して続行しています";
    }
    run.updatedAt = isoNow();
    if (action === "cancel" && run.threadId && run.turnId) {
      await this.client.request("turn/interrupt", { threadId: run.threadId, turnId: run.turnId });
    }
    return this.publicRun(run);
  }

  failRun(run, error) {
    run.status = "failed";
    run.stage = "実行を開始できませんでした";
    run.error = truncate(error?.message ?? error, 1_000);
    run.completedAt = isoNow();
    run.updatedAt = isoNow();
    run.result = parseStructuredResult(run.output, "failed");
  }

  trimRuns() {
    if (this.runs.size <= 60) return;
    for (const [id, run] of this.runs) {
      if (terminalStatuses.has(run.status)) this.runs.delete(id);
      if (this.runs.size <= 50) break;
    }
  }
}

function sanitizeContentBrief(brief = {}) {
  const keys = ["topicOpen", "topicOrProblem", "audience", "sourceUrls", "operatorNotes", "confirmedFacts", "cta", "sourceContent", "targetAccount", "finalUrl"];
  return Object.fromEntries(keys.filter((key) => key in brief).map((key) => [key, key === "topicOpen" ? Boolean(brief[key]) : truncate(String(brief[key] ?? "").trim(), ["sourceContent", "operatorNotes"].includes(key) ? 12_000 : 3_000)]));
}

function validateContentInput(input) {
  const business = contentBusinesses.get(input?.businessId);
  if (!business) throw new Error("対象事業を最初に選び直してください");
  if (!new Set(["myblog", "myreel"]).has(input?.skill)) throw new Error("利用できる制作Skillではありません");
  const brief = sanitizeContentBrief(input.brief);
  if (input.skill === "myblog" && !brief.topicOpen && !brief.topicOrProblem) throw new Error("テーマまたは解決したい悩みを入力してください");
  if (input.skill === "myreel" && (!brief.sourceContent || !brief.targetAccount || !brief.finalUrl)) throw new Error("元になる内容、投稿先アカウント、確認済み最終URLが必要です");
  return { business, skill: input.skill, brief };
}

function buildContentDirective(run, continuation = "") {
  const stageInstruction = {
    topics: "テーマ未定として国内の直近7日・30日・90日の候補を調べ、指定Schemaの6〜8件だけを返してください。",
    titles: "指定されたテーマに対する仮タイトル案を、指定Schemaどおり必ず3件返してください。",
    h2: "選ばれたタイトルに対するH2グループを、各3〜5見出し、全体で必ず3グループ返してください。",
    review: "選ばれたH2グループで調査・本文・各H2画像案・最終タイトル再検討まで進め、最終確認用Schemaを返してください。HTML化やCMS保存はまだ行わないでください。",
    html: "これは最終確認後の指令です。clean HTMLとCMS payloadを返し、認証済み下書き保存が可能な場合だけdraftで保存してください。公開・予約は行わないでください。",
    "reel-set": "9:16全画面動画、中央の短文5つ、caption、Story短文、店舗commentを指定Schemaで返してください。まだ投稿しないでください。",
    "reel-publish-review": "投稿セット承認済みです。REELだけを投稿し、公開URLを確認したうえで、Story文と店舗commentの最終承認用Schemaを返してください。Story共有とcomment投稿はまだ行わないでください。",
    "reel-final": "Story文と店舗commentも最終承認済みです。同じ公開済みREELに実行し、それぞれの完了結果を報告してください。",
  }[run.stage] ?? "指定された工程をSkillの手順どおり進めてください。";
  return [
    `$${run.skill}`,
    `最初の指令：対象事業を「${run.businessName}」（${run.businessId}）として固定してください。このthreadでは別事業の声、出典、CTA、投稿先、保存先へ切り替えないでください。`,
    "実行司令室は非公開の制作管理面です。公開、SNS投稿、メール送信、課金、顧客データ変更は、その操作を示した明示承認がある工程まで実行しないでください。",
    stageInstruction,
    continuation ? `選択・追加指令：${truncate(continuation, 24_000)}` : "",
    `確認済み入力：${JSON.stringify(run.brief)}`,
  ].filter(Boolean).join("\n\n");
}

export class ContentExecutionManager {
  constructor(client, registry) {
    this.client = client;
    this.registry = registry;
    this.runs = new Map();
    this.threadRuns = new Map();
    this.turnRuns = new Map();
    this.pendingApprovals = new Map();
    this.load();
    client.setHandlers({
      onNotification: (method, params) => this.onNotification(method, params),
      onServerRequest: (message) => this.onServerRequest(message),
    });
  }

  load() {
    if (!existsSync(contentStatePath)) return;
    try {
      const saved = loadJson(contentStatePath);
      for (const item of saved.runs ?? []) {
        const run = { ...item, project: this.registry.lookup(item.businessId), approvals: new Map(), events: item.events ?? [], versions: item.versions ?? [] };
        this.runs.set(run.id, run);
        if (run.threadId) this.threadRuns.set(run.threadId, run.id);
        if (run.turnId) this.turnRuns.set(run.turnId, run.id);
      }
    } catch {}
  }

  save() {
    mkdirSync(dirname(contentStatePath), { recursive: true });
    const saved = [...this.runs.values()].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).slice(0, 100).map((run) => ({ ...this.publicRun(run), brief: run.brief, versions: run.versions }));
    writeFileSync(contentStatePath, JSON.stringify({ schemaVersion: 1, runs: saved }, null, 2), "utf8");
  }

  publicRun(run) {
    return {
      id: run.id, businessId: run.businessId, businessName: run.businessName, skill: run.skill, stage: run.stage,
      status: run.status, threadId: run.threadId, turnId: run.turnId, version: run.version, output: run.output,
      structuredOutput: run.structuredOutput, approvals: [...run.approvals.values()].map((approval) => approval.public),
      events: run.events.slice(-80), error: run.error, createdAt: run.createdAt, updatedAt: run.updatedAt,
    };
  }

  get(id) {
    const run = this.runs.get(id);
    return run ? this.publicRun(run) : null;
  }

  list(businessId = "") {
    return [...this.runs.values()].filter((run) => !businessId || run.businessId === businessId).sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).map((run) => this.publicRun(run));
  }

  start(input) {
    const { business, skill, brief } = validateContentInput(input);
    const project = this.registry.lookup(business.businessId);
    if (!project.available) throw new Error(`${business.displayName}: ${project.reason}`);
    const stage = skill === "myblog" ? (brief.topicOpen ? "topics" : "titles") : "reel-set";
    const run = {
      id: randomBytes(12).toString("base64url"), businessId: business.businessId, businessName: business.displayName, skill, brief, project,
      stage, status: "starting", threadId: null, turnId: null, version: 1, output: "", structuredOutput: null,
      approvals: new Map(), events: [], error: "", versions: [], createdAt: isoNow(), updatedAt: isoNow(),
    };
    this.runs.set(run.id, run);
    void this.launch(run, { resume: false });
    return this.publicRun(run);
  }

  async launch(run, { resume, continuation = "" }) {
    try {
      await this.client.ensureStarted();
      const skillResponse = await this.client.request("skills/list", { cwds: [run.project.root], forceReload: true });
      const skill = (skillResponse?.data ?? []).flatMap((entry) => entry.skills ?? []).find((item) => item.name === run.skill && item.enabled);
      if (!skill) throw new Error(`${run.skill} Skillを対象プロジェクトで読み込めませんでした`);
      const settings = { cwd: run.project.root, approvalPolicy: "on-request", approvalsReviewer: "user", sandbox: "workspace-write" };
      if (resume) await this.client.request("thread/resume", { threadId: run.threadId, ...settings });
      else {
        const response = await this.client.request("thread/start", settings);
        run.threadId = response?.thread?.id;
      }
      if (!run.threadId) throw new Error("Codex threadを開始できませんでした");
      this.threadRuns.set(run.threadId, run.id);
      run.status = "running";
      run.output = "";
      run.structuredOutput = null;
      run.error = "";
      run.updatedAt = isoNow();
      this.addEvent(run, "bridge/turn-started", `${run.stage}工程を開始`);
      const params = {
        threadId: run.threadId,
        approvalPolicy: "on-request",
        approvalsReviewer: "user",
        input: [{ type: "skill", name: skill.name, path: skill.path }, { type: "text", text: buildContentDirective(run, continuation) }],
      };
      if (STAGE_SCHEMAS[run.stage]) params.outputSchema = STAGE_SCHEMAS[run.stage];
      const response = await this.client.request("turn/start", params);
      run.turnId = response?.turn?.id;
      if (run.turnId) this.turnRuns.set(run.turnId, run.id);
      this.save();
    } catch (error) {
      run.status = "failed";
      run.error = truncate(error?.message ?? error, 1000);
      run.updatedAt = isoNow();
      this.save();
    }
  }

  addEvent(run, method, label) {
    run.events.push({ at: isoNow(), method, label: truncate(label, 500) });
    run.events = run.events.slice(-80);
  }

  continue(id, input) {
    const run = this.runs.get(id);
    if (!run || run.status !== "completed") throw new Error("完了した工程だけ次へ進めます");
    const nextStage = String(input.nextStage ?? "");
    if (!(NEXT_STAGES[run.stage] ?? []).includes(nextStage)) throw new Error(`${run.stage}から${nextStage}へは進めません`);
    const instruction = String(input.instruction ?? "").trim();
    if (!instruction) throw new Error("選択または承認内容がありません");
    run.versions.push({ version: run.version, stage: run.stage, output: run.output, structuredOutput: run.structuredOutput, savedAt: isoNow() });
    run.stage = nextStage;
    run.version += 1;
    run.status = "starting";
    run.updatedAt = isoNow();
    void this.launch(run, { resume: true, continuation: instruction });
    return this.publicRun(run);
  }

  adjust(id, instruction) {
    const run = this.runs.get(id);
    if (!run || run.status !== "completed") throw new Error("完了した成果物だけ全体調整できます");
    if (!String(instruction ?? "").trim()) throw new Error("全体調整プロンプトがありません");
    run.versions.push({ version: run.version, stage: run.stage, output: run.output, structuredOutput: run.structuredOutput, savedAt: isoNow() });
    run.version += 1;
    run.status = "starting";
    run.updatedAt = isoNow();
    const adjustment = ["全体調整です。事業、確認済み事実、出典、CTA、公開状態、承認段階は変更しないでください。", `調整指示：${truncate(instruction, 6000)}`, `現在の成果物：${truncate(run.output, 24_000)}`, "指定Schemaを保った改訂版を返してください。"].join("\n\n");
    void this.launch(run, { resume: true, continuation: adjustment });
    return this.publicRun(run);
  }

  async interrupt(id) {
    const run = this.runs.get(id);
    if (!run?.threadId || !run?.turnId || terminalStatuses.has(run.status)) throw new Error("停止できる制作がありません");
    await this.client.request("turn/interrupt", { threadId: run.threadId, turnId: run.turnId });
    run.status = "interrupted";
    run.updatedAt = isoNow();
    this.save();
    return this.publicRun(run);
  }

  onNotification(method, params) {
    const runId = this.turnRuns.get(params.turnId) ?? this.threadRuns.get(params.threadId);
    const run = runId ? this.runs.get(runId) : null;
    if (!run) return;
    run.updatedAt = isoNow();
    if (method === "item/agentMessage/delta") run.output = `${run.output}${params.delta ?? ""}`.slice(-MAX_OUTPUT_CHARS);
    else if (method === "item/started") this.addEvent(run, method, summarizeItem(params.item));
    else if (method === "item/completed") this.addEvent(run, method, `${summarizeItem(params.item)}・完了`);
    else if (method === "error") { run.error = truncate(params.error?.message ?? "実行中に問題が発生しました", 1000); this.addEvent(run, method, run.error); }
    else if (method === "turn/completed") {
      run.status = params.turn?.status === "completed" ? "completed" : params.turn?.status ?? "failed";
      run.structuredOutput = parseStructuredResult(run.output, run.status);
      run.approvals.clear();
      this.addEvent(run, method, run.status === "completed" ? "工程が完了しました" : "工程を完了できませんでした");
      this.save();
    }
  }

  async onServerRequest(message) {
    const params = message.params ?? {};
    const runId = this.turnRuns.get(params.turnId) ?? this.threadRuns.get(params.threadId);
    const run = runId ? this.runs.get(runId) : null;
    if (!run) return undefined;
    const kind = approvalKind(message.method);
    if (kind === "unsupported") return { success: false, contentItems: [{ type: "inputText", text: "制作Studioでは未許可の要求です" }] };
    const requestId = String(message.id);
    const publicApproval = {
      requestId, method: message.method,
      summary: truncate(JSON.stringify({ reason: params.reason ?? "続行確認", command: kind === "command" ? params.command ?? "" : "", target: kind === "file_change" ? basename(params.grantRoot ?? "") : "" }, null, 2), 4000),
    };
    const pending = { rpcId: message.id, method: message.method, params, kind, public: publicApproval };
    run.approvals.set(requestId, pending);
    this.pendingApprovals.set(`${run.id}:${requestId}`, { run, pending });
    run.status = "waiting_approval";
    this.addEvent(run, message.method, "承認が必要です");
    return null;
  }

  async answerApproval(runId, requestId, action) {
    const record = this.pendingApprovals.get(`${runId}:${requestId}`);
    if (!record) throw new Error("承認要求が見つかりません");
    const { run, pending } = record;
    let result;
    if (pending.kind === "command" || pending.kind === "file_change") result = { decision: action === "allow" ? "accept" : action === "cancel" ? "cancel" : "decline" };
    else if (pending.kind === "permission") result = { permissions: {}, scope: "turn", strictAutoReview: false };
    else if (pending.kind === "user_input") result = { answers: {} };
    else result = { action: "decline", content: null };
    this.client.respond(pending.rpcId, result);
    run.approvals.delete(requestId);
    this.pendingApprovals.delete(`${runId}:${requestId}`);
    run.status = "running";
    run.updatedAt = isoNow();
    if (action === "cancel" && run.threadId && run.turnId) await this.client.request("turn/interrupt", { threadId: run.threadId, turnId: run.turnId });
    return this.publicRun(run);
  }

  async status() {
    await this.client.ensureStarted();
    const [account, skills] = await Promise.all([
      this.client.request("account/read", { refreshToken: false }),
      this.client.request("skills/list", { cwds: [commandRoomRoot], forceReload: true }),
    ]);
    const availableSkills = (skills?.data ?? []).flatMap((entry) => entry.skills ?? []);
    return {
      connected: true, codexCliVersion: CODEX_SCHEMA_VERSION,
      account: { connected: Boolean(account?.account), type: account?.account?.type ?? null, planType: account?.account?.planType ?? null },
      skills: ["myblog", "myreel"].map((name) => ({ name, enabled: availableSkills.some((skill) => skill.name === name && skill.enabled) })),
    };
  }
}

class RateLimiter {
  constructor() { this.entries = new Map(); }
  allow(key, limit, windowMs) {
    const now = Date.now();
    const current = this.entries.get(key);
    if (!current || current.resetAt < now) {
      this.entries.set(key, { count: 1, resetAt: now + windowMs });
      return true;
    }
    current.count += 1;
    return current.count <= limit;
  }
}

async function readBody(request) {
  const declared = Number(request.headers["content-length"] ?? 0);
  if (declared > MAX_BODY_BYTES) throw new Error("request_too_large");
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new Error("request_too_large");
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function corsHeaders(origin) {
  return {
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "authorization, content-type, x-command-room-csrf",
    "access-control-allow-private-network": "true",
    "access-control-max-age": "600",
    "cache-control": "no-store",
    "cross-origin-resource-policy": "cross-origin",
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    vary: "Origin",
  };
}

function sendJson(response, status, data, origin) {
  const body = JSON.stringify(data);
  response.writeHead(status, { ...corsHeaders(origin), "content-type": "application/json; charset=utf-8", "content-length": Buffer.byteLength(body) });
  response.end(body);
}

export function createBridgeServer({ manager, contentManager, registry, authority, ownerVerifier = new OwnerAssertionVerifier(), onPairCode = () => {} }) {
  const limiter = new RateLimiter();
  return createServer(async (request, response) => {
    const origin = request.headers.origin ?? "";
    if (!isAllowedOrigin(origin)) {
      response.writeHead(403, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
      response.end(JSON.stringify({ error: "origin_not_allowed" }));
      return;
    }
    if (request.method === "OPTIONS") {
      response.writeHead(204, corsHeaders(origin));
      response.end();
      return;
    }
    const url = new URL(request.url ?? "/", "http://127.0.0.1");
    const remote = request.socket.remoteAddress ?? "loopback";
    try {
      if (request.method === "GET" && url.pathname === "/v1/health") {
        sendJson(response, 200, { ok: true, bridgeVersion: BRIDGE_VERSION, codexSchemaVersion: CODEX_SCHEMA_VERSION, connected: false, projects: registry.publicList() }, origin);
        return;
      }
      if (request.method === "POST" && url.pathname === "/v1/pair") {
        if (!limiter.allow(`pair:${remote}`, 10, 60_000)) return sendJson(response, 429, { error: "too_many_attempts" }, origin);
        const body = await readBody(request);
        const credential = authority.pair(String(body.code ?? ""), origin);
        if (!credential) return sendJson(response, 401, { error: "invalid_pairing_code" }, origin);
        onPairCode(authority.code);
        sendJson(response, 200, { ok: true, ...credential, projects: registry.publicList() }, origin);
        return;
      }
      if (request.method === "POST" && url.pathname === "/v1/auto-pair") {
        if (!limiter.allow(`auto-pair:${remote}`, 12, 60_000)) return sendJson(response, 429, { error: "too_many_attempts" }, origin);
        const body = await readBody(request);
        const owner = ownerVerifier.verify(body.assertion, origin);
        if (!owner) return sendJson(response, 401, { error: "invalid_owner_assertion" }, origin);
        return sendJson(response, 200, { ok: true, ...authority.issue(origin), owner: owner.email, projects: registry.publicList() }, origin);
      }
      if (!authority.authenticate(request.headers.authorization, request.headers["x-command-room-csrf"], origin)) {
        return sendJson(response, 401, { error: "bridge_auth_required" }, origin);
      }
      if (!limiter.allow(`api:${remote}`, 180, 60_000)) return sendJson(response, 429, { error: "too_many_requests" }, origin);

      if (request.method === "GET" && url.pathname === "/v1/content/status" && contentManager) {
        return sendJson(response, 200, await contentManager.status(), origin);
      }
      if (request.method === "POST" && url.pathname === "/v1/account/login" && contentManager) {
        await contentManager.client.ensureStarted();
        return sendJson(response, 200, await contentManager.client.request("account/login/start", { type: "chatgpt" }), origin);
      }
      if (request.method === "POST" && url.pathname === "/v1/account/logout" && contentManager) {
        await contentManager.client.request("account/logout", undefined);
        return sendJson(response, 200, { ok: true }, origin);
      }
      if (request.method === "GET" && url.pathname === "/v1/content-runs" && contentManager) {
        return sendJson(response, 200, { runs: contentManager.list(url.searchParams.get("businessId") ?? "") }, origin);
      }
      if (request.method === "POST" && url.pathname === "/v1/content-runs" && contentManager) {
        return sendJson(response, 202, contentManager.start(await readBody(request)), origin);
      }
      const contentRunMatch = url.pathname.match(/^\/v1\/content-runs\/([A-Za-z0-9_-]+)$/);
      if (request.method === "GET" && contentRunMatch && contentManager) {
        const run = contentManager.get(contentRunMatch[1]);
        return sendJson(response, run ? 200 : 404, run ?? { error: "run_not_found" }, origin);
      }
      const contentContinueMatch = url.pathname.match(/^\/v1\/content-runs\/([A-Za-z0-9_-]+)\/continue$/);
      if (request.method === "POST" && contentContinueMatch && contentManager) {
        return sendJson(response, 202, contentManager.continue(contentContinueMatch[1], await readBody(request)), origin);
      }
      const contentAdjustMatch = url.pathname.match(/^\/v1\/content-runs\/([A-Za-z0-9_-]+)\/adjust$/);
      if (request.method === "POST" && contentAdjustMatch && contentManager) {
        const body = await readBody(request);
        return sendJson(response, 202, contentManager.adjust(contentAdjustMatch[1], body.instruction), origin);
      }
      const contentInterruptMatch = url.pathname.match(/^\/v1\/content-runs\/([A-Za-z0-9_-]+)\/interrupt$/);
      if (request.method === "POST" && contentInterruptMatch && contentManager) {
        return sendJson(response, 200, await contentManager.interrupt(contentInterruptMatch[1]), origin);
      }
      const contentApprovalMatch = url.pathname.match(/^\/v1\/content-runs\/([A-Za-z0-9_-]+)\/approvals\/([^/]+)$/);
      if (request.method === "POST" && contentApprovalMatch && contentManager) {
        const body = await readBody(request);
        return sendJson(response, 200, await contentManager.answerApproval(contentApprovalMatch[1], decodeURIComponent(contentApprovalMatch[2]), body.action), origin);
      }

      if (request.method === "POST" && (url.pathname === "/v1/runs" || url.pathname === "/v1/runs/resume")) {
        const body = await readBody(request);
        const run = manager.start(body);
        return sendJson(response, 202, run, origin);
      }
      const runMatch = url.pathname.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)$/);
      if (request.method === "GET" && runMatch) {
        const run = manager.get(runMatch[1]);
        return sendJson(response, run ? 200 : 404, run ?? { error: "run_not_found" }, origin);
      }
      const approvalMatch = url.pathname.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)\/approvals\/([^/]+)$/);
      if (request.method === "POST" && approvalMatch) {
        const body = await readBody(request);
        const run = await manager.answerApproval(approvalMatch[1], decodeURIComponent(approvalMatch[2]), body.action, body.answers ?? {});
        return sendJson(response, 200, run, origin);
      }
      const interruptMatch = url.pathname.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)\/interrupt$/);
      if (request.method === "POST" && interruptMatch) {
        const run = await manager.interrupt(interruptMatch[1]);
        return sendJson(response, 200, run, origin);
      }
      const adjustMatch = url.pathname.match(/^\/v1\/runs\/([A-Za-z0-9_-]+)\/adjust$/);
      if (request.method === "POST" && adjustMatch) {
        const body = await readBody(request);
        const run = manager.adjust(adjustMatch[1], String(body.adjustment ?? ""));
        return sendJson(response, 202, run, origin);
      }
      return sendJson(response, 404, { error: "not_found" }, origin);
    } catch (error) {
      const status = error?.message === "request_too_large" ? 413 : error instanceof SyntaxError ? 400 : 422;
      return sendJson(response, status, { error: truncate(error?.message ?? "bridge_error", 500) }, origin);
    }
  });
}

export async function startBridge(options = {}) {
  if (!existsSync(commandSkillPath)) throw new Error("command-room-executor skill is missing");
  const registry = options.registry ?? new ProjectRegistry(loadProjectConfig());
  const authority = options.authority ?? new PairingAuthority();
  const client = options.client ?? new AppServerClient();
  const manager = options.manager ?? new ExecutionManager(client, registry);
  const contentManager = options.contentManager ?? new ContentExecutionManager(client, registry);
  const showPairCode = (code) => {
    process.stdout.write(`\n実行司令室の接続コード: ${code}\n`);
    process.stdout.write("このコードを実行司令室の『このPCと接続』へ入力してください。\n");
  };
  const server = createBridgeServer({ manager, contentManager, registry, authority, ownerVerifier: options.ownerVerifier, onPairCode: showPairCode });
  const port = Number(options.port ?? process.env.COMMAND_ROOM_BRIDGE_PORT ?? DEFAULT_PORT);
  await new Promise((resolveListen, rejectListen) => {
    server.once("error", rejectListen);
    server.listen(port, "127.0.0.1", resolveListen);
  });
  process.stdout.write(`実行司令室 Codex bridge ${BRIDGE_VERSION} を 127.0.0.1:${port} で起動しました。\n`);
  process.stdout.write(`Codex App Server Schema: ${CODEX_SCHEMA_VERSION}\n`);
  showPairCode(authority.code);
  const relay = options.relay ?? new SitesRelayClient({ authority, manager });
  relay.start();
  const shutdown = () => {
    server.close();
    relay.close();
    client.close();
  };
  process.once("SIGINT", shutdown);
  process.once("SIGTERM", shutdown);
  return { server, client, manager, contentManager, registry, authority, relay };
}

const isMain = process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url;
if (isMain) {
  startBridge().catch((error) => {
    process.stderr.write(`実行司令室の接続を開始できませんでした: ${error.message}\n`);
    process.exitCode = 1;
  });
}
