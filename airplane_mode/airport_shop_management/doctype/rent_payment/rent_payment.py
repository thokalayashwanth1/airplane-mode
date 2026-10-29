import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, formatdate, get_first_day, getdate


class RentPayment(Document):
	"""Rent collected against a contract, for one or more consecutive months.

	Submitting the payment ticks the matching months in the contract's payment
	schedule as paid. Cancelling it unticks them.
	"""

	def validate(self):
		# store the month as its first day, so there is one value per month
		self.rent_for_month = get_first_day(self.rent_for_month)
		self.months_paid = cint(self.months_paid) or 1
		self.set_tenant()
		self.validate_contract()
		self.set_amount()

	def on_submit(self):
		for row in self.get_schedule_rows():
			frappe.db.set_value(
				"Contract Payment Schedule", row.name, {"paid": 1, "rent_payment": self.name}
			)

	def on_cancel(self):
		for name in frappe.get_all(
			"Contract Payment Schedule",
			filters={"rent_payment": self.name, "parent": self.contract},
			pluck="name",
			parent_doctype="Shop Contract",
		):
			frappe.db.set_value(
				"Contract Payment Schedule", name, {"paid": 0, "rent_payment": None}
			)

	# ---- helpers ----------------------------------------------------------

	def set_tenant(self):
		self.tenant = frappe.db.get_value("Shop Contract", self.contract, "tenant")

	def validate_contract(self):
		status = frappe.db.get_value("Shop Contract", self.contract, "status")
		if status == "Terminated":
			frappe.throw(_("Rent cannot be collected for a terminated contract."))

	def get_schedule_rows(self):
		"""The consecutive schedule months this payment covers, starting at rent_for_month."""
		contract = frappe.get_doc("Shop Contract", self.contract)
		start = getdate(self.rent_for_month)
		rows = [row for row in contract.payment_schedule if getdate(row.due_month) >= start]
		return rows[: cint(self.months_paid)]

	def set_amount(self):
		rows = self.get_schedule_rows()
		month = formatdate(self.rent_for_month, "MMMM yyyy")

		if not rows or getdate(rows[0].due_month) != getdate(self.rent_for_month):
			frappe.throw(_("There is no rent due in this contract for {0}.").format(month))

		if len(rows) < self.months_paid:
			frappe.throw(
				_("The contract has only {0} month(s) from {1} onwards.").format(len(rows), month)
			)

		for row in rows:
			if row.paid and row.rent_payment != self.name:
				frappe.throw(
					_("Rent for {0} is already paid ({1}).").format(
						formatdate(row.due_month, "MMMM yyyy"), row.rent_payment
					)
				)

		self.amount = sum(flt(row.amount) for row in rows)
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero."))
