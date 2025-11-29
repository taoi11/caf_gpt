/**
 * Handles the frontend logic for the Policy Assistant chat interface.
 *
 * - Manages sending user messages to the backend API.
 * - Processes responses, including parsing XML for answer, citations, and follow-up.
 * - Updates the chat display, citations area, and suggestion text.
 * - Handles loading states and error messages.
 */
class PolicyChat {
    /**
     * Initializes the PolicyChat instance.
     * - Selects necessary DOM elements (chat container, input form, citations area, etc.).
     * - Sets up event listeners for form submission and potentially other interactions.
     * - Defines the API endpoint for chat communication.
     * - Initializes an empty array to store the conversation history.
     */
    constructor() {
        // DOM Element Selection
        this.chatContainer = document.getElementById('chatContainer');
        this.chatForm = document.getElementById('chatForm');
        this.userInput = document.getElementById('userInput');
        this.sendButton = this.chatForm.querySelector('button[type="submit"]'); // Assuming a submit button exists

        // API Endpoint (Update this URL when the backend route is defined)
        this.chatApiEndpoint = '/policy/api/chat/'; // Placeholder URL

        // Conversation History
        this.messageHistory = []; // Stores { role: 'user'/'assistant', content: 'message text' }

        // Bind event listeners
        this.setupEventListeners();

        // Initial setup (e.g., clear citations, add initial assistant message to history if needed)
        this.initializeChat();
    }

