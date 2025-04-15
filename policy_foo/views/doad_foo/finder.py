"""
Defines the logic and interface for finding relevant DOAD documents or sections
based on the user's query.
"""

"""
Workflow:
1. Receives the user query and conversation history from main.py.
2. Dynamically formats the system prompt from `policy_foo/prompts/doad_foo/finder.md`.
  - Dynamically adds "{policies_table}" from the `policy_foo/prompts/doad_foo/DOAD-list-table.md`.
3. Maps the user and assistant messages to the user and assistant message sections of the LLM API Call.
4. Sends the formatted system message with user and assistant message pairs to `core/services/open_router_service.py`.
5. Receives the list of DOAD numbers from the LLM API.
  - Can be one or comma separated list of DOAD numbers or "none".
  - ex: 10001-1
  - ex: 10001-1,10002-1,10002-2
  - ex: none
6. If the result is "none", signals this back to `main.py`.
7. If DOAD numbers are received, triggers `reader.py` for each DOAD number, passing the DOAD number and the user query/conversation history.
Note: The parallel execution of multiple `reader.py` calls requires further planning and implementation (e.g., async handling).
"""