import frappe

no_cache = 1


def get_context(context):
	context.title = "Airport Shops"
	context.shops = frappe.get_all(
		"Shop",
		filters={"is_published": 1},
		fields=["name", "shop_number", "shop_name", "airport", "shop_type", "area_sq_ft", "status"],
		order_by="airport, shop_number",
	)
