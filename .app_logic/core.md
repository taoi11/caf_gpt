# Core App Specification

## Purpose
Base application containing shared functionality, landing page, and health check endpoint.

## Key Features
- Bootstrap-based landing page with tool navigation
- Security headers middleware
- Health check endpoint for monitoring
- Base templates and styles
- Common models (TimeStampedModel)

## Components
1. **Views**
   - LandingPageView - Bootstrap-styled landing page with tool cards
   - HealthCheckView - JSON response for monitoring

2. **Middleware**
   - SecurityHeadersMiddleware - Adds security headers to responses

3. **Models**
   - TimeStampedModel - Abstract base model with created_at and updated_at fields

4. **Templates**
   - core/base.html - Main template with Bootstrap styling and navigation
   - core/landing_page.html - Landing page with tool cards

## Implementation Details
- Bootstrap 5 for styling
- Environment variables loaded from .env file
- Modular settings structure (base.py and environment-specific overrides)
- PostgreSQL database connection via URL parsing
- Navbar with links to all available tools (Home, PaceNote, Policy)
- Common footer across all pages

## Future Enhancements
- IP-based rate limiting
- Analytics tracking (optional)
- API client base class
- Additional security middleware

## Questions
1. Do we need any analytics tracking on the landing page?
2. Should rate limits be configurable via environment variables?
