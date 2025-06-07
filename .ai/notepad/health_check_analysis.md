# Health Check Endpoint Analysis

## Current Status
- Health check endpoint is properly configured at `/health/` 
- URL routing is correct in `core/urls.py`
- View implementation in `core/views.py` returns proper JSON response
- Local testing shows 200 OK response with correct payload

## Potential Issues Identified

### 1. ALLOWED_HOSTS Configuration Issue
**Most Likely Cause**: In production (`prod.py`), `ALLOWED_HOSTS` is loaded from environment variable:
```python
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
```

If `ALLOWED_HOSTS` environment variable is not set correctly, Django will return 400 Bad Request for health checks from Fly.io.

### 2. Missing Fly.io Internal Host
Fly.io health checks come from internal infrastructure. The app needs to allow the internal Fly.io hostnames or IP addresses.

### 3. CSRF Middleware Interference
The `HealthCheckView` inherits from `TemplateView` which might be subject to CSRF checks, though GET requests typically aren't.

### 4. Security Headers
Production has strict security settings that might interfere with health checks.

## Recommended Solutions

### Priority 1: Fix ALLOWED_HOSTS
1. Add Fly.io internal hostnames to ALLOWED_HOSTS
2. Consider using wildcard for internal IPs
3. Add debug logging to see what Host header is being sent

### Priority 2: Simplify Health Check View
1. Change from TemplateView to simple function-based view
2. Bypass unnecessary middleware for health checks
3. Add more diagnostic information to response

### Priority 3: Add Health Check Debugging
1. Add logging to see incoming requests
2. Return more diagnostic info in development mode
