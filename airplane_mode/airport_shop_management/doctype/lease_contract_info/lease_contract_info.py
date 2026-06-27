# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from frappe.utils import nowdate
from dateutil.relativedelta import relativedelta
import calendar
class LeaseContractInfo(Document):
	def validate(self):
		if self.start_date >= self.expiry_date:
			frappe.throw("Lease Start Date cannot be greater than or equal to Expiry Date")

	def autoname(self):
		sd = get_datetime(self.start_date)
		ed = get_datetime(self.expiry_date)
		prefix = f"{self.shop}-{sd.month}/{sd.year}-{ed.month}/{ed.year}"
		self.name=f"{prefix}"
		self.total_lease_months=(ed.year - sd.year) * 12 + (ed.month - sd.month)
		if ed.day > sd.day:
			self.total_lease_months += 1

	def before_save(self):
		old_doc = self.get_doc_before_save()
		if (old_doc and old_doc.workflow_state != "Reject" and self.workflow_state == "Approved"):
			self.pending_lease_months = self.total_lease_months
			self.upcoming_rent_day = get_datetime(self.start_date) + relativedelta(months=1)

		if self.workflow_state == "Approved":
			self.docstatus=1;
			
			frappe.db.set_value("Airport Shop", self.shop, "status", "Occupied")

		if self.workflow_state == "Close" or self.workflow_state == "Reject":
			sd=frappe.get_doc("Airport Shop",self.shop)
			sd.db_set("status","Available")
	

#crate rent payment

@frappe.whitelist()
def create_rent_payment(lease_contract):
	try:
		df=frappe.get_doc("Lease Contract Info",lease_contract)
		sd = get_datetime(df.start_date)
		
		if df.pending_lease_months > 0:
			diff=df.total_lease_months-df.pending_lease_months
			expected_month = ((sd.month + diff - 1) % 12) + 1
			# check last payment month 
			last_payment = frappe.get_all(
				"Rent Payment",
				filters={"lease_contract": lease_contract},
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


			doc = frappe.get_doc({
				"doctype": "Rent Payment",
				"month":calendar.month_name[expected_month],
				"lease_contract": lease_contract,
				"payment_date": nowdate()
			})
			doc.insert(ignore_permissions=True)
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

			return doc.name
		else:
			frappe.throw("No Rent Pending According to Lease Contract")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(
			title="Rent Payment Creation Error",
			message=frappe.get_traceback()
		)
		frappe.throw(f"Error while creating Rent Payment: {str(e)}")




