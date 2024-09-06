import time
from django.core.management.base import BaseCommand
from django.db import OperationalError, connections
from django.utils import timezone

class Command(BaseCommand):
    """Django command to wait for database to be available"""

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🕒 Waiting for database...'))

        # Wait for database to become available
        time.sleep(5)
        
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write(self.style.WARNING('🛑 Database unavailable, waiting 5 seconds...'))
                time.sleep(5)

        self.stdout.write(self.style.SUCCESS('✅ Database available!'))
