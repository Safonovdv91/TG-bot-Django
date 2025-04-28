import pytest
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
