# OpenHands Instructions

## Development Philosophy
- Simplicity : Maintain minimal, straightforward design
- Learning Focus : Prioritize understanding over complexity
- Iterative Development : Build incrementally

## Project Structure
- This is a FastAPI-based AI email agent platform (CAF GPT)
- Main entry point: `src/main.py`
- Key components:
  - `src/agents/` - AI Agents logic
  - `src/email_code/` - Email handling (IMAP/SMTP)
  - `src/storage/` - S3 storage interface
  - `src/config.py` - Configuration via Pydantic
  - `src/llm_interface.py` - LLM interface

#### Architecture
- FastAPI application with async/await support
- Modular design with clear separation of concerns
- Configuration via environment variables and Pydantic settings

#### Coding Standards
- Use type hints and Pydantic models for data validation
- Follow FastAPI best practices for route definitions
- Use async/await for I/O operations
- Implement proper error handling and logging
- Security: No hardcoded secrets, use environment variables
- Logging: Use structlog for structured logging
