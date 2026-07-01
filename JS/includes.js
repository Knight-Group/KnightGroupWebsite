// Production fallback for legacy .html URLs when the host serves both versions.
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

    var cleanPath = path.replace(/\/index\.html$/i, '/').replace(/\.html$/i, '') || '/';
    var target = cleanPath + window.location.search + window.location.hash;
    var current = path + window.location.search + window.location.hash;

    if (target !== current) {
        window.location.replace(target);
    }
})();

(function kgEarlyPartialPrefetch() {
    window.__kgPartialCache = window.__kgPartialCache || {};
    var version = '20260701-unified-includes';
    ['/header.html?v=' + version, '/footer.html?v=' + version].forEach(function (path) {
        if (window.__kgPartialCache[path]) return;
        window.__kgPartialCache[path] = fetch(path, { credentials: 'same-origin' })
            .then(function (res) { return res.ok ? res.text() : ''; })
            .catch(function () { return ''; });
    });
})();

// Dynamic HTML includes system
class HTMLInclude {
    constructor() {
        this.ensureCriticalSharedStyles();
        this.ensureHeaderStyles();
        this.ensureKgMotionAssets();
        this.ensureKgNavMegaScript();
        this.loadIncludes();
    }

    ensureHeaderStyles() {
        const headerVersion = '20260701-unified-includes';

        if (!document.getElementById('kg-header-css') && !document.querySelector('link[href*="header.min.css"]')) {
            const link = document.createElement('link');
            link.id = 'kg-header-css';
            link.rel = 'stylesheet';
            link.href = '/CSS/header.min.css?v=' + headerVersion;
            document.head.appendChild(link);
        }

        this.prefetchPartial('/header.html?v=' + headerVersion, 'kg-preload-header');
        this.prefetchPartial('/footer.html?v=' + headerVersion, 'kg-preload-footer');
    }

    prefetchPartial(url, marker) {
        if (document.querySelector(`link[data-${marker}]`)) return;
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'fetch';
        link.href = url;
        link.crossOrigin = 'anonymous';
        link.setAttribute(`data-${marker}`, '');
        document.head.appendChild(link);
    }

    ensureKgMotionAssets() {
        const motionVersion = '20260701-unified-includes';

        if (!document.getElementById('kg-redesign-css') && !document.querySelector('link[href*="kg-redesign.css"]')) {
            const link = document.createElement('link');
            link.id = 'kg-redesign-css';
            link.rel = 'stylesheet';
            link.href = '/CSS/kg-redesign.css?v=' + motionVersion;
            document.head.appendChild(link);
        }
    }

    ensureKgNavMegaScript() {
        const navVersion = '20260701-unified-includes';

        if (!document.getElementById('kg-nav-mega-js') && !document.querySelector('script[src*="kg-nav-mega.js"]')) {
            const script = document.createElement('script');
            script.id = 'kg-nav-mega-js';
            script.src = '/JS/kg-nav-mega.js?v=' + navVersion;
            script.defer = true;
            document.head.appendChild(script);
        }
    }

    ensureCriticalSharedStyles() {
        if (document.getElementById('critical-shared-button-styles')) return;

        const style = document.createElement('style');
        style.id = 'critical-shared-button-styles';
        style.textContent = `
            .btn-primary {
                background: #9a2f2f;
                background-color: #9a2f2f;
                background-image: none;
                color: #fff;
                padding: 10px 24px;
                border: 2px solid #9a2f2f;
                border-radius: 6px;
                font-weight: 600;
                text-decoration: none;
                transition: background 0.2s;
                font-size: 1rem;
                display: inline-block;
            }

            .btn-primary:hover {
                background: #6f2024;
                background-color: #6f2024;
                border-color: #6f2024;
            }

            .btn-secondary {
                background: #fff;
                background-color: #fff;
                background-image: none;
                color: #9a2f2f;
                border: 2px solid #9a2f2f;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: 600;
                text-decoration: none;
                transition: background 0.2s, color 0.2s;
                font-size: 1rem;
                display: inline-block;
            }

            .btn-secondary:hover {
                background: #9a2f2f;
                color: #fff;
            }

            button.btn-primary,
            button.btn-secondary {
                -webkit-appearance: none;
                appearance: none;
                cursor: pointer;
                font-family: inherit;
            }
        `;

        document.head.appendChild(style);
    }

    // Security: only allow same-origin relative paths (no http:// or // URLs)
    _isSafePartialPath(path) {
        return !/^(https?:)?\/\//i.test(path);
    }

