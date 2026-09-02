import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.cwd();
const policyRelativePath = ".github/deployment-platform.json";
const policyPath = join(root, policyRelativePath);
const guardWorkflowName = "cloudflare-deployment-guard.yml";
const errors = [];
const warnings = [];
let repositoryPolicy;

function annotation(kind, message, file, line) {
  const location = file ? ` file=${file}${line ? `,line=${line}` : ""}` : "";
  if (process.env.GITHUB_ACTIONS === "true") {
    console.log(`::${kind}${location}::${message}`);
  } else {
    console.log(`${kind.toUpperCase()}: ${file ? `${file}${line ? `:${line}` : ""}: ` : ""}${message}`);
  }
}

function addError(message, file, line) {
  errors.push({ message, file, line });
}

function addWarning(message, file, line) {
  warnings.push({ message, file, line });
}

function findLine(contents, pattern) {
  const index = contents.split(/\r?\n/).findIndex((line) => pattern.test(line));
  return index >= 0 ? index + 1 : undefined;
}

function workflowFiles(directory) {
  if (!existsSync(directory)) return [];
  return readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isFile() && /\.ya?ml$/i.test(entry.name))
    .map((entry) => join(directory, entry.name));
}

if (!existsSync(policyPath)) {
  addError("Cloudflare deployment policy is missing.", policyRelativePath);
} else {
  let policy;
  try {
    policy = JSON.parse(readFileSync(policyPath, "utf8"));
  } catch (error) {
    addError(`Cloudflare deployment policy is invalid JSON: ${error.message}`, policyRelativePath);
  }

  if (policy) {
    repositoryPolicy = policy;
    const validStatuses = new Set(["active", "partial_migration", "migration_required", "not_applicable"]);
    if (policy.version !== 1) addError("Policy version must be 1.", policyRelativePath);
    if (policy.platform !== "cloudflare") addError("Deployment platform must be cloudflare.", policyRelativePath);
    if (!validStatuses.has(policy.status)) addError("Policy status is invalid.", policyRelativePath);

    const cloudflare = policy.cloudflare ?? {};
    if (policy.status === "active" && cloudflare.ready !== true) {
      addError("An active repository must be Cloudflare-ready.", policyRelativePath);
    }
    if ((policy.status === "partial_migration" || policy.status === "migration_required") && !policy.nextAction) {
      addError("An incomplete migration must include nextAction.", policyRelativePath);
    }
    if (policy.status === "partial_migration") {
      addWarning(`Cloudflare migration is partial. Next action: ${policy.nextAction}`, policyRelativePath);
    }
    if (policy.status === "migration_required") {
      addWarning(`Cloudflare migration required. Next action: ${policy.nextAction}`, policyRelativePath);
    }

    if (cloudflare.ready === true) {
      if (!["public", "private"].includes(cloudflare.exposure)) {
        addError("Cloudflare exposure must be public or private when ready is true.", policyRelativePath);
      }
      if (!cloudflare.configPath || !existsSync(join(root, cloudflare.configPath))) {
        addError(`Cloudflare config does not exist: ${cloudflare.configPath ?? "(not set)"}`, policyRelativePath);
      }
      if (!cloudflare.deployCommand) {
        addError("Cloudflare deployCommand is required when ready is true.", policyRelativePath);
      } else if (/\bvercel\b/i.test(cloudflare.deployCommand)) {
        addError("Cloudflare deployCommand must not invoke Vercel.", policyRelativePath);
      }
      if (cloudflare.exposure === "public" && !/^https:\/\//i.test(cloudflare.productionUrl ?? "")) {
        addError("Cloudflare productionUrl must be an HTTPS URL when ready is true.", policyRelativePath);
      }
      if (cloudflare.exposure === "private" && !cloudflare.verificationCommand) {
        addError("A private Cloudflare Worker must include verificationCommand.", policyRelativePath);
      }
    }

    const legacy = policy.legacyVercel ?? {};
    const retainedFiles = new Set((legacy.retainedFiles ?? []).map((file) => file.replaceAll("\\", "/")));
    const rootVercelConfig = "vercel.json";
    if (existsSync(join(root, rootVercelConfig))) {
      if (legacy.gitIntegration !== "disconnected" || !retainedFiles.has(rootVercelConfig)) {
        addError("vercel.json remains without an explicit disconnected read-only exception.", rootVercelConfig);
      } else {
        addWarning("Legacy Vercel file retained for read-only migration reference; remove it after runtime parity is complete.", rootVercelConfig);
      }
    }
    for (const retainedFile of retainedFiles) {
      if (existsSync(join(root, retainedFile)) && retainedFile !== rootVercelConfig) {
        addWarning("Legacy Vercel file retained for read-only migration reference.", retainedFile);
      }
    }
  }
}

