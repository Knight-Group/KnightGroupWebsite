function toggleMobileMenu() {
    var menu = document.getElementById('mobileMenu');
    menu.classList.toggle('active');
}

function toggleServicesMenu(e) {
    console.log('toggleServicesMenu called');
    if (e) e.preventDefault();
    var submenu = document.getElementById('mobileServicesMenu');
    var toggleBtn = document.querySelector('.submenu-toggle');
    var isOpen = submenu.classList.contains('show');
    if (isOpen) {
        submenu.classList.remove('show');
        submenu.setAttribute('aria-hidden', 'true');
        toggleBtn.setAttribute('aria-expanded', 'false');
    } else {
        submenu.classList.add('show');
        submenu.setAttribute('aria-hidden', 'false');
        toggleBtn.setAttribute('aria-expanded', 'true');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var toggleBtn = document.querySelector('.submenu-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleServicesMenu();
            }
        });
    }
});
