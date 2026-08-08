import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import test from "node:test";
import {
  ExecutionManager,
  OwnerAssertionVerifier,
  PairingAuthority,
  ProjectRegistry,
  SitesRelayClient,
  appServerChildEnvironment,
  buildRunPrompt,
  createBridgeServer,
  isAllowedOrigin,
  parseStructuredResult,
  pickCompatibleModel,
} from "./bridge.mjs";

test("production and loopback origins only are allowed", () => {
  assert.equal(isAllowedOrigin("https://ai-hub-jp.vercel.app"), true);
  assert.equal(isAllowedOrigin("http://127.0.0.1:3000"), true);
  assert.equal(isAllowedOrigin("https://example.com"), false);
});

test("Codex child process never inherits relay authentication secrets", () => {
  const environment = appServerChildEnvironment({
    PATH: "test-path",
    COMMAND_ROOM_BRIDGE_AUTH_SECRET: "bridge-secret",
    COMMAND_CENTER_SERVICE_TOKEN: "service-secret",
  });
  assert.equal(environment.PATH, "test-path");
  assert.equal(environment.COMMAND_ROOM_BRIDGE_AUTH_SECRET, undefined);
  assert.equal(environment.COMMAND_CENTER_SERVICE_TOKEN, undefined);
});

test("project registry exposes availability without returning paths", () => {
  const registry = new ProjectRegistry({ projects: { ok: { folder: "ok" }, missing: { folder: "missing" }, unsafe: { folder: "..\\outside" } } }, {
    commandRoot: "C:\\Project\\実行司令室",
    projectsRoot: "C:\\Project",
    exists: (path) => path.endsWith("\\ok"),
  });
  assert.equal(registry.lookup("ok").available, true);
  assert.equal(registry.lookup("missing").available, false);
  assert.equal(registry.lookup("unsafe").available, false);
  assert.deepEqual(Object.keys(registry.publicList()[0]).sort(), ["available", "businessId", "reason"]);
});

test("pairing code is one-use and credentials are bound to an origin", () => {
  let now = 1_000;
  let codeIndex = 0;
  const codes = ["123456", "654321"];
  let tokenIndex = 0;
  const authority = new PairingAuthority({ now: () => now, codeFactory: () => codes[codeIndex++], tokenFactory: () => `token-${tokenIndex++}` });
  const credential = authority.pair("123456", "http://localhost:3000");
  assert.ok(credential);
  assert.equal(authority.pair("123456", "http://localhost:3000"), null);
  assert.equal(authority.authenticate(`Bearer ${credential.token}`, credential.csrf, "http://localhost:3000"), true);
  assert.equal(authority.authenticate(`Bearer ${credential.token}`, credential.csrf, "http://localhost:4000"), false);
  now += 8 * 60 * 60_000 + 1;
  assert.equal(authority.authenticate(`Bearer ${credential.token}`, credential.csrf, "http://localhost:3000"), false);
});

function ownerAssertion(secret, payload) {
  const encoded = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const signature = createHmac("sha256", secret).update(encoded).digest("base64url");
  return `${encoded}.${signature}`;
}

test("owner assertion is short-lived, origin-bound, and one-use", () => {
  const now = Date.parse("2026-07-24T00:00:00.000Z");
  const origin = "https://ai-hub-jp.vercel.app";
  const secret = "test-secret";
  const verifier = new OwnerAssertionVerifier({ secret, now: () => now, ownerEmail: "goodbouldering@gmail.com" });
  const assertion = ownerAssertion(secret, {
    v: 1,
    aud: "execution-command-room-bridge",
    sub: "goodbouldering@gmail.com",
    origin,
    iat: Math.floor(now / 1_000),
    exp: Math.floor(now / 1_000) + 60,
    nonce: "nonce-1",
  });
  assert.equal(verifier.verify(assertion, origin)?.email, "goodbouldering@gmail.com");
  assert.equal(verifier.verify(assertion, origin), null);
  assert.equal(verifier.verify(ownerAssertion(secret, {
    v: 1,
    aud: "execution-command-room-bridge",
    sub: "goodbouldering@gmail.com",
    origin,
    iat: Math.floor(now / 1_000),
    exp: Math.floor(now / 1_000) + 60,
    nonce: "nonce-2",
  }), "https://example.com"), null);
});

