import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

class FakeElement {
  constructor() {
    this.dataset = {};
    this.textContent = "";
    this.innerHTML = "";
    this.classList = { toggle() {} };
  }

  addEventListener() {}
}

function jsonResponse(payload) {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  };
}

async function renderView(view = "calendar", dashboard = {}) {
  const elements = new Map([
    ["cc-content", new FakeElement()],
    ["cc-live", new FakeElement()],
    ["cc-generated-at", new FakeElement()],
  ]);
  const document = {
    body: { dataset: { view } },
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, new FakeElement());
      return elements.get(id);
    },
    querySelectorAll() {
      return [];
    },
  };
  const dateParts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const datePart = (type) => dateParts.find((part) => part.type === type)?.value || "";
  const today = `${datePart("year")}-${datePart("month")}-${datePart("day")}`;
  const source = await readFile(new URL("../site/static/admin/command-center.js", import.meta.url), "utf8");

  vm.runInNewContext(source, {
    Date,
    Promise,
    URL,
    console,
    document,
    encodeURIComponent,
    fetch: async (url) => {
      if (url === "/api/admin/command-center/data") {
        return jsonResponse({
          tasks: dashboard.tasks || [{ id: "task-1", title: "AI相談の移行確認", dueDate: today, status: "today", reason: "移行後の確認" }],
          projects: dashboard.projects || [],
          directives: dashboard.directives || [],
          trades: dashboard.trades || [],
          tradePlans: dashboard.tradePlans || [],
        });
      }
      if (String(url).startsWith("/api/admin/command-center/calendar?")) {
        return jsonResponse({
          accountLabel: "Google カレンダー",
          privacy: "busy_only",
          status: "connected",
          days: [{ date: today, busyCount: 1, allDayCount: 0 }],
        });
      }
      throw new Error(`unexpected URL: ${url}`);
    },
    window: { location: { href: "" } },
  }, { filename: "command-center.js" });

  for (let index = 0; index < 4; index += 1) await new Promise((resolve) => setImmediate(resolve));
  return elements.get(view === "calendar" ? "calendar-result" : "cc-content").innerHTML;
}

test("protected calendar renders unfinished task deadlines alongside busy-only counts", async () => {
  const rendered = await renderView();

  assert.match(rendered, /1件 忙しい/);
  assert.match(rendered, /期限 1件/);
  assert.match(rendered, /AI相談の移行確認/);
});

test("calendar uses Japan time for its initial date", async () => {
  const source = await readFile(new URL("../site/static/admin/command-center.js", import.meta.url), "utf8");

  assert.match(source, /timeZone:\s*["']Asia\/Tokyo["']/);
  assert.doesNotMatch(source, /const today = \(\) => new Date\(\)\.toISOString\(\)\.slice\(0, 10\)/);
});

test("business page does not render non-http production URLs as links", async () => {
  const rendered = await renderView("businesses", {
    projects: [
      { businessId: "unsafe", displayName: "Unsafe", status: "active", productionUrl: "javascript:alert(1)", lastReviewDate: "2026-08-09" },
      { businessId: "safe", displayName: "Safe", status: "active", productionUrl: "https://example.com/", lastReviewDate: "2026-08-09" },
    ],
  });

  assert.doesNotMatch(rendered, /href="javascript:/);
  assert.match(rendered, /href="https:\/\/example\.com\//);
});
