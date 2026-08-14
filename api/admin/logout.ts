import { clearAdminSessionCookie, safeNextPath, type VercelReq, type VercelRes } from "../_lib/auth.js";
import { adminRequestUrl } from "../_lib/admin-origin.js";

export default function handler(req: VercelReq, res: VercelRes) {
  const next = getNext(req);
  res.setHeader("Set-Cookie", clearAdminSessionCookie());
  res.status(303);
  res.setHeader("Location", `/admin/login?next=${encodeURIComponent(next)}`);
  res.send("Logged out");
}

function getNext(req: VercelReq): string {
  const queryNext = req.query?.next;
  if (queryNext) return safeNextPath(queryNext);
  try {
    const url = adminRequestUrl(req.url, "/admin/logout");
    return safeNextPath(url.searchParams.get("next"));
  } catch {
    return "/admin";
  }
}
