# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, nowdate
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar
from frappe.desk.reportview import get_filters_cond, get_match_cond


class AMC(Document):

    def validate(self):
        if self.amc_service_date and self.amc_frequency and not self.amc_frequency_list and self.no_of_month:
            self.amc_frequency_list = []
            start_date = getdate(self.amc_service_date)
            for i in range(self.no_of_month):
                end_date = add_months(start_date, self.amc_frequency) - timedelta(days=1)
                self.append("amc_frequency_list", {
                    "from_date": start_date.strftime('%Y-%m-%d'),
                    "to_date": end_date.strftime('%Y-%m-%d') 
                })
                start_date = add_months(start_date, self.amc_frequency)
                if i + 1 >= self.no_of_month:
                    break
        if self.number_of_portable_fire_extinguisher or self.number_of_trolley_fireextinguisher:
            self.total_extinguisher = (
                int(self.number_of_portable_fire_extinguisher or 0) + 
                int(self.number_of_trolley_fireextinguisher or 0)
            )

def amc_visitor_tracker():
    amc_list = frappe.db.get_all("AMC", fields=["name"])
    if amc_list:
        for amc in amc_list:
            if amc.name:
                amc_doc = frappe.get_doc("AMC", amc.name)
                if amc_doc and amc_doc.amc_frequency_list:
                    for amc_fre in amc_doc.amc_frequency_list:
                        avt = frappe.db.get_list(
                            "AMC Visitor Tracking",
                            filters={"amc_service_date": amc_fre.from_date, "amc_template": amc_doc.name},
                            fields=["name"]
                        )
                        if getdate(amc_fre.from_date) == getdate(nowdate()) and not avt:
                            next_date = ""
                            if amc_fre.from_date and amc_doc.amc_frequency:
                                from_date = getdate(amc_fre.from_date)
                                frequency_months = amc_doc.amc_frequency
                                next_date = from_date + relativedelta(months=frequency_months)
                            amc_tracker_doc = frappe.new_doc("AMC Visitor Tracking")
                            amc_tracker_doc.amc_template = amc_doc.name
                            amc_tracker_doc.customer_name = amc_doc.customer_name
                            amc_tracker_doc.contact_number = amc_doc.contact_number
                            amc_tracker_doc.mail_id = amc_doc.mail_id
                            amc_tracker_doc.location = amc_doc.location
                            amc_tracker_doc.concern_person = amc_doc.concern_person
                            amc_tracker_doc.service_by = amc_doc.service_by
                            amc_tracker_doc.amc_service_date = amc_fre.from_date
                            amc_tracker_doc.next_amc_service_due_date = next_date
                            amc_tracker_doc.amc_frequency = amc_doc.amc_frequency
                            amc_tracker_doc.invoice_number = amc_doc.invoice_number
                            amc_tracker_doc.total_extinguisher = amc_doc.total_extinguisher
                            amc_tracker_doc.number_of_portable_fire_extinguisher = amc_doc.number_of_portable_fire_extinguisher
                            amc_tracker_doc.number_of_trolley_fireextinguisher = amc_doc.number_of_trolley_fireextinguisher
                            amc_tracker_doc.recommendations_quote_no = amc_doc.recommendations_quote_no
                            amc_tracker_doc.vendor_number = amc_doc.vendor_number
                            amc_tracker_doc.po_number = amc_doc.po_number
                            amc_tracker_doc.company = amc_doc.company
                            amc_tracker_doc.company_address = amc_doc.company_address
                            amc_tracker_doc.customer_address = amc_doc.customer_address
                            amc_tracker_doc.fire_extinguisher_amc_scope_of_work = amc_doc.fire_extinguisher_amc_scope_of_work
                            if amc_doc.refilling_schedule:
                                for refilling_entry in amc_doc.refilling_schedule:
                                    refilling_child = amc_tracker_doc.append("refilling_schedule", {})
                                    refilling_child.location = refilling_entry.location
                                    refilling_child.point_no = refilling_entry.point_no
                                    refilling_child.type = refilling_entry.type
                                    refilling_child.cap = refilling_entry.cap
                                    refilling_child.full_weight = refilling_entry.full_weight
                                    refilling_child.actual_weight = refilling_entry.actual_weight
                                    refilling_child.empty_weight = refilling_entry.empty_weight
                                    refilling_child.year_of_mfg = refilling_entry.year_of_mfg
                                    refilling_child.hpt_due_date = refilling_entry.hpt_due_date
                                    refilling_child.year_frequency = refilling_entry.year_frequency
                                    refilling_child.expiry_life_due = refilling_entry.expiry_life_due
                                    refilling_child.qr_code = refilling_entry.qr_code
                                    refilling_child.qr_attach = refilling_entry.qr_attach
                            if amc_doc.amc_tracking_notes_details:
                                for notes in amc_doc.amc_tracking_notes_details:
                                    notes_child = amc_tracker_doc.append("amc_tracking_notes_details", {})
                                    notes_child.header =  notes.header
                                    notes_child.amc_scope_of_work =  notes.amc_scope_of_work
                            amc_tracker_doc.save(ignore_permissions=True)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def location_list(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    if isinstance(filters, str):
        filters = json.loads(filters)

    amc = filters.pop("amc_master", None)
    loc_list_amc_master = []

    # ✅ Step 1: Pull location values from AMC Master
    if amc:
        amc_temp = frappe.get_doc("AMC Master", amc)
        if amc_temp and amc_temp.refilling_schedule:
            for loc in amc_temp.refilling_schedule:
                if loc.location and txt.lower() in loc.location.lower():
                    loc_list_amc_master.append(loc.location)  # Store as plain strings

    # ✅ Step 2: Add to filters if we have matching locations
    if len(loc_list_amc_master) == 1:
        filters['name'] = loc_list_amc_master[0]
    elif len(loc_list_amc_master) > 1:
        filters['name'] = ['in', loc_list_amc_master]
    else:
        return []

    # ✅ Step 3: Get searchable fields
    meta = frappe.get_meta(doctype, cached=True)
    searchfields = meta.get_search_fields()
    extra_searchfields = [field for field in searchfields if field != "name"]

    columns = ""
    if extra_searchfields:
        columns += ", " + ", ".join([f"`tab{doctype}`.`{f}`" for f in extra_searchfields])

    # ✅ Step 4: Build search condition
    searchfields_cond = " OR ".join([
        f"`tab{doctype}`.`{field}` LIKE %(txt)s" for field in searchfields
    ])

    # ✅ Step 5: Final query
    return frappe.db.sql(
        f"""
        SELECT `tab{doctype}`.`name` {columns}
        FROM `tab{doctype}`
        WHERE 1=1
            {get_filters_cond(doctype, filters, []).replace("%", "%%")}
            AND ({searchfields_cond})
        ORDER BY
            IF(LOCATE(%(_txt)s, `name`), LOCATE(%(_txt)s, `name`), 99999),
            idx DESC,
            `name`
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "txt": f"%%{txt}%%",
            "_txt": txt.replace("%", ""),
            "start": start,
            "page_len": page_len,
        },
        as_dict=as_dict,
    )
