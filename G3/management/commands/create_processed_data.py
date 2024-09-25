from django.core.management.base import BaseCommand
from G3.models import G3Data
from G3.utils import update_processed_data


class Command(BaseCommand):
    help = "Create processed data for all G3Data instances"

    def handle(self, *args, **kwargs):
        # Get all G3Data instances
        instances = G3Data.objects.all()
        # Process the data for each instance
        for instance in instances:
            metadata = instance.metadata
            updated_processed_data = update_processed_data(
                processed_data=instance.processed_data, metadata=metadata
            )
            instance.processed_data = updated_processed_data
            instance.save()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created processed data for all G3Data instances"
            )
        )
