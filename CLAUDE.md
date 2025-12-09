# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CAF-GPT is a FastAPI-based AI email agent platform that processes incoming emails and generates AI-powered responses. The system uses a multi-agent architecture with specialized agents for different domains (policy questions, feedback note generation). It connects to IMAP for reading emails, uses OpenRouter for LLM integration, and S3-compatible storage for document retrieval.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running the Application
Leroy jinkins
We push to main.
Run the test and be sure of your work. This is a hobby app. we debug on the main branch.

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_email.py

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=src
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Type checking with mypy
mypy src/

# Check formatting without making changes
black --check src/ tests/
```

## Architecture Overview

### Multi-Agent System

The system uses a coordinator pattern with specialized agents:

1. **AgentCoordinator** (`src/agents/agent_coordinator.py`) - Main orchestrator that:
   - Routes emails to appropriate agents based on recipient address
   - Handles iterative LLM conversation loops (e.g., research requests, rank requests)
   - Parses XML responses and manages agent workflows
   - Appends standard signatures to all agent replies

2. **Prime Foo Agent** (policy agent) - Handles policy-related questions:
   - Triggered by emails to `policy@caf-gpt.com`
   - Can make research requests to sub-agents (e.g., LeaveFooAgent)
   - Supports iterative workflow: prime_foo → research request → sub-agent → prime_foo → reply
   - Model configured via `LLM__PRIME_FOO_MODEL` env var

3. **Feedback Note Agent** (`src/agents/feedback_note_agent.py`) - Generates performance feedback notes:
   - Triggered by emails to `pacenote@caf-gpt.com`
   - Implements circuit breaker pattern (max 3 LLM calls per email)
   - Uses rank-based competency documents from S3 (cpl.md, mcpl.md, sgt.md, wo.md)
   - Supports iterative workflow: initial request → rank request → competencies loaded → feedback generated
   - Model configured via `LLM__PACENOTE_MODEL` env var

4. **Sub-agents** (`src/agents/sub_agents/`) - Specialized research agents:
   - **LeaveFooAgent** - Handles leave policy queries by retrieving documents from S3
   - Each sub-agent has its own LLM model configuration

### Email Processing Flow

```text
IMAP Inbox → SimpleEmailProcessor → AgentCoordinator → [Prime Foo | Feedback Note] → SMTP Reply
                                                               ↓
                                                          Sub-agents (if needed)
                                                               ↓
                                                          DocumentRetriever (S3)
```

**Key Components:**

- **SimpleEmailProcessor** (`src/email_code/simple_email_handler.py`) - Main email loop:
  - Polls IMAP inbox every N seconds (configured via `EMAIL__EMAIL_PROCESS_INTERVAL`)
  - Processes unseen emails oldest-first
  - Routes to appropriate agent based on recipient email address
  - Handles email threading (In-Reply-To, References headers)
  - Marks emails as read only after successful processing

- **IMAPConnector** (`src/email_code/imap_connector.py`) - Low-level IMAP operations using imap_tools library

- **EmailSender** (`src/email_code/components/email_sender.py`) - Handles SMTP for sending replies

- **EmailThreadManager** (`src/email_code/components/email_thread_manager.py`) - Manages email threading headers

### Prompt Management

- **PromptManager** (`src/agents/prompt_manager.py`):
  - Loads agent prompts from `src/agents/prompts/*.md` files
  - Implements LRU-style caching (max 32 prompts)
  - Supports placeholder replacement (e.g., `{{leave_policy}}` in prompts)
  - Available prompts: `prime_foo.md`, `feedback_notes.md`, `leave_foo.md`

### Storage Layer

- **DocumentRetriever** (`src/storage/document_retriever.py`):
  - Provides read-only access to S3-compatible storage
  - Organized by category and filename: `s3://bucket/category/filename`
  - Categories: `leave/`, `paceNote/`
  - Used by agents to fetch policy documents and competency frameworks

### Configuration

Configuration uses Pydantic Settings with nested structure (`src/config.py`):

- **EmailConfig**: IMAP/SMTP settings
- **LLMConfig**: OpenRouter API key and model selection per agent
- **StorageConfig**: S3-compatible storage configuration
- **LogConfig**: Logging level

Environment variables use double underscore nesting:
```bash
EMAIL__IMAP_HOST=imap.example.com
LLM__PRIME_FOO_MODEL=google/gemini-3-pro-preview
LLM__PACENOTE_MODEL=anthropic/claude-haiku-4.5
STORAGE__S3_BUCKET_NAME=policies
```

### XML Response Format

Agents use XML for structured responses:

**Prime Foo Agent:**
```xml
<no_response />

<reply>
  <body>Response text here</body>
</reply>

<research>
  <sub_agent name="leave_foo">
    <query>What is the leave policy for...?</query>
  </sub_agent>
</research>
```

**Feedback Note Agent:**
```xml
<no_response />

<reply>
  <body>Feedback note text here</body>
</reply>

<rank>mcpl</rank>
```

The XML parsing logic is unified in `AgentCoordinator._parse_xml_response()` with fallback string parsing for malformed XML.

## Important Patterns and Conventions

### Agent Routing

Emails are routed to agents based on recipient address (`src/config.py:should_trigger_agent()`):
- `policy@caf-gpt.com` → Prime Foo Agent (policy questions)
- `pacenote@caf-gpt.com` → Feedback Note Agent (performance feedback)
- Other recipients → marked as read without processing

### Error Handling

- Emails with processing errors are left unread for retry on next poll
- Circuit breaker pattern in FeedbackNoteAgent prevents infinite LLM loops
- Generic error responses use `AgentResponse.error` field
- All S3 errors are logged but gracefully handled

### Thread Safety

`SimpleEmailProcessor` uses threading.Lock to ensure only one processing loop runs at a time, preventing race conditions with IMAP state.

### Logging

Structured logging throughout with contextual info:
```python
logger.info(f"[uid={uid}] Processing email through {agent_type} agent pipeline")
```

### Testing

Tests use pytest with fixtures for mocking:
- Email components tested with mock IMAP/SMTP
- Agent logic tested with mock LLM responses
- Configuration tested with environment variable overrides

## Common Development Patterns

### Adding a New Sub-Agent

1. Create agent class in `src/agents/sub_agents/your_agent.py`
2. Implement `research(query: str) -> str` method
3. Register in `AgentCoordinator._load_sub_agents()`
4. Add prompt file in `src/agents/prompts/your_agent.md`
5. Add model config in `LLMConfig` (optional)

### Adding Documents to S3

Documents are organized by category:
```text
s3://bucket-name/
  leave/
    leave_policy_2025.md
  paceNote/
    cpl.md
    mcpl.md
    sgt.md
    wo.md
    examples.md
```

Access via: `document_retriever.get_document("category", "filename.md")`

### Modifying Email Processing Logic

Email processing flow is in `SimpleEmailProcessor.process_unseen_emails()`. Key steps:
1. Fetch unseen emails (sorted oldest-first)
2. Parse email data
3. Route to agent coordinator
4. Build threading headers for reply
5. Send reply via EmailSender
6. Mark as read only on success

### Working with Prompts

Prompts support placeholder replacement:
```python
prompt = prompt_manager.get_prompt("leave_foo")
prompt = prompt.replace("{{leave_policy}}", policy_content)
```

Always use PromptManager rather than reading files directly - it provides caching and fallback handling.
