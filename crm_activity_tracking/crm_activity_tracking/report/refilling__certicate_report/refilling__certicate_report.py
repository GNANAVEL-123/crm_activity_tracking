# Copyright (c) 2024, CRM and contributors
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
            "label": _("RR BOOKNO"),
            "fieldtype": "Data",
            "fieldname": "rrno",
            "width": 150
        },
        {
            "label": _("INVOICE NO"),
            "fieldtype": "Data",
            "fieldname": "invoice_no",
            "width": 150
        },
        {
            "label": _("COMPANY NAME"),
            "fieldtype": "Data",
            "fieldname": "company_name",
            "width": 180
        },
       
        {
            "label": _("LOCATION"),
            "fieldtype": "Link",
            "fieldname": "location",
			"options": "Territory",
            "width": 100
        },
        {
            "label": _("TYPE OF CAPACITY"),
            "fieldtype": "Small Text",
            "fieldname": "type_of_capacity",
            "width": 200
        },
        {
            "label": _("CAPACITY"),
            "fieldtype": "Data",
            "fieldname": "capacity",
            "width": 100
        },
        {
            "label": _("REFILLING DATE"),
            "fieldtype": "Date",
            "fieldname": "refilling_date",
            "width": 150
        },
        {
            "label": _("DUE DATE"),
            "fieldtype": "DATE",
            "fieldname": "due_date",
            "width": 150
        },
    ]
    return columns

def get_data(filters):
	data = []
	rc_filter = {}
	if filters.get('from_date') and filters.get('to_date'):
		rc_filter["refilling_report_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
	if filters.get('region'):
		rc_filter["region"] = filters.get("region")
	rc_list = frappe.db.get_all(
		"Refilling Certificate",
		filters=rc_filter,
		fields=["name", "refilling_report_date"],
		order_by="refilling_report_date"
	)
	for rc in rc_list:
		rc_details = {}
		if rc.name:
			rc_doc = frappe.get_doc("Refilling Certificate", rc.name)
			if rc_doc:
				item_names = []
				item_qtys = []
				
				if rc_doc.table_wxkh:
					for item in rc_doc.table_wxkh:
						if item.item:
							item_names.append(item.item)  # Append item name to the list
							item_qtys.append(str(item.quantity))  # Append quantity to the list as string

				# Join the item names and quantities with commas
				item_name_str = ", ".join(item_names)
				item_qty_str = ", ".join(item_qtys)

				rc_details.update({
					"rrno": rc_doc.get("refilling_report_no", ""),
					"invoice_no": rc_doc.get("invoice_number", ""),
					"company_name": rc_doc.get("customer", ""),
					"location": rc_doc.get("region", ""),
					"type_of_capacity": item_name_str,  # Joined string of item names
					"capacity": item_qty_str,  # Joined string of quantities
					"refilling_date": rc_doc.get("refilling_report_date", ""),
					"due_date": rc_doc.get("refilling_report_date", ""),
				})

				data.append(rc_details)

	return data