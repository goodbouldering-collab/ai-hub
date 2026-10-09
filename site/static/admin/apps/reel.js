import { $, api, apiBlob, bindApiKeyPanel, configureStudioShell, escapeHtml, handoffToAdmin, loadProfiles, refreshHealth, requireSession, STUDIO_CONFIG, toast } from "./studio-core.js";

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
  coverUrl: "",
  squareBlob: null,
  squareUrl: "",
  research: null,
  narrationFiles: new Map(),
  rendering: false
};

const today = () => new Date().toISOString().slice(0, 10);
const textLines = (value) => String(value || "").split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
const speechWords = (value) => String(value || "").replace(/[\r\n\p{P}]/gu, "");
const readingSeconds = (value) => Math.max(3, Math.ceil(([...String(value || "").replace(/\s/g, "")].length / 5 + 1.5) * 10) / 10);
const durationOf = (frame) => Math.max(readingSeconds(frame.text), Number(frame.duration) || 0);
const totalSeconds = () => Math.round(state.draft.frames.reduce((sum, frame) => sum + durationOf(frame), 0) * 10) / 10;

function researchInput() {
  const reviewed = $("#reel-research-reviewed").checked;
  return {
    observations: textLines($("#reel-research-urls").value).map((url) => ({ url, checkedAt: reviewed ? new Date().toISOString() : "", video: reviewed, audio: reviewed, caption: reviewed })),
    keep: $("#reel-research-keep").value.trim(), change: $("#reel-research-change").value.trim(),
    reason: $("#reel-research-change").value.trim(), webSources: state.research?.webSources || []
  };
}

function resetApproval() {
  for (const id of ["chrome-post-confirm", "reel-visual-qa", "reel-audio-qa", "reel-url-qa", "reel-blog-live-checked"]) $("#" + id).checked = false;
  if (state.draft?.manifest) delete state.draft.manifest.publication_review;
}
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
  invalidateFinalRender();
  revoke(state.rawVideoUrl);
  revoke(state.finalVideoUrl);
  revoke(state.coverUrl);
  revoke(state.squareUrl);
  state.rawVideoBlob = null;
  state.rawVideoUrl = "";
  state.finalVideoBlob = null;
  state.finalVideoUrl = "";
  state.finalVideoExtension = "";
  state.coverBlob = null;
  state.coverUrl = "";
  state.squareBlob = null;
  state.squareUrl = "";
  $("#raw-video-wrap").hidden = true;
  $("#final-video-wrap").hidden = true;
  $("#download-raw-video").hidden = true;
  $("#download-reel-video").hidden = true;
  $("#download-reel-cover").hidden = true;
  $("#download-reel-square").hidden = true;
  $("#reel-cover-preview").hidden = true;
  resetApproval();
  $("#reel-video-status").textContent = "";
}

function resetWorkflow({ clearInputs = false } = {}) {
  state.concepts = [];
  state.draft = null;
  state.narrationFiles.clear();
  clearGeneratedAssets();
  $("#reel-concept-panel").hidden = true;
  $("#reel-approval-panel").hidden = true;
  $("#reel-concepts").innerHTML = "";
  $("#reel-frame-editors").innerHTML = "";
  $("#reel-preview").innerHTML = `<div class="empty-preview"><b>ここに場面ごとのプレビューが表示されます</b><p>ブログ、文章、URL、または承認済み動画・画像から企画を作ってください。</p></div>`;
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
    state.research = null;
    for (const id of ["reel-research-urls", "reel-research-keep", "reel-research-change", "reel-blog-live-url", "reel-blog-video-url", "reel-blog-cover-url"]) $("#" + id).value = "";
    $("#reel-research-reviewed").checked = false;
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
    blogLinked: $("#reel-blog-linked").checked,
    audioMode: $("#reel-audio-mode").value,
    research: researchInput(),
    finalPrompt: $("#reel-final-prompt").value.trim(),
    scheduledAt: $("#reel-scheduled-at").value || null
  };
}

function validateSources({ forDraft = false } = {}) {
  const input = payload();
  if (!input.topic && !input.sourceText && !input.sourceUrl) return "テーマ、本文、URLのいずれかを入力してください";
  if (!forDraft) return "";
  if (input.sourceMode === "stills" && (input.media.length < 1 || input.media.length > 20)) return "画像モードは承認済み画像を1〜20枚選んでください";
  if (input.sourceMode === "video" && input.media.length !== 1) return "動画モードは承認済み動画を1本だけ選んでください";
  if (input.sourceMode === "generated" && input.media.length) return "生成モードでは画像・動画の選択を外してください";
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
    state.research = result.research || null;
    renderConcepts();
    $("#reel-concept-panel").hidden = false;
    $("#reel-concept-panel").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.textContent = "1. 入力元を調べてリール企画を3案作る"; }
}

