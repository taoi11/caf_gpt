# Core App Specification

## Purpose
Base application containing shared functionality and landing page

## Key Features
- Landing page with tool navigation
- IP-based rate limiting for tool pages (Cloudflare FORWARDED_FROM_IP_HEADER)
- Common utilities framework
- Base templates/styles
- Security middleware

## Components
1. **Views**
   - LandingPageView
   - HealthCheckView
2. **Middleware**
   - RateLimitMiddleware
   - SecurityHeadersMiddleware
3. **Utilities**
   - Logger configuration
   - API client base class
   - Rate limit helper functions

## Questions
1. Do we need any analytics tracking on the landing page?
2. Should rate limits be configurable via environment variables?
