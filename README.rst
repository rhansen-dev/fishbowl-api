============
Fishbowl API
============

A Python wrapper for the Fishbowl Inventory API.

Currently supports add inventory request, cycle inventory count::

	add_inventory(part_number, quantity, UOM_ID, cost, location_tag_num)
	cycle_inventory(part_number, new_qty, location_id)

Example usage::

	from fishbowl.api import Fishbowl

	fishbowl_api = Fishbowl()
	fishbowl_api.connect(username='admin', password='admin', host='10.0.2.2')
	fishbowl_api.add_inventory('B500', 5, 1, 50.00, 386)
	fishbowl_api.close()
