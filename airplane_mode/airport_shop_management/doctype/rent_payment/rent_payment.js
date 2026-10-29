frappe.ui.form.on("Rent Payment", {
	setup(frm) {
		frm.set_query("contract", () => ({
			filters: { status: ["!=", "Terminated"] },
		}));
	},

	contract(frm) {
		if (!frm.doc.contract) return;

		// suggest the first month that is still unpaid
		frappe.db.get_doc("Shop Contract", frm.doc.contract).then((contract) => {
			const next = (contract.payment_schedule || []).find((row) => !row.paid);
			if (next) frm.set_value("rent_for_month", next.due_month);
		});
	},
});
