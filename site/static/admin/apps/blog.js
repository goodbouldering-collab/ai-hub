import { $, $$, api, bindApiKeyPanel, configureStudioShell, escapeHtml, handoffToAdmin, loadProfiles, refreshHealth, requireSession, STUDIO_CONFIG, toast } from "./studio-core.js";

const state = {
  profiles: [],
  profile: null,
  entryStarter: null,
  storyTemplateActive: false,
  trendDiscovery: null,
  selectedTrend: null,
  research: null,
  titlePlan: null,
  outlinePlan: null,
  selectedOutline: null,
  draft: null,
  images: { hero: null, sections: [] }
};

const today = () => new Date().toISOString().slice(0, 10);
const lines = (value) => String(value || "").split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
const paragraphHtml = (value) => escapeHtml(value || "").replace(/\n/g, "<br>");

function ownerStoryValue() {
  return lines($("#owner-story").value).filter((line) => {
    if (line.startsWith("【実話メモ")) return false;
    if (line.startsWith("思い出す場面：")) return false;
    return !/[：:]$/.test(line);
  }).join("\n");
}
const safeUrl = (value) => {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch { return ""; }
};
const slugify = (value) => String(value || "blog").normalize("NFKC").toLowerCase()
  .replace(/[^a-z0-9ぁ-んァ-ヶ一-龠]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 54) || "blog";

function payload() {
  return {
    profileId: $("#profile").value,
    topic: $("#topic").value.trim(),
    audience: $("#audience").value.trim(),
    ownerStory: ownerStoryValue(),
    officialUrls: lines($("#official-urls").value),
    cta: $("#cta").value.trim(),
    entryGuide: state.profile?.entryGuide || null,
    entryStarter: state.entryStarter,
    selectedTrend: state.selectedTrend
  };
}

function mergeSources(...groups) {
  const seen = new Set();
  return groups.flat().filter((source) => {
    const href = safeUrl(source?.url);
    if (!href || seen.has(href)) return false;
    seen.add(href);
    source.url = href;
    if (!source.claim && source.signal) source.claim = source.signal;
    return true;
  });
}

