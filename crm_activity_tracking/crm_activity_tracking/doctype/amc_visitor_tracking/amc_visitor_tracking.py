# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from frappe import _
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
		sync_refilling_to_amc(self.name)


def sync_refilling_to_amc(avt_name):
	"""
	Push date_refilling / refilling_frequency / enter_datetime /
	refilling_due_date from this AMC Visitor Tracking's refilling_schedule
	rows back to the matching rows on the linked AMC (amc_template).

	Rows are matched via amc_refilling_row (the AMC row's name), falling
	back to location + type + cap for rows created without that link.
	The same values are then pushed one level up to the AMC Master linked
	to that AMC (amc_master), matching rows by location + type + cap.
	Uses frappe.db.set_value so AMC's / AMC Master's validate() is not re-triggered.
	"""
	amc_template = frappe.db.get_value("AMC Visitor Tracking", avt_name, "amc_template")
	if not amc_template:
		return

	amc_master = frappe.db.get_value("AMC", amc_template, "amc_master")

	rows = frappe.get_all(
		"Refilling Schedule Table",
		filters={"parent": avt_name, "parenttype": "AMC Visitor Tracking"},
		fields=[
			"amc_refilling_row", "location", "type", "cap",
			"date_refilling", "refilling_frequency", "enter_datetime", "refilling_due_date"
		]
	)

	for row in rows:
		values = {
			"date_refilling": row.date_refilling,
			"refilling_frequency": row.refilling_frequency,
			"enter_datetime": row.enter_datetime,
			"refilling_due_date": row.refilling_due_date
		}

		amc_row = row.amc_refilling_row
		if not amc_row:
			amc_row = frappe.db.get_value(
				"Refilling Schedule Table",
				{
					"parent": amc_template,
					"parenttype": "AMC",
					"location": row.location,
					"type": row.type,
					"cap": row.cap
				},
				"name"
			)
		if amc_row:
			frappe.db.set_value("Refilling Schedule Table", amc_row, values, update_modified=False)

		if not amc_master:
			continue

		master_row = frappe.db.get_value(
			"Refilling Schedule Table",
			{
				"parent": amc_master,
				"parenttype": "AMC Master",
				"location": row.location,
				"type": row.type,
				"cap": row.cap
			},
			"name"
		)
		if master_row:
			frappe.db.set_value("Refilling Schedule Table", master_row, values, update_modified=False)


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