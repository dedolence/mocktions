from django.core.management.base import BaseCommand, CommandError, CommandParser
from listings.models import Listing
from typing import Any, Optional

class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '-y',
            action="store_true"
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        queryset = Listing.objects.all()

        if queryset.count() > 0:
            if not options['y']:
                conf = input(self.style.WARNING("Are you sure you want to delete all listings? "))
                if conf.lower() not in ("y", "yes"):
                    self.stdout.write(self.style.ERROR("Canceled."))
            
            for i, listing in enumerate(queryset, start=1):
                listing.delete()
            self.stdout.write(self.style.SUCCESS(f"{i} listings deleted."))
        else:
            self.stdout.write(self.style.NOTICE("No listings found."))
        
        return