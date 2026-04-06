import pytest

from django.contrib.auth.models import User
from .factories import UserFactory, SportsmanClassFactory, SubscriptionFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def sportsman_class(db):
    return SportsmanClassFactory()


@pytest.fixture
def subscription(db):
    return SubscriptionFactory()


@pytest.fixture()
def user_1(db):
    user = User.objects.create_user("test_user")
    return user
