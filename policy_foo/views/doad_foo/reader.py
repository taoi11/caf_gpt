"""
Agent responsible for retrieving the content of a specific DOAD document and extracting relevant information using an LLM.
"""

"""
Workflow:
1. Receives a specific DOAD number (e.g., "1000-1") and the user query/conversation history from the orchestrator (`doad_foo/__init__.py`).
2. Calls the S3Service (`core/services/s3_service.py`) to retrieve the full text content of the specified DOAD.
  - Bucket: `policies` (or configured bucket)
  - Key: `doad/<DOAD_NUMBER>.md` (e.g., `doad/1001-1.md`)
3. Loads the system prompt template from `policy_foo/prompts/doad_foo/reader.md`.
4. Replaces the `{POLICY_CONTENT}` placeholder in the system prompt with the retrieved DOAD document content.
  - Note: Assumes the LLM can handle potentially long context from full documents.
5. Constructs the messages payload for the LLM service (`core/services/open_router_service.py`), including:
  - The formatted system prompt.
  - The user and assistant message pairs (conversation history).
6. Sends the request to the LLM service.
7. Receives a response string (expected to be loosely formatted XML containing relevant excerpts/info) from the LLM.
8. Returns the resulting XML string back to the orchestrator (`doad_foo/__init__.py`).
"""
