// Copyright (c) 2026, shubham and contributors
// For license information, please see license.txt
frappe.ui.form.on("Airplane Ticket", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new() && frm.doc.flight) {
			frm.add_custom_button(
				__("Assign Seat"),
				() => {
					frappe
						.call({
							method: "airplane_mode.airplane_mode.doctype.airplane_ticket.airplane_ticket.get_available_seats",
							args: { flight: frm.doc.flight },
						})
						.then((r) => {
							const seats = r.message || [];
							if (!seats.length) {
								frappe.msgprint(__("No seats available on this flight"));
								return;
							}
							const d = new frappe.ui.Dialog({
								title: __("Select a Seat"),
								size: "extra-large",
								fields: [
									{
										fieldname: "seat_selector",
										fieldtype: "HTML",
									},
								],
								primary_action_label: __("Assign"),
								primary_action() {
									const selectedSeat = this.selectedSeat;

									if (!selectedSeat) {
										frappe.msgprint("Please select a seat");
										return;
									}

									frm.set_value("seat", selectedSeat);

									frappe
										.call({
											method: "airplane_mode.airplane_mode.doctype.airplane_ticket.airplane_ticket.assign_seat",
											args: {
												flight: frm.doc.flight,
												seat: selectedSeat,
												ticket: frm.doc.name,
											},
										})
										.then(() => {
											frm.reload_doc();
											d.hide();
										});
								},
							});

							d.show();

							const wrapper = d.fields_dict.seat_selector.$wrapper;
							wrapper.html("");

							const rootDiv = document.createElement("div");
							rootDiv.id = "seat-react-root";
							rootDiv.style.minHeight = "300px";
							rootDiv.style.display = "block";

							wrapper[0].appendChild(rootDiv);

							frappe.require("/assets/airplane_mode/react/index-B8luLr0x.js", () => {
								const el = wrapper.find("#seat-react-root")[0];
								if (el) {
									window.renderSeatSelector(el, seats, d);
								}
							});
						});
				},
				__("Action"),
			);
		}
	},

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
