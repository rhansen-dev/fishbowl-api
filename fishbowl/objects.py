from __future__ import unicode_literals
import collections
import sys
import inspect
import datetime
import decimal

import six


def fishbowl_datetime(text):
    return datetime.strptime(text, '%Y-%m-%dT%H:%M:%S')


def fishbowl_boolean(text):
    if not text:
        return False
    if text.lower() in ('0', 'false', 'f'):
        return False
    return True


def all_fishbowl_objects():
    return dict(inspect.getmembers(
        sys.modules[__name__],
        lambda member: (
            inspect.isclass(member) and member.__module__ == __name__)
    ))


@six.python_2_unicode_compatible
class FishbowlObject(collections.Mapping):
    id_field = None
    name_attr = None

    def __init__(self, root_el=None, lazy_root_el=None, name=None):
        if not (root_el is None) ^ (lazy_root_el is None):
            raise AttributeError('Expected either root_el or lazy_root_el')
        self._lazy_load = lazy_root_el
        if root_el is not None:
            self.mapped = self.parse_fields(root_el, self.fields)
        self.name = name

    def __str__(self):
        if self.name:
            return self.name
        if not self.name_attr:
            return ''
        value = self
        for attr in self.name_attr.split('.'):
            value = value[attr]
        return value or ''

    def __bool__(self):
        return bool(self.mapped)

    __nonzero__ = __bool__

    @property
    def mapped(self):
        if not hasattr(self, '_mapped'):
            self._mapped = self.parse_fields(self._lazy_load(), self.fields)
        return self._mapped

    @mapped.setter
    def mapped(self, value):
        self._mapped = value

    def parse_fields(self, base_el, fields):
        output = {}
        items = fields.items()
        if self.id_field and 'ID' not in fields:
            items.append(('ID', int))
        for field_name, parser in items:
            el = self.get_child(base_el, field_name)
            if el is None:
                continue
            if isinstance(parser, dict):
                value = self.parse_fields(el, parser)
            elif isinstance(parser, list):
                value = []
                if parser:
                    classes = dict((cls.__name__, cls) for cls in parser)
                else:
                    classes = all_fishbowl_objects()
                for child in el:
                    child_parser = classes.get(child.tag)
                    if not child_parser:
                        continue
                    value.append(child_parser(child))
            elif isinstance(parser, FishbowlObject):
                value = parser(el)
            else:
                value = el.text
                if value is None:
                    continue
                if parser:
                    try:
                        value = parser(value)
                    except Exception:
                        continue
            output[field_name] = value
        if self.id_field and self.id_field not in output:
            value = output.pop('ID', None)
            if value:
                output[self.id_field] = value
        return output

    def get_child(self, el, name):
        for child in el:
            if child.tag == name:
                return child

    def __getitem__(self, key):
        return self.mapped[key]

    def __iter__(self):
        return iter(self.mapped)

    def __len__(self):
        return len(self.mapped)

    def squash(self):
        return self.squash_obj(self.mapped)

    def squash_obj(self, obj):
        if isinstance(obj, dict):
            return dict(
                (key, self.squash_obj(value)) for key, value in obj.items())
        if isinstance(obj, list):
            return [self.squash_obj(value) for value in obj]
        if isinstance(obj, FishbowlObject):
            return obj.squash()
        return obj


class CustomListItem(FishbowlObject):
    fields = {
        'ID': int,
        'Name': None,
        'Description': None,
    }


class CustomList(FishbowlObject):
    fields = {
        'ID': int,
        'Name': None,
        'Description': None,
        'CustomListItems': [CustomListItem]
    }


class CustomField(FishbowlObject):
    fields = {
        'ID': int,
        'Type': None,
        'Name': None,
        'Description': None,
        'SortOrder': int,
        'Info': None,
        'RequiredFlag': fishbowl_boolean,
        'ActiveFlag': fishbowl_boolean,
        'CustomList': CustomList,
    }


class Address(FishbowlObject):
    fields = {
        'ID': int,
        'Temp-Account': {
            'ID': int,
            'Type': int,
        },
        'Name': None,
        'Attn': None,
        'Street': None,
        'City': None,
        'Zip': None,
        'LocationGroupID': int,
        'Default': fishbowl_boolean,
        'Residential': fishbowl_boolean,
        'Type': None,
        'State': {
            'ID': int,
            'Code': None,
            'Name': None,
            'CountryID': int,
        },
        'Country': {
            'ID': int,
            'Name': None,
            'Code': None,
        },
        'AddressInformationList': {
            'AddressInformation': {
                'ID': int,
                'Name': None,
                'Data': None,
                'Default': fishbowl_boolean,
                'Type': None,
            }
        },
    }


class Customer(FishbowlObject):
    fields = {
        'CustomerID': int,
        'AccountID': int,
        'CustomerID': int,
        'AccountID': int,
        'Status': None,
        'DefPaymentTerms': None,
        'DefShipTerms': None,
        'TaxRate': None,
        'Name': None,
        'Number': None,
        'DateCreated': fishbowl_datetime,
        'DateLastModified': fishbowl_datetime,
        'LastChangedUser': None,
        'CreditLimit': decimal.Decimal,
        'TaxExempt': fishbowl_boolean,
        'TaxExemptNumber': None,
        'Note': None,
        'ActiveFlag': fishbowl_boolean,
        'AccountingID': None,
        'CurrencyName': None,
        'CurrencyRate': int,  # was double
        'DefaultSalesman': None,
        'DefaultCarrier': None,
        'DefaultShipService': None,
        'JobDepth': int,
        'QuickBooksClassName': None,
        'ParentID': int,
        'PipelineAccount': int,
        'URL': None,
        'Addresses': [Address],
        'CustomFields': [CustomField],
    }


