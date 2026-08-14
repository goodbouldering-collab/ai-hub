export const ADMIN_ORIGIN = "https://aiclimb.vercel.app";

export function adminRequestUrl(requestUrl: string | undefined, fallbackPath: string): URL {
  return new URL(requestUrl || fallbackPath, ADMIN_ORIGIN);
}
