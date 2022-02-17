import csv
import io

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from api.models import Property


class Command(BaseCommand):
    help = "Create initial data"

    def handle(self, *args, **options):
        data_url = getattr(settings, "INITIAL_DATA_URL")
        if not data_url:
            raise CommandError("Initial data url not set")
        response = requests.request("GET", data_url)
        print(response._content.decode("utf-8"))
        quantity = 0
        content = response._content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        for row in reader:
            print(row)
            try:
                property = Property(
                    name=row["name"],
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    daily_price=row["price"],
                )
                property.save()
                quantity += 1
            except (ValueError, TypeError) as e:
                print(e)
                pass

        self.stdout.write(
            self.style.SUCCESS(f"Succesfully created {quantity} properties")
        )
