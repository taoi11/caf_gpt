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

See the root README.md for full documentation of environment variables.
