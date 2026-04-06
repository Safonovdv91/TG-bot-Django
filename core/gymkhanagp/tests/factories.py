import factory
from django.contrib.auth import get_user_model
from gymkhanagp.models import (
    UserSubscription,
    SportsmanClassModel,
    Subscription,
    CompetitionTypeModel,
)


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


class CompetitionTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompetitionTypeModel

    name = factory.Sequence(lambda n: f"Competition{n}")
    description = factory.Faker("sentence")


class UserSubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSubscription

    user = factory.SubFactory(UserFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        переписываем метод создания, если подписки пользователя уже есть
        то возвращаем их, если нет - то вызываем родительский метод.
        """
        user = kwargs.get("user")
        if user and hasattr(user, "subscriptions"):
            # UserSubscription already created by signal
            return user.subscriptions
        return super()._create(model_class, *args, **kwargs)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    # Первое создание UserSubscription (от которого создадим все остальные подписки)
    user_subscription = factory.SubFactory(UserSubscriptionFactory)
    sportsman_class = factory.SubFactory(SportsmanClassFactory)
    competition_type = factory.SubFactory(CompetitionTypeFactory)
