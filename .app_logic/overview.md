# Overview
A collection of AI tools and agents for army personnel, packaged as a Django application with NixOS support for development and Docker for production.

## Tech Stack
- Python 3.12
- Django 4.2
- PostgreSQL (Neon.tech serverless)
- Bootstrap 5
- NixOS development environment
- Docker for production deployment
- Open Router API for LLM integration (Claude 3.5 Haiku)
- S3-compatible storage (Storj) for data sources
- RAG (Retrieval Augmented Generation)

## Application Structure

### Django Apps
1. **core** - Base application with shared components
   - Landing page
   - Security headers middleware
   - Health check endpoint
   - Common utilities and base models
   - Open Router service for LLM integration
   - S3 client for storage access

2. **pacenote_foo** - PaceNoteFoo LLM workflow
   - Pace Notes generator interface
   - Client-side session storage
   - Rate limiting display
   - Bootstrap-based UI
   - API endpoint for generating pace notes
   - Prompt template handling

3. **policy_foo** - PolicyFoo LLM workflow
   - Policy document search interface (implemented)
   - Chat interface (planned)
   - RAG implementation (planned)
   - LLM integration (planned)

### Pages
1. **Landing Page** - Introduction and navigation to tools
2. **Pace Notes Tool** - Interface for generating pace notes based on observations
3. **Policy Documents** - Interface for browsing and searching policy documents
4. **Policy Chat** - Chat interface for policy questions (coming soon)

## Project Structure
```
caf_gpt/
├── caf_gpt/              # Main project settings
│   ├── settings/         # Settings configuration
│   │   ├── base.py       # Base settings
│   │   └── __init__.py   # Environment-specific settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                 # Core app
│   ├── services/         # Shared services
│   │   └── open_router_service.py  # LLM integration
│   └── utils/            # Utility functions
│       └── s3_client.py  # S3 storage access
│   └── templates/        # Core templates
│       └── base.html     # Base template
│   ├── static/           # Static files
│   │   └── css/         # CSS files
│   │   └── js/          # JavaScript files
├── pacenote_foo/         # PaceNote app
│   ├── services/         # App-specific services
│   │   └── prompt_service.py  # Prompt template handling
│   └── prompts/          # Prompt templates
│       └── base.md       # Base prompt template
│   └── templates/        # PaceNote templates
│       └── pacenote_foo.html  # PaceNote generator template
│   └── static/           # Static files
│       └── css/         # CSS files
│       └── js/          # JavaScript files
├── policy_foo/           # Policy app
│   └── templates/        # Policy templates
│       └── policy_foo.html  # Policy document search template
│   └── static/           # Static files
│       └── css/         # CSS files
│       └── js/          # JavaScript files
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── shell.nix            # NixOS development environment
```

## Features

### PaceNote Generator
- Generate professional feedback notes based on user observations
- Select rank to customize the competency list (currently Cpl/MCpl)
- Uses Claude 3.5 Haiku model for high-quality, consistent outputs
- Retrieves competency lists and examples from S3 storage
- Simulated rate limiting with UI indicators
- Copy to clipboard functionality
- Session storage for preserving user input

### Core Services
- Open Router integration for LLM access
- S3 client for retrieving data from storage
- Shared utilities and base models

## Development
- NixOS development environment via shell.nix
- Environment variables loaded from .env file
- PostgreSQL database connection via URL
- Local development without container rebuilds

## Deployment
- Docker containers for production deployment
- Environment variables for configuration
- Support for development and production environments
- Consistent deployment across different servers

## Environment Configuration
The application requires the following environment variables:
- `DJANGO_SECRET_KEY` - Secret key for Django
- `DJANGO_ENV` - Environment (development/production)
- `DATABASE_URL` - PostgreSQL connection URL
- `OPENROUTER_API_KEY` - API key for Open Router
- `AWS_ACCESS_KEY_ID` - Access key for S3
- `AWS_SECRET_ACCESS_KEY` - Secret key for S3
- `AWS_S3_ENDPOINT_URL` - S3 endpoint URL
