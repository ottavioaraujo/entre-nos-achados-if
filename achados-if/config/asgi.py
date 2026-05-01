import os
from django.core.asgi import get_asgi_application
from config.bootstrap import run_startup_migrations

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
run_startup_migrations()
