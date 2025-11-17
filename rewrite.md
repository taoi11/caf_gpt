# CAF-GPT Email Agent (Rewrite)

## Overview

This document outlines the architecture for rewriting the CAF-GPT email agent. The goal is to migrate away from chat and webui to a email based user interface while maintaining all existing functionality while adopting a "batteries included" Python approach with modern, well-supported libraries.

## Python Architecture

### Container Platform
**Docker** - The application will run as a containerized Python service, making it portable and easy to deploy on any cloud platform (AWS ECS, Google Cloud Run, Azure Container Instances, or self-hosted).

### Core Framework
**FastAPI** - Modern, fast (built on Starlette and Pydantic), with excellent async support and automatic API documentation. This will serve as the web framework for handling incoming webhooks and health checks.

---

## Email Module Architecture

Handles the inbound, composition and outbound of emails by this app.

### Email Service Provider
**Purelymail IMAP/SMTP** - Direct email access via standard protocols.

### Email Libraries (Batteries Included Approach)

#### 1. **imaplib** - Standard Library IMAP Client
- Handles connecting to Purelymail IMAP server
- Searches and fetches emails synchronously
- Deletes processed emails from inbox
- Simple search capabilities for finding unseen emails

#### 2. **smtplib** - Standard Library SMTP Client
- Sends reply emails via Purelymail SMTP
- Handles authentication and TLS
- Synchronous operation for blocking email sends

#### 3. **email (Python stdlib)** - Email Parsing and Composition
- `email.parser.BytesParser` - Parse raw MIME messages
- `email.message.EmailMessage` - Create properly formatted emails
- Built-in support for headers, multipart messages, and threading

#### 4. **mailparser (optional alternative)** - More Advanced Parsing
- If stdlib email parsing isn't sufficient
- Better handling of malformed emails
- More convenient API for extracting parts

### Email Component Structure

#### **EmailParser** (`src/email/components/email_parser.py`)
**Responsibility**: Parse raw email messages into structured data

**Key Functions**:
- `parse_email(raw_message: bytes) -> ParsedEmailData` - Parse raw MIME message
- `extract_recipients(parsed) -> EmailRecipients` - Extract to/cc/bcc
- `extract_email_address(address_header) -> List[str]` - Parse email addresses
- `validate_parsed_data(data) -> None` - Ensure required fields present

**Libraries Used**: Python stdlib `email` module or `mailparser`

#### **EmailThreadManager** (`src/email/components/email_thread_manager.py`)
**Responsibility**: Manage RFC 5322 compliant email threading

**Key Functions**:
- `build_threading_headers(original_message) -> ThreadingHeaders` - Create In-Reply-To and References headers
- `trim_references(references: str, max_length: int) -> str` - Keep references within limits
- `validate_message_id(message_id: str) -> bool` - Verify Message-ID format

**Libraries Used**: Python stdlib `email` module, regex for validation

#### **EmailComposer** (`src/email/components/email_composer.py`)
**Responsibility**: Compose properly formatted reply emails

**Key Functions**:
- `compose_reply(reply_data: ReplyData) -> EmailMessage` - Build complete email with headers
- `format_quoted_content(original_message) -> str` - Create attribution and quote original
- `format_subject(subject: str) -> str` - Add "Re:" prefix if needed
- `validate_reply_data(data) -> None` - Ensure all required fields present

**Libraries Used**: Python stdlib `email.message.EmailMessage`

#### **SimpleEmailHandler** (`src/email/simple_email_handler.py`)
**Responsibility**: Main orchestrator - coordinates parsing, AI processing, and replying

**Key Functions**:
- `process_email(raw_message: bytes) -> None` - Main entry point
- `send_reply_using_components(reply_data) -> None` - Send via SMTP
- `handle_processing_error(error) -> None` - Error recovery strategies
- `should_send_error_response(error) -> bool` - Determine if user should be notified

**Flow**:
1. Parse incoming email
2. Validate sender (prevent self-loops)
3. Extract email body and context
4. Call AgentCoordinator for AI processing
5. Build threading headers
6. Compose reply with quoted content
7. Send via SMTP
8. Handle errors gracefully
9. Delete processed email from inbox

**Libraries Used**: All email components + smtplib for sending

### Email Queue Processing Strategy

#### **EmailQueueProcessor** (`src/email/email_queue_processor.py`)
**Responsibility**: Treat inbox as a simple FIFO queue - process oldest email first, then delete it

