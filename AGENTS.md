# CAF-GPT Development Guide

## Project Overview
CAF-GPT is a backend only email agent platform using a multi-agent coordinator pattern. The system polls IMAP, routes emails to specialized AI agents (policy questions, feedback notes), retrieves context from S3 storage, and sends AI-generated replies via SMTP.
FastAPI for healthy API endpoints.

## Essential Workflows
### Running & Testing
```bash
# Run locally (uses .env for config)
uvicorn src.main:app --reload

# Docker (preferred for production)
docker-compose up --build

# Tests (always run before pushing - we debug on main)
pytest -q                 # Run all tests
pytest -v                 # Verbose output
```

### Development Philosophy
- **"Leroy Jenkins - We push to main"**: This is a hobby app, direct commits to main are expected
- Always run tests before pushing to validate changes
- No staging/dev branch complexity - debug in production if needed

## Agent Architecture Patterns
### Email Routing
Emails route to agents based on **recipient address** (`src/config.py:should_trigger_agent()`):
- `agent@caf-gpt.com` → Prime Foo Agent (policy questions, can delegate to sub-agents)
- `pacenote@caf-gpt.com` → Prime Foo Agent with pacenote context (performance feedback with rank-based competencies)
  - Email context includes indicator: `[NOTE: This email was sent to pacenote@caf-gpt.com - the user wants a feedback note]`
  - Prime Foo delegates to PacenoteAgent sub-agent via `<feedback_note>` response
- Other addresses → marked as read, no processing

### Iterative Agent Workflow
**Prime Foo Agent** (`process_email_with_prime_foo`) uses **iterative XML response loops**:
- LLM returns `<reply>`, `<research>`, `<feedback_note>`, or `<no_response>`
- If `<research>`: delegate to sub-agent → send results back → LLM replies again
  - Sub-agents registered in `AgentCoordinator._load_sub_agents()`
  - Example: `<research><sub_agent name="leave_foo"><query>...</query></sub_agent></research>`
- If `<feedback_note>`: delegate to PacenoteAgent → send generated note back → LLM wraps in reply
  - Format: `<feedback_note rank="cpl">event context</feedback_note>`
  - PacenoteAgent loads competencies from S3 (`paceNote/{rank}.md`) and generates feedback
  - Rank files: `cpl.md`, `mcpl.md`, `sgt.md`, `wo.md`
- **Circuit breaker**: max 6 LLM calls per email to prevent infinite loops

### XML Parsing with Retry
All agents use `call_llm_with_retry()` pattern:
- Parse LLM response as XML
- On `XMLParseError`: send parse error back to LLM, retry once
- No more retries after first failure - raises exception for error handling

## Storage & Document Retrieval
S3 organization: `s3://bucket/category/filename`
- Categories: `leave/` (policy docs), `paceNote/` (rank competencies)
- Access via: `document_retriever.get_document("paceNote", "mcpl.md")`
- DocumentRetriever handles encoding detection (UTF-8 → ISO-8859-1 fallback)

## Adding New Agents/Sub-agents
1. Create agent class in `src/agents/sub_agents/your_agent.py`
2. Implement `research(query: str) -> str` method
3. Register in `AgentCoordinator._load_sub_agents()`:
   ```python
   self.sub_agents["your_agent"] = YourAgent(self.prompt_manager)
   ```
4. Add prompt file: `src/agents/prompts/your_agent.md`
5. (Optional) Add model config: `LLMConfig.your_agent_model`

## Code Quality Standards
### Formatting & Type Checking
```bash
black src/ tests/        # Format code (100 char line length)
mypy src/ --strict       # Type checking (Python 3.12)
```

### Testing Conventions
- Use pytest fixtures for mocking (`mock_llm_client`, `mock_prompt_manager`, `sample_mail_message`)
- Test agent logic with mock LLM responses (see `tests/test_feedback_note_agent.py`)
- Test email components with mock IMAP/SMTP (see `tests/test_email.py`)
- Circuit breaker tests verify max LLM call limits

## Email Processing Details
### Threading & Concurrency
- `SimpleEmailProcessor` uses `threading.Lock` to prevent IMAP race conditions
- Background thread polls every `EMAIL__EMAIL_PROCESS_INTERVAL` seconds (default: 30s)
- Processes emails **oldest-first** (sorted by UID)
- Marks email as read **only on success** - errors leave unread for retry

### Email Threading Headers
`EmailThreadManager` builds proper threading headers:
- `In-Reply-To`: original message-id
- `References`: all parent message-ids
- Ensures replies appear in same thread in email clients

### HTML Replies
Email templates use Jinja2 (`src/email_code/templates/reply.html.jinja`). `EmailComposer` builds HTML replies with proper structure.

## Important Gotchas
- **Prompts use caching**: `PromptManager` caches loaded prompts (LRU, max 32) - use its methods, don't read files directly
- **Signature appending**: `AgentCoordinator.SIGNATURE` is appended to all Prime Foo agent replies (includes GitHub link)
- **Error handling**: Emails with processing errors are left unread for retry, but logged for debugging
- **Path style S3**: Some S3-compatible services need `STORAGE__USE_PATH_STYLE_ENDPOINT=true`

## Python Comment Standards
This repository follows a strict commenting standard for **ALL** `.py` files (except simple `__init__.py` files that only re-export names).

### File-Level Comments (Required)
Every Python module must have a module docstring at the **very top** that:
1. Includes the file path (relative to repo root)
2. States the responsibility/purpose of the code in the file
3. Lists all top-level functions or classes

#### Example
```python
"""
src/utils/env_utils.py

Environment utilities helpers that centralize the runtime configuration helpers.

Top-level declarations:
- is_dev_mode: Check if the environment is configured for development
"""
```

## Function/Class Comments (Required)
Every top-level function or class must have inline # comments immediately after its definition that:
1. Expand on the short description from the module docstring
2. Provide additional context about its purpose or behavior
3. Minimum one line, maximum three lines

### Example
```python
def my_function():
    # Brief description expanding on the module docstring reference
    # Additional context about purpose or behavior
    ...
```

## Inline Comments (Minimal)
Minimize inline comments within functions. **Only add them when:**
1. Documenting a specific lesson learned
2. Explaining a non-obvious solution to a specific problem
3. Noting a workaround for a known issue

**Avoid:**
- Obvious comments that just restate what the code does
- Redundant comments that explain self-documenting code
- Excessive comments that clutter the code