test("Sites relay signs outbound heartbeat and completes only dispatched requests", async () => {
  const secret = "relay-test-secret";
  const calls = [];
  const fetchStub = async (_url, options) => {
    const body = JSON.parse(options.body);
    const timestamp = options.headers["x-command-room-relay-timestamp"];
    const expected = createHmac("sha256", secret).update(`${timestamp}.${options.body}`).digest("base64url");
    assert.equal(options.headers["x-command-room-relay-signature"], expected);
    assert.equal(typeof body.nonce, "string");
    calls.push(body);
    if (body.action === "heartbeat") {
      return Response.json({
        ok: true,
        rotatePairCode: false,
        requests: [{ id: "request-1", method: "GET", path: "/v1/runs/run-1", body: {} }],
      });
    }
    return Response.json({ ok: true });
  };
  const relay = new SitesRelayClient({
    secret,
    fetch: fetchStub,
    authority: {
      code: "123456",
      codeExpiresAt: Date.now() + 60_000,
      now: () => Date.now(),
      rotateCode() {},
    },
    manager: { get: () => ({ id: "run-1", status: "completed" }) },
  });
  await relay.tick();
  assert.equal(calls[0].action, "heartbeat");
  assert.equal(calls[0].bridge.transport, "outbound-sites-relay");
  assert.equal(calls[1].action, "complete");
  assert.equal(calls[1].requestId, "request-1");
  assert.equal(calls[1].statusCode, 200);
  assert.equal(calls[1].response.id, "run-1");
});

