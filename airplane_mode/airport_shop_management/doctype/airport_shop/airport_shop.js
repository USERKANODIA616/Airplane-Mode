// Copyright (c) 2026, shubham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airport Shop", {
	refresh(frm) {
		cur_frm.add_custom_button(__("Check History"), function () {
			frappe.db
				.get_list("Lease Contract Info", {
					filters: {
						shop: cur_frm.doc.name,
					},
					fields: ["tenant"],
					limit: 0,
				})
				.then((res) => {
					let tenants = res.map((r) => r.tenant.trim());
					frappe.msgprint({
						title: __("History Of Shops"),
						message: tenants.join("<br><br>"),
					});
				});
		});
	},
});
