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

export async function getGroup(id: number | string): Promise<any> {
  return call(`/v1/groups/${id}`);
}

export async function createGroup(payload: {
  name: string;
  image_url?: string;
  expl?: string;
  display_state?: "showing" | "hidden";
  parent_group_id?: number | null;
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
    body: JSON.stringify({ page: payload }),
  });
}

export async function getTemplatePreviewUrl(templateId: number): Promise<any> {
  return call(`/v1/templates/${templateId}/preview_url`);
}
