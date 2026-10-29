import frappe
from frappe import _


def execute(filters=None):
    return get_columns(), get_data()


def get_columns():
    return [
        {"label": _("Airport"), "fieldname": "airport", "fieldtype": "Link", "options": "Airport", "width": 180},
        {"label": _("Total Shops"), "fieldname": "total", "fieldtype": "Int", "width": 110},
        {"label": _("Available"), "fieldname": "available", "fieldtype": "Int", "width": 110},
        {"label": _("Occupied"), "fieldname": "occupied", "fieldtype": "Int", "width": 110},
    ]


def get_data():
    airports = frappe.get_list("Airport", pluck="name", order_by="name asc")
    shops = frappe.get_list("Shop", fields=["airport", "status"])

    rows = {a: {"airport": a, "total": 0, "available": 0, "occupied": 0} for a in airports}
    for shop in shops:
        row = rows.get(shop.airport)
        if not row:
            continue
        row["total"] += 1
        if shop.status == "Available":
            row["available"] += 1
        elif shop.status == "Occupied":
            row["occupied"] += 1

    return list(rows.values())
