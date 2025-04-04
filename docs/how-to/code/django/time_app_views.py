import datetime

from django.http import HttpResponse


def index(request):
    return HttpResponse(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
