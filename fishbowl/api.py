from __future__ import unicode_literals
import base64
import socket
import struct
import hashlib
import datetime
import functools
from lxml import etree

from . import xmlrequests, statuscodes


class FishbowlError(Exception):
    pass


def require_connected(func):

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

    def connect(self, username, password, host=None, port=None, timeout=5):
        """
        Open socket stream, set timeout, and log in.
        """
        password = base64.b64encode(hashlib.md5(password.encode('utf-8')).digest())

        if self.connected:
            self.close()

        if host:
            self.host = host
        if port:
            self.port = port
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.connect((self.host, self.port))
        self.stream.settimeout(timeout)
        self._connected = True

        try:
            self.key = None
            login_xml = xmlrequests.Login(username, password).request
            response = self.send_message(login_xml)
            # parse xml, grab api key, check status
            for element in xmlparse(response).iter():
                if element.tag == 'Key':
                    self.key = element.text
                status_code = element.get('statusCode')
                if status_code and element.tag == 'LoginRs':
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
        try:
            self.stream.close()
        except Exception:
            if not skip_errors:
                raise
        self._connected = False
        self.key = None

    @require_connected
    def send_message(self, msg):
        if isinstance(msg, xmlrequests.Request):
            msg = msg.request

        # Calculate msg length and prepend to msg.
        msg_length = len(msg)
        # '>L' = 4 byte unsigned long, big endian format
        packed_length = struct.pack('>L', msg_length)
        msg = packed_length + msg
        self.stream.send(msg)

        # Get response
        packed_length = self.stream.recv(4)
        length = struct.unpack('>L', packed_length)
        byte_count = 0
        response = ''
        while byte_count < length[0]:
            try:
                byte = self.stream.recv(1)
                byte_count += 1
                response += byte
            except socket.timeout:
                self.close(skip_errors=True)
                raise FishbowlError('Connection Timeout')
        return response

    @require_connected
    def add_inventory(self, partnum, qty, uomid, cost, loctagnum, log=False):
        """
        Add inventory.
        """
        request = xmlrequests.AddInventory(
            partnum, qty, uomid, cost, loctagnum, key=self.key)
        # send request to fishbowl server
        response = self.send_message(request)
        # parse xml, check status
        for element in xmlparse(response).iter():
            if element.tag != 'AddInventoryRs':
                continue
            status_code = element.get('statusCode')
            if status_code:
                check_status(status_code)
            if log:
                with open('api_log.txt', 'a') as f:
                    f.write(','.join(
                        'add_inv', str(datetime.now()), str(partnum), str(qty),
                        str(uomid), str(cost), str(loctagnum)))
                    f.write('\n')

    @require_connected
    def cycle_inventory(self, partnum, qty, locationid, log=False):
        """
        Cycle inventory of part in Fishbowl.
        """
        request = xmlrequests.CycleCount(
            partnum, qty, locationid, key=self.key)
        response = self.send_message(request)
        for element in xmlparse(response).iter():
            if element.tag != 'CycleCountRs':
                continue
            status_code = element.get('statusCode')
            if status_code:
                check_status(status_code)
            if log:
                with open('api_log.txt', 'a') as f:
                    f.write(','.join(
                        'cycle_inv', str(datetime.now()), str(partnum),
                        str(qty), str(locationid)))
                    f.write('\n')

    @require_connected
    def get_po_list(self, locationgroup):
        """
        Get list of POs.
        """
        request = xmlrequests.GetPOList(locationgroup, key=self.key)
        return self.send_message(request)


def xmlparse(xml):
    """ global function for parsing xml """
    root = etree.fromstring(xml)
    return root


def check_status(code, expected=statuscodes.SUCCESS):
    message = statuscodes.get_status(code)
    if str(code) != expected:
        raise FishbowlError(message)
    return message
