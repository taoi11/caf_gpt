// Main JavaScript file for CAF GPT

document.addEventListener('DOMContentLoaded', function() {
    console.log('CAF GPT application initialized');
    
    // Mobile menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (menuToggle && navbarMenu) {
        menuToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
        });
    }
    
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
    
    // Smooth scrolling for anchor links
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
    
    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation === linkPath || currentLocation.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });
    
    // Common functionality for text areas with Ctrl+Enter support
    const textAreas = document.querySelectorAll('textarea[data-ctrl-enter="true"]');
    textAreas.forEach(textArea => {
        textArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                
                // Find closest form and submit it
                const form = textArea.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }
        });
    });
    
    // Rate limit display updater
    updateRateLimits();
});

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