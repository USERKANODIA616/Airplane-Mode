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

	def validate(self):
		try:
			df=frappe.get_doc("Lease Contract Info",self.lease_contract)
			sd = get_datetime(df.start_date)
			
			if df.pending_lease_months > 0:
				diff=df.total_lease_months-df.pending_lease_months
				expected_month = ((sd.month + diff - 1) % 12) + 1 
				# check last payment month 
				last_payment = frappe.get_all(
					"Rent Payment",
					filters={"lease_contract": self.lease_contract},
					fields=["month"],
					order_by="creation desc",
					limit=1
				)
				month_map = {
					"January": 1,
					"February": 2,
					"March": 3,
					"April": 4,
					"May": 5,
					"June": 6,
					"July": 7,
					"August": 8,
					"September": 9,
					"October": 10,
					"November": 11,
					"December": 12,
				}
				if last_payment:
					last_month = month_map[last_payment[0].month]

					next_month = (last_month % 12) + 1

					if expected_month != next_month:
						frappe.throw(
							f"Expected rent for {calendar.month_name[next_month]}"
						)

				new_pending_lease_month = df.pending_lease_months - 1
				df.db_set(
					"pending_lease_months",
					new_pending_lease_month
				)
				if new_pending_lease_month==0:
					df.db_set("workflow_state","Close")
					sd=frappe.get_doc("Airport Shop",df.shop)
					sd.db_set("status","Available")

				df.db_set(
					"upcoming_rent_day",
					get_datetime(df.upcoming_rent_day) + relativedelta(months=1)
				)
			else:
				frappe.throw("No Rent Pending According to Lease Contract")
		except Exception as e:
			frappe.db.rollback()
			frappe.log_error(
				title="Rent Payment Creation Error",
				message=frappe.get_traceback()
			)
			frappe.throw(f"Error while creating Rent Payment: {str(e)}")


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
