# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        {
            "label": _("Quotation"),
            "fieldtype": "Link",
            "fieldname": "quotation",
            "options": "Quotation",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldtype": "Date",
            "fieldname": "date",
            "width": 150
        },
        {
            "label": _("Company Name"),
            "fieldtype": "Link",
            "fieldname": "company_name",
            "options": "Customer",
            "width": 180
        },
        {
            "label": _("Region"),
            "fieldtype": "Link",
            "fieldname": "region",
            "options": "Territory",
            "width": 100
        },
        {
            "label": _("Allocated To"),
            "fieldtype": "Link",
            "fieldname": "allocated_to",
            "options": "User",
            "width": 200
        },
        {
            "label": _("Status"),
            "fieldtype": "Data",
            "fieldname": "status",
            "width": 150
        },
    ]

def get_data(filters):
    data = []
    quo_filter = {}

    if filters.get('from_date') and filters.get('to_date'):
        quo_filter["transaction_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
    if filters.get('region'):
        quo_filter["custom_region"] = filters.get("region")
    if filters.get('allocated_to'):
        quo_filter["custom_assigned_to"] = filters.get("allocated_to")
    if filters.get('status'):
        quo_filter["status"] = filters.get("status")
    if filters.get('customer'):
        quo_filter["party_name"] = filters.get("customer")

    quo_list = frappe.db.get_all(
        "Quotation",
        filters=quo_filter,
        fields=[
            "name", "transaction_date", "custom_region",
            "custom_assigned_to", "party_name", "status"
        ],
        order_by="transaction_date"
    )

    for quo in quo_list:
        data.append({
            "quotation": quo.name,
            "date": quo.transaction_date,
            "company_name": quo.party_name,
            "region": quo.custom_region,
            "allocated_to": quo.custom_assigned_to,
            "status": quo.status,
        })

    return data