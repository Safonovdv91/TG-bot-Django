import factory
from django.contrib.auth import get_user_model
from gymkhanagp.models import UserSubscription, SportsmanClassModel, Subscription


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "password")

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """
        Переопределение метода для сохранения пользователя после создания
        объекта, (необходимо для корректной работы UserFactory), т.к. в следующих обновлениях pytest-factory
        сохранение пользователя автоматически не будет происходить.
        """
        if create and results and not cls._meta.skip_postgeneration_save:
            instance.save()


class SportsmanClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SportsmanClassModel

    name = factory.Sequence(lambda n: f"C{int(n) + 1}")
    description = factory.Faker("sentence")


class UserSubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSubscription

    user = factory.SubFactory(UserFactory)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    user_subscription = factory.SubFactory(UserSubscriptionFactory)
    sportsman_class = factory.SubFactory(SportsmanClassFactory)
    competition_type_id = 1
