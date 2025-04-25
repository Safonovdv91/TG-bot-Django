from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Subscription,
    UserSubscription,
    CompetitionTypeModel,
    SportsmanClassModel,
)


# Create your views here.
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


@require_POST
@login_required
def delete_subscription(request, pk):
    subscription = get_object_or_404(
        Subscription, pk=pk, user_subscription__user=request.user
    )
    subscription.delete()
    return redirect("gymkhanagp:index")


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


@require_POST
@login_required
def toggle_subscription(request):
    competition_type_id = request.POST.get("competition_type_id")
    sportsman_class_id = request.POST.get("sportsman_class_id")
    user_subscription = UserSubscription.objects.get(user=request.user)

    subscription, created = Subscription.objects.get_or_create(
        user_subscription=user_subscription,
        competition_type_id=competition_type_id,
        sportsman_class_id=sportsman_class_id,
        defaults={"created_at": timezone.now()},
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
