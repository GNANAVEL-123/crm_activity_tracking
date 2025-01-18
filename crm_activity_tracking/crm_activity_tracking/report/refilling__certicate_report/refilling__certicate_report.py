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
            "label": _("MOBILE NO"),
            "fieldtype": "Data",
            "fieldname": "mobile_no",
            "width": 180
        },
        {
            "label": _("COMPANY ADDRESS"),
            "fieldtype": "Small Text",
            "fieldname": "company_address",
            "width": 200
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
            "label": _("NOS"),
            "fieldtype": "Data",
            "fieldname": "capacity",
            "width": 100
        },
        {
            "label": _("PRICE"),
            "fieldtype": "Data",
            "fieldname": "price",
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
            "fieldtype": "Date",
            "fieldname": "due_date",
            "width": 150
        },
    ]
    return columns

def get_data(filters):
    data = []
    if filters.get("refilling_certificate") == 1:
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
                    item_price = []
                    mob_no = ""
                    add_list = []
                    if rc_doc.address:
                        add_doc = frappe.get_doc("Address", rc_doc.address)
                        if add_doc and add_doc.phone:
                            mob_no = add_doc.phone
                        if add_doc and add_doc.address_line1:
                            add_list.append(str(add_doc.address_line1))
                        if add_doc and add_doc.address_line2:
                            add_list.append(str(add_doc.address_line2))
                        if add_doc and add_doc.city:
                            add_list.append(str(add_doc.city))
                        if add_doc and add_doc.state:
                            add_list.append(str(add_doc.state))
                        if add_doc and add_doc.pincode:
                            add_list.append(str(add_doc.pincode))
                    if rc_doc.table_wxkh:
                        for item in rc_doc.table_wxkh:
                            if item.item:
                                item_names.append(item.item)  # Append item name to the list
                                item_qtys.append(str(item.quantity))  # Append quantity to the list as string
                                item_price.append(str(item.rate))

                    # Join the item names and quantities with commas
                    item_name_str = ", ".join(item_names)
                    item_qty_str = ", ".join(item_qtys)
                    item_price_str = ", ".join(item_price)
                    address_str = ", ".join(add_list)

                    rc_details.update({
                        "rrno": rc_doc.get("refilling_report_no", ""),
                        "invoice_no": rc_doc.get("invoice_number", ""),
                        "company_name": rc_doc.get("customer", ""),
                        "mobile_no" : mob_no,
                        "location": rc_doc.get("region", ""),
                        "type_of_capacity": item_name_str,  # Joined string of item names
                        "capacity": item_qty_str,  # Joined string of quantities
                        "price": item_price_str,
                        "company_address":address_str,
                        "refilling_date": rc_doc.get("refilling_report_date", ""),
                        "due_date": rc_doc.get("refilling_due_date", ""),
                    })

                    data.append(rc_details)
    if filters.get("warranty_certificate") == 1:
        wc_filter = {}
        if filters.get('from_date') and filters.get('to_date'):
            wc_filter["refilling__report_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
        if filters.get('region'):
            wc_filter["region"] = filters.get("region")
        wc_list = frappe.db.get_all(
            "Warranty Certificate",
            filters=wc_filter,
            fields=["name", "refilling__report_date"],
            order_by="refilling__report_date"
        )
        for wc in wc_list:
            wc_details = {}
            if wc.name:
                wc_doc = frappe.get_doc("Warranty Certificate", wc.name)
                if wc_doc:
                    item_names = []
                    item_qtys = []
                    item_price = []
                    mob_no = ""
                    add_list = []
                    if wc_doc.customer_address:
                        add_doc = frappe.get_doc("Address", wc_doc.customer_address)
                        if add_doc and add_doc.phone:
                            mob_no = add_doc.phone
                        if add_doc and add_doc.address_line1:
                            add_list.append(str(add_doc.address_line1))
                        if add_doc and add_doc.address_line2:
                            add_list.append(str(add_doc.address_line2))
                        if add_doc and add_doc.city:
                            add_list.append(str(add_doc.city))
                        if add_doc and add_doc.state:
                            add_list.append(str(add_doc.state))
                        if add_doc and add_doc.pincode:
                            add_list.append(str(add_doc.pincode))
                    if wc_doc.table_nrxp:
                        for item in wc_doc.table_nrxp:
                            if item.item:
                                item_names.append(item.item)  # Append item name to the list
                                item_qtys.append(str(item.quantity))  # Append quantity to the list as string
                                item_price.append(str(item.rate))

                    # Join the item names and quantities with commas
                    item_name_str = ", ".join(item_names)
                    item_qty_str = ", ".join(item_qtys)
                    item_price_str = ", ".join(item_price)
                    address_str = ", ".join(add_list)

                    wc_details.update({
                        "rrno": wc_doc.get("refilling__report_no", ""),
                        "invoice_no": wc_doc.get("invoice_number", ""),
                        "company_name": wc_doc.get("customer_name", ""),
                        "mobile_no" : mob_no,
                        "location": wc_doc.get("region", ""),
                        "type_of_capacity": item_name_str,  # Joined string of item names
                        "capacity": item_qty_str,  # Joined string of quantities
                        "price": item_price_str,
                        "company_address":address_str,
                        "refilling_date": wc_doc.get("refilling__report_date", ""),
                        "due_date": wc_doc.get("refilling_due_date", ""),
                    })

                    data.append(wc_details)
    if filters.get("refilling_report_no") == 1:
        rrn_filter = {}
        if filters.get('from_date') and filters.get('to_date'):
            rrn_filter["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
        if filters.get('region'):
            rrn_filter["region"] = filters.get("region")
        rrn_list = frappe.db.get_all(
            "Refilling Report No",
            filters=rrn_filter,
            fields=["name", "date"],
            order_by="date"
        )
        for rrn in rrn_list:
            rrn_details = {}
            if rrn.name:
                rrn_doc = frappe.get_doc("Refilling Report No", rrn.name)
                if rrn_doc:
                    item_names = []
                    item_qtys = []
                    if rrn_doc.refilling_report_table:
                        for item in rrn_doc.refilling_report_table:
                            if  item.item_name:
                                item_names.append(item.item_name) 
                                item_qtys.append(str(item.qty))
                    item_name_str = ", ".join(item_names)
                    item_qty_str = ", ".join(item_qtys)
                    rrn_details.update({
                        "rrno": rrn_doc.get("name", ""),
                        "invoice_no": rrn_doc.get("invoice_no", ""),
                        "company_name": rrn_doc.get("customer", ""),
                        "mobile_no" : rrn_doc.get("customer", ""),
                        "location": rrn_doc.get("region", ""),
                        "type_of_capacity": item_name_str,
                        "capacity": item_qty_str,
                        "refilling_date": rrn_doc.get("refilling_date", ""),
                    })

                    data.append(rrn_details)

    return data