**Queue Approach**:
- **Synchronous Processing Loop** - Simple synchronous loop that processes emails one at a time
  - Connect to IMAP server
  - Search for unseen emails (or all emails if no unseen available)
  - Sort by arrival date and process oldest first
  - Fetch and process each email synchronously
  - Delete email after successful processing
  - Sleep and repeat loop
- Converts inbox into a reliable queue with first-in-first-out semantics
- No concurrency for simplified logic and debugging

**Key Functions**:
- `start_queue_processing() -> None` - Begin synchronous processing loop
- `process_next_email() -> None` - Find and process oldest email in queue
- `get_oldest_email_id() -> str|None` - Search IMAP for oldest unseen email
- `fetch_and_process_email(email_id: str) -> None` - Fetch raw message, process via SimpleEmailHandler, delete
- `delete_email(email_id: str) -> None` - Mark as deleted and expunge to remove from inbox

**Libraries Used**: imaplib (stdlib), time (stdlib)

### Data Models (Pydantic)

**Purpose**: Type safety and validation using Pydantic models

**Models** (`src/email/types.py`):
- `ParsedEmailData` - Structured email data after parsing
- `EmailRecipients` - To, CC, BCC lists
- `ThreadingHeaders` - In-Reply-To, References
- `ReplyData` - All data needed to compose reply
- `EmailConfig` - Configuration for IMAP/SMTP

**Libraries Used**: Pydantic for data validation

---

## Agents Module Architecture

The agents module maintains the hierarchical AI architecture with coordinator and specialized sub-agents.

### AI Service Provider
**OpenRouter API** - Direct API calls

### AI Libraries

#### **requests** - HTTP Client
- Standard library HTTP client for synchronous operations
- Reliable, well-tested, batteries included
- Clean API for JSON requests
- Built-in timeout and retry support mechanisms

**Usage**: Call OpenRouter API endpoints

#### **pydantic-ai** or **langchain** (Optional)
- If we want a more structured agent framework
- For now, keeping it simple with direct API calls like the TS version

### Agent Component Structure

#### **BaseAgent** (`src/agents/base_agent.py`)
**Responsibility**: Base class with OpenRouter integration and logging

**Key Functions**:
- `call_openrouter(messages: List[Message], model: str, temperature: float) -> str` - Make LLM API calls
- `_build_request(...)` - Construct OpenRouter request payload
- `_handle_api_error(...)` - Handle API failures gracefully

**Libraries Used**: requests, pydantic for message models

#### **AgentCoordinator** (`src/agents/agent_coordinator.py`)
**Responsibility**: Orchestrate prime_foo and sub-agent interactions

**Key Functions**:
- `process_email_with_prime_foo(email_context: str) -> AgentResponse` - Main coordination loop
- `parse_prime_foo_response(response: str) -> PrimeFooResponse` - Parse XML response structure
- `handle_research_request(research) -> str` - Delegate to appropriate sub-agent
- `handle_no_response() -> AgentResponse` - Return no-reply indicator
- `get_generic_error_response() -> AgentResponse` - Fallback error message

**Flow**:
1. Send email context to prime_foo
2. Parse response for: `<no_response>`, `<research>`, or `<reply>`
3. If research needed, call sub-agent and send results back to prime_foo
4. Loop until prime_foo returns final reply or no_response
5. Return final response to email handler

**Libraries Used**: requests (via BaseAgent), xml parsing (stdlib or lxml)

#### **PromptManager** (`src/agents/prompt_manager.py`)
**Responsibility**: Load and manage system prompts

**Key Functions**:
- `get_prompt(prompt_name: str) -> str` - Load prompt from files
- `_load_from_filesystem(path) -> str` - Read prompt files
- `_cache_prompts()` - Cache in memory for performance

**Libraries Used**: Python stdlib (pathlib, functools.lru_cache)

#### **Sub-Agents** (`src/agents/sub_agents/`)

##### **LeaveFooAgent** (`leave_foo_agent.py`)
**Responsibility**: Answer leave policy questions using document retrieval

**Key Functions**:
- `research(request: ResearchRequest) -> str` - Main research function
- `_retrieve_leave_policy() -> str` - Fetch document from storage
- `_build_leave_foo_prompt(policy: str, question: str) -> List[Message]` - Construct prompt
- `_call_with_context(...)` - Call OpenRouter with policy context

**Libraries Used**: requests (via BaseAgent), document storage client

**Additional Sub-Agents**: Can add more agents following same pattern (e.g., TimesheetAgent, PayrollAgent, etc.)

### Data Models

