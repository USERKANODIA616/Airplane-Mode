import frappe

def execute():
    tickets = frappe.get_all("Airplane Ticket",pluck="name")
    for t in tickets:
        try:
            ticket = frappe.get_doc("Airplane Ticket",t)
            ticket.assign_seat()
            ticket.save()
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                "Update Ticket Gate Numbers Job Failed"
            )
    frappe.db.commit()
