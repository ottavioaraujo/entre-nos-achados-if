import os
from django.core.asgi import get_asgi_application
from config.bootstrap import run_startup_migrations

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
run_startup_migrations()
application = get_asgi_application()
