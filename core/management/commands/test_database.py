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

        try:
            # Test basic database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    self.stdout.write(
                        self.style.SUCCESS("✓ Database connection successful")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR("✗ Database connection test failed")
                    )
                    return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Database connection failed: {e}")
            )
            return

        # Test DOAD table access
        try:
            doad_count = DoadDocument.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f"✓ DOAD table accessible - {doad_count} records found")
            )

            # Get sample DOAD numbers
            sample_doads = list(DoadDocument.get_available_doad_numbers()[:5])
            if sample_doads:
                self.stdout.write(f"  Sample DOAD numbers: {', '.join(sample_doads)}")
            else:
                self.stdout.write("  No DOAD numbers found")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ DOAD table access failed: {e}")
            )

        # Test Leave table access
        try:
            leave_count = LeaveDocument.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Leave table accessible - {leave_count} records found")
            )

            # Get sample chapters
            sample_chapters = list(LeaveDocument.get_available_chapters()[:5])
            if sample_chapters:
                self.stdout.write(f"  Sample chapters: {', '.join(sample_chapters)}")
            else:
                self.stdout.write("  No chapters found")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Leave table access failed: {e}")
            )

        # Test specific DOAD retrieval if available
        try:
            first_doad = DoadDocument.get_available_doad_numbers().first()
            if first_doad:
                chunks = DoadDocument.get_by_doad_number(first_doad)
                chunk_count = chunks.count()
                total_length = sum(len(chunk.text_chunk) for chunk in chunks)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ DOAD {first_doad} retrieval test - {chunk_count} chunks, {total_length} total characters"
                    )
                )
            else:
                self.stdout.write("  No DOAD available for retrieval test")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ DOAD retrieval test failed: {e}")
            )

        self.stdout.write("\nDatabase integration test completed!")
