# Copyright (c) 2026, Yashwanth and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator


def get_list_context(context):
    context.title = _("Flights")
    context.introduction = _("Browse available flights.")


class AirplaneFlight(WebsiteGenerator):

    def on_submit(self):
        self.db_set("status", "Completed")

    def on_update(self):
        self.queue_gate_number_update()

    def on_update_after_submit(self):
        self.queue_gate_number_update()

    def queue_gate_number_update(self):
        # only when the gate number actually changed
        if not self.has_value_changed("gate_number"):
            return

        frappe.enqueue(
            "airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight.update_ticket_gate_numbers",
            queue="short",
            enqueue_after_commit=True,
            flight=self.name,
            gate_number=self.gate_number,
        )


def update_ticket_gate_numbers(flight, gate_number):
    """Background job: copy the flight's new gate number to all its tickets."""
    tickets = frappe.get_all(
        "Airplane Ticket",
        filters={"flight": flight, "docstatus": ["<", 2]},
        pluck="name",
    )
    for ticket in tickets:
        frappe.db.set_value("Airplane Ticket", ticket, "gate_number", gate_number)
