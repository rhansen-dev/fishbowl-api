from unittest import TestCase
from lxml import etree

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


class APITest(TestCase):

    def setUp(self):
        self.api = api.Fishbowl()
        self.fake_stream = mock.MagicMock()
        self.api.make_stream = mock.Mock(return_value=self.fake_stream)

    def test_connect(self):
        self.api.send_message = mock.Mock(return_value=LOGIN_SUCCESS)
        self.api.connect(username='test', password='password')
