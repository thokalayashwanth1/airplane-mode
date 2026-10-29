import frappe
from frappe import _
from frappe.query_builder.functions import IfNull, Sum


def execute(filters=None):
    columns = get_columns()
    data = get_data()
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "label": _("Airline"),
            "fieldname": "airline",
            "fieldtype": "Link",
            "options": "Airline",
            "width": 200,
        },
        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


def get_data():
    airline = frappe.qb.DocType("Airline")
    airplane = frappe.qb.DocType("Airplane")
    flight = frappe.qb.DocType("Airplane Flight")
    ticket = frappe.qb.DocType("Airplane Ticket")

    rows = (
        frappe.qb.from_(airline)
        .left_join(airplane).on(airplane.airline == airline.name)
        .left_join(flight).on(flight.airplane == airplane.name)
        .left_join(ticket).on((ticket.flight == flight.name) & (ticket.docstatus == 1))
        .select(airline.name.as_("airline"), Sum(IfNull(ticket.total_amount, 0)).as_("revenue"))
        .groupby(airline.name)
        .run(as_dict=True)
    )
    rows.sort(key=lambda r: r.revenue or 0, reverse=True)
    return rows


def get_chart(data):
    return {
        "data": {
            "labels": [d.airline for d in data],
            "datasets": [{"values": [d.revenue or 0 for d in data]}],
        },
        "type": "donut",
    }


def get_summary(data):
    total = sum(d.revenue or 0 for d in data)
    return [
        {
            "value": total,
            "label": _("Total Revenue"),
            "datatype": "Currency",
        }
    ]
