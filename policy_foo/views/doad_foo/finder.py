"""
Agent responsible for identifying relevant DOAD document numbers based on the user query and conversation history.
"""

"""
Workflow:
1. Receives the user query and conversation history from the orchestrator (`doad_foo/__init__.py`).
2. Dynamically formats the system prompt from `policy_foo/prompts/doad_foo/finder.md`.
  - Dynamically adds "{policies_table}" from the `policy_foo/prompts/doad_foo/DOAD-list-table.md`.
3. Maps the user and assistant messages to the user and assistant message sections of the LLM API Call.
4. Sends the formatted system message with user and assistant message pairs to `core/services/open_router_service.py`.
5. Receives the list of DOAD numbers from the LLM API.
  - Can be one or comma separated list of DOAD numbers or "none".
  - ex: 10001-1
  - ex: 10001-1,10002-1,10002-2
  - ex: none
6. Returns the resulting list of DOAD numbers (or "none") back to the orchestrator (`doad_foo/__init__.py`).
"""
