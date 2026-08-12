import { existsSync, rmSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const output = join(root, ".market-test-dist");
if (existsSync(output)) rmSync(output, { recursive: true, force: true });
const compiler = join(root, "node_modules", "typescript", "bin", "tsc");
const compiled = spawnSync(process.execPath, [compiler, "-p", "tsconfig.market-tests.json"], { cwd: root, stdio: "inherit" });
if (compiled.status !== 0) process.exit(compiled.status ?? 1);
const tested = spawnSync(process.execPath, ["--test", join(output, "tests", "market-compass-runtime.test.js")], { cwd: root, stdio: "inherit" });
process.exit(tested.status ?? 1);

