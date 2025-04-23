from django.shortcuts import render


# Create your views here.
def index(request):
    context = {
        "letters": ["A", "B", "C1", "C2", "C3", "D1", "D2", "D3", "D4", "N"],
    }
    return render(request, "index/index.html", context=context)
