# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    consolidated = filters.get("consolidated_view")

    columns = get_columns(consolidated)
    data = get_data(filters, consolidated)

    return columns, data


def get_columns(consolidated):
    if consolidated:
        # Summary view: one row per user
        return [
            {
                "label": _("User"),
                "fieldname": "owner",
                "fieldtype": "Data",
                "width": 200
            },
            {
                "label": _("User Full Name"),
                "fieldname": "full_name",
                "fieldtype": "Data",
                "width": 180
            },
            {
                "label": _("No. of Invoices"),
                "fieldname": "invoice_count",
                "fieldtype": "Int",
                "width": 130
            },
            {
                "label": _("Total Amount"),
                "fieldname": "total_amount",
                "fieldtype": "Currency",
                "width": 150
            },
            {
                "label": _("Total Rounded Amount"),
                "fieldname": "total_rounded_amount",
                "fieldtype": "Currency",
                "width": 170
            }
        ]

    # Detailed view: one row per invoice
    return [
        {
            "label": _("User"),
            "fieldname": "owner",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("User Full Name"),
            "fieldname": "full_name",
            "fieldtype": "Data",
            "width": 160
        },
        {
            "label": _("Invoice No"),
            "fieldname": "invoice_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 140
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 180
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": _("Rounded Total"),
            "fieldname": "rounded_total",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        }
    ]


def build_conditions(filters):
    conditions = []
    values = {}

    # Always exclude Cancelled invoices (docstatus 2)
    docstatus_filter = filters.get("docstatus_filter")

    if docstatus_filter == "Draft":
        conditions.append("si.docstatus = 0")
    elif docstatus_filter == "Submitted":
        conditions.append("si.docstatus = 1")
    else:
        # Both Draft and Submitted, still excluding Cancelled
        conditions.append("si.docstatus IN (0, 1)")

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    if filters.get("owner"):
        conditions.append("si.owner = %(owner)s")
        values["owner"] = filters.get("owner")

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.get("customer")

    if filters.get("company"):
        conditions.append("si.company = %(company)s")
        values["company"] = filters.get("company")

    return conditions, values


def get_data(filters, consolidated):
    conditions, values = build_conditions(filters)

    where_condition = ""
    if conditions:
        where_condition = "WHERE " + " AND ".join(conditions)

    if consolidated:
        query = f"""
            SELECT
                si.owner,
                u.full_name,
                COUNT(si.name) AS invoice_count,
                SUM(si.grand_total) AS total_amount,
                SUM(si.rounded_total) AS total_rounded_amount

            FROM `tabSales Invoice` si

            LEFT JOIN `tabUser` u
                ON u.name = si.owner

            {where_condition}

            GROUP BY si.owner

            ORDER BY total_amount DESC
        """
    else:
        query = f"""
            SELECT
                si.owner,
                u.full_name,
                si.name AS invoice_no,
                si.customer,
                si.posting_date,
                si.grand_total,
                si.rounded_total,
                CASE
                    WHEN si.docstatus = 0 THEN 'Draft'
                    WHEN si.docstatus = 1 THEN 'Submitted'
                    ELSE 'Cancelled'
                END AS status

            FROM `tabSales Invoice` si

            LEFT JOIN `tabUser` u
                ON u.name = si.owner

            {where_condition}

            ORDER BY si.owner, si.posting_date
        """

    data = frappe.db.sql(query, values, as_dict=True)

    return data