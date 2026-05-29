// Copyright (c) 2026, shubham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lease Contract Info", {
	refresh(frm) {
		if (frm.doc.workflow_state == "Approved") {
			frm.add_custom_button(
				__("Receipt"),
				() => {
					frappe.call({
						method: "airplane_mode.airport_shop_management.doctype.lease_contract_info.lease_contract_info.create_rent_payment",
						args: {
							lease_contract: frm.doc.name,
						},
						callback: function (r) {
							if (r.message) {
								frappe.msgprint({
									title: __("Success"),
									indicator: "green",
									message: `Rent Payment Created:
												<br>
												<a href="/app/rent-payment/${r.message}">
													${r.message}
												</a>
											`,
								});
							}
						},
					});
				},
				__("Action"),
			);
		}
	},
});
