# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt
import random
import string
import frappe
from frappe.model.document import Document
from frappe.utils import flt


class AirplaneTicket(Document):
	def before_save(self):
		self.set_seat()

	def set_seat(self):
		if not self.seat:
			number = random.randint(1, 99)
			letter = random.choice(["A", "B", "C", "D", "E"])
			self.seat = f"{number}{letter}"

	def validate(self):
		total_amount = 0
		add_ons=[]
		
		for items in self.add_ons:
			total_amount += items.amount
			if items.item in add_ons:
				frappe.throw(f"In Add-ons {items.item} added multiple times")
			add_ons.append(items.item)

		self.total_amount = flt(total_amount) + flt(self.flight_price)

	def before_submit(self):
		if self.status != "Boarded":
			frappe.throw("Ticket can only be submitted if status is Boarded")