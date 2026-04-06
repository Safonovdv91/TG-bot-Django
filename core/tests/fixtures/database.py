import pytest_asyncio
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.db import OperationalError
from users.models import Report

User = get_user_model()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db():
    """
    Автоматически очищает БД после каждого теста.
    Используется во всех тестах core/tests/
    """
    yield
    try:
        await Report.objects.all().adelete()
        await User.objects.all().adelete()
        await SocialAccount.objects.all().adelete()
    except OperationalError:
        # Таблицы могут не существовать при первом запуске/миграциях
        pass
