"""
Главный файл настроек Django.
Импортирует все модули настроек в правильном порядке.
"""
# Переопределения для production/development

from .base import *
from .logging import *
from .database import *
# from .cache import *
# from .storage import *
# from .email import *
# from .auth import *
# from .logging import *
# from .celery import *
# from .delivery import *

# if os.environ.get("DJANGO_DEBUG") != "True":
#     from .production import *