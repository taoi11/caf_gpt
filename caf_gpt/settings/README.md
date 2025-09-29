# CAF GPT Settings

This directory contains the Django settings for the CAF GPT project, organized by environment.

## Structure

- `base.py`: Common settings shared across all environments
- `dev.py`: Development-specific settings (extends base.py)
- `prod.py`: Production-specific settings (extends base.py)
- `__init__.py`: Loads the appropriate settings module based on the `DJANGO_ENV` environment variable

## Environment Selection

The settings module is selected based on the `DJANGO_ENV` environment variable:

- `DJANGO_ENV=development` (default) → Uses `dev.py`
- `DJANGO_ENV=production` → Uses `prod.py`

## Environment Variables

The following environment variables are used:

### Required in All Environments
- `DATABASE_URL`: Connection string for the PostgreSQL database

### Required in Production Only
- `DJANGO_SECRET_KEY`: A secure secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames

### Optional
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email server configuration (used in production)
- `DEFAULT_FROM_EMAIL`: Default sender address for emails
- `TURNSTILE_SITE_KEY`: Cloudflare Turnstile site key
- `TURNSTILE_SECRET_KEY`: Cloudflare Turnstile secret key

## Using Different Settings Modules

### For Development
```bash
# Default - no need to set explicitly
export DJANGO_ENV=development
```

### For Production
```bash
export DJANGO_ENV=production
export DJANGO_SECRET_KEY='your-secure-secret-key'
export ALLOWED_HOSTS='example.com,www.example.com'
export TURNSTILE_SITE_KEY='your-turnstile-site-key'
export TURNSTILE_SECRET_KEY='your-turnstile-secret-key'
```

## Django Management Commands

When running management commands, you can also specify the settings module directly:

```bash
# Development
python manage.py runserver --settings=caf_gpt.settings.dev

# Production
python manage.py collectstatic --settings=caf_gpt.settings.prod
```

## Adding New Settings

- Add common settings to `base.py`
- Add environment-specific settings to `dev.py` or `prod.py`
- For new environments, add a new file and update the mapping in `__init__.py`