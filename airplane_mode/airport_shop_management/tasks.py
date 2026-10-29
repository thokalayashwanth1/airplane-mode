import frappe
from frappe import _
from frappe.utils import fmt_money, get_first_day, nowdate


def send_rent_reminders():
	"""Scheduled monthly: remind tenants whose rent for the current month is still unpaid.

	The contract's payment schedule is the source of truth, so a month that was
	paid in advance (even months ago) is never reminded.
	"""
	if not frappe.db.get_single_value("Shop Settings", "enable_rent_reminders"):
		return

	month_start = get_first_day(nowdate())
	month_label = month_start.strftime("%B %Y")

	for contract in frappe.get_all("Shop Contract", filters={"status": "Active"}, fields=["name", "tenant"]):
		amount_due = frappe.db.get_value(
			"Contract Payment Schedule",
			{
				"parent": contract.name,
				"parenttype": "Shop Contract",
				"due_month": month_start,
				"paid": 0,
			},
			"amount",
		)
		if amount_due is None:
			# already paid, or this month is outside the contract
			continue

		tenant = frappe.db.get_value("Tenant", contract.tenant, ["tenant_name", "email"], as_dict=True)
		if not tenant or not tenant.email:
			continue

		shops = frappe.get_all(
			"Contract Shop",
			filters={"parent": contract.name},
			fields=["shop", "shop_name"],
			parent_doctype="Shop Contract",
		)
		shop_list = ", ".join(f"{s.shop_name} ({s.shop})" for s in shops)

		frappe.sendmail(
			recipients=[tenant.email],
			subject=_("Rent due for {0} - {1}").format(shop_list, month_label),
			message=_(
				"Dear {0},<br><br>This is a reminder that rent of {1} for {2} "
				"(contract {3}) is due for {4}.<br><br>Thank you."
			).format(
				tenant.tenant_name,
				fmt_money(amount_due, currency="INR"),
				shop_list,
				contract.name,
				month_label,
			),
			reference_doctype="Shop Contract",
			reference_name=contract.name,
		)


def expire_contracts():
	"""Daily: mark finished contracts as Expired and free their shops.

	The contract keeps its tenant, dates and payments, so history is preserved.
	"""
	for name in frappe.get_all(
		"Shop Contract",
		filters={"status": "Active", "contract_end_date": ["<", nowdate()]},
		pluck="name",
	):
		contract = frappe.get_doc("Shop Contract", name)
		contract.status = "Expired"
		contract.save(ignore_permissions=True)
