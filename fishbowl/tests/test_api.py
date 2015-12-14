from unittest import TestCase
from lxml import etree
import struct

from fishbowl import api, statuscodes

try:
    from unittest import mock
except ImportError:   # < Python 3.3
    import mock


LOGIN_SUCCESS = etree.fromstring('''
<FbiXml>
<Key>ABC</Key>
<statusCode>{0}</statusCode>
</FbiXml>
'''.format(statuscodes.SUCCESS))


class APIStreamTest(TestCase):

    @mock.patch('fishbowl.api.socket')
    def test_make_stream(self, mock_socket):
        api.Fishbowl().make_stream()
        self.assertTrue(mock_socket.socket.called)
        fake_socket = mock_socket.socket()
        self.assertTrue(fake_socket.connect)
        # Check default timeout set.
        fake_socket.settimeout.assert_called_with(5)


class APITest(TestCase):

    def setUp(self):
        self.api = api.Fishbowl()
        self.fake_stream = mock.MagicMock()
        self.api.make_stream = mock.Mock(return_value=self.fake_stream)

    def connect(self):
        self.api.send_message = mock.Mock(return_value=LOGIN_SUCCESS)
        self.api.connect(username='test', password='password')
        del self.api.send_message

    def test_connect(self):
        self.assertFalse(self.api.connected)
        self.connect()
        self.assertTrue(self.api.make_stream.called)
        self.assertTrue(self.api.connected)

        self.api.close()
        self.assertTrue(self.fake_stream.close.called)
        self.assertFalse(self.api.connected)

    def test_required_connected_method(self):
        self.assertRaises(OSError, self.api.close)

    def test_send_message(self):
        self.connect()
        request_xml = b'<test></test>'
        response_xml = b'<FbiXml><FbiMsgsRq/></FbiXml>'
        self.fake_stream.recv.side_effect = [
            struct.pack('>L', len(response_xml))
        ] + list(response_xml)
        response = self.api.send_message(request_xml)
        self.assertEqual(etree.tostring(response), response_xml)
        self.fake_stream.send.assert_called_with(
            struct.pack('>L', len(request_xml)) + request_xml)
