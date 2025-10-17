# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import string
import secrets
from india_compliance.gst_india.utils.jinja import get_qr_code
import base64
import io
from frappe.utils.file_manager import save_file
from frappe.utils import getdate, add_months, nowdate
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

class AMCMaster(Document):
    def validate(self):
        if self.number_of_portable_fire_extinguisher or self.number_of_trolley_fireextinguisher:
            self.total_extinguisher = (
                int(self.number_of_portable_fire_extinguisher or 0) + 
                int(self.number_of_trolley_fireextinguisher or 0)
            )


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

    for i, row in enumerate(rows_to_update):
        new_code = unique_codes[i]
        row.qr_code = new_code
        
        qr_code_base64 = get_qr_code(new_code, scale=5)
        img_bytes = base64.b64decode(qr_code_base64)

        # Save file properly
        saved_file = save_file(
            fname=f"{new_code}.png",
            content=img_bytes,
            dt="AMC Master",
            dn=docname,
            folder=None,
            is_private=0
        )

        # Now properly set the qr_attach
        row.qr_attach = saved_file.file_url


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

