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
            "label": _("SI NO"),
            "fieldtype": "Data",
            "fieldname": "sino",
            "width": 150
        },
		{
            "label": _("COMPANY NAME"),
            "fieldtype": "Data",
            "fieldname": "company_name",
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
            "label": _("LOCAL DC"),
            "fieldtype": "Data",
            "fieldname": "local_dc",
            "width": 200
        },
		{
            "label": _("GATE PASS NO"),
            "fieldtype": "Data",
            "fieldname": "gate_pass_no",
            "width": 200
        },
		{
            "label": _("EMP NAME"),
            "fieldtype": "Data",
            "fieldname": "emp_name",
            "width": 200
        },
		  {
            "label": _("TYPE OF CAPACITY"),
            "fieldtype": "Small Text",
            "fieldname": "type_of_capacity",
            "width": 200
        },
        {
            "label": _("NOS"),
            "fieldtype": "Data",
            "fieldname": "capacity",
            "width": 100
        },
		{
            "label": _("IN"),
            "fieldtype": "Date",
            "fieldname": "in",
            "width": 100
        },
		{
            "label": _("MOBILE NO"),
            "fieldtype": "Data",
            "fieldname": "mobile_no",
            "width": 180
        },
		{
            "label": _("OUT"),
            "fieldtype": "Date",
            "fieldname": "out",
            "width": 100
        },
		 {
            "label": _("RR BOOK NO"),
            "fieldtype": "Data",
            "fieldname": "rr_book_no",
            "width": 100
        },
        {
            "label": _("INVOICE NO"),
            "fieldtype": "Data",
            "fieldname": "invoice_no",
            "width": 150
        },
		{
            "label": _("DATE"),
            "fieldtype": "Date",
            "fieldname": "date",
            "width": 150
        },
       	{
            "label": _("REMARKS"),
            "fieldtype": "Data",
            "fieldname": "remarks",
            "width": 150
        },
    ]
    return columns

def get_data(filters):
	data = []
	rrno_filter = {}
	if filters.get('from_date') and filters.get('to_date'):
		rrno_filter["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
	if filters.get('region'):
		rrno_filter["region"] = filters.get("region")
	rrno_list = frappe.db.get_all(
		"Refilling Report No",
		filters=rrno_filter,
		fields=["name", "date"],
		order_by="date"
	)
	for rrno in rrno_list:
		rrno_details = {}
		if rrno.name:
			rrno_doc = frappe.get_doc("Refilling Report No", rrno.name)
			if rrno_doc:
				item_names = []
				item_qtys = []
				if rrno_doc.refilling_report_table:
					for item in rrno_doc.refilling_report_table:
						if item.item_name:
							item_names.append(item.item_name)  # Append item name to the list
							item_qtys.append(str(item.qty))  # Append quantity to the list as string

				# Join the item names and quantities with commas
				item_name_str = ", ".join(item_names)
				item_qty_str = ", ".join(item_qtys)
			

				rrno_details.update({
					"sino": rrno_doc.get("name", ""),
					"company_name": rrno_doc.get("customer", ""),
					"region":rrno_doc.get("region"),
					"local_dc":rrno_doc.get("local_dc"),
					"gate_pass_no":rrno_doc.get("gate_pass_no"),
					"emp_name":rrno_doc.get("employee"),
					"type_of_capacity": item_name_str,
					"capacity": item_qty_str,  
					"in":rrno_doc.get("in_date"),
					"mobile_no" : rrno_doc.get("mobile_no"),
					"out":rrno_doc.get("out_date"),
					"rr_book_no":rrno_doc.get("rr_book_no"),
					"invoice_no": rrno_doc.get("invoice_no", ""),
					"date": rrno_doc.get("date", ""),
					"remarks": rrno_doc.get("remarks", ""),
				})

				data.append(rrno_details)

	return data