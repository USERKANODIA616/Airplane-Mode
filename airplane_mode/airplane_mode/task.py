import frappe
from frappe.utils import get_datetime,getdate,nowdate,today
from dateutil.relativedelta import relativedelta

def mailThis(due_date,emailAddress):
    if due_date <= getdate(today()):
        frappe.sendmail(recipients=emailAddress,subject="Rent Reminder",message="Please pay your monthly rent.")

def send_rent_reminders():
    leases = frappe.get_all("Lease Contract Info",filters={"workflow_state": "Approved"},fields=["name", "tenant.email","start_date","disable_notification"])
    for l in leases:
        if l.disable_notification == 0:
            rent = frappe.get_all("Rent Payment",filters={"docstatus":1, "lease_contract": l.name},fields=["payment_date"],order_by="payment_date desc",limit=1)
            if rent:
                due_date = getdate(rent[0].payment_date) + relativedelta(months=1)
                mailThis(due_date,l.email)
            else:
                due_date = l.start_date + relativedelta(months=1)
                mailThis(due_date,l.email)