const packagePath = join(root, "package.json");
if (existsSync(packagePath)) {
  const contents = readFileSync(packagePath, "utf8");
  try {
    const pkg = JSON.parse(contents);
    for (const [name, command] of Object.entries(pkg.scripts ?? {})) {
      if (typeof command !== "string" || command.includes("--no-vercel")) continue;
      const line = findLine(contents, new RegExp(`"${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`));
      if (/(?<![\w./@-])vercel(?:\.cmd)?(?=\s|$)|\bVERCEL_(?:TOKEN|ORG_ID|PROJECT_ID)\b/i.test(command)) {
        addError(`Active Vercel command remains in package script "${name}". Replace it with Cloudflare.`, "package.json", findLine(contents, new RegExp(`"${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`)));
      } else if (/\.vercel\.app\b/i.test(command)) {
        if (["partial_migration", "migration_required"].includes(repositoryPolicy?.status)) {
          addWarning(`Legacy Vercel runtime reference remains in package script "${name}" during migration.`, "package.json", line);
        } else {
          addError(`Vercel runtime URL remains in package script "${name}". Replace it with Cloudflare.`, "package.json", line);
        }
      }
    }
    for (const section of ["dependencies", "devDependencies", "optionalDependencies"]) {
      for (const dependency of Object.keys(pkg[section] ?? {})) {
        if (dependency === "vercel") {
          addWarning(`Legacy Vercel CLI dependency remains in ${section}; remove it when no migration tooling needs it.`, "package.json", findLine(contents, /"vercel"/));
        }
      }
    }
  } catch (error) {
    addError(`package.json is invalid JSON: ${error.message}`, "package.json");
  }
}

const activeWorkflowPattern = /vercel-action|\bvercel(?:\.cmd)?\s+(?:deploy|link|build|pull|env|projects?|api|ls|inspect|rollback|redeploy)\b|\bVERCEL_(?:TOKEN|ORG_ID|PROJECT_ID)\b/i;
const runtimeWorkflowPattern = /\.vercel\.app\b/i;
for (const workflowPath of workflowFiles(join(root, ".github", "workflows"))) {
  if (workflowPath.endsWith(guardWorkflowName)) continue;
  const contents = readFileSync(workflowPath, "utf8");
  const lines = contents.split(/\r?\n/);
  lines.forEach((line, index) => {
    const activeLine = line.trimStart();
    if (!activeLine.startsWith("#") && !activeLine.includes("--no-vercel") && activeWorkflowPattern.test(activeLine)) {
      addError("Workflow still references Vercel. Replace this step, secret, or URL with Cloudflare.", relative(root, workflowPath).replaceAll("\\", "/"), index + 1);
    } else if (!activeLine.startsWith("#") && runtimeWorkflowPattern.test(activeLine)) {
      const file = relative(root, workflowPath).replaceAll("\\", "/");
      if (["partial_migration", "migration_required"].includes(repositoryPolicy?.status)) {
        addWarning("Legacy Vercel runtime reference remains in workflow during migration.", file, index + 1);
      } else {
        addError("Workflow still references a Vercel runtime URL. Replace it with Cloudflare.", file, index + 1);
      }
    }
  });
}

for (const warning of warnings) annotation("warning", warning.message, warning.file, warning.line);
for (const error of errors) annotation("error", error.message, error.file, error.line);

if (errors.length > 0) {
  console.error(`Cloudflare deployment policy: FAIL (${errors.length} error(s), ${warnings.length} warning(s))`);
  process.exit(1);
}

console.log(`Cloudflare deployment policy: PASS (${warnings.length} warning(s))`);
