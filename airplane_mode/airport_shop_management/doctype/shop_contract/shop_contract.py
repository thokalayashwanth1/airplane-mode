import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, cint, flt, get_first_day, getdate


class ShopContract(Document):
	"""One lease: a tenant renting one or more shops for a period.

	Contracts are never deleted when they end. They become Expired (or Terminated),
	so the full history of every shop stays available for reports.
	"""

	def validate(self):
		self.validate_shops()
		self.set_end_date()
		self.set_shop_rents()
		self.validate_no_overlap()
		self.build_schedule()

	def on_update(self):
		self.sync_shops()

	def on_trash(self):
		for row in self.shops:
			release_shop(row.shop, self.name)

	# ---- validation -------------------------------------------------------

	def validate_shops(self):
		if not self.shops:
			frappe.throw(_("Add at least one shop to the contract."))

		if cint(self.contract_duration) < 1:
			frappe.throw(_("Contract Duration must be at least 1 month."))

		seen = set()
		for row in self.shops:
			if row.shop in seen:
				frappe.throw(_("Shop {0} is added more than once.").format(row.shop))
			seen.add(row.shop)

	def set_end_date(self):
		start = getdate(self.contract_start_date)
		self.contract_end_date = add_days(add_months(start, cint(self.contract_duration)), -1)

	def set_shop_rents(self):
		default_rent = frappe.db.get_single_value("Shop Settings", "default_rent_amount") or 0
		for row in self.shops:
			if not flt(row.rent_amount):
				row.rent_amount = frappe.db.get_value("Shop", row.shop, "rent_amount") or default_rent
		self.monthly_rent = sum(flt(row.rent_amount) for row in self.shops)

	def validate_no_overlap(self):
		"""A shop cannot be in two active contracts for the same dates."""
		if self.status != "Active":
			return

		start = getdate(self.contract_start_date)
		end = getdate(self.contract_end_date)

		for row in self.shops:
			parents = frappe.get_all(
				"Contract Shop",
				filters={"shop": row.shop, "parent": ["!=", self.name or ""]},
				pluck="parent",
				parent_doctype="Shop Contract",
			)
			for parent in set(parents):
				other = frappe.db.get_value(
					"Shop Contract",
					parent,
					["status", "contract_start_date", "contract_end_date"],
					as_dict=True,
				)
				if (
					other
					and other.status == "Active"
					and getdate(other.contract_start_date) <= end
					and getdate(other.contract_end_date) >= start
				):
					frappe.throw(
						_("Shop {0} is already in active contract {1} for these dates.").format(
							row.shop, parent
						)
					)

	# ---- payment schedule -------------------------------------------------

	def build_schedule(self):
		"""One row per month of the contract. Rebuilt only when dates change."""
		before = self.get_doc_before_save()
		dates_changed = (
			not before
			or getdate(before.contract_start_date) != getdate(self.contract_start_date)
			or cint(before.contract_duration) != cint(self.contract_duration)
		)

		if not dates_changed and self.payment_schedule:
			# keep unpaid months in line with the current rent
			for row in self.payment_schedule:
				if not row.paid:
					row.amount = self.monthly_rent
			return

		if any(row.paid for row in self.payment_schedule):
			frappe.throw(_("Start date or duration cannot be changed after rent has been paid."))

		self.set("payment_schedule", [])
		first_month = get_first_day(self.contract_start_date)
		for i in range(cint(self.contract_duration)):
			self.append(
				"payment_schedule",
				{"due_month": add_months(first_month, i), "amount": self.monthly_rent, "paid": 0},
			)

	# ---- shop status ------------------------------------------------------

	def sync_shops(self):
		"""Keep each shop's status, tenant and current contract in line with this contract."""
		before = self.get_doc_before_save()
		current = [row.shop for row in self.shops]
		removed = [row.shop for row in before.shops if row.shop not in current] if before else []

		for shop in current:
			if self.status == "Active":
				frappe.db.set_value(
					"Shop",
					shop,
					{"status": "Occupied", "tenant": self.tenant, "current_contract": self.name},
				)
			else:
				release_shop(shop, self.name)

		for shop in removed:
			release_shop(shop, self.name)


def release_shop(shop, contract):
	"""Make a shop Available again, unless another active contract still holds it."""
	parents = frappe.get_all(
		"Contract Shop",
		filters={"shop": shop, "parent": ["!=", contract]},
		pluck="parent",
		parent_doctype="Shop Contract",
	)
	for parent in set(parents):
		other = frappe.db.get_value("Shop Contract", parent, ["status", "tenant"], as_dict=True)
		if other and other.status == "Active":
			frappe.db.set_value(
				"Shop",
				shop,
				{"status": "Occupied", "tenant": other.tenant, "current_contract": parent},
			)
			return

	frappe.db.set_value(
		"Shop", shop, {"status": "Available", "tenant": None, "current_contract": None}
	)
