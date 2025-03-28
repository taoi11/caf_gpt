/**
 * Policy Assistant chat functionality
 */

class PolicyChatUI {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.chatForm = document.getElementById('chatForm');
        this.userInput = document.getElementById('userInput');
        this.citationsContainer = document.getElementById('citationsContainer');
        this.apiEndpoint = '/policy/api/retrieve/';
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Handle form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Handle policy document clicks
        document.querySelectorAll('.policy-document').forEach(doc => {
            doc.addEventListener('click', (e) => {
                e.preventDefault();
                const docName = e.target.textContent;
                this.userInput.value = `Tell me about the ${docName}`;
                this.handleSubmit();
            });
        });
        
        // Handle keyboard shortcut (Ctrl+Enter)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.handleSubmit();
            }
        });
    }
    
    handleSubmit() {
        const query = this.userInput.value.trim();
        if (!query) return;
        
        // Add user message to chat
        this.addMessage(query, true);
        
        // Clear input
        this.userInput.value = '';
        
        // Show loading state
        this.citationsContainer.innerHTML = '<p class="text-muted">Searching policy documents...</p>';
        
        // Call API
        this.fetchPolicyResponse(query);
    }
    
    async fetchPolicyResponse(query) {
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken() 
                },
                body: JSON.stringify({ query })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    // Add assistant response
                    this.addMessage(data.response, false, data.citations);
                    // Update citations container
                    this.updateCitationsDisplay(data.citations);
                } else {
                    this.showError('Failed to get a response. Please try again.');
                }
            } else {
                this.showError('Server error. Please try again later.');
            }
        } catch (error) {
            console.error('Error fetching policy response:', error);
            this.showError('Connection error. Please check your network and try again.');
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
    
    updateCitationsDisplay(citations) {
        if (!citations || citations.length === 0) {
            this.citationsContainer.innerHTML = '<p class="text-muted">No citations available for this response.</p>';
            return;
        }
        
        this.citationsContainer.innerHTML = '<p class="text-muted">Click on a citation number in the response to view details.</p>';
    }
    
    addMessage(content, isUser, citations = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'assistant-message');
        
        const messagePara = document.createElement('p');
        messagePara.textContent = content;
        
        messageDiv.appendChild(messagePara);
        
        // Add citations if any
        if (citations && citations.length > 0 && !isUser) {
            const citationsDiv = document.createElement('div');
            citationsDiv.classList.add('citations');
            
            citations.forEach((citation, index) => {
                const citationSpan = document.createElement('span');
                citationSpan.classList.add('citation');
                citationSpan.textContent = `[${index + 1}]`;
                citationSpan.dataset.citation = JSON.stringify(citation);
                
                citationSpan.addEventListener('click', () => {
                    this.showCitation(citation);
                });
                
                citationsDiv.appendChild(citationSpan);
            });
            
            messageDiv.appendChild(citationsDiv);
        }
        
        this.chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    showCitation(citation) {
        this.citationsContainer.innerHTML = `
            <div class="citation-content">
                <h6>${citation.title}</h6>
                <p class="small">${citation.excerpt}</p>
                <div class="text-end">
                    <small class="text-muted">Document ID: ${citation.document_id}</small>
                </div>
            </div>
        `;
    }
    
    showError(message) {
        // Show error in chat
        const errorDiv = document.createElement('div');
        errorDiv.classList.add('message', 'error-message');
        errorDiv.textContent = message;
        this.chatContainer.appendChild(errorDiv);
        
        // Clear citations loading state
        this.citationsContainer.innerHTML = '<p class="text-muted">No citations available.</p>';
        
        // Scroll to bottom
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const chatContainer = document.getElementById('chatContainer');
    
    if (chatForm && chatContainer) {
        new PolicyChatUI();
    }
});
