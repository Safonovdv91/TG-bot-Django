FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
WORKDIR /app
# Копируем зависимости
COPY pyproject.toml .
# Установка зависимостей через uv
RUN uv lock
RUN uv sync --frozen

ADD core .

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv run manage.py collectstatic --noinput

EXPOSE 8000
CMD uv run manage.py runserver 0.0.0.0:8000