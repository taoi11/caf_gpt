"""
The functionality of this module is to import the `RateLimitService` from the core app.

It sends a `+1` to the `RateLimitService` when the `Router` sends a message back to the front end.
`rate_limit_service.increment(ip)`
"""

"""
Workflow:
1. Triggered when the `Router` sends a message back to the front end.
2. The `RateLimitService` increments "+1" the rate limit for the given IP address.

Note: Does not include requests from the agent's intermediate messages, only for the final response that's sent to the user.
"""