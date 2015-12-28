import os
from unittest import TestCase
from lxml import etree
from decimal import Decimal

from fishbowl import objects

xml_filename = os.path.join(os.path.dirname(__file__), 'taxrate.xml')
with open(xml_filename) as xml_file:
    xml = xml_file.read()


class TaxRateTest(TestCase):
    maxDiff = 5000

    def test_object(self):
        el = etree.fromstring(xml)
        obj = objects.TaxRate(el)
        self.assertEqual(
            obj.squash(),
            {
                'ActiveFlag': True,
                'DefaultFlag': True,
                'ID': 2,
                'Name': 'Tax',
                'Rate': Decimal('0.05'),
                'TypeID': 10,
                'VendorID': 6,
            }
        )
