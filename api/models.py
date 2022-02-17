import json

import requests
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Round

LOOKUP_API = getattr(settings, "LOOKUP_API_URL", "https://api.postcodes.io")


class Outcode(models.Model):
    symbol = models.CharField(
        max_length=4,
        null=False,
        blank=False,
        validators=[RegexValidator(r"^[0-9a-zA-Z]*$")],
    )

    def get_nearest_outcodes(self):
        response = requests.request(
            "GET", f"{LOOKUP_API}/outcodes/{self.symbol}/nearest"
        )
        if response.status_code == 200:
            results = json.loads(response._content).get("result", [])
            return [area["outcode"] for area in results]
        return []

    def get_properties_for_outcode(self):
        properites = Property.objects.filter(outcode=self).aggregate(
            quantity=models.Count("pk"),
            average_price=Round(models.Avg("daily_price"), precision=2),
        )
        return properites

    def get_properties_for_nearest_outcodes(self):
        outcodes = self.get_nearest_outcodes()

        properties_qs = Outcode.objects.filter(symbol__in=outcodes).annotate(
            quantity=models.Count("property"),
            average_price=Round(models.Avg("property__daily_price"), precision=2),
        )
        all_properties_aggregation = Outcode.objects.filter(
            symbol__in=outcodes
        ).aggregate(
            quantity=models.Count("pk"),
            average_price=Round(models.Avg("property__daily_price"), precision=2),
        )

        return properties_qs, all_properties_aggregation


class Property(models.Model):
    outcode = models.ForeignKey(Outcode, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=128)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    longitude = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

    def get_outcode_for_coords(self):
        params = {
            "lon": self.longitude,
            "lat": self.latitude,
            "limit": 1,
        }
        response = requests.request("GET", f"{LOOKUP_API}/postcodes", params=params)
        if response.status_code == 200:
            result = json.loads(response._content).get("result")
            return result[0]["outcode"]
        return False

    def save(self, *args, **kwargs):
        if not self.pk:
            response = self.get_outcode_for_coords()
            if response:
                outcode, created = Outcode.objects.get_or_create(symbol=response)
                self.outcode = outcode
            else:
                raise ValueError("There is no outcode for given coordinates")
        super(Property, self).save(*args, **kwargs)
