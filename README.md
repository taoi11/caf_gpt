# CAF GPT

A Django-based AI assistant platform with specialized assistants for different use cases.

## Features

- **Core App**: Common functionality, landing page, and health check
- **PaceNoteFoo App**: RAG-powered chat interface for generating feedback notes
- **PolicyFoo App**: Specialized assistants for policy-related questions

## Project Structure

The project follows a standard Django project structure with multiple apps:

```
caf_gpt/
├── caf_gpt/              # Main project settings
│   ├── settings/         # Settings configuration
│   │   ├── base.py       # Base settings
│   │   └── __init__.py   # Environment-specific settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                 # Core app
│   ├── models.py         # Base models
│   ├── views.py          # Landing page and health check views
│   └── urls.py           # Core URL configuration
├── pacenote_foo/         # PaceNote app
│   ├── models.py         # Chat session models
│   ├── views.py          # Chat interface and RAG search views
│   └── urls.py           # PaceNote URL configuration
├── policy_foo/           # Policy app
│   ├── models.py         # Policy document models
│   ├── views.py          # Policy chat and document search views
│   └── urls.py           # Policy URL configuration
├── static/               # Static files
│   ├── css/              # CSS files
│   ├── js/               # JavaScript files
│   └── img/              # Image files
├── templates/            # Project-wide templates
│   └── base/             # Base templates
├── .app_logic/           # Project documentation
│   ├── overview.md       # Project overview
│   ├── core.md           # Core app documentation
│   ├── pacenote_foo.md   # PaceNote app documentation
│   ├── policy_foo.md     # Policy app documentation
│   └── progress.md       # Progress tracking and TODO list
├── manage.py             # Django management script
├── requirements.txt      # Project dependencies
├── Dockerfile            # Docker configuration for production
└── docker-compose.yml    # Docker Compose configuration for local testing
```

## Environment Variables

- `DJANGO_ENV`: Environment to use (development or production)
- `DJANGO_SECRET_KEY`: Secret key for production
- `DATABASE_URL`: Database connection URL
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DEBUG`: Set to True for development, False for production
