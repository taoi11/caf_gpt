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
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_email.py  # Specific file
```

### Development Philosophy
- **"Leroy Jenkins - We push to main"**: This is a hobby app, direct commits to main are expected
- Always run tests before pushing to validate changes
- No staging/dev branch complexity - debug in production if needed

## Agent Architecture Patterns

### Email Routing
Emails route to agents based on **recipient address** (`src/config.py:should_trigger_agent()`):
- `policy@caf-gpt.com` → Prime Foo Agent (policy questions, can delegate to sub-agents)
- `pacenote@caf-gpt.com` → Feedback Note Agent (performance feedback with rank-based competencies)
- Other addresses → marked as read, no processing

### Iterative Agent Workflow
Both main agents use **iterative XML response loops**:

1. **Prime Foo Agent** (`process_email_with_prime_foo`):
   - LLM returns `<reply>`, `<research>`, or `<no_response>`
   - If `<research>`: delegate to sub-agent → send results back → LLM replies again
   - Sub-agents registered in `AgentCoordinator._load_sub_agents()`
   - Example: `<research><sub_agent name="leave_foo"><query>...</query></sub_agent></research>`

2. **Feedback Note Agent** (`process_email`):
   - LLM returns `<reply>`, `<rank>`, or `<no_response>`
   - If `<rank>`: load competencies from S3 (`paceNote/{rank}.md`) → send to LLM → LLM generates feedback
   - **Circuit breaker**: max 3 LLM calls per email to prevent infinite loops
   - Rank files: `cpl.md`, `mcpl.md`, `sgt.md`, `wo.md`

### XML Parsing with Retry
All agents use `_call_llm_with_retry()` pattern:
- Parse LLM response as XML
- On `XMLParseError`: send parse error back to LLM, retry once
- No more retries after first failure - raises exception for error handling

## Configuration Patterns

### Pydantic Settings with Nested Env Vars
Use **double underscore** for nested config (`src/config.py`):
```bash
EMAIL__IMAP_HOST=imap.example.com
EMAIL__EMAIL_PROCESS_INTERVAL=30
LLM__PRIME_FOO_MODEL=google/gemini-3-pro-preview
LLM__PACENOTE_MODEL=anthropic/claude-haiku-4.5
LLM__LEAVE_FOO_MODEL=x-ai/grok-4.1-fast
STORAGE__S3_BUCKET_NAME=policies
```

Each agent can use a **different LLM model** via `LLMConfig` fields (`pacenote_model`, `prime_foo_model`, `leave_foo_model`).

### Global Singletons
- `llm_client` (`src/llm_interface.py`): Use for all LLM calls via OpenRouter
- `config` (`src/config.py`): Application-wide configuration
- All components reference these instead of creating instances

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
mypy src/                # Type checking (Python 3.12)
black --check src/       # Verify formatting without changes
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
