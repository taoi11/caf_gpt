"""
Management command to test database connection and models.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from core.models import DoadDocument, LeaveDocument


class Command(BaseCommand):
    help = 'Test database connection and models for SvelteKit integration'

    def handle(self, *args, **options):
        self.stdout.write("Testing database connection...")

        if self.test_database_connection():
            self.stdout.write(self.style.SUCCESS("✓ Database connection successful"))
        else:
            self.stdout.write(self.style.ERROR("✗ Database connection failed"))
            return

    def test_database_connection(self) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception:
            return False
