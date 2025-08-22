// Dynamic HTML includes system
class HTMLInclude {
    constructor() {
        this.loadIncludes();
        this.initializeAfterIncludes();
    }

    async loadIncludes() {
        // Determine if we're in a subdirectory
        const pathPrefix = window.location.pathname.includes('/Services/') || 
                          window.location.pathname.includes('/PolicyPages/') ? '../' : '';

        // Load header
        const headerElement = document.getElementById('header-include');
        if (headerElement) {
            try {
                const headerResponse = await fetch(pathPrefix + 'header.html');
                if (headerResponse.ok) {
                    headerElement.innerHTML = await headerResponse.text();
                    
                    // Fix paths in header for subdirectory pages
                    if (pathPrefix) {
                        this.fixRelativePaths(headerElement, pathPrefix);
                    }
                }
            } catch (error) {
                console.error('Error loading header:', error);
            }
        }

        // Load footer
        const footerElement = document.getElementById('footer-include');
        if (footerElement) {
            try {
                const footerResponse = await fetch(pathPrefix + 'footer.html');
                if (footerResponse.ok) {
                    footerElement.innerHTML = await footerResponse.text();
                    
                    // Fix paths in footer for subdirectory pages
                    if (pathPrefix) {
                        this.fixRelativePaths(footerElement, pathPrefix);
                    }
                }
            } catch (error) {
                console.error('Error loading footer:', error);
            }
        }

        // Initialize scripts after includes are loaded
        setTimeout(() => {
            this.initializeAfterIncludes();
            this.setActiveNavItem();
        }, 100);
    }

    initializeAfterIncludes() {
        // Mobile menu functionality
        window.toggleMobileMenu = function() {
            const mobileMenu = document.getElementById('mobileMenu');
            if (mobileMenu) {
                mobileMenu.classList.toggle('active');
            }
        };

        // Close mobile menu when clicking on a link
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', () => {
                const mobileMenu = document.getElementById('mobileMenu');
                if (mobileMenu) {
                    mobileMenu.classList.remove('active');
                }
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            const mobileMenu = document.getElementById('mobileMenu');
            const hamburger = document.querySelector('.hamburger');
            
            if (mobileMenu && hamburger && !mobileMenu.contains(e.target) && !hamburger.contains(e.target)) {
                mobileMenu.classList.remove('active');
            }
        });

        // Theme Toggle functionality
        const themeToggle = document.getElementById('theme-toggle');
        const themeDisplay = document.getElementById('theme-display');
        if (themeToggle && themeDisplay) {
            // Load saved theme
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                themeDisplay.textContent = '🌙 Dark';
            } else {
                themeDisplay.textContent = '☀️ Light';
            }

            // Add click event listener
            themeToggle.addEventListener('click', () => {
                document.body.classList.toggle('dark-mode');
                
                if (document.body.classList.contains('dark-mode')) {
                    themeDisplay.textContent = '🌙 Dark';
                    localStorage.setItem('theme', 'dark');
                } else {
                    themeDisplay.textContent = '☀️ Light';
                    localStorage.setItem('theme', 'light');
                }
            });
        }
    }

    setActiveNavItem() {
        // Get current page filename and path
        const currentPath = window.location.pathname;
        const currentPage = currentPath.split('/').pop() || 'index.html';
        
        // Map page names to navigation items
        const pageMap = {
            'index.html': 'index.html',
            'about.html': 'about.html', 
            'pricing.html': 'pricing.html',
            'contact.html': 'contact.html',
            'galleries.html': 'galleries.html'
        };

        // Find and highlight the active navigation item
        const navLinks = document.querySelectorAll('nav a');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href) {
                // Handle main page links
                if (href === currentPage || href === pageMap[currentPage]) {
                    link.style.background = '#800000';
                    link.style.color = '#fff';
                }
                // Handle service page links - check if current page matches the service
                if (currentPath.includes('/Services/') && href.includes(currentPage)) {
                    link.style.background = '#800000';
                    link.style.color = '#fff';
                }
            }
        });

        // Handle services pages - highlight Services dropdown if on any service page
        if (currentPath.includes('/Services/') || 
            ['handyman.html', 'general-repairs.html', 'plumbing-services.html', 'electrical-work.html', 
             'carpentry-framing.html', 'painting-finishing.html', 'home-renovations.html', 
             'doors-windows.html', 'custom-projects.html', 'handcraftedfurniture&resins.html',
             'programming&databases.html'].includes(currentPage)) {
            
            const servicesLink = document.querySelector('nav a[href="#"]');
            if (servicesLink && servicesLink.textContent.trim() === 'Services') {
                servicesLink.style.background = '#800000';
                servicesLink.style.color = '#fff';
            }
        }
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
