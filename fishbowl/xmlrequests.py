from lxml import etree


class Request(object):
    key_required = True

    def __init__(self, key=''):
        if self.key_required and not key:
            raise TypeError(
                "An API key was not provided (not enough arguments for {0} "
                "request)".format(self.__class__.__name__))
        self.el_root = etree.Element('FbiXml')
        el_ticket = etree.SubElement(self.el_root, 'Ticket')
        el_key = etree.SubElement(el_ticket, 'Key')
        el_key.text = key
        self.el_request = etree.SubElement(self.el_root, 'FbiMsgsRq')

    @property
    def request(self):
        return etree.tostring(self.el_root, pretty_print=True)

    def add_elements(self, parent, elements):
        if isinstance(elements, dict):
            elements = elements.items()
        for name, value in elements:
            el = etree.SubElement(parent, name)
            if value is not None:
                el.text = str(value)


class Login(Request):
    key_required = False

    def __init__(self, username, password, key=''):
        Request.__init__(self, key)
        el_rq = etree.SubElement(self.el_request, 'LoginRq')
        self.add_elements(el_rq, {
            'IAID': '22',
            'IAName': 'PythonApp',
            'IADescription': 'Connection for Python Wrapper',
            'UserName': username,
            'UserPassword': password,
        })


class SimpleRequest(object):

    def __init__(self, request_name, value=None, key=''):
        Request.__init__(self, key)
        el = etree.SubElement(self.el_request, request_name)
        if value is not None:
            el.text = str(value)


class AddInventory(Request):

    def __init__(
            self, partnum, qty, uomid, cost, loctagnum, note='', tracking='',
            key=''):
        Request.__init__(self, key)
        el_rq = etree.SubElement(self.el_request, 'AddInventoryRq')
        self.add_elements(el_rq, {
            'PartNum': partnum,
            'Quantity': qty,
            'UOMID': uomid,
            'Cost': cost,
            'Note': note,
            'Tracking': tracking,
            'LocationTagNum': loctagnum,
            'TagNum': '0',
        })


class CycleCount(Request):

    def __init__(self, partnum, qty, locationid, tracking='', key=''):
        Request.__init__(self, key)
        el_rq = etree.SubElement(self.el_request, 'CycleCountRq')
        self.add_elements(el_rq, {
            'PartNum': partnum,
            'Quantity': qty,
            'LocationID': locationid,
        })


class GetPOList(Request):

    def __init__(self, locationgroup, key=''):
        Request.__init__(self, key)
        el_rq = etree.SubElement(self.el_request, 'GetPOListRq')
        self.add_elements(el_rq, {
            'LocationGroup': locationgroup,
        })
