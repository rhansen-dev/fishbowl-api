import os
from unittest import TestCase
from lxml import etree

from fishbowl import objects

xml_filename = os.path.join(os.path.dirname(__file__), 'part.xml')
with open(xml_filename) as xml_file:
    xml = xml_file.read()


class CustomerTest(TestCase):
    maxDiff = 5000

    def test_customer_object(self):
        el = etree.fromstring(xml)
        part = objects.Part(el)
        self.assertEqual(
            part.squash(),
            {
              'ActiveFlag': True,
              'Configurable': True,
              'Description': 'Custom Value Bike',
              'HasBOM': False,
              'Height': 0,
              'Len': 0,
              'Num': 'BB2005',
              'PartClassID': 0,
              'PartID': 60,
              'SerializedFlag': True,
              'StandardCost': '0',
              'TrackingFlag': True,
              'TypeID': 10,
              'Weight': 0,
              'Width': 0,
            }
          )
