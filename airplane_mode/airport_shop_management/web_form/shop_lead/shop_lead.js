frappe.ready(function () {
	frappe.web_form.after_load = () => {
		const shop = frappe.utils.get_url_arg("shop");
		if (shop) {
			frappe.web_form.set_value("shop", shop);
		}
	};
});
