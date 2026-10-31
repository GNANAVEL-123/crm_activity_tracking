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
from crm_activity_tracking.crm_activity_tracking.doctype.amc.amc import sync_qr_codes_to_linked_visitor_tracking

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
        # Even if AMC Master already has all codes, any linked AMC
        # document might still be missing them (e.g. AMC was created
        # before codes were generated). Sync those regardless.
        sync_qr_codes_to_linked_amc(doc)
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
    frappe.db.commit()

    # ✅ Push newly generated codes into any linked AMC document(s)
    # that are still missing them, without overwriting anything
    # already filled in on the AMC side.
    sync_qr_codes_to_linked_amc(doc)

    return f"{count} QR code(s) generated and saved."


@frappe.whitelist()
def update_qr_codes_downstream(docname):
    """
    Standalone action for already-created records: pushes this AMC
    Master's EXISTING qr_code/qr_attach values down to any linked AMC
    and AMC Visitor Tracking documents that are still missing them —
    without generating any new QR codes first.

    Useful for AMC/AMC Visitor Tracking records that were created
    before this AMC Master had QR codes, or before this sync logic
    existed at all.
    """
    doc = frappe.get_doc("AMC Master", docname)
    sync_qr_codes_to_linked_amc(doc)
    return {"status": "ok"}


def sync_qr_codes_to_linked_amc(amc_master_doc):
    """
    For every AMC document linked to this AMC Master (via the
    'amc_master' field), fill in qr_code / qr_attach on any
    refilling_schedule row that is still empty, matching rows by
    location + type + cap against the AMC Master's rows.

    This only fills EMPTY rows on the AMC side — it never overwrites
    a qr_code/qr_attach that the AMC document already has.

    IMPORTANT: this updates child table rows directly via
    frappe.db.set_value, instead of loading + saving the full parent
    AMC document, so it can't be blocked by any unrelated validation
    logic in AMC's own validate() method.
    """
    linked_amc_names = frappe.get_all(
        "AMC",
        filters={"amc_master": amc_master_doc.name},
        pluck="name"
    )

    if not linked_amc_names:
        return

    for amc_name in linked_amc_names:
        amc_rows = frappe.get_all(
            "Refilling Schedule Table",
            filters={"parent": amc_name, "parenttype": "AMC"},
            fields=["name", "location", "type", "cap", "qr_code", "qr_attach", "amc_master_row"]
        )

        for amc_row in amc_rows:
            if amc_row.qr_code and amc_row.qr_attach:
                # Already has a code — don't touch it
                continue

            for master_row in amc_master_doc.refilling_schedule:
                if is_same_extinguisher(amc_row, master_row) and master_row.qr_code:
                    frappe.db.set_value(
                        "Refilling Schedule Table",
                        amc_row.name,
                        {
                            "qr_code": master_row.qr_code,
                            "qr_attach": master_row.qr_attach
                        },
                        update_modified=False
                    )
                    break

        frappe.db.commit()

        # ✅ Cascade one level further: AMC -> AMC Visitor Tracking.
        # Re-fetch the AMC doc fresh so its refilling_schedule reflects
        # the child-row updates just made above.
        amc_doc = frappe.get_doc("AMC", amc_name)
        sync_qr_codes_to_linked_visitor_tracking(amc_doc)


def is_same_extinguisher(amc_row, master_row):
    """AMC row vs AMC Master row: by the amc_master_row link when set,
    else by location + type + cap."""
    if amc_row.get("amc_master_row"):
        return amc_row.amc_master_row == master_row.name
    return (
        amc_row.location == master_row.location
        and amc_row.type == master_row.type
        and amc_row.cap == master_row.cap
    )


def generate_unique_codes(count, existing_codes):
    characters = string.ascii_uppercase + string.digits
    unique_codes = set()

    while len(unique_codes) < count:
        new_code = ''.join(secrets.choice(characters) for _ in range(6))
        if new_code not in existing_codes:
            unique_codes.add(new_code)
            existing_codes.add(new_code)

    return list(unique_codes)

import frappe
from frappe.utils import getdate, nowdate
import base64
from frappe.utils.file_manager import save_file
from crm_activity_tracking.crm_activity_tracking.doctype.amc_master.amc_master import generate_unique_codes, get_qr_code



