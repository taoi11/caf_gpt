"""
Orchestrates the DOAD policy question-answering workflow.

Acts as the main entry point for the DOAD policy set, coordinating the
finder, reader, and synthesizer agents to generate a response based on
user queries and conversation history.
"""

"""
Workflow:
1. Receives the user query and conversation history from the PolicyRouterView (`policy_foo/views/router.py`).
2. Calls the 'finder' agent (`finder.py`) with the user query and conversation history.
3. Receives either a list of DOAD numbers or a "none" signal from `finder.py`.
4. If "none" is received from `finder.py`:
    - Skips reader and synthesizer steps.
    - Formulates a standard "No relevant policy documents found" message.
    - Returns this message to the PolicyRouterView.
5. If DOAD numbers are received:
    - For each DOAD number, calls the 'reader' agent (`reader.py`), passing the DOAD number and user query/history.
      - Note: Handles potential parallel execution/async calls to `reader.py` if needed.
    - Collects the XML result strings from all successful `reader.py` calls.
    - Concatenates all received XML strings into one larger string.
    - Calls the 'synthesizer' agent (`main.py`) with the concatenated XML string and the original user query/history.
6. Receives the final synthesized response string from the synthesizer agent (`main.py`).
7. Returns the final assistant message back to the PolicyRouterView.
"""
