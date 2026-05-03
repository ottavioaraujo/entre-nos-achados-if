import os
from django.core.wsgi import get_wsgi_application
from config.bootstrap import run_startup_migrations

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
run_startup_migrations()