def amc_to_amc_master_creation():
    today = getdate(nowdate())
    amc_list = frappe.db.get_list("AMC", filters={"amc_master":["is", "not set"]}, pluck="name")

    for amc in amc_list:
        amc_doc = frappe.get_doc("AMC", amc)
        if not amc_doc.amc_frequency_list:
            continue
        # ✅ Check for future dates in amc_frequency_list
        has_future_row = any(
            freq.from_date and getdate(freq.from_date) > today
            for freq in amc_doc.amc_frequency_list
        )

        if not has_future_row:
            continue  # Skip this AMC if no future schedule exists

        # ✅ Create AMC Master
        amc_master_doc = frappe.new_doc("AMC Master")
        amc_master_doc.location = amc_doc.location
        amc_master_doc.customer_name = amc_doc.customer_name
        amc_master_doc.concern_person = amc_doc.concern_person
        amc_master_doc.invoice_number = amc_doc.invoice_number
        amc_master_doc.mail_id = amc_doc.mail_id
        amc_master_doc.contact_number = amc_doc.contact_number
        amc_master_doc.amc_service_date = amc_doc.amc_service_date
        amc_master_doc.service_by = amc_doc.service_by
        amc_master_doc.total_extinguisher = amc_doc.total_extinguisher
        amc_master_doc.number_of_portable_fire_extinguisher = amc_doc.number_of_portable_fire_extinguisher
        amc_master_doc.recommendations_quote_no = amc_doc.recommendations_quote_no
        amc_master_doc.vendor_number = amc_doc.vendor_number
        amc_master_doc.job_sheet_no = amc_doc.job_sheet_no
        amc_master_doc.product_delivery_date = amc_doc.product_delivery_date
        amc_master_doc.po_number = amc_doc.po_number
        amc_master_doc.completion_report_no = amc_doc.completion_report_no
        amc_master_doc.number_of_trolley_fireextinguisher = amc_doc.number_of_trolley_fireextinguisher
        amc_master_doc.company_address = amc_doc.company_address
        amc_master_doc.customer_address = amc_doc.customer_address
        amc_master_doc.refilling_schedule = []
        row_links = []

        # ✅ Map rows from AMC → refilling_schedule to AMC Master → refilling_schedule
        for ref_row in amc_doc.refilling_schedule:
            if not ref_row.location:
                continue

            refilling_child = amc_master_doc.append("refilling_schedule", {})
            row_links.append((ref_row.name, refilling_child))
            refilling_child.location = ref_row.location
            refilling_child.year_of_mfg = ref_row.year_of_mfg
            refilling_child.type = ref_row.type
            refilling_child.year_frequency = ref_row.year_frequency
            refilling_child.expiry_life_due = ref_row.expiry_life_due
            refilling_child.cap = ref_row.cap
            refilling_child.expiry_life_due = ref_row.expiry_life_due
            refilling_child.date_refilling = ref_row.date_refilling
            refilling_child.full_weight = ref_row.full_weight
            refilling_child.refilling_frequency = ref_row.refilling_frequency
            refilling_child.refilling_due_date = ref_row.refilling_due_date
            refilling_child.empty_weight = ref_row.empty_weight
            refilling_child.actual_weight = ref_row.actual_weight
            refilling_child.remarks = ref_row.remarks
            refilling_child.enter_datetime = ref_row.enter_datetime
           

        amc_master_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # ✅ Update AMC with AMC Master name
        amc_doc.db_set("amc_master", amc_master_doc.name)
        # ✅ Link each AMC row to the AMC Master row created from it
        for amc_row_name, master_child in row_links:
            frappe.db.set_value("Refilling Schedule Table", amc_row_name, "amc_master_row", master_child.name, update_modified=False)
        frappe.db.commit()

        # ✅ Create QR codes and sync them back to AMC
        qrcode_creation_and_sync(amc_master_doc.name, amc_doc.name)

