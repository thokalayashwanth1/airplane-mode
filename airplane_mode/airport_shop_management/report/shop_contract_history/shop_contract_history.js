frappe.query_reports["Shop Contract History"] = {
	filters: [
		{ fieldname: "shop", label: __("Shop"), fieldtype: "Link", options: "Shop" },
		{ fieldname: "tenant", label: __("Tenant"), fieldtype: "Link", options: "Tenant" },
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nActive\nExpired\nTerminated",
		},
	],
};
