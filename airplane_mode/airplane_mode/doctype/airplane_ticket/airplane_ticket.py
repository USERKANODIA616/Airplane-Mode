# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt
import random
import string
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils.pdf import get_pdf
import base64


class AirplaneTicket(Document):
	def before_save(self):
		self.validate_seat()

	def set_seat(self):
		# if not self.seat:
			# number = random.randint(1, 99)
			# letter = random.choice(["A", "B", "C", "D", "E"])
			# self.seat = f"{number}{letter}"
		pass

	def before_submit():
		if not self.seat:
			frappe.throw("seat not set")

	def validate_seat(self):
		flight = frappe.get_doc("Airplane Flight", self.flight)

		booked_tickets = frappe.db.count("Airplane Ticket",{"flight": self.flight})

		airplane = frappe.get_doc("Airplane", flight.airplane)

		if booked_tickets >= airplane.capacity:
			frappe.throw("No more seats available for this flight")
			
	def total_calculation(self):
		total_amount = 0
		add_ons=[]
		
		for items in self.add_ons:
			total_amount += items.amount
			if items.item in add_ons:
				frappe.throw(f"In Add-ons {items.item} added multiple times")
			add_ons.append(items.item)

		self.total_amount = flt(total_amount) + flt(self.flight_price)

	def validate(self):
		self.validate_seat()
		self.total_calculation()

	def before_submit(self):
		if self.status != "Boarded":
			frappe.throw("Ticket can only be submitted if status is Boarded")

@frappe.whitelist()
def get_invoice_pdf(invoice_no):
	invoice_no = f"Qatar Airways-001-6-2026-00001-GPA-to-NWI-{invoice_no.zfill(3)}"
	html = frappe.get_print("Airplane Ticket",invoice_no,print_format="Airplane Ticket Invoice")
	pdf = get_pdf(html)

	return {
		"pdf": base64.b64encode(pdf).decode()
	}