class UOM(FishbowlObject):
    fields = {
        'UOMID': int,
        'Name': None,
        'Code': None,
        'Integral': fishbowl_boolean,
        'Active': fishbowl_boolean,
        'Type': None,
    }


class Part(FishbowlObject):
    id_field = 'PartID'
    fields = {
        'PartID': int,
        'PartClassID': int,
        'TypeID': int,
        'UOM': UOM,
        'UOMID': int,   # Used for light parts
        'Num': None,
        'Description': None,
        'Manufacturer': None,
        'Details': None,
        'TagLabel': None,
        'StandardCost': None,
        'HasBOM': fishbowl_boolean,
        'Configurable': fishbowl_boolean,
        'ActiveFlag': fishbowl_boolean,
        'SerializedFlag': fishbowl_boolean,
        'TrackingFlag': fishbowl_boolean,
        'UsedFlag': fishbowl_boolean,
        'Weight': int,
        'WeightUOMID': int,
        'Width': int,
        'Height': int,
        'Len': int,
        'SizeUOMID': int,
        'CustomFields': [CustomField],
        'VendorPartNums': None,
    }


class SalesOrderItem(FishbowlObject):
    fields = {
        'ID': int,
        'ProductNumber': None,
        'SOID': int,
        'Description': None,
        'CustomerPartNum': None,
        'Taxable': fishbowl_boolean,
        'Quantity': int,
        'ProductPrice': int,
        'TotalPrice': int,
        'UOMCode': None,
        'ItemType': int,
        'Status': int,
        'QuickBooksClassName': None,
        'NewItemFlag': fishbowl_boolean,
        'LineNumber': int,
        'KitItemFlag': fishbowl_boolean,
        'ShowItemFlag': fishbowl_boolean,
        'AdjustmentAmount': decimal.Decimal,
        'AdjustPercentage': int,
        'DateLastFulfillment': fishbowl_datetime,
        'DateLastModified': fishbowl_datetime,
        'DateScheduledFulfillment': fishbowl_datetime,
        'ExchangeSOLineItem': int,
        'ItemAdjustID': int,
        'QtyFulfilled': int,
        'QtyPicked': int,
        'RevisionLevel': int,
        'TotalCost': decimal.Decimal,
        'TaxableFlag': fishbowl_boolean,
    }


class Memo(FishbowlObject):
    fields = {
        'ID': int,
        'Memo': None,
        'UserName': None,
        'DateCreated': fishbowl_datetime,
    }


class SalesOrder(FishbowlObject):
    fields = {
        'ID': int,
        'Note': None,
        'TotalPrice': decimal.Decimal,
        'TotalTax': decimal.Decimal,
        'PaymentTotal': decimal.Decimal,
        'ItemTotal': decimal.Decimal,
        'Salesman': None,
        'Number': None,
        'Status': int,
        'Carrier': None,
        'FirstShipDate': fishbowl_datetime,
        'CreatedDate': fishbowl_datetime,
        'IssuedDate': fishbowl_datetime,
        'TaxRatePercentage': decimal.Decimal,
        'TaxRateName': None,
        'ShippingCost': decimal.Decimal,
        'ShippingTerms': None,
        'PaymentTerms': None,
        'CustomerContact': None,
        'CustomerName': None,
        'CustomerID': int,
        'FOB': None,
        'QuickBooksClassName': None,
        'LocationGroup': None,
        'PriorityId': int,
        'CurrencyRate': decimal.Decimal,
        'CurrencyName': None,
        'PriceIsInHomeCurrency': fishbowl_boolean,
        'BillTo': {
            'Name': None,
            'AddressField': None,
            'City': None,
            'Zip': None,
            'Country': None,
            'State': None,
        },
        'Ship': {
            'Name': None,
            'AddressField': None,
            'City': None,
            'Zip': None,
            'Country': None,
            'State': None,
        },
        'IssueFlag': fishbowl_boolean,
        'VendorPO': None,
        'CustomerPO': None,
        'UPSServiceID': int,
        'TotalIncludesTax': fishbowl_boolean,
        'TypeID': int,
        'URL': None,
        'Cost': decimal.Decimal,
        'DateCompleted': fishbowl_datetime,
        'DateLastModified': fishbowl_datetime,
        'DateRevision': fishbowl_datetime,
        'RegisterID': int,
        'ResidentialFlag': fishbowl_boolean,
        'SalesmanInitials': None,
        'CustomFields': [CustomField],
        'Memos': [Memo],
        'Items': [SalesOrderItem],
    }


class TaxRate(FishbowlObject):
    fields = {
        'ID': int,
        'Name': None,
        'Description': None,
        'Rate': decimal.Decimal,
        'TypeID': int,
        'VendorID': int,
        'DefaultFlag': fishbowl_boolean,
        'ActiveFlag': fishbowl_boolean,
    }
