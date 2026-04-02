import pytest_asyncio

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

User = get_user_model()


@pytest_asyncio.fixture
async def django_user(db):
    """
    Создает тестового пользователя Django.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_user(
        username="test_user",
        email="test@example.com",
        password="password1234",
    )
    return user


@pytest_asyncio.fixture
async def django_user_not_active(db):
    """
    Создает тестового пользователя Django.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_user(
        username="test_user",
        email="test@example.com",
        password="password1234",
        is_active=False,
    )
    return user


@pytest_asyncio.fixture
async def django_superuser(db):
    """
    Создает тестового пользователя Django.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_superuser(
        username="test_superuser",
        email="test_superuser@example.com",
        password="admin1234",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest_asyncio.fixture
async def django_superuser_not_active(db):
    """
    Создает тестового пользователя Django.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_superuser(
        username="test_superuser_not_active",
        email="test_superuser_not_active@example.com",
        password="admin1234",
        is_staff=True,
        is_active=False,
    )
    return user


@pytest_asyncio.fixture
async def django_user_with_telegram(db):
    """
    Создает тестового пользователя Django с telegram.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_user(
        username="test_user_with_telegram",
        email="test_user_with_telegram@example.com",
        password="password189000981",
    )
    await SocialAccount.objects.acreate(
        user=user,
        provider="telegram",
        uid=189000981,
        extra_data={"id": 189000981},  # TG id пользователя
    )
    return user


@pytest_asyncio.fixture
async def django_admin_with_telegram(db):
    """
    Создает тестового администратора с telegram.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    from django.contrib.auth import get_user_model
    from allauth.socialaccount.models import SocialAccount

    User = get_user_model()

    # Асинхронное создание суперпользователя
    user = await User.objects.acreate_superuser(
        username="test_superuser_with_telegram",
        email="test_superuser_with_telegram@example.com",
        password="admin1234",
    )
    await SocialAccount.objects.acreate(
        user=user,
        provider="telegram",
        uid=666666666,
        extra_data={"id": 666666666},  # TG id пользователя
    )
    return user


@pytest_asyncio.fixture
async def django_admin_with_telegram_not_active(db):
    """
    Создает тестового администратора с telegram.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    from django.contrib.auth import get_user_model
    from allauth.socialaccount.models import SocialAccount

    User = get_user_model()

    # Асинхронное создание суперпользователя
    user = await User.objects.acreate_superuser(
        username="test_superuser_with_telegram",
        email="test_superuser_with_telegram@example.com",
        password="admin1234",
        is_active=False,
    )
    await SocialAccount.objects.acreate(
        user=user,
        provider="telegram",
        uid=666666666,
        extra_data={"id": 666666666},  # TG id пользователя
    )
    return user
