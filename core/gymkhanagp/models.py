from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CompetitionTypeModel(models.Model):
    name = models.CharField(max_length=15, unique=True, verbose_name="Тип соревнований")
    description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Тип соревнования"
        verbose_name_plural = "Типы соревнования"

    def __str__(self):
        return f"{self.name} - {self.description}"


class SportsmanClassModel(models.Model):
    name = models.CharField(max_length=2, unique=True, verbose_name="Класс спортсмена")
    description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Класс спортсмена"
        verbose_name_plural = "Классы спортсменов"

    def __str__(self):
        return f"{self.name} - {self.description}"


class UserSubscription(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активна ли подписка")
    source = models.CharField(
        max_length=10,
        choices=(("telegram", "Telegram"), ("site", "Сайт"), ("admin", "Админ панель")),
        default="admin",
    )

    competition_type = models.ManyToManyField(
        CompetitionTypeModel,
        through="Subscription",
        through_fields=("user_subscription", "competition_type"),
    )
    sportsman_class = models.ManyToManyField(
        SportsmanClassModel,
        through="Subscription",
        through_fields=("user_subscription", "sportsman_class"),
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.username}"


class Subscription(models.Model):
    user_subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE)
    competition_type = models.ForeignKey(CompetitionTypeModel, on_delete=models.CASCADE)
    sportsman_class = models.ForeignKey(SportsmanClassModel, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_subscription", "competition_type", "sportsman_class"],
                name="user_subscription_combination",
            )
        ]

    def __str__(self):
        return f"{self.user_subscription.user.username} - {self.competition_type.name} - {self.sportsman_class.name}"
