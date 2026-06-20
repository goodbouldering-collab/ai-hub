/**
 * /api/admin/status
 *   GET → outputs/agents_status.json をそのまま返す (管理ログイン必須)
 *
 * /admin の「タスクと最近の動き」パネルが fetch して動的描画する。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

export default withAdmin({ method: "GET" }, async ({ res }) => {
  try {
    const p = join(process.cwd(), "outputs", "agents_status.json");
    const raw = readFileSync(p, "utf-8");
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.status(200).send(raw);
  } catch (e: any) {
    res.status(200).json({
      error: "agents_status.json not found",
      detail: e.message,
      recent_works: [],
      tasks_open: [],
      per_business_recent: [],
      daily_histogram: [],
      cma_apps: [],
      totals: { consul_work_total: 0, recent_7d_total: 0, tasks_open_total: 0 },
    });
  }
});