test("HTTP bridge requires origin, pairing capability, and CSRF", async () => {
  const authority = new PairingAuthority({ codeFactory: () => "123456", tokenFactory: (() => { let index = 0; return () => `http-token-${index++}`; })() });
  const registry = { publicList: () => [{ businessId: "trust", available: true, reason: null }] };
  const manager = {
    start: (body) => ({ id: "run-http", status: "starting", ...body }),
    get: () => null,
  };
  const server = createBridgeServer({ manager, registry, authority });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  const origin = "http://localhost:3000";
  const base = `http://127.0.0.1:${address.port}`;
  try {
    const forbidden = await fetch(`${base}/v1/health`, { headers: { origin: "https://example.com" } });
    assert.equal(forbidden.status, 403);
    const pair = await fetch(`${base}/v1/pair`, { method: "POST", headers: { origin, "content-type": "application/json" }, body: JSON.stringify({ code: "123456" }) });
    assert.equal(pair.status, 200);
    const credential = await pair.json();
    const unauthenticated = await fetch(`${base}/v1/runs`, { method: "POST", headers: { origin, "content-type": "application/json" }, body: "{}" });
    assert.equal(unauthenticated.status, 401);
    const started = await fetch(`${base}/v1/runs`, {
      method: "POST",
      headers: { origin, "content-type": "application/json", authorization: `Bearer ${credential.token}`, "x-command-room-csrf": credential.csrf },
      body: JSON.stringify({ directiveId: "d1", businessId: "trust", mode: "research", instruction: "確認" }),
    });
    assert.equal(started.status, 202);
    assert.equal((await started.json()).id, "run-http");
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("HTTP bridge accepts an owner assertion without exposing the shared secret", async () => {
  const now = Date.parse("2026-07-24T00:00:00.000Z");
  const origin = "https://ai-hub-jp.vercel.app";
  const secret = "http-owner-secret";
  const authority = new PairingAuthority({ now: () => now, codeFactory: () => "123456", tokenFactory: (() => { let index = 0; return () => `owner-token-${index++}`; })() });
  const ownerVerifier = new OwnerAssertionVerifier({ secret, now: () => now, ownerEmail: "goodbouldering@gmail.com" });
  const registry = { publicList: () => [] };
  const manager = { start: () => ({ id: "unused" }), get: () => null };
  const server = createBridgeServer({ manager, registry, authority, ownerVerifier });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const assertion = ownerAssertion(secret, {
      v: 1,
      aud: "execution-command-room-bridge",
      sub: "goodbouldering@gmail.com",
      origin,
      iat: Math.floor(now / 1_000),
      exp: Math.floor(now / 1_000) + 60,
      nonce: "http-nonce",
    });
    const paired = await fetch(`${base}/v1/auto-pair`, {
      method: "POST",
      headers: { origin, "content-type": "application/json" },
      body: JSON.stringify({ assertion }),
    });
    assert.equal(paired.status, 200);
    const credential = await paired.json();
    assert.equal(typeof credential.token, "string");
    assert.equal(Object.hasOwn(credential, "secret"), false);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("execution prompt and structured fallback keep execution boundaries explicit", () => {
  const prompt = buildRunPrompt({ businessId: "trust", mode: "implement", instruction: "予約導線を直す" });
  assert.match(prompt, /対象事業ID: trust/);
  assert.match(prompt, /実際に進めてください/);
  const parsed = parseStructuredResult('{"status":"completed","summary":"完了"}');
  assert.equal(parsed.summary, "完了");
  const fallback = parseStructuredResult("plain result", "failed");
  assert.equal(fallback.status, "partial");
});

test("the bridge prefers the current Sol model", () => {
  const model = pickCompatibleModel([
    { id: "gpt-5.6-sol", model: "gpt-5.6-sol", hidden: false },
    { id: "gpt-5.5", model: "gpt-5.5", hidden: false },
  ]);
  assert.equal(model.id, "gpt-5.6-sol");
});

class FakeClient {
  constructor() { this.calls = []; this.responses = []; }
  setHandlers(handlers) { this.handlers = handlers; }
  async ensureStarted() {}
  async request(method, params) {
    this.calls.push({ method, params });
    if (method === "skills/list") return { data: [{ cwd: params.cwds[0], errors: [], skills: [{ name: "command-room-executor", path: "C:\\skill\\SKILL.md", enabled: true }] }] };
    if (method === "model/list") return { data: [{ id: "gpt-5.5", model: "gpt-5.5", hidden: false, isDefault: true }] };
    if (method === "thread/start") return { thread: { id: "thread-1" } };
    if (method === "thread/resume") return { thread: { id: params.threadId } };
    if (method === "turn/start") return { turn: { id: `turn-${this.calls.filter((call) => call.method === "turn/start").length}` } };
    return {};
  }
  respond(id, result) { this.responses.push({ id, result }); }
}

async function waitFor(check, timeout = 1_000) {
  const started = Date.now();
  while (!check()) {
    if (Date.now() - started > timeout) throw new Error("condition timed out");
    await new Promise((resolve) => setTimeout(resolve, 5));
  }
}

test("execution manager starts a skill turn, pauses for approval, and captures the result", async () => {
  const client = new FakeClient();
  const registry = { lookup: () => ({ businessId: "trust", available: true, root: "C:\\Project\\トラスト" }) };
  const manager = new ExecutionManager(client, registry, { skillPath: "C:\\skill\\SKILL.md" });
  const started = manager.start({ directiveId: "directive-1", businessId: "trust", mode: "implement", instruction: "導線を改善する" });
  await waitFor(() => manager.get(started.id)?.turnId);
  const running = manager.get(started.id);
  assert.equal(running.status, "running");
  const turnCall = client.calls.find((call) => call.method === "turn/start");
  assert.equal(turnCall.params.input[0].type, "skill");
  assert.equal(turnCall.params.approvalPolicy, "on-request");

  await client.handlers.onServerRequest({ id: 77, method: "item/commandExecution/requestApproval", params: { threadId: "thread-1", turnId: running.turnId, command: "npm test", reason: "検証" } });
  assert.equal(manager.get(started.id).status, "waiting_approval");
  await manager.answerApproval(started.id, "77", "allow");
  assert.deepEqual(client.responses[0], { id: 77, result: { decision: "accept" } });

  client.handlers.onNotification("item/agentMessage/delta", { threadId: "thread-1", turnId: running.turnId, delta: '{"status":"completed","summary":"導線を改善","details":[],"artifacts":[],"verification":["test"],"nextActions":[],"requiresApproval":false}' });
  client.handlers.onNotification("turn/completed", { threadId: "thread-1", turn: { id: running.turnId, status: "completed" } });
  const completed = manager.get(started.id);
  assert.equal(completed.status, "completed");
  assert.equal(completed.result.summary, "導線を改善");

  const adjusted = manager.adjust(started.id, "見出しを短くする");
  await waitFor(() => manager.get(adjusted.id)?.turnId);
  assert.equal(manager.get(adjusted.id).version, 2);
  assert.ok(client.calls.some((call) => call.method === "thread/resume"));
});
