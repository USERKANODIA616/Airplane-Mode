# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt
import frappe
import string
import random
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils.pdf import get_pdf
import base64


class AirplaneTicket(Document):
	def before_insert(self):
		self.assign_seat()

	def after_insert(self):
		# document is in the DB now and has a name, so we can link the seat to it
		book_seat(self.flight, self.seat, self.name)

	def on_update(self):
		before = self.get_doc_before_save()
		before = self.get_doc_before_save()
		if before and before.seat != self.seat:
			release_seat(before.flight, before.seat)
			book_seat(self.flight, self.seat, self.name)

	def before_submit(self):
		if not self.seat:
			self.assign_seat()
		if self.status != "Boarded":
			frappe.throw("Ticket can only be submitted if status is Boarded")

	def validate_seat(self):
		flight = frappe.get_doc("Airplane Flight", self.flight)

		booked_tickets = frappe.db.count("Airplane Ticket",{"flight": self.flight,"docstatus": ["!=", 2]})

		airplane = frappe.get_doc("Airplane", flight.airplane)

		if booked_tickets >= airplane.capacity:
			frappe.throw("No more seats available for this flight")
			
	def total_calculation(self):
		total_amount = 0
		add_ons=[]
		
		for items in self.add_ons:
			total_amount += items.amount
			if items.item in add_ons:
				# frappe.throw(f"In Add-ons {items.item} added multiple times")
				frappe.msgprint(
					"Add-on already exists",
					title="Warning",
					indicator="orange"
				)
				self.add_ons.remove(items)
			add_ons.append(items.item)

		self.total_amount = flt(total_amount) + flt(self.flight_price)

	def validate(self):
		if not self.is_new():
			old_doc = self.get_doc_before_save()

			if old_doc and old_doc.flight != self.flight:
				frappe.throw("Flight cannot be changed after creation")
		self.total_calculation()


	def assign_seat(self):
		if not self.seat:
			available = frappe.get_all(
				"Flight Seat",
				filters={"flight": self.flight, "status": "Available"},
				pluck="seat_number",
				order_by="creation asc",
				limit=1,
			)
			if not available:
				frappe.throw(f"No more seats available on flight {self.flight}")
			self.seat = available[0]

@frappe.whitelist()
def get_invoice_pdf(invoice_no):
	invoice_no = f"Qatar Airways-001-6-2026-00001-GPA-to-NWI-{invoice_no.zfill(3)}"
	html = frappe.get_print("Airplane Ticket",invoice_no,print_format="Airplane Ticket Invoice")
	pdf = get_pdf(html)

	return {
		"pdf": base64.b64encode(pdf).decode()
	}

@frappe.whitelist()
def book_airplane_ticket(passenger, flight):
	flight_doc = frappe.get_doc("Airplane Flight", flight)
	passenger_doc = frappe.db.get_value("Flight Passenger",{"full_name":passenger},"name")
	if flight_doc.status == "Cancelled":
		frappe.throw("Flight is cancelled")
	ticket = frappe.new_doc("Airplane Ticket")
	ticket.passenger = passenger_doc
	ticket.flight = flight_doc.name
	ticket.status = "Booked"
	ticket.insert()

	return {
		"ticket": ticket.name,
		"status": ticket.status,
		"total_amount":ticket.total_amount
	}

def book_seat(flight, seat_number, ticket):
	seat_name = f"{flight}-{seat_number}"

	status = frappe.db.get_value("Flight Seat", seat_name, "status", for_update=True)

	if status is None:
		frappe.throw(f"Seat {seat_number} does not exist on flight {flight}")

	if status == "Booked" and frappe.db.get_value("Flight Seat", seat_name, "ticket") != ticket:
		frappe.throw(f"Seat {seat_number} is already booked on this flight")

	frappe.db.set_value("Flight Seat", seat_name, {"status": "Booked", "ticket": ticket})


def release_seat(flight, seat_number):
	seat_name = f"{flight}-{seat_number}"
	if frappe.db.exists("Flight Seat", seat_name):
		frappe.db.set_value("Flight Seat", seat_name, {"status": "Available", "ticket": None})


@frappe.whitelist()
def get_available_seats(flight):
	frappe.has_permission("Airplane Ticket", throw=True)
	return  frappe.get_all(
        "Flight Seat",
        filters={"flight": flight},
        fields=["seat_number", "status"],
        order_by="seat_number asc"
    )

@frappe.whitelist()
def assign_seat(flight,seat,ticket):
	ticket_doc = frappe.get_doc("Airplane Ticket", ticket)

	if ticket_doc.seat and ticket_doc.seat != seat:
		release_seat(flight, ticket_doc.seat)
	ticket_doc.seat = seat
	ticket_doc.save(ignore_permissions=True)
	book_seat(flight, seat, ticket)
	return True
