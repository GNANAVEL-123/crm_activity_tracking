# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import cstr, flt
import json

class AMCVisitorTracking(Document):
	def validate(self):
		if self.checkin_details:
			seen_dates = {}
			for row in self.checkin_details:
				row_date = row.in_time.split(" ")[0]
				if row_date in seen_dates:
					frappe.throw(
						f"Duplicate date found: {row_date} in rows {seen_dates[row_date]} and {row.idx}. Each date must be unique."
					)
				else:
					seen_dates[row_date] = row.idx
		if self.amc_frequency and self.amc_service_date and not self.is_new():
			service_date = datetime.strptime(self.amc_service_date, "%Y-%m-%d")
			next_amc_service_date = service_date + relativedelta(months=self.amc_frequency)
			self.next_amc_service_due_date = next_amc_service_date.strftime("%Y-%m-%d")
		if self.number_of_portable_fire_extinguisher or self.number_of_trolley_fireextinguisher:
			self.total_extinguisher = (
				int(self.number_of_portable_fire_extinguisher or 0) + 
				int(self.number_of_trolley_fireextinguisher or 0)
			)
		if self.checkin_details:
			for che in self.checkin_details:
				if che.in_time and che.outtime:
					if not self.feedback_table or any(not row.description or not row.marks for row in self.feedback_table):
						frappe.throw("Please ensure all rows in Feedback Table have both 'Description' and 'Marks' filled before Update Checkout.")
		if self.amc_service_date and self.amc_template:
			avt = frappe.db.get_list(
				"AMC Visitor Tracking",
				filters={"amc_service_date": self.amc_service_date, "amc_template": self.amc_template},
				fields=["name"]
			)
			# if avt:
			# 	existing_doc_name = avt[0].name
			# 	existing_doc_link = frappe.utils.get_link_to_form("AMC Visitor Tracking", existing_doc_name)
			# 	frappe.throw(
			# 		_(
			# 			"An entry already exists with the same Service Date ({0}) and AMC Template ({1}). "
			# 			"Document: {2}."
			# 		).format(
			# 			self.amc_service_date,
			# 			self.amc_template,
			# 			existing_doc_link
			# 		)
			# 	)

	def on_update(self):
		sync_refilling_to_amc(self)


CHILD = "Refilling Schedule Table"
# Values pushed from a visit row up to its AMC row and AMC Master row.
REFILL_SYNC_FIELDS = ("date_refilling", "refilling_frequency", "refilling_due_date", "enter_datetime")


def _norm(field, value):
	if field == "refilling_frequency":
		return flt(value)
	return cstr(value or "")


def sync_refilling_to_amc(doc):
	"""Desk save: push only the visit rows whose refilling values changed in
	this save, so re-saving an old visit never overwrites newer AMC / AMC
	Master values. Nothing is pushed when the visit is first created."""
	before = doc.get_doc_before_save()
	if not before or not doc.amc_template:
		return
	old_rows = {r.name: r for r in before.refilling_schedule}
	for row in doc.refilling_schedule:
		prev = old_rows.get(row.name)
		if prev and all(_norm(f, prev.get(f)) == _norm(f, row.get(f)) for f in REFILL_SYNC_FIELDS):
			continue
		propagate_refill_values(row, {f: row.get(f) for f in REFILL_SYNC_FIELDS}, doc.amc_template)


def _single_row(filters):
	"""The only matching child row, or None when there are none or several."""
	rows = frappe.get_all(CHILD, filters=filters, fields=["name", "amc_master_row"], limit=2)
	return rows[0] if len(rows) == 1 else None


def _find_amc_row(visit_row, amc_template):
	"""AMC row for a visit row: amc_refilling_row link, else the one row of
	that AMC with the same QR code, else the one with the same location + type + cap."""
	base = {"parent": amc_template, "parenttype": "AMC", "parentfield": "refilling_schedule"}
	if visit_row.get("amc_refilling_row"):
		row = _single_row({**base, "name": visit_row.amc_refilling_row})
		if row:
			return row
	if visit_row.get("qr_code"):
		row = _single_row({**base, "qr_code": visit_row.qr_code})
		if row:
			return row
	if visit_row.get("location"):
		return _single_row({**base, "location": visit_row.location, "type": visit_row.type, "cap": visit_row.cap})
	return None


