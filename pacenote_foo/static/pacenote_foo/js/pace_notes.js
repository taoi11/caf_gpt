/**
 * Handles the frontend logic for the PaceNotes Generator page.
 * Includes Turnstile token management, handling user input, generating pace notes via API,
 * and displaying results or errors.
 */
class PaceNotesGenerator {
    /**
     * Initializes the PaceNotesGenerator by capturing DOM elements,
     * defining API endpoints, and binding event listeners.
     */
    constructor() {
        // DOM Elements
        this.inputBox = document.getElementById('input-box');
        this.generateBtn = document.getElementById('generate-btn');
        this.rankSelect = document.getElementById('rank-select');
        this.outputSection = document.querySelector('.output-section');
        
        // API Endpoints
        this.apiEndpoint = '/pacenote/api/generate-pace-note/';

        this.setupEventListeners();
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
     * Manages pace note generation workflow:
     * 1. Extracts user input and rank selection
     * 2. Validates input
     * 3. Gets fresh Turnstile token
     * 4. Toggles loading state
     * 5. Submits API request with token
     * 6. Renders result or error message
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
            // Get fresh Turnstile token
            if (!window.turnstileManager || !window.turnstileManager.isInitialized()) {
                throw new Error('Turnstile not initialized. Please refresh the page.');
            }
            
            const turnstileToken = await window.turnstileManager.getToken();
            
            const response = await fetch(this.apiEndpoint, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.getCSRFToken(),
              },
              body: JSON.stringify({
                rank: rank,
                user_input: inputText,
                turnstile_token: turnstileToken,
              }),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayOutput(data.pace_note);
            } else {
                this.showError(data.message || 'An error occurred while generating the pace note.');
            }
        } catch (error) {
            console.error('Error:', error);
            if (error.message.includes('Turnstile')) {
                this.showError('Security verification failed. Please refresh the page and try again.');
            } else {
                this.showError('Connection error. Please check your network and try again.');
            }
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
            this.generateBtn.textContent = 'Generate Pace Note';
        }
    }

    /**
     * Renders pace note output in a card with copy functionality.
     * @param {string} content - HTML/text content to display.
     */
    displayOutput(content) {
        // Clear previous output/errors and set new content
        this.outputSection.innerHTML = `
            <div class="output-card">
                <div class="output-header">
                    <h5>Generated Pace Note</h5>
                    <button class="copy-button button" title="Copy to clipboard">Copy</button> 
                </div>
                <div class="output-body">
                    <div class="output-content">${content}</div>
                </div>
            </div>
        `;
        
        // Set up copy button functionality
        const copyBtn = document.querySelector('.copy-button');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const outputContent = document.querySelector('.output-content');
                navigator.clipboard.writeText(outputContent.textContent)
                    .then(() => {
                        copyBtn.textContent = 'Copied!';
                        setTimeout(() => {
                            copyBtn.textContent = 'Copy';
                        }, 2000);
                    })
                    .catch(error => {
                        console.error('Error copying to clipboard:', error);
                    });
            });
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
        errorBox.className = 'error-message'; // Use custom error class
        errorBox.textContent = message;
        
        this.outputSection.insertBefore(errorBox, this.outputSection.firstChild);
        setTimeout(() => errorBox.remove(), 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PaceNotesGenerator();
});