    // Sanitize a DOM element tree before injecting:
    // - Removes script, iframe, object, embed, template elements
    // - Strips javascript: and data: (non-image) URLs from href/src/action
    // Note: on* event handlers are intentionally kept — header/footer are same-origin
    // static files controlled by this repo; removing onclick breaks toggleMobileMenu().
    _sanitizeElement(root) {
        const BLOCKED_TAGS = ['script', 'iframe', 'object', 'embed', 'template'];
        BLOCKED_TAGS.forEach(tag => {
            root.querySelectorAll(tag).forEach(el => el.remove());
        });
        const UNSAFE_URL_ATTRS = ['href', 'src', 'action', 'formaction'];
        root.querySelectorAll('*').forEach(el => {
            // Strip javascript: and data: (non-image) URLs only
            UNSAFE_URL_ATTRS.forEach(attrName => {
                const val = el.getAttribute(attrName);
                if (val && /^\s*(javascript:|data:(?!image\/))/i.test(val)) {
                    el.removeAttribute(attrName);
                }
            });
        });
    }

    // Fetch a partial, hoist its <link> and <style> tags to document.head,
    // sanitize the remaining content, then inject into targetElement.
    async _fetchPartialText(path) {
        if (!this._isSafePartialPath(path)) return '';

        const cache = window.__kgPartialCache;
        if (cache && cache[path]) {
            return cache[path];
        }

        const res = await fetch(path);
        if (!res.ok) return '';
        const text = await res.text();
        if (cache) cache[path] = Promise.resolve(text);
        return text;
    }

    async _fetchAndInject(targetElement, path, pathPrefix) {
        if (!this._isSafePartialPath(path)) return;
        try {
            const text = await this._fetchPartialText(path);
            if (!text) return;

            // Parse safely — DOMParser puts <link>/<style> found before body content into <head>
            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');

            // Hoist <link> tags (preconnect, preload, stylesheet) — deduplicated by href
            doc.querySelectorAll('link').forEach(link => {
                const href = link.getAttribute('href') || '';
                const existing = document.head.querySelector(`link[href="${href.replace(/"/g, '\\"')}"]`);
                if (!existing) {
                    document.head.appendChild(link.cloneNode(true));
                }
            });

            // Hoist <style> blocks — DOMParser puts them in <head> for fragment files,
            // so they would be lost if we only inject doc.body.innerHTML.
            // Use a data attribute to avoid re-hoisting on repeated loads.
            doc.querySelectorAll('style').forEach(style => {
                const id = style.textContent.trim().slice(0, 40); // fingerprint
                const alreadyHoisted = Array.from(document.head.querySelectorAll('style'))
                    .some(s => s.textContent.trim().slice(0, 40) === id);
                if (!alreadyHoisted) {
                    document.head.appendChild(style.cloneNode(true));
                }
            });

            // Remove hoisted elements so they don't duplicate in body fragment
            doc.querySelectorAll('link, style').forEach(el => el.remove());

            // Sanitize body fragment before injection
            this._sanitizeElement(doc.body);

            // Freeze element height during swap to prevent CLS.
            // When innerHTML is replaced, the element briefly collapses to 0px
            // before new content renders, causing sticky header to shift page content.
            const prevHeight = targetElement.offsetHeight;
            if (prevHeight > 0) targetElement.style.minHeight = prevHeight + 'px';

            // Inject remaining content
            targetElement.innerHTML = doc.body.innerHTML;

            // Clear the freeze — real content now defines the height
            if (prevHeight > 0) targetElement.style.minHeight = '';

            this.fixRelativePaths(targetElement);
        } catch (error) {
            console.error('Error loading partial:', path, error);
        }
    }

    moveCrawlHubBeforeFooter() {
        const crawlHub = document.querySelector('.kg-crawl-hub');
        const footerElement = document.getElementById('footer-include');

        if (!crawlHub || !footerElement || !footerElement.parentNode) {
            return;
        }

        // Homepage closing stack (and other in-page placements) control crawl hub order.
        if (crawlHub.closest('#kg-closing-stack, .kg-closing-stack, main, #main-content')) {
            return;
        }

        if (crawlHub.nextElementSibling === footerElement) {
            return;
        }

        footerElement.parentNode.insertBefore(crawlHub, footerElement);
    }

