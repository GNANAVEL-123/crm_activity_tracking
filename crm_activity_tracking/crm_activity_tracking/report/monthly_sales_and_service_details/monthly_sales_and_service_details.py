# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": _("DATE"), "fieldtype": "Date", "fieldname": "date", "width": 180},
        {"label": _("NO OF NEW VISIT"), "fieldtype": "float", "fieldname": "new_visit", "width": 180},
        {"label": _("NO OF EXISTIN VISIT"), "fieldtype": "float", "fieldname": "existin_visit", "width": 180},
        {"label": _("NO OF QUOTATION"), "fieldtype": "float", "fieldname": "no_quotation", "width": 180},
        {"label": _("NO OF PO FOLLOW"), "fieldtype": "float", "fieldname": "po_follow", "width": 200},
        {"label": _("NO OF MEETING"), "fieldtype": "Float", "fieldname": "no_meeting", "width": 180},
        {"label": _("NO OF AMC SERVICE"), "fieldtype": "Float", "fieldname": "amc_service", "width": 200},
        {"label": _("NO OF DELIVERY"), "fieldtype": "Float", "fieldname": "no_delivery", "width": 180},
        {"label": _("INVOICE VALUE"), "fieldtype": "currency", "fieldname": "invoice_value", "width": 180},
        {"label": _("VALUE OF PAYMENTS"), "fieldtype": "currency", "fieldname": "value_of_payments", "width": 180},
        {"label": _("GENERAL VISIT"), "fieldtype": "Float", "fieldname": "general_visit", "width": 180},
    ]
    return columns

def get_data(filters):
    data = []
    rc_filter = {}
    
    # Applying filters for the query
    if filters.get("from_date") and filters.get("to_date"):
        rc_filter["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
    if filters.get("region"):
        rc_filter["region"] = filters.get("region")
    if filters.get("user"):
        rc_filter["employee"] = filters.get("user")
    
    # Fetching monthly sales data
    monthly_sales_list = frappe.db.get_all(
        "Sales and Service Details",
        filters=rc_filter,
        fields=["name", "date", "sales_purpose", "service_purpose", "invoice_value", "amount"],
        order_by="date"
    )
    
    # Initialize sales type and service type mapping
    sales_type_map = {
        "New Visit Follow": "new_visit",
        "Existin Visit Follow": "existin_visit",
        "Quotation Follow": "no_quotation",
        "PO Follow": "po_follow",
        "Meeting": "no_meeting",
        "Payments": "value_of_payments",
    }
    service_type_map = {
        "AMC Service": "amc_service",
        "Delivery": "no_delivery",
        "General Visit": "general_visit",
    }
    
    # Process data date-wise
    date_wise_data = {}
    for record in monthly_sales_list:
        record_date = record.get("date")
        if record_date not in date_wise_data:
            # Initialize data for the date
            date_wise_data[record_date] = {
                "date": record_date,
                "new_visit": 0,
                "existin_visit": 0,
                "no_quotation": 0,
                "po_follow": 0,
                "no_meeting": 0,
                "amc_service": 0,
                "no_delivery": 0,
                "general_visit": 0,
                "invoice_value": 0,
                "value_of_payments": 0,
            }
        
        # Process sales type
        sales_type = record.get("sales_purpose")
        if sales_type in sales_type_map:
            fieldname = sales_type_map[sales_type]
            if fieldname == "value_of_payments":
                date_wise_data[record_date][fieldname] += record.get("amount", 0)
            else:
                date_wise_data[record_date][fieldname] += 1
        
        # Process service type
        service_type = record.get("service_purpose")
        if service_type in service_type_map:
            fieldname = service_type_map[service_type]
            date_wise_data[record_date][fieldname] += 1
        
        # Update invoice value
        date_wise_data[record_date]["invoice_value"] += record.get("invoice_value", 0)
    
    # Convert the dictionary to a list for the report
    data = list(date_wise_data.values())
    return data