import os


def run_startup_migrations():
    """Optionally initialize a fresh production database on first deployment."""
    if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "").lower() in {"1", "true", "yes"}:
        from django.core.management import call_command

        call_command("migrate", interactive=False, verbosity=1)
