(function redirectLegacyHtmlPath() {
    var host = (window.location.hostname || '').toLowerCase();
    var isProductionHost = host === 'www.knightgroup.com' || host === 'knightgroup.com';

    if (!isProductionHost) {
        return;
    }

    var path = window.location.pathname || '';
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
        window.location.replace(target);
    }
})();