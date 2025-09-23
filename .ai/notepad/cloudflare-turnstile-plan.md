# Cloudflare Turnstile Implementation Plan

## Overview

This plan outlines the implementation of Cloudflare Turnstile to protect LLM API endpoints from bot abuse while maintaining an invisible user experience. The solution will integrate with the existing rate limiting system and protect the two main LLM API endpoints.

## Current State Analysis

### Protected Endpoints
1. **PaceNote Generator**: `/pacenote/api/generate-pace-note/` (POST)
2. **Policy Chat**: `/policy/api/chat/` (POST)

### Current Protection Mechanisms
- IP-based rate limiting (hourly/daily limits) - **TO BE REMOVED**
- CSRF exemption on API endpoints
- Basic input validation

### Vulnerabilities
- No bot detection mechanism
- Rate limits can be bypassed with IP rotation
- No protection against automated browser tools
- API endpoints are publicly accessible without human verification

## Cloudflare Turnstile Integration Strategy

### 1. Invisible Turnstile Implementation

**Approach**: Use Cloudflare Turnstile's "invisible" mode to verify users without showing a challenge UI.

**Benefits**:
- Zero friction for legitimate users
- Effective bot detection
- Integrates with Cloudflare's global threat intelligence
- Minimal performance impact

### 2. Architecture Design

#### Frontend Integration
- Add Turnstile widget to pages containing LLM API forms
- Configure invisible mode with automatic challenge execution
- Implement token retrieval and submission with API calls
- Handle token expiration and refresh scenarios

#### Backend Validation
- Create Turnstile validation service in `core/services/`
- Integrate validation into existing API views
- Implement token verification before rate limit checks
- Add proper error handling and logging

#### Security Layers (Simplified)
```
User Request → Turnstile Validation → LLM API Call
```

**Note**: IP-based rate limiting will be removed as Turnstile provides superior bot protection.

### 3. Implementation Components

#### A. Turnstile Service (`core/services/turnstile_service.py`)
- Token validation against Cloudflare API
- Error handling and retry logic
- Caching for performance optimization
- Configuration management

#### B. Middleware Integration
- Optional: Create middleware for automatic Turnstile validation
- Apply to specific URL patterns
- Bypass for health checks and static content

#### C. Frontend JavaScript
- Turnstile widget initialization
- Token management and refresh
- API call integration
- Error handling and user feedback

#### D. Template Updates
- Add Turnstile script inclusion
- Widget placement in forms
- Progressive enhancement approach

### 4. Configuration Management

#### Environment Variables
```
TURNSTILE_SITE_KEY=<public_site_key>
TURNSTILE_SECRET_KEY=<secret_key>
```

**Note**: Using Turnstile defaults for timeout and always-enabled approach for simplicity.

#### Settings Integration
- Add Turnstile settings to Django settings
- Environment-specific configuration (dev/prod)

### 5. Implementation Phases

#### Phase 1: Core Service Development
- [ ] Create `TurnstileService` class
- [ ] Implement token validation logic
- [ ] Add configuration management
- [ ] Create unit tests

#### Phase 2: Backend Integration
- [ ] Update PaceNote API view with Turnstile validation
- [ ] Update Policy API view with Turnstile validation
- [ ] Remove existing IP-based rate limiting code
- [ ] Implement proper error responses
- [ ] Add logging and monitoring

#### Phase 3: Frontend Integration
- [ ] Add Turnstile script to base templates
- [ ] Implement hybrid token management (initial + per-request)
- [ ] Update API call functions for multiple submissions
- [ ] Add error handling UI

#### Phase 4: Documentation
- [ ] Documentation updates

### 6. Technical Implementation Details

#### Turnstile Token Management Strategy

**Hybrid Approach**: Initial token on page load + fresh token per API call

```javascript
// Token management for multiple submissions
class TurnstileManager {
    constructor(siteKey) {
        this.siteKey = siteKey;
        this.widgetId = null;
        this.init();
    }
    
    init() {
        // Create invisible widget
        this.widgetId = turnstile.render('#turnstile-container', {
            sitekey: this.siteKey,
            size: 'invisible',
            callback: (token) => {
                // Token ready - can be used immediately
                console.log('Token ready');
            }
        });
    }
    
    async getToken() {
        // Always get fresh token for each API call
        return new Promise((resolve, reject) => {
            turnstile.reset(this.widgetId);
            turnstile.execute(this.widgetId, {
                callback: resolve,
                'error-callback': reject
            });
        });
    }
}

// Usage in API calls
async function submitPaceNote() {
    try {
        const token = await turnstileManager.getToken();
        const response = await fetch('/pacenote/api/generate-pace-note/', {
            method: 'POST',
            headers: {
                'CF-Turnstile-Token': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        // Handle response...
    } catch (error) {
        console.error('Turnstile or API error:', error);
    }
}
```

