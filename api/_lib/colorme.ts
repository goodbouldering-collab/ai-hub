import { requireEnv } from "./config.js";

const COLORME_API = "https://api.shop-pro.jp";

function token(): string {
  return requireEnv("COLORME_ACCESS_TOKEN");
}

async function call(path: string, init: RequestInit = {}): Promise<any> {
  const res = await fetch(`${COLORME_API}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token()}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  const text = await res.text();
  let json: any = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    /* keep raw */
  }
  if (!res.ok) {
    const err: any = new Error(`Colorme API ${res.status}`);
    err.status = res.status;
    err.body = json ?? text;
    throw err;
  }
  return json;
}

export async function listGroups(limit = 50, offset = 0): Promise<any> {
  return call(`/v1/groups?limit=${limit}&offset=${offset}`);
}

/**
 * 全 group を取得する。
 * 注: カラーミー API の /v1/groups は limit/offset を尊重せず常に全件返す
 * （2026-05-08 グッぼる本店で確認: 約1400件を1リクエストで返却）。
 * そのため pagination ループは不要で 1 回だけ呼ぶ。
 */
export async function listAllGroups(): Promise<any[]> {
  const res = await listGroups(1000, 0);
  return (res?.groups || []) as any[];
}

/** 全件取得後にメモリ上で parent_group_id でフィルタ（API 側に直接フィルタが無いため） */
export async function listChildGroups(parentId: number | string): Promise<any[]> {
  const all = await listAllGroups();
  const pid = Number(parentId);
  return all
    .filter((g) => Number(g.parent_group_id) === pid)
    .sort((a, b) => (Number(a.sort ?? 0) - Number(b.sort ?? 0)));
}

/** 親候補（parent_group_id が null = トップレベル）のみ抽出 */
export async function listTopLevelGroups(): Promise<any[]> {
  const all = await listAllGroups();
  return all
    .filter((g) => g.parent_group_id == null)
    .sort((a, b) => (Number(a.sort ?? 0) - Number(b.sort ?? 0)));
}

export async function getGroup(id: number | string): Promise<any> {
  return call(`/v1/groups/${id}`);
}

export async function createGroup(payload: {
  name: string;
  image_url?: string;
  expl?: string;
  display_state?: "showing" | "hidden";
  parent_group_id?: number | null;
  sort?: number;
}): Promise<any> {
  return call(`/v1/groups`, {
    method: "POST",
    body: JSON.stringify({ group: payload }),
  });
}

export async function updateGroup(
  id: number | string,
  payload: Partial<{
    name: string;
    image_url: string;
    expl: string;
    display_state: "showing" | "hidden";
    parent_group_id: number | null;
    sort: number;
  }>,
): Promise<any> {
  return call(`/v1/groups/${id}`, {
    method: "PUT",
    body: JSON.stringify({ group: payload }),
  });
}

export async function getTemplatePage(templateId: number, pageType: string): Promise<any> {
  return call(`/v1/templates/${templateId}/pages/${pageType}`);
}

export async function updateTemplatePage(
  templateId: number,
  pageType: string,
  payload: { html?: string; css?: string },
): Promise<any> {
  return call(`/v1/templates/${templateId}/pages/${pageType}`, {
    method: "PUT",
    body: JSON.stringify({ template_page: payload }),
  });
}

export async function getTemplatePreviewUrl(templateId: number): Promise<any> {
  return call(`/v1/templates/${templateId}/preview_url`);
}
