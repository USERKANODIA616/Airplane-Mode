# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AirportShop(Document):
	def before_save(self):
		self.shop_name = self.shop_name.title()

	def autoname(self):
		prefix = f"{self.airport_code}-{self.shop_name.title()}-{self.shop_number}"	
		self.name=f"{prefix}"
