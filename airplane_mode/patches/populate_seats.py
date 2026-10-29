import random
import frappe


def execute():
    tickets = frappe.get_all(
        "Airplane Ticket",
        fields=["name", "seat"]
    )

    for ticket in tickets:
        if not ticket.seat:
            seat = f"{random.randint(1, 99)}{random.choice('ABCDE')}"

            frappe.db.set_value(
                "Airplane Ticket",
                ticket.name,
                "seat",
                seat,
                update_modified=False
            )