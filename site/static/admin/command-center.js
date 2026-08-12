(() => {
  const body = document.body;
  const view = body.dataset.view || "dashboard";
  const content = document.getElementById("cc-content");
  const live = document.getElementById("cc-live");
  const state = { dashboard: null, market: null, screen: null, security: null, sources: null };
  const dashboardViews = ["dashboard", "calendar", "tasks", "businesses", "directives", "studio", "tools", "trade"];
  const marketViews = ["market", "screener", "security", "trade-plan", "trade-plans", "trades", "market-sources"];
  const views = [...dashboardViews, ...marketViews];
  const viewLabels = {
    calendar: "カレンダー", tasks: "タスク", businesses: "事業", directives: "指示", studio: "Codex連携", tools: "検証・移行", trade: "相場羅針盤",
    market: "市場候補", screener: "財務スクリーナー", security: "銘柄詳細", "trade-plan": "取引プラン作成", "trade-plans": "登録プラン", trades: "取引記録", "market-sources": "データ収集状況",
  };
  const screeningRules = [
    ["売上高・営業利益", "過去3年間、両方が右肩上がりか"],
    ["自己資本比率", "一般企業は40％以上か。銀行・保険・REITは業種別確認"],
    ["配当性向", "利益が正で50％以下か"],
    ["連続増配年数", "長いほどよい。単独では合否を決めない"],
    ["PER", "15倍以下を一次目安。低PERの理由も確認"],
    ["営業キャッシュフロー", "直近3年間が安定してプラスか"],
    ["有利子負債", "3年連続で増え続けていないか"],
    ["EPS", "希薄化後EPSが継続的に成長しているか"],
    ["配当の現金余力", "配当を利益だけでなく現金で賄えているか"],
    ["特別利益", "一時的な特別利益だけで増益になっていないか"],
    ["会社予想", "今後の業績予想が減収・営業減益ではないか"],
    ["過去PER・PBR比較", "現在値が過去5年中央値より高すぎないか"],
  ];

  const esc = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
  const japanDateKey = (value = new Date()) => {
    const parts = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(value);
    const part = (type) => parts.find((item) => item.type === type)?.value || "";
    return `${part("year")}-${part("month")}-${part("day")}`;
  };
  const today = () => japanDateKey();
  const addDays = (value, amount) => { const date = new Date(`${value}T00:00:00Z`); date.setUTCDate(date.getUTCDate() + amount); return date.toISOString().slice(0, 10); };
  const setLive = (message, error = false) => { live.textContent = message || ""; live.classList.toggle("is-error", Boolean(error)); };
  const badge = (value, tone = "") => `<span class="cc-badge ${tone ? `cc-badge--${tone}` : ""}">${esc(value)}</span>`;
  const empty = (message) => `<div class="cc-empty">${esc(message)}</div>`;
  const safeExternalUrl = (value) => {
    try {
      const url = new URL(String(value || ""));
      return url.protocol === "https:" || url.protocol === "http:" ? url.href : "";
    } catch { return ""; }
  };

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, { credentials: "same-origin", cache: "no-store", ...options, headers: { "Accept": "application/json", ...(options.headers || {}) } });
    if (response.status === 401 || response.status === 303) { window.location.href = `/admin/login?next=${encodeURIComponent(window.location.pathname)}`; throw new Error("login_required"); }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || `request_failed_${response.status}`);
    return payload;
  }
  async function loadDashboard() { state.dashboard = await fetchJson("/api/admin/command-center/data"); return state.dashboard; }
  async function postData(payload) { state.dashboard = await fetchJson("/api/admin/command-center/data", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); render(); }
  function layout(title, description, inner) { return `<div class="cc-stack"><section class="cc-card"><div class="cc-section-head"><div><p class="cc-kicker">EXECUTION COMMAND ROOM</p><h2>${esc(title)}</h2><p>${esc(description)}</p></div></div>${inner}</section></div>`; }
  function metric(label, value, hint) { return `<article class="cc-card cc-metric"><span>${esc(label)}</span><strong>${esc(value)}</strong><small class="cc-muted">${esc(hint)}</small></article>`; }
  function formatNumber(value, suffix = "") { if (value === null || value === undefined || value === "") return "—"; const number = Number(value); return Number.isFinite(number) ? `${new Intl.NumberFormat("ja-JP", { maximumFractionDigits: 2 }).format(number)}${suffix}` : "—"; }
  function decisionLabel(value) { return ({ research_candidate: "一次調査候補", watch: "監視", deprioritize: "優先度を下げる", insufficient_data: "データ不足" }[value] || "データ不足"); }
  function decisionTone(value) { return value === "research_candidate" ? "ok" : value === "deprioritize" ? "rose" : "warn"; }
  function ruleStatusLabel(value) { return ({ pass: "合格", check: "要確認", fail: "不合格", na: "対象外", missing: "データ不足" }[value] || "データ不足"); }
  function ruleTone(value) { return value === "pass" ? "ok" : value === "fail" ? "rose" : "warn"; }
  function checklistMarkup() {
    return `<div class="cc-checklist">${screeningRules.map(([label, description], index) => `<article class="cc-rule-guide"><span>${index + 1}</span><div><strong>${esc(label)}</strong><small>${esc(description)}</small></div></article>`).join("")}</div>`;
  }

  function renderDashboard() {
    const data = state.dashboard;
    const tasks = data.tasks || [];
    const openTasks = tasks.filter((task) => task.status !== "done").length;
    const waiting = tasks.filter((task) => task.status === "waiting").length;
    const openTrades = (data.trades || []).filter((trade) => trade.status === "open").length;
    const cards = `<div class="cc-grid cc-grid--metrics">${metric("未完了タスク", openTasks, `${waiting}件が確認待ち`)}${metric("登録事業", (data.projects || []).length, "保護された事業一覧")}${metric("実行指示", (data.directives || []).length, "最新の指示を確認")}${metric("保有記録", openTrades, "相場羅針盤の未決済")}</div>`;
    const links = views.slice(1).map((item) => `<a class="cc-card cc-link-card" href="/admin/command-center/${item}"><p class="cc-kicker">${esc(item.toUpperCase())}</p><h3>${esc(viewLabels[item])}</h3><p class="cc-muted">この領域だけを開いて確認・実行できます。</p></a>`).join("");
    content.innerHTML = `${cards}<div class="cc-grid cc-grid--two" style="margin-top:14px">${links}</div>`;
  }

  function renderTasks() {
    const tasks = state.dashboard.tasks || [];
    const rows = tasks.length ? tasks.map((task) => `<tr><td><strong>${esc(task.title)}</strong><br><small class="cc-muted">${esc(task.reason)}</small></td><td>${esc(task.businessId)}</td><td>${esc(task.dueDate)}</td><td><select class="cc-select" data-task-id="${esc(task.id)}" aria-label="${esc(task.title)}の状態"><option value="today" ${task.status === "today" ? "selected" : ""}>今日</option><option value="planned" ${task.status === "planned" ? "selected" : ""}>予定</option><option value="waiting" ${task.status === "waiting" ? "selected" : ""}>確認待ち</option><option value="done" ${task.status === "done" ? "selected" : ""}>完了</option></select></td></tr>`).join("") : `<tr><td colspan="4">${empty("タスクはまだありません")}</td></tr>`;
    content.innerHTML = layout("タスク", "今日やること、確認待ち、期限を一画面で整えます。", `<div class="cc-grid cc-grid--two"><form class="cc-card cc-form" id="task-form"><h3>タスクを追加</h3><div class="cc-form-grid"><div class="cc-field"><label for="task-business">事業ID</label><input class="cc-input" id="task-business" required maxlength="80" placeholder="例: ai-consult"></div><div class="cc-field"><label for="task-due">期限</label><input class="cc-input" id="task-due" type="date" required value="${today()}"></div><div class="cc-field cc-field--full"><label for="task-title">タイトル</label><input class="cc-input" id="task-title" required maxlength="180"></div></div><button class="cc-button cc-button--primary" type="submit">追加する</button></form><div class="cc-card"><h3>状態の使い分け</h3><ul class="cc-list"><li><strong>今日</strong><span class="cc-muted">今日動かすもの</span></li><li><strong>確認待ち</strong><span class="cc-muted">判断や承認が必要なもの</span></li></ul></div></div><div class="cc-table-wrap" style="margin-top:14px"><table class="cc-table"><thead><tr><th>タスク</th><th>事業</th><th>期限</th><th>状態</th></tr></thead><tbody>${rows}</tbody></table></div>`);
    document.getElementById("task-form")?.addEventListener("submit", async (event) => { event.preventDefault(); try { setLive("タスクを保存しています…"); await postData({ action: "create_task", businessId: document.getElementById("task-business").value, title: document.getElementById("task-title").value, dueDate: document.getElementById("task-due").value, priority: 2 }); setLive("タスクを追加しました。"); } catch (error) { setLive(error.message, true); } });
    document.querySelectorAll("[data-task-id]").forEach((select) => select.addEventListener("change", async (event) => { try { setLive("状態を更新しています…"); await postData({ action: "update_task", id: event.target.dataset.taskId, status: event.target.value }); setLive("状態を更新しました。"); } catch (error) { setLive(error.message, true); } }));
  }

  function renderBusinesses() {
    const projects = state.dashboard.projects || [];
    const rows = projects.length ? projects.map((project) => { const productionUrl = safeExternalUrl(project.productionUrl); return `<tr><td><strong>${esc(project.displayName)}</strong><br><small class="cc-muted">${esc(project.businessId)}</small></td><td>${badge(project.statusLabel || project.status, project.status === "active" ? "ok" : "")}</td><td>${productionUrl ? `<a href="${esc(productionUrl)}" target="_blank" rel="noreferrer">公開ページ</a>` : "—"}</td><td>${esc(project.lastReviewDate)}</td></tr>`; }).join("") : `<tr><td colspan="4">${empty("事業データはまだありません")}</td></tr>`;
    content.innerHTML = layout("事業一覧", "事業ごとの状態と公開導線だけを確認します。", `<div class="cc-table-wrap"><table class="cc-table"><thead><tr><th>事業</th><th>状態</th><th>公開URL</th><th>最終確認</th></tr></thead><tbody>${rows}</tbody></table></div>`);
  }

  function renderDirectives() {
    const directives = state.dashboard.directives || [];
    const rows = directives.length ? directives.map((item) => `<li><strong>${esc(item.businessId)} / ${esc(item.mode)}</strong><span class="cc-copy">${esc(item.instruction)}</span><small class="cc-muted">${esc(item.createdAtLabel || item.createdAt)}</small></li>`).join("") : `<li>${empty("指示はまだありません")}</li>`;
    content.innerHTML = layout("実行指示", "調査・下書き・実装・保留を明示して、判断の境界を残します。", `<div class="cc-grid cc-grid--two"><form class="cc-card cc-form" id="directive-form"><h3>指示を追加</h3><div class="cc-field"><label for="directive-business">事業ID</label><input class="cc-input" id="directive-business" required maxlength="80"></div><div class="cc-field"><label for="directive-mode">モード</label><select class="cc-select" id="directive-mode"><option value="research">調査</option><option value="draft">下書き</option><option value="implement">実装</option><option value="hold">保留</option></select></div><div class="cc-field"><label for="directive-instruction">指示</label><textarea class="cc-textarea" id="directive-instruction" required maxlength="800"></textarea></div><button class="cc-button cc-button--primary" type="submit">指示を保存</button></form><div class="cc-card"><h3>最近の指示</h3><ul class="cc-list">${rows}</ul></div></div>`);
    document.getElementById("directive-form")?.addEventListener("submit", async (event) => { event.preventDefault(); try { setLive("指示を保存しています…"); await postData({ action: "create_directive", businessId: document.getElementById("directive-business").value, mode: document.getElementById("directive-mode").value, instruction: document.getElementById("directive-instruction").value }); setLive("指示を保存しました。"); } catch (error) { setLive(error.message, true); } });
  }

  async function renderCalendar() {
    const from = today(); const to = addDays(from, 6);
    content.innerHTML = layout("カレンダー", "Google予定は忙しさの件数だけ、課題は期限とタイトルだけを表示します。", `<form class="cc-actions" id="calendar-form"><label class="cc-field"><span>開始日</span><input class="cc-input" id="calendar-from" type="date" value="${from}"></label><label class="cc-field"><span>終了日</span><input class="cc-input" id="calendar-to" type="date" value="${to}"></label><button class="cc-button cc-button--primary" type="submit">更新</button></form><div id="calendar-result" style="margin-top:14px">読み込み中…</div>`);
    const load = async (start, end) => {
      const result = document.getElementById("calendar-result");
      const deadlinesByDate = new Map();
      for (const task of state.dashboard?.tasks || []) {
        if (task.status === "done" || typeof task.dueDate !== "string" || task.dueDate < start || task.dueDate > end) continue;
        const tasks = deadlinesByDate.get(task.dueDate) || [];
        tasks.push(task);
        deadlinesByDate.set(task.dueDate, tasks);
      }
      result.textContent = "取得中…";
      try {
        const payload = await fetchJson(`/api/admin/command-center/calendar?from=${encodeURIComponent(start)}&to=${encodeURIComponent(end)}`);
        const days = (payload.days || []).map((day) => {
          const deadlines = deadlinesByDate.get(day.date) || [];
          const classes = ["cc-day", day.busyCount ? "is-busy" : "", deadlines.length ? "is-deadline" : ""].filter(Boolean).join(" ");
          return `<div class="${classes}"><strong>${esc(day.date.slice(5))}</strong><span>${day.busyCount ? `${esc(day.busyCount)}件 忙しい` : "予定なし"}</span>${deadlines.length ? `<span class="cc-deadline-count">期限 ${esc(deadlines.length)}件</span>` : ""}</div>`;
        }).join("");
        const deadlineList = [...deadlinesByDate.entries()].sort(([left], [right]) => left.localeCompare(right)).map(([date, tasks]) => `<li><strong>${esc(date)} / 期限 ${esc(tasks.length)}件</strong><span class="cc-muted">${tasks.map((task) => `${esc(task.title)}（${esc(task.status)}）`).join("、")}</span></li>`).join("");
        result.innerHTML = `<p class="cc-muted">${esc(payload.accountLabel)} / ${esc(payload.privacy)} / ${esc(payload.status)}</p><div class="cc-calendar">${days}</div><section class="cc-card cc-deadline-list"><h3>課題の期限</h3><ul class="cc-list">${deadlineList || `<li class="cc-muted">この期間の課題期限はありません。</li>`}</ul></section>`;
      } catch (error) { result.innerHTML = empty(error.message); }
    };
    await load(from, to);
    document.getElementById("calendar-form")?.addEventListener("submit", async (event) => { event.preventDefault(); await load(document.getElementById("calendar-from").value, document.getElementById("calendar-to").value); });
  }

  async function renderStudio() {
    content.innerHTML = layout("Codex連携", "PC上のCodexは秘密をブラウザへ渡さず、HMAC付きリレーで接続します。", `<div id="studio-result">接続状態を確認中…</div><form class="cc-form" id="pair-form" style="margin-top:14px"><div class="cc-field"><label for="pair-code">PCに表示された6桁コード</label><input class="cc-input" id="pair-code" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autocomplete="one-time-code" required></div><button class="cc-button cc-button--primary" type="submit">このPCをペアリング</button></form>`);
    const result = document.getElementById("studio-result");
    try { const payload = await fetchJson("/api/admin/command-center/relay"); result.innerHTML = `<div class="cc-grid cc-grid--two"><div class="cc-card"><p class="cc-kicker">接続状態</p><h3>${payload.connected ? badge("接続中", "ok") : badge("未接続", "warn")}</h3><p class="cc-muted">${payload.heartbeatAt ? `最終通信: ${esc(payload.heartbeatAt)}` : "PC bridgeの起動を待っています。"}</p></div><div class="cc-card"><p class="cc-kicker">ペアリング</p><h3>${payload.paired ? badge("ペア済み", "ok") : badge("未ペア", "warn")}</h3><p class="cc-muted">コードは保存せず、一度だけ送信します。</p></div></div>`; } catch (error) { result.innerHTML = empty(error.message); }
    document.getElementById("pair-form")?.addEventListener("submit", async (event) => { event.preventDefault(); try { setLive("ペアリングしています…"); await fetchJson("/api/admin/command-center/relay", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "pair", code: document.getElementById("pair-code").value }) }); setLive("ペアリングしました。"); await renderStudio(); } catch (error) { setLive(error.message, true); } });
  }

  async function renderTools() {
    content.innerHTML = layout("検証・移行", "旧D1からの移行は、件数とハッシュを検証してから確定します。", `<div class="cc-grid cc-grid--two"><div class="cc-card"><h3>旧データを取り込む</h3><p class="cc-muted">顧客情報・認証情報はレスポンスへ返さず、保護されたDBへ直接保存します。</p><button class="cc-button cc-button--primary" id="migrate-button" type="button">移行を実行</button><div id="migration-result" style="margin-top:12px"></div></div><div class="cc-card"><h3>削除ゲート</h3><ul class="cc-list"><li>新画面の表示・更新確認</li><li>件数・ハッシュ・再取得確認</li><li>バックアップと切り戻し確認</li><li>最後に旧Sitesとフォルダを削除</li></ul></div></div>`);
    document.getElementById("migrate-button")?.addEventListener("click", async () => { const result = document.getElementById("migration-result"); result.textContent = "移行中…"; try { const payload = await fetchJson("/api/admin/command-center/migrate", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); result.innerHTML = `<p>${badge("移行・検証済み", "ok")}</p><p class="cc-muted">件数: ${esc(JSON.stringify(payload.verified))}<br>ハッシュ: <code>${esc(payload.sourceDigest)}</code></p>`; await loadDashboard(); } catch (error) { result.innerHTML = `<p>${badge("移行失敗", "rose")}</p><p class="cc-muted">${esc(error.message)}</p>`; } });
  }

  function marketMarkup(market) {
    const candidates = Array.isArray(market?.candidates) ? market.candidates : [];
    const rows = candidates.slice(0, 24).map((candidate) => {
      const details = candidate.market === "JP" && /^\d{4}$/.test(String(candidate.symbol || ""))
        ? `<a class="cc-inline-link" href="/admin/command-center/security?symbol=${encodeURIComponent(candidate.symbol)}">12項目を見る</a>`
        : `<span class="cc-muted">価格候補のみ</span>`;
      return `<tr><td><strong>${esc(candidate.name)}</strong><br><small class="cc-muted">${esc(candidate.symbol)} / ${esc(candidate.market)}</small></td><td>${formatNumber(candidate.price)} ${esc(candidate.currency || "")}</td><td>${formatNumber(candidate.changePercent, "%")}</td><td>${badge(decisionLabel(candidate.decision), decisionTone(candidate.decision))}<br><small class="cc-muted">充足率 ${formatNumber(candidate.dataCoverage, "%")}</small></td><td>${esc(candidate.whyNow || "一次情報を確認してください。")}<br>${details}</td></tr>`;
    }).join("");
    const missing = Array.isArray(market?.missingEvidence) ? market.missingEvidence : [];
    return `<div class="cc-grid cc-grid--metrics">${metric("データ状態", market?.mode || "unavailable", market?.freshnessLabel || "取得状況を確認")}${metric("一次調査候補", candidates.filter((candidate) => candidate.decision === "research_candidate").length, market?.marketStance || "候補なし")}${metric("監視", candidates.filter((candidate) => candidate.decision === "watch").length, "追加確認が必要")}${metric("提供方式", market?.providerMode === "market_compass_service" ? "財務連携" : "価格のみ", "注文は実行しません")}</div><div class="cc-table-wrap" style="margin-top:14px"><table class="cc-table"><thead><tr><th>銘柄</th><th>価格</th><th>変化</th><th>一次判定</th><th>根拠・次の確認</th></tr></thead><tbody>${rows || `<tr><td colspan="5">市場候補を取得できませんでした。</td></tr>`}</tbody></table></div>${missing.length ? `<div class="cc-notice"><strong>不足している根拠</strong><p>${esc(missing.join(" / "))}</p></div>` : ""}<p class="cc-disclaimer">この表示は詳しく調べる銘柄を選ぶ一次スクリーニングです。購入判断ではありません。</p>`;
  }

  async function loadMarket(targetId = "market-result") {
    const target = document.getElementById(targetId);
    if (target) target.textContent = "市場データを取得中…";
    try {
      const market = await fetchJson("/api/admin/command-center/market");
      state.market = market;
      if (target) target.innerHTML = marketMarkup(market);
    } catch (error) {
      if (target) target.innerHTML = empty(error.message);
    }
  }

  function tradePlanFormMarkup() {
    return `<form class="cc-card cc-form" id="trade-plan-form"><h3>取引プラン</h3><p class="cc-muted">スクリーニング結果とは分けて、自分の根拠と中止条件を記録します。注文は送信しません。</p><div class="cc-form-grid"><div class="cc-field"><label for="plan-market">市場</label><input class="cc-input" id="plan-market" value="JP" maxlength="40"></div><div class="cc-field"><label for="plan-symbol">銘柄</label><input class="cc-input" id="plan-symbol" required maxlength="40"></div><div class="cc-field"><label for="plan-style">取引方法</label><select class="cc-select" id="plan-style"><option value="cash">現物</option><option value="margin">信用</option></select></div><div class="cc-field"><label for="plan-direction">方向</label><select class="cc-select" id="plan-direction"><option value="long">買い</option><option value="short">売り</option></select></div><div class="cc-field cc-field--full"><label for="plan-thesis">根拠</label><textarea class="cc-textarea" id="plan-thesis" maxlength="1000" placeholder="一次情報、想定、撤退条件を記録"></textarea></div></div><button class="cc-button cc-button--primary" type="submit">プランを保存</button></form>`;
  }

  function tradePlansMarkup() {
    const plans = state.dashboard?.tradePlans || [];
    return `<ul class="cc-list" id="trade-plans-list">${plans.length ? plans.map((plan) => `<li><strong>${esc(plan.symbol)} / ${esc(plan.direction)}</strong>${badge(plan.status)}<br><small class="cc-muted">${esc(plan.thesis || "根拠未入力")}</small></li>`).join("") : `<li class="cc-muted">プランはまだありません。</li>`}</ul>`;
  }

  function tradesMarkup() {
    const trades = state.dashboard?.trades || [];
    const rows = trades.length ? trades.map((trade) => `<tr><td>${esc(trade.tradedAt)}</td><td>${esc(trade.symbol)}</td><td>${esc(trade.direction)}</td><td>${badge(trade.status, trade.status === "open" ? "warn" : "ok")}</td><td>${esc(trade.pnl)}</td></tr>`).join("") : `<tr><td colspan="5">記録はまだありません。</td></tr>`;
    return `<div class="cc-table-wrap"><table class="cc-table"><thead><tr><th>日付</th><th>銘柄</th><th>方向</th><th>状態</th><th>損益</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  function bindTradePlanForm() {
    document.getElementById("trade-plan-form")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await postData({ action: "create_trade_plan", market: document.getElementById("plan-market").value, symbol: document.getElementById("plan-symbol").value, tradeStyle: document.getElementById("plan-style").value, direction: document.getElementById("plan-direction").value, thesis: document.getElementById("plan-thesis").value });
        setLive("取引プランを保存しました。");
      } catch (error) { setLive(error.message, true); }
    });
  }

  async function renderMarket() {
    content.innerHTML = layout("市場候補", "日本株は財務一次判定を重ね、米国株は従来の価格候補として表示します。", `<div id="market-result">市場データを取得中…</div>`);
    await loadMarket();
  }

  function screenResultsMarkup(payload) {
    const results = Array.isArray(payload?.results) ? payload.results : [];
    const cards = results.map((result) => {
      const status = result.overall?.status || "insufficient_data";
      const missing = Array.isArray(result.missingEvidence) ? result.missingEvidence : [];
      return `<article class="cc-screen-result"><div><p class="cc-kicker">${esc(result.symbol)} / ${esc(result.sector || "業種未分類")}</p><h3>${esc(result.name)}</h3></div><div>${badge(decisionLabel(status), decisionTone(status))}<strong class="cc-coverage">${formatNumber(result.overall?.coverage, "%")}</strong></div><p class="cc-muted">${missing.length ? `未確認: ${esc(missing.slice(0, 4).join(" / "))}` : "主要データを取得済み"}</p><a class="cc-button" href="/admin/command-center/security?symbol=${encodeURIComponent(result.symbol)}">12項目と出典を確認</a></article>`;
    }).join("");
    const counts = payload?.counts || {};
    return `<div class="cc-grid cc-grid--metrics">${metric("一次調査候補", counts.research_candidate || 0, "重大な不合格なし")}${metric("監視", counts.watch || 0, "要確認あり")}${metric("優先度を下げる", counts.deprioritize || 0, "重大条件に不合格")}${metric("データ不足", counts.insufficient_data || 0, "充足率50％未満")}</div><div class="cc-screen-results">${cards || empty("条件に合う結果はありません。")}</div><p class="cc-disclaimer">${esc(payload?.disclaimer || "一次スクリーニングであり、購入判断ではありません。")}</p>`;
  }

  async function renderScreener() {
    content.innerHTML = layout("財務スクリーナー", "5つの基本条件と7つの安全条件で、詳しく調べる日本株を絞ります。", `<form class="cc-card cc-form" id="screen-form"><div class="cc-form-grid"><div class="cc-field cc-field--full"><label for="screen-symbols">日本株コード（空白・カンマ区切り、最大24銘柄）</label><textarea class="cc-textarea" id="screen-symbols" required>6857, 7011, 8035, 5803, 9984, 7203</textarea></div><div class="cc-field"><label for="screen-overall">結果フィルター</label><select class="cc-select" id="screen-overall"><option value="">すべて</option><option value="research_candidate">一次調査候補</option><option value="watch">監視</option><option value="deprioritize">優先度を下げる</option><option value="insufficient_data">データ不足</option></select></div><div class="cc-field cc-field--button"><button class="cc-button cc-button--primary" type="submit">スクリーニング実行</button></div></div></form><section class="cc-card"><h3>確認する12項目</h3><p class="cc-muted">一般企業の目安です。銀行・保険・不動産・REITは業種に合わせて対象外または要確認にします。</p>${checklistMarkup()}</section><div id="screen-result" class="cc-stack"><div class="cc-loading">初回スクリーニングを実行しています…</div></div><div class="cc-notice"><strong>最終確認先</strong><p>Yahoo!ファイナンス / IR BANK / 企業IR / EDINET。数値だけで決めず、最新の決算資料と会社予想を確認してください。</p></div>`);
    const runScreen = async () => {
      const target = document.getElementById("screen-result");
      const symbols = [...new Set(document.getElementById("screen-symbols").value.split(/[\s,]+/).map((item) => item.trim()).filter(Boolean))];
      if (!symbols.length || symbols.length > 24 || symbols.some((symbol) => !/^\d{4}$/.test(symbol))) { target.innerHTML = empty("4桁の日本株コードを1〜24件入力してください。"); return; }
      const overall = document.getElementById("screen-overall").value;
      target.innerHTML = `<div class="cc-loading">${esc(symbols.join(", "))} を判定しています…</div>`;
      try {
        const payload = await fetchJson("/api/admin/command-center/screen", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ symbols, ...(overall ? { filters: { overall: [overall] } } : {}) }) });
        state.screen = payload;
        target.innerHTML = screenResultsMarkup(payload);
      } catch (error) { target.innerHTML = empty(error.message); }
    };
    document.getElementById("screen-form")?.addEventListener("submit", async (event) => { event.preventDefault(); await runScreen(); });
    await runScreen();
  }

  function evidenceLinksMarkup(result) {
    const links = Array.isArray(result?.verificationLinks) ? result.verificationLinks : [];
    return links.map((item) => { const url = safeExternalUrl(item.url); return url ? `<a class="cc-source-link" href="${esc(url)}" target="_blank" rel="noreferrer">${esc(item.label)}</a>` : ""; }).join("");
  }

  function securityMarkup(payload) {
    const result = payload?.result;
    if (!result) return empty("銘柄データを取得できませんでした。");
    const status = result.overall?.status || "insufficient_data";
    const rules = Array.isArray(result.rules) ? result.rules : [];
    const periods = Array.isArray(result.financialPeriods) ? result.financialPeriods.slice(-3) : [];
    const periodRows = periods.map((period) => `<tr><td>FY${esc(period.fiscalYear)}</td><td>${formatNumber(period.revenue)}</td><td>${formatNumber(period.operatingIncome)}</td><td>${formatNumber(period.operatingCashFlow)}</td><td>${formatNumber(period.interestBearingDebt)}</td><td>${formatNumber(period.dilutedEps)}</td></tr>`).join("");
    const ruleCards = rules.map((rule, index) => `<article class="cc-rule-card"><div class="cc-rule-card__head"><span>${index + 1}</span><div><h3>${esc(rule.label)}</h3><small>${esc(rule.threshold)}</small></div>${badge(ruleStatusLabel(rule.status), ruleTone(rule.status))}</div><strong class="cc-rule-value">${esc(rule.value)}</strong><p>${esc(rule.explanation)}</p><small class="cc-muted">期間: ${esc((rule.periods || []).join(" / ") || "期間未取得")}　取得: ${esc(rule.observedAt || result.asOf)}</small></article>`).join("");
    const valuation = result.valuation || {};
    const missing = Array.isArray(result.missingEvidence) ? result.missingEvidence : [];
    return `<div class="cc-security-head"><div><p class="cc-kicker">${esc(result.symbol)} / ${esc(result.sector)} / ${esc(result.sectorProfile)}</p><h2>${esc(result.name)}</h2><p class="cc-muted">取得日時: ${esc(result.asOf)}</p></div><div>${badge(decisionLabel(status), decisionTone(status))}<strong class="cc-coverage">充足率 ${formatNumber(result.overall?.coverage, "%")}</strong></div></div><div class="cc-grid cc-grid--metrics">${metric("株価", formatNumber(result.price), result.currency || "JPY")}${metric("予想PER", formatNumber(valuation.forwardPer, "倍"), valuation.forwardPer ? "会社予想" : "未取得")}${metric("実績PER", formatNumber(valuation.trailingPer, "倍"), "過去利益ベース")}${metric("PBR", formatNumber(valuation.pbr, "倍"), "純資産ベース")}</div><section class="cc-card"><h3>直近3年度</h3><div class="cc-table-wrap"><table class="cc-table"><thead><tr><th>年度</th><th>売上高</th><th>営業利益</th><th>営業CF</th><th>有利子負債</th><th>EPS</th></tr></thead><tbody>${periodRows || `<tr><td colspan="6">3年度分のデータがありません。</td></tr>`}</tbody></table></div></section><section class="cc-card"><h3>12項目の判定</h3><div class="cc-rule-grid">${ruleCards || checklistMarkup()}</div></section><section class="cc-card"><h3>一次資料と確認先</h3><div class="cc-source-links">${evidenceLinksMarkup(result)}</div><p class="cc-muted">Yahoo!ファイナンス、IR BANK、企業IR、EDINETを見比べ、予想値・一時利益・決算期変更を確認してください。</p></section>${missing.length ? `<div class="cc-notice"><strong>不足データ・注意</strong><p>${esc(missing.join(" / "))}</p></div>` : ""}<p class="cc-disclaimer">${esc(payload.disclaimer || "一次スクリーニングであり、購入判断ではありません。")}</p>`;
  }

  async function renderSecurity() {
    const params = new URLSearchParams(window.location.search || "");
    const initial = /^\d{4}$/.test(params.get("symbol") || "") ? params.get("symbol") : "6857";
    content.innerHTML = layout("銘柄詳細", "12項目、3年推移、取得時刻、出典を一つずつ確認します。", `<form class="cc-actions" id="security-form"><label class="cc-field"><span>日本株コード</span><input class="cc-input" id="security-symbol" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" value="${esc(initial)}" required></label><button class="cc-button cc-button--primary" type="submit">銘柄を確認</button></form><div id="security-result" class="cc-stack"><div class="cc-loading">銘柄データを取得中…</div></div>`);
    const load = async () => {
      const target = document.getElementById("security-result");
      const symbol = document.getElementById("security-symbol").value.trim();
      if (!/^\d{4}$/.test(symbol)) { target.innerHTML = empty("4桁の日本株コードを入力してください。"); return; }
      target.innerHTML = `<div class="cc-loading">${esc(symbol)} を確認しています…</div>`;
      try {
        const payload = await fetchJson(`/api/admin/command-center/security?symbol=${encodeURIComponent(symbol)}`);
        state.security = payload;
        target.innerHTML = securityMarkup(payload);
        window.history?.replaceState?.({}, "", `/admin/command-center/security?symbol=${encodeURIComponent(symbol)}`);
      } catch (error) { target.innerHTML = empty(error.message); }
    };
    document.getElementById("security-form")?.addEventListener("submit", async (event) => { event.preventDefault(); await load(); });
    await load();
  }

  function renderTradePlan() {
    content.innerHTML = layout("取引プラン作成", "財務スクリーニングとは分けて、根拠と中止条件を保存します。", tradePlanFormMarkup());
    bindTradePlanForm();
  }

  function renderTradePlans() {
    content.innerHTML = layout("登録プラン", "保存済みの取引プランを一覧で確認します。注文は自動実行しません。", tradePlansMarkup());
  }

  function renderTrades() {
    content.innerHTML = layout("取引記録", "実行済みの記録と損益を振り返り、次の判断材料にします。", tradesMarkup());
  }

  async function renderMarketSources() {
    content.innerHTML = layout("データ収集状況", "取得元の役割、設定、欠損と手動確認先を明示します。", `<div id="market-sources-result"><div class="cc-loading">収集状況を確認中…</div></div>`);
    const target = document.getElementById("market-sources-result");
    try {
      const payload = await fetchJson("/api/admin/command-center/market-sources");
      state.sources = payload;
      const sources = Array.isArray(payload.sources) ? payload.sources : [];
      const cards = sources.map((source) => { const url = safeExternalUrl(source.url); const tone = ["available", "connected", "configured"].includes(source.status) ? "ok" : source.status === "error" ? "rose" : "warn"; return `<article class="cc-card cc-source-card"><div><p class="cc-kicker">${esc(source.id)}</p><h3>${esc(source.name)}</h3></div>${badge(source.status, tone)}<p>${esc(source.note)}</p>${url ? `<a class="cc-inline-link" href="${esc(url)}" target="_blank" rel="noreferrer">提供元を確認</a>` : ""}</article>`; }).join("");
      target.innerHTML = `<div class="cc-grid cc-grid--two">${cards || empty("取得元情報がありません。")}</div><div class="cc-notice"><strong>確認の順序</strong><p>企業IR・EDINET・JPX/J-Quantsを優先し、Yahoo!ファイナンスとIR BANKを照合します。未設定や欠損を合格扱いにはしません。</p></div><p class="cc-disclaimer">${esc(payload.disclaimer || "一次スクリーニングであり、購入判断ではありません。")}</p>`;
    } catch (error) { target.innerHTML = empty(error.message); }
  }

  async function renderTrade() {
    content.innerHTML = layout("相場羅針盤", "従来の統合画面を残し、市場候補・取引プラン・登録プラン・取引記録をまとめて確認します。", `<div id="market-result">市場データを取得中…</div><div class="cc-grid cc-grid--two" style="margin-top:14px">${tradePlanFormMarkup()}<div class="cc-card"><h3>登録済みプラン</h3>${tradePlansMarkup()}</div></div><div class="cc-card" style="margin-top:14px"><h3>取引記録</h3>${tradesMarkup()}</div>`);
    bindTradePlanForm();
    await loadMarket();
  }

  function setCurrentNav() { document.querySelectorAll("[data-view-link]").forEach((link) => link.classList.toggle("is-current", link.dataset.viewLink === view)); }
  async function render() {
    setCurrentNav();
    try {
      if (dashboardViews.includes(view) || ["trade-plan", "trade-plans", "trades"].includes(view)) {
        if (!state.dashboard) await loadDashboard();
      }
      if (view === "dashboard") renderDashboard();
      else if (view === "calendar") await renderCalendar();
      else if (view === "tasks") renderTasks();
      else if (view === "businesses") renderBusinesses();
      else if (view === "directives") renderDirectives();
      else if (view === "studio") await renderStudio();
      else if (view === "tools") await renderTools();
      else if (view === "trade") await renderTrade();
      else if (view === "market") await renderMarket();
      else if (view === "screener") await renderScreener();
      else if (view === "security") await renderSecurity();
      else if (view === "trade-plan") renderTradePlan();
      else if (view === "trade-plans") renderTradePlans();
      else if (view === "trades") renderTrades();
      else if (view === "market-sources") await renderMarketSources();
      document.getElementById("cc-generated-at").textContent = `更新: ${new Date().toLocaleString("ja-JP")}`;
    } catch (error) { content.innerHTML = `<div class="cc-error">${esc(error.message)}</div>`; setLive("保護データを取得できませんでした。", true); }
  }
  render();
})();
