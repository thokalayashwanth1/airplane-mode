frappe.ui.form.on("Shop Contract", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status !== "Active") return;

		frm.add_custom_button(__("Collect Rent"), () => {
			frappe.new_doc("Rent Payment", { contract: frm.doc.name });
		});

		frm.add_custom_button(__("Terminate Contract"), () => {
			frappe.confirm(__("Terminate this contract and free its shops?"), () => {
				frm.set_value("status", "Terminated");
				frm.save();
			});
		});
	},
});

frappe.ui.form.on("Contract Shop", {
	shop(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.shop) return;
		frappe.db.get_value("Shop", row.shop, "rent_amount").then((r) => {
			frappe.model.set_value(cdt, cdn, "rent_amount", r.message.rent_amount);
		});
	},
});
