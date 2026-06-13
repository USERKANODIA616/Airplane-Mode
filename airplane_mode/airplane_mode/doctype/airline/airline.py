# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class Airline(Document):
	def validate(self):
		if self.founding_year < now_datetime().year:
			frappe.throw("Founding year cannot be greater than the current year.")
		if self.founding_year < now_datetime().year - 500:
			frappe.throw("Invalid founding year.")
