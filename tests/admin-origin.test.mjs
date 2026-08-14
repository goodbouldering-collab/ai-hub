import assert from "node:assert/strict";
import test from "node:test";

import { ADMIN_ORIGIN, adminRequestUrl } from "../api/_lib/admin-origin.ts";

test("relative admin requests default to the aiclimb production origin", () => {
  assert.equal(ADMIN_ORIGIN, "https://aiclimb.vercel.app");
  assert.equal(
    adminRequestUrl(undefined, "/admin/login?next=%2Fadmin").href,
    "https://aiclimb.vercel.app/admin/login?next=%2Fadmin",
  );
});
