frappe.ui.form.on("Shop", {
	setup(frm) {
		frm.set_query("shop_type", () => ({
			filters: { enabled: 1 },
		}));
	},

	onload(frm) {
		if (frm.is_new() && !frm.doc.rent_amount) {
			frappe.db
				.get_single_value("Shop Settings", "default_rent_amount")
				.then((value) => {
					if (value) frm.set_value("rent_amount", value);
				});
		}
	},

	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(__("Contract History"), () => {
			frappe.set_route("query-report", "Shop Contract History", { shop: frm.doc.name });
		});

		if (frm.doc.status === "Available") {
			frm.add_custom_button(__("New Contract"), () => {
				frappe.new_doc("Shop Contract", {}, (doc) => {
					const row = frappe.model.add_child(doc, "Contract Shop", "shops");
					row.shop = frm.doc.name;
					row.shop_name = frm.doc.shop_name;
					row.rent_amount = frm.doc.rent_amount;
				});
			});
		}
	},
});
