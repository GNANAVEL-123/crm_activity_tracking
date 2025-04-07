# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import string
import secrets
from india_compliance.gst_india.utils.jinja import get_qr_code
import base64

class AMCMaster(Document):
	pass




@frappe.whitelist()
def qrcode_creation(docname):
    doc = frappe.get_doc("AMC Master", docname)

    if not doc.refilling_schedule:
        return

    # Fetch existing QR codes globally to avoid duplicates
    existing_codes = set(
        frappe.get_all(
            "Refilling Schedule Table",
            filters={"parenttype": "AMC Master"},
            pluck="qr_code"
        )
    )

    # Identify rows that need new codes
    rows_to_update = [row for row in doc.refilling_schedule if not row.qr_code]
    count = len(rows_to_update)

    if count == 0:
        return "All rows already have QR codes."

    unique_codes = generate_unique_codes(count, existing_codes)

    # Update only the rows that need QR codes
    for i, row in enumerate(rows_to_update):
        new_code = unique_codes[i]
        row.qr_code = new_code
        row.qr_image = f"<img width='120px' height='120px' src='data:image/png;base64,{get_qr_code(new_code, scale=2)}' class='qrcode'>"

    doc.save(ignore_permissions=True)
    return f"{count} QR code(s) generated and saved."


def generate_unique_codes(count, existing_codes):
    characters = string.ascii_uppercase + string.digits
    unique_codes = set()

    while len(unique_codes) < count:
        new_code = ''.join(secrets.choice(characters) for _ in range(6))
        if new_code not in existing_codes:
            unique_codes.add(new_code)
            existing_codes.add(new_code)

    return list(unique_codes)

