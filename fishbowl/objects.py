import collections
import sys
import inspect
import datetime
import decimal


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


class FishbowlObject(collections.Mapping):

    def __init__(self, root_el):
        self.mapped = self.parse_fields(root_el, self.fields)

    def parse_fields(self, base_el, fields):
        output = {}
        for field_name, parser in fields.items():
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
            return dict((key, self.squash_obj(value)) for key, value in obj.items())
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
