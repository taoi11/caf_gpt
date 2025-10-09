# CAF GPT

A Django-based AI assistant platform with specialized assistants for different use cases.

## Features

- **Core App**: Common functionality, landing page, health check, and shared services
- **PaceNoteFoo App**: AI-powered interface for generating structured feedback notes
- **PolicyFoo App**: Specialized assistants for policy-related questions with document citations

## Project Structure

The project follows a standard Django project structure with multiple apps:

- caf_gpt/: Main project settings
- core/: Core app with shared functionality
- pacenote_foo/: PaceNote app for feedback notes
- policy_foo/: Policy app for policy questions

## Environment Variables

The following environment variables are used:

### Required in All Environments
- `DATABASE_URL`: Connection string for the PostgreSQL database

### Required in Production Only
- `DJANGO_SECRET_KEY`: A secure secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames

### Optional
- `DJANGO_ENV`: Environment to use (development or production) - Default: development
- `OPENROUTER_API_KEY`: API key for OpenRouter LLM service
- `TURNSTILE_SITE_KEY`: Cloudflare Turnstile site key
- `TURNSTILE_SECRET_KEY`: Cloudflare Turnstile secret key
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email server configuration (used in production)
- `DEFAULT_FROM_EMAIL`: Default sender address for emails

## Security Features
- Input validation and sanitization
- Error handling with appropriate status codes
- CSP compliance
- Cloudflare Turnstile integration for bot protection (see core/README.md for implementation details)

## Environment Setup

### Django Settings Configuration

The project uses environment-based settings:
- Development mode (default): `DJANGO_ENV=development`
- Production mode: `DJANGO_ENV=production`

For more details, see [`caf_gpt/settings/README.md`](caf_gpt/settings/README.md).
