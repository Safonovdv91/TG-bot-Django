import os

from .settings import *

# =============================================================================
# Test Settings - All environment variables are set directly here for CI
# =============================================================================

# Database - use SQLite in memory by default (works everywhere)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {"timeout": 30},
        "TEST": {"NAME": ":memory:"},
    }
}

# For CI with PostgreSQL (optional - set CI_USE_POSTGRES=true to enable)
if os.getenv("CI_USE_POSTGRES") == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "test_db"),
            "USER": os.getenv("DB_USER", "test_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", "test_password"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

DATABASE_ROUTERS = []


# =============================================================================
# Core Django Settings
# =============================================================================
SECRET_KEY = "(fwtvv(%f%o_tb8+$4t_+3y%oil(^+49wv86-f%i%te0#=fg4k"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
CORS_ALLOWED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
SITE_ID = 1

# =============================================================================
# Test-Specific Settings
# =============================================================================
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable caching for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# =============================================================================
# External Services - Mock/Test Values
# =============================================================================

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", "7110713844:AAEyjgfsPB2KyOkGos84rhEqlfKqaNRf7nM"
)

# Gymkhana Cup API
GYMKHANA_CUP_URL = os.getenv("GYMKHANA_CUP_URL", "https://api.gymkhana-cup.ru")
GYMKHANA_CUP_TOKEN = os.getenv("GYMKHANA_CUP_TOKEN", "test_token_for_ci_pipeline")

# =============================================================================
# Redis & Celery
# =============================================================================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# Use dummy broker for tests (no Redis/RabbitMQ required)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "memory://localhost/")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# =============================================================================
# Email Backend
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
