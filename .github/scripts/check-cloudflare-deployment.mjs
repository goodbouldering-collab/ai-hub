import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.cwd();
const policyRelativePath = ".github/deployment-platform.json";
const policyPath = join(root, policyRelativePath);
const guardWorkflowName = "cloudflare-deployment-guard.yml";
const deployWorkflowRelativePath = ".github/workflows/cloudflare-deploy.yml";
const deployWorkflowPath = join(root, deployWorkflowRelativePath);
const forDeploy = process.argv.includes("--for-deploy");
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

function readWranglerName(configPath) {
  const contents = readFileSync(configPath, "utf8");
  const match = contents.match(/(?:^|[{,\r\n])\s*"?name"?\s*[:=]\s*["']([A-Za-z0-9_-]+)["']/m);
  return match?.[1];
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
    if (policy.version !== 2) addError("Policy version must be 2.", policyRelativePath);
    if (policy.platform !== "cloudflare") addError("Deployment platform must be cloudflare.", policyRelativePath);
    if (!validStatuses.has(policy.status)) addError("Policy status is invalid.", policyRelativePath);

    const cloudflare = policy.cloudflare ?? {};
    if (typeof cloudflare.targetVerified !== "boolean") {
      addError("cloudflare.targetVerified must be an explicit boolean.", policyRelativePath);
    }
    if (policy.status === "active" && (cloudflare.ready !== true || cloudflare.targetVerified !== true)) {
      addError("An active repository must be Cloudflare-ready with a verified target.", policyRelativePath);
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
    if (cloudflare.ready === true && cloudflare.targetVerified !== true) {
      addWarning("Cloudflare target is not verified in the authoritative workspace registry; production deploy is blocked.", policyRelativePath);
    }

    if (cloudflare.ready === true) {
      if (!/^[a-f0-9]{32}$/i.test(cloudflare.accountId ?? "")) {
        addError("Cloudflare accountId must be the 32-character registry account ID.", policyRelativePath);
      }
      if (!cloudflare.registryProject || !cloudflare.targetKey || !cloudflare.targetName) {
        addError("Cloudflare registryProject, targetKey, and targetName are required when ready is true.", policyRelativePath);
      }
      if (!["public", "private"].includes(cloudflare.exposure)) {
        addError("Cloudflare exposure must be public or private when ready is true.", policyRelativePath);
      }
      const configPath = cloudflare.configPath ? join(root, cloudflare.configPath) : null;
      if (!configPath || !existsSync(configPath)) {
        addError(`Cloudflare config does not exist: ${cloudflare.configPath ?? "(not set)"}`, policyRelativePath);
      } else {
        const wranglerName = readWranglerName(configPath);
        if (!wranglerName || wranglerName !== cloudflare.targetName) {
          addError(`Cloudflare targetName does not match Wrangler name: expected=${cloudflare.targetName}, actual=${wranglerName ?? "(missing)"}.`, cloudflare.configPath, findLine(readFileSync(configPath, "utf8"), /^\s*"?name"?\s*[:=]/));
        }
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

    if (forDeploy) {
      if (cloudflare.ready !== true || cloudflare.targetVerified !== true) {
        addError("Deploy mode requires a Cloudflare-ready, verified target.", policyRelativePath);
      }
      if (process.env.CLOUDFLARE_TARGET_VERIFIED !== "true") {
        addError("Deploy mode requires CLOUDFLARE_TARGET_VERIFIED=true.", policyRelativePath);
      }
      if (!process.env.CLOUDFLARE_ACCOUNT_ID) {
        addError("Deploy mode requires CLOUDFLARE_ACCOUNT_ID.", policyRelativePath);
      } else if (process.env.CLOUDFLARE_ACCOUNT_ID !== cloudflare.accountId) {
        addError("Cloudflare account ID does not match the registered accountId.", policyRelativePath);
      }
    }

    const legacy = policy.legacyVercel ?? {};
    if (legacy.gitIntegration !== "disconnected") {
      addError("legacyVercel.gitIntegration must remain disconnected.", policyRelativePath);
    }
    const retainedFiles = new Set((legacy.retainedFiles ?? []).map((file) => file.replaceAll("\\", "/")));
    const rootVercelConfig = "vercel.json";
    if (existsSync(join(root, rootVercelConfig))) {
      if (!retainedFiles.has(rootVercelConfig)) {
        addError("vercel.json remains without an explicit disconnected read-only exception.", rootVercelConfig);
      } else {
        addWarning("Legacy Vercel file retained for read-only migration reference; remove it after runtime parity is complete.", rootVercelConfig);
      }
    }
    if (existsSync(join(root, ".vercel", "project.json"))) {
      addWarning(".vercel/project.json remains as a legacy link. Do not run Vercel CLI commands.", ".vercel/project.json");
    }
    for (const retainedFile of retainedFiles) {
      if (existsSync(join(root, retainedFile)) && retainedFile !== rootVercelConfig) {
        addWarning("Legacy Vercel file retained for read-only migration reference.", retainedFile);
      }
    }
  }
}

const centralRegistryRelativePath = "docs/cloudflare-targets.json";
const centralRegistryPath = join(root, centralRegistryRelativePath);
if (existsSync(centralRegistryPath)) {
  let registry;
  try {
    registry = JSON.parse(readFileSync(centralRegistryPath, "utf8"));
  } catch (error) {
    addError(`Central registry is invalid JSON: ${error.message}`, centralRegistryRelativePath);
  }
  if (registry) {
    if (registry.schemaVersion !== 2) {
      addError("Central registry schemaVersion must be 2.", centralRegistryRelativePath);
    }
    const lastApiAudit = registry.cloudflareAccount?.lastApiAudit;
    const maxApiAuditAgeDays = registry.cloudflareAccount?.maxApiAuditAgeDays;
    const auditTime = Date.parse(`${lastApiAudit}T00:00:00Z`);
    const auditAgeDays = Math.floor((Date.now() - auditTime) / 86_400_000);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(lastApiAudit ?? "") || !Number.isFinite(auditTime)) {
      addError("Central registry Cloudflare API audit date is missing or invalid.", centralRegistryRelativePath);
    } else if (!Number.isInteger(maxApiAuditAgeDays) || maxApiAuditAgeDays <= 0) {
      addError("Central registry maxApiAuditAgeDays must be a positive integer.", centralRegistryRelativePath);
    } else if (auditAgeDays < -1 || auditAgeDays > maxApiAuditAgeDays) {
      addError(`Central registry Cloudflare API inventory is stale or future-dated: age=${auditAgeDays} days, max=${maxApiAuditAgeDays}.`, centralRegistryRelativePath);
    }
    const projects = registry.projects ?? {};
    const excludedRoots = registry.excludedRoots ?? {};
    const targetMap = new Map();
    for (const [projectName, record] of Object.entries(projects)) {
      if (!record?.status || record.status === "unregistered") {
        addError(`Central registry project has no explicit status: ${projectName}.`, centralRegistryRelativePath);
      }
      if (record?.sourceRoot !== `C:\\Project\\${projectName}`) {
        addError(`Central registry sourceRoot mismatch: ${projectName}.`, centralRegistryRelativePath);
      }
      const addTarget = (targetKey, target) => {
        if (!target?.name) return;
        if (targetMap.has(target.name)) {
          addError(`Central registry target name is duplicated: ${target.name}.`, centralRegistryRelativePath);
          return;
        }
        targetMap.set(target.name, { project: projectName, targetKey, target });
      };
      if (record.target) addTarget("default", record.target);
      if (!record.target && !record.targets && record.candidateTarget) addTarget("candidate", record.candidateTarget);
      for (const [targetKey, target] of Object.entries(record.targets ?? {})) addTarget(targetKey, target);
    }
    const githubInventory = registry.githubInventory ?? {};
    const githubRepositories = githubInventory.repositories ?? [];
    const githubNames = githubRepositories.map((repository) => repository.name);
    if (githubInventory.repositoryCount !== githubRepositories.length || new Set(githubNames).size !== githubRepositories.length) {
      addError("Central registry GitHub repository count or uniqueness is invalid.", centralRegistryRelativePath);
    }
    if (githubInventory.manualDeployWorkflows !== githubRepositories.filter((repository) => repository.deployWorkflow === "manual").length) {
      addError("Central registry GitHub manual deploy workflow count is invalid.", centralRegistryRelativePath);
    }
    const branchExceptions = Object.entries(githubInventory.defaultBranchExceptions ?? {});
    if (githubInventory.mainRepositoryCount + branchExceptions.length !== githubRepositories.length || branchExceptions.some(([name, branch]) => !githubNames.includes(name) || typeof branch !== "string" || branch.length === 0)) {
      addError("Central registry GitHub default branch accounting is invalid.", centralRegistryRelativePath);
    }
    for (const repository of githubRepositories) {
      if (repository.guard !== "installed") {
        addError(`Central registry GitHub guard is not installed: ${repository.name ?? "(missing)"}.`, centralRegistryRelativePath);
      }
      if (repository.project == null) {
        if (repository.role !== "control_plane") {
          addError(`Central registry GitHub repository has no project or control-plane role: ${repository.name ?? "(missing)"}.`, centralRegistryRelativePath);
        }
        continue;
      }
      if (!projects[repository.project]) {
        addError(`Central registry GitHub repository maps to an unknown project: ${repository.name}.`, centralRegistryRelativePath);
      }
      if (repository.targetKey != null) {
        const matches = [...targetMap.values()].filter((mapped) => mapped.project === repository.project && mapped.targetKey === repository.targetKey);
        if (matches.length !== 1) {
          addError(`Central registry GitHub target mapping is invalid: ${repository.name}.`, centralRegistryRelativePath);
        }
      }
    }
    for (const [rootName, excluded] of Object.entries(excludedRoots)) {
      if (excluded?.canonicalProject && !projects[excluded.canonicalProject]) {
        addError(`Central registry excluded alias has an unknown canonicalProject: ${rootName}.`, centralRegistryRelativePath);
      }
    }

    const workers = registry.cloudflareInventory?.workers ?? [];
    const pages = registry.cloudflareInventory?.pages ?? [];
    const seenResources = new Set();
    for (const worker of workers) {
      if (!worker?.name || seenResources.has(`workers:${worker.name}`)) {
        addError(`Central registry Worker is missing a unique name: ${worker?.name ?? "(missing)"}.`, centralRegistryRelativePath);
        continue;
      }
      seenResources.add(`workers:${worker.name}`);
      const mapped = targetMap.get(worker.name);
      if (!mapped) {
        addError(`Central registry Worker is unmapped: ${worker.name}.`, centralRegistryRelativePath);
      } else if (mapped.project !== worker.project || mapped.targetKey !== worker.targetKey) {
        addError(`Central registry Worker mapping mismatch: ${worker.name}.`, centralRegistryRelativePath);
      }
      if (mapped && worker.workersDevEnabled === true) {
        const expectedWorkersDevUrl = `https://${worker.name}.${registry.cloudflareAccount?.workersDevSubdomain}.workers.dev`;
        const registeredUrls = [mapped.target?.publicUrl, mapped.target?.workersDevUrl].filter(Boolean);
        if (!registeredUrls.includes(expectedWorkersDevUrl)) {
          addError(`Central registry Worker URL mismatch: ${worker.name} must register ${expectedWorkersDevUrl}.`, centralRegistryRelativePath);
        }
      }
    }
    const bindingAudit = registry.cloudflareInventory?.bindingAudit ?? {};
    const d1Records = bindingAudit.workersWithD1 ?? [];
    const withoutD1 = bindingAudit.workersWithoutD1 ?? [];
    const bindingClassifications = [...d1Records.map((record) => record.name), ...withoutD1];
    const bindingClassificationSet = new Set(bindingClassifications);
    const workerNameSet = new Set(workers.map((worker) => worker.name));
    if (bindingAudit.settingsHttp200 !== workers.length) {
      addError("Central registry binding audit must have an HTTP 200 settings result for every Worker.", centralRegistryRelativePath);
    }
    if (bindingClassificationSet.size !== workers.length || bindingClassifications.length !== workers.length || [...workerNameSet].some((name) => !bindingClassificationSet.has(name)) || [...bindingClassificationSet].some((name) => !workerNameSet.has(name))) {
      addError("Central registry D1 binding audit must classify every Worker exactly once.", centralRegistryRelativePath);
    }
    for (const record of d1Records) {
      if (record.binding !== "DB" || !/^[0-9a-f]{8}-[0-9a-f-]{27}$/i.test(record.databaseId ?? "")) {
        addError(`Central registry D1 binding record is invalid: ${record.name ?? "(missing)"}.`, centralRegistryRelativePath);
      }
      if (record.connectionProof === "health_query" && (!/^https:\/\//i.test(record.probe ?? "") || record.probeHttpStatus !== 200)) {
        addError(`Central registry D1 health proof is invalid: ${record.name ?? "(missing)"}.`, centralRegistryRelativePath);
      }
    }
    const bindingAuditTime = Date.parse(bindingAudit.observedAt ?? "");
    const bindingAuditAgeDays = Math.floor((Date.now() - bindingAuditTime) / 86_400_000);
    if (!Number.isFinite(bindingAuditTime) || bindingAuditAgeDays < -1 || bindingAuditAgeDays > maxApiAuditAgeDays) {
      addError("Central registry Cloudflare binding audit is missing, stale, or future-dated.", centralRegistryRelativePath);
    }
    for (const page of pages) {
      if (!page?.name || seenResources.has(`pages:${page.name}`)) {
        addError(`Central registry Pages project is missing a unique name: ${page?.name ?? "(missing)"}.`, centralRegistryRelativePath);
        continue;
      }
      seenResources.add(`pages:${page.name}`);
      const expectedPagesUrl = `https://${page.name}.pages.dev`;
      if (page.status === "orphaned_unverified" && page.project == null && page.targetKey == null) {
        if (page.publicUrl !== expectedPagesUrl) {
          addError(`Central registry orphaned Pages URL mismatch: ${page.name}.`, centralRegistryRelativePath);
        }
        continue;
      }
      const mapped = targetMap.get(page.name);
      if (!mapped || mapped.project !== page.project || mapped.targetKey !== page.targetKey) {
        addError(`Central registry Pages mapping mismatch: ${page.name}.`, centralRegistryRelativePath);
      } else if (![mapped.target?.publicUrl, mapped.target?.pagesDevUrl].filter(Boolean).includes(expectedPagesUrl)) {
        addError(`Central registry Pages URL mismatch: ${page.name} must register ${expectedPagesUrl}.`, centralRegistryRelativePath);
      }
    }

    const observed = registry.cloudflareAccount?.observed ?? {};
    const enabledWorkers = workers.filter((worker) => worker.workersDevEnabled === true).length;
    const disabledWorkers = workers.filter((worker) => worker.workersDevEnabled === false).length;
    if (observed.workers !== workers.length || observed.pagesProjects !== pages.length || observed.workersDevEnabled !== enabledWorkers || observed.workersDevDisabled !== disabledWorkers) {
      addError("Central registry Cloudflare API counts do not match the inventory.", centralRegistryRelativePath);
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
        addError(`Active Vercel command remains in package script "${name}". Replace it with Cloudflare.`, "package.json", line);
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

if (existsSync(deployWorkflowPath)) {
  const contents = readFileSync(deployWorkflowPath, "utf8");
  if (!/^\s*workflow_dispatch\s*:/m.test(contents)) {
    addError("Cloudflare production workflow must be manually dispatched.", deployWorkflowRelativePath);
  }
  if (/^\s*push\s*:/m.test(contents)) {
    addError("Cloudflare production workflow must not deploy on push.", deployWorkflowRelativePath, findLine(contents, /^\s*push\s*:/));
  }
  const requirements = [
    ["--for-deploy", "Production workflow must run the guard in deploy mode."],
    ["CLOUDFLARE_TARGET_VERIFIED", "Production workflow must enforce CLOUDFLARE_TARGET_VERIFIED."],
    ["CLOUDFLARE_ACCOUNT_ID", "Production workflow must provide CLOUDFLARE_ACCOUNT_ID."],
    ["CLOUDFLARE_API_TOKEN", "Production workflow must provide CLOUDFLARE_API_TOKEN."],
    ["cloudflare/wrangler-action@v3", "Production workflow must deploy through cloudflare/wrangler-action@v3."],
  ];
  for (const [needle, message] of requirements) {
    if (!contents.includes(needle)) addError(message, deployWorkflowRelativePath);
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
  console.error(`Cloudflare deployment policy: FAIL (${errors.length} error(s), ${warnings.length} warning(s), mode=${forDeploy ? "deploy" : "review"})`);
  process.exit(1);
}

console.log(`Cloudflare deployment policy: PASS (${warnings.length} warning(s), mode=${forDeploy ? "deploy" : "review"})`);
