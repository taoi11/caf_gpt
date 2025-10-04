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
        this.initPromise = null;
        this._pending = null; // { resolve, reject, timeoutId }
        
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
    async initialize() {
        // Return existing promise if initialization is already in progress
        if (this.initPromise) {
            return this.initPromise;
        }
        
        this.initPromise = new Promise((resolve) => {
            try {
                // Create a hidden container for the widget
                const container = document.createElement('div');
                container.style.display = 'none';
                container.id = 'turnstile-widget';
                document.body.appendChild(container);
                
                // Wait for DOM to be ready
                if (document.readyState !== 'complete') {
                    window.addEventListener('load', () => {
                        this.renderWidget(container, resolve);
                    });
                } else {
                    this.renderWidget(container, resolve);
                }
            } catch (error) {
                console.error('Failed to initialize Turnstile:', error);
                this.isReady = false;
                resolve();
            }
        });
        
        return this.initPromise;
    }
    
    /**
     * Render the Turnstile widget
     */
    renderWidget(container, resolve) {
        try {
            // Render the invisible widget
            this.widgetId = window.turnstile.render(container, {
                sitekey: this.siteKey,
                theme: 'light',
                size: 'invisible',
                callback: (token) => this._onToken(token),
                'error-callback': (error) => this._onError(error),
                'expired-callback': () => this._onExpired()
            });
            
            this.isReady = true;
            console.log('TurnstileManager initialized');
            resolve();
        } catch (error) {
            console.error('Failed to render Turnstile widget:', error);
            this.isReady = false;
            resolve();
        }
    }
    
    /**
     * Internal: handle successful token issuance
     */
    _onToken(token) {
        this.currentToken = token;
        console.log('Turnstile token received');
        if (this._pending) {
            const { resolve, timeoutId } = this._pending;
            clearTimeout(timeoutId);
            this._pending = null;
            resolve(token);
        }
    }

    /**
     * Internal: handle widget error
     */
    _onError(error) {
        console.error('Turnstile error:', error);
        this.currentToken = null;
        if (this._pending) {
            const { reject, timeoutId } = this._pending;
            clearTimeout(timeoutId);
            this._pending = null;
            reject(new Error('Turnstile error'));
        }
    }

    /**
     * Internal: handle token expiration
     */
    _onExpired() {
        console.log('Turnstile token expired');
        this.currentToken = null;
        if (this._pending) {
            const { reject, timeoutId } = this._pending;
            clearTimeout(timeoutId);
            this._pending = null;
            reject(new Error('Turnstile token expired'));
        }
    }

    /**
     * Get a fresh token for API calls
     * This method ensures we always have a valid token for each submission
     */
    async getToken() {
        // Wait for initialization to complete
        if (this.initPromise) {
            await this.initPromise;
        }
        
        if (!this.isReady || !this.widgetId) {
            throw new Error('Turnstile not ready');
        }
        
        try {
            // If a previous token request is pending, cancel it
            if (this._pending) {
                const { reject, timeoutId } = this._pending;
                clearTimeout(timeoutId);
                this._pending = null;
                // Reject the older pending request to avoid leaks
                reject(new Error('Superseded by a new token request'));
            }

            // Reset the widget to get a fresh token and return a promise for the next callback
            window.turnstile.reset(this.widgetId);

            return new Promise((resolve, reject) => {
                const timeoutId = setTimeout(() => {
                    this._pending = null;
                    reject(new Error('Turnstile token timeout'));
                }, 15000); // 15 second timeout to be generous on slow networks

                // Keep handles so the render callback can resolve/reject
                this._pending = { resolve, reject, timeoutId };

                // Execute the challenge
                window.turnstile.execute(this.widgetId);
            });
        } catch (error) {
            console.error('Failed to get Turnstile token:', error);
            throw error;
        }
    }
    
    /**
     * Re-initialize the widget if it's broken
     */
    async reinitialize() {
        try {
            // Clean up existing widget
            const oldContainer = document.getElementById('turnstile-widget');
            if (oldContainer) {
                oldContainer.remove();
            }
            
            // Reset state
            this.widgetId = null;
            this.currentToken = null;
            this.isReady = false;
            this.initPromise = null;
            
            // Re-initialize
            await this.initialize();
        } catch (error) {
            console.error('Failed to re-initialize Turnstile:', error);
            this.isReady = false;
        }
    }
    
    /**
     * Check if Turnstile is ready
     */
    isInitialized() {
        // Avoid relying on undocumented internals; if we've rendered and marked ready, consider it initialized
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