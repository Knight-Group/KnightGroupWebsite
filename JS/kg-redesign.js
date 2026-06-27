(function () {
  document.documentElement.classList.add('kg-js');

  var VAR_DIRECTIONS = ['left', 'right', 'top', 'bottom'];
  var HERO_DESKTOP_SLOTS = [
    { slot: 'left', dir: 'left' },
    { slot: 'top', dir: 'top' },
    { slot: 'bottom', dir: 'bottom' },
    { slot: 'right', dir: 'right' }
  ];
  var HERO_MOBILE_SLOTS = [
    { slot: 'left', dir: 'left' },
    { slot: 'right', dir: 'right' }
  ];
  var scrollObserver = null;
  var marked = new WeakSet();
  var heroPanelsReady = false;

  function assetUrl(path) {
    if (!path || /^(?:https?:)?\/\//i.test(path) || path.charAt(0) === '/') {
      return path;
    }
    var normalized = String(path).replace(/^(\.\.\/)+/, '');
    return '/' + normalized.replace(/^\/+/, '');
  }

  function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function shuffleArray(list) {
    var items = list.slice();
    for (var i = items.length - 1; i > 0; i -= 1) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = items[i];
      items[i] = items[j];
      items[j] = temp;
    }
    return items;
  }

  var HERO_FALLBACK_IMAGES = [
    { src: 'Images/hero-panels/fixed.webp' },
    { src: 'Images/hero-panels/after.webp' },
    { src: 'Images/hero-panels/5e07b6f70709456ca2c12b02ecc44ed9.webp' },
    { src: 'Images/hero-panels/8616534258664c79aace7cfccd4bec96.webp' }
  ];

  function heroFallbackImages() {
    return HERO_FALLBACK_IMAGES.map(function (image) {
      return { src: assetUrl(image.src) };
    });
  }

  function heroSlotConfig() {
    return window.matchMedia('(max-width: 768px)').matches
      ? HERO_MOBILE_SLOTS
      : HERO_DESKTOP_SLOTS;
  }

  function buildHeroPanel(image, slot) {
    var panel = document.createElement('div');
    panel.className = 'kg-hero-panel kg-hero-panel--photo kg-hero-panel--' + slot.slot + ' kg-hero-panel--from-' + slot.dir;

    var img = document.createElement('img');
    img.src = assetUrl(image.src);
    img.alt = '';
    img.decoding = 'async';
    img.loading = 'eager';
    img.setAttribute('role', 'presentation');
    panel.appendChild(img);

    return panel;
  }

  function markHeroPanelsReady(hero) {
    if (!hero || heroPanelsReady) return;
    heroPanelsReady = true;
    requestAnimationFrame(function () {
      hero.classList.add('kg-hero-panels-ready');
      revealImmediate();
      syncHeroColumnHeights();
    });
  }

  function renderHeroPanels(hero, images) {
    var mount = hero.querySelector('.kg-hero-panels');
    if (!mount || !images.length) return;

    var slots = heroSlotConfig();
    var pool = shuffleArray(images);
    var picks = [];

    for (var i = 0; i < slots.length; i += 1) {
      picks.push(pool[i % pool.length]);
    }

    mount.innerHTML = '';
    slots.forEach(function (slot, index) {
      mount.appendChild(buildHeroPanel(picks[index], slot));
    });

    if (prefersReducedMotion()) {
      hero.classList.add('kg-hero-panels-ready');
      revealImmediate();
      syncHeroColumnHeights();
      return;
    }

    markHeroPanelsReady(hero);
  }

  function initHeroPanels() {
    var hero = document.querySelector('.kg-home .kg-hero[data-hero-panels]');
    if (!hero || hero.dataset.heroPanelsInit) return;
    hero.dataset.heroPanelsInit = '1';

    renderHeroPanels(hero, heroFallbackImages());

    fetch(assetUrl('Images/hero-panels/manifest.json'))
      .then(function (response) {
        if (!response.ok) throw new Error('hero manifest load failed');
        return response.json();
      })
      .then(function (data) {
        var images = (data.images || []).map(function (image) {
          return Object.assign({}, image, { src: assetUrl(image.src) });
        });
        if (images.length) {
          renderHeroPanels(hero, images);
        }
        fitHeroPills();
        syncHeroColumnHeights();
      })
      .catch(function () {
        fitHeroPills();
        syncHeroColumnHeights();
      });
  }

  function prepareEnter(el, direction, delayMs, immediate) {
    if (!el || marked.has(el) || el.getAttribute('data-kg-static') === 'true') return;
    marked.add(el);
    el.setAttribute('data-kg-enter', direction);
    el.style.setProperty('--kg-enter-delay', (delayMs || 0) + 'ms');
    if (immediate) {
      el.setAttribute('data-kg-enter-immediate', 'true');
    }
  }

  function findLeadAfterH1(h1) {
    if (!h1 || !h1.parentElement) return null;
    var scoped = h1.parentElement.querySelector('.kg-hero__lead, .kg-page-hero__lead, .subtitle');
    if (scoped && scoped !== h1) return scoped;
    var sibling = h1.nextElementSibling;
    while (sibling) {
      if (sibling.matches && sibling.matches('p, .kg-hero__lead, .kg-page-hero__lead, .subtitle')) {
        return sibling;
      }
      if (sibling.matches && sibling.matches('div, section, article, form, ul, ol')) {
        break;
      }
      sibling = sibling.nextElementSibling;
    }
    return null;
  }

  function applyEnterRules() {
    document.querySelectorAll('main h1, #main-content h1').forEach(function (h1) {
      prepareEnter(h1, 'left', 0, true);
      var lead = findLeadAfterH1(h1);
      if (lead) {
        prepareEnter(lead, 'left', 80, true);
      }
    });

    document.querySelectorAll('.kg-eyebrow').forEach(function (el) {
      prepareEnter(el, 'left', 0, true);
    });

    document.querySelectorAll('.kg-hero-form-card').forEach(function (el) {
      prepareEnter(el, 'right', 60, true);
    });

    document.querySelectorAll('.header-btn-primary').forEach(function (el) {
      if (el.closest('.kg-hero-form-phone-row') || el.closest('#header-include')) return;
      prepareEnter(el, 'right', 100, true);
    });

    document.querySelectorAll('.kg-intent-strip__inner').forEach(function (el) {
      prepareEnter(el, 'top', 150, true);
    });

    document.querySelectorAll('.kg-map-review-shell').forEach(function (el) {
      prepareEnter(el, 'top', 0, false);
    });

    // Carousel slides are translated off-screen; scroll enter animations break image paint/load.

    document.querySelectorAll('.kg-overview-grid .kg-panel').forEach(function (el, index) {
      prepareEnter(el, index === 0 ? 'left' : 'right', index * 80, false);
    });

    document.querySelectorAll('.kg-route-grid .kg-route-card').forEach(function (el, index) {
      prepareEnter(el, VAR_DIRECTIONS[index % VAR_DIRECTIONS.length], index * 90, false);
    });

    document.querySelectorAll('.kg-services-mosaic .kg-service-card').forEach(function (el) {
      el.setAttribute('data-kg-static', 'true');
    });

    document.querySelectorAll('.kg-page-hero__cutout-wrap[data-kg-enter]').forEach(function (el) {
      prepareEnter(el, 'right', 0, true);
    });

    document.querySelectorAll(
      '.kg-service-stack .kg-service-prose[data-kg-enter], .kg-service-stack .kg-service-sidebar[data-kg-enter], .kg-service-stack .kg-service-cta__actions[data-kg-enter]'
    ).forEach(function (el) {
      el.setAttribute('data-kg-enter-immediate', 'true');
    });
  }

  function revealImmediate() {
    document.querySelectorAll('[data-kg-enter-immediate="true"]').forEach(function (el) {
      el.style.setProperty('--kg-enter-delay', '0ms');
      el.classList.add('is-visible');
    });
  }

  function ensureScrollObserver() {
    if (prefersReducedMotion()) return;

    if (!scrollObserver) {
      scrollObserver = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    }

    document.querySelectorAll('[data-kg-enter]:not([data-kg-enter-immediate]):not(.is-visible)').forEach(function (el) {
      scrollObserver.observe(el);
    });
  }

  function bindParallaxShift(target, cssVar, intensity, options) {
    if (!target || prefersReducedMotion()) return;

    options = options || {};
    var mode = options.mode || 'viewport';
    var layer = options.layer ? target.querySelector(options.layer) : target;
    var subject = layer || target;
    var ticking = false;

    function update() {
      ticking = false;
      var rect = target.getBoundingClientRect();
      var shift;

      if (mode === 'scroll') {
        var anchor = 0;
        if (typeof options.getScrollAnchor === 'function') {
          anchor = options.getScrollAnchor();
        } else if (options.scrollAnchor != null) {
          anchor = options.scrollAnchor;
        }
        shift = -(rect.top - anchor) * intensity;
      } else {
        var progress = Math.max(-1, Math.min(1, rect.top / Math.max(window.innerHeight, 1)));
        shift = progress * intensity;
      }

      subject.style.setProperty(cssVar, Math.round(shift) + 'px');
    }

    function queue() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }

    update();
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', queue, { passive: true });
  }

  function getHeaderHeight() {
    var header = document.querySelector('#header-include > header');
    return header ? header.getBoundingClientRect().height : 0;
  }

  function initHeroParallax() {
    if (window.matchMedia('(max-width: 900px)').matches) return;

    var hero = document.querySelector('.kg-home .kg-hero');
    if (hero) {
      var restTop = getHeaderHeight() || hero.getBoundingClientRect().top;

      bindParallaxShift(hero, '--kg-hero-shift', 0.45, {
        mode: 'scroll',
        layer: '.kg-hero-panels',
        getScrollAnchor: function () {
          if (window.scrollY < 2) {
            restTop = getHeaderHeight() || hero.getBoundingClientRect().top;
          }
          return restTop;
        }
      });

      bindParallaxShift(hero, '--kg-hero-shift', 0.45, {
        mode: 'scroll',
        layer: '.kg-hero-cutout-wrap',
        getScrollAnchor: function () {
          if (window.scrollY < 2) {
            restTop = getHeaderHeight() || hero.getBoundingClientRect().top;
          }
          return restTop;
        }
      });
    }

    bindParallaxShift(document.querySelector('.kg-process-band'), '--kg-process-shift', 0.72, {
      mode: 'scroll',
      layer: '.kg-process-band__bg'
    });
  }

  function fitHeroPills() {
    var pills = document.querySelector('.kg-home .kg-hero-pills');
    if (!pills || window.matchMedia('(max-width: 900px)').matches) {
      if (pills) pills.style.removeProperty('--kg-hero-pill-size');
      return;
    }

    pills.style.setProperty('--kg-hero-pill-size', '0.82rem');
    var size = 13.12;
    var minSize = 10.4;

    while (pills.scrollWidth > pills.clientWidth && size > minSize) {
      size -= 0.4;
      pills.style.setProperty('--kg-hero-pill-size', (size / 16) + 'rem');
    }
  }

  function syncMobileHeroCutoutPlacement() {
    var hero = document.querySelector('.kg-home .kg-hero[data-hero-panels]');
    var cutout = document.querySelector('.kg-home .kg-hero-cutout-wrap');
    var copy = document.querySelector('.kg-home .kg-hero-copy');
    var proof = document.querySelector('.kg-home .kg-hero-proof-aside');
    if (!hero || !cutout || !copy) return;

    var mobile = window.matchMedia('(max-width: 900px)').matches;

    if (mobile) {
      if (proof) {
        if (cutout.parentElement !== copy || cutout.previousElementSibling !== proof) {
          proof.insertAdjacentElement('afterend', cutout);
        }
      } else if (cutout.parentElement !== copy) {
        copy.appendChild(cutout);
      }

      cutout.classList.add('kg-hero-cutout-wrap--mobile-flow');
      cutout.style.removeProperty('top');
      cutout.style.removeProperty('right');
      cutout.style.removeProperty('left');
      cutout.style.removeProperty('bottom');
      return;
    }

    cutout.classList.remove('kg-hero-cutout-wrap--mobile-flow');
    cutout.style.removeProperty('top');
    cutout.style.removeProperty('right');
    cutout.style.removeProperty('left');
    cutout.style.removeProperty('bottom');

    if (cutout.parentElement === copy) {
      var overlay = hero.querySelector('.kg-hero__overlay');
      if (overlay) {
        hero.insertBefore(cutout, overlay);
      } else {
        hero.appendChild(cutout);
      }
    }
  }

  function syncHeroColumnHeights() {
    var copy = document.querySelector('.kg-home .kg-hero-copy');
    var shell = document.querySelector('.kg-home .kg-hero-form-shell');
    var card = document.querySelector('.kg-home .kg-hero-form-card');
    var panels = document.querySelector('.kg-home .kg-hero-panels');
    var overlay = document.querySelector('.kg-home .kg-hero__overlay');
    var cutoutWrap = document.querySelector('.kg-home .kg-hero-cutout-wrap');
    if (!copy || !shell) return;

    if (window.matchMedia('(max-width: 900px)').matches) {
      syncMobileHeroCutoutPlacement();

      shell.style.removeProperty('height');
      if (card) {
        card.style.removeProperty('--kg-hero-textarea-min');
        card.style.removeProperty('--kg-hero-textarea-max');
      }

      var stageHeight = Math.ceil(copy.getBoundingClientRect().height);
      if (panels && stageHeight > 0) {
        panels.style.setProperty('height', stageHeight + 'px', 'important');
        panels.style.setProperty('bottom', 'auto', 'important');
      }
      if (overlay && stageHeight > 0) {
        overlay.style.setProperty('height', stageHeight + 'px', 'important');
        overlay.style.setProperty('bottom', 'auto', 'important');
      }
      return;
    }

    syncMobileHeroCutoutPlacement();

    if (cutoutWrap) {
      cutoutWrap.style.removeProperty('top');
      cutoutWrap.style.removeProperty('bottom');
      cutoutWrap.style.removeProperty('left');
      cutoutWrap.style.removeProperty('right');
    }

    if (panels) {
      panels.style.removeProperty('height');
      panels.style.removeProperty('bottom');
    }
    if (overlay) {
      overlay.style.removeProperty('height');
      overlay.style.removeProperty('bottom');
    }

    shell.style.removeProperty('height');
    if (card) {
      card.style.removeProperty('--kg-hero-textarea-min');
      card.style.removeProperty('--kg-hero-textarea-max');
    }

    var copyHeight = Math.ceil(copy.getBoundingClientRect().height);
    var naturalShell = Math.ceil(shell.scrollHeight);
    var target = Math.max(copyHeight, naturalShell);

    if (target > 0) {
      shell.style.setProperty('height', target + 'px', 'important');
    }

    fitHeroFormToColumn();
  }

  function fitHeroFormToColumn() {
    var card = document.querySelector('.kg-home .kg-hero-form-card');
    var textarea = document.getElementById('hero-message');
    if (!card || !textarea) return;
    if (window.matchMedia('(max-width: 900px)').matches) return;

    var mins = [56, 48, 44, 40, 36, 32];
    var i;

    card.style.removeProperty('--kg-hero-textarea-min');
    card.style.removeProperty('--kg-hero-textarea-max');

    if (card.scrollHeight <= card.clientHeight + 1) return;

    for (i = 0; i < mins.length; i += 1) {
      card.style.setProperty('--kg-hero-textarea-min', mins[i] + 'px');
      card.style.setProperty('--kg-hero-textarea-max', Math.max(mins[i] + 16, 64) + 'px');
      if (card.scrollHeight <= card.clientHeight + 1) return;
    }
  }

  function initHeroColumnHeightSync() {
    var copy = document.querySelector('.kg-home .kg-hero-copy');
    if (!copy) return;

    var queueSync = function () {
      requestAnimationFrame(function () {
        syncMobileHeroCutoutPlacement();
        fitHeroPills();
        syncHeroColumnHeights();
      });
    };

    queueSync();

    if (typeof ResizeObserver !== 'undefined') {
      var observer = new ResizeObserver(queueSync);
      observer.observe(copy);
    }

    window.addEventListener('resize', queueSync, { passive: true });
    window.addEventListener('load', queueSync, { passive: true });
    document.fonts.ready.then(queueSync).catch(function () {});
    setTimeout(queueSync, 450);
  }

  function initHeroForm() {
    var form = document.getElementById('heroEstimateForm');
    if (!form) return;
    form.addEventListener('submit', function () {
      var submit = form.querySelector('.kg-hero-form-submit');
      if (!submit) return;
      var label = submit.querySelector('span');
      if (label) label.textContent = 'Sending...';
      submit.disabled = true;
    });
  }

  function initServiceMosaicImages() {
    var cards = document.querySelectorAll('.kg-services-mosaic .kg-service-card__bg');
    if (!cards.length) return;

    if (!('IntersectionObserver' in window)) return;

    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var img = entry.target;
        if (img.dataset.kgLoaded === 'true') return;
        img.dataset.kgLoaded = 'true';
        obs.unobserve(img);
      });
    }, { rootMargin: '480px 0px', threshold: 0.01 });

    cards.forEach(function (img, index) {
      if (index < 2) {
        img.loading = 'eager';
        img.fetchPriority = 'high';
      } else {
        img.loading = 'lazy';
      }
      observer.observe(img);
    });
  }

  function initHeaderLogoCoins() {
    document.querySelectorAll('.logo-home-link picture, .mm-logo picture, .footer-logo picture').forEach(function (picture) {
      if (!picture || picture.closest('.kg-logo-coin')) return;

      var sizeClass = 'kg-logo-coin--header';
      if (picture.closest('.mm-logo')) sizeClass = 'kg-logo-coin--menu';
      if (picture.closest('.footer-logo')) sizeClass = 'kg-logo-coin--footer';

      var coin = document.createElement('div');
      coin.className = 'kg-logo-coin ' + sizeClass;
      coin.setAttribute('aria-hidden', 'true');

      var scene = document.createElement('div');
      scene.className = 'kg-logo-coin__scene';
      var spinner = document.createElement('div');
      spinner.className = 'kg-logo-coin__spinner';

      ['front', 'back'].forEach(function (side) {
        var face = document.createElement('div');
        face.className = 'kg-logo-coin__face kg-logo-coin__face--' + side;
        var clone = picture.cloneNode(true);
        var cloneImg = clone.querySelector('img');
        if (cloneImg) cloneImg.alt = '';
        face.appendChild(clone);
        spinner.appendChild(face);
      });

      scene.appendChild(spinner);
      coin.appendChild(scene);
      picture.replaceWith(coin);
    });
  }

  function initStickyHeader() {
    var header = document.querySelector('#header-include > header');
    if (!header) return;

    function updateHeaderScrollState() {
      header.classList.toggle('kg-header-scrolled', window.scrollY > 12);
    }

    updateHeaderScrollState();
    window.addEventListener('scroll', updateHeaderScrollState, { passive: true });
  }

  var headerNavFitBound = false;

  function fitHeaderNav() {
    var navList = document.querySelector('#header-include .nav-section > nav > ul');
    var logo = document.querySelector('#header-include .logo-section');
    var actions = document.querySelector('#header-include .header-actions');
    if (!navList || !logo || !actions) return;

    if (window.matchMedia('(max-width: 1200px)').matches) {
      navList.style.removeProperty('--kg-header-nav-size');
      navList.style.removeProperty('--kg-header-nav-gap');
      navList.style.removeProperty('max-width');
      return;
    }

    var sizes = [12.48, 11.84, 11.2, 10.56, 9.92, 9.28, 8.64, 8.0, 7.36, 6.72];
    var gaps = [18, 14, 11, 8, 6, 4, 2];
    var available = actions.getBoundingClientRect().left - logo.getBoundingClientRect().right - 12;
    var i;
    var j;

    navList.style.maxWidth = Math.max(120, Math.floor(available)) + 'px';
    navList.style.setProperty('--kg-header-nav-size', '0.78rem');
    navList.style.setProperty('--kg-header-nav-gap', '18px');

    for (i = 0; i < gaps.length; i += 1) {
      navList.style.setProperty('--kg-header-nav-gap', gaps[i] + 'px');
      for (j = 0; j < sizes.length; j += 1) {
        navList.style.setProperty('--kg-header-nav-size', (sizes[j] / 16) + 'rem');
        if (navList.scrollWidth <= navList.clientWidth + 1) return;
      }
    }

    navList.style.setProperty('--kg-header-nav-size', (sizes[sizes.length - 1] / 16) + 'rem');
    navList.style.setProperty('--kg-header-nav-gap', gaps[gaps.length - 1] + 'px');
  }

  function initHeaderNavFit() {
    var queue = function () {
      requestAnimationFrame(fitHeaderNav);
    };

    fitHeaderNav();
    if (headerNavFitBound) return;
    headerNavFitBound = true;
    window.addEventListener('resize', queue, { passive: true });
    window.addEventListener('load', queue, { passive: true });
    document.fonts.ready.then(queue).catch(function () {});
    setTimeout(queue, 450);
  }

  function initEnterAnimations() {
    if (prefersReducedMotion()) {
      document.querySelectorAll('[data-kg-enter]').forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }

    applyEnterRules();

    if (!document.querySelector('.kg-home .kg-hero[data-hero-panels]')) {
      revealImmediate();
    } else if (heroPanelsReady) {
      revealImmediate();
    }

    ensureScrollObserver();
  }

  function boot() {
    initHeaderLogoCoins();
    initHeroPanels();
    initEnterAnimations();
    initServiceMosaicImages();
    initHeroParallax();
    initHeroForm();
    initStickyHeader();
    initHeaderNavFit();
    initHeroColumnHeightSync();
  }

  window.kgInitEnterAnimations = initEnterAnimations;
  window.kgFitHeaderNav = fitHeaderNav;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  document.addEventListener('kg-includes-ready', function () {
    initHeaderLogoCoins();
    initHeroPanels();
    initEnterAnimations();
    initServiceMosaicImages();
    initStickyHeader();
    fitHeaderNav();
    if (typeof window.kgInitNavMegaMenus === 'function') {
      window.kgInitNavMegaMenus();
    }
    initHeroColumnHeightSync();
  });
})();
