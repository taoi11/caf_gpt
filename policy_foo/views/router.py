"""Contains the main PolicyRouterView which acts as the central entry point for incoming chat requests.

Workflow:
1. Receives incoming chat requests (POST) containing user messages and potentially conversation history.
2. Extracts the 'policy_set' parameter from the request data.
3. Validates the 'policy_set' parameter against a predefined list of supported policy sets.
4. If validation fails, returns an error response.
5. Dynamically imports and instantiates the appropriate handler view based on the validated 'policy_set'.
6. Forwards the request (including messages and other relevant data) to the selected handler's 'post' method.
7. Receives the response (typically the assistant's message or an error) from the handler.
8. Relays the handler's response back to the original client (frontend).
9. Handles potential errors during handler instantiation or execution.

Note: Rate limiting is expected to be handled before this view or within the specific policy set handlers, not directly in the router itself.
"""
