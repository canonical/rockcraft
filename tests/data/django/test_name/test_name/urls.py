# Rockcraft repo doesn't need Django installed so ignore module-not-found mypy error
from django.contrib import admin  # type: ignore
from django.urls import path  # type: ignore

urlpatterns = [
    path("admin/", admin.site.urls),
]
