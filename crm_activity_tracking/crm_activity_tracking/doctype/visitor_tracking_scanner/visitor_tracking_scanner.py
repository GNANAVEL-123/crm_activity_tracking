# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class VisitorTrackingScanner(Document):
	pass

@frappe.whitelist()
def get_qr_schedule_data(qr_code, amc=None, customer=None):
    if not qr_code or not amc or not customer:
        return

    # Match QR code + parent AMC and Customer
    result = frappe.db.sql("""
        SELECT
            rs.name as rowname,
            rs.location,
            rs.type,
            rs.cap,
            rs.date_refilling,
            rs.refilling_frequency,
            rs.year_of_mfg,
            rs.year_frequency,
            rs.expiry_life_due,
            rs.full_weight,
            rs.empty_weight,
            rs.actual_weight,
            rs.remarks,
            rs.qr_code,
            rs.qr_attach,
            avt.name as amc_visitor_tracking,
            avt.amc_template,
            avt.customer_name
        FROM `tabAMC Visitor Tracking` avt
        JOIN `tabRefilling Schedule Table` rs ON rs.parent = avt.name
        WHERE rs.qr_code = %(qr_code)s
          AND avt.amc_template = %(amc)s
          AND avt.customer_name = %(customer)s
        LIMIT 1
    """, {
        "qr_code": qr_code,
        "amc": amc,
        "customer": customer
    }, as_dict=True)

    return result[0] if result else None

@frappe.whitelist()
def update_amc_row(parent, rowname, values):
    if isinstance(values, str):
        values = json.loads(values)

    for key, val in values.items():
        if frappe.db.has_column("Refilling Schedule Table", key):
            frappe.db.set_value("Refilling Schedule Table", rowname, key, val)

    return "success"



