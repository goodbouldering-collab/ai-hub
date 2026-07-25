#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import {
  copyFile,
  lstat,
  mkdir,
  readdir,
  realpath,
  rm,
  stat,
} from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const MAX_STATIC_ASSET_BYTES = 25 * 1024 * 1024;

export const EXCLUDED_TOP_LEVEL_PATHS = new Set([
  "admin",
  "api",
  "media",
  "ops",
  "videos",
  "watch",
]);

export const EXCLUDED_EXACT_PATHS = new Set([
  "lectures/assets/codex-app-onboarding.webm",
]);

const SCRIPT_PATH = fileURLToPath(import.meta.url);
export const DEFAULT_REPO_ROOT = path.resolve(path.dirname(SCRIPT_PATH), "..");

function normalizedRelativePath(relativePath) {
  return relativePath.split(path.sep).join("/").replace(/^\/+/, "");
}

export function isExcludedStaticPath(relativePath) {
  const normalized = normalizedRelativePath(relativePath).toLowerCase();
  const topLevelPath = normalized.split("/", 1)[0];
  return (
    EXCLUDED_TOP_LEVEL_PATHS.has(topLevelPath) ||
    EXCLUDED_EXACT_PATHS.has(normalized)
  );
}

function assertExactChildPath(repoRoot, candidate, childPath, label) {
  const resolvedRoot = path.resolve(repoRoot);
  const expected = path.resolve(resolvedRoot, childPath);
  const resolvedCandidate = path.resolve(candidate);

  if (resolvedCandidate !== expected) {
    throw new Error(
      `${label} must resolve exactly to ${expected}; received ${resolvedCandidate}`,
    );
  }
}

async function assertDirectoryIsNotSymlink(directory, label) {
  const metadata = await lstat(directory);
  if (metadata.isSymbolicLink()) {
    throw new Error(`${label} must not be a symbolic link: ${directory}`);
  }
  if (!metadata.isDirectory()) {
    throw new Error(`${label} is not a directory: ${directory}`);
  }
}

export async function assertSafeLayout({
  repoRoot,
  sourceDir,
  outputDir,
}) {
  const resolvedRoot = path.resolve(repoRoot);
  const resolvedSource = path.resolve(sourceDir);
  const resolvedOutput = path.resolve(outputDir);

  assertExactChildPath(resolvedRoot, resolvedSource, path.join("site", "dist"), "sourceDir");
  assertExactChildPath(resolvedRoot, resolvedOutput, "public", "outputDir");

  await assertDirectoryIsNotSymlink(resolvedRoot, "repoRoot");
  await assertDirectoryIsNotSymlink(resolvedSource, "sourceDir");

  const canonicalRoot = await realpath(resolvedRoot);
  const canonicalSource = await realpath(resolvedSource);
  const expectedCanonicalSource = path.join(
    canonicalRoot,
    "site",
    "dist",
  );

  if (canonicalSource !== expectedCanonicalSource) {
    throw new Error(
      `sourceDir escapes the repository through a symbolic link: ${canonicalSource}`,
    );
  }

  try {
    const outputMetadata = await lstat(resolvedOutput);
    if (outputMetadata.isSymbolicLink()) {
      throw new Error(
        `Refusing to replace symbolic-link outputDir: ${resolvedOutput}`,
      );
    }
  } catch (error) {
    if (error?.code !== "ENOENT") {
      throw error;
    }
  }

  return {
    repoRoot: resolvedRoot,
    sourceDir: resolvedSource,
    outputDir: resolvedOutput,
  };
}

