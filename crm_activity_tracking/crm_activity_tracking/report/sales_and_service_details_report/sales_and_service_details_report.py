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
         {
            "label": _("Date"),
            "fieldtype": "Date",
            "fieldname": "date",
            "width": 150
        },
		{
            "label": _("COMPANY NAME"),
            "fieldtype": "Link",
            "fieldname": "company_name",
			"options":"Customer",
            "width": 180
        },
		{
            "label": _("REGION"),
            "fieldtype": "Link",
            "fieldname": "region",
			"options": "Territory",
            "width": 100
        },
		{
            "label": _("CUSTOMER CONTACT NO"),
            "fieldtype": "Data",
            "fieldname": "customer_contact_no",
            "width": 200
        },
        {
            "label": _("CONTACT NAME"),
            "fieldtype": "Data",
            "fieldname": "contact_name",
            "width": 200
        },
		{
            "label": _("IN TIME"),
            "fieldtype": "Datetime",
            "fieldname": "in_time",
            "width": 200
        },
		{
            "label": _("OUT TIME"),
            "fieldtype": "Datetime",
            "fieldname": "out_time",
            "width": 200
        },
		{
            "label": _("PURPOSE TYPE"),
            "fieldtype": "Data",
            "fieldname": "purpose_type",
            "width": 200
        },
		{
            "label": _("SALES TYPE"),
            "fieldtype": "Data",
            "fieldname": "sales_type",
            "width": 200
        },
		{
            "label": _("SERVICE TYPE"),
            "fieldtype": "Data",
            "fieldname": "service_type",
            "width": 200
        },
		{
            "label": _("Employee"),
            "fieldtype": "Link",
            "fieldname": "employee",
			"options":"User",
            "width": 200
        },
    ]
    return columns

def get_data(filters):
	data = []
	ssd_filter = {}
	if filters.get('from_date') and filters.get('to_date'):
		ssd_filter["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
	if filters.get('region'):
		ssd_filter["region"] = filters.get("region")
	if filters.get('user'):
		ssd_filter["employee"] = filters.get("user")
	ssd_list = frappe.db.get_all(
		"Sales and Service Details",
		filters=ssd_filter,
		fields=["name", "date"],
		order_by="date"
	)
	for ssd in ssd_list:
		ssd_details = {}
		if ssd.name:
			ssd_doc = frappe.get_doc("Sales and Service Details", ssd.name)
			if ssd_doc:
				ssd_details.update({
					"date": ssd_doc.get("date", ""),
					"company_name": ssd_doc.get("company_name", ""),
					"region":ssd_doc.get("region"),
					"customer_contact_no":ssd_doc.get("customer_contact_no"),
                    "contact_name":ssd_doc.get("customer_name"),
					"purpose_type":ssd_doc.get("purpose_type"),
					"sales_type":ssd_doc.get("sales_purpose"),
					"service_type": ssd_doc.get('service_purpose'),
					"employee": ssd_doc.get('employee'),  
					"in_time":ssd_doc.get("in_time"),
					"out_time":ssd_doc.get("out_time"),
					
				})

				data.append(ssd_details)

	return data
