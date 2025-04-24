from django.http import HttpRequest
from django.shortcuts import render


# Create your views here.
# @login_required(login_url="/accounts/login")
def index(request: HttpRequest):
    article_text = """
    Этот сервис создан в помощь мотоспортсменам увлекающимся фигурным управление мотоциклом.
    Вместо того чтобы носиться как оголтелы по городу - лучше оттачивать свои навыки на площадке
    И этот бот покажет вам, а именно будет присылать вам каждй раз когда вас обгоняют уведомления.
    """
    context = {
        "article_title": "Gymkhana bot - здесь будет заголовок",
        "text": article_text,
    }
    return render(request, "index/index.html", context=context)