**Models** (`src/agents/types.py`):
- `Message` - Single chat message (role, content)
- `AgentResponse` - Final response from coordinator
- `PrimeFooResponse` - Parsed prime_foo response (union type)
- `ResearchRequest` - Sub-agent research query
- `SubAgentQuery` - Individual research question

---

## Storage Module Architecture

### Document Storage Provider
**AWS S3 / MinIO / Cloudlfare-R2 Storage** - use any S3-compatible storage
**Read only** - This app needs read only access.

### Storage Libraries

#### **boto3** - AWS SDK for Python
- Industry standard for S3 interactions
- Works with Cloudflare R2 (S3-compatible)
- Works with MinIO and other S3-compatible stores
- Mature, well-documented, batteries included

### Storage Component Structure

#### **DocumentRetriever** (`src/storage/document_retriever.py`)
**Responsibility**: Fetch documents from object storage

**Key Functions**:
- `get_document(category: str, filename: str) -> str` - Retrieve document by category and name
- `_build_object_key(category, filename) -> str` - Construct S3 key
- `_fetch_from_s3(key: str) -> bytes` - Download from storage
- `_decode_content(content: bytes) -> str` - Convert to string

**Configuration**:
- Bucket name from environment
- S3 endpoint URL (for R2/MinIO compatibility)
- Access key and secret key
- Region (if applicable)

**Libraries Used**: aioboto3 or boto3

---

## Supporting Infrastructure

### Configuration Management

#### **pydantic-settings**
- Load configuration from environment variables
- Type-safe config with validation
- Support for .env files via python-dotenv
- Hierarchical config structure

**Config Structure** (`src/config.py`):
- `EmailConfig` - IMAP/SMTP settings
- `LLMConfig` - OpenRouter API settings
- `StorageConfig` - S3/R2 settings
- `AppConfig` - Top-level config aggregator

### Logging

#### **structlog** - Structured Logging
- JSON structured logs for better parsing
- Context binding (message_id, user, etc.)
- Better than stdlib logging for production
- Integration with cloud logging services

**Usage**:
- Logger.info("Processing email", from_addr=email.from, message_id=email.id)
- Automatic context propagation
- Performance timing with decorators

---

## Application Entry Point

### Main Application (`src/main.py`)

**FastAPI Application Structure**:

```
- Health check endpoint (GET /health)
- Background thread: EmailQueueProcessor running synchronous loop
- Graceful shutdown handling
```

**Initialization Flow**:
1. Load configuration from environment
2. Initialize logging
3. Create email queue processor instance
4. Start email processing loop in background thread (via FastAPI lifespan)
5. Start FastAPI server
6. Wait for health checks while processing emails in loop

**Deployment**: 
- Docker container with Python 3.11+
- Environment variables for secrets
- Health checks for orchestrator
- Auto-restart on failures

---

## Python Libraries Summary

### Core Framework
- **FastAPI** - Web framework for health checks
- **threading** (stdlib) - Background email processing thread

### Email Handling
- **imaplib** (stdlib) - Synchronous IMAP client for queue processing
- **smtplib** (stdlib) - Synchronous SMTP client for sending replies
- **email** (stdlib) - Parsing and composition
- **email-validator** - Email validation

### AI/Agent System
- **requests** - Synchronous HTTP for OpenRouter API
- **pydantic** - Data models and validation

### Storage
- **boto3** - S3-compatible storage client

### Infrastructure
- **pydantic-settings** - Configuration management
- **python-dotenv** - Load .env files
- **structlog** - Structured logging

### Development
- **pytest** - Testing framework
- **black** - Code formatting
- **mypy** - Static type checking

---

## Deployment Architecture

### Container Structure
```
Dockerfile:
- Python 3.12+ slim base image
- Install dependencies via requirements.txt
- Copy source code
- Expose health check port
- Run main.py as entrypoint
```

### Environment Variables
- `IMAP_HOST`, `IMAP_PORT`, `IMAP_USERNAME`, `IMAP_PASSWORD`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `OPENROUTER_API_KEY`
- `S3_BUCKET_NAME`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- `AGENT_EMAIL` - The bot's email address
- `EMAIL_PROCESS_INTERVAL` - Seconds between queue processing checks (default: 30)
- `DELETE_AFTER_PROCESS` - Whether to delete emails after processing (default: true)
- `DEV_MODE` - Enable debug logging

### Deployment Targets
- **Docker Compose** - Self-hosted on any VPS
- **Fly.io** - Managed Containers. ( future plans )

### Scaling Considerations
- Single container handles IMAP monitoring + processing
- Hobby project, very low user cunt
- For now: Stateless, ephemeral, simple deployment