function showStep(step) {
  $$(`[data-step]`).forEach((panel) => { panel.hidden = Number(panel.dataset.step) > step; });
  $$(`[data-step-indicator]`).forEach((item) => {
    const value = Number(item.dataset.stepIndicator);
    item.classList.toggle("active", value === step);
    item.classList.toggle("done", value < step);
  });
  document.querySelector(`[data-step="${step}"]`)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function enableEmbeddedAutoHeight() {
  if (!STUDIO_CONFIG.embedded || window.parent === window) return;

  let frameRequest = 0;
  const reportHeight = () => {
    frameRequest = 0;
    const height = Math.max(
      document.body?.scrollHeight || 0,
      document.documentElement.scrollHeight,
      document.body?.offsetHeight || 0,
      document.documentElement.offsetHeight
    );
    const messageType = STUDIO_CONFIG.handoffMessageType === "junpa:content-studio-handoff"
      ? "junpa:content-studio-resize"
      : "content-studio:resize";
    window.parent.postMessage({ type: messageType, kind: "blog", height }, window.location.origin);
  };
  const scheduleHeightReport = () => {
    if (frameRequest) return;
    frameRequest = window.requestAnimationFrame(reportHeight);
  };

  if ("ResizeObserver" in window) {
    const observer = new ResizeObserver(scheduleHeightReport);
    observer.observe(document.documentElement);
    if (document.body) observer.observe(document.body);
  } else {
    window.setInterval(scheduleHeightReport, 500);
  }

  window.addEventListener("load", scheduleHeightReport);
  window.addEventListener("resize", scheduleHeightReport);
  scheduleHeightReport();
}

function resetWorkflow({ keepDiscovery = false } = {}) {
  if (!keepDiscovery) {
    state.trendDiscovery = null;
    state.selectedTrend = null;
    $("#trend-status").hidden = true;
    $("#trend-status").textContent = "";
    $("#trend-results").hidden = true;
    $("#trend-options").innerHTML = "";
    $("#trend-method").textContent = "";
    $("#trend-warnings").textContent = "";
  }
  state.research = null;
  state.titlePlan = null;
  state.outlinePlan = null;
  state.selectedOutline = null;
  state.draft = null;
  state.images = { hero: null, sections: [] };
  $("#research-report").textContent = "";
  $("#research-sources").innerHTML = "";
  $("#research-progress").classList.remove("complete");
  $("#research-progress span").textContent = "調査を準備しています";
  $("#make-plan").disabled = true;
  $("#title-options").innerHTML = "";
  $("#selected-title").value = "";
  $("#outline-options").innerHTML = "";
  $("#outline-stage").hidden = true;
  $("#blog-edit-fields").innerHTML = "";
  $("#title-review").innerHTML = "";
  $("#article-preview").innerHTML = `<div class="empty-preview"><b>ここに記事が表示されます</b><p>左の手順で、調査・選択・記事生成を進めてください。</p></div>`;
  $(".workspace").classList.remove("preview-mode");
  $("#back-editor").hidden = true;
  showStep(1);
}

function storyTemplate(starter) {
  const questions = state.profile?.entryGuide?.storyQuestions || [];
  return [
    "【実話メモ｜分かるところだけ書いてください】",
    `思い出す場面：${starter?.storyQuestion || questions[0] || "最近、実際に起きた場面は？"}`,
    "実際に聞かれた言葉：",
    "その場で困っていたこと：",
    "最初に試したこと：",
    "うまくいかなかった点：",
    "修正したこと：",
    "確認できた変化：",
    "時期・場所・確認できる数字："
  ].join("\n");
}

function applyTopicStarter(starter, { silent = false } = {}) {
  if (!starter) return;
  state.entryStarter = starter;
  $("#topic").value = starter.topic || starter.searchQuery || "";
  $("#audience").value = state.profile?.audience || "";
  if (state.storyTemplateActive || !$("#owner-story").value.trim()) {
    $("#owner-story").value = storyTemplate(starter);
    state.storyTemplateActive = true;
  }
  $$("[data-entry-starter]").forEach((button) => {
    const selected = button.dataset.entryStarter === starter.id;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  if (!silent) toast("入口の仮説を入力しました。テーマと実話メモは自由に直せます。");
}

function renderEntryGuide() {
  const guide = state.profile?.entryGuide;
  if (!guide) return;
  $("#entry-guide-status").textContent = guide.hypothesisLabel || "";
  $("#entry-guide-audience").textContent = guide.customerSnapshot || state.profile.audience || "";
  $("#entry-guide-season").innerHTML = `<strong>${escapeHtml(guide.season?.label || "今月")}</strong>${escapeHtml(guide.season?.topic || "")}`;
  $("#entry-guide-searches").innerHTML = (guide.searchQueries || []).map((query, index) =>
    `<button type="button" data-entry-search="${index}">${escapeHtml(query)}</button>`
  ).join("");
  $("#entry-topic-starters").innerHTML = (guide.topicStarters || []).map((starter, index) => `
    <button type="button" data-entry-starter="${escapeHtml(starter.id)}" data-entry-index="${index}" aria-pressed="false">
      <span>${escapeHtml(starter.label)}</span>
      <b>${escapeHtml(starter.topic)}</b>
      <small>検索入口：${escapeHtml(starter.searchQuery)}</small>
    </button>`).join("");
  $("#entry-story-questions").innerHTML = (guide.storyQuestions || []).map((question) => `<li>${escapeHtml(question)}</li>`).join("");
}

function applyProfile({ reset = false } = {}) {
  state.profile = state.profiles.find((item) => item.id === $("#profile").value) || null;
  if (!state.profile) return;
  document.documentElement.dataset.business = state.profile.id;
  document.body.dataset.business = state.profile.id;
  const brandName = $("#studio-brand-name");
  const brandHeading = $("#studio-brand-heading");
  if (brandName) brandName.textContent = state.profile.name;
  if (brandHeading) brandHeading.textContent = `${state.profile.name} ブログ編集`;
  if (reset) {
    resetWorkflow();
    state.entryStarter = null;
    state.storyTemplateActive = false;
    $("#blog-final-prompt").value = "";
  }
  $("#audience").value = state.profile.audience || "";
  $("#cta").value = state.profile.defaultCta || "";
  $("#official-urls").value = (state.profile.sourceUrls || []).join("\n");
  renderEntryGuide();
  if (!$("#topic").value.trim() || reset) applyTopicStarter(state.profile.entryGuide?.topicStarters?.[0], { silent: true });
}

async function initialize() {
  if (!await requireSession(initialize)) return;
  bindApiKeyPanel(refreshHealth);
  const [profiles] = await Promise.all([loadProfiles($("#profile")), refreshHealth()]);
  state.profiles = profiles;
  applyProfile();
}

async function discoverTrends() {
  resetWorkflow();
  const button = $("#discover-trends");
  const status = $("#trend-status");
  button.disabled = true;
  button.textContent = "国内の話題を調査中…";
  status.hidden = false;
  status.textContent = "直近7日・30日・90日の国内情報と一次資料を確認しています…";
  try {
    const result = await api("/api/blog/research", {
      method: "POST",
      body: JSON.stringify({ ...payload(), mode: "discovery" })
    });
    const completed = result.status === "completed" ? result : await pollResearch(result.id, "discovery");
    state.trendDiscovery = completed.discovery;
    renderTrendDiscovery(Boolean(completed.mock));
  } catch (error) {
    status.textContent = error.message;
    toast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "この顧客像で国内トレンドを調査";
  }
}

function renderTrendDiscovery(mock = false) {
  const discovery = state.trendDiscovery;
  if (!discovery) return;
  const ideas = [...(discovery.ideas || [])].sort((a, b) => Number(b.buzzScore) - Number(a.buzzScore));
  $("#trend-status").hidden = false;
  $("#trend-status").textContent = mock ? "デモ候補です。実際の国内話題度は取得していません。" : `${discovery.asOf || "現在"}時点の国内話題を確認しました。`;
  $("#trend-method").textContent = discovery.rankingMethod || "推定話題度順";
  $("#trend-warnings").textContent = (discovery.warnings || []).join(" / ");
  $("#trend-options").innerHTML = ideas.map((idea, index) => `
    <article class="trend-card" data-trend-card="${index}">
      <div class="trend-rank"><b>${index + 1}</b><span>推定話題度 ${escapeHtml(idea.buzzScore)} / 100</span><em>${escapeHtml(idea.buzzLabel || "")}</em></div>
      <h4>${escapeHtml(idea.topic)}</h4>
      <p class="trend-reason">${escapeHtml(idea.buzzReason)}</p>
      <dl><div><dt>誰向け</dt><dd>${escapeHtml(idea.audience)}</dd></div><div><dt>悩み</dt><dd>${escapeHtml(idea.problem)}</dd></div><div><dt>この事業が書く理由</dt><dd>${escapeHtml(idea.businessFit)}</dd></div><div><dt>記事の切り口</dt><dd>${escapeHtml(idea.articleAngle)}</dd></div><div><dt>次の行動</dt><dd>${escapeHtml(idea.nextAction)}</dd></div></dl>
      <details><summary>出典と媒体展開を見る</summary><div class="trend-source-list">${(idea.sources || []).map((source) => {
        const href = safeUrl(source.url);
        return href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer"><b>${escapeHtml(source.title || href)}</b><small>${escapeHtml([source.publisher, source.publishedAt, source.signal || source.claim].filter(Boolean).join(" / "))}</small></a>` : "";
      }).join("")}</div><p class="trend-media"><b>ブログ:</b> ${escapeHtml(idea.mediaPlan?.blog || "")}<br><b>SNS:</b> ${escapeHtml(idea.mediaPlan?.sns || "")}<br><b>note:</b> ${escapeHtml(idea.mediaPlan?.note || "")}<br><b>YouTube:</b> ${escapeHtml(idea.mediaPlan?.youtube || "")}</p></details>
      <button class="primary select-trend" type="button" data-trend-index="${index}">このネタを選んで詳しく調査</button>
    </article>`).join("");
  state.trendDiscovery.ideas = ideas;
  $("#trend-results").hidden = false;
}

async function startResearch() {
  const input = payload();
  if (!input.topic) return toast("今回のテーマを入力してください");
  resetWorkflow({ keepDiscovery: true });
  showStep(2);
  const progress = $("#research-progress");
  progress.querySelector("span").textContent = "Web・公式情報・地域検索・最新動向を調査しています…";
  $("#start-research").disabled = true;
  try {
    const result = await api("/api/blog/research", { method: "POST", body: JSON.stringify(input) });
    state.research = result.status === "completed" ? result : await pollResearch(result.id, "topic");
    state.research.sources = mergeSources(state.selectedTrend?.sources || [], state.research.sources || []);
    renderResearch();
  } catch (error) {
    progress.querySelector("span").textContent = error.message;
    toast(error.message);
  } finally {
    $("#start-research").disabled = false;
  }
}

async function pollResearch(id, mode = "topic") {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
    const result = await api(`/api/blog/research-status?id=${encodeURIComponent(id)}&profileId=${encodeURIComponent(state.profile.id)}&mode=${encodeURIComponent(mode)}`);
    const status = mode === "discovery" ? $("#trend-status") : $("#research-progress span");
    status.textContent = `調査中… ${result.status}`;
    if (result.complete) return result;
    if (["failed", "cancelled", "incomplete"].includes(result.status)) {
      throw new Error(result.error?.message || `調査が${result.status}になりました`);
    }
  }
  throw new Error("調査に時間がかかっています。少し待ってから再試行してください。");
}

function renderResearch() {
  $("#research-progress").classList.add("complete");
  $("#research-progress span").textContent = state.research.mock ? "デモ調査が完了しました" : "ディープリサーチが完了しました";
  $("#research-report").textContent = state.research.report || "";
  $("#research-sources").innerHTML = (state.research.sources || []).map((source) => {
    const href = safeUrl(source.url);
    return href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title || href)}</a>` : "";
  }).join("");
  $("#make-plan").disabled = false;
}

