"""
Example use of api.

Create a fishbowl.ini file in this project root that looks something like
this::

    [connect]
    host = 192.168.1.10
    port = 28192
    timeout = 6000
    username = someuser
    password = somepassword

Then run::

    python fishbowl/__init__.py
"""

import datetime
import logging
import os
import sys
import json
from lxml import etree

from fishbowl.api import Fishbowl

try:
    import configparser
except ImportError:  # Python 2
    import ConfigParser as configparser

FILENAME = os.path.join(os.path.dirname(__file__), 'fishbowl.ini')


def run():
    config = configparser.ConfigParser()
    config.read(FILENAME)
    connect_options = dict(
        (key, config.get('connect', key)) for key in config.options('connect'))

    logging.basicConfig(
        filename='fishbowl.log',
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - '
        '%(message)s',
        datefmt='%H:%M:%S',
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # # set a format which is simpler for console use
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    fishbowl = Fishbowl()
    fishbowl.connect(**connect_options)

    if len(sys.argv) > 1:
        value = None
        if len(sys.argv) > 2:
            value = json.loads(sys.argv[2])
        response = fishbowl.send_request(sys.argv[1], value)
        return etree.tostring(response)

    # fishbowl.send_request(
    #     'GetSOListRq',
    #     {
    #         'DateCreatedEnd': datetime.datetime(1900, 1, 1),
    #     }
    # )
    # fishbowl.send_request('GetPartListRq')
    # with open('LightPartListRq.xml', 'w') as f:
    #     f.write(etree.tostring(fishbowl.send_request('LightPartListRq')))
    # response = fishbowl.send_request('GetShipListRq')

    response = fishbowl.send_request('CustomerNameListRq')
    return etree.tostring(response)
