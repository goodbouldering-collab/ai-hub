(() => {
  const menuGroups = [
    {
      id: "operations",
      label: "運営",
      summary: "予定・指示・資料",
      description: "毎日の予定と実行を整える",
      sections: [{
        items: [
          { href: "/admin/command-center", label: "実行指令室", description: "予定・指示・相場・Codexをまとめる" },
          { href: "/ops", label: "OPS", description: "資料とプロンプトを確認する" },
        ],
      }],
    },
    {
      id: "publishing",
      label: "制作・発信",
      summary: "記事・動画・SNS",
      description: "つくる・直す・届ける",
      sections: [{
        items: [
          { href: "/admin/blog", label: "ブログ管理", description: "記事を編集して公開する" },
          { href: "/admin/apps/blog", label: "ブログ制作", description: "調査から記事の下書きを作る" },
          { href: "/admin/apps/reel/", label: "リール制作", description: "動画と投稿文を作る" },
          { href: "/admin/sns-post", label: "SNS投稿", description: "複数のSNSへ投稿する" },
        ],
      }],
    },
    {
      id: "insights",
      label: "分析・相談",
      summary: "反応・改善・相談",
      description: "結果を見て次の一手を決める",
      sections: [{
        items: [
          { href: "/admin/gubble-sns", label: "SNS分析", description: "投稿の反応と改善点を見る" },
          { href: "/admin/chat", label: "AI相談", description: "運用メモや次の行動を相談する" },
        ],
      }],
    },
    {
      id: "market",
      label: "相場",
      summary: "調査・計画・記録",
      description: "相場を調べ、判断材料を残す",
      sections: [
        {
          label: "調べる",
          items: [
            { href: "/admin/command-center/trade", label: "相場羅針盤", description: "市場・プラン・記録をまとめて見る" },
            { href: "/admin/command-center/market", label: "市場候補", description: "価格と一次候補を見る" },
            { href: "/admin/command-center/screener", label: "財務スクリーナー", description: "12項目で日本株を絞る" },
            { href: "/admin/command-center/security?symbol=6857", label: "銘柄詳細", description: "3年推移と出典を見る" },
          ],
        },
        {
          label: "計画・記録",
          items: [
            { href: "/admin/command-center/trade-plan", label: "取引プラン作成", description: "根拠と中止条件を残す" },
            { href: "/admin/command-center/trade-plans", label: "登録プラン", description: "保存済みプランを見る" },
            { href: "/admin/command-center/trades", label: "取引記録", description: "実行記録と損益を見る" },
            { href: "/admin/command-center/market-sources", label: "データ収集状況", description: "取得元と欠損を確認する" },
          ],
        },
      ],
    },
    {
      id: "utility",
      label: "その他",
      summary: "確認・設定",
      description: "表示確認と管理画面の設定",
      sections: [{
        items: [
          { href: "/design-system/", label: "デザインシステム", description: "共通の色・部品・状態を確認する", kind: "reference" },
          { href: "/", label: "公開ページ", description: "公開中の表示を確認する", kind: "public" },
          { href: "/admin/logout", label: "ログアウト", description: "管理画面から退出する", kind: "logout" },
        ],
      }],
    },
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

  const menuItems = menuGroups.flatMap((group) => group.sections.flatMap((section) => section.items));
  const activeItemPath = menuItems
    .map((item) => canonicalPath(item.href))
    .filter((href) => href !== "/" && href !== "/admin/logout")
    .filter((href) => normalizedPath === href || normalizedPath.startsWith(`${href}/`))
    .sort((left, right) => right.length - left.length)[0] || null;

  function isCurrent(href) {
    return canonicalPath(href) === activeItemPath;
  }

  function isGroupCurrent(group) {
    return group.sections.some((section) => section.items.some((item) => isCurrent(item.href)));
  }

  function linkMarkup(item, mobile = false) {
    const current = isCurrent(item.href);
    const classes = [
      mobile ? "admin-shared-mobile-link" : "admin-scroll-link admin-menu-popover-link",
      current ? "is-current" : "",
      item.kind ? `admin-menu-link--${item.kind}` : "",
    ].filter(Boolean).join(" ");
    const currentAttribute = current ? ' aria-current="page"' : "";
    const kindAttribute = item.kind ? ` data-menu-kind="${item.kind}"` : "";

    if (mobile) {
      return `<a class="${classes}" href="${item.href}"${currentAttribute}${kindAttribute}><span class="mobile-link-title">${item.label}</span><small>${item.description}</small></a>`;
    }
    return `<a class="${classes}" href="${item.href}"${currentAttribute}${kindAttribute}><span class="admin-menu-link-copy"><strong>${item.label}</strong><small>${item.description}</small></span><span class="admin-menu-link-arrow" aria-hidden="true">→</span></a>`;
  }

  function sectionMarkup(section, mobile) {
    const label = section.label
      ? `<span class="admin-menu-subgroup-label">${section.label}</span>`
      : "";
    const links = section.items.map((item) => linkMarkup(item, mobile)).join("");
    return `<section class="admin-menu-subgroup">${label}<div class="${mobile ? "mobile-link-list" : "admin-menu-popover-links"}">${links}</div></section>`;
  }

  function desktopMenuMarkup() {
    return menuGroups.map((group) => {
      const current = isGroupCurrent(group);
      const classes = ["admin-menu-desktop-group", current ? "is-current-group" : ""].filter(Boolean).join(" ");
      const sections = group.sections.map((section) => sectionMarkup(section, false)).join("");
      const layout = group.sections.length > 1 ? "split" : "single";
      return `<details class="${classes}" data-menu-group="${group.id}">
        <summary class="admin-menu-group-trigger" aria-label="${group.label}メニュー、${group.summary}"><span>${group.label}</span><svg class="admin-menu-group-chevron" width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="m4 6 4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></summary>
        <div class="admin-menu-popover" data-menu-layout="${layout}" role="group" aria-label="${group.label}の項目">
          <div class="admin-menu-popover-heading"><strong>${group.label}</strong><small>${group.description}</small></div>
          <div class="admin-menu-popover-sections">${sections}</div>
        </div>
      </details>`;
    }).join("");
  }

  function mobileMenuMarkup() {
    return menuGroups.map((group) => {
      const current = isGroupCurrent(group);
      const classes = ["admin-menu-mobile-group", current ? "is-current-group" : ""].filter(Boolean).join(" ");
      const open = current ? " open" : "";
      const count = group.sections.reduce((total, section) => total + section.items.length, 0);
      const sections = group.sections.map((section) => sectionMarkup(section, true)).join("");
      return `<details class="${classes}" data-menu-group="${group.id}"${open}>
        <summary class="admin-menu-mobile-summary">
          <span class="admin-menu-mobile-copy"><strong>${group.label}</strong><small>${group.summary}</small></span>
          <span class="admin-menu-mobile-count">${count}件</span>
          <svg class="admin-menu-group-chevron" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="m4 6 4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </summary>
        <div class="admin-menu-mobile-content">${sections}</div>
      </details>`;
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
        <a class="admin-public-page-link" href="/" aria-label="AI相談の公開ページを見る">公開ページ</a>
        <button class="mobile-toggle" id="mobile-toggle" aria-label="管理メニューを開く" aria-controls="mobile-nav" aria-expanded="false" type="button">
          <span class="mobile-toggle-icon" aria-hidden="true"><span></span><span></span><span></span></span>
          <span class="mobile-toggle-text">メニュー</span>
        </button>
      </div>
      <div class="mobile-nav" id="mobile-nav" aria-hidden="true" hidden>
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
  const toggleText = toggle.querySelector?.(".mobile-toggle-text");
  const panel = header.querySelector("#mobile-nav");
  const brand = header.querySelector(".admin-shared-brand");
  const desktopGroups = [...header.querySelectorAll(".admin-menu-desktop-group")];
  const mobileGroups = [...header.querySelectorAll(".admin-menu-mobile-group")];

  function closeGroups(groups, except = null) {
    groups.forEach((group) => {
      if (group !== except) group.open = false;
    });
  }

  function keepOneGroupOpen(groups) {
    groups.forEach((group) => {
      group.addEventListener("toggle", () => {
        if (group.open) closeGroups(groups, group);
      });
    });
  }

  keepOneGroupOpen(desktopGroups);
  keepOneGroupOpen(mobileGroups);

  const drawerFocusableSelector = [
    "a[href]",
    "button:not([disabled])",
    "summary",
    "input:not([disabled])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    '[tabindex]:not([tabindex="-1"])',
  ].join(",");

  function drawerFocusables() {
    return [toggle, ...panel.querySelectorAll(drawerFocusableSelector)].filter((control) => {
      if (control === toggle) return true;
      if (control.hidden || control.getAttribute?.("aria-hidden") === "true") return false;
      return typeof control.getClientRects !== "function" || control.getClientRects().length > 0;
    });
  }

  function setMenuOpen(open, { restoreFocus = null } = {}) {
    const focusWasInDrawer = panel.contains?.(document.activeElement) === true;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "管理メニューを閉じる" : "管理メニューを開く");
    if (toggleText) toggleText.textContent = open ? "閉じる" : "メニュー";
    panel.setAttribute("aria-hidden", String(!open));
    panel.hidden = !open;
    panel.classList.toggle("open", open);
    document.body.classList.toggle("admin-shared-menu-open", open);

    const shouldRestoreFocus = !open && (restoreFocus === true || (restoreFocus === null && focusWasInDrawer));
    if (shouldRestoreFocus) toggle.focus?.();
  }

  toggle.addEventListener("click", () => {
    setMenuOpen(toggle.getAttribute("aria-expanded") !== "true");
  });

  panel.addEventListener("click", (event) => {
    if (event.target === panel) {
      setMenuOpen(false, { restoreFocus: true });
      return;
    }
    if (event.target.closest?.("a")) setMenuOpen(false, { restoreFocus: false });
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest?.(".admin-menu-desktop-group")) closeGroups(desktopGroups);
  });

  document.addEventListener("keydown", (event) => {
    const drawerIsOpen = toggle.getAttribute("aria-expanded") === "true";
    if (event.key === "Tab" && drawerIsOpen) {
      const focusables = drawerFocusables();
      const first = focusables[0];
      const last = focusables.at(-1);
      const activeIsContained = focusables.includes(document.activeElement);

      if (event.shiftKey && (document.activeElement === first || !activeIsContained)) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !activeIsContained)) {
        event.preventDefault();
        first?.focus();
      }
      return;
    }

    if (event.key !== "Escape") return;
    if (drawerIsOpen) {
      setMenuOpen(false, { restoreFocus: true });
      return;
    }
    const openGroup = desktopGroups.find((group) => group.open);
    if (openGroup) {
      openGroup.open = false;
      openGroup.querySelector("summary")?.focus();
    }
    setMenuOpen(false);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth <= 900) return;
    const menuOwnedFocus =
      toggle.getAttribute("aria-expanded") === "true" ||
      document.activeElement === toggle ||
      panel.contains?.(document.activeElement) === true;
    setMenuOpen(false, { restoreFocus: false });
    if (menuOwnedFocus) brand?.focus();
  });

  window.__AI_CONSULT_ADMIN_MENU_READY__ = true;
})();
