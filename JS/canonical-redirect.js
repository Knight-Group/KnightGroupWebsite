(function redirectLegacyHtmlPath() {
    var host = (window.location.hostname || '').toLowerCase();
    var isProductionHost = host === 'www.knightgroup.com' || host === 'knightgroup.com';

    if (!isProductionHost) {
        return;
    }

    var path = window.location.pathname || '';
    var legacyProgrammingPath = /\/Services\/programming(?:%26|&)databases(?:\.html)?$/i;

    if (legacyProgrammingPath.test(path)) {
        window.location.replace('https://knightlogics.com/service-ai-automation');
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
        window.location.replace(target);
    }
})();