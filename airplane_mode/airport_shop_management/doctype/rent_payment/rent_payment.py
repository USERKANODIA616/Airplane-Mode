# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class RentPayment(Document):
	def autoname(self):
		pd = get_datetime(self.payment_date)
		prefix = f"{self.shop}-{self.month}-{pd.day}/{pd.month}/{pd.year}"
		self.name=f"{prefix}"

	def after_delete(self):
		df=frappe.get_doc("Lease Contract Info",self.lease_contract)
		if df.pending_lease_months < df.total_lease_months:
			df.db_set(
				"pending_lease_months",
				df.pending_lease_months + 1
			)
		if df.workflow_state=="Close":
			df.db_set(
				"workflow_state","Approved"
			)
			sd=frappe.get_doc("Airport Shop",df.shop)
			sd.db_set("status","Occupied")

	def before_save(self):
		df=frappe.get_doc("Lease Contract Info",self.lease_contract)
		# if df.workflow_state!="Approved":
		# 	frappe.throw("First Approve Lease Contract")
		# try:
		# 	frappe.sendmail(
		# 		["temp.skanodia616@gmail.com"],
		# 		subject="Important Notification",
		# 		message="# Hello Bro! rent rec is ready",
		# 		as_markdown=True
		# 	)
		# except Exception as e:
		# 	frappe.throw(e)
