# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.fixtures import export_fixtures


class ShopType(Document):
	def on_update(self):
		export_fixtures()