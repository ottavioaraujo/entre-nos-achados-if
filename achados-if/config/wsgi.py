import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# The first production deployment can initialize a fresh managed database by
# enabling RUN_MIGRATIONS_ON_STARTUP. Keep this opt-in so routine serverless
# cold starts do not run schema changes unexpectedly.
if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "").lower() in {"1", "true", "yes"}:
    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=1)

application = get_wsgi_application()
