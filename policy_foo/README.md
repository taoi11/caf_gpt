# PolicyFoo App

## Purpose
LLM workflow for answering policy/regulation questions with citations from authoritative sources.

## Directory Structure
```
policy_foo/
├── models.py         # Policy document models
├── urls.py           # Policy URL configuration
├── views/            # Organized view modules
│   ├── router.py     # Policy routing logic
│   ├── rate_limits.py # Rate limiting checks
│   └── doad_foo/     # DOAD policy handler
│       ├── finder.py # Document finder
│       ├── reader.py # Document reader
│       └── main.py   # Response synthesizer
├── templates/        # Policy templates
├── static/           # Policy static files
└── prompts/          # Policy prompt templates
```

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
- Integrates Cloudflare Turnstile for bot protection

### Policy Handlers
- Modular design with separate handlers for each policy set
- Currently implemented: DOAD (Defence Administrative Orders and Directives)
- Extensible architecture for adding new policy sets

## Integration Points
- Uses the shared base template from Core app
- Uses `base` CSS and JS to maintain UI consistency
- Utilizes shared logging infrastructure
- Leverages OpenRouterService for LLM interactions

## Security Features
- Input validation and sanitization
- Error handling with appropriate status codes
- CSP compliance
- Cloudflare Turnstile integration for bot protection (see core/README.md for implementation details)