async function makePlan() {
  if (!state.research) return toast("先に調査を完了してください");
  const button = $("#make-plan");
  button.disabled = true;
  button.textContent = "タイトル候補を生成中…";
  try {
    const result = await api("/api/blog/plan", {
      method: "POST",
      body: JSON.stringify({ ...payload(), stage: "titles", report: state.research.report, sources: state.research.sources || [] })
    });
    state.titlePlan = result.plan;
    renderTitlePlan();
    showStep(3);
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.textContent = "2. タイトル候補を3つ作る"; }
}

function renderTitlePlan() {
  const titles = state.titlePlan?.titles || [];
  $("#title-options").innerHTML = titles.map((item, index) => `
    <article class="choice-card editable-choice">
      <label class="choice-select"><input type="radio" name="title-option" value="${index}">候補 ${index + 1} を選ぶ</label>
      <label>タイトル<input data-title-field="title" data-index="${index}" value="${escapeHtml(item.title)}"></label>
      <div class="title-context"><b>${escapeHtml(item.editorialAngle)}</b><span>対象：${escapeHtml(item.audience)}</span><span>悩み：${escapeHtml(item.problem)}</span><span>顧客メリット：${escapeHtml(item.customerBenefit)}</span><span>事業との接点：${escapeHtml(item.businessFit)}</span><span>次の行動：${escapeHtml(item.cta)}</span></div>
      <label>狙い<textarea data-title-field="reason" data-index="${index}" rows="2">${escapeHtml(item.reason)}</textarea></label>
      <small>${escapeHtml(item.primaryKeyword)} × ${escapeHtml(item.localKeyword)}</small>
    </article>`).join("");
  $("#plan-notes").textContent = (state.titlePlan?.editorialWarnings || []).join(" / ");
}

async function makeOutlines() {
  const selected = $("input[name='title-option']:checked");
  if (!selected) return toast("タイトル候補を1つ選んでください");
  const selectedTitle = $("#selected-title").value.trim();
  if (!selectedTitle) return toast("選んだタイトルを確認してください");
  const button = $("#make-outlines");
  button.disabled = true;
  button.textContent = "H2構成を生成中…";
  try {
    const result = await api("/api/blog/plan", {
      method: "POST",
      body: JSON.stringify({ ...payload(), stage: "outlines", selectedTitle, report: state.research?.report || "", sources: state.research?.sources || [] })
    });
    state.outlinePlan = result.plan;
    renderOutlinePlan();
    $("#outline-stage").hidden = false;
    $("#outline-stage").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.textContent = "3. このタイトルからH2構成を3案作る"; }
}

function renderOutlinePlan() {
  const groups = state.outlinePlan?.outlineGroups || [];
  $("#outline-options").innerHTML = groups.map((group, groupIndex) => `
    <article class="outline-card editable-choice">
      <label class="choice-select"><input type="radio" name="outline-option" value="${groupIndex}">構成 ${groupIndex + 1} を選ぶ</label>
      <label>構成名<input data-outline-field="name" data-group="${groupIndex}" value="${escapeHtml(group.name)}"></label>
      <label>記事の角度<textarea data-outline-field="angle" data-group="${groupIndex}" rows="2">${escapeHtml(group.angle)}</textarea></label>
      <div class="heading-editors">${group.headings.map((item, headingIndex) => `
        <fieldset><legend>H2 ${headingIndex + 1}</legend>
          <input data-heading-field="heading" data-group="${groupIndex}" data-heading="${headingIndex}" value="${escapeHtml(item.heading)}">
          <textarea data-heading-field="purpose" data-group="${groupIndex}" data-heading="${headingIndex}" rows="2">${escapeHtml(item.purpose)}</textarea>
        </fieldset>`).join("")}</div>
    </article>`).join("");
  const warnings = [...(state.titlePlan?.editorialWarnings || []), ...(state.outlinePlan?.editorialWarnings || [])];
  $("#plan-notes").textContent = [...new Set(warnings)].join(" / ");
}

function selectedOutline() {
  const selected = $("input[name='outline-option']:checked");
  return selected ? state.outlinePlan?.outlineGroups?.[Number(selected.value)] : null;
}

function ensureDraftShape(draft = {}) {
  const sources = state.research?.sources || [];
  return {
    finalTitle: draft.finalTitle || $("#selected-title").value.trim(),
    titleReviewReason: draft.titleReviewReason || "本文と検索意図に合わせて公開前に再確認してください。",
    metaTitle: draft.metaTitle || draft.finalTitle || "",
    metaDescription: draft.metaDescription || "",
    excerpt: draft.excerpt || "",
    intro: draft.intro || "",
    heroImagePrompt: draft.heroImagePrompt || "",
    heroImageAlt: draft.heroImageAlt || "",
    heroImageCaption: draft.heroImageCaption || "",
    sections: (draft.sections || []).map((section) => ({
      heading: section.heading || "", body: section.body || "", imagePrompt: section.imagePrompt || "",
      imageAlt: section.imageAlt || "", imageCaption: section.imageCaption || ""
    })),
    conclusion: draft.conclusion || "",
    cta: draft.cta || payload().cta,
    faq: (draft.faq || []).map((item) => ({ question: item.question || "", answer: item.answer || "" })),
    references: (draft.references?.length ? draft.references : sources).map((item) => ({
      title: item.title || item.url || "", url: item.url || "", publisher: item.publisher || "",
      publishedAt: item.publishedAt || "", claim: item.claim || ""
    })),
    factChecks: draft.factChecks || [],
    repurpose: { sns: draft.repurpose?.sns || "", note: draft.repurpose?.note || "", youtube: draft.repurpose?.youtube || "" }
  };
}

const clampScore = (value) => Math.max(0, Math.min(100, Math.round(value)));

function textBigrams(value = "") {
  const text = String(value).normalize("NFKC").toLowerCase().replace(/[\s、。・｜|/／:：!?！？「」『』（）()[\]【】<>＜＞\-—_]/g, "");
  const items = new Set();
  for (let index = 0; index < text.length - 1; index += 1) items.add(text.slice(index, index + 2));
  return items;
}

