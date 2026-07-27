(() => {
  const items = [
    { href: "/admin", label: "管理トップ", description: "管理ページを選ぶ", group: "管理" },
    { href: "/admin/blog", label: "ブログ管理", description: "記事の作成・編集・公開", group: "作成" },
    { href: "/admin/apps/reel/", label: "リール制作", description: "動画と投稿文を作る", group: "作成" },
    { href: "/admin/sns-post", label: "SNS投稿", description: "SNS投稿を準備する", group: "作成" },
    { href: "/admin/gubble-sns", label: "SNS分析", description: "反応と改善点を見る", group: "分析・運用" },
    { href: "/admin/chat", label: "AI相談", description: "運用メモを相談する", group: "分析・運用" },
    { href: "/ops", label: "OPS", description: "資料とプロンプトを見る", group: "分析・運用" },
    { href: "/", label: "公開ページ", description: "公開中の表示を確認する", group: "確認", kind: "public" },
    { href: "/admin/logout", label: "ログアウト", description: "管理画面から退出する", group: "確認", kind: "logout" },
  ];

  const normalizedPath = window.location.pathname.replace(/\/+$/, "") || "/";

  function isCurrent(href) {
    const normalizedHref = href.replace(/\/+$/, "") || "/";
    if (normalizedHref === "/admin") return normalizedPath === "/admin";
    if (normalizedHref === "/" || normalizedHref === "/admin/logout") return false;
    return normalizedPath === normalizedHref || normalizedPath.startsWith(`${normalizedHref}/`);
  }

  function linkMarkup(item, mobile = false) {
    const current = isCurrent(item.href);
    const classes = [
      mobile ? "admin-shared-mobile-link" : "admin-scroll-link",
      current ? "is-current" : "",
      item.kind ? `admin-menu-link--${item.kind}` : "",
    ].filter(Boolean).join(" ");
    const currentAttribute = current ? ' aria-current="page"' : "";
    const kindAttribute = item.kind ? ` data-menu-kind="${item.kind}"` : "";

    if (mobile) {
      return `<a class="${classes}" href="${item.href}"${currentAttribute}${kindAttribute}><span class="mobile-link-title">${item.label}</span><small>${item.description}</small></a>`;
    }
    return `<a class="${classes}" href="${item.href}"${currentAttribute}${kindAttribute}>${item.label}</a>`;
  }

  function desktopMenuMarkup() {
    return items.map((item) => linkMarkup(item)).join("");
  }

  function mobileMenuMarkup() {
    const groups = [...new Set(items.map((item) => item.group))];
    return groups.map((group) => {
      const links = items
        .filter((item) => item.group === group)
        .map((item) => linkMarkup(item, true))
        .join("");
      return `<section class="admin-shared-mobile-section"><span class="mobile-nav-label">${group}</span><div class="mobile-link-list">${links}</div></section>`;
    }).join("");
  }

  function headerMarkup() {
    return `
      <div class="site-header-inner">
        <a class="site-logo admin-shared-brand" href="/admin" aria-label="AI相談 管理トップへ">
          <span class="admin-shared-brand-name">AI相談</span>
          <span class="admin-shared-brand-context">管理画面</span>
        </a>
        <nav class="site-nav admin-slide-nav" aria-label="管理ページ固定メニュー">
          <div class="admin-scroll-menu">${desktopMenuMarkup()}</div>
        </nav>
        <button class="mobile-toggle" id="mobile-toggle" aria-label="管理メニューを開く" aria-controls="mobile-nav" aria-expanded="false" type="button">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>
      <div class="mobile-nav" id="mobile-nav" hidden>
        <div class="mobile-nav-panel mobile-nav-panel--admin">${mobileMenuMarkup()}</div>
      </div>`;
  }

  const existingHeader = document.querySelector("header.site-header, header.public-admin-header");
  const needsOffset = !existingHeader || existingHeader.classList.contains("public-admin-header");
  const header = existingHeader || document.createElement("header");

  if (!existingHeader) document.body.prepend(header);
  header.className = "site-header admin-shared-header";
  header.id = "site-header";
  header.innerHTML = headerMarkup();
  document.body.classList.add("admin-shared-menu-active");
  document.body.dataset.adminMenuReady = "true";
  if (needsOffset) document.body.classList.add("admin-shared-menu-offset");

  const toggle = header.querySelector("#mobile-toggle");
  const panel = header.querySelector("#mobile-nav");

  function setMenuOpen(open) {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "管理メニューを閉じる" : "管理メニューを開く");
    panel.hidden = !open;
    panel.classList.toggle("open", open);
    document.body.classList.toggle("admin-shared-menu-open", open);
  }

  toggle.addEventListener("click", () => {
    setMenuOpen(toggle.getAttribute("aria-expanded") !== "true");
  });

  panel.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenuOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenuOpen(false);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 1100) setMenuOpen(false);
  });

  window.__AI_CONSULT_ADMIN_MENU_READY__ = true;
})();
