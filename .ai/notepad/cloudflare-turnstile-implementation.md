# Cloudflare Turnstile Implementation Plan

## Overview
This document outlines the implementation of Cloudflare Turnstile to protect LLM API endpoints from bot abuse while maintaining an invisible user experience. The implementation replaces the existing IP-based rate limiting system with Turnstile's superior bot protection.

## Goals
- **Primary**: Prevent bot abuse of LLM API calls to control costs
- **Secondary**: Maintain invisible user experience (no visible CAPTCHAs)
- **Tertiary**: Handle multiple API submissions from the same user session

## Implementation Strategy

### 1. Backend Integration
- **TurnstileService**: Core service class for token validation with Cloudflare API
- **API View Updates**: Replace rate limiting middleware with Turnstile token validation
- **Django Settings**: Add Turnstile configuration (site key, secret key, CSP updates)

### 2. Frontend Integration
- **Invisible Widgets**: Use Turnstile's invisible mode for seamless UX
- **Hybrid Token Strategy**: Generate fresh tokens for each API call to handle multiple submissions
- **TurnstileManager**: JavaScript class to manage token lifecycle and API interactions

### 3. Security Considerations
- **Token Freshness**: Each API call gets a new token to prevent replay attacks
- **Error Handling**: Graceful fallbacks when Turnstile fails to initialize
- **CSP Updates**: Allow Cloudflare domains for script loading and API calls

## Technical Architecture

### Backend Components

#### TurnstileService (`core/services/turnstile_service.py`)
```python
class TurnstileService:
    def validate_token(self, token: str, remote_ip: str = None) -> bool
    def _make_verification_request(self, token: str, remote_ip: str = None) -> dict
```

#### Turnstile Utilities (`core/utils/turnstile_utils.py`)
```python
def validate_turnstile_token(request) -> tuple[bool, str]
```

#### API View Integration
- Replace `@ratelimit` decorators with Turnstile token validation
- Extract `turnstile_token` from request body
- Return appropriate error messages for validation failures

### Frontend Components

#### TurnstileManager (`core/static/core/js/turnstile.js`)
```javascript
class TurnstileManager {
    constructor(siteKey)
    async getToken() -> Promise<string>
    isInitialized() -> boolean
}
```

#### Application Integration
- **PaceNotes**: Updated `generatePaceNote()` to include Turnstile token
- **Policy Chat**: Updated `sendMessageToBackend()` to include Turnstile token

## Configuration

### Environment Variables
```bash
TURNSTILE_SITE_KEY=your_site_key_here
TURNSTILE_SECRET_KEY=your_secret_key_here
```

### Django Settings
```python
TURNSTILE_SITE_KEY = os.getenv('TURNSTILE_SITE_KEY')
TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY')

# CSP Updates
CSP_SCRIPT_SRC = [..., 'https://challenges.cloudflare.com']
CSP_CONNECT_SRC = [..., 'https://challenges.cloudflare.com']
```

## Implementation Phases

### Phase 1: Core Service ✅
- [x] Create TurnstileService class
- [x] Add Django settings configuration
- [x] Update CSP for Cloudflare domains
- [x] Create utility functions for token validation

### Phase 2: Backend Integration ✅
- [x] Update PaceNoteGeneratorView to use Turnstile validation
- [x] Update PolicyRouterView to use Turnstile validation
- [x] Remove rate limiting views and URL patterns
- [x] Clean up rate limiting service references

### Phase 3: Frontend Integration ✅
- [x] Add Turnstile script to base template
- [x] Create TurnstileManager JavaScript class
- [x] Update PaceNotes JavaScript to use Turnstile tokens
- [x] Update Policy Chat JavaScript to use Turnstile tokens
- [x] Remove rate limiting UI components

### Phase 4: Finalization 🔄
- [x] Commit all changes to feature branch
- [ ] Test implementation with actual Turnstile keys
- [ ] Deploy to staging environment
- [ ] Monitor for bot activity reduction

## Token Management Strategy

### Hybrid Approach
The implementation uses a "hybrid" token management strategy:

1. **Invisible Widgets**: Turnstile widgets are rendered invisibly on page load
2. **Fresh Tokens**: Each API call generates a new token via `turnstile.execute()`
3. **Automatic Refresh**: Tokens are refreshed automatically when expired
4. **Error Recovery**: Graceful handling of token generation failures

### Multiple Submissions Handling
For scenarios like generating multiple pace notes from the same input:
- Each submission gets a fresh token
- No token reuse between API calls
- Prevents token exhaustion issues
- Maintains security against replay attacks

## Error Handling

### Backend Errors
- **Invalid Token**: Return 400 with "Invalid security token" message
- **Turnstile API Failure**: Return 500 with "Security verification failed" message
- **Missing Token**: Return 400 with "Security token required" message

### Frontend Errors
- **Turnstile Not Loaded**: Display "Please refresh the page" message
- **Token Generation Timeout**: Display "Security verification failed" message
- **Network Errors**: Display standard connection error messages

## Testing Strategy

### Manual Testing
1. **Normal Usage**: Verify API calls work with valid tokens
2. **Bot Simulation**: Test with automated requests (should be blocked)
3. **Multiple Submissions**: Test rapid successive API calls
4. **Error Scenarios**: Test with invalid/missing tokens

### Monitoring
- Monitor Turnstile dashboard for challenge statistics
- Track API error rates for Turnstile-related failures
- Monitor LLM API costs for reduction in bot traffic

## Migration Notes

### Removed Components
- `RateLimitService` class and related functionality
- Rate limiting views (`RateLimitsView`) in both apps
- Rate limiting URL patterns
- Rate limiting JavaScript and CSS files
- Rate limiting UI components in templates

### Preserved Components
- CSRF protection (still required)
- Cost tracking functionality
- User input validation
- Error handling patterns

## Security Benefits

### Over IP Rate Limiting
1. **Bot Detection**: Advanced ML-based bot detection vs simple IP counting
2. **Distributed Attacks**: Protects against distributed bot networks
3. **Legitimate Users**: Doesn't penalize users behind shared IPs (offices, cafes)
4. **Adaptive**: Cloudflare's system adapts to new bot patterns automatically

### Implementation Security
1. **Token Freshness**: New token per request prevents replay attacks
2. **Server Validation**: All tokens validated server-side with Cloudflare
3. **No Client Trust**: Frontend cannot bypass security checks
4. **Invisible Mode**: No user friction while maintaining protection

## Future Enhancements

### Potential Improvements
1. **Analytics Integration**: Track bot attempt statistics
2. **Adaptive Challenges**: Use visible challenges for suspicious traffic
3. **Rate Limiting Hybrid**: Combine with light rate limiting for additional protection
4. **Custom Rules**: Implement custom Turnstile rules based on usage patterns

### Monitoring and Alerting
1. **High Bot Activity**: Alert when bot attempts spike
2. **Turnstile Failures**: Alert when validation service is down
3. **Cost Monitoring**: Track LLM API cost reduction
4. **User Experience**: Monitor for legitimate user blocks

## Conclusion

This implementation provides robust bot protection while maintaining a seamless user experience. The hybrid token strategy ensures security without compromising functionality for legitimate users making multiple API calls. The invisible Turnstile widgets provide enterprise-grade bot protection without the friction of traditional CAPTCHAs.