# Базовый образ с Python 3.13 c uv
FROM python:3.13-slim as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
RUN uv lock && uv sync --frozen

# Финальный образ
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /bin/uv /bin/uv
COPY --from=builder /bin/uvx /bin/uvx

COPY --from=builder /app/.venv /app/.venv
COPY core .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["sh", "-c", \
    "python manage.py collectstatic --noinput && \
     python manage.py migrate && \
     gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
