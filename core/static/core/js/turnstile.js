/**
 * TurnstileManager - Handles Cloudflare Turnstile token management
 * 
 * This class provides a hybrid approach for token management:
 * - Uses invisible Turnstile widgets
 * - Generates fresh tokens for each API call to handle multiple submissions
 * - Automatically handles token expiration and refresh
 */
class TurnstileManager {
    constructor(siteKey) {
        this.siteKey = siteKey;
        this.widgetId = null;
        this.currentToken = null;
        this.isReady = false;
        
        // Wait for Turnstile API to be ready
        this.waitForTurnstile().then(() => {
            this.initialize();
        });
    }
    
    /**
     * Wait for the Turnstile API to be available
     */
    async waitForTurnstile() {
        return new Promise((resolve) => {
            const checkTurnstile = () => {
                if (window.turnstile) {
                    resolve();
                } else {
                    setTimeout(checkTurnstile, 100);
                }
            };
            checkTurnstile();
        });
    }
    
    /**
     * Initialize the invisible Turnstile widget
     */
    initialize() {
        try {
            // Create a hidden container for the widget
            const container = document.createElement('div');
            container.style.display = 'none';
            container.id = 'turnstile-widget';
            document.body.appendChild(container);
            
            // Render the invisible widget
            this.widgetId = window.turnstile.render(container, {
                sitekey: this.siteKey,
                theme: 'light',
                size: 'invisible',
                callback: (token) => {
                    this.currentToken = token;
                    console.log('Turnstile token received');
                },
                'error-callback': (error) => {
                    console.error('Turnstile error:', error);
                    this.currentToken = null;
                },
                'expired-callback': () => {
                    console.log('Turnstile token expired');
                    this.currentToken = null;
                }
            });
            
            this.isReady = true;
            console.log('TurnstileManager initialized');
        } catch (error) {
            console.error('Failed to initialize Turnstile:', error);
        }
    }
    
    /**
     * Get a fresh token for API calls
     * This method ensures we always have a valid token for each submission
     */
    async getToken() {
        if (!this.isReady || !this.widgetId) {
            throw new Error('Turnstile not ready');
        }
        
        try {
            // Reset the widget to get a fresh token
            window.turnstile.reset(this.widgetId);
            
            // Execute the challenge to get a new token
            return new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Turnstile token timeout'));
                }, 10000); // 10 second timeout
                
                // Override the callback temporarily to capture the new token
                const originalCallback = (token) => {
                    clearTimeout(timeout);
                    this.currentToken = token;
                    resolve(token);
                };
                
                // Execute the challenge
                window.turnstile.execute(this.widgetId);
                
                // Poll for token (fallback in case callback doesn't fire)
                const pollForToken = () => {
                    if (this.currentToken) {
                        clearTimeout(timeout);
                        resolve(this.currentToken);
                    } else {
                        setTimeout(pollForToken, 100);
                    }
                };
                
                setTimeout(pollForToken, 100);
            });
        } catch (error) {
            console.error('Failed to get Turnstile token:', error);
            throw error;
        }
    }
    
    /**
     * Check if Turnstile is ready
     */
    isInitialized() {
        return this.isReady && this.widgetId !== null;
    }
}

// Global instance - will be initialized when the page loads
window.turnstileManager = null;

// Initialize when DOM is ready and site key is available
document.addEventListener('DOMContentLoaded', () => {
    if (window.TURNSTILE_SITE_KEY) {
        window.turnstileManager = new TurnstileManager(window.TURNSTILE_SITE_KEY);
    } else {
        console.warn('Turnstile site key not found');
    }
});