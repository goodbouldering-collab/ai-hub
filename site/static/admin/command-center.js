(() => {
  const body = document.body;
  const view = body.dataset.view || "dashboard";
  const content = document.getElementById("cc-content");
  const live = document.getElementById("cc-live");
  const state = { dashboard: null, market: null };
  const views = ["dashboard", "calendar", "tasks", "businesses", "directives", "studio", "tools", "trade"];

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

  function renderDashboard() {
    const data = state.dashboard;
    const tasks = data.tasks || [];
    const openTasks = tasks.filter((task) => task.status !== "done").length;
    const waiting = tasks.filter((task) => task.status === "waiting").length;
    const openTrades = (data.trades || []).filter((trade) => trade.status === "open").length;
    const cards = `<div class="cc-grid cc-grid--metrics">${metric("未完了タスク", openTasks, `${waiting}件が確認待ち`)}${metric("登録事業", (data.projects || []).length, "保護された事業一覧")}${metric("実行指示", (data.directives || []).length, "最新の指示を確認")}${metric("保有記録", openTrades, "相場羅針盤の未決済")}</div>`;
    const links = views.slice(1).map((item) => `<a class="cc-card cc-link-card" href="/admin/command-center/${item}"><p class="cc-kicker">${esc(item.toUpperCase())}</p><h3>${esc({ calendar: "カレンダー", tasks: "タスク", businesses: "事業", directives: "指示", studio: "Codex連携", tools: "検証・移行", trade: "相場羅針盤" }[item])}</h3><p class="cc-muted">この領域だけを開いて確認・実行できます。</p></a>`).join("");
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

  async function renderTrade() {
    content.innerHTML = layout("相場羅針盤", "取引記録と市場データを分離表示し、注文は自動で実行しません。", `<div id="market-result">市場データを取得中…</div><div class="cc-grid cc-grid--two" style="margin-top:14px"><form class="cc-card cc-form" id="trade-plan-form"><h3>取引プラン</h3><div class="cc-form-grid"><div class="cc-field"><label for="plan-market">市場</label><input class="cc-input" id="plan-market" value="JP" maxlength="40"></div><div class="cc-field"><label for="plan-symbol">銘柄</label><input class="cc-input" id="plan-symbol" required maxlength="40"></div><div class="cc-field"><label for="plan-style">取引方法</label><select class="cc-select" id="plan-style"><option value="cash">現物</option><option value="margin">信用</option></select></div><div class="cc-field"><label for="plan-direction">方向</label><select class="cc-select" id="plan-direction"><option value="long">買い</option><option value="short">売り</option></select></div><div class="cc-field cc-field--full"><label for="plan-thesis">根拠</label><textarea class="cc-textarea" id="plan-thesis" maxlength="1000"></textarea></div></div><button class="cc-button cc-button--primary" type="submit">プランを保存</button></form><div class="cc-card"><h3>登録済みプラン</h3><ul class="cc-list" id="trade-plans-list"></ul></div></div><div class="cc-card" style="margin-top:14px"><h3>取引記録</h3><div class="cc-table-wrap"><table class="cc-table"><thead><tr><th>日付</th><th>銘柄</th><th>方向</th><th>状態</th><th>損益</th></tr></thead><tbody id="trades-body"></tbody></table></div></div>`);
    try { const market = await fetchJson("/api/admin/command-center/market"); state.market = market; const candidates = market.candidates || []; document.getElementById("market-result").innerHTML = `<div class="cc-grid cc-grid--metrics">${metric("データ状態", market.mode, market.freshnessLabel)}${metric("監視候補", candidates.filter((candidate) => candidate.decision === "buy_candidate").length, market.marketStance)}</div><div class="cc-table-wrap" style="margin-top:14px"><table class="cc-table"><thead><tr><th>銘柄</th><th>価格</th><th>変化</th><th>判定</th><th>根拠</th></tr></thead><tbody>${candidates.slice(0, 16).map((candidate) => `<tr><td><strong>${esc(candidate.name)}</strong><br><small class="cc-muted">${esc(candidate.symbol)} / ${esc(candidate.market)}</small></td><td>${esc(candidate.price)}</td><td>${esc(candidate.changePercent)}%</td><td>${badge(candidate.decision, candidate.decision === "buy_candidate" ? "ok" : candidate.decision === "avoid" ? "rose" : "warn")}</td><td>${esc(candidate.whyNow)}</td></tr>`).join("")}</tbody></table></div>`; } catch (error) { document.getElementById("market-result").innerHTML = empty(error.message); }
    const plans = state.dashboard.tradePlans || []; document.getElementById("trade-plans-list").innerHTML = plans.length ? plans.map((plan) => `<li><strong>${esc(plan.symbol)} / ${esc(plan.direction)}</strong>${badge(plan.status)}<br><small class="cc-muted">${esc(plan.thesis || "根拠未入力")}</small></li>`).join("") : `<li class="cc-muted">プランはまだありません。</li>`;
    const trades = state.dashboard.trades || []; document.getElementById("trades-body").innerHTML = trades.length ? trades.map((trade) => `<tr><td>${esc(trade.tradedAt)}</td><td>${esc(trade.symbol)}</td><td>${esc(trade.direction)}</td><td>${badge(trade.status, trade.status === "open" ? "warn" : "ok")}</td><td>${esc(trade.pnl)}</td></tr>`).join("") : `<tr><td colspan="5">記録はまだありません。</td></tr>`;
    document.getElementById("trade-plan-form")?.addEventListener("submit", async (event) => { event.preventDefault(); try { await postData({ action: "create_trade_plan", market: document.getElementById("plan-market").value, symbol: document.getElementById("plan-symbol").value, tradeStyle: document.getElementById("plan-style").value, direction: document.getElementById("plan-direction").value, thesis: document.getElementById("plan-thesis").value }); setLive("取引プランを保存しました。"); } catch (error) { setLive(error.message, true); } });
  }

  function setCurrentNav() { document.querySelectorAll("[data-view-link]").forEach((link) => link.classList.toggle("is-current", link.dataset.viewLink === view)); }
  async function render() {
    setCurrentNav();
    try { if (!state.dashboard) await loadDashboard(); if (view === "dashboard") renderDashboard(); else if (view === "calendar") await renderCalendar(); else if (view === "tasks") renderTasks(); else if (view === "businesses") renderBusinesses(); else if (view === "directives") renderDirectives(); else if (view === "studio") await renderStudio(); else if (view === "tools") await renderTools(); else if (view === "trade") await renderTrade(); document.getElementById("cc-generated-at").textContent = `更新: ${new Date().toLocaleString("ja-JP")}`; } catch (error) { content.innerHTML = `<div class="cc-error">${esc(error.message)}</div>`; setLive("保護データを取得できませんでした。", true); }
  }
  render();
})();
