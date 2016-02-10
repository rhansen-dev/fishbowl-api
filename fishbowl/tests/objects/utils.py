from unittest import TestCase
from lxml import etree


class ObjectTest(TestCase):
    xml_filename = None
    fishbowl_object = None
    expected = None

    maxDiff = 5000

    def test_object(self):
        with open(self.xml_filename) as xml_file:
            xml = xml_file.read()
        el = etree.fromstring(xml)
        object_instance = self.fishbowl_object(el)
        self.assertEqual(self.expected, object_instance.squash())
