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
            resolve();
        } catch (error) {
            console.error('Failed to render Turnstile widget:', error);
            this.isReady = false;
            resolve();
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
            // Check if the widget element exists before trying to reset it
            if (!this.widgetExists()) {
                console.warn('Turnstile widget element not found, re-initializing...');
                await this.reinitialize();
                if (!this.isReady) {
                    throw new Error('Failed to re-initialize Turnstile');
                }
            }
            
            // Reset the widget to get a fresh token
            window.turnstile.reset(this.widgetId);
            
            // Execute the challenge to get a new token
            return new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Turnstile token timeout'));
                }, 10000); // 10 second timeout

                // Create a new callback to capture the token
                const tokenCallback = (token) => {
                    clearTimeout(timeout);
                    this.currentToken = token;
                    resolve(token);
                };

                // Safely set the callback
                this.setWidgetCallback(tokenCallback);

                // Execute the challenge
                window.turnstile.execute(this.widgetId);
            });
        } catch (error) {
            console.error('Failed to get Turnstile token:', error);
            throw error;
        }
    }
    
    /**
     * Check if the widget element exists in the DOM
     */
    widgetExists() {
        try {
            // Check if the widget container exists
            const container = document.getElementById('turnstile-widget');
            if (!container) return false;
            
            // Check if the widget is in the renderedWidgets object
            if (!window.turnstile.renderedWidgets) return false;
            
            // Check if our specific widget exists
            return !!window.turnstile.renderedWidgets[this.widgetId];
        } catch (error) {
            console.error('Error checking widget existence:', error);
            return false;
        }
    }
    
    /**
     * Safely set the widget callback
     */
    setWidgetCallback(callback) {
        try {
            if (window.turnstile.renderedWidgets && window.turnstile.renderedWidgets[this.widgetId]) {
                window.turnstile.renderedWidgets[this.widgetId].callback = callback;
            } else {
                console.error('Cannot set callback: widget not found in renderedWidgets');
            }
        } catch (error) {
            console.error('Error setting widget callback:', error);
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
        return this.isReady && this.widgetId !== null && this.widgetExists();
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