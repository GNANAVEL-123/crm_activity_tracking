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
			if avt:
				existing_doc_name = avt[0].name
				existing_doc_link = frappe.utils.get_link_to_form("AMC Visitor Tracking", existing_doc_name)
				frappe.throw(
					_(
						"An entry already exists with the same Service Date ({0}) and AMC Template ({1}). "
						"Document: {2}."
					).format(
						self.amc_service_date,
						self.amc_template,
						existing_doc_link
					)
				)

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
