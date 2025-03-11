# CAF GPT

A Django-based AI assistant platform with specialized assistants for different use cases.

## Features

- **Core App**: Common functionality, landing page, and health check
- **PaceNoteFoo App**: RAG-powered chat interface for general questions
- **PolicyFoo App**: Specialized assistant for policy-related questions

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
│   ├── middleware.py     # Security headers middleware
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
├── manage.py             # Django management script
└── requirements.txt      # Project dependencies
```

## Setup with NixOS

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/caf_gpt.git
   cd caf_gpt
   ```

2. Enter the Nix shell:
   ```
   nix-shell
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Environment Variables

- `DJANGO_ENV`: Environment to use (development or production)
- `DJANGO_SECRET_KEY`: Secret key for production
- `DATABASE_URL`: Database connection URL
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DEBUG`: Set to True for development, False for production

## Development

- Use the development settings by setting `DJANGO_ENV=development`
- Debug toolbar is available in development mode

## Deployment

- Set `DJANGO_ENV=production` for production deployment
- Configure proper security settings in production
- Set up proper database credentials
- Configure static files serving

## License

This project is licensed under the MIT License - see the LICENSE file for details. 