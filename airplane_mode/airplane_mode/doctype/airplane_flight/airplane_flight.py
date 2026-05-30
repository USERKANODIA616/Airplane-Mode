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

	def on_update(self):
		doc = self.get_doc_before_save()
		if doc and doc.gate_number!=self.gate_number:
			frappe.enqueue(
				"airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight.update_ticket_gate_numbers",
				flight=self.name,
				gate_number=self.gate_number
    		)

	def autoname(self):
		dt = get_datetime(self.creation)
		prefix = f"{self.airplane}-{dt.month}-{dt.year}-"
		series = getseries(prefix, 5)
		self.name=f"{prefix}{series}"
		
def update_ticket_gate_numbers(flight,gate_number):
	try:
		doc=frappe.get_all("Airplane Ticket",filters={"flight":flight},fields=["name","gate_number"])
		for i in doc:
			if i.gate_number!=gate_number:
				frappe.db.set_value("Airplane Ticket",i.name,"gate_number",gate_number)
		frappe.db.commit()
	except Exception as e:
		frappe.db.rollback()
		frappe.errorlog(e)