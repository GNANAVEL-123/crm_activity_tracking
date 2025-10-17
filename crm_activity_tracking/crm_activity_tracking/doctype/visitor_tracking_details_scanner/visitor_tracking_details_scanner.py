# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VisitorTrackingDetailsScanner(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_qr_schedule_data(qr_code):
    if not qr_code:
        return

    # Fetch all matching rows for the given QR code
    row_data = frappe.db.sql("""
        SELECT
            avt.name AS amc_visitor_trcking,
            avt.customer_name,
            avt.amc_service_date
        FROM `tabAMC Visitor Tracking` avt
        JOIN `tabRefilling Schedule Table` rs ON rs.parent = avt.name
        WHERE rs.qr_code = %s
    """, (qr_code,), as_dict=True)

    return row_data  # Return list of dicts

