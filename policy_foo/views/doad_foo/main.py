"""
Agent responsible for synthesizing a final answer from extracted policy content.

This acts as the 'Synthesizer' agent in the DOAD workflow.
"""

"""
Workflow:
1. Receives concatenated XML string (containing extracted information from relevant DOADs) and the original user query/conversation history from the orchestrator (`doad_foo/__init__.py`).
2. Loads the system prompt from `policy_foo/prompts/doad_foo/main.md` (or a dedicated synthesizer prompt).
    - Replaces the `{POLICY_CONTENT}` placeholder in the system prompt with the concatenated XML string.
3. Constructs the messages payload for the final synthesis LLM call, including:
    - The formatted system prompt.
    - The user query and conversation history.
4. Sends the synthesis request to the LLM service (`core/services/open_router_service.py`).
5. Receives the final synthesized response string from the LLM.
6. Returns the final assistant message back to the orchestrator (`doad_foo/__init__.py`).

Note: Parsing of the final LLM response is handled by the frontend.
"""
