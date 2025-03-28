// Base JavaScript functionality for CAF GPT

document.addEventListener('DOMContentLoaded', function() {
    console.log('CAF GPT application initialized');
    
    // Mobile menu toggle
    initMobileMenu();
    
    // Initialize Bootstrap components if available
    initBootstrapComponents();
    
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
 * Initializes Bootstrap tooltips and popovers if Bootstrap is available
 */
function initBootstrapComponents() {
    // Check if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
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

/**
 * Updates any rate limit displays on the page
 */
function updateRateLimits() {
    // Check if we need to fetch rate limits
    const rateLimitElements = document.querySelectorAll('.hourly-remaining, .daily-remaining');
    if (rateLimitElements.length === 0) return;
    
    // Determine which app we're in based on the URL path
    const path = window.location.pathname;
    let rateLimitsEndpoint = '/api/rate-limits/';
    
    // Adjust endpoint based on current app
    if (path.startsWith('/pacenote/')) {
        rateLimitsEndpoint = '/pacenote/api/rate-limits/';
    } else if (path.startsWith('/policy/')) {
        rateLimitsEndpoint = '/policy/api/rate-limits/';
    }
    
    // Fetch rate limits from API
    fetch(rateLimitsEndpoint)
        .then(response => response.json())
        .then(data => {
            // Update hourly limits
            document.querySelectorAll('.hourly-remaining').forEach(el => {
                el.textContent = `${data.hourly.remaining}/${data.hourly.limit}`;
            });
            
            // Update daily limits
            document.querySelectorAll('.daily-remaining').forEach(el => {
                el.textContent = `${data.daily.remaining}/${data.daily.limit}`;
            });
        })
        .catch(error => console.error('Error fetching rate limits:', error));
}

// Expose functions that might be needed by other modules
window.cafGpt = {
    updateRateLimits: updateRateLimits
};