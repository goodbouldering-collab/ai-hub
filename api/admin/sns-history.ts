/**
 * GET /api/admin/sns-history
 * portal.sns_posts から最新 30 件を返す。
 */

import { withAdmin } from "../_lib/http.js";
import { listSnsPosts } from "../_lib/supabase-portal.js";

export default withAdmin({ method: "GET" }, async ({ res }) => {
  const posts = await listSnsPosts(30);
  res.status(200).json({ posts });
});
