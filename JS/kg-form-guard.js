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

  function bindForm(form) {
    var submitBtn = form.querySelector('[type="submit"]');

    form.addEventListener('submit', function (e) {
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
    if (siteKey && !window.turnstile) {
      window.addEventListener('load', init, { once: true });
    } else {
      init();
    }
  });
})();
