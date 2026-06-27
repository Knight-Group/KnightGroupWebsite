(function () {
  document.documentElement.classList.add('kg-js');

  var VAR_DIRECTIONS = ['left', 'right', 'top', 'bottom'];
  var scrollObserver = null;
  var marked = new WeakSet();

  function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function prepareEnter(el, direction, delayMs, immediate) {
    if (!el || marked.has(el)) return;
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
      prepareEnter(el, 'right', 100, true);
    });

    document.querySelectorAll('.kg-intent-strip__inner').forEach(function (el) {
      prepareEnter(el, 'top', 150, true);
    });

    document.querySelectorAll('.kg-map-review-shell').forEach(function (el) {
      prepareEnter(el, 'top', 0, false);
    });

    document.querySelectorAll('.kg-job-card img').forEach(function (el, index) {
      prepareEnter(el, VAR_DIRECTIONS[index % VAR_DIRECTIONS.length], index * 90, false);
    });

    document.querySelectorAll('.kg-overview-grid .kg-panel').forEach(function (el, index) {
      prepareEnter(el, index === 0 ? 'left' : 'right', index * 80, false);
    });

    document.querySelectorAll('.kg-route-grid .kg-route-card').forEach(function (el, index) {
      prepareEnter(el, VAR_DIRECTIONS[index % VAR_DIRECTIONS.length], index * 90, false);
    });

    document.querySelectorAll('.kg-services-mosaic .kg-service-card').forEach(function (el, index) {
      prepareEnter(el, VAR_DIRECTIONS[index % VAR_DIRECTIONS.length], (index % 3) * 80, false);
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
    var hero = document.querySelector('.kg-home .kg-hero');
    if (hero) {
      var restTop = getHeaderHeight() || hero.getBoundingClientRect().top;

      bindParallaxShift(hero, '--kg-hero-shift', 0.45, {
        mode: 'scroll',
        layer: '.kg-hero__bg',
        getScrollAnchor: function () {
          if (window.scrollY < 2) {
            restTop = getHeaderHeight() || hero.getBoundingClientRect().top;
          }
          return restTop;
        }
      });
    }

    bindParallaxShift(document.querySelector('.kg-route-band'), '--kg-route-shift', 0.72, {
      mode: 'scroll',
      layer: '.kg-route-band__bg'
    });
    bindParallaxShift(document.querySelector('.kg-process-band'), '--kg-process-shift', 0.72, {
      mode: 'scroll',
      layer: '.kg-process-band__bg'
    });
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

  function initEnterAnimations() {
    if (prefersReducedMotion()) {
      document.querySelectorAll('[data-kg-enter]').forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }

    applyEnterRules();
    revealImmediate();
    ensureScrollObserver();
  }

  function boot() {
    initHeaderLogoCoins();
    initEnterAnimations();
    initHeroParallax();
    initHeroForm();
    initStickyHeader();
  }

  window.kgInitEnterAnimations = initEnterAnimations;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  document.addEventListener('kg-includes-ready', function () {
    initHeaderLogoCoins();
    initEnterAnimations();
    initStickyHeader();
  });
})();
