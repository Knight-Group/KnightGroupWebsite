/**
 * Knight Group site analytics.
 *
 * Why this file exists:
 * 1. header.html GTM is stripped by includes.js, so city pages only count if
 *    the page itself loads tags.
 * 2. Click-gated GTM dropped idle homepage sessions (Clarity saw Contact, not Home).
 * 3. The site already pushes form_start / form_submit / form_success / phone_click
 *    to dataLayer, but GTM-MNHVDBHG has no matching triggers. This file also
 *    sends those events to GA4 G-XWB08NGJWR via gtag so estimates and calls
 *    show up without a GTM container edit.
 *
 * Do not also add a GTM GA4 Event tag for generate_lead — the page already
 * sends it. Optional GTM triggers are only needed for ads / other non-GA4 tags.
 */
(function kgAnalytics(window, document) {
    var GTM_ID = 'GTM-MNHVDBHG';
    var GA4_ID = 'G-XWB08NGJWR';
    var ATTR_KEY = 'kg:firstTouch';
    var gtmRequested = false;
    var gtagFallbackRequested = false;

    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== 'function') {
        window.gtag = function () {
            window.dataLayer.push(arguments);
        };
    }

    function pageType() {
        var path = window.location.pathname || '/';
        if (path === '/' || path === '/index.html') return 'home';
        if (path.indexOf('/Services/') === 0) return 'service';
        if (path.indexOf('/gallery/') === 0) return 'gallery';
        if (/handyman$/.test(path.replace(/\.html$/i, ''))) return 'location';
        if (path.indexOf('pricing') !== -1) return 'pricing';
        if (path.indexOf('booking') !== -1) return 'booking';
        if (path.indexOf('contact') !== -1) return 'contact';
        if (path.indexOf('thank-you') !== -1) return 'thank-you';
        return 'content';
    }

    function readSearch() {
        try {
            return new URLSearchParams(window.location.search);
        } catch (error) {
            return new URLSearchParams();
        }
    }

    function aiReferral(referrer) {
        var host = '';
        try {
            host = new URL(referrer).hostname.toLowerCase();
        } catch (error) {
            return null;
        }
        if (host.indexOf('chatgpt.com') !== -1 || host.indexOf('chat.openai.com') !== -1) {
            return { source: 'chatgpt.com', medium: 'ai_referral' };
        }
        if (host.indexOf('perplexity.ai') !== -1) return { source: 'perplexity.ai', medium: 'ai_referral' };
        if (host.indexOf('claude.ai') !== -1) return { source: 'claude.ai', medium: 'ai_referral' };
        if (host.indexOf('gemini.google.com') !== -1) return { source: 'gemini.google.com', medium: 'ai_referral' };
        if (host.indexOf('copilot.microsoft.com') !== -1) return { source: 'copilot.microsoft.com', medium: 'ai_referral' };
        return null;
    }

    function captureFirstTouch() {
        var existing = null;
        try {
            existing = JSON.parse(window.sessionStorage.getItem(ATTR_KEY) || 'null');
        } catch (error) {
            existing = null;
        }
        if (existing && existing.landing_page) return existing;

        var params = readSearch();
        var referrer = document.referrer || '';
        var ai = (!params.get('utm_source') && referrer) ? aiReferral(referrer) : null;
        var rec = {
            landing_page: window.location.pathname || '/',
            referrer: referrer,
            utm_source: params.get('utm_source') || (ai && ai.source) || '',
            utm_medium: params.get('utm_medium') || (ai && ai.medium) || '',
            utm_campaign: params.get('utm_campaign') || '',
            utm_content: params.get('utm_content') || '',
            captured_at: new Date().toISOString()
        };
        try {
            window.sessionStorage.setItem(ATTR_KEY, JSON.stringify(rec));
        } catch (error) {
            // Private mode / blocked storage — keep the in-memory record.
        }
        return rec;
    }

    function attribution() {
        var first = captureFirstTouch() || {};
        var params = readSearch();
        return {
            landing_page: first.landing_page || (window.location.pathname || '/'),
            referrer: first.referrer || document.referrer || '',
            utm_source: params.get('utm_source') || first.utm_source || '',
            utm_medium: params.get('utm_medium') || first.utm_medium || '',
            utm_campaign: params.get('utm_campaign') || first.utm_campaign || '',
            utm_content: params.get('utm_content') || first.utm_content || ''
        };
    }

    function alreadyHasGtm() {
        if (window.google_tag_manager) return true;
        return !!document.querySelector('script[src*="googletagmanager.com/gtm.js"]');
    }

    function loadGtm() {
        if (gtmRequested || alreadyHasGtm()) {
            gtmRequested = true;
            window._gtmLoaded = true;
            return;
        }
        gtmRequested = true;
        window._gtmLoaded = true;
        var script = document.createElement('script');
        script.async = true;
        script.src = 'https://www.googletagmanager.com/gtm.js?id=' + GTM_ID;
        document.head.appendChild(script);
        window.dataLayer.push({
            'gtm.start': new Date().getTime(),
            event: 'gtm.js'
        });
    }

    function loadGtagFallback() {
        if (gtagFallbackRequested) return;
        if (document.querySelector('script[src*="googletagmanager.com/gtag/js?id=' + GA4_ID + '"]')) {
            gtagFallbackRequested = true;
            return;
        }
        gtagFallbackRequested = true;
        var script = document.createElement('script');
        script.async = true;
        script.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
        script.onload = function () {
            window.gtag('js', new Date());
            window.gtag('config', GA4_ID, {
                send_page_view: !window.google_tag_manager
            });
        };
        document.head.appendChild(script);
    }

    function cleanDetails(details) {
        var out = {};
        var src = details || {};
        Object.keys(src).forEach(function (key) {
            if (/^(name|email|phone|message|description)$/i.test(key)) return;
            var value = src[key];
            if (value === undefined || value === null || value === '') return;
            out[key] = value;
        });
        return out;
    }

    function ga4Params(details) {
        var attr = attribution();
        var params = {
            send_to: GA4_ID,
            transport_type: 'beacon',
            page_path: window.location.pathname || '/',
            page_title: document.title || '',
            page_type: pageType(),
            landing_page: attr.landing_page
        };
        if (attr.referrer) params.page_referrer = attr.referrer;
        if (attr.utm_source) params.utm_source = attr.utm_source;
        if (attr.utm_medium) params.utm_medium = attr.utm_medium;
        if (attr.utm_campaign) params.utm_campaign = attr.utm_campaign;
        return Object.assign(params, cleanDetails(details));
    }

    function track(eventName, details) {
        loadGtm();
        loadGtagFallback();

        var attr = attribution();
        var payload = Object.assign({
            event: eventName,
            page_path: window.location.pathname || '/',
            page_title: document.title || '',
            page_type: pageType(),
            landing_page: attr.landing_page,
            referrer: attr.referrer,
            utm_source: attr.utm_source,
            utm_medium: attr.utm_medium,
            utm_campaign: attr.utm_campaign
        }, cleanDetails(details));
        window.dataLayer.push(payload);

        var params = ga4Params(details);
        window.gtag('event', eventName, params);

        if (eventName === 'form_success') {
            var leadParams = Object.assign({}, params, { lead_source: 'form' });
            window.dataLayer.push(Object.assign({
                event: 'generate_lead',
                page_path: payload.page_path,
                page_title: payload.page_title,
                page_type: payload.page_type,
                landing_page: payload.landing_page,
                lead_source: 'form'
            }, cleanDetails(details)));
            window.gtag('event', 'generate_lead', leadParams);
        }
    }

    function ensureAnalytics() {
        captureFirstTouch();
        loadGtm();
        loadGtagFallback();
    }

    window.kgAnalyticsTrack = track;
    window.kgEnsureAnalytics = ensureAnalytics;
    window.kgAttribution = attribution;
    if (typeof window.kgTrackLeadEvent !== 'function') {
        window.kgTrackLeadEvent = track;
    }
    ensureAnalytics();
})(window, document);
