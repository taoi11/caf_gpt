# CAF GPT Platform

## Purpose
Collection of AI tools for Canadian Armed Forces personnel, providing specialized assistance for common administrative tasks through LLM technology.

## Tech Stack

### Backend
- Python 3.12
- Django 4.2
- PostgreSQL (Neon.tech serverless)
- Open Router API (Claude 3.5 Haiku)
- S3 storage (Storj)

### Frontend
- Bootstrap 5
- Vanilla JavaScript
- Responsive design

### Infrastructure
- NixOS development environment
- Docker for production deployment
- Environment-based configuration

## Application Structure

### Core App
Foundation module providing shared functionality across the platform:
- Base templates and static assets
- LLM integration services (OpenRouterService)
- Storage access (S3Service)
- Security middleware
- Health check endpoints

### PaceNote App
Tool for generating professional feedback notes for CAF members:
- Rank-specific competency integration
- Two-paragraph structured output
- System prompt templates with variable substitution
- Copy functionality and session storage

### Policy App (Planned)
Tool for policy document search and QA:
- Document search interface
- RAG implementation for context-aware answers
- Chat interface for policy questions

## Project Structure
```
caf_gpt/
├── caf_gpt/              # Django project settings
│   ├── settings/         # Environment-specific configs
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                 # Core app (foundation)
│   ├── services/         # Shared services
│   ├── templates/        # Base templates
│   └── static/           # Common static files
├── pacenote_foo/         # PaceNote generator
│   ├── services/         # Prompt handling
│   ├── prompts/          # Template storage
│   ├── templates/        # UI templates
│   └── static/           # App-specific assets
├── policy_foo/           # Policy tool
│   ├── templates/        # UI templates
│   └── static/           # App-specific assets
├── .ai/                  # Development documentation
│   └── notepad/          # Implementation notes
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── shell.nix            # Development environment
```

## Service Integrations

### Open Router API
- LLM access via OpenRouterService
- Model: Claude 3.5 Haiku
- Configurable parameters

### S3 Storage (Storj)
- Document retrieval for RAG
- Competency list storage
- Example storage
- Configuration via environment variables

## Application Features

### PaceNote Generator
- Professional feedback note generation
- Rank-specific competency integration (Cpl, MCpl, Sgt, WO)
- Two-paragraph formatted output
- Copy to clipboard functionality
- Session storage for input preservation

### Policy Tool (Planned)
- Document search capability
- Natural language policy questions
- Context-aware responses using RAG
- Citation of relevant documentation

## Development Workflow
- NixOS development environment
- Environment variables from .env file
- PostgreSQL connection via URL
- Hot-reload for templates and static files

## Deployment
- Docker containers
- Environment-based configuration
- PostgreSQL database connection
- S3-compatible storage integration

## Environment Configuration
Required environment variables:
- `DJANGO_SECRET_KEY`: Django security key
- `DJANGO_ENV`: Environment name (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `OPENROUTER_API_KEY`: LLM API authentication
- `AWS_ACCESS_KEY_ID`: S3 access credential
- `AWS_SECRET_ACCESS_KEY`: S3 secret credential
- `AWS_S3_ENDPOINT_URL`: S3 endpoint
