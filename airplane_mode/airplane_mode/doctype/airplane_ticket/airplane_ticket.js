frappe.ui.form.on("Airplane Ticket", {
	refresh(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(
				__("Assign Seat"),
				() => {
					const dialog = new frappe.ui.Dialog({
						title: __("Select Seat"),
						fields: [
							{
								label: __("Seat Number"),
								fieldname: "seat",
								fieldtype: "Data",
								reqd: 1,
								default: frm.doc.seat,						
							},
						],
						primary_action_label: __("Assign"),
						primary_action(values) {
							frm.set_value("seat", values.seat);
							dialog.hide();
						},
					});
					dialog.show();
				},
				__("Actions")
			);
		}
	},
});
