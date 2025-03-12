# Overview
A collection of AI tools and agents for army personnel, packaged as a Django application with NixOS support for development and Docker for production.

## Tech Stack
- Python 3.12
- Django 4.2
- PostgreSQL (Neon.tech serverless)
- Bootstrap 5
- NixOS development environment
- Docker for production deployment
- LLM Integration (to be determined)
- RAG (Retrieval Augmented Generation)

## Application Structure

### Django Apps
1. **core** - Base application with shared components
   - Landing page
   - Security headers middleware
   - Health check endpoint
   - Common utilities and base models

2. **pacenote_foo** - PaceNoteFoo LLM workflow
   - Pace Notes generator interface
   - Client-side session storage
   - Rate limiting display
   - Bootstrap-based UI

3. **policy_foo** - PolicyFoo LLM workflow
   - Chat interface (planned)
   - RAG implementation (planned)
   - LLM integration (planned)

### Pages
1. **Landing Page** - Introduction and navigation to tools
2. **Pace Notes Tool** - Interface for generating pace notes based on observations
3. **Policy Tool** - Chat interface for policy questions (coming soon)

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
├── pacenote_foo/         # PaceNote app
├── policy_foo/           # Policy app
├── static/               # Static files
├── templates/            # Project-wide templates
├── .app_logic/           # Documentation
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── shell.nix            # NixOS development environment
```

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
