import pytest
from django.urls import reverse
from gymkhanagp.models import Subscription


@pytest.mark.django_db
class TestSubscriptionViews:
    def test_subscription_manage_authenticated(self, client, user):
        """Тест доступа к странице подписок для авторизованного пользователя"""
        client.force_login(user)
        response = client.get(reverse("gymkhanagp:subscriptions"))
        assert response.status_code == 200
        assert "sportsman_classes" in response.context

    def test_unsubscribe_class(self, client, subscription):
        """Тест удаления подписки"""
        client.force_login(subscription.user_subscription.user)
        url = (
            reverse("gymkhanagp:unsubscribe_class")
            + f"?sportsman_class={subscription.sportsman_class.id}"
        )

        response = client.post(url)
        assert response.status_code == 200
        assert not Subscription.objects.filter(id=subscription.id).exists()

    def test_anonymous_redirect(self, client):
        """Тест редиректа для анонимных пользователей"""
        for url in [
            reverse("gymkhanagp:subscriptions"),
            reverse("gymkhanagp:subscribe_class"),
        ]:
            response = client.get(url)
            assert response.status_code == 302
            assert "/login/" in response.url
