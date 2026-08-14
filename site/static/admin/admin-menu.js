(() => {
  const primaryItems = [
    { href: "/admin/command-center", label: "実行指令室", description: "予定・指示・相場・Codexをまとめて動かす" },
    { href: "/admin/blog", label: "ブログ管理", description: "記事の作成・編集・公開" },
    { href: "/admin/apps/blog", label: "ブログ制作", description: "調査から記事の下書きを作る" },
    { href: "/admin/apps/reel/", label: "リール制作", description: "動画と投稿文を作る" },
    { href: "/admin/sns-post", label: "SNS投稿", description: "SNS投稿を準備する" },
    { href: "/admin/gubble-sns", label: "SNS分析", description: "反応と改善点を見る" },
    { href: "/admin/chat", label: "AI相談", description: "運用メモを相談する" },
  ];

  const secondaryItems = [
    { href: "/ops", label: "OPS", description: "資料とプロンプトを見る", group: "運用" },
    { href: "/design-system/", label: "デザインシステム", description: "共通の色・部品・状態を確認する", group: "運用", kind: "reference" },
    { href: "/", label: "公開ページ", description: "公開中の表示を確認する", group: "サイト", kind: "public" },
    { href: "/admin/logout", label: "ログアウト", description: "管理画面から退出する", group: "アカウント", kind: "logout" },
  ];

  const marketItems = [
    { href: "/admin/command-center/trade", label: "相場羅針盤", description: "市場・プラン・記録の統合画面", group: "相場" },
    { href: "/admin/command-center/market", label: "市場候補", description: "価格と一次候補を見る", group: "相場" },
    { href: "/admin/command-center/screener", label: "財務スクリーナー", description: "12項目で日本株を絞る", group: "相場" },
    { href: "/admin/command-center/security?symbol=6857", label: "銘柄詳細", description: "3年推移と出典を見る", group: "相場" },
    { href: "/admin/command-center/trade-plan", label: "取引プラン作成", description: "根拠と中止条件を残す", group: "相場" },
    { href: "/admin/command-center/trade-plans", label: "登録プラン", description: "保存済みプランを見る", group: "相場" },
    { href: "/admin/command-center/trades", label: "取引記録", description: "実行記録と損益を見る", group: "相場" },
    { href: "/admin/command-center/market-sources", label: "データ収集状況", description: "取得元と欠損を確認する", group: "相場" },
  ];

  function canonicalPath(value) {
    const path = String(value).split(/[?#]/, 1)[0].replace(/\/+$/, "") || "/";
    const legacyPageAliases = {
      "/admin/index.html": "/admin",
      "/admin/hub.html": "/admin",
      "/admin/blog.html": "/admin/blog",
      "/admin/chat.html": "/admin/chat",
      "/admin/sns-post.html": "/admin/sns-post",
      "/admin/gubble-sns.html": "/admin/gubble-sns",
      "/admin/sns-cross-media-dashboard.html": "/admin/gubble-sns",
      "/admin/command-center.html": "/admin/command-center",
      "/ops/index.html": "/ops",
    };
    if (legacyPageAliases[path]) return legacyPageAliases[path];
    if (path === "/admin/apps/blog.html") return "/admin/apps/blog";
    if (path === "/admin/apps/reel.html") return "/admin/apps/reel";
    return path;
  }

  const normalizedPath = canonicalPath(window.location.pathname);

  const childPageLabels = {
    "/admin/command-center/calendar": ["実行指令室", "カレンダー"],
    "/admin/command-center/tasks": ["実行指令室", "タスク"],
    "/admin/command-center/businesses": ["実行指令室", "事業"],
    "/admin/command-center/directives": ["実行指令室", "指示"],
    "/admin/command-center/studio": ["実行指令室", "Codex連携"],
    "/admin/command-center/tools": ["実行指令室", "検証・移行"],
    "/admin/command-center/trade": ["実行指令室", "相場羅針盤"],
    "/admin/command-center/market": ["実行指令室", "市場候補"],
    "/admin/command-center/screener": ["実行指令室", "財務スクリーナー"],
    "/admin/command-center/security": ["実行指令室", "銘柄詳細"],
    "/admin/command-center/trade-plan": ["実行指令室", "取引プラン作成"],
    "/admin/command-center/trade-plans": ["実行指令室", "登録プラン"],
    "/admin/command-center/trades": ["実行指令室", "取引記録"],
    "/admin/command-center/market-sources": ["実行指令室", "データ収集状況"],
    "/admin/blog/status": ["ブログ管理", "接続状態"],
    "/admin/blog/settings": ["ブログ管理", "設定"],
    "/admin/blog/articles": ["ブログ管理", "記事一覧"],
    "/admin/blog/generate": ["ブログ管理", "AI記事生成"],
    "/admin/blog/editor": ["ブログ管理", "編集・画像"],
    "/admin/blog/publish": ["ブログ管理", "公開"],
    "/ops/prompts": ["OPS", "プロンプト"],
    "/ops/doc": ["OPS", "資料"],
  };

  function pageContext() {
    const exact = childPageLabels[normalizedPath];
    if (exact) return exact;
    if (normalizedPath === "/admin") return [];
    if (normalizedPath === "/admin/command-center") return ["実行指令室"];
    if (normalizedPath === "/admin/blog") return ["ブログ管理"];
    if (normalizedPath.startsWith("/admin/blog")) return ["ブログ管理", "作業ページ"];
    if (normalizedPath.startsWith("/admin/apps/blog")) return ["ブログ制作"];
    if (normalizedPath.startsWith("/admin/apps/reel")) return ["リール制作"];
    if (normalizedPath.startsWith("/admin/sns-post")) return ["SNS投稿"];
    if (normalizedPath.startsWith("/admin/gubble-sns")) return ["SNS分析"];
    if (normalizedPath.startsWith("/admin/chat")) return ["AI相談"];
    if (normalizedPath === "/ops") return ["OPS"];
    if (normalizedPath.startsWith("/ops")) return ["OPS", "作業ページ"];
    return ["管理ホーム"];
  }

  function contextMarkup() {
    const context = pageContext();
    if (!context.length) return '<div class="admin-page-context" aria-label="現在地"><strong>管理ホーム</strong></div>';
    const label = context.join(" / ");
    return `<div class="admin-page-context" aria-label="現在地"><a href="/admin" aria-label="管理ホームへ戻る">管理ホーム</a><span aria-hidden="true">/</span><strong>${label}</strong></div>`;
  }

  function isCurrent(href) {
    const normalizedHref = canonicalPath(href);
    if (normalizedPath === "/admin" && normalizedHref === "/admin/blog") return true;
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
    return primaryItems.map((item) => linkMarkup(item)).join("");
  }

  function mobileMenuMarkup() {
    const menuItems = [
      ...primaryItems.map((item) => ({ ...item, group: "管理" })),
      ...marketItems,
      ...secondaryItems,
    ];
    const groups = [...new Set(menuItems.map((item) => item.group))];
    return groups.map((group) => {
      const links = menuItems
        .filter((item) => item.group === group)
        .map((item) => linkMarkup(item, true))
        .join("");
      return `<section class="admin-shared-mobile-section"><span class="mobile-nav-label">${group}</span><div class="mobile-link-list">${links}</div></section>`;
    }).join("");
  }

  function headerMarkup() {
    return `
      <div class="site-header-inner">
        <a class="site-logo admin-shared-brand" href="/admin" aria-label="管理ホームへ戻る">
          <span class="admin-shared-brand-name">AI相談</span>
          <span class="admin-shared-brand-context">管理画面</span>
        </a>
        ${contextMarkup()}
        <nav class="site-nav admin-slide-nav" aria-label="管理ページ固定メニュー">
          <div class="admin-scroll-menu">${desktopMenuMarkup()}</div>
        </nav>
        <button class="mobile-toggle" id="mobile-toggle" aria-label="補助メニューを開く" aria-controls="mobile-nav" aria-expanded="false" type="button">
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
  document.title = "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】";
  document.body.classList.add("admin-shared-menu-active");
  document.body.dataset.adminMenuReady = "true";
  if (needsOffset) document.body.classList.add("admin-shared-menu-offset");

  const toggle = header.querySelector("#mobile-toggle");
  const panel = header.querySelector("#mobile-nav");

  function setMenuOpen(open) {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "補助メニューを閉じる" : "補助メニューを開く");
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