function overlapScore(source, target) {
  const sourceItems = textBigrams(source);
  if (!sourceItems.size) return 0;
  const targetItems = textBigrams(target);
  return [...sourceItems].filter((item) => targetItems.has(item)).length / sourceItems.size;
}

function finalQualityEvaluation() {
  if (!state.draft) return { overall: 0, metrics: [], priorities: [] };
  const draft = state.draft;
  const sections = draft.sections || [];
  const faq = draft.faq || [];
  const references = (draft.references || []).filter((item) => safeUrl(item.url));
  const sourceCount = state.research?.sources?.length || 0;
  const researchLength = String(state.research?.report || "").length;
  const ownerStory = ownerStoryValue();
  const topic = $("#topic").value.trim();
  const area = String(state.profile?.area || "");
  const profileName = String(state.profile?.name || "");
  const mainText = [
    draft.intro,
    ...sections.flatMap((section) => [section.heading, section.body]),
    draft.conclusion,
    draft.cta,
    ...faq.flatMap((item) => [item.question, item.answer])
  ].join("\n");
  const searchText = [draft.finalTitle, draft.metaTitle, draft.metaDescription, draft.intro, ...sections.map((item) => item.heading)].join("\n");
  const fullText = [searchText, mainText].join("\n");
  const headingsInRange = sections.filter((section) => section.heading.length >= 6 && section.heading.length <= 34).length;
  const substantialSections = sections.filter((section) => section.body.length >= 140).length;
  const completeFaq = faq.filter((item) => item.question.length >= 6 && item.answer.length >= 45).length;
  const referenceClaims = references.filter((item) => item.claim?.trim()).length;
  const factCheckCount = draft.factChecks?.length || 0;
  const actionWords = (draft.cta.match(/予約|相談|確認|選ぶ|試す|問い合わせ|申し込/g) || []).length;
  const localWords = (fullText.match(/地域|来店|予約|店舗|教室|施設|相談/g) || []).length;
  const firsthandWords = (fullText.match(/実際|お客様|利用者|現場|失敗|変え|修正|確認|会話/g) || []).length;
  const cautionWords = (fullText.match(/医療|断定|個人差|体調|中止|相談|無理をしない/g) || []).length;
  const unsafeClaims = [...new Set(fullText.match(/治る|完治|治療できる|必ず改善|免疫力が上がる|毒素を排出|病気を防ぐ/g) || [])];
  const intentOverlap = overlapScore(topic, searchText);
  const titleOverlap = overlapScore(draft.finalTitle, [draft.intro, ...sections.map((item) => item.heading), draft.conclusion].join("\n"));
  const storyOverlap = ownerStory ? overlapScore(ownerStory, mainText) : 0;

  const metrics = [
    {
      id: "llmo",
      label: "LLMO・AI回答適性",
      weight: 16,
      score: clampScore(
        (researchLength >= 500 ? 15 : researchLength >= 200 ? 9 : 3) +
        (draft.intro.length >= 80 && draft.intro.length <= 420 ? 20 : 10) +
        (completeFaq >= 2 ? 20 : completeFaq * 8) +
        (sections.length >= 3 && sections.length <= 5 ? 15 : 7) +
        (references.length >= 3 ? 15 : references.length * 5) +
        (draft.metaDescription.length >= 60 && draft.metaDescription.length <= 180 ? 10 : 4) + 5
      ),
      reason: `調査${researchLength}字・FAQ${completeFaq}件・出典${references.length}件を、AIが回答へ抜き出しやすい形か確認。`,
      action: "導入で結論を先に示し、具体的な質問と短い回答、根拠URLを増やす。"
    },
    {
      id: "seo",
      label: "SEO・検索意図",
      weight: 13,
      score: clampScore(
        intentOverlap * 50 +
        (draft.metaTitle.length >= 18 && draft.metaTitle.length <= 48 ? 15 : 7) +
        (draft.metaDescription.length >= 60 && draft.metaDescription.length <= 180 ? 15 : 7) +
        (draft.finalTitle.length >= 16 && draft.finalTitle.length <= 48 ? 10 : 5) +
        (draft.excerpt.length >= 45 && draft.excerpt.length <= 180 ? 10 : 5)
      ),
      reason: `入力テーマとタイトル・導入・H2の一致度を${Math.round(intentOverlap * 100)}%として点検。`,
      action: "読者が検索する言葉を、タイトル・導入・主要H2へ自然に揃える。"
    },
    {
      id: "meo",
      label: "MEO・地域性",
      weight: 10,
      score: clampScore(
        (area && fullText.includes(area) ? 30 : 8) +
        (profileName && fullText.includes(profileName) ? 20 : 8) +
        (payload().officialUrls.length ? 15 : 5) +
        (actionWords ? 20 : 7) +
        Math.min(15, localWords * 3)
      ),
      reason: `地域名「${area || "未設定"}」・事業名・利用行動・公式URLのつながりを確認。`,
      action: "地域名、事業名、対象者、相談・予約までの具体的な流れを本文とCTAへ入れる。"
    },
    {
      id: "evidence",
      label: "根拠・信頼性",
      weight: 13,
      score: clampScore(
        Math.min(44, references.length * 11) +
        (references.length ? Math.round((referenceClaims / references.length) * 20) : 0) +
        Math.min(20, factCheckCount * 5) +
        (sourceCount >= 3 ? 16 : sourceCount * 5)
      ),
      reason: `調査ソース${sourceCount}件・記事出典${references.length}件・事実確認${factCheckCount}件を評価。`,
      action: "主張ごとに一次情報を対応させ、公開前の確認項目と注意点を明記する。"
    },
    {
      id: "firsthand",
      label: "一次情報・独自性",
      weight: 11,
      score: clampScore(
        (ownerStory.length >= 80 ? 40 : ownerStory.length >= 30 ? 25 : ownerStory.length ? 12 : 0) +
        Math.min(30, storyOverlap * 45) +
        Math.min(30, firsthandWords * 5)
      ),
      reason: `実話メモ${ownerStory.length}字・本文への反映度${Math.round(storyOverlap * 100)}%を確認。`,
      action: "実際の会話、失敗と修正、現場の順番、確認済み数字を本人の言葉で足す。"
    },
    {
      id: "readability",
      label: "構成・読みやすさ",
      weight: 10,
      score: clampScore(
        (sections.length >= 3 && sections.length <= 5 ? 20 : 10) +
        (sections.length ? Math.round((substantialSections / sections.length) * 25) : 0) +
        (sections.length ? Math.round((headingsInRange / sections.length) * 15) : 0) +
        (draft.intro.length >= 70 && draft.intro.length <= 320 ? 15 : 7) +
        (draft.conclusion.length >= 60 ? 15 : 7) +
        (completeFaq >= 2 ? 10 : completeFaq * 4)
      ),
      reason: `H2 ${sections.length}本・十分な本文${substantialSections}本・完成FAQ${completeFaq}件を点検。`,
      action: "悩み→判断材料→現場例→次の一歩の順にし、長い段落を短く分ける。"
    },
    {
      id: "safety",
      label: "安全表現・正確性",
      weight: 10,
      score: clampScore(85 + Math.min(15, cautionWords * 3) - unsafeClaims.length * 28),
      reason: unsafeClaims.length
        ? `断定を避けたい表現を${unsafeClaims.length}件検出: ${unsafeClaims.join("、")}`
        : `強い断定は未検出。注意・配慮の表現を${cautionWords}件確認。`,
      action: "効果を断定せず、条件・例外・必要時の専門家相談を具体的にする。"
    },
    {
      id: "action",
      label: "読者の行動導線",
      weight: 9,
      score: clampScore(
        (draft.cta.length >= 18 ? 30 : 12) +
        Math.min(30, actionWords * 10) +
        ($("#audience").value.trim().length >= 20 ? 20 : 8) +
        (completeFaq >= 2 ? 20 : completeFaq * 8)
      ),
      reason: `CTA ${draft.cta.length}字・行動語${actionWords}件・不安解消FAQ${completeFaq}件を確認。`,
      action: "誰が、何を確認し、どの予約・相談・申込方法へ進むかを一つに絞る。"
    },
    {
      id: "alignment",
      label: "タイトル・本文整合",
      weight: 8,
      score: clampScore(
        titleOverlap * 60 +
        (draft.titleReviewReason.length >= 30 ? 20 : 8) +
        (draft.finalTitle.length >= 16 && draft.finalTitle.length <= 48 ? 20 : 10)
      ),
      reason: `最終タイトルと導入・H2・まとめの一致度を${Math.round(titleOverlap * 100)}%として確認。`,
      action: "本文完成後の中心メッセージに合わせ、タイトルかH2のどちらかを再調整する。"
    }
  ];
  const totalWeight = metrics.reduce((sum, item) => sum + item.weight, 0);
  const overall = clampScore(metrics.reduce((sum, item) => sum + item.score * item.weight, 0) / totalWeight);
  const priorities = [...metrics].sort((left, right) => left.score - right.score).slice(0, 3);
  return { overall, metrics, priorities, evaluatedAt: new Date().toISOString() };
}

