# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FlightSeat(Document):
	_DOCTYPE_NAME = "Flight Seat"
	def autoname(self):
		prefix = f"{self.flight}-{self.seat_number}"
		self.name=f"{prefix}"