def amc_to_amc_master_creation_withdate():
    today = getdate(nowdate())
    amc_list = frappe.db.get_list("AMC", filters={"amc_master":["is", "not set"]}, pluck="name")

    for amc in amc_list:
        amc_doc = frappe.get_doc("AMC", amc)
        # if not amc_doc.amc_frequency_list:
        #     continue
        # # ✅ Check for future dates in amc_frequency_list
        # has_future_row = any(
        #     freq.from_date and getdate(freq.from_date) > today
        #     for freq in amc_doc.amc_frequency_list
        # )

        # if not has_future_row:
        #     continue  # Skip this AMC if no future schedule exists

        # ✅ Create AMC Master
        amc_master_doc = frappe.new_doc("AMC Master")
        amc_master_doc.location = amc_doc.location
        amc_master_doc.customer_name = amc_doc.customer_name
        amc_master_doc.concern_person = amc_doc.concern_person
        amc_master_doc.invoice_number = amc_doc.invoice_number
        amc_master_doc.mail_id = amc_doc.mail_id
        amc_master_doc.contact_number = amc_doc.contact_number
        amc_master_doc.amc_service_date = amc_doc.amc_service_date
        amc_master_doc.service_by = amc_doc.service_by
        amc_master_doc.total_extinguisher = amc_doc.total_extinguisher
        amc_master_doc.number_of_portable_fire_extinguisher = amc_doc.number_of_portable_fire_extinguisher
        amc_master_doc.recommendations_quote_no = amc_doc.recommendations_quote_no
        amc_master_doc.vendor_number = amc_doc.vendor_number
        amc_master_doc.job_sheet_no = amc_doc.job_sheet_no
        amc_master_doc.product_delivery_date = amc_doc.product_delivery_date
        amc_master_doc.po_number = amc_doc.po_number
        amc_master_doc.completion_report_no = amc_doc.completion_report_no
        amc_master_doc.number_of_trolley_fireextinguisher = amc_doc.number_of_trolley_fireextinguisher
        amc_master_doc.company_address = amc_doc.company_address
        amc_master_doc.customer_address = amc_doc.customer_address
        amc_master_doc.refilling_schedule = []
        row_links = []

        # ✅ Map rows from AMC → refilling_schedule to AMC Master → refilling_schedule
        for ref_row in amc_doc.refilling_schedule:
            if not ref_row.location:
                continue

            refilling_child = amc_master_doc.append("refilling_schedule", {})
            row_links.append((ref_row.name, refilling_child))
            refilling_child.location = ref_row.location
            refilling_child.point_no = ref_row.point_no
            refilling_child.year_of_mfg = ref_row.year_of_mfg
            refilling_child.hpt = ref_row.hpt
            refilling_child.type = ref_row.type
            refilling_child.year_frequency = ref_row.year_frequency
            refilling_child.expiry_life_due = ref_row.expiry_life_due
            refilling_child.cap = ref_row.cap
            refilling_child.expiry_life_due = ref_row.expiry_life_due
            refilling_child.date_refilling = ref_row.date_refilling
            refilling_child.full_weight = ref_row.full_weight
            refilling_child.refilling_frequency = ref_row.refilling_frequency
            refilling_child.refilling_due_date = ref_row.refilling_due_date
            refilling_child.empty_weight = ref_row.empty_weight
            refilling_child.actual_weight = ref_row.actual_weight
            refilling_child.remarks = ref_row.remarks
            refilling_child.enter_datetime = ref_row.enter_datetime
           

        amc_master_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # ✅ Update AMC with AMC Master name
        amc_doc.db_set("amc_master", amc_master_doc.name)
        # ✅ Link each AMC row to the AMC Master row created from it
        for amc_row_name, master_child in row_links:
            frappe.db.set_value("Refilling Schedule Table", amc_row_name, "amc_master_row", master_child.name, update_modified=False)
        frappe.db.commit()

        # ✅ Create QR codes and sync them back to AMC
        qrcode_creation_and_sync(amc_master_doc.name, amc_doc.name)


def qrcode_creation_and_sync(amc_master_name, amc_name):
    doc = frappe.get_doc("AMC Master", amc_master_name)

    if not doc.refilling_schedule:
        return

    existing_codes = set(
        frappe.get_all(
            "Refilling Schedule Table",
            filters={"parenttype": "AMC Master"},
            pluck="qr_code"
        )
    )

    rows_to_update = [row for row in doc.refilling_schedule if not row.qr_code]
    if not rows_to_update:
        return

    unique_codes = generate_unique_codes(len(rows_to_update), existing_codes)

    for i, row in enumerate(rows_to_update):
        new_code = unique_codes[i]
        row.qr_code = new_code

        qr_code_base64 = get_qr_code(new_code, scale=5)
        img_bytes = base64.b64decode(qr_code_base64)

        saved_file = save_file(
            fname=f"{new_code}.png",
            content=img_bytes,
            dt="AMC Master",
            dn=amc_master_name,
            is_private=0
        )

        row.qr_attach = saved_file.file_url

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # ✅ Update corresponding rows in AMC refilling_schedule
    amc_doc = frappe.get_doc("AMC", amc_name)

    for master_row in doc.refilling_schedule:
        for amc_row in amc_doc.refilling_schedule:
            if is_same_extinguisher(amc_row, master_row):
                amc_row.qr_code = master_row.qr_code
                amc_row.qr_attach = master_row.qr_attach
    if not amc_doc.company:
        amc_doc.company = frappe.db.get_single_value("Global Defaults", "default_company")

    amc_doc.save(ignore_permissions=True)
    frappe.db.commit()

import frappe
from frappe.utils import getdate, nowdate

def amc_count():
    today = getdate(nowdate())

    # Fetch all AMC records
    amc_list = frappe.db.get_list("AMC", pluck="name")

    total_amc = len(amc_list)
    print(f"🔍 Total AMC records found: {total_amc}")

    future_amc_count = 0
    no_future_amc_count = 0

    for amc in amc_list:
        amc_doc = frappe.get_doc("AMC", amc)

        if not amc_doc.amc_frequency_list:
            no_future_amc_count += 1
            continue

        # ✅ Check if any row in amc_frequency_list has a future from_date
        has_future_row = any(
            freq.from_date and getdate(freq.from_date) > today
            for freq in amc_doc.amc_frequency_list
        )

        if has_future_row:
            future_amc_count += 1
        else:
            no_future_amc_count += 1

    print(f"""
✅ AMC Count Summary:
------------------------
Total AMC Records      : {total_amc}
With Future Dates      : {future_amc_count}
Without Future Dates   : {no_future_amc_count}
------------------------
""")

    return {
        "total_amc": total_amc,
        "with_future_date": future_amc_count,
        "without_future_date": no_future_amc_count,
    }
