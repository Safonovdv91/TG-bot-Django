from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from users.utils import get_telegram_id
from .models import (
    Subscription,
    UserSubscription,
    CompetitionTypeModel,
    SportsmanClassModel,
)
from .tasks import send_telegram_message_task


@login_required(login_url="/accounts/login")
def index(request: HttpRequest):
    page_title = "Настройки подписки соревнования Gymkhana GP"
    article_text = """
    Здесь управление подписками, связанными с соревнованием Gymkhana GP.
    """
    user_subscription = UserSubscription.objects.get(user=request.user)
    subscriptions = (
        Subscription.objects.all()
        .filter(
            user_subscription=user_subscription,
            competition_type=CompetitionTypeModel.objects.get(pk=1),
        )
        .select_related("competition_type", "sportsman_class")
    )
    print(subscriptions)

    context = {
        "title": page_title,
        "text": article_text,
        "subscriptions": subscriptions,
    }
    return render(request, "gymkhanagp/index.html", context=context)


@login_required
def subscriptions_view(request):
    competition_types = CompetitionTypeModel.objects.all()
    sportsman_classes = SportsmanClassModel.objects.all()

    user_subscriptions = set(
        Subscription.objects.filter(user_subscription__user=request.user).values_list(
            "competition_type_id", "sportsman_class_id"
        )
    )

    return render(
        request,
        "gymkhanagp/subscriptions.html",
        {
            "competition_types": competition_types,
            "sportsman_classes": sportsman_classes,
            "user_subscriptions": user_subscriptions,
        },
    )


@login_required
def subscribe_class(request):
    """Добавление подписки"""

    competition_type_id = 1
    sportsman_class_id = request.GET.get("sportsman_class")
    user_subscription = UserSubscription.objects.get(user=request.user)

    Subscription.objects.get_or_create(
        user_subscription=user_subscription,
        competition_type_id=competition_type_id,
        sportsman_class_id=sportsman_class_id,
    )
    sportsman_class = get_object_or_404(SportsmanClassModel, pk=sportsman_class_id)
    telegram_id = get_telegram_id(request.user)
    if telegram_id:
        message = (
            f"✅ Вы успешно подписались на класс: {sportsman_class.name}!\n"
            f"Теперь вы будете получать уведомления о соревнованиях."
        )

        send_telegram_message_task.delay(telegram_id, message)

    return render(
        request,
        "gymkhanagp/components/class_input_on.html",
        {
            "sportsman_class": get_object_or_404(
                SportsmanClassModel, pk=sportsman_class_id
            )
        },
    )


@login_required
def unsubscribe_class(request):
    """Удаление подписки"""
    competition_type_id = 1
    sportsman_class_id = request.GET.get("sportsman_class")

    subscription = get_object_or_404(
        Subscription,
        user_subscription__user=request.user,
        competition_type_id=competition_type_id,
        sportsman_class_id=sportsman_class_id,
    )
    subscription.delete()

    sportsman_class = get_object_or_404(SportsmanClassModel, pk=sportsman_class_id)

    telegram_id = get_telegram_id(request.user)  # Используем один из способов выше
    if telegram_id:
        message = (
            f"❌ Вы успешно отписались от класа: {sportsman_class.name}!\n"
            f"Теперь вы НЕ будете получать уведомления о соревнованиях."
        )
        send_telegram_message_task.delay(telegram_id, message)

    return render(
        request,
        "gymkhanagp/components/class_input_off.html",
        {
            "sportsman_class": get_object_or_404(
                SportsmanClassModel, pk=sportsman_class_id
            )
        },
    )