#### Multiple Submission Handling

**Key Benefit**: Users can click submit multiple times (e.g., generate multiple pace notes) and each submission gets a fresh, valid token.

```javascript
// Example: Multiple pace note generations
document.getElementById('generate-btn').addEventListener('click', async () => {
    // Each click gets a fresh token - perfect for multiple submissions
    await submitPaceNote();
});

// User can click multiple times rapidly - each gets its own validation
```

#### Backend Validation Flow (Simplified)
```python
def validate_turnstile_token(request):
    token = request.headers.get('CF-Turnstile-Token')
    if not token:
        return False, 'Missing Turnstile token'
    
    # Validate with Cloudflare (no rate limiting needed)
    is_valid, error = turnstile_service.verify_token(token, request.META.get('REMOTE_ADDR'))
    return is_valid, error

# Updated API view (example)
def post(self, request, *args, **kwargs):
    # Only Turnstile validation needed
    is_valid, error = validate_turnstile_token(request)
    if not is_valid:
        return JsonResponse({'error': error}, status=400)
    
    # Proceed with LLM API call
    result = generate_pace_note(user_input, rank)
    return JsonResponse(result)
```

### 7. Error Handling Strategy

#### Client-Side Errors
- Network failures during token generation
- Token expiration
- Turnstile service unavailable

#### Server-Side Errors
- Invalid tokens
- Cloudflare API failures
- Rate limiting after Turnstile validation

#### User Experience
- Graceful degradation when Turnstile fails
- Clear error messages
- Retry mechanisms
- Fallback to rate limiting only (configurable)

### 8. Security Considerations

#### Token Security
- Tokens are single-use and time-limited
- Server-side validation prevents token reuse
- IP address binding for additional security

#### Privacy
- Minimal data collection
- GDPR compliance considerations
- User consent handling

#### Performance
- Async token validation
- Caching of validation results
- Timeout handling

### 9. Monitoring and Analytics

#### Metrics to Track
- Turnstile challenge success/failure rates
- Bot detection effectiveness
- API endpoint protection coverage
- Performance impact measurements

#### Logging Strategy
- Turnstile validation attempts
- Failed validations with reasons
- Performance metrics
- Security incidents

### 10. Deployment Strategy

#### Development Environment
- Use Turnstile test keys
- Enable debug logging
- Test with various scenarios

#### Production Rollout
- Feature flag controlled deployment
- Gradual rollout to percentage of users
- Monitor for issues
- Rollback plan ready

### 11. Maintenance and Updates

#### Regular Tasks
- Monitor Turnstile service health
- Update tokens and keys as needed
- Review bot detection effectiveness
- Performance optimization

#### Documentation
- API integration guide
- Troubleshooting documentation
- Security best practices
- Monitoring playbooks

## Success Criteria

1. **Bot Protection**: Significant reduction in automated API abuse
2. **User Experience**: No visible impact on legitimate users
3. **Performance**: < 100ms additional latency for API calls
4. **Reliability**: 99.9% uptime for Turnstile validation
5. **Monitoring**: Comprehensive visibility into protection effectiveness

## Risk Mitigation

### Technical Risks
- **Turnstile service outage**: Implement graceful degradation
- **False positives**: Provide manual override mechanisms
- **Performance impact**: Implement caching and async validation

### Business Risks
- **User friction**: Use invisible mode and thorough testing
- **Cost implications**: Monitor Turnstile usage and optimize
- **Compliance**: Ensure GDPR and privacy compliance

## Next Steps

1. Set up Cloudflare Turnstile account and obtain keys
2. Begin Phase 1 implementation with core service development
3. Create development environment for testing
4. Implement comprehensive test suite
5. Plan production deployment strategy

This plan provides a comprehensive approach to implementing Cloudflare Turnstile while maintaining the existing user experience and adding robust bot protection to the LLM API endpoints.