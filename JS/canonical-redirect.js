(function kgBootAnalyticsFromCanonical() {
    var host = (window.location.hostname || '').toLowerCase();
    if (host !== 'www.knightgroup.com' && host !== 'knightgroup.com') return;
    if (window.kgEnsureAnalytics) {
        window.kgEnsureAnalytics();
        return;
    }
    if (document.querySelector('script[src*="kg-analytics.js"]')) return;
    var script = document.createElement('script');
    script.src = '/JS/kg-analytics.js?v=20260912-lead';
    script.async = true;
    document.head.appendChild(script);
})();

(function redirectLegacyHtmlPath() {
    var host = (window.location.hostname || '').toLowerCase();
    var isProductionHost = host === 'www.knightgroup.com' || host === 'knightgroup.com';

    if (!isProductionHost) {
        return;
    }

    function safeReplace(url) {
        try {
            var resolved = new URL(url, window.location.href);
            if (
                resolved.pathname === window.location.pathname &&
                resolved.search === window.location.search &&
                resolved.hash === window.location.hash
            ) {
                return;
            }
        } catch (e) {
            /* fall through */
        }

        window.location.replace(url);
    }

    var path = window.location.pathname || '';
    var legacyProgrammingPath = /\/Services\/programming(?:%26|&)databases(?:\.html)?$/i;

    if (legacyProgrammingPath.test(path)) {
        safeReplace('https://knightlogics.com/service-ai-automation');
        return;
    }

    var legacyFurniturePath = /\/Services\/handcraftedfurniture(?:%26|&)resins(?:\.html)?$/i;
    if (legacyFurniturePath.test(path)) {
        safeReplace('/Services/custom-projects' + window.location.search + window.location.hash);
        return;
    }

    // Hub trailing slash only — /services is the canonical hub URL
    if (path === '/services/') {
        safeReplace('/services' + window.location.search + window.location.hash);
        return;
    }

    // Capital-S /Services/ folder stub only — never match lowercase /services
    if (path === '/Services' || path === '/Services/' || /^\/Services\/index\.html$/i.test(path)) {
        safeReplace('/services' + window.location.search + window.location.hash);
        return;
    }

    var lowercaseServicesPath = path.match(/^\/services\/([^/]+)\/?$/);
    if (lowercaseServicesPath) {
        safeReplace('/Services/' + lowercaseServicesPath[1] + window.location.search + window.location.hash);
        return;
    }

    if (!/\.html$/i.test(path)) {
        return;
    }

    var cleanPath = path.replace(/\/index\.html$/i, '/').replace(/\.html$/i, '');
    if (!cleanPath) {
        cleanPath = '/';
    }

    var target = cleanPath + window.location.search + window.location.hash;
    var current = path + window.location.search + window.location.hash;

    if (target !== current) {
        safeReplace(target);
    }
})();
