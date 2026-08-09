import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

test("PC Codex bridge is relocated to AI相談 and targets the protected relay", async () => {
  const bridge = await readFile(new URL("bridge/bridge.mjs", root), "utf8");
  await access(new URL("bridge/contracts.mjs", root));
  await access(new URL(".agents/skills/command-room-executor/SKILL.md", root));
  assert.match(bridge, /COMMAND_ROOM_ORIGIN\s*=\s*"https:\/\/ai-hub-jp\.vercel\.app"/);
  assert.match(bridge, /\/api\/admin\/command-center\/relay/);
  assert.doesNotMatch(bridge, /climbing-consult-daily-command\.goodbouldering\.chatgpt\.site/);
  assert.match(bridge, /SAFE_APP_SERVER_ENVIRONMENT_KEYS/);
  assert.doesNotMatch(bridge, /const childEnvironment = \{ \.\.\.source \}/);
});

test("bridge base configuration contains no credential material", async () => {
  const projects = await readFile(new URL("bridge/projects.json", root), "utf8");
  const businesses = await readFile(new URL("bridge/businesses.json", root), "utf8");
  assert.doesNotMatch(`${projects}\n${businesses}`, /secret|token|password|BEGIN [A-Z ]+ KEY/i);
});
