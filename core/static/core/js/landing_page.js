// Landing page specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Landing page script loaded');
    
    // Add any landing page specific interactivity here
    initFeatureCards();
});

/**
 * Initialize feature card interactions if any
 */
function initFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        // Example: Add click handler for feature cards if needed
        card.addEventListener('click', function() {
            const link = this.querySelector('a');
            if (link) {
                link.click();
            }
        });
    });
}
