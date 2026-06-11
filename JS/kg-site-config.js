/**
 * Public site config for Knight Group forms.
 * Turnstile: create keys at https://dash.cloudflare.com → Turnstile,
 * then paste the site key below and the secret key in Formspree form settings.
 */
window.KG_FORMS = {
  turnstileSiteKey: ''
};

/** Site-wide phone CTA — matches header `header-btn-primary kg-header-call` markup */
window.KG_PHONE = {
  tel: 'tel:+18136493341',
  display: '(813) 649-3341',
  title: 'Click to call or text (813) 649-3341',
  ariaLabel: 'Call or text (813) 649-3341'
};
