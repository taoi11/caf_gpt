# PolicyFoo App

## Purpose
LLM workflow for answering policy/regulation questions with citations from authoritative sources.

## Workflow
   1. User sends a question + `policy_set` parameter from the frontend
   2. Router receives the `user` message only as its the first message
   3. Router validates the `policy_set` parameter
   4. Router selects the appropriate `<policy_set>_foo` based on the `policy_set` and sends the `user` message to the `<policy_set>_foo`
   5. Router receives the `assistant` message from the `<policy_set>_foo`
   6. Router sends the `assistant` message to the frontend
   7. User sends a follow-up question + `policy_set` parameter from the frontend
   8. Router receives the `user` + `assistant` message sequence from the frontend
      - Accounts for long running conversations
   9. Router validates the `policy_set` parameter
   10. Router selects the appropriate `<policy_set>_foo` based on the `policy_set` and sends the `user` + `assistant` message sequence to the `<policy_set>_foo`
   ...

## Directory Structure
```
policy_foo/
├── views/
│   ├── __init__.py          # Exports views for easy importing
│   ├── router.py            # PolicyRouterView implementation
│   ├── rate_limits.py       # Checks for rate limits compliance
│   ├── doad_foo/            # DOAD policy handler
│   │   ├── README.md        # Documentation for DOAD_foo sub agents
│   │   ├── __init__.py      # Orchestration logic for DOAD handlers
│   │   ├── finder.py        # Identifies relevant DOAD documents
│   │   ├── reader.py        # Retrieves and processes document content
│   │   └── main.py          # Synthesizes final response
```

## Components

### Views
- **PolicyRouterView**: Main entry point for policy questions
  - Validates policy set parameters
  - Routes requests to appropriate policy handlers
  - Manages conversation history
  - Handles error cases

### Rate Limiting
- Implements shared rate limiting with core services
- Counts only final responses to users, not internal agent calls
- Configurable limits per policy set

### Policy Handlers
- Modular design with separate handlers for each policy set
- Currently implemented: DOAD (Defence Administrative Orders and Directives)
- Extensible architecture for adding new policy sets

## Integration Points
- Uses the shared base template from Core app
- Shares rate limiting approach with PaceNoteFoo
  * Increments rate limit usage for final message to user, not agent calls
- Uses `base` CSS and JS to maintain UI consistency
- Integrates with S3Service from core app for document storage
  * Each `<policy_set>_foo` makes S3 calls as needed
- Utilizes shared logging infrastructure
- Leverages OpenRouterService for LLM interactions

## Security Features
- Input validation and sanitization
- Rate limiting to prevent abuse
- Error handling with appropriate status codes
- CSP compliance