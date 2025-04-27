from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import (
    Subscription,
    UserSubscription,
    CompetitionTypeModel,
    SportsmanClassModel,
)


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
    competition_type_id = 1  # Фиксированный тип, как в вашем примере
    sportsman_class_id = request.GET.get("sportsman_class")
    
    subscription, created = Subscription.objects.get_or_create(
        user_subscription=request.user.user_subscription,
        competition_type_id=competition_type_id,
        sportsman_class_id=sportsman_class_id
    )
    
    return render(request, "gymkhanagp/components/class_input_on.html", {
        "sportsman_class": get_object_or_404(SportsmanClassModel, pk=sportsman_class_id)
    })

@login_required
def unsubscribe_class(request):
    """Удаление подписки"""
    competition_type_id = 1  # Фиксированный тип
    sportsman_class_id = request.GET.get("sportsman_class")
    
    subscription = get_object_or_404(
        Subscription,
        user_subscription__user=request.user,
        competition_type_id=competition_type_id,
        sportsman_class_id=sportsman_class_id
    )
    subscription.delete()
    
    return render(request, "gymkhanagp/components/class_input_off.html", {
        "sportsman_class": get_object_or_404(SportsmanClassModel, pk=sportsman_class_id)
    })


@login_required
def toggle_subscription(request):
    try:
        competition_type_id = request.GET.get("competition_type")
        sportsman_class_id = request.GET.get("sportsman_class")

        if not competition_type_id or not sportsman_class_id:
            return JsonResponse({"error": "Missing parameters"}, status=400)

        user_subscription = UserSubscription.objects.get(user=request.user)

        subscription, created = Subscription.objects.get_or_create(
            user_subscription=user_subscription,
            competition_type_id=competition_type_id,
            sportsman_class_id=sportsman_class_id,
        )

        if not created:
            subscription.delete()

        return JsonResponse(
            {
                "is_subscribed": created,
                "competition_type_id": competition_type_id,
                "sportsman_class_id": sportsman_class_id,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
