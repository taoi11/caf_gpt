# DOAD Foo Handler

Handles policy questions specifically related to the Defence Administrative Orders and Directives (DOADs) policy set.

## Workflow Orchestration

The main orchestration logic resides in `policy_foo/views/doad_foo/__init__.py`. It coordinates the following agents:

1.  **Finder (`finder.py`):** Identifies relevant DOAD document numbers based on the user query using an LLM call.
2.  **Reader (`reader.py`):** For a given DOAD number, retrieves the document content from S3 and uses an LLM call to extract relevant information (in XML format). Multiple instances might be called by the orchestrator.
3.  **Synthesizer (`main.py`):** Takes the collected XML snippets from the Reader(s) and the original query/history, then uses an LLM call to synthesize the final, user-facing answer.

## Interaction Flow

`Router` -> `doad_foo/__init__.py` (Orchestrator)
Orchestrator -> `finder.py`
`finder.py` -> LLM Service
`finder.py` -> Orchestrator (returns DOAD numbers or "none")
Orchestrator -> `reader.py` (for each DOAD number)
`reader.py` -> S3 Service
`reader.py` -> LLM Service
`reader.py` -> Orchestrator (returns XML snippet)
Orchestrator -> `main.py` (Synthesizer) (with combined XML)
`main.py` -> LLM Service
`main.py` -> Orchestrator (returns final response)
Orchestrator -> `Router`
