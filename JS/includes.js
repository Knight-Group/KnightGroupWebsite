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

// Dynamic HTML includes system
class HTMLInclude {
    constructor() {
        this.ensureCriticalSharedStyles();
        this.loadIncludes();
        this.initializeAfterIncludes();
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
    async _fetchAndInject(targetElement, path, pathPrefix) {
        if (!this._isSafePartialPath(path)) return;
        try {
            const res = await fetch(path);
            if (!res.ok) return;
            const text = await res.text();

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

            // Inject remaining content
            targetElement.innerHTML = doc.body.innerHTML;

            if (pathPrefix) {
                this.fixRelativePaths(targetElement, pathPrefix);
            }
        } catch (error) {
            console.error('Error loading partial:', path, error);
        }
    }

    async loadIncludes() {
        // Run-once guard — prevent double execution if constructor is called more than once
        if (window._knightGroupIncludesLoaded) return;
        window._knightGroupIncludesLoaded = true;

        const includeVersion = '20260521-red-header-footer-fix';

        // Determine if we're in a subdirectory
        const pathPrefix = window.location.pathname.includes('/Services/') || 
                          window.location.pathname.includes('/PolicyPages/') ? '../' : '';

        const headerElement = document.getElementById('header-include');
        if (headerElement) {
            await this._fetchAndInject(headerElement, pathPrefix + 'header.html?v=' + includeVersion, pathPrefix);
        }

        const footerElement = document.getElementById('footer-include');
        if (footerElement) {
            await this._fetchAndInject(footerElement, pathPrefix + 'footer.html?v=' + includeVersion, pathPrefix);
        }

        // Initialize scripts after includes are loaded
        setTimeout(() => {
            this.initializeAfterIncludes();
            this.setActiveNavItem();
        }, 100);
    }

    initializeAfterIncludes() {
        // ── Mobile menu toggle ────────────────────────────────────────────────
        window.toggleMobileMenu = function(forceClose) {
            const menu     = document.getElementById('mobileMenu');
            const backdrop = document.getElementById('mobileBackdrop');
            if (!menu) return;
            const isOpen = menu.classList.contains('active');
            if (forceClose || isOpen) {
                menu.classList.remove('active');
                if (backdrop) backdrop.classList.remove('active');
                document.body.style.overflow = '';
            } else {
                menu.classList.add('active');
                if (backdrop) backdrop.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        };

        // ── Services submenu accordion ────────────────────────────────────────
        window.toggleMmServices = function(btn) {
            const submenu  = document.getElementById('mmServicesMenu');
            if (!submenu) return;
            const expanded = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', String(!expanded));
            submenu.classList.toggle('open', !expanded);
        };

        // ── Close menu on backdrop click ──────────────────────────────────────
        const backdrop = document.getElementById('mobileBackdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => window.toggleMobileMenu(true));
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

    fixRelativePaths(element, pathPrefix) {
        const currentPath = window.location.pathname;
        const isInServices = currentPath.includes('/Services/');
        const isInPolicyPages = currentPath.includes('/PolicyPages/');
        
        // Fix all image src attributes
        const images = element.querySelectorAll('img');
        images.forEach(img => {
            const src = img.getAttribute('src');
            if (src) {
                // Handle absolute paths that need to be made relative for subdirectories
                if (src.startsWith('/') && (isInServices || isInPolicyPages)) {
                    img.setAttribute('src', '..' + src);
                }
                // Handle relative paths that need prefix
                else if (!src.startsWith('http') && !src.startsWith('../') && !src.startsWith('/')) {
                    img.setAttribute('src', pathPrefix + src);
                }
            }
        });

        // Fix <source srcset> attributes (picture elements) — same logic as img src
        const sources = element.querySelectorAll('source');
        sources.forEach(source => {
            const srcset = source.getAttribute('srcset');
            if (srcset) {
                if (srcset.startsWith('/') && (isInServices || isInPolicyPages)) {
                    source.setAttribute('srcset', '..' + srcset);
                } else if (!srcset.startsWith('http') && !srcset.startsWith('../') && !srcset.startsWith('/')) {
                    source.setAttribute('srcset', pathPrefix + srcset);
                }
            }
        });

        // Fix relative links with special handling for different navigation scenarios
        const links = element.querySelectorAll('a');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href) {
                // Handle absolute paths that need to be made relative for subdirectories  
                if (href.startsWith('/') && (isInServices || isInPolicyPages) && 
                    !href.startsWith('//') && // Don't modify protocol-relative URLs
                    !href.includes('http')) { // Don't modify full URLs
                    link.setAttribute('href', '..' + href);
                }
                // Handle Services/ links when we're in Services directory
                else if (isInServices && href.startsWith('Services/')) {
                    // Remove Services/ prefix since we're already in Services directory
                    const newHref = href.substring(9); // Remove 'Services/' 
                    link.setAttribute('href', newHref);
                }
                // Handle Services/ links from other subdirectories
                else if ((isInServices || isInPolicyPages) && href.startsWith('Services/')) {
                    // We're in a subdirectory but link goes to Services - need ../ prefix
                    link.setAttribute('href', '../' + href);
                }
                // Handle standard relative paths
                else if (!href.startsWith('http') && !href.startsWith('mailto:') && !href.startsWith('tel:') && 
                        !href.startsWith('../') && !href.startsWith('/') && !href.startsWith('#')) {
                    // Standard path fixing - add prefix for relative paths
                    link.setAttribute('href', pathPrefix + href);
                }
            }
        });

        // Fix background-image URLs in style attributes  
        const elementsWithStyle = element.querySelectorAll('[style*="background-image"]');
        elementsWithStyle.forEach(el => {
            const style = el.getAttribute('style');
            if (style) {
                let updatedStyle = style;
                
                // Handle absolute paths in background images
                if ((isInServices || isInPolicyPages)) {
                    updatedStyle = updatedStyle.replace(/url\(['"]?\/(?!\/)/g, `url('../`);
                }
                
                // Handle relative paths in background images
                updatedStyle = updatedStyle.replace(/url\(['"]?(?!http|\/|\.\.)([^'"]+)['"]?\)/g, `url('${pathPrefix}$1')`);
                
                if (updatedStyle !== style) {
                    el.setAttribute('style', updatedStyle);
                }
            }
        });

        // Fix onclick attributes that contain window.location.href with paths
        const elementsWithOnclick = element.querySelectorAll('[onclick*="window.location.href"]');
        elementsWithOnclick.forEach(el => {
            const onclick = el.getAttribute('onclick');
            if (onclick && (isInServices || isInPolicyPages)) {
                // Fix absolute paths in onclick handlers
                const updatedOnclick = onclick.replace(/window\.location\.href\s*=\s*['"`]\/(?!\/)/g, `window.location.href='../`);
                if (updatedOnclick !== onclick) {
                    el.setAttribute('onclick', updatedOnclick);
                }
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
    const mailtoLink = `mailto:nickknight488@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        
        // Open default email client
        window.location.href = mailtoLink;
        
        // Show success message
        alert('Opening your email client to send the request. If it doesn\'t work, please call us at (813) 649-3341');
        
        return false;
    }
    
    // If Formspree is properly configured, allow normal submission
    return true;
}
