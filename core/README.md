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

- **S3Service**: S3-compatible storage access
  - File listing and retrieval
  - Error handling with custom exceptions
  - Configurable endpoints and credentials

- **RateLimitService**: IP-based rate limiting
  - Request counting and threshold enforcement
  - Configurable time windows and limits
  - Memory based implementation
  - Shared across all app endpoints

- **CostTrackerService**: Cost tracking for LLM usage
  - Integration with `OpenRouterService` for real-time tracking
  - Calls https://openrouter.ai/api/v1/generation?id=gen-######
  - Gets `gen_id` from `OpenRouterService` API return
  - Half second delay after return of `gen_id` from `OpenRouterService`
  - Stores the total accumulated cost in a single JSON file (`./data/cost.json`)

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

