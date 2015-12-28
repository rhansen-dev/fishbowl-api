import os
from unittest import TestCase
from lxml import etree
from decimal import Decimal

from fishbowl import objects

xml_filename = os.path.join(os.path.dirname(__file__), 'customer.xml')
with open(xml_filename) as xml_file:
    xml = xml_file.read()


class CustomerTest(TestCase):
    maxDiff = 5000

    def test_customer_object(self):
        el = etree.fromstring(xml)
        customer = objects.Customer(el)
        self.assertEqual(
            customer.squash(),
            {
                'ActiveFlag': True,
                'Addresses': [{
                    'AddressInformationList': {
                        'AddressInformation': {
                            'Data': 'Address Data',
                            'Default': True,
                            'Name': 'Main Office',
                            'Type': 'Home',
                        },
                    },
                    'Attn': 'Attention',
                    'City': 'Murray',
                    'Country': {'Code': 'US', 'Name': 'United States'},
                    'Default': True,
                    'Name': 'Main Office',
                    'Residential': False,
                    'State': {'Code': 'UT', 'CountryID': 2, 'Name': 'Utah'},
                    'Street': '123 Neverland dr.',
                    'Temp-Account': {'Type': 10},
                    'Type': 'Main Office',
                    'Zip': '84121',
                }],
                'CreditLimit': Decimal('1000000.00'),
                'CustomFields': [{
                    'Info': 'Custom Data',
                    'Name': 'Custom1',
                    'Type': 'CFT_TEXT',
                }],
                'DefPaymentTerms': 'COD',
                'DefShipTerms': 'Prepaid',
                'DefaultCarrier': 'USPS',
                'DefaultSalesman': 'jen',
                'JobDepth': 1,
                'Name': 'Sam Ball',
                'Note': 'Hello World',
                'Status': 'Normal',
                'TaxExempt': True,
                'TaxExemptNumber': '12345',
                'TaxRate': 'None'
            }
        )
