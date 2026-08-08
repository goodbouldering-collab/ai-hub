const API_KEY_STORAGE = "contentStudioOpenAIKey";
let sharedServerKeyConfigured = false;
const rawStudioConfig = window.CONTENT_STUDIO_CONFIG && typeof window.CONTENT_STUDIO_CONFIG === "object"
  ? window.CONTENT_STUDIO_CONFIG
  : {};
const apiBase = String(rawStudioConfig.apiBase || "").trim().replace(/\/+$/, "");

export const STUDIO_CONFIG = Object.freeze({
  apiBase,
  profileId: String(rawStudioConfig.profileId || "").trim(),
  localAdmin: rawStudioConfig.localAdmin === true,
  embedded: new URLSearchParams(window.location.search).get("embedded") === "1",
  handoffMessageType: String(rawStudioConfig.handoffMessageType || "content-studio:handoff").trim(),
  adminUrl: String(rawStudioConfig.adminUrl || "/admin").trim() || "/admin"
});

export const $ = (selector) => document.querySelector(selector);
export const $$ = (selector) => [...document.querySelectorAll(selector)];

export function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

export function toast(message) {
  const target = $("#toast");
  if (!target) return;
  target.textContent = message;
  target.classList.add("show");
  setTimeout(() => target.classList.remove("show"), 2600);
}

export function getSessionApiKey() {
  return sessionStorage.getItem(API_KEY_STORAGE)?.trim() || "";
}

function acceptsOpenAIKey(path) {
  return path === "/api/key/verify" || path.startsWith("/api/blog/") || path.startsWith("/api/reel/");
}

function apiUrl(path) {
  const normalized = String(path || "");
  return STUDIO_CONFIG.apiBase ? `${STUDIO_CONFIG.apiBase}${normalized.startsWith("/") ? normalized : `/${normalized}`}` : normalized;
}

function nativeHeaders() {
  return STUDIO_CONFIG.localAdmin ? { "X-Content-Studio-Embed": "1" } : {};
}

export async function api(path, options = {}) {
  const key = getSessionApiKey();
  const response = await fetch(apiUrl(path), {
    ...options,
    credentials: STUDIO_CONFIG.localAdmin ? "omit" : "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...nativeHeaders(),
      ...(key && acceptsOpenAIKey(path) ? { "X-OpenAI-API-Key": key } : {}),
      ...(options.headers || {})
    }
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) throw new Error(data.error || `通信エラー: ${response.status}`);
  return data;
}

export async function apiBlob(path, options = {}) {
  const key = getSessionApiKey();
  const response = await fetch(apiUrl(path), {
    ...options,
    credentials: STUDIO_CONFIG.localAdmin ? "omit" : "same-origin",
    headers: { ...nativeHeaders(), ...(key && acceptsOpenAIKey(path) ? { "X-OpenAI-API-Key": key } : {}), ...(options.headers || {}) }
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || `動画取得エラー: ${response.status}`);
  }
  return response.blob();
}

function keySummary(key) {
  if (key) return "入力済み・検証済み";
  if (sharedServerKeyConfigured) return "全事業共通キーを使用中";
  return STUDIO_CONFIG.localAdmin
    ? "共通キー未設定（必要な場合のみこのタブで設定）"
    : "未入力（サーバー設定またはデモを使用）";
}

export function updateKeyStatus() {
  const key = getSessionApiKey();
  const status = $("#api-key-status");
  const clear = $("#clear-api-key");
  if (status) {
    status.textContent = keySummary(key);
    status.classList.toggle("ready", Boolean(key));
  }
  if (clear) clear.hidden = !key;
}

export function bindApiKeyPanel(onChanged) {
  const input = $("#api-key-input");
  const save = $("#save-api-key");
  const clear = $("#clear-api-key");
  if (!input || !save || !clear) return;
  updateKeyStatus();
  save.addEventListener("click", async () => {
    const key = input.value.trim();
    if (key.length < 20 || key.length > 512 || /\s/.test(key)) {
      return toast("OpenAI APIキーの形式を確認してください");
    }
    save.disabled = true;
    sessionStorage.setItem(API_KEY_STORAGE, key);
    try {
      await api("/api/key/verify", { method: "POST", body: "{}" });
      input.value = "";
      updateKeyStatus();
      toast("APIキーを確認し、このタブのセッションに設定しました");
      await onChanged?.();
    } catch (error) {
      sessionStorage.removeItem(API_KEY_STORAGE);
      updateKeyStatus();
      toast(`APIキーを設定できません: ${error.message}`);
    } finally {
      save.disabled = false;
    }
  });
  clear.addEventListener("click", async () => {
    sessionStorage.removeItem(API_KEY_STORAGE);
    input.value = "";
    updateKeyStatus();
    toast("APIキーをこのタブから削除しました");
    await onChanged?.();
  });
}

