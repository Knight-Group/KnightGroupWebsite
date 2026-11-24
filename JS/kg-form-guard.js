(function () {
  var cfg = window.KG_FORMS || {};
  var siteKey = (cfg.turnstileSiteKey || '').trim();

  function markVerified() {
    document.querySelectorAll('.kg-turnstile').forEach(function (el) {
      el.dataset.kgVerified = '1';
    });
    document.querySelectorAll('form[data-kg-guard] [type="submit"]').forEach(function (btn) {
      btn.disabled = false;
      btn.removeAttribute('aria-disabled');
    });
  }

  window.kgTurnstileSuccess = markVerified;

  function honeypotTripped(form) {
    var hp = form.querySelector('[name="address_2"]');
    return !!(hp && hp.value);
  }

  function turnstileReady(form) {
    if (!siteKey) return true;
    var widget = form.querySelector('.kg-turnstile');
    return widget && widget.dataset.kgVerified === '1';
  }

  var ATTR_KEYS = [
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_term',
    'utm_content',
    'source',
    'thread_id',
    'service',
    'gclid',
    'fbclid'
  ];

  function captureAttribution() {
    try {
      var params = new URLSearchParams(window.location.search || '');
      var stored = {};
      var firstTouch = {};
      try {
        stored = JSON.parse(window.sessionStorage.getItem('kg_attr') || '{}') || {};
      } catch (e) {
        stored = {};
      }
      try {
        firstTouch = JSON.parse(window.sessionStorage.getItem('kg:firstTouch') || '{}') || {};
      } catch (e) {
        firstTouch = {};
      }
      var changed = false;
      ATTR_KEYS.forEach(function (k) {
        var v = params.get(k) || stored[k] || firstTouch[k];
        if (v) {
          var clean = String(v).trim().slice(0, 120);
          if (stored[k] !== clean) {
            stored[k] = clean;
            changed = true;
          }
        }
      });
      var lp = stored.landing_page || firstTouch.landing_page || (window.location && window.location.pathname) || '';
      if (lp && stored.landing_page !== String(lp).slice(0, 120)) {
        stored.landing_page = String(lp).slice(0, 120);
        changed = true;
      }
      var ref = stored.initial_referrer || firstTouch.referrer || document.referrer || '';
      if (!stored.initial_referrer && ref) {
        try {
          var refHost = new URL(ref).hostname.toLowerCase();
          var curHost = (window.location.hostname || '').toLowerCase();
          if (refHost && refHost !== curHost) {
            stored.initial_referrer = String(ref).slice(0, 200);
            changed = true;
          }
        } catch (e) {}
      }
      if (changed) {
        window.sessionStorage.setItem('kg_attr', JSON.stringify(stored));
      }
      return stored;
    } catch (e) {
      return {};
    }
  }

  function attachAttribution(form, data) {
    if (!form || !data) return;
    Object.keys(data).forEach(function (k) {
      var val = data[k];
      if (!val) return;
      var fieldName = k;
      if (form.querySelector('[name="' + k + '"]')) {
        if (k === 'service' && !form.querySelector('[name="attr_service"]')) {
          fieldName = 'attr_service';
        } else {
          return;
        }
      }
      var inp = document.createElement('input');
      inp.type = 'hidden';
      inp.name = fieldName;
      inp.value = val;
      form.appendChild(inp);
    });
  }

  function bindForm(form) {
    attachAttribution(form, captureAttribution());
    var submitBtn = form.querySelector('[type="submit"]');

    form.addEventListener('submit', function (e) {
      if (typeof window.kgPrepareEstimatePhotos === 'function' && !window.kgPrepareEstimatePhotos(form)) {
        e.preventDefault();
        return;
      }
      if (honeypotTripped(form) || !turnstileReady(form)) {
        e.preventDefault();
        return;
      }
      if (!submitBtn) return;
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-disabled', 'true');
      var sending = submitBtn.getAttribute('data-kg-sending') || 'Sending…';
      if (submitBtn.tagName === 'BUTTON') {
        submitBtn.textContent = sending;
      } else {
        submitBtn.value = sending;
      }
    });
  }

  function renderTurnstile() {
    if (!siteKey || !window.turnstile) return;
    document.querySelectorAll('.kg-turnstile').forEach(function (el) {
      if (el.dataset.kgRendered === '1') return;
      el.dataset.kgRendered = '1';
      window.turnstile.render(el, {
        sitekey: siteKey,
        theme: el.getAttribute('data-theme') || 'light',
        size: el.getAttribute('data-size') || 'flexible',
        callback: 'kgTurnstileSuccess'
      });
    });
  }

  function init() {
    document.querySelectorAll('form[data-kg-guard]').forEach(function (form) {
      bindForm(form);
      if (siteKey) {
        var btn = form.querySelector('[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.setAttribute('aria-disabled', 'true');
        }
      }
    });

    if (siteKey) {
      renderTurnstile();
    } else {
      document.querySelectorAll('.kg-turnstile').forEach(function (el) {
        el.hidden = true;
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    captureAttribution();
    if (siteKey && !window.turnstile) {
      window.addEventListener('load', init, { once: true });
    } else {
      init();
    }
  });
})();
