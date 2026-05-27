# Copyright (c) 2026, shubham and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Sum, Coalesce

def execute(filters: dict | None = None):

    columns = get_columns()

    Airplane = frappe.qb.DocType("Airplane")
    Flight = frappe.qb.DocType("Airplane Flight")
    Ticket = frappe.qb.DocType("Airplane Ticket")

    data = (
        frappe.qb
        .from_(Airplane)
        .left_join(Flight).on(Flight.airplane == Airplane.name)
        .left_join(Ticket).on((Ticket.flight == Flight.name) & (Ticket.docstatus==1))
        .select(
            Airplane.airline,
            Coalesce(Sum(Ticket.total_amount), 0).as_("revenue")
        )
        .groupby(Airplane.airline)
    ).run(as_dict=True)
    chart = {
        "data": {
            "labels": [x.airline for x in data],
            "datasets": [
                {
                    "values": [x.revenue for x in data]
                }
            ]
        },
        "type": "donut"
    }
    report_summary = [{"label":"Total Revenue","value":sum([x.revenue for x in data]),'indicator':'Green'}]

    return columns, data, None, chart,report_summary


def get_columns() -> list[dict]:
    """Return columns for the report.

    One field definition per column, just like a DocType field definition.
    """
    return [
        {
            "label": "Airline",
            "fieldname": "airline",
            "fieldtype": "Data",
        },
        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "option":"IRN"
        }
    ]

def get_data() -> list[list]:
    """Return data for the report.

    The report data is a list of rows, with each row being a list of cell values.
    """
    return [
        ["Row 1", 1],
        ["Row 2", 2],
    ]