function renderFinalEvaluation() {
  const evaluation = finalQualityEvaluation();
  const overallLabel = evaluation.overall >= 85 ? "公開前チェック良好" : evaluation.overall >= 70 ? "改善すると強くなる" : "再構成を推奨";
  $("#overall-score").innerHTML = `<strong>${evaluation.overall}</strong><span>/ 100<br>${overallLabel}</span>`;
  $("#quality-score-grid").innerHTML = evaluation.metrics.map((metric) => `
    <article class="score-card">
      <header><h3>${escapeHtml(metric.label)}</h3><strong>${metric.score}</strong></header>
      <div class="score-meter" role="progressbar" aria-label="${escapeHtml(metric.label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${metric.score}"><i style="--score:${metric.score}%"></i></div>
      <p>${escapeHtml(metric.reason)}</p><small>改善案: ${escapeHtml(metric.action)}</small>
    </article>`).join("");
  $("#priority-improvements").innerHTML = evaluation.priorities.map((metric) => `<li><b>${escapeHtml(metric.label)} ${metric.score}点:</b> ${escapeHtml(metric.action)}</li>`).join("");
}

async function makeDraft({ refine = false, trigger = null } = {}) {
  const outline = refine ? state.selectedOutline : selectedOutline();
  if (!outline) return toast("H2構成を1つ選んでください");
  state.selectedOutline = structuredClone(outline);
  const selectedTitle = $("#selected-title").value.trim();
  const button = trigger || (refine ? $("#refine-draft") : $("#make-draft"));
  const original = button.textContent;
  button.disabled = true;
  button.textContent = refine ? "本文へ再適用中…" : "本文を生成中…";
  try {
    const started = await api("/api/blog/draft", {
      method: "POST",
      body: JSON.stringify({
        ...payload(), report: state.research?.report || "", sources: state.research?.sources || [],
        selectedTitle, selectedOutline: state.selectedOutline, finalPrompt: $("#blog-final-prompt").value.trim(),
        ...(refine ? { currentDraft: state.draft } : {})
      })
    });
    const result = started.draft ? started : await pollDraft(started.id, refine, button);
    result.draft.references = state.research?.sources || [];
    state.draft = ensureDraftShape(result.draft);
    state.images = { hero: null, sections: state.draft.sections.map(() => null) };
    renderTitleReview();
    renderBlogEditFields();
    renderArticle();
    showStep(4);
    if (refine) toast("最終プロンプトを本文へ反映しました。画像は本文確定後に再生成してください。");
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.textContent = original; }
}

async function pollDraft(id, revised, button) {
  if (!id) throw new Error("記事生成ジョブを開始できませんでした。");
  for (let attempt = 0; attempt < 120; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
    const result = await api(`/api/blog/draft-status?id=${encodeURIComponent(id)}&profileId=${encodeURIComponent(state.profile.id)}&revised=${revised ? "1" : "0"}`);
    button.textContent = `本文を生成中… ${result.status}`;
    if (result.complete && result.draft) return result;
    if (["failed", "cancelled", "incomplete"].includes(result.status)) {
      throw new Error(result.error?.message || `記事生成が${result.status}になりました。`);
    }
  }
  throw new Error("記事生成に時間がかかっています。少し待ってから再試行してください。");
}

function renderTitleReview() {
  $("#title-review").innerHTML = `<b>本文完成後の最終タイトル</b><br>${escapeHtml(state.draft.finalTitle)}<br><small>${escapeHtml(state.draft.titleReviewReason)}</small>`;
}