function renderConcepts() {
  $("#reel-concepts").innerHTML = state.concepts.map((concept, index) => `
    <article class="choice-card editable-choice reel-concept">
      <label class="choice-select"><input type="radio" name="reel-concept" value="${index}" ${index === 0 ? "checked" : ""}>企画 ${index + 1}${index === 0 ? "（推奨）" : ""} を選ぶ</label>
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
  button.textContent = "全文を読み切れる場面を構成中…";
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
  return {
    ...draft,
    frames: frames.map((frame, index) => ({ ...frame, index: index + 1, duration: durationOf(frame), text: frame.text || "", narration_text: frame.narration_text ?? frame.text.replace(/\n/g, ""), crop: frame.crop || "全画面", focalX: 50, focalY: 50 })),
    cover: { ...draft?.cover, title: draft?.cover?.title || "", sourceIndex: 0 },
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
  $("#reel-story-caption").value = draft.storyCaption || "";
  $("#reel-shop-comment").value = draft.shopComment || "";
  $("#reel-blog-review").hidden = !draft.blogLinked;
  $("#reel-cover-source").innerHTML = draft.frames.map((_, index) => `<option value="${index}">場面 ${index + 1} の素材</option>`).join("");
  $("#reel-cover-source").value = String(draft.cover.sourceIndex || 0);
  const observations = draft.research?.observations || [];
  const complete = observations.length >= 2 && observations.every((item) => item.video && item.audio && item.caption && item.checkedAt);
  $("#reel-research-status").innerHTML = `<b>${complete ? "過去投稿の確認記録あり（担当者申告）" : "過去投稿の映像・音声・本文の確認が未完了"}</b><p>${escapeHtml(state.research?.note || draft.research?.note || "今回の公式投稿調査を入力してください")}</p>${(draft.research?.webSources || []).map((item) => `<a href="${escapeHtml(safeHttpUrl(item.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title || item.url)}</a>`).join(" / ")}`;
  renderFrameEditors();
  $("#reel-approval-list").innerHTML = `<b>公開前チェック</b><ul>${draft.approvalChecklist.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  renderPreview();
}

function renderFrameEditors() {
  $("#reel-frame-editors").innerHTML = `<strong>中央の大きな文字（各3行以内・短く収まらなければ場面を追加）</strong>${state.draft.frames.map((frame, index) => `
    <fieldset><legend>場面 ${index + 1}</legend>
      <label>表示テキスト<textarea data-frame-field="text" data-index="${index}" rows="3">${escapeHtml(frame.text)}</textarea><small data-line-count="${index}">${textLines(frame.text).length || 1}行</small></label>
      <label>全文読み上げ台本<textarea data-frame-field="narration_text" data-index="${index}" rows="3">${escapeHtml(frame.narration_text)}</textarea></label>
      <label>表示秒数（読み上げ速度を上げず自動延長）<input type="number" min="3" step="0.1" data-frame-field="duration" data-index="${index}" value="${durationOf(frame)}"></label>
      <label>この場面のナレーション音声<input type="file" accept="audio/*" data-narration-index="${index}"><small>${escapeHtml(state.narrationFiles.get(index)?.name || "未選択・音声生成は未実装")}</small></label>
      <label>素材名・URL<input data-frame-field="media" data-index="${index}" value="${escapeHtml(frame.media || "")}"></label>
      <label>主役の横位置（0〜100%）<input type="number" min="0" max="100" data-frame-field="focalX" data-index="${index}" value="${frame.focalX ?? 50}"></label>
      <label>主役の縦位置（0〜100%）<input type="number" min="0" max="100" data-frame-field="focalY" data-index="${index}" value="${frame.focalY ?? 50}"></label>
      <label>切り抜き・構図<textarea data-frame-field="crop" data-index="${index}" rows="2">${escapeHtml(frame.crop)}</textarea></label>
    </fieldset>`).join("")}`;
}

function localOrRemoteSource(index) {
  const mode = $("#reel-source-mode").value;
  if (state.rawVideoUrl) return { url: state.rawVideoUrl, type: "video" };
  const frameValue = state.draft?.frames?.[index]?.media;
  const local = mode === "video" ? state.localMedia.find((item) => item.file.name === frameValue) || state.localMedia[0] : state.localMedia.find((item) => item.file.name === frameValue);
  if (local) return { url: local.url, type: local.type };
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
  $("#reel-duration-summary").textContent = `1080 × 1920・${state.draft.frames.length}場面・${totalSeconds()}秒（音声が長い場合は延長）`;
  $("#reel-preview").innerHTML = state.draft.frames.map((frame, index) => {
    const source = localOrRemoteSource(index);
    return `<article class="reel-phone-frame" style="--focal-x:${Math.max(0, Math.min(100, Number(frame.focalX) || 50))}%;--focal-y:${Math.max(0, Math.min(100, Number(frame.focalY) || 50))}%">${sourceElement(source)}<div class="reel-shade"></div><div class="reel-safe-area"><span>${escapeHtml(state.profile.name)} · ${index + 1}/${state.draft.frames.length} · ${durationOf(frame)}秒</span><strong>${escapeHtml(frame.text).replace(/\n/g, "<br>")}</strong><small>${escapeHtml(state.draft.sourceUrl || "公開前プレビュー")}</small></div></article>`;
  }).join("");
}

function invalidateFinalRender() {
  resetApproval();
  if (state.draft?.manifest) {
    delete state.draft.manifest.final_video;
    delete state.draft.manifest.cover_image;
    delete state.draft.manifest.square_qa_image;
    for (const post of state.draft.manifest.posts || []) for (const media of post.media || []) { media.path = null; media.status = "pending_render"; }
  }
  if (!state.finalVideoBlob && !state.coverBlob) return;
  revoke(state.finalVideoUrl);
  revoke(state.coverUrl);
  revoke(state.squareUrl);
  state.finalVideoBlob = null;
  state.finalVideoUrl = "";
  state.coverBlob = null;
  state.coverUrl = "";
  state.squareBlob = null;
  state.squareUrl = "";
  $("#final-video-wrap").hidden = true;
  $("#download-reel-video").hidden = true;
  $("#download-reel-cover").hidden = true;
  $("#download-reel-square").hidden = true;
  $("#reel-cover-preview").hidden = true;
  if (state.draft?.manifest) {
    delete state.draft.manifest.final_video;
    delete state.draft.manifest.cover_image;
    for (const post of state.draft.manifest.posts || []) for (const media of post.media || []) { media.path = null; media.status = "pending_render"; }
    state.draft.audio.bgm.qa = "pending_render_and_listening";
  }
  $("#reel-video-status").textContent = "編集内容が変わりました。完成動画をもう一度焼き込んでください。";
}

function updateFrame(event) {
  if (!state.draft || !event.target.dataset.frameField) return;
  const index = Number(event.target.dataset.index);
  state.draft.frames[index][event.target.dataset.frameField] = event.target.value;
  if (event.target.dataset.frameField === "text") {
    state.draft.frames[index].center_text = event.target.value;
    state.draft.frames[index].narration_text = event.target.value.replace(/\n/g, "");
    $(`[data-frame-field='narration_text'][data-index='${index}']`).value = state.draft.frames[index].narration_text;
    state.narrationFiles.delete(index);
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
    "threads-caption": () => { state.draft.threadsCaption = event.target.value; },
    "reel-story-caption": () => { state.draft.storyCaption = event.target.value; },
    "reel-shop-comment": () => { state.draft.shopComment = event.target.value; },
    "reel-cover-source": () => { state.draft.cover.sourceIndex = Number(event.target.value); }
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
  state.draft.durationSeconds = totalSeconds();
  state.draft.manifest.duration_seconds = totalSeconds();
  state.draft.manifest.frames = state.draft.frames.map((frame) => ({ ...frame, duration: durationOf(frame), center_text: frame.text, narration_match: speechWords(frame.text) === speechWords(frame.narration_text) }));
  state.draft.manifest.research = { ...state.draft.research, ...researchInput() };
  state.draft.manifest.audio = state.draft.audio;
  state.draft.manifest.qa = { visual: $("#reel-visual-qa").checked ? "operator-confirmed" : "pending", listening: $("#reel-audio-qa").checked ? "operator-confirmed" : "pending", url: $("#reel-url-qa").checked ? "operator-confirmed" : "pending" };
  const embed = state.draft.manifest.blog_embed ||= { required: state.draft.blogLinked, same_mp4: true, same_cover: true };
  Object.assign(embed, { article_url: $("#reel-blog-live-url").value, video_url: $("#reel-blog-video-url").value, cover_url: $("#reel-blog-cover-url").value, status: $("#reel-blog-live-checked").checked ? "operator-confirmed" : "unverified" });
  state.draft.manifest.cover = { ...state.draft.cover };
  for (const post of state.draft.manifest.posts || []) {
    post.scheduled_at = scheduledAt;
    post.cta = state.draft.cta;
    post.source_refs = state.draft.sourceUrl ? [state.draft.sourceUrl] : [];
    if (post.kind === "reel") post.caption = state.draft.instagramCaption;
    if (post.kind === "story") { post.caption = state.draft.storyCaption; post.link.url = state.draft.sourceUrl; post.link.status = $("#reel-url-qa").checked ? "operator-confirmed" : "unverified"; }
    if (post.kind === "shop_comment") post.caption = state.draft.shopComment;
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
    status.textContent = "背景動画が完成しました。全場面の文字を焼き込むときは、読み切れる尺まで通常速度で繰り返します。";
    invalidateFinalRender();
    renderPreview();
  } catch (error) { invalidateFinalRender(); status.textContent = error.message; toast(error.message); }
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
  for (let index = 0; index < state.draft.frames.length; index += 1) {
    const source = localOrRemoteSource(index);
    if (!source.url) throw new Error(`場面${index + 1}の背景素材がありません`);
    if (!unique.has(source.url)) unique.set(source.url, { ...source, element: null });
  }
  for (const item of unique.values()) item.element = item.type === "video" ? await loadVideo(item.url) : await loadImage(item.url);
  return state.draft.frames.map((_, index) => unique.get(localOrRemoteSource(index).url));
}

function drawCover(ctx, element, type, focalX = 50, focalY = 50) {
  const canvas = ctx.canvas;
  const sourceWidth = type === "video" ? element.videoWidth : element.naturalWidth;
  const sourceHeight = type === "video" ? element.videoHeight : element.naturalHeight;
  const scale = Math.max(canvas.width / sourceWidth, canvas.height / sourceHeight);
  const width = sourceWidth * scale;
  const height = sourceHeight * scale;
  ctx.drawImage(element, (canvas.width - width) * Math.max(0, Math.min(100, focalX)) / 100, (canvas.height - height) * Math.max(0, Math.min(100, focalY)) / 100, width, height);
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
  const fontSize = 90;
  ctx.font = `900 ${fontSize}px "Yu Gothic", "Noto Sans JP", sans-serif`;
  const wrapped = wrapAtWidth(ctx, value, 860);
  if (wrapped.length > 3) throw new Error("中央文字が大きな3行に収まりません。文字を短くするか、場面を追加してください。縮小・省略はしません。");
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
  return ["video/mp4;codecs=avc1.42E01E,mp4a.40.2", "video/mp4", "video/webm;codecs=vp9,opus", "video/webm"]
    .find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

async function canvasToBlob(canvas, type = "image/png") {
  return new Promise((resolve, reject) => canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("画像を書き出せませんでした")), type));
}

function sceneTimeline(frames) {
  let offset = 0;
  return frames.map((frame) => {
    const scene = { start: offset, duration: durationOf(frame) };
    offset += scene.duration;
    return { ...scene, end: offset };
  });
}

async function prepareAudio() {
  const audio = state.draft.audio;
  if ($("#reel-audio-mode").value === "silent") {
    audio.mode = "silent";
    audio.narration.status = "explicitly-disabled";
    audio.bgm = { type: "none", qa: "explicit-silence" };
    return null;
  }
  const AudioEngine = window.AudioContext || window.webkitAudioContext;
  if (!AudioEngine || !window.OfflineAudioContext) throw new Error("音声合成を利用できません。対応ブラウザを使うか、音声なしを明示指定してください。");
  const decoder = new AudioEngine();
  const narration = new Map();
  try {
    for (let index = 0; index < state.draft.frames.length; index += 1) {
      const frame = state.draft.frames[index];
      if (speechWords(frame.text) !== speechWords(frame.narration_text)) throw new Error(`場面${index + 1}の表示文字とナレーション台本が一致しません。改行・句読点以外の単語を変えないでください。`);
      const file = state.narrationFiles.get(index);
      if (!file) {
        if (state.draft.blogLinked) throw new Error(`場面${index + 1}のナレーションがありません。全文を自然に読んだ音声を選択してください。自動音声生成は未対応です。`);
        continue;
      }
      const buffer = await decoder.decodeAudioData(await file.arrayBuffer());
      if (!buffer.duration || buffer.duration > 180) throw new Error(`場面${index + 1}の音声が長すぎます。場面ごとの音声を選んでください。`);
      let peak = 0;
      for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) for (const sample of buffer.getChannelData(channel)) peak = Math.max(peak, Math.abs(sample));
      if (peak < 0.0001) throw new Error(`場面${index + 1}の音声が無音です。`);
      narration.set(index, { buffer, peak, name: file.name });
      frame.duration = Math.max(durationOf(frame), Math.ceil((buffer.duration + .6) * 10) / 10);
    }
  } finally { await decoder.close(); }
  const timeline = sceneTimeline(state.draft.frames);
  const duration = timeline.at(-1).end;
  if (duration > 600) throw new Error("ブラウザ書き出しは10分までです。内容を分けて制作してください。文字や音声は省略しません。");
  const sampleRate = 44100;
  const offline = new OfflineAudioContext(2, Math.ceil(duration * sampleRate), sampleRate);
  const music = offline.createBuffer(1, Math.ceil(duration * sampleRate), sampleRate);
  const samples = music.getChannelData(0);
  const seedText = `${state.profile.id}|${state.draft.manifest.campaign_key}|${state.draft.frames.map((frame) => frame.text).join("|")}`;
  const seed = [...seedText].reduce((sum, character) => (Math.imul(sum, 31) + character.codePointAt(0)) >>> 0, 7);
  const notes = [0, 2, 4, 7, 9, 12];
  const noteSeconds = .65 + (seed % 15) / 100;
  let sceneIndex = 0;
  for (let sample = 0; sample < samples.length; sample += 1) {
    const time = sample / sampleRate;
    while (sceneIndex < timeline.length - 1 && time >= timeline[sceneIndex].end) sceneIndex += 1;
    const scene = timeline[sceneIndex];
    const voice = narration.get(sceneIndex);
    // Keep the whole voiced scene below the narration, with a smooth recovery afterward.
    const recovery = voice ? Math.max(0, Math.min(1, (time - scene.start - voice.buffer.duration - .15) / .35)) : 1;
    const level = .006 + .019 * recovery;
    const beat = Math.floor(time / noteSeconds);
    const note = notes[(seed + beat * 5 + Math.floor(beat / 4)) % notes.length];
    const frequency = 220 * Math.pow(2, (note + seed % 5) / 12);
    const phase = time % noteSeconds;
    const envelope = Math.sin(Math.PI * phase / noteSeconds) ** 2;
    const fade = Math.min(1, time / .8, (duration - time) / 1.2);
    samples[sample] = Math.sin(2 * Math.PI * frequency * time) * level * envelope * Math.max(0, fade);
  }
  const musicSource = offline.createBufferSource();
  musicSource.buffer = music;
  musicSource.connect(offline.destination);
  musicSource.start(0);
  for (const [index, voice] of narration) {
    const source = offline.createBufferSource();
    source.buffer = voice.buffer;
    source.playbackRate.value = 1;
    const gain = offline.createGain();
    gain.gain.value = .75 / voice.peak;
    source.connect(gain).connect(offline.destination);
    source.start(timeline[index].start);
  }
  const mixed = await offline.startRendering();
  audio.mode = "original-bgm";
  audio.narration = { status: narration.size ? "operator-audio-mixed" : "not_generated", required: state.draft.blogLinked, sceneCount: narration.size, textMatch: true, playbackRate: 1, listeningQa: "pending", files: [...narration].map(([index, voice]) => ({ scene: index + 1, name: voice.name, seconds: voice.buffer.duration })) };
  audio.bgm = { type: "original-instrumental", source: "browser-synthesis-v1", seed, rights: "波形から自作。第三者の録音素材不使用", normalPeak: .025, narrationPeak: .75, duckedPeak: .006, ducking: narration.size ? "applied-during-every-voiced-scene" : "not-needed-no-narration", qa: "rendered-listening-pending", note: "音量差は合成設定で検査。台本どおりの発話・聞き取りやすさは試聴確認が必要です。" };
  return mixed;
}

async function createCoverAssets(sources) {
  const canvas = document.createElement("canvas");
  canvas.width = 1080;
  canvas.height = 1920;
  const ctx = canvas.getContext("2d");
  const index = Math.min(sources.length - 1, Number(state.draft.cover.sourceIndex) || 0);
  const source = sources[index];
  const frame = state.draft.frames[index];
  drawCover(ctx, source.element, source.type, frame.focalX, frame.focalY);
  ctx.fillStyle = "rgba(0,0,0,.25)";
  ctx.fillRect(0, 0, 1080, 1920);
  drawTextOverlay(ctx, state.draft.cover.title);
  ctx.font = '700 46px "Yu Gothic", "Noto Sans JP", sans-serif';
  ctx.lineWidth = 6;
  const nameLines = wrapAtWidth(ctx, state.profile.name, 860);
  if (nameLines.length > 3) throw new Error("カバーの事業名が中央安全領域に収まりません。");
  nameLines.forEach((line, index) => { ctx.strokeText(line, 540, 630 + index * 58); ctx.fillText(line, 540, 630 + index * 58); });
  state.coverBlob = await canvasToBlob(canvas);
  state.coverUrl = URL.createObjectURL(state.coverBlob);
  const square = document.createElement("canvas");
  square.width = square.height = 1080;
  square.getContext("2d").drawImage(canvas, 0, 420, 1080, 1080, 0, 0, 1080, 1080);
  state.squareBlob = await canvasToBlob(square);
  state.squareUrl = URL.createObjectURL(state.squareBlob);
  for (const [id, url, name] of [["download-reel-cover", state.coverUrl, "cover"], ["download-reel-square", state.squareUrl, "cover-square-qa"]]) {
    $("#" + id).href = url;
    $("#" + id).download = `reel-${name}-${state.profile.id}-${today()}.png`;
    $("#" + id).hidden = false;
  }
  $("#reel-cover-image").src = state.coverUrl;
  $("#reel-square-image").src = state.squareUrl;
  $("#reel-cover-preview").hidden = false;
  state.draft.cover.squareQa = "image-created-awaiting-visual-review";
}

async function renderFinalReel() {
  if (state.rendering) return;
  if (!state.draft) return toast("先にリール下書きを作成してください");
  const invalidFrame = state.draft.frames.findIndex((frame) => !frame.text.trim() || textLines(frame.text).length > 3);
  if (invalidFrame >= 0) return toast(`場面${invalidFrame + 1}の文字を1〜3行にしてください`);
  if (!state.draft.cover.title.trim()) return toast("カバーの主題を入力してください");
  if (!window.MediaRecorder || !HTMLCanvasElement.prototype.captureStream) return toast("このブラウザは動画書き出しに対応していません。最新版のChromeまたはEdgeを使ってください。");
  const button = $("#render-final-reel");
  const status = $("#reel-video-status");
  const controls = [...document.querySelectorAll(".reel-editor input, .reel-editor textarea, .reel-editor select, .reel-editor button")].map((element) => [element, element.disabled]);
  controls.forEach(([element]) => { element.disabled = true; });
  state.rendering = true;
  invalidateFinalRender();
  let sources = [], stream, recorder, audioContext;
  status.textContent = "背景素材を読み込んでいます…";
  try {
    sources = await prepareRenderSources();
    if (document.fonts?.ready) await document.fonts.ready;
    const canvas = document.createElement("canvas");
    canvas.width = 1080;
    canvas.height = 1920;
    const ctx = canvas.getContext("2d", { alpha: false });
    for (const frame of state.draft.frames) fitText(ctx, frame.text);
    fitText(ctx, state.draft.cover.title);
    status.textContent = "ナレーションと自作BGMを準備しています…";
    const mixedAudio = await prepareAudio();
    const timeline = sceneTimeline(state.draft.frames);
    const duration = timeline.at(-1).end * 1000;
    if (duration > 600_000) throw new Error("ブラウザ書き出しは10分までです。内容を分けて制作してください。");
    renderPreview();
    let audioSource;
    const mimeType = recorderMimeType();
    if (!mimeType) throw new Error("投稿動画のエンコード方式を利用できません");
    stream = canvas.captureStream(30);
    if (mixedAudio) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      await audioContext.resume();
      if (audioContext.state !== "running") throw new Error("音声の再生が許可されていません。画面上の書き出しボタンから再実行してください。");
      const destination = audioContext.createMediaStreamDestination();
      audioSource = audioContext.createBufferSource();
      audioSource.buffer = mixedAudio;
      audioSource.connect(destination);
      for (const track of destination.stream.getAudioTracks()) stream.addTrack(track);
    }
    recorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 10_000_000, audioBitsPerSecond: 192_000 });
    const chunks = [];
    recorder.addEventListener("dataavailable", (event) => { if (event.data.size) chunks.push(event.data); });
    const completed = new Promise((resolve, reject) => {
      recorder.addEventListener("stop", resolve, { once: true });
      recorder.addEventListener("error", () => reject(recorder.error || new Error("動画を書き出せませんでした")), { once: true });
    });
    for (const source of new Set(sources.filter((item) => item.type === "video"))) await source.element.play();
    recorder.start(1000);
    const audioStarted = audioContext?.currentTime || 0;
    audioSource?.start(audioStarted);
    const started = performance.now();
    let lastFrameIndex = -1;
    await new Promise((resolve, reject) => {
      const draw = (now) => {
        if (document.hidden) return reject(new Error("書き出し中にタブが非表示になりました。場面欠落を避けるため、このタブを表示したまま再実行してください。"));
        const elapsed = Math.min(audioContext ? (audioContext.currentTime - audioStarted) * 1000 : now - started, duration);
        const foundIndex = timeline.findIndex((scene) => elapsed < scene.end * 1000);
        const frameIndex = foundIndex < 0 ? timeline.length - 1 : foundIndex;
        const source = sources[frameIndex];
        ctx.fillStyle = "#1d2a24";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawCover(ctx, source.element, source.type, state.draft.frames[frameIndex].focalX, state.draft.frames[frameIndex].focalY);
        const gradient = ctx.createLinearGradient(0, 0, 0, 1920);
        gradient.addColorStop(0, "rgba(0,0,0,.16)");
        gradient.addColorStop(.55, "rgba(0,0,0,.26)");
        gradient.addColorStop(1, "rgba(0,0,0,.42)");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 1080, 1920);
        drawTextOverlay(ctx, state.draft.frames[frameIndex].text);
        if (frameIndex !== lastFrameIndex) {
          status.textContent = `場面 ${frameIndex + 1}/${timeline.length} を焼き込み中… ${Math.floor(elapsed / 1000)}/${Math.ceil(duration / 1000)}秒`;
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

    await createCoverAssets(sources);
    syncManifest();
    state.draft.manifest.final_video = download.download;
    state.draft.manifest.cover_image = $("#download-reel-cover").download;
    state.draft.manifest.square_qa_image = $("#download-reel-square").download;
    for (const post of state.draft.manifest.posts) for (const media of post.media || []) {
      media.path = download.download;
      media.status = state.finalVideoExtension === "mp4" ? "rendered-awaiting-review" : "requires-mp4-conversion";
    }
    status.textContent = state.finalVideoExtension === "mp4"
      ? `MP4・独立カバー・正方形確認画像を書き出しました（${totalSeconds()}秒）。映像と音声の試聴、投稿セットの最終承認は未完了です。`
      : "テロップ焼き込みは完了しましたがWebM形式です。Instagram投稿前にMP4へ変換してください。";
  } catch (error) { invalidateFinalRender(); status.textContent = error.message; toast(error.message); }
  finally {
    if (recorder && recorder.state !== "inactive") recorder.stop();
    for (const track of stream?.getTracks() || []) track.stop();
    for (const source of new Set(sources.filter((item) => item.type === "video"))) source.element.pause();
    if (audioContext) await audioContext.close();
    state.rendering = false;
    controls.forEach(([element, disabled]) => { element.disabled = disabled; });
    button.disabled = false;
  }
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
  if (!state.finalVideoBlob || !state.coverBlob || !state.squareBlob) return toast("先に動画・独立カバー・正方形確認画像を書き出してください");
  if (state.finalVideoExtension !== "mp4") return toast("Instagram投稿用にMP4形式の完成動画が必要です");
  const captionError = captionsReady();
  if (captionError) return toast(captionError);
  if (state.draft.threadsCaption.length > 500) return toast("Threads本文を500文字以内にしてください");
  if (!state.draft.storyCaption.trim() || textLines(state.draft.storyCaption).length > 2 || !state.draft.shopComment.trim()) return toast("Storyの1〜2行と店舗コメントを確認してください");
  const research = researchInput();
  if (research.observations.length < 2 || !research.observations.every((item) => item.video && item.audio && item.caption) || !research.keep || !research.change) return toast("今回の公式投稿を複数確認し、引き継ぐ表現・今回の調整理由を記録してください");
  for (const [id, message] of [["reel-visual-qa", "動画とカバー・正方形の画面確認が必要です"], ["reel-audio-qa", "音声または明示指定の無音を実際に確認してください"], ["reel-url-qa", "公式アカウント・正規URLの確認が必要です"]]) if (!$("#" + id).checked) return toast(message);
  if (state.draft.blogLinked && (!$("#reel-blog-live-checked").checked || !["reel-blog-live-url", "reel-blog-video-url", "reel-blog-cover-url"].every((id) => safeHttpUrl($("#" + id).value).startsWith("https://")))) return toast("同一MP4・カバーを埋め込んだ本番記事と素材URLを確認してください");
  if (!$("#chrome-post-confirm").checked) return toast("投稿先、完成動画、本文、末尾URLの確認にチェックしてください");
  const account = state.draft.postingAccount;
  if (account?.status !== "registered") return toast("判断.mdで投稿先アカウントを確定してください");
  const caption = platform === "instagram" ? state.draft.instagramCaption : state.draft.threadsCaption;
  await navigator.clipboard.writeText(caption);
  const target = platform === "instagram" ? account.instagram?.url : account.threads?.url;
  if (!target || !safeHttpUrl(target)) return toast("この媒体の公式アカウントが未登録です");
  syncManifest();
  state.draft.manifest.publication_review = { status: "operator-approved-for-manual-posting", checkedAt: new Date().toISOString(), publication: "not_performed", same_mp4_for_threads: true };
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
    workflow: "myreel",
    durationSeconds: state.draft.durationSeconds,
    blogLinked: state.draft.blogLinked,
    research: state.draft.manifest.research,
    audio: state.draft.audio,
    cover: state.draft.cover,
    instagramCaption: state.draft.instagramCaption,
    threadsCaption: state.draft.threadsCaption,
    storyCaption: state.draft.storyCaption,
    shopComment: state.draft.shopComment,
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
    handoffToAdmin("reel", packageData(), key);
    toast("管理画面へリール下書きを渡しました");
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
    await writeFile(directory, "README.md", `# ${payload().topic || state.draft.cover.title}\n\n- 事業: ${state.profile.name}\n- 対象: ${payload().audience}\n- 状態: ローカル確認用素材。外部投稿・Instagram下書き保存は未実施\n- 形式: 1080×1920 / ${state.draft.frames.length}場面 / ${totalSeconds()}秒。通常速度、全文を表示\n- 音声: ${state.draft.audio.narration.status}。自動ナレーション生成は未対応\n- 次の作業: 動画・独立カバー・正方形・音声確認、正式アカウントと正規URL確認、4点セットの最終承認、公開結果記録\n`);
    await writeFile(directory, "source.md", `# 入力元\n\nURL: ${state.draft.sourceUrl}\n\n## 元テキスト\n\n${payload().sourceText}\n\n## 事業者の言葉\n\n${payload().story}\n`);
    await writeFile(directory, "storyboard.json", JSON.stringify(packageData(), null, 2));
    await writeFile(directory, "captions.md", `# Instagram\n\n${state.draft.instagramCaption}\n\n# Story\n\n${state.draft.storyCaption}\n\n公開Reelを共有。下部中央リンク「詳細はこちら」: ${state.draft.sourceUrl}\n\n# 店舗コメント\n\n${state.draft.shopComment}\n\n# Threads（Reelと同一MP4）\n\n${state.draft.threadsCaption}\n`);
    await writeFile(directory, "prompts.md", `# 背景動画\n\n${state.draft.videoPrompt}\n\n# 最終調整\n\n${$("#reel-final-prompt").value.trim()}\n`);
    const assets = await directory.getDirectoryHandle("assets", { create: true });
    for (const item of state.localMedia) await writeFile(assets, item.file.name, item.file);
    for (const [index, file] of state.narrationFiles) await writeFile(assets, `narration-${index + 1}-${file.name}`, file);
    if (state.rawVideoBlob) await writeFile(assets, "background.mp4", state.rawVideoBlob);
    if (state.finalVideoBlob) await writeFile(directory, state.draft.manifest.final_video || `reel-final.${state.finalVideoExtension}`, state.finalVideoBlob);
    if (state.coverBlob) await writeFile(directory, state.draft.manifest.cover_image || "cover.png", state.coverBlob);
    if (state.squareBlob) await writeFile(directory, state.draft.manifest.square_qa_image || "cover-square-qa.png", state.squareBlob);
    await writeFile(directory, "qa.json", JSON.stringify({ research: state.draft.manifest.research, audio: state.draft.audio, cover: state.draft.cover, sceneText: state.draft.manifest.frames.map((frame) => ({ scene: frame.index, center_text: frame.center_text, narration_text: frame.narration_text, exactMatch: frame.narration_match, duration: frame.duration })), review: state.draft.manifest.qa, publication: "not_performed" }, null, 2));
    toast(`content/campaigns/${campaignName} に保存しました`);
  } catch (error) {
    if (error.name !== "AbortError") toast(`保存できませんでした: ${error.message}`);
  }
}

