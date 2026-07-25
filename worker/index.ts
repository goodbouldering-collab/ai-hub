import {
  DEFAULT_DEVICE_SIZES,
  DEFAULT_IMAGE_SIZES,
  handleImageOptimization,
} from "vinext/server/image-optimization";
import handler from "vinext/server/app-router-entry";

const LEGACY_ORIGIN = "https://ai-hub-jp.vercel.app";
const EXACT_LEGACY_PATHS = new Set([
  "/lectures/assets/codex-app-onboarding.webm",
]);
const LEGACY_PATH_PREFIXES = [
  "/api",
  "/admin",
  "/img",
  "/ops",
  "/watch",
  "/media",
  "/videos",
] as const;
const DYNAMIC_PATH_PREFIXES = ["/api", "/admin", "/ops", "/watch"] as const;

interface Env {
  ASSETS: {
    fetch(input: Request): Promise<Response>;
  };
  DB: unknown;
  IMAGES: {
    input(stream: ReadableStream): {
      transform(options: Record<string, unknown>): {
        output(options: {
          format: string;
          quality: number;
        }): Promise<{ response(): Response }>;
      };
    };
  };
}

interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
  passThroughOnException(): void;
}

function pathMatchesPrefix(
  pathname: string,
  prefixes: readonly string[],
): boolean {
  return prefixes.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

function shouldProxyToLegacy(pathname: string): boolean {
  return (
    EXACT_LEGACY_PATHS.has(pathname) ||
    pathMatchesPrefix(pathname, LEGACY_PATH_PREFIXES)
  );
}

async function proxyToLegacy(
  request: Request,
  pathname: string,
): Promise<Response> {
  const incomingUrl = new URL(request.url);
  const upstreamUrl = new URL(
    `${incomingUrl.pathname}${incomingUrl.search}`,
    LEGACY_ORIGIN,
  );
  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const upstreamBody = hasBody ? await request.arrayBuffer() : undefined;
  const upstreamHeaders = new Headers(request.headers);
  // Sites owner-only verification is only for the Sites edge. Never forward
  // its bypass credential to the legacy Vercel origin.
  upstreamHeaders.delete("oai-sites-authorization");
  upstreamHeaders.set("x-forwarded-host", incomingUrl.host);
  upstreamHeaders.set("x-forwarded-proto", incomingUrl.protocol.slice(0, -1));
  const upstreamRequest = new Request(upstreamUrl, {
    body: upstreamBody,
    headers: upstreamHeaders,
    method: request.method,
    redirect: "manual",
  });
  const upstreamResponse = await fetch(upstreamRequest);

  // Cloning from the upstream response keeps status, Location, Range response
  // headers and all Set-Cookie values while allowing cache headers to be set.
  const response = new Response(upstreamResponse.body, upstreamResponse);
  if (pathMatchesPrefix(pathname, DYNAMIC_PATH_PREFIXES)) {
    response.headers.set(
      "Cache-Control",
      "private, no-store, no-cache, must-revalidate, max-age=0",
    );
    response.headers.set("CDN-Cache-Control", "no-store");
    response.headers.set("Cloudflare-CDN-Cache-Control", "no-store");
  }
  return response;
}

const worker = {
  async fetch(
    request: Request,
    env: Env | undefined,
    ctx: ExecutionContext,
  ): Promise<Response> {
    const url = new URL(request.url);

    if (shouldProxyToLegacy(url.pathname)) {
      return proxyToLegacy(request, url.pathname);
    }

    if (
      url.pathname === "/" &&
      (request.method === "GET" || request.method === "HEAD") &&
      env?.ASSETS
    ) {
      const indexUrl = new URL("/index.html", request.url);
      indexUrl.search = url.search;
      const staticResponse = await env.ASSETS.fetch(
        new Request(indexUrl, request),
      );
      if (staticResponse.status !== 404) {
        return staticResponse;
      }
    }

    if (url.pathname === "/_vinext/image" && env?.ASSETS && env.IMAGES) {
      const allowedWidths = [...DEFAULT_DEVICE_SIZES, ...DEFAULT_IMAGE_SIZES];
      return handleImageOptimization(
        request,
        {
          fetchAsset: (path) =>
            env.ASSETS.fetch(new Request(new URL(path, request.url))),
          transformImage: async (body, { width, format, quality }) => {
            const result = await env.IMAGES.input(body)
              .transform(width > 0 ? { width } : {})
              .output({ format, quality });
            return result.response();
          },
        },
        allowedWidths,
      );
    }

    if (
      (request.method === "GET" || request.method === "HEAD") &&
      env?.ASSETS
    ) {
      const staticResponse = await env.ASSETS.fetch(request);
      if (staticResponse.status !== 404) {
        return staticResponse;
      }
    }

    return handler.fetch(request, env ?? {}, ctx);
  },
};

export default worker;