function renderBlogEditFields() {
  if (!state.draft) return;
  const draft = state.draft;
  $("#blog-edit-fields").innerHTML = `
    <fieldset><legend>検索表示と導入</legend>
      <label>最終タイトル<input data-draft-field="finalTitle" value="${escapeHtml(draft.finalTitle)}"></label>
      <label>タイトル見直し理由<textarea data-draft-field="titleReviewReason" rows="2">${escapeHtml(draft.titleReviewReason)}</textarea></label>
      <label>SEOタイトル<input data-draft-field="metaTitle" value="${escapeHtml(draft.metaTitle)}"></label>
      <label>メタ説明<textarea data-draft-field="metaDescription" rows="3">${escapeHtml(draft.metaDescription)}</textarea></label>
      <label>一覧用要約<textarea data-draft-field="excerpt" rows="3">${escapeHtml(draft.excerpt)}</textarea></label>
      <label>導入文<textarea data-draft-field="intro" rows="5">${escapeHtml(draft.intro)}</textarea></label>
    </fieldset>
    <fieldset><legend>タイトル直下画像</legend>
      <label>画像プロンプト<textarea data-draft-field="heroImagePrompt" rows="4">${escapeHtml(draft.heroImagePrompt)}</textarea></label>
      <label>代替テキスト<input data-draft-field="heroImageAlt" value="${escapeHtml(draft.heroImageAlt)}"></label>
      <label>画像説明<input data-draft-field="heroImageCaption" value="${escapeHtml(draft.heroImageCaption)}"></label>
    </fieldset>
    ${draft.sections.map((section, index) => `<fieldset><legend>H2 ${index + 1} と直下画像</legend>
      <label>見出し<input data-section-field="heading" data-index="${index}" value="${escapeHtml(section.heading)}"></label>
      <label>本文<textarea data-section-field="body" data-index="${index}" rows="8">${escapeHtml(section.body)}</textarea></label>
      <label>画像プロンプト<textarea data-section-field="imagePrompt" data-index="${index}" rows="4">${escapeHtml(section.imagePrompt)}</textarea></label>
      <label>代替テキスト<input data-section-field="imageAlt" data-index="${index}" value="${escapeHtml(section.imageAlt)}"></label>
      <label>画像説明<input data-section-field="imageCaption" data-index="${index}" value="${escapeHtml(section.imageCaption)}"></label>
    </fieldset>`).join("")}
    <fieldset><legend>結論と行動</legend>
      <label>まとめ<textarea data-draft-field="conclusion" rows="5">${escapeHtml(draft.conclusion)}</textarea></label>
      <label>CTA<textarea data-draft-field="cta" rows="3">${escapeHtml(draft.cta)}</textarea></label>
    </fieldset>
    <fieldset><legend>FAQ</legend>${draft.faq.map((item, index) => `
      <label>質問 ${index + 1}<input data-faq-field="question" data-index="${index}" value="${escapeHtml(item.question)}"></label>
      <label>回答 ${index + 1}<textarea data-faq-field="answer" data-index="${index}" rows="3">${escapeHtml(item.answer)}</textarea></label>`).join("")}
    </fieldset>
    <fieldset><legend>出典と事実確認</legend>${draft.references.map((item, index) => `
      <div class="reference-editor"><label>出典名<input data-reference-field="title" data-index="${index}" value="${escapeHtml(item.title)}"></label>
      <label>URL<input data-reference-field="url" data-index="${index}" value="${escapeHtml(item.url)}"></label>
      <label>この記事で支える内容<textarea data-reference-field="claim" data-index="${index}" rows="2">${escapeHtml(item.claim)}</textarea></label></div>`).join("")}
      <label>公開前の事実確認（1行1件）<textarea data-fact-checks rows="4">${escapeHtml(draft.factChecks.join("\n"))}</textarea></label>
    </fieldset>
    <fieldset><legend>同じ実践知の再編集</legend>
      <label>SNS案<textarea data-repurpose-field="sns" rows="3">${escapeHtml(draft.repurpose.sns)}</textarea></label>
      <label>note案<textarea data-repurpose-field="note" rows="3">${escapeHtml(draft.repurpose.note)}</textarea></label>
      <label>YouTube案<textarea data-repurpose-field="youtube" rows="3">${escapeHtml(draft.repurpose.youtube)}</textarea></label>
    </fieldset>`;
}

function syncBlogEdit(event) {
  if (!state.draft) return;
  const target = event.target;
  if (target.dataset.draftField) {
    state.draft[target.dataset.draftField] = target.value;
    if (["finalTitle", "heroImagePrompt", "heroImageAlt"].includes(target.dataset.draftField)) state.images.hero = null;
    if (target.dataset.draftField === "finalTitle") state.images.sections = state.images.sections.map(() => null);
  }
  if (target.dataset.sectionField) {
    const index = Number(target.dataset.index);
    state.draft.sections[index][target.dataset.sectionField] = target.value;
    if (["heading", "imagePrompt", "imageAlt"].includes(target.dataset.sectionField)) state.images.sections[index] = null;
  }
  if (target.dataset.faqField) state.draft.faq[Number(target.dataset.index)][target.dataset.faqField] = target.value;
  if (target.dataset.referenceField) state.draft.references[Number(target.dataset.index)][target.dataset.referenceField] = target.value;
  if (target.dataset.repurposeField) state.draft.repurpose[target.dataset.repurposeField] = target.value;
  if (target.hasAttribute("data-fact-checks")) state.draft.factChecks = lines(target.value);
  if (!state.images.hero || state.images.sections.some((item) => !item)) $("#image-status").textContent = "本文または画像指示を編集しました。公開前に画像を再生成してください。";
  renderTitleReview();
  renderArticle();
}

function imageBlock(src, prompt, alt, caption, className) {
  return `<figure class="${className}">${src ? `<img src="${src}" alt="${escapeHtml(alt)}">` : `<div class="image-placeholder"><span>画像生成前</span><small>${escapeHtml(prompt)}</small></div>`}<figcaption>${escapeHtml(caption)}</figcaption></figure>`;
}

function renderArticle() {
  if (!state.draft) return;
  const draft = state.draft;
  const refs = draft.references.filter((item) => safeUrl(item.url));
  $("#article-preview").innerHTML = `
    <span class="article-kicker">${escapeHtml(state.profile.name)} JOURNAL</span>
    <h1 contenteditable="true" data-preview-field="finalTitle">${escapeHtml(draft.finalTitle)}</h1>
    <div class="article-meta">${escapeHtml(state.profile.area)}・公開前プレビュー</div>
    ${imageBlock(state.images.hero, draft.heroImagePrompt, draft.heroImageAlt, draft.heroImageCaption, "article-hero")}
    <p class="article-intro" contenteditable="true" data-preview-field="intro">${paragraphHtml(draft.intro)}</p>
    ${draft.sections.map((section, index) => `<section>
      <h2 contenteditable="true" data-preview-section-field="heading" data-index="${index}">${escapeHtml(section.heading)}</h2>
      ${imageBlock(state.images.sections[index], section.imagePrompt, section.imageAlt, section.imageCaption, "section-image")}
      <p contenteditable="true" data-preview-section-field="body" data-index="${index}">${paragraphHtml(section.body)}</p>
    </section>`).join("")}
    <p contenteditable="true" data-preview-field="conclusion">${paragraphHtml(draft.conclusion)}</p>
    <div class="article-cta"><b>次の一歩</b><p contenteditable="true" data-preview-field="cta">${paragraphHtml(draft.cta)}</p></div>
    <section class="article-faq"><h2>よくある質問</h2>${draft.faq.map((item, index) => `<h3 contenteditable="true" data-preview-faq-field="question" data-index="${index}">Q. ${escapeHtml(item.question)}</h3><p contenteditable="true" data-preview-faq-field="answer" data-index="${index}">${paragraphHtml(item.answer)}</p>`).join("")}</section>
    ${refs.length ? `<section class="article-references"><h2>参考情報</h2><ol>${refs.map((item) => `<li><a href="${escapeHtml(safeUrl(item.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title || item.url)}</a>${item.claim ? `<small>${escapeHtml(item.claim)}</small>` : ""}</li>`).join("")}</ol></section>` : ""}`;
  renderFinalEvaluation();
}

