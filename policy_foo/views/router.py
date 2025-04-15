"""Contains the main PolicyRouterView which acts as the central entry point for incoming chat requests.
"""

"""
Workflow:
1. Receives incoming requests from the frontend with user messages or user and assistant message pairs if not a new conversation.
2. Extracts the 'policy_set' parameter from the request data.
  - Only DOAD policy set is supported for now.
  - More policy sets can be added in the future.
3. Validates the 'policy_set' parameter against a predefined list of supported policy sets.
4. For `policy_set` = 'doad', it sends the user and assistant message pairs to the `doad_foo` `main.py` component.
"""