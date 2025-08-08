import os

from .settings import *

# Настройки для локального тестирования (SQLite)
if os.getenv("CI") != "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "OPTIONS": {"timeout": 30},
            "TEST": {"NAME": ":memory:"},
        }
    }
else:
    # Настройки для CI (PostgreSQL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_db",
            "USER": "test_user",
            "PASSWORD": "test_password",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
DATABASE_ROUTERS = []


# Настройки для тестирования
SECRET_KEY = "(fwtvv(%f%o_tb8+$4t_+3y%oil(^+49wv86-f%i%te0#=fg4k"
DEBUG = True
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Отключаем кеширование
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
