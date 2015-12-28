import os
from unittest import TestCase
from lxml import etree
from decimal import Decimal

from fishbowl import objects

xml_filename = os.path.join(os.path.dirname(__file__), 'so.xml')
with open(xml_filename) as xml_file:
    xml = xml_file.read()


class SalesOrderTest(TestCase):
    maxDiff = 5000

    def test_salesorder_object(self):
        el = etree.fromstring(xml)
        sales_order = objects.SalesOrder(el)
        self.assertEqual(
            sales_order.squash(),
            {
                'BillTo': {
                    'AddressField': '555 Suntan Ave.',
                    'City': 'Santa Barbara',
                    'Name': 'Beach Bike',
                    'Zip': '93101',
                },
                'Carrier': 'Will Call',
                'CustomerContact': 'Beach Bike',
                'CustomerName': 'Beach Bike',
                'FOB': 'Origin',
                'Items': [
                    {
                        'Description': 'Battery Pack',
                        'ID': -1,
                        'ItemType': 10,
                        'LineNumber': 1,
                        'NewItemFlag': False,
                        'ProductNumber': 'BTY100',
                        'Quantity': 1,
                        'QuickBooksClassName': 'Salt Lake City',
                        'SOID': 93,
                        'Status': 10,
                        'Taxable': True,
                        'UOMCode': 'ea',
                    },
                ],
                'LocationGroup': 'SLC',
                'Number': '500100',
                'PaymentTerms': 'COD',
                'PriorityId': 30,
                'QuickBooksClassName': 'Salt Lake City',
                'Salesman': 'admin',
                'Ship': {
                    'AddressField': '555 Suntan Ave.',
                    'Country': 'US',
                    'Name': 'Beach Bike',
                    'State': 'California',
                    'Zip': '93101',
                },
                'ShippingTerms': 'Prepaid & Billed',
                'Status': 20,
                'TaxRateName': 'Utah',
                'TaxRatePercentage': Decimal('0.0625'),
            }
        )
