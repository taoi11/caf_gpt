/**
 * Handles the frontend logic for the PaceNotes Generator page.
 * Includes fetching rate limits, handling user input, generating pace notes via API,
 * and displaying results or errors.
 */
class PaceNotesGenerator {
    /**
     * Initializes the PaceNotesGenerator by capturing DOM elements,
     * defining API endpoints, binding event listeners, and fetching
     * initial rate limits.
     */
    constructor() {
        // DOM Elements
        this.inputBox = document.getElementById('input-box');
        this.generateBtn = document.getElementById('generate-btn');
        this.rankSelect = document.getElementById('rank-select');
        this.outputSection = document.querySelector('.output-section');
        this.hourlyRemainingElement = document.querySelector('.hourly-remaining');
        this.dailyRemainingElement = document.querySelector('.daily-remaining');
        // API Endpoints
        this.apiEndpoint = '/pacenote/api/generate-pace-note/';
        this.rateLimitsEndpoint = '/pacenote/api/rate-limits/';

        this.setupEventListeners();
        this.loadRateLimits(); // Perform initial load of rate limits when the page loads
    }

    /**
     * Sets up event listeners for the generate button click and
     * the Ctrl+Enter keyboard shortcut in the input box.
     */
    setupEventListeners() {
        // Generate button click listener
        this.generateBtn.addEventListener('click', () => {
            this.generatePaceNote();
        });
        
        // Ctrl+Enter shortcut
        this.inputBox.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.generatePaceNote();
            }
        });
    }

    /**
     * Fetches current rate limit status from the API.
     *
     * Called during:
     * 1. Initial page load to display starting limits
     * 2. After successful or failed pace note generation to reflect current server state
     *
     * Implements aggressive cache-busting to ensure fresh limit data
     */
    async loadRateLimits() {
        try {
            // Fetch rate limits from the dedicated endpoint.
            // Use cache-busting headers to ensure fresh data.
            const response = await fetch(this.rateLimitsEndpoint, {
                cache: 'no-cache', // Tells the browser not to use its cache
                headers: {
                    'Cache-Control': 'no-cache', // Standard HTTP header for cache control
                    'Pragma': 'no-cache' // Legacy header for older browsers/proxies
                }
            });
            // Check if the fetch request itself was successful (e.g., network ok, server responded)
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.updateRateLimitsDisplay(data);
        } catch (error) {
            console.error('Error fetching rate limits for PaceNotes:', error);
            // Optionally display an error or default values
            if (this.hourlyRemainingElement) this.hourlyRemainingElement.textContent = 'Error';
            if (this.dailyRemainingElement) this.dailyRemainingElement.textContent = 'Error';
        }
    }

    /**
     * Updates rate limit counters in the UI.
     * @param {object} data - Rate limit data from API.
     * @param {object} data.hourly - Hourly limit info (remaining/limit).
     * @param {object} data.daily - Daily limit info (remaining/limit).
     */
    updateRateLimitsDisplay(data) {
        // Update hourly remaining display if the element exists
        if (this.hourlyRemainingElement) {
            this.hourlyRemainingElement.textContent = `${data.hourly.remaining}/${data.hourly.limit}`;
        }
        
        if (this.dailyRemainingElement) {
            this.dailyRemainingElement.textContent = `${data.daily.remaining}/${data.daily.limit}`;
        }
    }

    /**
     * Manages pace note generation workflow:
     * 1. Extracts user input and rank selection
     * 2. Validates input
     * 3. Toggles loading state
     * 4. Submits API request
     * 5. Renders result or error message
     * 6. Refreshes rate limit counters
     * 7. Resets UI state
     */
    async generatePaceNote() {
        const inputText = this.inputBox.value.trim();
        const rank = this.rankSelect.value;
        
        if (!inputText) {
            this.showError('Please provide details about the CAF member.');
            return;
        }
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            const response = await fetch(this.apiEndpoint, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.getCSRFToken(),
              },
              body: JSON.stringify({
                rank: rank,
                user_input: inputText,
              }),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayOutput(data.pace_note);
                this.loadRateLimits(); // Fetch and update rate limits after successful generation
            } else {
                this.showError(data.message || 'An error occurred while generating the pace note.');
                // Still try to update rate limits even if generation failed (e.g., rate limit exceeded error)
                this.loadRateLimits(); 
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please check your network and try again.');
        } finally {
            this.setLoadingState(false);
        }
    }
    /**
     * Extracts CSRF token from cookies.
     * Required for Django POST requests to protect against CSRF attacks.
     * @returns {string} CSRF token value or empty string if not found.
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return ''; // Return empty string if token not found
    }

    /**
     * Toggles the generate button's loading state.
     * Disables button and displays spinner during API calls.
     * @param {boolean} isLoading - Whether to show loading state.
     */
    setLoadingState(isLoading) {
        if (isLoading) {
            this.generateBtn.disabled = true; // Disable button during generation
            this.generateBtn.innerHTML = '<span class="loading-spinner"></span> Generating...'; // Show spinner and text
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i>Generate Pace Note';
        }
    }

    /**
     * Renders pace note output in a card with copy functionality.
     * @param {string} content - HTML/text content to display.
     */
    displayOutput(content) {
        // Clear previous output/errors and set new content
        this.outputSection.innerHTML = `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Generated Pace Note</h5>
                    <button class="btn btn-sm btn-outline-secondary copy-btn" data-bs-toggle="tooltip" title="Copy to clipboard">
                        <i class="bi bi-clipboard"></i>
                    </button>
                </div>
                <div class="card-body">
                    <div class="output-content">${content}</div>
                </div>
            </div>
        `;
        
        // Set up copy button functionality
        const copyBtn = document.querySelector('.copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const outputContent = document.querySelector('.output-content');
                navigator.clipboard.writeText(outputContent.textContent)
                    .then(() => {
                        copyBtn.innerHTML = '<i class="bi bi-check2"></i>';
                        setTimeout(() => {
                            copyBtn.innerHTML = '<i class="bi bi-clipboard"></i>';
                        }, 2000);
                    })
                    .catch(error => {
                        console.error('Error copying to clipboard:', error);
                    });
            });
        }
        
        // Initialize tooltips if Bootstrap is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
        }
    }

    /**
     * Displays a temporary error alert in the output section.
     * Auto-dismisses after 5 seconds.
     * @param {string} message - Error text to display.
     */
    showError(message) {
        // Create a Bootstrap alert element
        const errorBox = document.createElement('div');
        errorBox.className = 'alert alert-danger'; // Use Bootstrap's danger alert style
        errorBox.textContent = message;
        
        this.outputSection.insertBefore(errorBox, this.outputSection.firstChild);
        setTimeout(() => errorBox.remove(), 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PaceNotesGenerator();
});
