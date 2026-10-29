import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("Shop"), "fieldname": "shop", "fieldtype": "Link", "options": "Shop", "width": 110},
		{"label": _("Shop Name"), "fieldname": "shop_name", "fieldtype": "Data", "width": 160},
		{"label": _("Tenant"), "fieldname": "tenant", "fieldtype": "Link", "options": "Tenant", "width": 150},
		{"label": _("Contract"), "fieldname": "contract", "fieldtype": "Link", "options": "Shop Contract", "width": 110},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Start"), "fieldname": "start_date", "fieldtype": "Date", "width": 100},
		{"label": _("End"), "fieldname": "end_date", "fieldtype": "Date", "width": 100},
		{"label": _("Monthly Rent"), "fieldname": "rent", "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	contract_filters = {}
	for key in ("tenant", "status"):
		if filters.get(key):
			contract_filters[key] = filters[key]

	contracts = frappe.get_list(
		"Shop Contract",
		filters=contract_filters,
		fields=["name", "tenant", "status", "contract_start_date", "contract_end_date"],
	)
	by_name = {c.name: c for c in contracts}
	if not by_name:
		return []

	shop_filters = {"parent": ["in", list(by_name)]}
	if filters.get("shop"):
		shop_filters["shop"] = filters["shop"]

	rows = frappe.get_all(
		"Contract Shop",
		filters=shop_filters,
		fields=["parent", "shop", "shop_name", "rent_amount"],
		parent_doctype="Shop Contract",
	)

	data = []
	for row in rows:
		contract = by_name[row.parent]
		data.append(
			{
				"shop": row.shop,
				"shop_name": row.shop_name,
				"tenant": contract.tenant,
				"contract": contract.name,
				"status": contract.status,
				"start_date": contract.contract_start_date,
				"end_date": contract.contract_end_date,
				"rent": row.rent_amount,
			}
		)

	# newest contract first within each shop
	data.sort(key=lambda d: str(d["start_date"]), reverse=True)
	data.sort(key=lambda d: d["shop"])
	return data