async function generateImages() {
  if (!state.draft) return toast("先に記事を作成してください");
  const button = $("#generate-images");
  button.disabled = true;
  const jobs = [
    { type: "hero", prompt: state.draft.heroImagePrompt, alt: state.draft.heroImageAlt },
    ...state.draft.sections.map((section, index) => ({ type: "section", index, prompt: section.imagePrompt, alt: section.imageAlt }))
  ];
  try {
    for (let index = 0; index < jobs.length; index += 1) {
      const job = jobs[index];
      $("#image-status").textContent = `${jobs.length}枚中 ${index + 1}枚目を生成中…`;
      const result = await api("/api/blog/image", {
        method: "POST",
        body: JSON.stringify({ ...job, profileId: state.profile.id, finalTitle: state.draft.finalTitle, finalPrompt: $("#blog-final-prompt").value.trim() })
      });
      if (result.mock) { $("#image-status").textContent = result.message; break; }
      if (job.type === "hero") state.images.hero = result.image;
      else state.images.sections[job.index] = result.image;
      renderArticle();
    }
    if (state.images.hero) $("#image-status").textContent = `${jobs.length}枚の画像を生成しました`;
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; }
}

function structuredData() {
  const draft = state.draft;
  const pageUrl = payload().officialUrls[0] || undefined;
  const images = [state.images.hero, ...state.images.sections].filter(Boolean);
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "BlogPosting", headline: draft.finalTitle, description: draft.metaDescription,
        image: images, author: { "@type": "Organization", name: state.profile.name },
        publisher: { "@type": "Organization", name: state.profile.name },
        dateModified: today(), ...(pageUrl ? { mainEntityOfPage: pageUrl } : {}),
        speakable: { "@type": "SpeakableSpecification", cssSelector: ["h1", ".article-intro", ".article-faq"] }
      },
      { "@type": "FAQPage", mainEntity: draft.faq.map((item) => ({ "@type": "Question", name: item.question, acceptedAnswer: { "@type": "Answer", text: item.answer } })) }
    ]
  };
}

