import frappe
from frappe import _

no_cache = 1


def get_context(context):
	name = frappe.form_dict.get("name")
	if not name or not frappe.db.exists("Shop", {"name": name, "is_published": 1}):
		frappe.throw(_("Shop not found"), frappe.DoesNotExistError)

	context.shop = frappe.get_doc("Shop", name)
	context.title = context.shop.shop_name
