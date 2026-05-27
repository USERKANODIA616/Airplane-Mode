# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.naming import getseries
from frappe.utils import get_datetime


class AirplaneFlight(WebsiteGenerator):
	def before_submit(self):
		if self.status != "Completed":
			self.status = "Completed"
			
	def autoname(self):
		dt = get_datetime(self.creation)
		prefix = f"{self.airplane}-{dt.month}-{dt.year}-"
		series = getseries(prefix, 5)
		self.name=f"{prefix}{series}"
		
		