function articleHtml() {
  const clone = $("#article-preview").cloneNode(true);
  clone.querySelectorAll("[contenteditable]").forEach((item) => item.removeAttribute("contenteditable"));
  clone.querySelectorAll("[data-preview-field],[data-preview-section-field],[data-preview-faq-field],[data-index]").forEach((item) => {
    item.removeAttribute("data-preview-field");
    item.removeAttribute("data-preview-section-field");
    item.removeAttribute("data-preview-faq-field");
    item.removeAttribute("data-index");
  });
  const jsonLd = JSON.stringify(structuredData()).replace(/<\//g, "<\\/");
  return `<script type="application/ld+json">${jsonLd}</script>\n${clone.innerHTML}`;
}

function articleMarkdown() {
  const draft = state.draft;
  return [`# ${draft.finalTitle}`, "", draft.intro, "", ...draft.sections.flatMap((section) => [`## ${section.heading}`, "", section.body, "", `> 画像: ${section.imageCaption}`, ""]), "## まとめ", "", draft.conclusion, "", `**次の一歩:** ${draft.cta}`, "", "## よくある質問", "", ...draft.faq.flatMap((item) => [`### ${item.question}`, "", item.answer, ""]), "## 参考情報", "", ...draft.references.map((item) => `- [${item.title || item.url}](${item.url}) ${item.claim || ""}`)].join("\n");
}

function packageData() {
  return {
    version: 1,
    schema: "content-studio.blog-draft",
    schemaVersion: 1,
    kind: "blog",
    createdAt: new Date().toISOString(),
    profile: state.profile,
    input: payload(),
    trendDiscovery: state.trendDiscovery,
    selectedTrend: state.selectedTrend,
    research: state.research,
    titlePlan: state.titlePlan,
    outlinePlan: state.outlinePlan,
    selectedOutline: state.selectedOutline,
    finalPrompt: $("#blog-final-prompt").value.trim(),
    draft: state.draft,
    qualityEvaluation: finalQualityEvaluation(),
    images: state.images
  };
}

function handoffBlogDraft() {
  if (!STUDIO_CONFIG.localAdmin) return toast("記事の受け渡しは各サイトの管理画面版で使用してください");
  if (!state.draft) return toast("先に記事を作成してください");
  try {
    const key = `contentStudioDraft:${state.profile.id}`;
    handoffToAdmin("blog", packageData(), key);
    toast("管理画面へ記事を渡しました");
  } catch (error) {
    toast(`記事を渡せませんでした: ${error.message}`);
  }
}

function downloadBlob(blob, filename) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
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

async function dataUrlBlob(value) {
  return value ? fetch(value).then((response) => response.blob()) : null;
}

async function saveBlogPackage() {
  if (!state.draft) return toast("先に記事を作成してください");
  if (!window.showDirectoryPicker) return toast("ChromeまたはEdgeで開き、保存先の事業フォルダを選択してください");
  try {
    const root = await window.showDirectoryPicker({ mode: "readwrite", id: `blog-${state.profile.id}` });
    const folderName = `${today()}-${slugify(state.draft.finalTitle)}`;
    const directory = await nestedDirectory(root, ["content", "blog-drafts", folderName]);
    await writeFile(directory, "README.md", `# ${state.draft.finalTitle}\n\n- 事業: ${state.profile.name}\n- 対象: ${payload().audience}\n- 状態: 公開前下書き\n- 次の作業: 事実確認、画像確認、CMS入稿、公開URL追記\n`);
    await writeFile(directory, "article.html", articleHtml());
    await writeFile(directory, "article.md", articleMarkdown());
    await writeFile(directory, "article.json", JSON.stringify(packageData(), null, 2));
    const assets = await directory.getDirectoryHandle("assets", { create: true });
    const hero = await dataUrlBlob(state.images.hero);
    if (hero) await writeFile(assets, "hero.webp", hero);
    for (let index = 0; index < state.images.sections.length; index += 1) {
      const image = await dataUrlBlob(state.images.sections[index]);
      if (image) await writeFile(assets, `h2-${index + 1}.webp`, image);
    }
    toast(`content/blog-drafts/${folderName} に保存しました`);
  } catch (error) {
    if (error.name !== "AbortError") toast(`保存できませんでした: ${error.message}`);
  }
}

$("#profile").addEventListener("change", () => applyProfile({ reset: true }));
$("#entry-guide").addEventListener("click", (event) => {
  const starterButton = event.target.closest("[data-entry-starter]");
  if (starterButton) {
    const starter = state.profile?.entryGuide?.topicStarters?.[Number(starterButton.dataset.entryIndex)];
    return applyTopicStarter(starter);
  }
  const searchButton = event.target.closest("[data-entry-search]");
  if (!searchButton) return;
  const searchQuery = state.profile?.entryGuide?.searchQueries?.[Number(searchButton.dataset.entrySearch)];
  if (!searchQuery) return;
  state.entryStarter = {
    id: "search",
    label: "検索の入口から",
    topic: searchQuery,
    searchQuery,
    storyQuestion: state.profile?.entryGuide?.storyQuestions?.[0] || ""
  };
  $("#topic").value = searchQuery;
  $$("[data-entry-starter]").forEach((button) => {
    button.classList.remove("selected");
    button.setAttribute("aria-pressed", "false");
  });
  toast("検索の入口をテーマ欄へ入れました。ライブ調査で実際の傾向を確認してください。");
});
$("#owner-story").addEventListener("input", () => { state.storyTemplateActive = false; });
$("#discover-trends").addEventListener("click", discoverTrends);
$("#start-research").addEventListener("click", startResearch);
$("#make-plan").addEventListener("click", makePlan);
$("#make-outlines").addEventListener("click", makeOutlines);
$("#make-draft").addEventListener("click", () => makeDraft());
$("#refine-draft").addEventListener("click", () => makeDraft({ refine: true }));
$("#generate-images").addEventListener("click", generateImages);
$("#save-blog-package").addEventListener("click", saveBlogPackage);
$("#handoff-blog-draft").addEventListener("click", handoffBlogDraft);
$("#show-preview").addEventListener("click", () => {
  if (!state.draft) return toast("先に記事を作成してください");
  renderFinalEvaluation();
  showStep(5);
  $("#back-editor").hidden = false;
});
$("#back-editor").addEventListener("click", () => {
  $("#back-editor").hidden = true;
  showStep(4);
});
$("#return-outline").addEventListener("click", () => {
  $("#back-editor").hidden = true;
  showStep(3);
  toast("タイトルとH2構成を選び直せます。現在の記事は再生成するまで保持されます");
});
$("#apply-restructure").addEventListener("click", async () => {
  const instruction = $("#restructure-prompt").value.trim();
  if (!instruction) return toast("変えたい点や構成の順番を入力してください");
  const currentPrompt = $("#blog-final-prompt").value.trim();
  $("#blog-final-prompt").value = [currentPrompt, `公開前評価を踏まえた再構成指示: ${instruction}`].filter(Boolean).join("\n");
  await makeDraft({ refine: true, trigger: $("#apply-restructure") });
});
$("#preview-desktop").addEventListener("click", () => $(".preview-column").classList.remove("mobile-preview"));
$("#preview-mobile").addEventListener("click", () => $(".preview-column").classList.add("mobile-preview"));
$("#title-options").addEventListener("change", (event) => {
  if (event.target.name === "title-option") $("#selected-title").value = state.titlePlan.titles[Number(event.target.value)].title;
});
$("#trend-options").addEventListener("click", (event) => {
  const button = event.target.closest("[data-trend-index]");
  if (!button) return;
  const idea = state.trendDiscovery?.ideas?.[Number(button.dataset.trendIndex)];
  if (!idea) return;
  state.selectedTrend = idea;
  state.entryStarter = {
    id: "live-trend",
    label: "ライブ国内トレンドから",
    topic: idea.topic,
    searchQuery: idea.topic,
    storyQuestion: state.profile?.entryGuide?.storyQuestions?.[0] || ""
  };
  $("#topic").value = idea.topic;
  $("#audience").value = idea.audience || state.profile.audience || "";
  $$('[data-trend-card]').forEach((card) => card.classList.toggle("selected", card.dataset.trendCard === button.dataset.trendIndex));
  startResearch();
});
$("#title-options").addEventListener("input", (event) => {
  if (!event.target.dataset.titleField) return;
  const index = Number(event.target.dataset.index);
  state.titlePlan.titles[index][event.target.dataset.titleField] = event.target.value;
  if ($(`input[name='title-option'][value='${index}']`)?.checked && event.target.dataset.titleField === "title") $("#selected-title").value = event.target.value;
});
$("#outline-options").addEventListener("input", (event) => {
  const group = state.outlinePlan?.outlineGroups?.[Number(event.target.dataset.group)];
  if (!group) return;
  if (event.target.dataset.outlineField) group[event.target.dataset.outlineField] = event.target.value;
  if (event.target.dataset.headingField) group.headings[Number(event.target.dataset.heading)][event.target.dataset.headingField] = event.target.value;
});
$("#copy-html").addEventListener("click", async () => {
  if (!state.draft) return toast("先に記事を作成してください");
  await navigator.clipboard.writeText(articleHtml());
  toast("構造化データ付きHTMLをコピーしました");
});
$("#download-json").addEventListener("click", () => {
  if (!state.draft) return toast("先に記事を作成してください");
  downloadBlob(new Blob([JSON.stringify(packageData(), null, 2)], { type: "application/json" }), `blog-${state.profile.id}-${today()}.json`);
});
$("#blog-edit-fields").addEventListener("input", syncBlogEdit);
$("#article-preview").addEventListener("input", (event) => {
  if (!state.draft) return;
  const target = event.target;
  const value = target.innerText.trim();
  if (target.dataset.previewField) {
    state.draft[target.dataset.previewField] = value;
    if (target.dataset.previewField === "finalTitle") {
      state.images.hero = null;
      state.images.sections = state.images.sections.map(() => null);
    }
  }
  if (target.dataset.previewSectionField) {
    const index = Number(target.dataset.index);
    state.draft.sections[index][target.dataset.previewSectionField] = value;
    if (target.dataset.previewSectionField === "heading") state.images.sections[index] = null;
  }
  if (target.dataset.previewFaqField) {
    const cleanValue = target.dataset.previewFaqField === "question" ? value.replace(/^Q\.\s*/, "") : value;
    state.draft.faq[Number(target.dataset.index)][target.dataset.previewFaqField] = cleanValue;
  }
  renderFinalEvaluation();
});
$("#blog-final-prompt").addEventListener("input", () => {
  if (!state.draft) return;
  state.images = { hero: null, sections: state.draft.sections.map(() => null) };
  $("#image-status").textContent = "最終調整プロンプトが変わりました。本文へ再適用後、画像を再生成してください。";
  renderArticle();
});

configureStudioShell();
enableEmbeddedAutoHeight();
initialize().catch((error) => { $("#server-state").textContent = "接続エラー"; toast(error.message); });
