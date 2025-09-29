# CAF GPT

A Django-based AI assistant platform with specialized assistants for different use cases.

## Features

- **Core App**: Common functionality, landing page, health check, and shared services
- **PaceNoteFoo App**: AI-powered interface for generating structured feedback notes
- **PolicyFoo App**: Specialized assistants for policy-related questions with document citations

## Project Structure

The project follows a standard Django project structure with multiple apps:

```
caf_gpt/
├── caf_gpt/              # Main project settings
│   ├── settings/         # Settings configuration
│   │   ├── base.py       # Base settings shared across environments
│   │   ├── dev.py        # Development-specific settings
│   │   ├── prod.py       # Production-specific settings
│   │   └── __init__.py   # Environment selector based on DJANGO_ENV
│   ├── urls.py           # Main URL configuration
│   ├── asgi.py           # ASGI configuration
│   └── wsgi.py           # WSGI configuration
├── core/                 # Core app
│   ├── models.py         # Base models
│   ├── views.py          # Landing page and health check views
│   ├── urls.py           # Core URL configuration
│   ├── middleware.py     # Custom middleware
│   ├── services/         # Shared services
│   │   ├── open_router_service.py # LLM integration
│   │   ├── s3_service.py # S3 storage integration
│   │   ├── database_service.py # Database operations
│   │   ├── cost_tracker_service.py # LLM cost tracking
│   │   └── turnstile_service.py # Cloudflare Turnstile integration
│   ├── templates/        # Core templates
│   │   └── base/         # Base templates
│   ├── static/           # Core static files
│   └── utils/            # Utility functions
├── pacenote_foo/         # PaceNote app
│   ├── models.py         # Chat session models
│   ├── views.py          # Chat interface views
│   ├── urls.py           # PaceNote URL configuration
│   ├── services/         # App-specific services
│   │   ├── prompt_service.py # Prompt template management
│   │   └── local_file_reader.py # Local file content reading
│   ├── prompts/          # Prompt templates
│   │   ├── base.md       # Base prompt template
│   │   └── competencies/ # Rank-specific competency templates
│   ├── templates/        # PaceNote templates
│   ├── static/           # PaceNote static files
│   └── management/       # Custom management commands
├── policy_foo/           # Policy app
│   ├── models.py         # Policy document models
│   ├── urls.py           # Policy URL configuration
│   ├── views/            # Organized view modules
│   │   ├── router.py     # Policy routing logic
│   │   ├── rate_limits.py # Rate limiting checks
│   │   └── doad_foo/     # DOAD policy handler
│   │       ├── finder.py # Document finder
│   │       ├── reader.py # Document reader
│   │       └── main.py   # Response synthesizer
│   ├── templates/        # Policy templates
│   ├── static/           # Policy static files
│   └── prompts/          # Policy prompt templates
├── static/               # Static files
│   ├── css/              # CSS files
│   ├── js/               # JavaScript files
│   └── img/              # Image files
├── templates/            # Project-wide templates
│   └── base/             # Base templates
├── staticfiles/          # Collected static files (production)
├── manage.py             # Django management script
├── requirements.txt      # Project dependencies
├── Dockerfile            # Docker configuration for production
└── docker-compose.yml    # Docker Compose configuration for local testing
```

## Environment Variables

- `DJANGO_ENV`: Environment to use (development or production)
- `DJANGO_SECRET_KEY`: Secret key for production
- `DATABASE_URL`: Database connection URL (PostgreSQL)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `OPENROUTER_API_KEY`: API key for OpenRouter LLM service
- `S3_ENDPOINT_URL`: S3-compatible storage endpoint
- `S3_ACCESS_KEY`: S3 access key
- `S3_SECRET_KEY`: S3 secret key
- `S3_BUCKET_NAME`: S3 bucket name
- `TURNSTILE_SITE_KEY`: Cloudflare Turnstile site key
- `TURNSTILE_SECRET_KEY`: Cloudflare Turnstile secret key

## Environment Setup

### Django Settings Configuration

The project uses environment-based settings:
- Development mode (default): `DJANGO_ENV=development`
- Production mode: `DJANGO_ENV=production`

For more details, see [`caf_gpt/settings/README.md`](caf_gpt/settings/README.md).
