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

## Development Setup with NixOS

NixOS is used for local development to provide a consistent environment without needing to rebuild containers:

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

## Production Deployment with Docker

For production, the application will be deployed in Docker containers:

1. Build the Docker image:
   ```
   docker build -t caf-gpt .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 -e DJANGO_ENV=production -e DATABASE_URL=your-db-url caf-gpt
   ```

## Local Testing with Docker Compose

For testing the production setup locally:

1. Start the services:
   ```
   docker-compose up -d
   ```

2. Run migrations:
   ```
   docker-compose exec web python manage.py migrate
   ```

3. Create a superuser:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

4. Access the application at http://localhost:8000

5. Stop the services:
   ```
   docker-compose down
   ```

## Environment Variables

- `DJANGO_ENV`: Environment to use (development or production)
- `DJANGO_SECRET_KEY`: Secret key for production
- `DATABASE_URL`: Database connection URL
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DEBUG`: Set to True for development, False for production

## Current Status

The project is under active development. Key completed items:
- Django project structure with three apps (Core, PaceNoteFoo, PolicyFoo)
- Security headers middleware
- Base templates with Bootstrap styling
- Landing page and health check endpoint
- Pace Notes UI implementation
- Environment variable configuration
- Database connection to Neon DB PostgreSQL
- NixOS development environment
- Docker configuration for production

For a detailed list of completed tasks, current sprint items, backlog, and open questions, see the `.app_logic/progress.md` file.

## Development

- Use the development settings by setting `DJANGO_ENV=development`
- Debug toolbar is available in development mode

### Code Quality

- **Linting**: Run `flake8` to check code quality
- **Formatting**: Run `black .` to format code
- **Import Sorting**: Run `isort .` to sort imports

The project uses the following tools for code quality:
- **Flake8**: For code linting (style and error checking)
- **Black**: For code formatting
- **isort**: For import sorting

Configuration files:
- `.flake8`: Flake8 configuration

## Deployment

- Set `DJANGO_ENV=production` for production deployment
- Configure proper security settings in production
- Set up proper database credentials
- Configure static files serving

## License

This project is licensed under the MIT License - see the LICENSE file for details. 