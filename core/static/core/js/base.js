// Base JavaScript functionality for CAF GPT

document.addEventListener('DOMContentLoaded', function() {
    console.log('CAF GPT application initialized');
    
    // Mobile menu toggle
    initMobileMenu();
    
    // Smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Add active class to current nav item
    highlightCurrentNavItem();
});

/**
 * Initializes mobile menu toggle functionality
 */
function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (menuToggle && navbarMenu) {
        menuToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
        });
    }
}


/**
 * Sets up smooth scrolling for anchor links
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Highlights the current navigation item based on URL
 */
function highlightCurrentNavItem() {
    const currentLocation = window.location.pathname;
    // Fixed selector to match our HTML structure
    const navLinks = document.querySelectorAll('.nav-links .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation === linkPath || currentLocation.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });
}