export function renderHealth(health) {
  const byok = Boolean(getSessionApiKey());
  sharedServerKeyConfigured = Boolean(health.openaiConfigured);
  const live = health.mode === "live" || byok;
  const badge = $("#server-state");
  if (badge) {
    badge.textContent = live
      ? (byok ? "実API接続・このタブのキー" : (sharedServerKeyConfigured ? "実API接続・全事業共通キー" : "実API接続"))
      : "デモモード";
    badge.classList.toggle("mock", !live);
  }
  const keyPanel = $(".api-key-panel");
  if (keyPanel) keyPanel.hidden = sharedServerKeyConfigured && !byok;
  updateKeyStatus();
  const notice = $("#mode-notice");
  if (notice) {
    notice.hidden = live;
    notice.textContent = STUDIO_CONFIG.localAdmin
      ? "現在はデモモードです。共通キーの設定を確認するか、下のAPIキーを検証すると、このタブだけで最新調査・文章・画像・動画生成を使えます。"
      : "現在はデモモードです。下のAPIキーを検証してこのタブだけで使うか、サーバー側のAPIキーを設定すると、最新調査・文章・画像・動画生成が有効になります。";
  }
}

export async function refreshHealth() {
  const health = await api("/api/health");
  renderHealth(health);
  return health;
}

export async function requireSession(onAuthenticated) {
  if (STUDIO_CONFIG.localAdmin) {
    const gate = $("#login-gate");
    if (gate) gate.hidden = true;
    return true;
  }
  const session = await api("/api/session/status");
  const gate = $("#login-gate");
  if (session.authenticated) {
    if (gate) gate.hidden = true;
    return true;
  }
  if (gate) gate.hidden = false;
  $("#studio-password")?.focus();
  const form = $("#login-form");
  if (form && !form.dataset.bound) {
    form.dataset.bound = "1";
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      $("#login-error").textContent = "";
      try {
        await api("/api/session/login", { method: "POST", body: JSON.stringify({ password: $("#studio-password").value }) });
        $("#studio-password").value = "";
        gate.hidden = true;
        await onAuthenticated();
      } catch (error) {
        $("#login-error").textContent = error.message;
      }
    });
  }
  return false;
}

export function handoffToAdmin(kind, payload, storageKey) {
  if (!STUDIO_CONFIG.localAdmin) throw new Error("管理画面版でのみ記事を受け渡せます。");
  if (storageKey) localStorage.setItem(storageKey, JSON.stringify(payload));

  if (STUDIO_CONFIG.embedded && window.parent !== window) {
    window.parent.postMessage({
      type: "content-studio:handoff",
      kind,
      payload
    }, window.location.origin);
    return "embedded";
  }

  window.location.assign(STUDIO_CONFIG.adminUrl);
  return "redirect";
}

export async function loadProfiles(select) {
  const result = await api("/api/profiles");
  let profiles = result.profiles;
  if (STUDIO_CONFIG.localAdmin) {
    if (!STUDIO_CONFIG.profileId) throw new Error("ローカル管理画面のprofileIdが設定されていません。");
    profiles = profiles.filter((profile) => profile.id === STUDIO_CONFIG.profileId);
    if (profiles.length !== 1) throw new Error(`この管理画面の事業プロフィールを取得できません: ${STUDIO_CONFIG.profileId}`);
  }
  select.innerHTML = profiles.map((profile) => `<option value="${escapeHtml(profile.id)}">${escapeHtml(profile.name)}｜${escapeHtml(profile.area)}</option>`).join("");
  if (STUDIO_CONFIG.localAdmin) {
    select.value = STUDIO_CONFIG.profileId;
    select.disabled = true;
    select.setAttribute("aria-disabled", "true");
    select.title = "この管理画面の事業に固定されています";
  } else {
    const queryProfile = new URLSearchParams(location.search).get("business");
    if (queryProfile && profiles.some((profile) => profile.id === queryProfile)) select.value = queryProfile;
  }
  return profiles;
}

export function configureStudioShell() {
  const blog = $("#studio-nav-blog");
  const reel = $("#studio-nav-reel");
  const back = $("#studio-nav-back");
  const navigation = document.querySelector(".studio-tabs");
  if (blog) blog.href = STUDIO_CONFIG.localAdmin ? "./blog.html" : "/blog";
  if (reel) reel.href = STUDIO_CONFIG.localAdmin ? "./reel.html" : "/reel";
  if (back) {
    back.href = STUDIO_CONFIG.localAdmin ? STUDIO_CONFIG.adminUrl : "/studio";
    back.textContent = STUDIO_CONFIG.localAdmin ? "管理画面へ戻る" : "入口";
  }
  if (navigation) navigation.hidden = STUDIO_CONFIG.localAdmin && STUDIO_CONFIG.embedded;
  document.documentElement.dataset.contentStudioMode = STUDIO_CONFIG.localAdmin ? "local-admin" : "shared-preview";
  document.documentElement.dataset.contentStudioEmbedded = String(STUDIO_CONFIG.embedded);
}
