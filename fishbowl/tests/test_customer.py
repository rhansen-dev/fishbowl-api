from unittest import TestCase
from lxml import etree
from decimal import Decimal

from fishbowl import objects

xml = '''
<Customer>
    <Status>Normal</Status>
    <DefPaymentTerms>COD</DefPaymentTerms>
    <DefShipTerms>Prepaid</DefShipTerms>
    <TaxRate>None</TaxRate>
    <Name>Sam Ball</Name>
    <CreditLimit>1000000.00</CreditLimit>
    <TaxExempt>true</TaxExempt>
    <TaxExemptNumber>12345</TaxExemptNumber>
    <Note>Hello World</Note>
    <ActiveFlag>true</ActiveFlag>
    <DefaultSalesman>jen</DefaultSalesman>
    <DefaultCarrier>USPS</DefaultCarrier>
    <JobDepth>1</JobDepth>
    <Addresses>
        <Address>
            <Temp-Account>
                <Type>10</Type>
            </Temp-Account>
            <Name>Main Office</Name>
            <Attn>Attention</Attn>
            <Street>123 Neverland dr.</Street>
            <City>Murray</City>
            <Zip>84121</Zip>
            <Default>true</Default>
            <Residential>false</Residential>
            <Type>Main Office</Type>
            <State>
                <Name>Utah</Name>
                <Code>UT</Code>
                <CountryID>2</CountryID>
            </State>
            <Country>
                <Name>United States</Name>
                <Code>US</Code>
            </Country>
            <AddressInformationList>
                <AddressInformation>
                    <Name>Main Office</Name>
                    <Data>Address Data</Data>
                    <Default>true</Default>
                    <Type>Home</Type>
                </AddressInformation>
            </AddressInformationList>
        </Address>
    </Addresses>
    <CustomFields>
        <CustomField>
            <Type>CFT_TEXT</Type>
            <Name>Custom1</Name>
            <Info>Custom Data</Info>
        </CustomField>
    </CustomFields>
</Customer>
'''


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
