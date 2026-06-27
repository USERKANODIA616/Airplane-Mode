# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.naming import getseries
from frappe import scrub
from frappe.utils import get_datetime,now_datetime

SEAT_LETTERS = ["A", "B", "C", "D", "E"]

class AirplaneFlight(WebsiteGenerator):
	def before_submit(self):
		if self.status != "Completed":
			frappe.throw("Flight status must be completed.")

	def on_submit(self):
		frappe.enqueue(
			"airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight.update_ticket_status",
			flight=self.name
    	)

	def after_insert(self):
		create_flight_seats(self.airplane,self.name)

	def on_trash(self):
		frappe.db.delete("Flight Seat", {"flight": self.name})

	def on_update(self):
		doc = self.get_doc_before_save()
		if doc and doc.gate_number!=self.gate_number:
			frappe.enqueue(
				"airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight.update_ticket_gate_numbers",
				flight=self.name,
				gate_number=self.gate_number
    		)

	def validate(self):
		if self.source_airport==self.destination_airport:
			frappe.throw("source Airport or destination airport must be different.")
		if get_datetime(self.date_of_departure) <= now_datetime():
			frappe.throw("Departure time must be later than the creation time.")
		if not self.route:
			site=f"flights/{self.name}"
			self.route = scrub(site)


	def autoname(self):
		dt = get_datetime(self.creation)
		prefix = f"{self.airplane}-{dt.month}-{dt.year}-"
		series = getseries(prefix, 5)
		self.name=f"{prefix}{series}"


def create_flight_seats(airplane,name):
	capacity = frappe.db.get_value("Airplane", airplane, "capacity")
	create = 0
	row = 1
	while create < capacity:
		for letter in SEAT_LETTERS:
			if create >= capacity:
				break
			seat_number = f"{row}{letter}"
			if not frappe.db.exists("Flight Seat", f"{name}-{seat_number}"):
				frappe.get_doc({
					"doctype": "Flight Seat",
					"flight": name,
					"seat_number": seat_number,
				}).insert(ignore_permissions=True)
			create += 1
		row += 1

	
def update_ticket_gate_numbers(flight,gate_number):
	try:
		doc=frappe.get_all("Airplane Ticket",filters={"flight":flight},fields=["name","gate_number"])
		for i in doc:
			if i.gate_number!=gate_number:
				frappe.db.set_value("Airplane Ticket",i.name,"gate_number",gate_number)
		frappe.db.commit()	
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(
			frappe.get_traceback(),
			"Update Ticket Gate Numbers Job Failed"
    	)

def update_ticket_status(flight):
	try:
		doc=frappe.get_all("Airplane Ticket",filters={"flight":flight,"docstatus":0},fields=["name","status"])
		for i in doc:
			ticket = frappe.get_doc("Airplane Ticket", i.name)
			ticket.db_set("status", "Boarded")
			ticket.submit()
	except Exception as e:
		# frappe.db.rollback()
		frappe.log_error(
			frappe.get_traceback(),
			"Update Ticket Status Job Failed"
    	)
@frappe.whitelist()
def cancel_flight(flight_name):
	flight_doc = frappe.get_doc("Airplane Flight",flight_name)
	if flight_doc.status == "Cancelled":
		frappe.throw("Flight is already Cancelled")

	flight_doc.status = "Cancelled"
	flight_doc.save(ignore_permissions=True)
	frappe.db.commit()

	return{
		"ticket": flight_doc.name,
		"status": flight_doc.status,
	}
