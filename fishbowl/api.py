from __future__ import unicode_literals
import base64
import socket
import struct
import hashlib
import functools
import logging
from lxml import etree

from . import xmlrequests, statuscodes

logger = logging.getLogger(__name__)


class FishbowlError(Exception):
    pass


def require_connected(func):
    """
    A decorator to wrap :cls:`Fishbowl` methods that can only be called after a
    connection to the API server has been made.
    """

    @functools.wraps(func)
    def dec(self, *args, **kwargs):
        if not self.connected:
            raise OSError('Not connected')
        return func(self, *args, **kwargs)

    return dec


class Fishbowl:
    """
    Fishbowl API.

    Example usage:
        fishbowl = Fishbowl()
        fishbowl.connect(username='admin', password='admin')
    """
    host = 'localhost'
    port = 28192

    def __init__(self):
        self._connected = False

    @property
    def connected(self):
        return self._connected

    def make_stream(self, timeout=5):
        """
        Create a connection to communicate with the API.
        """
        stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stream.connect((self.host, self.port))
        stream.settimeout(timeout)
        return stream

    def connect(self, username, password, host=None, port=None, timeout=5):
        """
        Open socket stream, set timeout, and log in.
        """
        password = base64.b64encode(
            hashlib.md5(password.encode('utf-8')).digest())

        if self.connected:
            self.close()

        if host:
            self.host = host
        if port:
            self.port = port
        self.stream = self.make_stream(timeout=timeout)
        self._connected = True

        try:
            self.key = None
            login_xml = xmlrequests.Login(username, password).request
            response = self.send_message(login_xml)
            # parse xml, grab api key, check status
            for element in response.iter():
                if element.tag == 'Key':
                    self.key = element.text
                if element.tag in ('loginRs', 'LoginRs'):
                    status_code = element.get('statusCode')
                    if status_code:
                        check_status(status_code)

            if not self.key:
                raise FishbowlError('No login key in response')
        except Exception:
            self.close(skip_errors=True)
            raise

    @require_connected
    def close(self, skip_errors=False):
        """
        Close connection to Fishbowl API.
        """
        self._connected = False
        self.key = None
        try:
            self.stream.close()
        except Exception:
            if not skip_errors:
                raise

    def pack_message(self, msg):
        """
        Calculate msg length and prepend to msg.
        """
        msg_length = len(msg)
        # '>L' = 4 byte unsigned long, big endian format
        packed_length = struct.pack('>L', msg_length)
        return packed_length + msg

    @require_connected
    def send_message(self, msg):
        """
        Send a message to the API and return the root element of the XML that
        comes back as a response.
        """
        if isinstance(msg, xmlrequests.Request):
            msg = msg.request
        self.stream.send(self.pack_message(msg))

        # Get response
        packed_length = self.stream.recv(4)
        length = struct.unpack('>L', packed_length)[0]
        byte_count = 0
        response = b''
        while byte_count < length:
            try:
                byte = self.stream.recv(1)
                byte_count += 1
                try:
                    response += byte.to_bytes(1, 'big')
                except AttributeError:   # Python 2
                    response += bytes(byte)
            except socket.timeout:
                self.close(skip_errors=True)
                raise FishbowlError('Connection Timeout')
        return etree.fromstring(response)

    @require_connected
    def add_inventory(self, partnum, qty, uomid, cost, loctagnum):
        """
        Add inventory.
        """
        request = xmlrequests.AddInventory(
            partnum, qty, uomid, cost, loctagnum, key=self.key)
        response = self.send_message(request)
        for element in response.iter():
            if element.tag != 'AddInventoryRs':
                continue
            status_code = element.get('statusCode')
            if status_code:
                check_status(status_code)
            logger.info(','.join((
                'add_inv', str(partnum), str(qty), str(uomid), str(cost),
                str(loctagnum))))

    @require_connected
    def cycle_inventory(self, partnum, qty, locationid):
        """
        Cycle inventory of part in Fishbowl.
        """
        request = xmlrequests.CycleCount(
            partnum, qty, locationid, key=self.key)
        response = self.send_message(request)
        for element in response.iter():
            if element.tag != 'CycleCountRs':
                continue
            status_code = element.get('statusCode')
            if status_code:
                check_status(status_code)
            logger.info(','.join((
                'cycle_inv', str(partnum), str(qty), str(locationid))))

    @require_connected
    def get_po_list(self, locationgroup):
        """
        Get list of POs.
        """
        request = xmlrequests.GetPOList(locationgroup, key=self.key)
        return self.send_message(request)


def check_status(code, expected=statuscodes.SUCCESS):
    """
    Check a status code, raising an exception if it wasn't the expected code.
    """
    message = statuscodes.get_status(code)
    if str(code) != expected:
        raise FishbowlError(message)
    return message
