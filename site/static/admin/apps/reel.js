import { $, api, apiBlob, bindApiKeyPanel, configureStudioShell, escapeHtml, loadProfiles, refreshHealth, requireSession, STUDIO_CONFIG, toast } from "./studio-core.js";

const state = {
  profiles: [],
  profile: null,
  concepts: [],
  draft: null,
  localMedia: [],
  rawVideoBlob: null,
  rawVideoUrl: "",
  finalVideoBlob: null,
  finalVideoUrl: "",
  finalVideoExtension: "",
  coverBlob: null,
  coverUrl: ""
};

const today = () => new Date().toISOString().slice(0, 10);
const textLines = (value) => String(value || "").split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
const slugify = (value) => String(value || "reel").normalize("NFKC").toLowerCase()
  .replace(/[^a-z0-9ぁ-んァ-ヶ一-龠]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50) || "reel";
const isVideoUrl = (value) => /\.(mp4|mov|m4v|webm)(?:[?#].*)?$/i.test(String(value || ""));
const safeHttpUrl = (value) => {
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? url.href : "";
  } catch { return ""; }
};

function revoke(url) { if (url?.startsWith("blob:")) URL.revokeObjectURL(url); }

function clearGeneratedAssets() {
  revoke(state.rawVideoUrl);
  revoke(state.finalVideoUrl);
  revoke(state.coverUrl);
  state.rawVideoBlob = null;
  state.rawVideoUrl = "";
  state.finalVideoBlob = null;
  state.finalVideoUrl = "";
  state.finalVideoExtension = "";
  state.coverBlob = null;
  state.coverUrl = "";
  $("#raw-video-wrap").hidden = true;
  $("#final-video-wrap").hidden = true;
  $("#download-raw-video").hidden = true;
  $("#download-reel-video").hidden = true;
  $("#download-reel-cover").hidden = true;
  $("#reel-video-status").textContent = "";
}

function resetWorkflow({ clearInputs = false } = {}) {
  state.concepts = [];
  state.draft = null;
  clearGeneratedAssets();
  $("#reel-concept-panel").hidden = true;
  $("#reel-approval-panel").hidden = true;
  $("#reel-concepts").innerHTML = "";
  $("#reel-frame-editors").innerHTML = "";
  $("#reel-preview").innerHTML = `<div class="empty-preview"><b>ここに5場面が表示されます</b><p>ブログ、文章、URL、または承認済み動画・画像から企画を作ってください。</p></div>`;
  if (clearInputs) {
    $("#reel-topic").value = "";
    $("#reel-source-text").value = "";
    $("#reel-story").value = "";
    $("#reel-media").value = "";
    $("#reel-files").value = "";
    $("#reel-final-prompt").value = "";
    $("#reel-scheduled-at").value = "";
    state.localMedia.forEach((item) => revoke(item.url));
    state.localMedia = [];
    renderFileStatus();
  }
}

function applyProfile({ reset = false } = {}) {
  state.profile = state.profiles.find((item) => item.id === $("#reel-profile").value) || null;
  if (!state.profile) return;
  if (reset) resetWorkflow({ clearInputs: true });
  $("#reel-audience").value = state.profile.audience || "";
  $("#reel-source-url").value = state.profile.sourceUrls?.[0] || "";
}

function sourceMediaNames() {
  return [...state.localMedia.map((item) => item.file.name), ...textLines($("#reel-media").value)];
}

function payload() {
  return {
    profileId: $("#reel-profile").value,
    topic: $("#reel-topic").value.trim(),
    audience: $("#reel-audience").value.trim(),
    sourceMode: $("#reel-source-mode").value,
    sourceUrl: $("#reel-source-url").value.trim(),
    sourceText: $("#reel-source-text").value.trim(),
    story: $("#reel-story").value.trim(),
    media: sourceMediaNames(),
    finalPrompt: $("#reel-final-prompt").value.trim(),
    scheduledAt: $("#reel-scheduled-at").value || null
  };
}

function validateSources({ forDraft = false } = {}) {
  const input = payload();
  if (!input.topic && !input.sourceText && !input.sourceUrl) return "テーマ、本文、URLのいずれかを入力してください";
  if (!forDraft) return "";
  if (input.sourceMode === "stills" && (input.media.length < 4 || input.media.length > 5)) return "画像モードは承認済み画像を4〜5枚選んでください";
  if (input.sourceMode === "video" && input.media.length !== 1) return "動画モードは承認済み動画を1本だけ選んでください";
  if (input.sourceMode === "generated" && input.media.length > 5) return "生成モードの参考素材は5件以内にしてください";
  return "";
}

async function initialize() {
  if (!await requireSession(initialize)) return;
  bindApiKeyPanel(refreshHealth);
  const [profiles] = await Promise.all([loadProfiles($("#reel-profile")), refreshHealth()]);
  state.profiles = profiles;
  applyProfile();
}

function renderFileStatus() {
  const target = $("#reel-file-status");
  if (!state.localMedia.length) {
    target.textContent = "選択したファイルはブラウザ内だけでプレビューと書き出しに使います。";
    return;
  }
  target.textContent = `${state.localMedia.length}件: ${state.localMedia.map((item) => item.file.name).join(" / ")}`;
}

function onFilesChanged(event) {
  state.localMedia.forEach((item) => revoke(item.url));
  state.localMedia = [...event.target.files].map((file) => ({
    file,
    url: URL.createObjectURL(file),
    type: file.type.startsWith("video/") ? "video" : "image"
  }));
  clearGeneratedAssets();
  renderFileStatus();
}

async function makeConcepts() {
  const validation = validateSources();
  if (validation) return toast(validation);
  resetWorkflow();
  const button = $("#make-reel-concepts");
  button.disabled = true;
  button.textContent = "入力元を確認し、3案を生成中…";
  try {
    const result = await api("/api/reel/generate", { method: "POST", body: JSON.stringify({ ...payload(), mode: "concepts" }) });
    state.concepts = result.concepts || [];
    renderConcepts();
    $("#reel-concept-panel").hidden = false;
    $("#reel-concept-panel").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.textContent = "1. 入力元を調べてリール企画を3案作る"; }
}

function renderConcepts() {
  $("#reel-concepts").innerHTML = state.concepts.map((concept, index) => `
    <article class="choice-card editable-choice reel-concept">
      <label class="choice-select"><input type="radio" name="reel-concept" value="${index}">企画 ${index + 1} を選ぶ</label>
      <label>企画名<input data-concept-field="name" data-index="${index}" value="${escapeHtml(concept.name)}"></label>
      <label>冒頭の一言<textarea data-concept-field="hook" data-index="${index}" rows="2">${escapeHtml(concept.hook)}</textarea></label>
      <label>構成の狙い<textarea data-concept-field="angle" data-index="${index}" rows="3">${escapeHtml(concept.angle)}</textarea></label>
      <label>読者<input data-concept-field="audience" data-index="${index}" value="${escapeHtml(concept.audience)}"></label>
      <label>CTA<textarea data-concept-field="cta" data-index="${index}" rows="2">${escapeHtml(concept.cta)}</textarea></label>
    </article>`).join("");
}

async function makeDraft() {
  const sourceValidation = validateSources({ forDraft: true });
  if (sourceValidation) return toast(sourceValidation);
  const selected = $("input[name='reel-concept']:checked");
  if (!selected) return toast("リール企画を1つ選んでください");
  const selectedConcept = structuredClone(state.concepts[Number(selected.value)]);
  const button = $("#make-reel-draft");
  button.disabled = true;
  button.textContent = "5場面を構成中…";
  try {
    const result = await api("/api/reel/generate", {
      method: "POST",
      body: JSON.stringify({ ...payload(), mode: "draft", selectedConcept })
    });
    state.draft = normalizeDraft(result.reel);
    clearGeneratedAssets();
    renderDraft();
    $("#reel-approval-panel").hidden = false;
    $("#reel-approval-panel").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.textContent = "2. 9:16投稿プレビューを作る"; }
}

function normalizeDraft(draft) {
  const frames = [...(draft?.frames || [])];
  while (frames.length < 5) frames.push({ index: frames.length + 1, text: "内容を入力", duration: 3, media: "", crop: "全画面" });
  return {
    ...draft,
    frames: frames.slice(0, 5).map((frame, index) => ({ ...frame, index: index + 1, duration: 3, text: frame.text || "", crop: frame.crop || "全画面" })),
    cover: { title: draft?.cover?.title || frames[0]?.text || "", media: draft?.cover?.media || frames[0]?.media || "", style: draft?.cover?.style || "" },
    cta: draft?.cta || draft?.selectedConcept?.cta || "",
    sourceUrl: draft?.sourceUrl || payload().sourceUrl,
    instagramCaption: draft?.instagramCaption || "",
    threadsCaption: draft?.threadsCaption || "",
    videoPrompt: draft?.videoPrompt || "",
    approvalChecklist: draft?.approvalChecklist || [],
    manifest: draft?.manifest || { campaign_key: `${state.profile.id}-${today()}-${slugify(payload().topic)}`, timezone: "Asia/Tokyo", mode: "preview", posts: [] }
  };
}

function renderDraft() {
  const draft = state.draft;
  const account = draft.postingAccount || { status: "unregistered" };
  $("#reel-account-status").innerHTML = account.status === "registered"
    ? `<div class="account-status registered"><b>投稿先登録済み</b><span>Instagram: ${escapeHtml(account.instagram?.handle || "未登録")} / Threads: ${escapeHtml(account.threads?.handle || "未登録")}</span></div>`
    : `<div class="account-status warning"><b>投稿先未登録</b><span>判断.mdでこの事業の正式アカウントを登録するまで、投稿画面は開きません。</span></div>`;
  $("#reel-cover-title").value = draft.cover.title;
  $("#reel-cta").value = draft.cta;
  $("#reel-final-url").value = draft.sourceUrl;
  $("#reel-final-scheduled-at").value = payload().scheduledAt || "";
  $("#reel-video-prompt").value = draft.videoPrompt;
  $("#instagram-caption").value = draft.instagramCaption;
  $("#threads-caption").value = draft.threadsCaption;
  $("#reel-frame-editors").innerHTML = `<strong>中央テロップ5つ（各3行以内・各3秒）</strong>${draft.frames.map((frame, index) => `
    <fieldset><legend>場面 ${index + 1}</legend>
      <label>表示テキスト<textarea data-frame-field="text" data-index="${index}" rows="3">${escapeHtml(frame.text)}</textarea><small data-line-count="${index}">${textLines(frame.text).length || 1}行</small></label>
      <label>素材名・URL<input data-frame-field="media" data-index="${index}" value="${escapeHtml(frame.media || "")}"></label>
      <label>切り抜き・構図<textarea data-frame-field="crop" data-index="${index}" rows="2">${escapeHtml(frame.crop)}</textarea></label>
    </fieldset>`).join("")}`;
  $("#reel-approval-list").innerHTML = `<b>公開前チェック</b><ul>${draft.approvalChecklist.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  renderPreview();
}

function localOrRemoteSource(index) {
  const mode = $("#reel-source-mode").value;
  if (state.rawVideoUrl) return { url: state.rawVideoUrl, type: "video" };
  const local = mode === "video" ? state.localMedia[0] : state.localMedia[index] || state.localMedia.at(-1);
  if (local) return { url: local.url, type: local.type };
  const frameValue = state.draft?.frames?.[index]?.media || textLines($("#reel-media").value)[mode === "video" ? 0 : index];
  const url = safeHttpUrl(frameValue);
  if (url) return { url, type: isVideoUrl(url) || mode === "video" ? "video" : "image" };
  return { url: "", type: "none" };
}

function sourceElement(source) {
  if (!source.url) return `<div class="reel-media-placeholder"><span>背景素材を準備</span></div>`;
  return source.type === "video"
    ? `<video src="${escapeHtml(source.url)}" muted loop playsinline autoplay></video>`
    : `<img src="${escapeHtml(source.url)}" alt="" crossorigin="anonymous">`;
}

function renderPreview() {
  if (!state.draft) return;
  $("#reel-preview").innerHTML = state.draft.frames.map((frame, index) => {
    const source = localOrRemoteSource(index);
    return `<article class="reel-phone-frame">${sourceElement(source)}<div class="reel-shade"></div><div class="reel-safe-area"><span>${escapeHtml(state.profile.name)} · ${index + 1}/5</span><strong>${escapeHtml(frame.text).replace(/\n/g, "<br>")}</strong><small>${escapeHtml(state.draft.sourceUrl || "公開前プレビュー")}</small></div></article>`;
  }).join("");
}

function invalidateFinalRender() {
  if (!state.finalVideoBlob && !state.coverBlob) return;
  revoke(state.finalVideoUrl);
  revoke(state.coverUrl);
  state.finalVideoBlob = null;
  state.finalVideoUrl = "";
  state.coverBlob = null;
  state.coverUrl = "";
  $("#final-video-wrap").hidden = true;
  $("#download-reel-video").hidden = true;
  $("#download-reel-cover").hidden = true;
  $("#reel-video-status").textContent = "編集内容が変わりました。完成動画をもう一度焼き込んでください。";
}

function updateFrame(event) {
  if (!state.draft || !event.target.dataset.frameField) return;
  const index = Number(event.target.dataset.index);
  state.draft.frames[index][event.target.dataset.frameField] = event.target.value;
  if (event.target.dataset.frameField === "text") {
    const count = textLines(event.target.value).length || 1;
    const label = $(`[data-line-count='${index}']`);
    label.textContent = `${count}行${count > 3 ? "・3行以内にしてください" : ""}`;
    label.classList.toggle("error", count > 3);
  }
  invalidateFinalRender();
  syncManifest();
  renderPreview();
}

function syncEditableMeta(event) {
  if (!state.draft) return;
  const map = {
    "reel-cover-title": () => { state.draft.cover.title = event.target.value; },
    "reel-cta": () => { state.draft.cta = event.target.value; },
    "reel-final-url": () => { state.draft.sourceUrl = event.target.value.trim(); },
    "reel-video-prompt": () => { state.draft.videoPrompt = event.target.value; },
    "instagram-caption": () => { state.draft.instagramCaption = event.target.value; },
    "threads-caption": () => { state.draft.threadsCaption = event.target.value; }
  };
  map[event.target.id]?.();
  invalidateFinalRender();
  syncManifest();
  renderPreview();
}

function syncManifest() {
  if (!state.draft?.manifest) return;
  const scheduledAt = $("#reel-final-scheduled-at").value || null;
  state.draft.manifest.source_mode = $("#reel-source-mode").value;
  state.draft.manifest.final_prompt = $("#reel-final-prompt").value.trim();
  state.draft.manifest.frames = state.draft.frames.map((frame) => ({ index: frame.index, duration: 3, text: frame.text, media: frame.media, crop: frame.crop }));
  state.draft.manifest.cover = { ...state.draft.cover };
  for (const post of state.draft.manifest.posts || []) {
    post.scheduled_at = scheduledAt;
    post.cta = state.draft.cta;
    post.source_refs = state.draft.sourceUrl ? [state.draft.sourceUrl] : [];
    if (post.platform === "instagram") post.caption = state.draft.instagramCaption;
    if (post.platform === "threads") post.caption = state.draft.threadsCaption;
  }
}

async function generateVideo() {
  if (!state.draft) return toast("先にリール下書きを作成してください");
  if ($("#reel-source-mode").value !== "generated") return toast("Sora背景動画は、背景素材の作り方を『内容から背景動画を生成』にした場合だけ使います");
  const prompt = $("#reel-video-prompt").value.trim();
  if (!prompt) return toast("背景動画の生成プロンプトを入力してください");
  const button = $("#generate-reel-video");
  const status = $("#reel-video-status");
  button.disabled = true;
  status.textContent = "Sora 2 Proで12秒・縦型の背景動画を生成しています…";
  try {
    const result = await api("/api/reel/video", { method: "POST", body: JSON.stringify({ profileId: state.profile.id, sourceMode: "generated", prompt }) });
    if (result.mock) { status.textContent = result.message; return; }
    let video = result.video;
    while (!["completed", "failed"].includes(video.status)) {
      await new Promise((resolve) => setTimeout(resolve, 5000));
      const progress = await api(`/api/reel/video-status?id=${encodeURIComponent(video.id)}&profileId=${encodeURIComponent(state.profile.id)}`);
      video = progress.video;
      status.textContent = `背景動画を生成中… ${video.progress || 0}%`;
    }
    if (video.status !== "completed") throw new Error(video.error?.message || "背景動画を生成できませんでした");
    state.rawVideoBlob = await apiBlob(`/api/reel/video-content?id=${encodeURIComponent(video.id)}&profileId=${encodeURIComponent(state.profile.id)}`);
    revoke(state.rawVideoUrl);
    state.rawVideoUrl = URL.createObjectURL(state.rawVideoBlob);
    $("#reel-video-result").src = state.rawVideoUrl;
    $("#raw-video-wrap").hidden = false;
    const download = $("#download-raw-video");
    download.href = state.rawVideoUrl;
    download.download = `reel-background-${state.profile.id}-${today()}.mp4`;
    download.hidden = false;
    status.textContent = "背景動画が完成しました。次に5場面テロップを焼き込んでください。";
    invalidateFinalRender();
    renderPreview();
  } catch (error) { status.textContent = error.message; toast(error.message); }
  finally { button.disabled = false; }
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    if (!url.startsWith("blob:")) image.crossOrigin = "anonymous";
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("画像を読み込めません。CORS対応URLまたはローカル画像を選んでください。"));
    image.src = url;
  });
}

function loadVideo(url) {
  return new Promise((resolve, reject) => {
    const video = document.createElement("video");
    if (!url.startsWith("blob:")) video.crossOrigin = "anonymous";
    video.src = url;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "auto";
    video.addEventListener("loadeddata", () => resolve(video), { once: true });
    video.addEventListener("error", () => reject(new Error("動画を読み込めません。MP4またはローカル動画を選んでください。")), { once: true });
    video.load();
  });
}

async function prepareRenderSources() {
  const unique = new Map();
  for (let index = 0; index < 5; index += 1) {
    const source = localOrRemoteSource(index);
    if (!source.url) throw new Error(`場面${index + 1}の背景素材がありません`);
    if (!unique.has(source.url)) unique.set(source.url, { ...source, element: null });
  }
  for (const item of unique.values()) item.element = item.type === "video" ? await loadVideo(item.url) : await loadImage(item.url);
  return [...Array(5)].map((_, index) => unique.get(localOrRemoteSource(index).url));
}

function drawCover(ctx, element, type) {
  const canvas = ctx.canvas;
  const sourceWidth = type === "video" ? element.videoWidth : element.naturalWidth;
  const sourceHeight = type === "video" ? element.videoHeight : element.naturalHeight;
  const scale = Math.max(canvas.width / sourceWidth, canvas.height / sourceHeight);
  const width = sourceWidth * scale;
  const height = sourceHeight * scale;
  ctx.drawImage(element, (canvas.width - width) / 2, (canvas.height - height) / 2, width, height);
}

function wrapAtWidth(ctx, value, maxWidth) {
  const explicit = String(value || "").split(/\r?\n/);
  const output = [];
  for (const raw of explicit) {
    const characters = [...raw.trim()];
    let line = "";
    for (const character of characters) {
      const test = line + character;
      if (line && ctx.measureText(test).width > maxWidth) { output.push(line); line = character; }
      else line = test;
    }
    if (line) output.push(line);
  }
  return output.length ? output : [""];
}

function fitText(ctx, value) {
  let fontSize = 86;
  let wrapped = [];
  while (fontSize >= 52) {
    ctx.font = `900 ${fontSize}px "Yu Gothic", "Noto Sans JP", sans-serif`;
    wrapped = wrapAtWidth(ctx, value, 900);
    if (wrapped.length <= 3) break;
    fontSize -= 4;
  }
  if (wrapped.length > 3) {
    wrapped = wrapped.slice(0, 3);
    let last = wrapped[2];
    while (last.length && ctx.measureText(`${last}…`).width > 900) last = last.slice(0, -1);
    wrapped[2] = `${last}…`;
  }
  return { fontSize, lines: wrapped };
}

function drawTextOverlay(ctx, value) {
  const { fontSize, lines: wrapped } = fitText(ctx, value);
  const lineHeight = fontSize * 1.38;
  const startY = 960 - ((wrapped.length - 1) * lineHeight) / 2;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.lineJoin = "round";
  ctx.miterLimit = 2;
  ctx.strokeStyle = "#000";
  ctx.fillStyle = "#fff";
  ctx.lineWidth = Math.max(10, fontSize * .16);
  for (let index = 0; index < wrapped.length; index += 1) {
    const y = startY + index * lineHeight;
    ctx.strokeText(wrapped[index], 540, y, 920);
    ctx.fillText(wrapped[index], 540, y, 920);
  }
}

function recorderMimeType() {
  return ["video/mp4;codecs=avc1.42E01E", "video/mp4", "video/webm;codecs=vp9", "video/webm"]
    .find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

async function canvasToBlob(canvas, type = "image/png") {
  return new Promise((resolve, reject) => canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("画像を書き出せませんでした")), type));
}

async function renderFinalReel() {
  if (!state.draft) return toast("先にリール下書きを作成してください");
  const invalidFrame = state.draft.frames.findIndex((frame) => !frame.text.trim() || textLines(frame.text).length > 3);
  if (invalidFrame >= 0) return toast(`場面${invalidFrame + 1}の文字を1〜3行にしてください`);
  if (!window.MediaRecorder || !HTMLCanvasElement.prototype.captureStream) return toast("このブラウザは動画書き出しに対応していません。最新版のChromeまたはEdgeを使ってください。");
  const button = $("#render-final-reel");
  const status = $("#reel-video-status");
  button.disabled = true;
  status.textContent = "背景素材を読み込んでいます…";
  try {
    const sources = await prepareRenderSources();
    for (const source of new Set(sources.filter((item) => item.type === "video"))) await source.element.play();
    const canvas = document.createElement("canvas");
    canvas.width = 1080;
    canvas.height = 1920;
    const ctx = canvas.getContext("2d", { alpha: false });
    const mimeType = recorderMimeType();
    if (!mimeType) throw new Error("投稿動画のエンコード方式を利用できません");
    const stream = canvas.captureStream(30);
    const recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 10_000_000 });
    const chunks = [];
    recorder.addEventListener("dataavailable", (event) => { if (event.data.size) chunks.push(event.data); });
    const completed = new Promise((resolve, reject) => {
      recorder.addEventListener("stop", resolve, { once: true });
      recorder.addEventListener("error", () => reject(recorder.error || new Error("動画を書き出せませんでした")), { once: true });
    });
    recorder.start(1000);
    const duration = 15_000;
    const started = performance.now();
    let lastFrameIndex = -1;
    await new Promise((resolve) => {
      const draw = (now) => {
        const elapsed = Math.min(now - started, duration);
        const frameIndex = Math.min(4, Math.floor(elapsed / 3000));
        const source = sources[frameIndex];
        ctx.fillStyle = "#1d2a24";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawCover(ctx, source.element, source.type);
        const gradient = ctx.createLinearGradient(0, 0, 0, 1920);
        gradient.addColorStop(0, "rgba(0,0,0,.16)");
        gradient.addColorStop(.55, "rgba(0,0,0,.26)");
        gradient.addColorStop(1, "rgba(0,0,0,.42)");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 1080, 1920);
        drawTextOverlay(ctx, state.draft.frames[frameIndex].text);
        if (frameIndex !== lastFrameIndex) {
          status.textContent = `場面 ${frameIndex + 1}/5 を焼き込み中…`;
          lastFrameIndex = frameIndex;
        }
        if (elapsed >= duration) resolve();
        else requestAnimationFrame(draw);
      };
      requestAnimationFrame(draw);
    });
    recorder.stop();
    await completed;
    state.finalVideoBlob = new Blob(chunks, { type: mimeType.split(";")[0] });
    revoke(state.finalVideoUrl);
    state.finalVideoUrl = URL.createObjectURL(state.finalVideoBlob);
    state.finalVideoExtension = mimeType.startsWith("video/mp4") ? "mp4" : "webm";
    $("#reel-final-video").src = state.finalVideoUrl;
    $("#final-video-wrap").hidden = false;
    const download = $("#download-reel-video");
    download.href = state.finalVideoUrl;
    download.download = `reel-final-${state.profile.id}-${today()}.${state.finalVideoExtension}`;
    download.hidden = false;

    ctx.fillStyle = "#1d2a24";
    ctx.fillRect(0, 0, 1080, 1920);
    drawCover(ctx, sources[0].element, sources[0].type);
    ctx.fillStyle = "rgba(0,0,0,.3)";
    ctx.fillRect(0, 0, 1080, 1920);
    drawTextOverlay(ctx, state.draft.cover.title);
    state.coverBlob = await canvasToBlob(canvas);
    revoke(state.coverUrl);
    state.coverUrl = URL.createObjectURL(state.coverBlob);
    const coverDownload = $("#download-reel-cover");
    coverDownload.href = state.coverUrl;
    coverDownload.download = `reel-cover-${state.profile.id}-${today()}.png`;
    coverDownload.hidden = false;
    syncManifest();
    state.draft.manifest.final_video = download.download;
    state.draft.manifest.cover_image = coverDownload.download;
    status.textContent = state.finalVideoExtension === "mp4"
      ? "完成MP4を書き出しました。全5場面の文字・映像・本文を確認してください。"
      : "テロップ焼き込みは完了しましたがWebM形式です。Instagram投稿前にMP4へ変換してください。";
  } catch (error) { status.textContent = error.message; toast(error.message); }
  finally { button.disabled = false; }
}

function captionsReady() {
  const url = state.draft.sourceUrl.trim();
  if (!url) return "本文末尾URLを入力してください";
  if (!state.draft.instagramCaption.trim().endsWith(url)) return "Instagramキャプションの最後を本文末尾URLにしてください";
  if (!state.draft.threadsCaption.trim().endsWith(url)) return "Threads本文の最後を本文末尾URLにしてください";
  return "";
}

async function prepareChromePost(platform) {
  if (!state.draft) return toast("先にリール投稿プレビューを作成してください");
  if (!state.finalVideoBlob) return toast("先に5場面テロップを焼き込んだ完成動画を作ってください");
  if (state.finalVideoExtension !== "mp4") return toast("Instagram投稿用にMP4形式の完成動画が必要です");
  const captionError = captionsReady();
  if (captionError) return toast(captionError);
  if (!$("#chrome-post-confirm").checked) return toast("投稿先、完成動画、本文、末尾URLの確認にチェックしてください");
  const account = state.draft.postingAccount;
  if (account?.status !== "registered") return toast("判断.mdで投稿先アカウントを確定してください");
  const caption = platform === "instagram" ? state.draft.instagramCaption : state.draft.threadsCaption;
  await navigator.clipboard.writeText(caption);
  const target = platform === "instagram" ? account.instagram?.url || "https://www.instagram.com/" : account.threads?.url || "https://www.threads.net/";
  window.open(target, "_blank", "noopener,noreferrer");
  $("#chrome-post-status").textContent = `${platform === "instagram" ? "Instagram" : "Threads"}本文をコピーし、正式アカウントを開きました。完成MP4を選び、最終シェア前で止めて確認してください。`;
}

async function copyValue(selector, label) {
  const value = $(selector).value;
  if (!value) return toast(`${label}がありません`);
  await navigator.clipboard.writeText(value);
  toast(`${label}をコピーしました`);
}

function packageData() {
  syncManifest();
  return {
    version: 1,
    schema: "content-studio.reel-draft",
    schemaVersion: 1,
    kind: "reel",
    createdAt: new Date().toISOString(),
    profile: state.profile,
    input: payload(),
    selectedConcept: state.draft.selectedConcept,
    frames: state.draft.frames,
    cover: state.draft.cover,
    instagramCaption: state.draft.instagramCaption,
    threadsCaption: state.draft.threadsCaption,
    sourceUrl: state.draft.sourceUrl,
    cta: state.draft.cta,
    videoPrompt: state.draft.videoPrompt,
    finalPrompt: $("#reel-final-prompt").value.trim(),
    manifest: state.draft.manifest
  };
}

function handoffReelDraft() {
  if (!STUDIO_CONFIG.localAdmin) return toast("下書きの受け渡しは各サイトの管理画面版で使用してください");
  if (!state.draft) return toast("先にリール投稿プレビューを作成してください");
  try {
    const key = `contentStudioReelDraft:${state.profile.id}`;
    localStorage.setItem(key, JSON.stringify(packageData()));
    toast("管理画面へリール下書きを渡しました");
    window.location.assign(STUDIO_CONFIG.adminUrl);
  } catch (error) {
    toast(`リール下書きを渡せませんでした: ${error.message}`);
  }
}

function downloadBlob(blob, filename) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

function downloadManifest() {
  if (!state.draft) return toast("先にリール投稿プレビューを作成してください");
  downloadBlob(new Blob([JSON.stringify(packageData(), null, 2)], { type: "application/json" }), `${state.draft.manifest.campaign_key}.json`);
}

async function nestedDirectory(root, segments) {
  let current = root;
  for (const segment of segments) current = await current.getDirectoryHandle(segment, { create: true });
  return current;
}

async function writeFile(directory, name, content) {
  const file = await directory.getFileHandle(name, { create: true });
  const writable = await file.createWritable();
  await writable.write(content);
  await writable.close();
}

async function saveReelPackage() {
  if (!state.draft) return toast("先にリール投稿プレビューを作成してください");
  if (!window.showDirectoryPicker) return toast("ChromeまたはEdgeで開き、保存先の事業フォルダを選択してください");
  try {
    const root = await window.showDirectoryPicker({ mode: "readwrite", id: `reel-${state.profile.id}` });
    const campaignName = state.draft.manifest.campaign_key || `${state.profile.id}-${today()}-${slugify(payload().topic)}`;
    const directory = await nestedDirectory(root, ["content", "campaigns", campaignName]);
    await writeFile(directory, "README.md", `# ${payload().topic || state.draft.cover.title}\n\n- 事業: ${state.profile.name}\n- 対象: ${payload().audience}\n- 状態: 投稿前下書き\n- 形式: 1080×1920 / 5場面 / 各3秒\n- 次の作業: 完成MP4確認、正式アカウント確認、明示承認、投稿URL追記\n`);
    await writeFile(directory, "source.md", `# 入力元\n\nURL: ${state.draft.sourceUrl}\n\n## 元テキスト\n\n${payload().sourceText}\n\n## 事業者の言葉\n\n${payload().story}\n`);
    await writeFile(directory, "storyboard.json", JSON.stringify(packageData(), null, 2));
    await writeFile(directory, "captions.md", `# Instagram\n\n${state.draft.instagramCaption}\n\n# Threads\n\n${state.draft.threadsCaption}\n`);
    await writeFile(directory, "prompts.md", `# 背景動画\n\n${state.draft.videoPrompt}\n\n# 最終調整\n\n${$("#reel-final-prompt").value.trim()}\n`);
    const assets = await directory.getDirectoryHandle("assets", { create: true });
    for (const item of state.localMedia) await writeFile(assets, item.file.name, item.file);
    if (state.rawVideoBlob) await writeFile(assets, "background.mp4", state.rawVideoBlob);
    if (state.finalVideoBlob) await writeFile(directory, `reel-final.${state.finalVideoExtension}`, state.finalVideoBlob);
    if (state.coverBlob) await writeFile(directory, "cover.png", state.coverBlob);
    toast(`content/campaigns/${campaignName} に保存しました`);
  } catch (error) {
    if (error.name !== "AbortError") toast(`保存できませんでした: ${error.message}`);
  }
}

