# Core App

## Purpose
Foundation module providing shared functionality, services, and utilities across the CAF GPT platform.
Holds common components used by other applications to ensure consistency and reusability.

## Directory Structure
```
core/
├── models.py         # Base models
├── views.py          # Landing page and health check views
├── urls.py           # Core URL configuration
├── middleware.py     # Custom middleware
├── services/         # Shared services
│   ├── open_router_service.py # LLM integration
│   ├── database_service.py # Database operations
│   └── turnstile_service.py # Cloudflare Turnstile integration
├── templates/        # Core templates
│   └── base/         # Base templates
├── static/           # Core static files
└── utils/            # Utility functions
```

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

 

- **DatabaseService**: Database operations and ORM utilities
  - Query optimization and batch processing
  - Transaction management
  - Custom query builders

### Views
- **Landing page**: Entry point with links to all applications
- **Health check**: System status endpoint
- **CSP report**: Content Security Policy violation reporting endpoint

### Context Processors
 

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
- Cloudflare Turnstile integration for bot protection

## Cloudflare Turnstile Integration

The platform implements Cloudflare Turnstile for bot protection across all applications. This integration helps prevent automated abuse of the system while maintaining a good user experience.

### Implementation Details

The Turnstile integration is implemented through the `TurnstileService` in the core application. This service handles:

- Token validation and verification
- Rate limiting through human verification
- Configurable site and secret keys
- Integration with Django views for bot protection

### Usage in Applications

All public-facing endpoints that require bot protection should integrate with the Turnstile service. This includes:

- PaceNoteGeneratorView in pacenote_foo app
- PolicyRouterView in policy_foo app
- Any other user-facing API endpoints

### Configuration

The following environment variables are required for Turnstile integration:

- `TURNSTILE_SITE_KEY`: Cloudflare Turnstile site key
- `TURNSTILE_SECRET_KEY`: Cloudflare Turnstile secret key

### Security Considerations

- Turnstile tokens are validated on the server-side
- All user submissions require valid Turnstile tokens
- The service implements rate limiting to prevent abuse
- Tokens are validated before processing any user input

### Utilities
- **turnstile_utils.py**: Helper functions for Turnstile token validation
- **database_utils.py**: Database connection and migration utilities

### Models
- **DoadDocument**: Unmanaged model for DOAD documents from external Postgres
- **LeaveDocument**: Unmanaged model for Leave policy documents from external Postgres

