import frappe


def get_context(context):
    context.title = "Flights"
    context.no_cache = 1

    context.flights = frappe.get_all(
        "Airplane Flight",
        filters={"is_published": 1},
        fields=[
            "name",
            "route",
            "airplane",
            "source_airport_code",
            "destination_airport_code",
            "date_of_departure",
            "time_of_departure",
            "duration",
        ],
        order_by="date_of_departure asc",
    )