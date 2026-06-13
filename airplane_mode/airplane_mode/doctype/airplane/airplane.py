# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Airplane(Document):
	def validate(self):
		if not self.capacity > 0:
			frappe.throw("Capacity Is Must Be Grater Then 0.")

