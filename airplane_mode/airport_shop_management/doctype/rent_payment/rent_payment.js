// Copyright (c) 2026, shubham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent Payment", {
	after_delete(frm) {
		frappe.set_route("List", "Rent Payment");
	},
});
