import os
from pathlib import Path

from dotenv import load_dotenv


def get_list_env(name: str, default: str = "") -> list[str]:
    """Get a comma-separated list from environment variable."""
    value = os.getenv(name) or default
    return [item.strip() for item in value.split(",") if item.strip()]


def get_env(name: str, default: str = "") -> str:
    """Get environment variable with optional default."""
    return os.getenv(name, default)


# BASE_DIR должен указывать на корень проекта (где manage.py), а не на core/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Загружаем .env файл если он существует (только для локальной разработки)
# В CI и тестах используются значения по умолчанию
env_file = BASE_DIR / ".env"
if not env_file.exists():
    env_file = BASE_DIR / ".env.prod"

if env_file.exists() and os.getenv("DJANGO_SETTINGS_MODULE") != "core.test":
    load_dotenv(env_file)


# =============================================================================
# Core Django Settings
# =============================================================================
SECRET_KEY: str = get_env("DJANGO_SECRET_KEY", "django-insecure-default-key-for-tests")
DEBUG: bool = get_env("DJANGO_DEBUG", "False") == "True"
SITE_ID: str = get_env("DJANGO_SITE_ID", "1")
ALLOWED_HOSTS = get_list_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
CSRF_TRUSTED_ORIGINS = get_list_env(
    "CSRF_TRUSTED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
)
CORS_ALLOWED_ORIGINS = get_list_env(
    "CORS_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
)

INTERNAL_IPS: list[str] = ["127.0.0.1"]


INSTALLED_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.telegram",
    "django_celery_results",
    "django_celery_beat",
    "index",
    "gymkhanagp",
    "g_cup_site",
    "telegram_bot",
    "users",
]

AUTHENTICATION_BACKENDS: list[str] = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

if DEBUG:
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"


MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "core/static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# Telegram Bot Settings
# =============================================================================
TELEGRAM_BOT_TOKEN = get_env(
    "TELEGRAM_BOT_TOKEN", "7110713844:AAEyjgfsPB2KyOkGos84rhEqlfKqaNRf7nM"
)
# Extract chat ID from token (first part before colon)
TELEGRAM_CHAT_ID = TELEGRAM_BOT_TOKEN.split(":")[0] if TELEGRAM_BOT_TOKEN else ""

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "telegram": {
        "SCOPE": ["photo_url"],
        "APP": {
            "client_id": TELEGRAM_CHAT_ID,
            "secret": TELEGRAM_BOT_TOKEN,
        },
        "AUTH_PARAMS": {"auth_date_validity": 30},
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True

LOGIN_REDIRECT_URL = "/"  # Перенаправление на главную страницу
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # Указываем Django, что он работает за обратным прокси
ACCOUNT_DEFAULT_HTTP_PROTOCOL = (
    "https"  # Указываем allauth использовать HTTPS для redirect_uri
)

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Временно для разработки

# =============================================================================
# Celery & Redis Configuration
# =============================================================================
REDIS_HOST = get_env("REDIS_HOST", "localhost")
REDIS_PORT = get_env("REDIS_PORT", "6379")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True  # Для отслеживания статуса задачи если в исполнении
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_EXTENDED = True

# =============================================================================
# Gymkhana Cup API Settings
# =============================================================================
GYMKHANA_CUP_URL = get_env("GYMKHANA_CUP_URL", "https://api.gymkhana-cup.ru")
GYMKHANA_CUP_TOKEN = get_env("GYMKHANA_CUP_TOKEN", "")

