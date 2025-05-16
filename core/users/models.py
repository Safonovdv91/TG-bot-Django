from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class Profile(BaseModel):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="Активный профиль")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering = ("-created_at",)
        db_table = "profiles"
        default_related_name = "profile"

    def __str__(self):
        return f"{[self.user.username]}"
