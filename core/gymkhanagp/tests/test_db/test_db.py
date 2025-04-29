from django.contrib.auth.models import User
import pytest

@pytest.mark.django_db
def test_user_create(user):
    count = User.objects.all().count()
    assert count == 1
    
@pytest.mark.django_db
def test_user_not_create():
    count = User.objects.all().count()
    assert count == 0
    
def test_username(user_1):
    assert user_1.username == "test_user"
    
    
def test_change_password(user_1):
    user_1.set_password("new_password")
    assert user_1.check_password("new_password") == True