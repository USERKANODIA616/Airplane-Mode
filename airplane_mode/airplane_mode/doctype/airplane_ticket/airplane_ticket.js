// Copyright (c) 2026, shubham and contributors
// For license information, please see license.txt
frappe.ui.form.on("Airplane Ticket", {
	flight_price(frm) {
		frm.trigger("update_total_amount");
	},

	update_total_amount(frm) {
		let total_amount = 0;
		for (let item of frm.doc.add_ons) {
			total_amount += item.amount;
		}
		frm.set_value("total_amount", total_amount + frm.doc.flight_price);
	},
});
frappe.ui.form.on("Airplane Ticket Add-on Item", {
	amount(frm) {
		frm.trigger("update_total_amount");
	},
	add_ons_remove(frm) {
		frm.trigger("update_total_amount");
	},
});