export async function scanStaticFiles(sourceDir) {
  const includedFiles = [];
  const excludedFiles = [];

  async function visit(relativeDirectory = "") {
    const absoluteDirectory = path.join(sourceDir, relativeDirectory);
    const entries = await readdir(absoluteDirectory, { withFileTypes: true });
    entries.sort((left, right) => left.name.localeCompare(right.name, "en"));

    for (const entry of entries) {
      const relativePath = path.join(relativeDirectory, entry.name);
      const normalizedPath = normalizedRelativePath(relativePath);

      if (entry.isSymbolicLink()) {
        throw new Error(
          `Symbolic links are not supported in site/dist: ${normalizedPath}`,
        );
      }

      if (isExcludedStaticPath(relativePath)) {
        excludedFiles.push(normalizedPath);
        continue;
      }

      if (entry.isDirectory()) {
        await visit(relativePath);
        continue;
      }

      if (!entry.isFile()) {
        throw new Error(
          `Unsupported filesystem entry in site/dist: ${normalizedPath}`,
        );
      }

      const absolutePath = path.join(sourceDir, relativePath);
      const metadata = await stat(absolutePath);
      if (metadata.size > MAX_STATIC_ASSET_BYTES) {
        throw new Error(
          `${normalizedPath} is ${metadata.size} bytes; Sites static assets must be at most ${MAX_STATIC_ASSET_BYTES} bytes (25 MiB)`,
        );
      }

      includedFiles.push({
        absolutePath,
        relativePath,
        normalizedPath,
        size: metadata.size,
      });
    }
  }

  await visit();

  return {
    includedFiles,
    excludedFiles,
    copiedBytes: includedFiles.reduce((total, file) => total + file.size, 0),
  };
}

export async function prepareSitesPublic({
  repoRoot = DEFAULT_REPO_ROOT,
  sourceDir = path.join(repoRoot, "site", "dist"),
  outputDir = path.join(repoRoot, "public"),
  checkOnly = false,
} = {}) {
  const safePaths = await assertSafeLayout({
    repoRoot,
    sourceDir,
    outputDir,
  });
  const scan = await scanStaticFiles(safePaths.sourceDir);

  if (!checkOnly) {
    await rm(safePaths.outputDir, { recursive: true, force: true });
    await mkdir(safePaths.outputDir, { recursive: true });

    for (const file of scan.includedFiles) {
      const outputPath = path.join(safePaths.outputDir, file.relativePath);
      await mkdir(path.dirname(outputPath), { recursive: true });
      await copyFile(file.absolutePath, outputPath);
    }
  }

  return {
    ...safePaths,
    checkOnly,
    copiedFileCount: scan.includedFiles.length,
    excludedPathCount: scan.excludedFiles.length,
    excludedFiles: scan.excludedFiles,
    copiedBytes: scan.copiedBytes,
  };
}

function runSiteBuild(repoRoot) {
  const pythonCommand =
    process.env.PYTHON ||
    (process.platform === "win32" ? "python" : "python3");
  const result = spawnSync(
    pythonCommand,
    [path.join("site", "build_site.py")],
    {
      cwd: repoRoot,
      encoding: "utf8",
      stdio: "inherit",
    },
  );

  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(
      `site/build_site.py failed with exit code ${result.status ?? "unknown"}`,
    );
  }
}

function parseCliArguments(argumentsList) {
  const options = {
    build: false,
    checkOnly: false,
  };

  for (const argument of argumentsList) {
    if (argument === "--build") {
      options.build = true;
    } else if (argument === "--check") {
      options.checkOnly = true;
    } else if (argument === "--help" || argument === "-h") {
      options.help = true;
    } else {
      throw new Error(`Unknown argument: ${argument}`);
    }
  }

  return options;
}

function printHelp() {
  console.log(`Usage: node scripts/prepare_sites_public.mjs [options]

Copies deployable static files from site/dist to public.

Options:
  --build  Run site/build_site.py before preparing public
  --check  Validate inputs, exclusions, and size limits without changing public
  -h, --help  Show this help`);
}

async function main() {
  const options = parseCliArguments(process.argv.slice(2));
  if (options.help) {
    printHelp();
    return;
  }

  if (options.build) {
    runSiteBuild(DEFAULT_REPO_ROOT);
  }

  const result = await prepareSitesPublic({
    repoRoot: DEFAULT_REPO_ROOT,
    checkOnly: options.checkOnly,
  });
  const action = result.checkOnly ? "Validated" : "Copied";
  console.log(
    `${action} ${result.copiedFileCount} files (${result.copiedBytes} bytes); excluded ${result.excludedPathCount} paths.`,
  );
}

const isMain =
  process.argv[1] &&
  pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url;

if (isMain) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
