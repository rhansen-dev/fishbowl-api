from __future__ import unicode_literals
import os

from fishbowl import objects
from . import utils


class LocationTest(utils.ObjectTest):
    xml_filename = os.path.join(os.path.dirname(__file__), 'location.xml')
    fishbowl_object = objects.Location
    expected = {
        'LocationID': 1,
        'TypeID': 10,
        'ParentID': 0,
        'Name': 'Stock 100',
        'Description': 'The default location within the Stockroom.',
        'CountedAsAvailable': 1,
        'Default': 0,
        'Active': 0,
        'Pickable': 1,
        'Receivable': 1,
        'LocationGroupID': 1,
        'LocationGroupName': 0,
        'EnforceTracking': 1,
        'SortOrder': 0,
    }
