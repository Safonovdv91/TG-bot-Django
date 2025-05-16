import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
load_dotenv("core/.env")

BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", default="False")
SITE_ID = os.environ.get("DJANGO_SITE_ID")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS").split(",")

INTERNAL_IPS = ["127.0.0.1"]


INSTALLED_APPS = [
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
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE = [
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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", default="5432"),
        "ATOMIC_REQUESTS": True,
    }
}

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


# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "telegram": {
        "SCOPE": ["photo_url"],
        "APP": {
            "client_id": os.getenv("OAUTH_TELEGRAM_CLIENT_ID"),
            "secret": os.getenv("OAUTH_TELEGRAM_SECRET"),
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

TELEGRAM_BOT_TOKEN = os.environ.get("OAUTH_TELEGRAM_SECRET")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Временно для разработки

# Celery Configuration Options
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True  # Для отслеживания статуса задачи если в исполнении
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
