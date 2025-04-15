"""
Implements the main handler logic for the DOAD policy set.
Coordinates the finder and reader components, interacts with the LLM service,
and formulates the final assistant response with citations for the router.
"""

"""
Workflow:
1. Receives the user query and conversation history from the PolicyRouterView.
2. Calls the 'finder' component (finder.py) with the user query and conversation history.
3. Receives either a list of DOAD numbers or a "none" signal from `finder.py`.
4. If "none" is received from `finder.py`:
    - Skips LLM synthesis steps.
    - Formulates a standard "No relevant policy documents found" message.
    - Returns this message to the PolicyRouterView.
5. If DOAD numbers are received:
    - Waits to receive XML result strings from the `reader.py` instance(s) triggered by `finder.py`.
    - Concatenates all received XML strings from the `reader.py` calls into one larger string.
6. Loads the system prompt from `policy_foo/prompts/doad_foo/main.md`.
    - Replaces the `{POLICY_CONTENT}` placeholder in the system prompt with the concatenated XML string.
    - Constructs the messages payload for the final synthesis LLM call (system prompt + user query/history).
    - uses `core/services/open_router_service.py` for LLM API calls.
7. Sends the synthesis request to the LLM service.
8. Receives the final synthesized response string from the LLM.
9. Returns the final assistant message back to the PolicyRouterView.

Note: Parsing of the final LLM response (potentially containing XML or other
structured data) for frontend display is handled separately (planning TBD).
"""