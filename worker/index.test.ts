import { exports } from "cloudflare:workers";
import { afterEach, describe, expect, it, vi } from "vitest";

describe("AIclimb Cloudflare edge", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("keeps monitoring independent from the Vercel origin", async () => {
    const originFetch = vi.fn();
    vi.stubGlobal("fetch", originFetch);

    const response = await exports.default.fetch("https://aiclimb.gb-jp.workers.dev/health");

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(await response.json()).toEqual({
      status: "ok",
      service: "aiclimb",
      delivery: "cloudflare-workers-static-assets",
    });
    expect(originFetch).not.toHaveBeenCalled();
  });

  it("sends administrators directly to Vercel without proxying credentials or bodies", async () => {
    const originFetch = vi.fn();
    vi.stubGlobal("fetch", originFetch);

    const response = await exports.default.fetch(
      new Request("https://aiclimb.gb-jp.workers.dev/admin/blog?draft=1", {
        method: "POST",
        redirect: "manual",
        headers: {
          authorization: "Basic opaque",
          cookie: "session=opaque",
          "content-type": "application/json",
        },
        body: JSON.stringify({ title: "draft" }),
      }),
    );

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("https://aiclimb.vercel.app/admin/blog?draft=1");
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(await response.text()).toBe("");
    expect(originFetch).not.toHaveBeenCalled();
  });

  it("sends the oversized course video directly to Vercel", async () => {
    const originFetch = vi.fn();
    vi.stubGlobal("fetch", originFetch);

    const response = await exports.default.fetch(
      new Request(
        "https://aiclimb.gb-jp.workers.dev/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm",
        { headers: { range: "bytes=0-10" }, redirect: "manual" },
      ),
    );

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://aiclimb.vercel.app/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm",
    );
    expect(originFetch).not.toHaveBeenCalled();
  });

  it("redirects dynamic APIs to Vercel without becoming an API proxy", async () => {
    const originFetch = vi.fn();
    vi.stubGlobal("fetch", originFetch);

    const response = await exports.default.fetch(
      new Request("https://aiclimb.gb-jp.workers.dev/api/admin/ping?mode=check", {
        redirect: "manual",
      }),
    );

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe(
      "https://aiclimb.vercel.app/api/admin/ping?mode=check",
    );
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(originFetch).not.toHaveBeenCalled();
  });
});
