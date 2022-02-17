from rest_framework import generics, response

from .models import Outcode
from .renderers import NexusRenderer, OutcodeRenderer


class OutcodeView(generics.RetrieveAPIView):
    renderer_classes = [
        OutcodeRenderer,
    ]

    def get(self, request, *args, **kwargs):
        outcode_obj = Outcode.objects.filter(symbol=self.kwargs["symbol"]).first()
        if outcode_obj:
            property = outcode_obj.get_properties_for_outcode()
            data = {
                "attr": {
                    "quantity": str(property["quantity"]),
                    "daily_price_avarage": f"{property['average_price']:.2f}",
                },
                "content": outcode_obj.symbol,
            }
            return response.Response(data)


class NexusView(generics.RetrieveAPIView):
    renderer_classes = [
        NexusRenderer,
    ]

    def get(self, request, *args, **kwargs):
        outcode_obj = Outcode.objects.filter(symbol=self.kwargs["symbol"]).first()
        if outcode_obj:
            properties, nexus_info = outcode_obj.get_properties_for_nearest_outcodes()
            items = [
                {
                    "attrs": {
                        "listing-count": str(property.quantity),
                        "average-daily-price": f"{property.average_price:.2f}",
                    },
                    "content": property.symbol,
                }
                for property in properties
            ]
            data = {
                "root_attrs": {
                    "listing-count": str(nexus_info["quantity"]),
                    "average-daily-price": f"{nexus_info['average_price']:.2f}",
                },
                "items": items,
                "content": outcode_obj.symbol,
            }
            return response.Response(data)
