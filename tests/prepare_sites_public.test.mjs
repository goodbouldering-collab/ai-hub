import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, rm, truncate, writeFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  MAX_STATIC_ASSET_BYTES,
  prepareSitesPublic,
} from "../scripts/prepare_sites_public.mjs";

const temporaryRoots = new Set();
const TEST_DIRECTORY = path.dirname(fileURLToPath(import.meta.url));

async function createTemporaryRepo() {
  const repoRoot = await mkdtemp(
    path.join(TEST_DIRECTORY, ".tmp-sites-static-"),
  );
  temporaryRoots.add(repoRoot);
  await mkdir(path.join(repoRoot, "site", "dist"), { recursive: true });
  return repoRoot;
}

async function writeFixture(repoRoot, relativePath, contents = relativePath) {
  const filePath = path.join(repoRoot, "site", "dist", relativePath);
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, contents);
  return filePath;
}

test.afterEach(async () => {
  for (const repoRoot of temporaryRoots) {
    await rm(repoRoot, { recursive: true, force: true });
    temporaryRoots.delete(repoRoot);
  }
});

test("copies static routes and excludes proxied paths", async () => {
  const repoRoot = await createTemporaryRepo();
  await writeFixture(repoRoot, "index.html", "<h1>AI相談</h1>");
  await writeFixture(repoRoot, "lectures/index.html", "lectures");
  await writeFixture(repoRoot, "lectures/beginner/index.html", "beginner");
  await writeFixture(repoRoot, "lectures/assets/worksheet.pdf", "worksheet");
  await writeFixture(
    repoRoot,
    "lectures/assets/codex-app-onboarding.webm",
    "excluded-video",
  );

  for (const directory of ["admin", "api", "media", "ops", "videos", "watch"]) {
    await writeFixture(repoRoot, `${directory}/private.txt`, directory);
  }

  const staleFile = path.join(repoRoot, "public", "stale.txt");
  await mkdir(path.dirname(staleFile), { recursive: true });
  await writeFile(staleFile, "stale");

  const result = await prepareSitesPublic({ repoRoot });

  assert.equal(result.copiedFileCount, 4);
  assert.equal(result.excludedPathCount, 7);
  assert.equal(
    await readFile(path.join(repoRoot, "public", "index.html"), "utf8"),
    "<h1>AI相談</h1>",
  );
  assert.equal(
    await readFile(
      path.join(repoRoot, "public", "lectures", "beginner", "index.html"),
      "utf8",
    ),
    "beginner",
  );
  await assert.rejects(readFile(staleFile), { code: "ENOENT" });
  await assert.rejects(
    readFile(path.join(repoRoot, "public", "media", "private.txt")),
    { code: "ENOENT" },
  );
  await assert.rejects(
    readFile(
      path.join(
        repoRoot,
        "public",
        "lectures",
        "assets",
        "codex-app-onboarding.webm",
      ),
    ),
    { code: "ENOENT" },
  );
});

test("check mode validates without replacing public", async () => {
  const repoRoot = await createTemporaryRepo();
  await writeFixture(repoRoot, "index.html", "new-index");
  const existingPublicFile = path.join(repoRoot, "public", "index.html");
  await mkdir(path.dirname(existingPublicFile), { recursive: true });
  await writeFile(existingPublicFile, "existing-index");

  const result = await prepareSitesPublic({ repoRoot, checkOnly: true });

  assert.equal(result.checkOnly, true);
  assert.equal(result.copiedFileCount, 1);
  assert.equal(await readFile(existingPublicFile, "utf8"), "existing-index");
});

test("oversized included assets fail before public is replaced", async () => {
  const repoRoot = await createTemporaryRepo();
  await writeFixture(repoRoot, "index.html", "index");
  const oversizedAsset = await writeFixture(repoRoot, "img/too-large.bin", "");
  await truncate(oversizedAsset, MAX_STATIC_ASSET_BYTES + 1);

  const existingPublicFile = path.join(repoRoot, "public", "keep.txt");
  await mkdir(path.dirname(existingPublicFile), { recursive: true });
  await writeFile(existingPublicFile, "keep");

  await assert.rejects(
    prepareSitesPublic({ repoRoot }),
    /Sites static assets must be at most/,
  );
  assert.equal(await readFile(existingPublicFile, "utf8"), "keep");
});

test("refuses any output path other than the repository public directory", async () => {
  const repoRoot = await createTemporaryRepo();
  await writeFixture(repoRoot, "index.html", "index");

  await assert.rejects(
    prepareSitesPublic({
      repoRoot,
      outputDir: path.join(repoRoot, "not-public"),
    }),
    /outputDir must resolve exactly/,
  );
});
