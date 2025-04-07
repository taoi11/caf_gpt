# PolicyFoo App Specification

## Purpose
LLM workflow for answering policy/regulation questions with citations.

## Work flow
   1. user sends a question + `policy_set` parameter from the frontend
   2. router receives the `user` message only as its the first message
   3. router validates the `policy_set` parameter
   4. router selects the appropriate `<policy_set>_foo` based on the `policy_set` and sends the `user` message to the `<policy_set>_foo`
   5. router receives the `assistant` message from the `<policy_set>_foo`
   6. router sends the `assistant` message to the frontend
   7. user sends a follow-up question + `policy_set` parameter from the frontend
   8. router receives the `user` + `assistant` message sequence from the frontend
      - account for long running conversations
   9. router validates the `policy_set` parameter
   10. router selects the appropriate `<policy_set>_foo` based on the `policy_set` and sends the `user` + `assistant` message sequence to the `<policy_set>_foo`
   ...


## Directory Structure
```
policy_foo/
├── views/
│   ├── __init__.py          # Exports views for easy importing
│   ├── router.py            # PolicyRouterView implementation
│   ├── rate_limits.py       # checks for rate limits compliance
│   ├── doad_foo/            # Further organization for handlers
│   │   ├── READEME.md       # Documentation for DOAD_foo sub agents
│   │   ├── __init__.py      # Exports DOAD_foo views
│   │   ├── finder.py        # Base handler interface
│   │   ├── reader.py        # DOAD policy handler
│   │   ├── main.py          # DOAD main handler
```

## Integration Points
- Uses the shared base template from Core app
- Will share rate limiting approach with PaceNoteFoo
   * +1 the rate limit usage for final message to user not agent calls. 
- Use `base` css and js to keep the UI consistent
- Integrates with S3Service from core app for document storage
   * `<policy_set>_foo` will make the s3 calls as needed
- Utilizes shared logging infrastructure