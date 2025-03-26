# noqa: INP001 (implicit namespace package)
import os

# Rockcraft repo doesn't need Django installed so ignore module-not-found mypy error
from django.core.wsgi import get_wsgi_application  # type: ignore[module-not-found]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
application = get_wsgi_application()
