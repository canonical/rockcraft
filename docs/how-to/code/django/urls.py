from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("time/", include("time_app.urls")),
    path("admin/", admin.site.urls),
]
