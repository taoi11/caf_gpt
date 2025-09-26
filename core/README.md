# Core App

## Purpose
Foundation module providing shared functionality, services, and utilities across the CAF GPT platform.
Holds common components used by other applications to ensure consistency and reusability.

## Key Components

### Services
- **OpenRouterService**: LLM integration via OpenRouter API
  - Request handling and error management
  - Response formatting and logging
  - Temperature and token control
  - Configurable model selection

- **TurnstileService**: Cloudflare Turnstile integration for bot protection
  - Token validation and verification
  - Rate limiting through human verification
  - Configurable site and secret keys

- **CostTrackerService**: Cost tracking for LLM usage
  - Integration with `OpenRouterService` for real-time tracking
  - Calls https://openrouter.ai/api/v1/generation?id=gen-######
  - Gets `gen_id` from `OpenRouterService` API return
  - Half second delay after return of `gen_id` from `OpenRouterService`
  - Stores the total accumulated cost in a database table (`cost_tracker`)
  - Table creation SQL:
    ```sql
    CREATE TABLE cost_tracker (
        id INTEGER PRIMARY KEY,
        total_usage DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    INSERT INTO cost_tracker (id, total_usage) VALUES (1, 0.0) ON CONFLICT (id) DO NOTHING;
    ```

### Views
- **Landing page**: Entry point with links to all applications
- **Health check**: System status endpoint
- **CSP report**: Content Security Policy violation reporting endpoint

### Context Processors
- **cost_context**: Provides cost tracking data to all templates

### Templates
- **base.html**: Main template with custom CSS
  - Navbar
  - Common footer
  - Cost usage display
  - CSP nonce integration
- **landing_page.html**: Landing page template
  - Block structure for `*_foo` apps

### Security Features
- Content Security Policy (CSP) implementation
- WhiteNoise for static file serving with compression
- Security headers configuration

