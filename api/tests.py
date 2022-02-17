from django.test import TestCase

from .models import Outcode, Property


class ApiModelTestCase(TestCase):
    def setUp(self) -> None:
        # m7 outcode
        self.property_1 = Property(
            name="Test1",
            latitude="53.50114",
            longitude="-2.26429",
            daily_price="100",
        )
        self.property_1.save()
        # m4 outcode
        self.property_2 = Property(
            name="Test2",
            latitude="53.48251",
            longitude="-2.22802",
            daily_price="150",
        )
        self.property_2.save()
        self.nearest_outcodes_for_m7 = [
            "M7",
            "M8",
            "M3",
            "M25",
            "M6",
            "M60",
            "M2",
            "M61",
            "M99",
            "M4",
        ]

    def test_set_outcode_when_saving(self):
        quantity = Property.objects.count()
        self.assertEqual(quantity, 2)
        self.assertEqual(self.property_1.outcode.symbol, "M7")
        self.assertEqual(self.property_2.outcode.symbol, "M4")

    def test_nearest_outcodes(self):
        outcodes = self.property_1.outcode.get_nearest_outcodes()
        self.assertEqual(self.nearest_outcodes_for_m7, outcodes)

    def test_nearest_outcodes_with_properties(self):
        (
            properties,
            nexus_info,
        ) = self.property_1.outcode.get_properties_for_nearest_outcodes()
        self.assertEqual(nexus_info["quantity"], 2)
        self.assertEqual(nexus_info["average_price"], 125.00)
        self.assertIn(self.property_2.outcode, properties)

    def test_properties_for_outcode(self):
        outcode = Outcode.objects.get(symbol="M4")
        properties = outcode.get_properties_for_outcode()
        self.assertEqual(properties["average_price"], 150.00)
        self.assertEqual(properties["quantity"], 1)

        # change outcode for test purposes
        self.property_1.outcode = outcode
        self.property_1.save()
        new_properties = outcode.get_properties_for_outcode()
        self.assertEqual(new_properties["quantity"], 2)
        self.assertEqual(new_properties["average_price"], 125.00)
