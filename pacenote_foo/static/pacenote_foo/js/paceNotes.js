/**
 * PaceNotes Generator functionality
 */

class PaceNotesGenerator {
    constructor() {
        this.inputBox = document.getElementById('input-box');
        this.generateBtn = document.getElementById('generate-btn');
        this.rankSelect = document.getElementById('rank-select');
        this.outputSection = document.querySelector('.output-section');
        this.hourlyRemainingElement = document.querySelector('.hourly-remaining');
        this.dailyRemainingElement = document.querySelector('.daily-remaining');
        this.apiEndpoint = '/pacenote/api/generate-pace-note/';
        this.rateLimitsEndpoint = '/pacenote/api/rate-limits/';
        
        this.setupEventListeners();
        this.loadRateLimits();
    }
    
    setupEventListeners() {
        // Generate button click
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
    
    loadRateLimits() {
        fetch(this.rateLimitsEndpoint)
            .then(response => response.json())
            .then(data => {
                this.updateRateLimitsDisplay(data);
            })
            .catch(error => {
                console.error('Error fetching rate limits:', error);
            });
    }
    
    updateRateLimitsDisplay(data) {
        if (this.hourlyRemainingElement) {
            this.hourlyRemainingElement.textContent = `${data.hourly.remaining}/${data.hourly.limit}`;
        }
        
        if (this.dailyRemainingElement) {
            this.dailyRemainingElement.textContent = `${data.daily.remaining}/${data.daily.limit}`;
        }
    }
    
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
                user_input: inputText,  // Use inputText instead of user_input and rename field to user_input
              }),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayOutput(data.pace_note);
                // Only update rate limits if they're included in the response
                if (data.rate_limits) {
                    this.updateRateLimitsDisplay(data.rate_limits);
                }
            } else {
                this.showError(data.message || 'An error occurred while generating the pace note.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please check your network and try again.');
        } finally {
            this.setLoadingState(false);
        }
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    setLoadingState(isLoading) {
        if (isLoading) {
            this.generateBtn.disabled = true;
            this.generateBtn.innerHTML = '<span class="loading-spinner"></span> Generating...';
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i>Generate Pace Note';
        }
    }
    
    displayOutput(content) {
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
    }
    
    showError(message) {
        const errorBox = document.createElement('div');
        errorBox.className = 'alert alert-danger';
        errorBox.textContent = message;
        
        this.outputSection.insertBefore(errorBox, this.outputSection.firstChild);
        setTimeout(() => errorBox.remove(), 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PaceNotesGenerator();
});