    async loadIncludes() {
        // Run-once guard — prevent double execution if constructor is called more than once
        if (window._knightGroupIncludesLoaded) return;
        window._knightGroupIncludesLoaded = true;

        const includeVersion = '20260701-unified-includes';

        const headerElement = document.getElementById('header-include');
        const footerElement = document.getElementById('footer-include');
        const includeTasks = [];

        if (headerElement) {
            includeTasks.push(this._fetchAndInject(headerElement, '/header.html?v=' + includeVersion, ''));
        }

        if (footerElement) {
            this.moveCrawlHubBeforeFooter();
            includeTasks.push(this._fetchAndInject(footerElement, '/footer.html?v=' + includeVersion, ''));
        }

        if (includeTasks.length) {
            await Promise.all(includeTasks);
        }

        this.moveCrawlHubBeforeFooter();
        this.initializeAfterIncludes();
        this.setActiveNavItem();
        if (typeof window.kgInitEnterAnimations === 'function') {
            window.kgInitEnterAnimations();
        }
        if (typeof window.kgInitNavMegaMenus === 'function') {
            window.kgInitNavMegaMenus();
        }
        if (typeof window.kgFitHeaderNav === 'function') {
            window.requestAnimationFrame(function () {
                window.kgFitHeaderNav();
                window.requestAnimationFrame(window.kgFitHeaderNav);
            });
        }
        document.dispatchEvent(new CustomEvent('kg-includes-ready'));
    }

