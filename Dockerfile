# --- Builder stage ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY . /code

# Collect static files for production
RUN python manage.py collectstatic --noinput

# --- Final stage ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files and collected static files only
COPY --from=builder /code /code

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","--workers","2","caf_gpt.wsgi"]