$("#reel-profile").addEventListener("change", () => applyProfile({ reset: true }));
$("#reel-files").addEventListener("change", onFilesChanged);
$("#reel-source-mode").addEventListener("change", () => { clearGeneratedAssets(); renderPreview(); });
$("#make-reel-concepts").addEventListener("click", makeConcepts);
$("#make-reel-draft").addEventListener("click", makeDraft);
$("#reel-concepts").addEventListener("input", (event) => {
  if (!event.target.dataset.conceptField) return;
  state.concepts[Number(event.target.dataset.index)][event.target.dataset.conceptField] = event.target.value;
});
$("#reel-frame-editors").addEventListener("input", updateFrame);
for (const id of ["reel-cover-title", "reel-cta", "reel-final-url", "reel-video-prompt", "instagram-caption", "threads-caption"]) $("#" + id).addEventListener("input", syncEditableMeta);
$("#reel-final-scheduled-at").addEventListener("input", syncManifest);
$("#copy-instagram").addEventListener("click", () => copyValue("#instagram-caption", "Instagram本文"));
$("#copy-threads").addEventListener("click", () => copyValue("#threads-caption", "Threads本文"));
$("#download-manifest").addEventListener("click", downloadManifest);
$("#save-reel-package").addEventListener("click", saveReelPackage);
$("#handoff-reel-draft").addEventListener("click", handoffReelDraft);
$("#generate-reel-video").addEventListener("click", generateVideo);
$("#render-final-reel").addEventListener("click", renderFinalReel);
$("#prepare-chrome-instagram").addEventListener("click", () => prepareChromePost("instagram"));
$("#prepare-chrome-threads").addEventListener("click", () => prepareChromePost("threads"));

configureStudioShell();
initialize().catch((error) => { $("#server-state").textContent = "接続エラー"; toast(error.message); });
