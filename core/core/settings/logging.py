# ===========================================
# LOGGING CONFIGURATION
# ===========================================
from .base import DEBUG

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {name} - {message}",
            "style": "{",
        },
        "django-server": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "colored": {
            "format": "{levelname}: {asctime} {name} — {message}",
            "style": "{",
            "datefmt": "%H:%M:%S",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        # Консоль для локальной разработки (DEBUG режим)
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "filters": ["require_debug_true"],
        },
        # Консоль для production/Docker (без фильтра DEBUG)
        "console_prod": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django-server",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"] if DEBUG else ["console_prod"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"] if DEBUG else ["console_prod"],
            "level": "WARNING" if DEBUG else "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "level": "DEBUG" if DEBUG else "WARNING",
            "handlers": ["console"] if DEBUG else [],
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"] if DEBUG else ["console_prod"],
            "level": "INFO",
            "propagate": False,
        },
        "telegram": {
            "handlers": ["console"] if DEBUG else ["console_prod"],
            "level": "WARNING",
            "propagate": False,
        },
        "httpx": {
            "handlers": ["console"] if DEBUG else ["console_prod"],
            "level": "WARNING",
            "propagate": False,
        },
        "httpcore": {
            "handlers": ["console"] if DEBUG else ["console_prod"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"] if DEBUG else ["console_prod"],
        "level": "INFO",
    },
}