    initializeAfterIncludes() {
        if (this._kgAfterIncludesInit) return;
        this._kgAfterIncludesInit = true;

        // ── Mobile menu toggle ────────────────────────────────────────────────
        window.toggleMobileMenu = function(forceClose) {
            const menu     = document.getElementById('mobileMenu');
            const backdrop = document.getElementById('mobileBackdrop');
            const toggle   = document.getElementById('mobileMenuToggle');
            if (!menu) return;
            const isOpen = menu.classList.contains('active');
            if (forceClose || isOpen) {
                menu.classList.remove('active');
                if (backdrop) backdrop.classList.remove('active');
                menu.setAttribute('aria-hidden', 'true');
                menu.hidden = true;
                menu.inert = true;
                if (backdrop) {
                    backdrop.hidden = true;
                    backdrop.setAttribute('aria-hidden', 'true');
                }
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
                if (typeof window.resetKgMobileSubmenus === 'function') {
                    window.resetKgMobileSubmenus();
                }
                document.body.style.overflow = '';
            } else {
                menu.hidden = false;
                menu.inert = false;
                menu.setAttribute('aria-hidden', 'false');
                if (backdrop) {
                    backdrop.hidden = false;
                    backdrop.setAttribute('aria-hidden', 'false');
                }
                menu.classList.add('active');
                if (backdrop) backdrop.classList.add('active');
                if (toggle) toggle.setAttribute('aria-expanded', 'true');
                document.body.style.overflow = 'hidden';
            }
        };

        // ── Close menu on backdrop click ──────────────────────────────────────
        const backdrop = document.getElementById('mobileBackdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => window.toggleMobileMenu(true));
        }

        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => window.toggleMobileMenu());
        }

        const mobileMenuClose = document.getElementById('mobileMenuClose');
        if (mobileMenuClose) {
            mobileMenuClose.addEventListener('click', () => window.toggleMobileMenu(true));
        }

        const mobileMenu = document.getElementById('mobileMenu');
        if (mobileMenu) {
            mobileMenu.hidden = true;
            mobileMenu.inert = true;
            mobileMenu.setAttribute('aria-hidden', 'true');
        }
        if (backdrop) {
            backdrop.hidden = true;
            backdrop.setAttribute('aria-hidden', 'true');
        }

        // ── Close menu when a nav link is tapped ─────────────────────────────
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', () => window.toggleMobileMenu(true));
        });

        // ── Close on Escape key ───────────────────────────────────────────────
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') window.toggleMobileMenu(true);
        });

        // ── Close when resized to desktop ─────────────────────────────────────
        window.addEventListener('resize', () => {
            if (window.innerWidth > 1200) window.toggleMobileMenu(true);
        });

        // ── Email picker modal ────────────────────────────────────────────────
        const TO      = 'nknight@knightgroup.com';
        const SUBJECT = encodeURIComponent('Knight Group Inquiry');
        const BODY    = encodeURIComponent('Hi, I found your website and would like to inquire about your services.');

        document.querySelectorAll('a[href^="mailto:nknight@knightgroup.com"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const m = document.getElementById('emailPickerModal');
                if (m) m.style.display = 'flex';
            });
        });

        function setHref(id, url) { const el = document.getElementById(id); if (el) el.href = url; }
        setHref('emailOptGmail',   'https://mail.google.com/mail/?view=cm&to=' + TO + '&su=' + SUBJECT + '&body=' + BODY);
        setHref('emailOptOutlook', 'https://outlook.live.com/mail/0/deeplink/compose?to=' + TO + '&subject=' + SUBJECT + '&body=' + BODY);
        setHref('emailOptYahoo',   'https://compose.mail.yahoo.com/?to=' + TO + '&subject=' + SUBJECT + '&body=' + BODY);
        setHref('emailOptDefault', 'mailto:' + TO + '?subject=' + SUBJECT + '&body=' + BODY);

        window.closeEmailModal = function() {
            const modal = document.getElementById('emailPickerModal');
            if (modal) modal.style.display = 'none';
        };

        const closeBtn = document.getElementById('emailPickerClose');
        const modal    = document.getElementById('emailPickerModal');
        if (closeBtn) closeBtn.addEventListener('click', window.closeEmailModal);
        if (modal)    modal.addEventListener('click', (e) => { if (e.target === modal) window.closeEmailModal(); });
    }

    setActiveNavItem() {
        const currentPath = window.location.pathname;
        const currentSlug = currentPath.replace(/\.html$/, '').replace(/^\//, '') || 'index';

        // Collect which links to activate (all reads first, then batch writes)
        const toActivate = [];
        const navLinks = document.querySelectorAll('nav a');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            const hrefSlug = href.replace(/\.html$/, '').replace(/^\/+/, '') || 'index';
            if (hrefSlug === currentSlug) {
                toActivate.push(link);
            }
            if (currentPath.includes('/Services/')) {
                const currentFile = currentSlug.split('/').pop();
                const hrefFile = hrefSlug.split('/').pop();
                if (hrefFile && hrefFile === currentFile) {
                    toActivate.push(link);
                }
            }
        });

        if (currentPath.includes('/Services/')) {
            const servicesLink = document.querySelector('nav a[href="services.html"], nav a[href="../services.html"], nav a[href="/services"], nav a[href="/services.html"]');
            if (servicesLink && servicesLink.textContent.trim() === 'Services') {
                toActivate.push(servicesLink);
            }
        }

        // Batch all writes via classList — avoids forced reflow from inline style churn
        toActivate.forEach(link => link.classList.add('nav-active'));
    }

    toRootSitePath(path) {
        if (!path || /^(?:https?:)?\/\//i.test(path) || /^(?:mailto:|tel:|#)/i.test(path)) {
            return path;
        }
        if (path.startsWith('/')) {
            return path;
        }
        const normalized = path.replace(/^(\.\.\/)+/, '');
        return '/' + normalized;
    }

    toRootAssetPath(path) {
        if (!path || /^(?:https?:)?\/\//i.test(path) || path.startsWith('data:')) {
            return path;
        }
        if (path.startsWith('/')) {
            return path;
        }
        const normalized = path.replace(/^(\.\.\/)+/, '');
        if (/^(Images|GalleryImages|CSS|JS)\//.test(normalized)) {
            const parts = normalized.split('?');
            return '/' + parts[0] + (parts.length > 1 ? '?' + parts.slice(1).join('?') : '');
        }
        return path;
    }

    fixRelativePaths(element) {
        const images = element.querySelectorAll('img');
        images.forEach(img => {
            const src = img.getAttribute('src');
            if (src) {
                const rootAsset = this.toRootAssetPath(src);
                if (rootAsset !== src) {
                    img.setAttribute('src', rootAsset);
                }
            }
        });

        const sources = element.querySelectorAll('source');
        sources.forEach(source => {
            const srcset = source.getAttribute('srcset');
            if (srcset) {
                const pieces = srcset.split(',').map(part => {
                    const tokens = part.trim().split(/\s+/);
                    if (!tokens.length) return part;
                    tokens[0] = this.toRootAssetPath(tokens[0]);
                    return tokens.join(' ');
                });
                const rootSrcset = pieces.join(', ');
                if (rootSrcset !== srcset) {
                    source.setAttribute('srcset', rootSrcset);
                }
            }
        });

        const links = element.querySelectorAll('a');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            const rootHref = this.toRootSitePath(href);
            if (rootHref !== href) {
                link.setAttribute('href', rootHref);
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HTMLInclude();
});

// Form submission handler with email fallback (for pages that have forms)
function handleFormSubmit(event) {
    // If Formspree is not set up (YOUR_FORM_ID still placeholder), use mailto fallback
    if (event.target.action.includes('YOUR_FORM_ID')) {
        event.preventDefault();
        
        // Collect form data
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        // Create email content
        const subject = `Service Request from ${data.name}`;
        const body = `
Name: ${data.name}
Phone: ${data.phone}
Email: ${data.email}
Service: ${data.service}
Timeline: ${data.timeline}
Address: ${data.address}

Project Description:
${data.message}
        `.trim();
        
        // Create mailto link
    const mailtoLink = `mailto:nknight@knightgroup.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        
        // Open default email client
        window.location.href = mailtoLink;
        
        // Show success message
        alert('Opening your email client to send the request. If it doesn\'t work, please call us at (813) 649-3341');
        
        return false;
    }
    
    // If Formspree is properly configured, allow normal submission
    return true;
}
