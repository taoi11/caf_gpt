# DOAD Foo Handler

Handles policy questions specifically related to the Defence Administrative Orders and Directives (DOADs) policy set.

## Workflow Orchestration

The main orchestration logic resides in `policy_foo/views/doad_foo/__init__.py`. It coordinates the following specialized agents:

1. **Finder (`finder.py`):** Identifies relevant DOAD document numbers based on the user query using an LLM call.
   - Analyzes user question to determine relevant policy areas
   - Returns specific DOAD numbers or "none" if no relevant documents found
   - Uses focused prompting to ensure accurate document identification

2. **Reader (`reader.py`):** For a given DOAD number, retrieves the document content from the database and uses an LLM call to extract relevant information (in XML format).
   - Multiple instances might be called by the orchestrator for different documents
   - Processes document content to extract only relevant sections
   - Formats extracted information in structured XML format
   - Handles error cases for missing or inaccessible documents

3. **Synthesizer (`main.py`):** Takes the collected XML snippets from the Reader(s) and the original query/history, then uses an LLM call to synthesize the final, user-facing answer.
   - Combines information from multiple documents when applicable
   - Maintains conversation context for follow-up questions
   - Formats responses with proper citations
   - Handles cases where no relevant information is found

## Interaction Flow

```
Router -> doad_foo/__init__.py (Orchestrator)
Orchestrator -> finder.py
finder.py -> LLM Service (OpenRouterService)
finder.py -> Orchestrator (returns DOAD numbers or "none")
Orchestrator -> reader.py (for each DOAD number)
reader.py -> Database Service (retrieves document content)
reader.py -> LLM Service (extracts relevant information)
reader.py -> Orchestrator (returns XML snippet)
Orchestrator -> main.py (Synthesizer) (with combined XML)
main.py -> LLM Service (generates final response)
main.py -> Orchestrator (returns final response)
Orchestrator -> Router
```

## Error Handling

- Graceful handling of missing documents
- Fallback strategies when no relevant documents are found
- Timeout management for LLM calls
- Proper error messaging for user feedback
- Integration with Cloudflare Turnstile for bot protection

## Performance Considerations

- Parallel processing of multiple documents when possible
- Caching of frequently accessed documents
- Optimized prompts to minimize token usage
