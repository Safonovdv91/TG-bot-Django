import pytest

from django.contrib.auth.models import User
from .factories import UserFactory, SportsmanClassFactory, SubscriptionFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def sportsman_class():
    return SportsmanClassFactory()


@pytest.fixture
def subscription():
    return SubscriptionFactory()


@pytest.fixture()
def user_1(db):
    user = User.objects.create_user("test_user")
    return user
