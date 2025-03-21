// PaceNote functionality

// Rate limiter utility
const rateLimiter = {
    initializeDisplay: function() {
        // For demo purposes, set some initial values
        document.querySelector('.hourly-remaining').textContent = '10/10';
        document.querySelector('.daily-remaining').textContent = '100/100';
    },
    
    updateLimits: async function() {
        try {
            // In a real implementation, this would fetch from the server
            // For now, just simulate a decrease in available requests
            const hourlyEl = document.querySelector('.hourly-remaining');
            const dailyEl = document.querySelector('.daily-remaining');
            
            if (hourlyEl && dailyEl) {
                const hourly = hourlyEl.textContent.split('/');
                const daily = dailyEl.textContent.split('/');
                
                const newHourly = Math.max(0, parseInt(hourly[0]) - 1);
                const newDaily = Math.max(0, parseInt(daily[0]) - 1);
                
                hourlyEl.textContent = `${newHourly}/${hourly[1]}`;
                dailyEl.textContent = `${newDaily}/${daily[1]}`;
            }
            
            return true;
        } catch (error) {
            console.error('Error updating rate limits:', error);
            return false;
        }
    }
};

class PaceNotesUI {
    constructor() {
        this.outputSection = document.querySelector('.output-section');
        this.inputBox = document.querySelector('.input-box');
        this.generateButton = document.getElementById('generate-btn');
        this.rankSelect = document.getElementById('rank-select');
        this.maxOutputs = 5;
        this.outputs = [];
        this.sessionKey = 'caf-gpt-pacenotes-input';
        this.apiEndpoint = '/pacenote/api/generate-pace-note/';
        
        // Restore input from session storage
        this.inputBox.value = sessionStorage.getItem(this.sessionKey) || '';
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.generateButton.addEventListener('click', () => this.handleGenerate());
        
        this.inputBox.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.handleGenerate();
            }
        });

        this.inputBox.addEventListener('input', () => {
            sessionStorage.setItem(this.sessionKey, this.inputBox.value);
        });
        
        this.rankSelect.addEventListener('change', () => {
            this.generateButton.disabled = !this.rankSelect.value;
        });
    }

    createOutputBox(content, timestamp, isLoading = false) {
        const box = document.createElement('div');
        box.className = 'card mb-4';
        
        if (isLoading) {
            box.innerHTML = `
                <div class="card-body text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">Generating pace note...</p>
                </div>
            `;
        } else {
            box.innerHTML = `
                <div class="card-body">
                    <pre class="response-text">${content}</pre>
                    <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
                        <small class="text-muted">${new Date(timestamp).toLocaleString()}</small>
                        <button class="btn btn-sm btn-outline-secondary copy-button">
                            Copy
                        </button>
                    </div>
                </div>
            `;

            const copyBtn = box.querySelector('.copy-button');
            copyBtn.addEventListener('click', () => this.handleCopy(content, copyBtn));
        }

        return box;
    }

    async handleCopy(content, button) {
        try {
            await navigator.clipboard.writeText(content);
            button.textContent = 'Copied!';
            setTimeout(() => button.textContent = 'Copy', 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
            button.textContent = 'Error';
            setTimeout(() => button.textContent = 'Copy', 2000);
        }
    }

    addOutput(content, timestamp) {
        // Remove oldest output if we have too many
        if (this.outputs.length >= this.maxOutputs) {
            const oldest = this.outputs.shift();
            oldest?.element.remove();
        }

        const box = this.createOutputBox(content, timestamp);
        this.outputSection.insertBefore(box, this.outputSection.firstChild);
        this.outputs.push({
            element: box,
            timestamp
        });
    }

    async handleGenerate() {
        const input = this.inputBox.value.trim();
        const rank = this.rankSelect.value;

        if (!input) {
            this.showError('Please enter some text to generate a pace note.');
            return;
        }

        if (!rank) {
            this.showError('Please select a rank before generating.');
            return;
        }

        // Disable input and button during generation
        this.generateButton.disabled = true;
        this.inputBox.disabled = true;
        this.rankSelect.disabled = true;

        // Add loading box
        const loadingBox = this.createOutputBox('', new Date().toISOString(), true);
        this.outputSection.insertBefore(loadingBox, this.outputSection.firstChild);

        try {
            // Convert rank format from 'cpl-mcpl' to 'cpl_mcpl'
            const apiRank = rank.replace('-', '_');
            
            // Call the API to generate the pace note
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: input,
                    rank: apiRank
                })
            });
            
            // Remove loading box
            loadingBox.remove();
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Display the result
                    this.addOutput(data.pace_note, new Date().toISOString());
                    
                    // Update rate limits
                    rateLimiter.updateLimits();
                } else {
                    this.showError(`Error: ${data.message || 'Unknown error'}`);
                }
            } else {
                this.showError(`Server error: ${response.status}`);
            }
        } catch (error) {
            // Remove loading box on error too
            loadingBox.remove();
            this.showError('Failed to connect to server. Please try again.');
            console.error('Error:', error);
        } finally {
            // Re-enable inputs
            this.generateButton.disabled = !this.rankSelect.value;
            this.inputBox.disabled = false;
            this.rankSelect.disabled = false;
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
    const ui = new PaceNotesUI();
    rateLimiter.initializeDisplay();
}); 