    /**
     * Sets up event listeners for the chat form.
     * - Listens for form submission.
     * - Listens for Ctrl+Enter keydown in the textarea.
     */
    setupEventListeners() {
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSendMessage();
        });

        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    }

    /**
     * Initializes the chat interface.
     * - Clears the citations container.
     * - Adds the initial assistant message to the message history (if not already done via HTML).
     */
    initializeChat() {
        // Optional: Add the initial assistant message from HTML to the history
        const initialAssistantMessage = this.chatContainer.querySelector('.assistant-message p');
        if (initialAssistantMessage) {
             this.messageHistory.push({ role: 'assistant', content: initialAssistantMessage.textContent });
        }
    }

    /**
     * Handles the process of sending a user message.
     * - Gets user input.
     * - If input is valid:
     *   - Displays the user message in the chat container.
     *   - Adds the user message to the message history.
     *   - Clears the input field.
     *   - Calls the method to send the message to the backend.
     */
    handleSendMessage() {
        const messageText = this.userInput.value.trim();
        if (!messageText) return;

        this.displayMessage(messageText, 'user');
        this.messageHistory.push({ role: 'user', content: messageText });
        this.userInput.value = '';
        this.userInput.placeholder = 'Thinking...'; // Clear suggestion

        this.sendMessageToBackend();
    }

    /**
     * Sends the current message history to the backend API.
     * - Sets loading state.
     * - Prepares the payload including message history and policy_set.
     * - Makes a POST request to the chat API endpoint.
     * - Handles the response or error.
     * - Resets loading state.
     */
    async sendMessageToBackend() {
        this.setLoadingState(true);
        const csrfToken = this.getCSRFToken();

        try {
            const response = await fetch(this.chatApiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    messages: this.messageHistory,
                    policy_set: 'doad' // Hardcoded for now, could be dynamic later
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const responseData = await response.json();
            this.handleBackendResponse(responseData.assistant_message); // Assuming backend returns { assistant_message: '...' }

        } catch (error) {
            console.error('Error sending message:', error);
            this.displayError(`Failed to get response: ${error.message}`);
            // Add the error message as an assistant response in history to avoid resending the user query immediately
             this.messageHistory.push({ role: 'assistant', content: `Error: ${error.message}` });
        } finally {
            this.setLoadingState(false);
        }
    }

    /**
     * Handles the response received from the backend.
     * - Parses the XML response string.
     * - Extracts answer, citations, and follow-up suggestion.
     * - Displays the answer as an assistant message.
     * - Updates the citations container.
     * - Sets the follow-up suggestion as placeholder text in the input field.
     * - Adds the assistant's answer to the message history.
     * @param {string} responseText - The raw XML response string from the backend.
     */
    handleBackendResponse(responseText) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(responseText, "text/xml");

            // Error handling for parsing
            const parseError = xmlDoc.querySelector("parsererror");
            if (parseError) {
                console.error("XML Parsing Error:", parseError);
                throw new Error("Received malformed XML response from server.");
            }

            const answer = xmlDoc.querySelector("answer")?.textContent || "Sorry, I couldn't formulate a response.";
            const citationsText = xmlDoc.querySelector("citations")?.textContent.trim() || "";
            const followUp = xmlDoc.querySelector("follow_up")?.textContent || "Ask another question...";

            // Display Answer
            this.displayMessage(answer, 'assistant', citationsText); // Pass citations
            this.messageHistory.push({ role: 'assistant', content: answer }); // Add only the answer part to history

            // Set Follow-up Suggestion
            this.userInput.placeholder = followUp;

        } catch (error) {
            console.error('Error processing backend response:', error);
            this.displayError(`Error processing response: ${error.message}`);
             // Add the error message as an assistant response in history
             this.messageHistory.push({ role: 'assistant', content: `Error processing response: ${error.message}` });
             this.userInput.placeholder = "Ask another question..."; // Reset placeholder on error
        }
    }

    /**
     * Displays a message in the chat container.
     * @param {string} message - The message text (can include simple HTML for formatting).
     * @param {string} sender - 'user' or 'assistant'.
     */
    displayMessage(message, sender, citationsText = '') { // Add optional citationsText
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        // Use innerHTML carefully, assuming backend sanitizes or response format is controlled
        // Consider using a markdown parser if backend provides markdown
        let messageHTML = `<p>${message.replace(/\n/g, '<br>')}</p>`; // Basic newline handling

        // Append citations if available for assistant messages
        if (sender === 'assistant' && citationsText) {
            const citationLines = citationsText.split('\n').filter(line => line.trim() !== '');
            if (citationLines.length > 0) {
                messageHTML += '<div class="citations-block">'; // Add a container div for citations
                messageHTML += '<h6>Citations:</h6>'; // Add a heading
                messageHTML += '<ul>';
                citationLines.forEach(line => {
                    // Simple list item for now. Could add links or more complex formatting later.
                    messageHTML += `<li>${line.trim()}</li>`;
                });
                messageHTML += '</ul>';
                messageHTML += '</div>'; // Close container div
            }
        }

        messageElement.innerHTML = messageHTML; // Set the combined HTML
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    /**
     * Displays an error message in the chat container.
     * @param {string} errorMessage - The error message text.
     */
    displayError(errorMessage) {
        const errorElement = document.createElement('div');
        errorElement.classList.add('message', 'error-message'); // Use 'message' for structure, 'error-message' for styling
        errorElement.innerHTML = `<p>${errorMessage}</p>`;
        this.chatContainer.appendChild(errorElement);
        this.scrollToBottom();
    }


    /**
     * Scrolls the chat container to the bottom.
     */
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    /**
     * Sets the loading state for the send button.
     * @param {boolean} isLoading - True to show loading, false otherwise.
     */
    setLoadingState(isLoading) {
        if (isLoading) {
            this.sendButton.disabled = true;
            this.sendButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';
            this.userInput.disabled = true;
        } else {
            this.sendButton.disabled = false;
            this.sendButton.innerHTML = 'Send';
            this.userInput.disabled = false;
            // Re-focus input after sending might be useful
            // this.userInput.focus();
        }
    }

    /**
     * Retrieves the CSRF token from cookies.
     * @returns {string} The CSRF token value.
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        console.warn('CSRF token not found.'); // Warn if token is missing
        return '';
    }
}

// Initialize the chat when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new PolicyChat();
});
