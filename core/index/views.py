from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url="login")
def index(request: HttpRequest):
    context = {
        "letters": ["A", "B", "C1", "C2", "C3", "D1", "D2", "D3", "D4", "N"],
    }
    return render(request, "index/index.html", context=context)
