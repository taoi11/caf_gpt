# Core App

## Purpose
Foundation module providing shared functionality, services, and utilities across the CAF GPT platform.

## Key Components

### Views
- **LandingPageView**: Bootstrap landing with tool navigation
- **HealthCheckView**: JSON endpoint for monitoring/load balancers

### Services
- **OpenRouterService**: LLM integration via OpenRouter API
  - Request handling and error management
  - Response formatting and logging
  - Temperature and token control

- **S3Service**: S3-compatible storage access
  - File listing and retrieval
  - Error handling with custom exceptions
  - Configurable endpoints and credentials

### Middleware
- **SecurityHeadersMiddleware**: Response security headers
  - Content Security Policy
  - X-Content-Type-Options
  - X-Frame-Options
  - Referrer Policy

### Templates
- **base.html**: Main template with Bootstrap
  - Responsive navbar
  - Common footer
  - Block structure for app extensions

### Models
- **TimeStampedModel**: Abstract base with created/updated fields

## Usage Examples

### Services Integration
```python
from core.services import OpenRouterService, S3Service

# LLM generation
router_service = OpenRouterService()
completion = router_service.generate_completion(prompt)

# S3 file access
s3_service = S3Service(bucket_name="policies")
content = s3_service.read_file("path/to/file.md")
```

### Template Extension
```html
{% extends "core/base.html" %}
{% load static %}

{% block content %}
  <!-- App content -->
{% endblock %}

{% block extra_js %}
  <script src="{% static 'myapp/js/script.js' %}"></script>
{% endblock %}
```

## Error Handling
- Custom exceptions for S3 operations
- Logging for API interactions
- Graceful fallbacks for service failures
