# CAF GPT

A FastAPI-based AI email agent platform.

## Features

- **Email Processing**: Connects to IMAP to read emails and SMTP to send replies.
- **LLM Integration**: Uses OpenRouter for AI responses.
- **Agents**: Specialized agents for different tasks (e.g., PolicyFoo, PaceNoteFoo).
- **Storage**: S3-compatible storage for documents.

## Project Structure

```
src/
├── agents/               # AI Agents logic
├── email_code/           # Email handling (IMAP/SMTP)
├── storage/              # S3 storage interface
├── config.py             # Configuration via Pydantic
├── main.py               # FastAPI entry point
└── llm_interface.py      # LLM interface
```

## Environment Variables

See `.env` for configuration options.
Key variables:
- `EMAIL__IMAP_HOST`, `EMAIL__IMAP_USERNAME`, `EMAIL__IMAP_PASSWORD`
- `EMAIL__SMTP_HOST`, `EMAIL__SMTP_USERNAME`, `EMAIL__SMTP_PASSWORD`
- `LLM__OPENROUTER_API_KEY`
- `STORAGE__S3_BUCKET_NAME`, `STORAGE__S3_ACCESS_KEY`, `STORAGE__S3_SECRET_KEY`

## Running

### Docker

```bash
docker-compose up --build
```

### Local

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```
