from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render


# Create your views here.
@login_required(login_url="/accounts/login")
def index(request: HttpRequest):
    page_title = "Настройки подписки соревнования Gymkhana GP"
    article_text = """
    Здесь управление подписками, связанными с соревнованием Gymkhana GP.
    """
    context = {
        "title": page_title,
        "text": article_text,
    }
    return render(request, "gymkhanagp/index.html", context=context)
