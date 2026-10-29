# Copyright (c) 2026, Yashwanth and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FlightPassenger(Document):
    def before_save(self):
        first_name = (self.first_name or "").strip()
        last_name = (self.last_name or "").strip()

        self.full_name = " ".join(
            part for part in (first_name, last_name) if part
        )