$("#reel-profile").addEventListener("change", () => applyProfile({ reset: true }));
$("#reel-files").addEventListener("change", onFilesChanged);
$("#reel-source-mode").addEventListener("change", () => resetWorkflow());
$("#reel-blog-linked").addEventListener("change", () => resetWorkflow());
$("#reel-audio-mode").addEventListener("change", invalidateFinalRender);
$("#make-reel-concepts").addEventListener("click", makeConcepts);
$("#make-reel-draft").addEventListener("click", makeDraft);
$("#reel-concepts").addEventListener("input", (event) => {
  if (!event.target.dataset.conceptField) return;
  state.concepts[Number(event.target.dataset.index)][event.target.dataset.conceptField] = event.target.value;
});
$("#reel-frame-editors").addEventListener("input", updateFrame);
$("#reel-frame-editors").addEventListener("change", (event) => {
  if (event.target.dataset.narrationIndex === undefined) return;
  const index = Number(event.target.dataset.narrationIndex);
  const file = event.target.files?.[0];
  if (file) state.narrationFiles.set(index, file);
  else state.narrationFiles.delete(index);
  event.target.nextElementSibling.textContent = file?.name || "未選択";
  invalidateFinalRender();
});
$("#add-reel-scene").addEventListener("click", () => {
  if (!state.draft) return;
  const last = state.draft.frames.at(-1);
  state.draft.frames.push({ index: state.draft.frames.length + 1, text: "", center_text: "", narration_text: "", duration: 3, media: last?.media || "", crop: "全画面", focalX: 50, focalY: 50 });
  invalidateFinalRender();
  renderDraft();
});
for (const id of ["reel-cover-title", "reel-cta", "reel-final-url", "reel-video-prompt", "instagram-caption", "threads-caption", "reel-story-caption", "reel-shop-comment", "reel-cover-source"]) $("#" + id).addEventListener("input", syncEditableMeta);
$("#reel-final-scheduled-at").addEventListener("input", () => { resetApproval(); syncManifest(); });
for (const id of ["reel-research-urls", "reel-research-reviewed", "reel-research-keep", "reel-research-change", "reel-blog-live-url", "reel-blog-video-url", "reel-blog-cover-url"]) $("#" + id).addEventListener("input", () => { resetApproval(); syncManifest(); });
$("#reel-research-urls").addEventListener("input", () => { $("#reel-research-reviewed").checked = false; syncManifest(); });
for (const id of ["reel-visual-qa", "reel-audio-qa", "reel-url-qa", "reel-blog-live-checked", "chrome-post-confirm"]) $("#" + id).addEventListener("change", syncManifest);
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