def find_amc_master_row(amc_row, amc_master):
	"""AMC Master row for an AMC row: amc_master_row link, else the one row
	of that AMC Master with the same QR code, else the one with the same
	location + type + cap. A link found by matching is saved on the AMC row."""
	base = {"parent": amc_master, "parenttype": "AMC Master", "parentfield": "refilling_schedule"}
	if amc_row.get("amc_master_row"):
		row = _single_row({**base, "name": amc_row.amc_master_row})
		if row:
			return row.name
	fields = ["qr_code", "location", "type", "cap"]
	src = frappe.db.get_value(CHILD, amc_row.name, fields, as_dict=True) or {}
	row = None
	if src.get("qr_code"):
		row = _single_row({**base, "qr_code": src.qr_code})
	if not row and src.get("location"):
		row = _single_row({**base, "location": src.location, "type": src.type, "cap": src.cap})
	if not row:
		return None
	frappe.db.set_value(CHILD, amc_row.name, "amc_master_row", row.name, update_modified=False)
	return row.name


def propagate_refill_values(visit_row, values, amc_template):
	"""Copy refilling values from an AMC Visitor Tracking row up the chain:
	AMC row (via amc_refilling_row), then AMC Master row (via the AMC row's
	amc_master_row). The visit row itself is the caller's job.
	Uses frappe.db.set_value so AMC's / AMC Master's validate() does not run."""
	values = {k: v for k, v in values.items() if k in REFILL_SYNC_FIELDS}
	if not values or not amc_template:
		return
	log = frappe.logger("crm_activity_tracking")

	amc_row = _find_amc_row(visit_row, amc_template)
	if not amc_row:
		log.info(f"Refill sync: no AMC row in {amc_template} for visit row {visit_row.name}")
		return
	frappe.db.set_value(CHILD, amc_row.name, values, update_modified=False)

	amc_master = frappe.db.get_value("AMC", amc_template, "amc_master")
	if not amc_master:
		return
	master_row = find_amc_master_row(amc_row, amc_master)
	if not master_row:
		log.info(f"Refill sync: no AMC Master row in {amc_master} for AMC row {amc_row.name}")
		return
	frappe.db.set_value(CHILD, master_row, values, update_modified=False)


@frappe.whitelist()
def description_list(doc):
    if doc:
        doc = json.loads(doc)
        given_des = []
        if doc.get("feedback_table"):
            for des in doc.get("feedback_table"):
                if des.get("description"):
                    given_des.append(des["description"])
        desc_list = frappe.db.get_all("Feedback Description", fields=["name"])
        desc_list = [desc["name"] for desc in desc_list]
        return_list = [desc for desc in desc_list if desc not in given_des]
        return return_list


@frappe.whitelist()
def update_quotation_link(amc_name, quotation_name):
    """
    Directly updates the 'quotation' field on an AMC Visitor Tracking
    record without triggering the full doc.save()/validate() cycle.

    This avoids unrelated validation errors (e.g. duplicate checkin
    dates, incomplete feedback table rows) from silently blocking the
    quotation link-back after a Quotation is created from this record.
    """
    if not amc_name or not quotation_name:
        frappe.throw(_("Both AMC Visitor Tracking name and Quotation name are required."))

    frappe.db.set_value(
        "AMC Visitor Tracking",
        amc_name,
        "quotation",
        quotation_name,
        update_modified=False
    )
    frappe.db.commit()

    return {"status": "ok"}


def link_quotation_to_amc(doc, method=None):
    """
    doc_events hook — runs automatically every time a Quotation is
    saved (on_update), regardless of whether that save came from the
    "Create Quotation" button's automated flow, a manual Save click by
    the user afterward, the API, or a bulk/import operation.

    If this Quotation has a linked AMC Visitor Tracking record
    (via custom_amc_tracking), push this Quotation's name into that
    record's "quotation" field — using a direct DB update so it does
    not re-trigger AMC Visitor Tracking's own validate() logic.

    Register this in hooks.py:

        doc_events = {
            "Quotation": {
                "on_update": "crm_activity_tracking.crm_activity_tracking.doctype.amc_visitor_tracking.amc_visitor_tracking.link_quotation_to_amc"
            }
        }
    """
    amc_name = doc.get("custom_amc_tracking")

    if not amc_name:
        return

    # Only update if it's not already pointing to this quotation,
    # to avoid unnecessary DB writes on every save.
    current_value = frappe.db.get_value("AMC Visitor Tracking", amc_name, "quotation")

    if current_value != doc.name:
        frappe.db.set_value(
            "AMC Visitor Tracking",
            amc_name,
            "quotation",
            doc.name,
            update_modified=False
        )