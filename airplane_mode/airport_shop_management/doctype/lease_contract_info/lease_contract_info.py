# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from frappe.utils import nowdate
from dateutil.relativedelta import relativedelta
import calendar

class LeaseContractInfo(Document):
	def autoname(self):
		sd = get_datetime(self.start_date)
		ed = get_datetime(self.expiry_date)
		prefix = f"{self.shop}-{sd.month}/{sd.year}-{ed.month}/{ed.year}"
		self.name=f"{prefix}"
	
	def monthCalculator(self):
		sd = get_datetime(self.start_date)
		ed = get_datetime(self.expiry_date)
		return (ed.year - sd.year) * 12 + (ed.month - sd.month)

	def validate(self):
		self.total_lease_months=self.monthCalculator()

	def before_submit(self):
		self.pending_lease_months=self.total_lease_months;
		self.upcoming_rent_day=get_datetime(self.start_date) + relativedelta(months=1)
		sd=frappe.get_doc("Airport Shop",self.shop)
		sd.db_set("status","Occupied")
	
	def before_delete(self):
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
			diff = ((sd.month + diff - 1) % 12) + 1
			doc = frappe.get_doc({
				"doctype": "Rent Payment",
				"month":calendar.month_name[diff],
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

			return doc.name
		else:
			frappe.throw("No Rent Pending According to Lease Contract")
	except Exception as e:
		frappe.log_error(
			title="Rent Payment Creation Error",
			message=frappe.get_traceback()
		)
		frappe.throw(f"Error while creating Rent Payment: {str(e)}")




