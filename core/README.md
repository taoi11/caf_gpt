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

- **S3Service**: S3-compatible storage access
  - File listing and retrieval
  - Error handling with custom exceptions
  - Configurable endpoints and credentials

- **RateLimitService**: IP-based rate limiting
  - Request counting and threshold enforcement
  - Configurable time windows and limits
  - Memory based implementation

- **CostTrackerService**: Cost tracking for LLM usage
  - Integration with `OpenRouterService` for real-time tracking
  - Calls https://openrouter.ai/api/v1/generation?id=gen-######
  - Gets `gen_id` from `OpenRouterService` API return
  - Half second delay after return of `gen_id` from `OpenRouterService`

### Templates
- **base.html**: Main template with custom CSS
  - navbar
  - Common footer
  - cost usage display
- **landing_page.html**: Landing page template
  - Block structure for `*_foo` apps

