(function initKgNavMegaMenusModule() {
  function closeDesktopBranches(menu, except) {
    if (!menu) return;
    menu.querySelectorAll(".fw-services-mega__item--branch.subnav-open").forEach(function (item) {
      if (item === except) return;
      item.classList.remove("subnav-open");
      var btn = item.querySelector(".subnav-toggle");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  }

  function closeAllDesktopDropdowns(exceptWrap) {
    document.querySelectorAll(".nav-dropdown-wrap").forEach(function (wrap) {
      if (wrap === exceptWrap) return;
      var dropdownBtn = wrap.querySelector(".nav-dropdown-btn");
      var dropdownMenu = wrap.querySelector(".nav-dropdown-menu");
      if (dropdownBtn) dropdownBtn.setAttribute("aria-expanded", "false");
      wrap.classList.remove("kg-nav-open");
      closeDesktopBranches(dropdownMenu);
    });
  }

  function bindDesktopMega(wrap) {
    if (wrap.getAttribute("data-kg-mega-bound") === "1") return;
    wrap.setAttribute("data-kg-mega-bound", "1");

    var dropdownBtn = wrap.querySelector(".nav-dropdown-btn");
    var dropdownMenu = wrap.querySelector(".nav-dropdown-menu");
    if (!dropdownBtn || !dropdownMenu) return;

    dropdownMenu.querySelectorAll(".fw-services-mega__item--branch .subnav-toggle").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var item = btn.closest(".fw-services-mega__item--branch");
        if (!item) return;
        var opening = !item.classList.contains("subnav-open");
        closeDesktopBranches(dropdownMenu, opening ? item : null);
        item.classList.toggle("subnav-open", opening);
        btn.setAttribute("aria-expanded", String(opening));
      });
    });

    dropdownBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var expanded = dropdownBtn.getAttribute("aria-expanded") === "true";
      closeAllDesktopDropdowns(expanded ? wrap : null);
      dropdownBtn.setAttribute("aria-expanded", String(!expanded));
      wrap.classList.toggle("kg-nav-open", !expanded);
      if (expanded) closeDesktopBranches(dropdownMenu);
    });

    dropdownMenu.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  }

  function bindMobileBranch(btn) {
    if (btn.getAttribute("data-kg-mm-bound") === "1") return;
    btn.setAttribute("data-kg-mm-bound", "1");

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var item = btn.closest(".fw-mm-item--branch");
      var submenu = document.getElementById(btn.getAttribute("aria-controls"));
      if (!item) return;
      var opening = !item.classList.contains("fw-mm-item--open");
      var parent = item.parentElement;
      if (parent) {
        parent.querySelectorAll(":scope > .fw-mm-item--branch.fw-mm-item--open").forEach(function (other) {
          if (other === item) return;
          other.classList.remove("fw-mm-item--open");
          var otherBtn = other.querySelector(".fw-mm-trigger");
          var otherSub = other.querySelector(".fw-mm-submenu");
          if (otherBtn) otherBtn.setAttribute("aria-expanded", "false");
          if (otherSub) otherSub.hidden = true;
        });
      }
      item.classList.toggle("fw-mm-item--open", opening);
      btn.setAttribute("aria-expanded", String(opening));
      if (submenu) submenu.hidden = !opening;
    });
  }

  function initKgNavMegaMenus() {
    document.querySelectorAll(".nav-dropdown-wrap").forEach(bindDesktopMega);
    document.querySelectorAll(".fw-mm-item--branch > .fw-mm-trigger").forEach(bindMobileBranch);
  }

  function resetMobileBranches() {
    document.querySelectorAll(".fw-mm-item--branch.fw-mm-item--open").forEach(function (item) {
      item.classList.remove("fw-mm-item--open");
      var btn = item.querySelector(".fw-mm-trigger");
      var submenu = item.querySelector(".fw-mm-submenu");
      if (btn) btn.setAttribute("aria-expanded", "false");
      if (submenu) submenu.hidden = true;
    });
  }

  if (!window.__kgNavMegaDocClickBound) {
    window.__kgNavMegaDocClickBound = true;
    document.addEventListener("click", function () {
      closeAllDesktopDropdowns();
      document.querySelectorAll(".nav-dropdown-wrap .nav-dropdown-btn").forEach(function (btn) {
        btn.setAttribute("aria-expanded", "false");
      });
      document.querySelectorAll(".nav-dropdown-wrap").forEach(function (wrap) {
        wrap.classList.remove("kg-nav-open");
      });
    });
  }

  window.kgInitNavMegaMenus = initKgNavMegaMenus;
  window.resetKgMobileSubmenus = resetMobileBranches;

  initKgNavMegaMenus();
  document.addEventListener("kg-includes-ready", initKgNavMegaMenus);
})();
