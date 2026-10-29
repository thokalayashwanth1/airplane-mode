# Copyright (c) 2026, Yashwanth and contributors
# For license information, please see license.txt

import random

import frappe
from frappe.model.document import Document


class AirplaneTicket(Document):

    def before_insert(self):
        self.validate_capacity()
        seat_number = random.randint(1, 99)
        seat_letter = random.choice("ABCDE")
        self.seat = f"{seat_number}{seat_letter}"

    def validate_capacity(self):
        flight_doctype = frappe.get_meta("Airplane Ticket").get_field("flight").options
        if flight_doctype == "Airplane":
            airplane = self.flight
        else:
            airplane = frappe.db.get_value(flight_doctype, self.flight, "airplane")

        capacity = frappe.db.get_value("Airplane", airplane, "capacity")
        if capacity is None:
            return

        booked = frappe.db.count(
            "Airplane Ticket", {"flight": self.flight, "docstatus": ["<", 2]}
        )
        if booked >= capacity:
            frappe.throw(
                f"No seats available: flight {self.flight} is full "
                f"({booked} of {capacity} seats booked)."
            )

    def validate(self):
        # Remove duplicates first so the total only counts unique add-ons
        self.remove_duplicate_add_ons()
        self.calculate_total_amount()

    def remove_duplicate_add_ons(self):
        seen_items = set()
        unique_rows = []

        for row in self.add_ons or []:
            # keep rows without an item so the mandatory check can flag them
            if row.item and row.item in seen_items:
                continue

            if row.item:
                seen_items.add(row.item)

            unique_rows.append(row)

        if len(unique_rows) != len(self.add_ons or []):
            self.set("add_ons", unique_rows)

        for idx, row in enumerate(self.add_ons or [], start=1):
            row.idx = idx

    def calculate_total_amount(self):
        flight_price = self.flight_price or 0

        add_on_total = sum(
            row.amount or 0 for row in (self.add_ons or [])
        )

        self.total_amount = flight_price + add_on_total

    def before_submit(self):
        if self.status != "Boarded":
            frappe.throw(
                "Airplane Ticket can only be submitted when Status is Boarded."
            )
