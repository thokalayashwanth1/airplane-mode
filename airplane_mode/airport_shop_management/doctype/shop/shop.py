import frappe
from frappe.model.document import Document


class Shop(Document):
	"""A shop at an airport.

	Status, tenant and current contract are set by the Shop Contract, not typed by
	hand. Past tenants live on old contracts, so nothing is lost when a lease ends.
	"""

	def validate(self):
		self.set_default_rent()

	def set_default_rent(self):
		if not self.rent_amount:
			self.rent_amount = (
				frappe.db.get_single_value("Shop Settings", "default_rent_amount") or 0
			)
