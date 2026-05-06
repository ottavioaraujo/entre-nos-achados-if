import os

from django.db import connection


_MIGRATION_LOCK = "entre_nos_django_migrations"


def run_startup_migrations():
    """Optionally initialize a fresh production database on first deployment."""
    if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "").lower() in {"1", "true", "yes"}:
        from django.core.management import call_command

        acquired = False
        if connection.vendor == "mysql":
            # Vercel can cold-start several function instances at once. Serialize
            # their migrations so TiDB never receives overlapping DDL statements.
            with connection.cursor() as cursor:
                cursor.execute("SELECT GET_LOCK(%s, 10)", [_MIGRATION_LOCK])
                acquired = cursor.fetchone()[0] == 1
            if not acquired:
                raise RuntimeError("Could not acquire the database migration lock.")

        try:
            call_command("migrate", interactive=False, verbosity=1)
        finally:
            if acquired:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT RELEASE_LOCK(%s)", [_MIGRATION_LOCK])
